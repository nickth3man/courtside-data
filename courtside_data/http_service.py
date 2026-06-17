"""HTTP transport: rate-limited, retried requests with selector caching.

Generic table endpoints are handled by :class:`~courtside_data.generic_endpoints.GenericEndpointHandler`.
Bespoke endpoints are handled by :class:`~courtside_data.custom_endpoints.CustomEndpointHandler`.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import logging
import os
import random
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from datetime import UTC
from pathlib import Path
from typing import Any, ClassVar

import httpx
import stamina
from curl_cffi.const import CurlOpt  # type: ignore[import-untyped]
from hishel.httpx import SyncCacheTransport
from lxml import html
from parsel import Selector

from courtside_data.debug import current_debug_trace
from courtside_data.errors import RateLimitJailed

logger = logging.getLogger(__name__)

_DEFAULT_RATE_LIMIT_INTERVAL = 6.0  # 10 req/min ceiling — matches pybaseball's proven safe rate
_DEFAULT_RATE_LIMIT_JITTER = 1.0  # uniform(0, 1.0) — average ~8.6 req/min with comfortable headroom
_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
_RETRY_ATTEMPTS = 3

# Pages like the 7-game playoff series outcomes matrix host multiple tables
# that are exposed as separate endpoints. Cache parsed selectors per URL so
# fetching several tables from the same page only makes one HTTP request and
# only parses the HTML once. The cache is per-instance and bounded to avoid
# unbounded growth for long-lived clients.
_SELECTOR_CACHE_SIZE = 16
# Basketball-Reference can send Retry-After values of an hour or more when a
# session is jailed. stamina uses a hook-returned float verbatim (wait_max
# does not apply to it), so cap it to keep a single request from sleeping
# for the full jail duration.
_MAX_RETRY_AFTER_WAIT = float(os.environ.get("BASKETBALL_REF_MAX_RETRY_AFTER", "60.0"))

# If Retry-After exceeds this threshold, the session is considered jailed
# and further retries are suppressed to avoid wasting requests.
_JAIL_THRESHOLD_SECONDS = 300.0  # 5 minutes

# Jail state is persisted to disk so a process that crashes (or is restarted)
# while jailed does not immediately re-offend — Basketball-Reference
# escalates bans for repeat offenders. Set the env var to an empty string to
# disable persistence (the test suite does this to stay hermetic).
_JAIL_STATE_PATH_ENV = "BASKETBALL_REF_JAIL_STATE_PATH"
_DEFAULT_JAIL_STATE_PATH = Path(".cache") / "courtside" / "jail.json"

# Browser-like headers proven to avoid bot-flagging.
# Tells Cloudflare this looks like a real browser navigation event.
_DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}


class _SafeCurlTransport(httpx.BaseTransport):
    """Wraps :class:`httpx_curl_cffi.CurlTransport` with two workarounds for
    correct caching behavior with hishel:

    1. **Timeout extension**: A hishel 1.x regression drops the ``timeout``
       extension when revalidating cached responses, causing
       ``CurlTransport._create_request_params`` to fail with an
       ``AssertionError``. The ``handle_request`` method ensures every
       request has a ``timeout`` extension before handing off to the real
       transport.

    2. **Content decoding**: ``curl-cffi`` decompresses gzip responses by
       default but leaves the ``Content-Encoding: gzip`` header in place.
       When hishel stores/retrieves the response, ``httpx`` sees the header
       and tries to decompress already-plaintext content, raising
       ``httpx.DecodingError``. Passing
       ``curl_options={CurlOpt.HTTP_CONTENT_DECODING: 0}`` tells libcurl
       not to decode content, so ``httpx`` handles decompression
       consistently.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        from httpx_curl_cffi import CurlTransport  # type: ignore[import-untyped]

        curl_options = kwargs.pop("curl_options", {})
        curl_options = {CurlOpt.HTTP_CONTENT_DECODING: 0, **curl_options}
        self._impl = CurlTransport(*args, curl_options=curl_options, **kwargs)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if "timeout" not in request.extensions:
            request.extensions["timeout"] = {
                "connect": _DEFAULT_TIMEOUT.connect,
                "read": _DEFAULT_TIMEOUT.read,
                "write": _DEFAULT_TIMEOUT.write,
                "pool": _DEFAULT_TIMEOUT.pool,
            }
        return self._impl.handle_request(request)

    def close(self) -> None:
        self._impl.close()


def _parse_retry_after(value: str) -> float:
    """Parse Retry-After header value, returning seconds to wait.

    Handles both integer seconds and HTTP-date formats per RFC 9110.
    """
    try:
        return float(value)
    except ValueError:
        pass
    # HTTP-date format: parse RFC 2822 date
    import email.utils as eutils
    from datetime import datetime

    parsed = eutils.parsedate_tz(value)
    if parsed is not None:
        retry_time = datetime(*parsed[:6], tzinfo=UTC)
        now = datetime.now(UTC)
        wait = (retry_time - now).total_seconds()
        return max(wait, 1.0)
    return 5.0


def _should_retry(exc: Exception) -> bool | float:
    """Custom stamina retry predicate.

    Returns True to retry with default backoff, a float to retry after
    that many seconds (honors Retry-After, capped at _MAX_RETRY_AFTER_WAIT),
    or False to abort. If the Retry-After value exceeds the jail threshold
    (5 minutes), returns False to skip retries — the caller handles jail
    detection.
    """
    if isinstance(exc, httpx.TransportError):
        logger.debug("Retrying after transport error: %s", exc)
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in (429, 502, 503, 504):
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after is not None:
                parsed = _parse_retry_after(retry_after)
                if parsed > _JAIL_THRESHOLD_SECONDS:
                    logger.warning("Retry-After of %.0fs exceeds jail threshold; not retrying", parsed)
                    return False  # We're jailed — don't burn retries
                wait = min(parsed, _MAX_RETRY_AFTER_WAIT)
                logger.debug("HTTP %d with Retry-After %s; retrying in %.1fs", code, retry_after, wait)
                return wait
            logger.debug("HTTP %d; retrying with default backoff", code)
            return True
        # Do NOT retry other 4xx (400, 401, 403, 404, etc.)
        return False
    return False


def _jail_state_path() -> Path | None:
    value = os.environ.get(_JAIL_STATE_PATH_ENV)
    if value is None:
        return _DEFAULT_JAIL_STATE_PATH
    return Path(value) if value else None


def _read_persisted_jail() -> float | None:
    """Return the persisted jailed-until UNIX timestamp if it is still active.

    Stale or unreadable state files are removed/ignored (best effort).
    """
    path = _jail_state_path()
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        jailed_until_epoch = float(payload["jailed_until_epoch"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if jailed_until_epoch <= time.time():
        with contextlib.suppress(OSError):
            path.unlink()
        return None
    return jailed_until_epoch


def _persist_jail(jailed_until_epoch: float) -> None:
    path = _jail_state_path()
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"jailed_until_epoch": jailed_until_epoch}), encoding="utf-8")
    except OSError:
        logger.warning("Could not persist rate-limit jail state to %s", path)


def build_client(
    cache: bool = False,
    timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
    headers: dict[str, str] | None = None,
    impersonate: str | None = "chrome124",
) -> httpx.Client:
    """Build the httpx client used by HTTPService.

    With cache=True, responses are cached per RFC 9111 via hishel's
    SQLite-backed storage. Headers default to browser-like values that
    reduce bot-flagging; pass ``headers`` to override or extend.

    TLS impersonation is enabled by default (``impersonate="chrome124"``)
    via the ``httpx-curl-cffi`` package. Set ``impersonate=None`` to use
    standard httpx TLS instead.
    """
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    transport: httpx.BaseTransport = httpx.HTTPTransport()

    if impersonate is not None:
        transport = _SafeCurlTransport(impersonate=impersonate)

    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(transport=transport, follow_redirects=True, timeout=timeout, headers=merged)


class HTTPService:
    """Rate-limited HTTP client with selector caching for Basketball Reference."""

    BASE_URL = "https://www.basketball-reference.com"
    _last_request_time: ClassVar[float] = float("-inf")
    _jailed_until: ClassVar[float] = 0.0  # monotonic timestamp; 0 = not jailed
    _jail_state_loaded: ClassVar[bool] = False  # persisted jail state is read at most once per process
    _rate_limit_lock: ClassVar[threading.RLock] = threading.RLock()

    def __init__(
        self,
        parser: Any = None,
        rate_limit_interval: float | None = None,
        rate_limit_jitter: float | None = None,
        session: httpx.Client | None = None,
        time_func: Callable[[], float] | None = None,
        sleep: Callable[[float], None] | None = None,
        random_func: Callable[[float, float], float] | None = None,
        timeout: httpx.Timeout | None = None,
        cache: bool = True,
        headers: dict[str, str] | None = None,
        impersonate: str | None = "chrome124",
    ) -> None:
        self.parser = parser
        # Constructor param > env var > default
        if rate_limit_interval is not None:
            self._rate_limit_interval = rate_limit_interval
        else:
            self._rate_limit_interval = float(
                os.environ.get("BASKETBALL_REF_RATE_LIMIT_INTERVAL", _DEFAULT_RATE_LIMIT_INTERVAL)
            )

        if rate_limit_jitter is not None:
            self._rate_limit_jitter = rate_limit_jitter
        else:
            self._rate_limit_jitter = float(
                os.environ.get("BASKETBALL_REF_RATE_LIMIT_JITTER", _DEFAULT_RATE_LIMIT_JITTER)
            )

        self._timeout = timeout if timeout is not None else _DEFAULT_TIMEOUT
        self._session = (
            session
            if session is not None
            else build_client(
                cache=cache,
                timeout=self._timeout,
                headers=headers,
                impersonate=impersonate,
            )
        )

        # Injectable dependencies for testing
        self._time = time_func if time_func is not None else time.monotonic
        self._sleep = sleep if sleep is not None else time.sleep
        self._random = random_func if random_func is not None else random.uniform

        # Bounded per-instance selector cache so multiple endpoints that scrape
        # the same URL share one fetch and one parse.
        self._selector_cache: OrderedDict[str, Selector] = OrderedDict()

    @classmethod
    def _url(cls, path: str = "") -> str:
        """Join :attr:`BASE_URL` with ``path`` (leading slash optional)."""
        return f"{cls.BASE_URL}/{path.lstrip('/')}" if path else cls.BASE_URL

    def _apply_rate_limiting(self) -> None:
        wait = 0.0
        trace = current_debug_trace()
        with self._rate_limit_lock:
            # A jail set by a previous process (persisted to disk) carries over
            if not self.__class__._jail_state_loaded:
                self.__class__._jail_state_loaded = True
                jailed_until_epoch = _read_persisted_jail()
                if jailed_until_epoch is not None:
                    remaining = jailed_until_epoch - time.time()
                    self.__class__._jailed_until = self._time() + remaining
                    logger.warning("Loaded persisted jail state: %.0fs remaining", remaining)
                    if trace is not None:
                        trace.record("rate_limit", "persisted_jail_loaded", remaining_seconds=remaining)

            # Circuit breaker: if jailed, refuse all requests immediately
            current_time = self._time()
            if current_time < self.__class__._jailed_until:
                remaining = self.__class__._jailed_until - current_time
                if trace is not None:
                    trace.record("rate_limit", "jailed_request_rejected", remaining_seconds=remaining)
                raise RateLimitJailed(retry_after=remaining)

            time_since_last = current_time - self.__class__._last_request_time
            if self._rate_limit_interval > 0 and time_since_last < self._rate_limit_interval:
                jitter = self._random(0.0, self._rate_limit_jitter)
                wait = (self._rate_limit_interval - time_since_last) + jitter
                if trace is not None:
                    trace.record(
                        "rate_limit",
                        "sleep",
                        interval_seconds=self._rate_limit_interval,
                        jitter_seconds=jitter,
                        wait_seconds=wait,
                        seconds_since_last_request=time_since_last,
                    )
                self.__class__._last_request_time = current_time + wait
            else:
                if trace is not None:
                    trace.record(
                        "rate_limit",
                        "no_sleep",
                        interval_seconds=self._rate_limit_interval,
                        seconds_since_last_request=time_since_last,
                    )
                self.__class__._last_request_time = current_time

        if wait > 0.0:
            logger.debug("Rate-limit pacing: sleeping %.2fs", wait)
            self._sleep(wait)

    def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        trace = current_debug_trace()
        if trace is not None:
            trace.record("http", "request_prepare", url=url, kwargs=sorted(kwargs))
        self._apply_rate_limiting()
        response = None
        attempt_count = 0
        try:
            for attempt in stamina.retry_context(
                on=_should_retry,
                attempts=_RETRY_ATTEMPTS,
                wait_initial=1.0,
                wait_max=10.0,
                wait_jitter=0.5,
            ):
                with attempt:
                    attempt_count += 1
                    if trace is not None:
                        trace.record("http", "attempt_start", attempt=attempt_count, url=url)
                    response = self._session.get(url=url, **kwargs)
                    if trace is not None:
                        trace.record(
                            "http",
                            "attempt_response",
                            attempt=attempt_count,
                            status_code=response.status_code,
                            url=str(response.url),
                            headers=trace.sanitize_headers(response.headers),
                            extensions={key: repr(value) for key, value in response.extensions.items()},
                        )
                    response.raise_for_status()
            assert response is not None  # retry_context either yields a response or raises
        except httpx.HTTPStatusError as e:
            if trace is not None:
                trace.record(
                    "http",
                    "status_error",
                    status_code=e.response.status_code,
                    url=str(e.response.url),
                    attempts=attempt_count,
                )
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                if retry_after is not None:
                    parsed = _parse_retry_after(retry_after)
                    if parsed > _JAIL_THRESHOLD_SECONDS:
                        # Set the circuit breaker so future calls fail fast,
                        # and persist it so restarted processes honor it too
                        self.__class__._jailed_until = self._time() + parsed
                        _persist_jail(time.time() + parsed)
                        logger.warning("Session jailed by Basketball-Reference for %.0fs", parsed)
                        if trace is not None:
                            trace.record("rate_limit", "jail_detected", retry_after_seconds=parsed)
                        raise RateLimitJailed(retry_after=parsed) from e
            raise
        else:
            # Reset pacing — retries consumed time, so measure from now
            with self._rate_limit_lock:
                self.__class__._last_request_time = self._time()
            if trace is not None:
                trace.record(
                    "http",
                    "request_complete",
                    status_code=response.status_code,
                    final_url=str(response.url),
                    attempts=attempt_count,
                )
        return response

    def _get_selector(self, url: str) -> Selector:
        """Fetch a page (no redirects) and wrap the body in a parsel Selector.

        Parsed selectors are cached per URL on this instance, so callers that
        extract several tables from the same page (e.g. the three 7-game
        playoff series outcome matrices) reuse one request and one parse.
        """
        if url in self._selector_cache:
            self._selector_cache.move_to_end(url)
            trace = current_debug_trace()
            if trace is not None:
                trace.record("http", "selector_cache_hit", url=url)
            return self._selector_cache[url]

        response = self._get(url=url, follow_redirects=False)
        response.raise_for_status()
        trace = current_debug_trace()
        if trace is not None:
            trace.record(
                "http",
                "selector_created",
                url=str(response.url),
                response_text_length=len(response.text),
                response_text_sha256=hashlib.sha256(response.text.encode("utf-8", errors="replace")).hexdigest(),
            )
        selector = Selector(text=response.text)
        self._selector_cache[url] = selector
        if len(self._selector_cache) > _SELECTOR_CACHE_SIZE:
            self._selector_cache.popitem(last=False)
        return selector

    def _get_html(self, url: str, **kwargs: Any) -> html.HtmlElement:
        """Fetch a page, raise on HTTP errors, and parse the body with lxml."""
        response = self._get(url=url, **kwargs)
        response.raise_for_status()
        trace = current_debug_trace()
        if trace is not None:
            trace.record(
                "http",
                "html_created",
                url=str(response.url),
                response_content_length=len(response.content),
                response_content_sha256=hashlib.sha256(response.content).hexdigest(),
            )
        return html.fromstring(response.content)
