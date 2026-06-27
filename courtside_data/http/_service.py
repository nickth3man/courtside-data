"""Slim :class:`HTTPService` — the rate-limited, retried, cache-aware transport.

Pure state + I/O lives here; rate-limit pacing and the persistent
circuit-breaker ("jail") state live in
:mod:`courtside_data.http._rate_limit`, retry predicates in
:mod:`courtside_data.http._retry`, transport construction in
:mod:`courtside_data.http._transport`, and module-level constants in
:mod:`courtside_data.http._constants`.

The :class:`HTTPService` symbol is re-exported from the
:mod:`courtside_data.http` package.
"""

from __future__ import annotations

import hashlib
import logging
import random
import threading
import time
from collections.abc import Callable
from contextlib import nullcontext
from typing import Any, ClassVar

import cachetools
import httpx
import stamina
from parsel import Selector

from courtside_data import config
from courtside_data.debug import DebugTrace, current_debug_trace
from courtside_data.errors import RateLimitJailed
from courtside_data.http import _rate_limit, _retry
from courtside_data.http._constants import (
    _DEFAULT_TIMEOUT,
    _JAIL_THRESHOLD_SECONDS,
    _RETRY_ATTEMPTS,
    _SELECTOR_CACHE_SIZE,
    _SELECTOR_CACHE_TTL,
    BASE_URL,
)

logger = logging.getLogger(__name__)


def _build_client(
    *,
    cache: bool,
    timeout: httpx.Timeout,
    headers: dict[str, str] | None,
    impersonate: str | None,
) -> httpx.Client:
    """Late-bound reference to :func:`build_client` via the public package.

    The :mod:`tests.conftest` session fixture patches
    :data:`courtside_data.http.build_client` to force
    ``impersonate=None`` so the offline suite doesn't drag in
    ``httpx-curl-cffi``. Resolving through the package rather than
    importing :mod:`courtside_data.http._transport` directly
    here — means the patch flows through to the :class:`HTTPService`
    constructor.

    The import is delayed until the first :class:`HTTPService` is
    constructed, which is after both :mod:`courtside_data.http`
    and :mod:`courtside_data.http._transport` are fully loaded, so the
    late import cannot create a circular dependency.
    """
    from courtside_data import http as http_module

    return http_module.build_client(
        cache=cache,
        timeout=timeout,
        headers=headers,
        impersonate=impersonate,
    )


class HTTPService:
    """Rate-limited HTTP client with selector caching for Basketball Reference."""

    BASE_URL: ClassVar[str] = BASE_URL

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
        impersonate: str | None = None,
    ) -> None:
        self.parser = parser
        # Constructor param > env var > default (via courtside_data.config)
        if rate_limit_interval is not None:
            self._rate_limit_interval = rate_limit_interval
        else:
            self._rate_limit_interval = config.rate_limit_interval()

        if rate_limit_jitter is not None:
            self._rate_limit_jitter = rate_limit_jitter
        else:
            self._rate_limit_jitter = config.rate_limit_jitter()

        self._timeout = timeout if timeout is not None else _DEFAULT_TIMEOUT
        if session is not None:
            self._session = session
        else:
            # Late-bound build_client so the conftest patch on
            # courtside_data.http.build_client flows through.
            self._session = _build_client(
                cache=cache,
                timeout=self._timeout,
                headers=headers,
                impersonate=impersonate,
            )

        # Injectable dependencies for testing
        self._time = time_func if time_func is not None else time.monotonic
        self._sleep = sleep if sleep is not None else time.sleep
        self._random = random_func if random_func is not None else random.uniform

        # Bounded per-instance selector cache so multiple endpoints that scrape
        # unchanged HTML from the same URL can reuse one parse. _get_selector()
        # still calls _get() for every request, so hishel keeps ownership of
        # response freshness and conditional revalidation.
        self._selector_cache: cachetools.TTLCache[str, tuple[str, Selector]] = cachetools.TTLCache(
            maxsize=_SELECTOR_CACHE_SIZE, ttl=_SELECTOR_CACHE_TTL
        )
        self._selector_cache_lock = threading.RLock()

    @classmethod
    def _url(cls, path: str = "") -> str:
        """Join :attr:`BASE_URL` with ``path`` (leading slash optional)."""
        return f"{cls.BASE_URL}/{path.lstrip('/')}" if path else cls.BASE_URL

    def _apply_rate_limiting(self) -> None:
        """Enforce pacing + circuit-breaker state via the singleton module.

        Delegates to :func:`courtside_data.http._rate_limit.apply_rate_limiting`
        using the per-instance injected time/sleep/random functions and the
        configured interval/jitter. The singleton ``_last_request_time`` and
        ``_jailed_until`` are read and updated under the singleton's lock, so
        every :class:`HTTPService` instance in the process shares one budget.
        """
        _rate_limit.apply_rate_limiting(
            time_func=self._time,
            sleep=self._sleep,
            random_func=self._random,
            interval=self._rate_limit_interval,
            jitter=self._rate_limit_jitter,
        )

    def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        trace = current_debug_trace()
        if trace is not None:
            with trace.span("http_fetch", stage="http_fetch"):
                return self._get_with_trace(url, trace=trace, **kwargs)
        return self._get_with_trace(url, trace=None, **kwargs)

    def _get_with_trace(self, url: str, *, trace: DebugTrace | None, **kwargs: Any) -> httpx.Response:
        if trace is not None:
            trace.record("http", "request_prepare", url=url, kwargs=sorted(kwargs))
        self._apply_rate_limiting()
        response = None
        attempt_count = 0
        try:
            for attempt in stamina.retry_context(
                on=_retry._should_retry,
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
                            reason_phrase=response.reason_phrase,
                            url=str(response.url),
                            response_bytes=len(response.content),
                            redirect_count=len(response.history),
                            headers=trace.sanitize_headers(response.headers),
                            extensions={key: repr(value) for key, value in response.extensions.items()},
                        )
                    response.raise_for_status()
            if response is None:  # pragma: no cover
                raise RuntimeError("stamina.retry_context completed without yielding a response")
        except httpx.HTTPStatusError as e:
            if trace is not None:
                trace.record(
                    "http",
                    "status_error",
                    status_code=e.response.status_code,
                    reason_phrase=e.response.reason_phrase,
                    url=str(e.response.url),
                    response_bytes=len(e.response.content),
                    redirect_count=len(e.response.history),
                    attempts=attempt_count,
                )
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                if retry_after is not None:
                    parsed = _retry._parse_retry_after(retry_after)
                    if parsed > _JAIL_THRESHOLD_SECONDS:
                        # Set the circuit breaker so future calls fail fast,
                        # and persist it so restarted processes honor it too.
                        # Use the injected time function so tests that drive a
                        # fake monotonic clock can assert on _jailed_until.
                        _rate_limit._jailed_until = self._time() + parsed
                        _rate_limit._persist_jail(time.time() + parsed)
                        logger.warning("Session jailed by Basketball-Reference for %.0fs", parsed)
                        if trace is not None:
                            trace.record("rate_limit", "jail_detected", retry_after_seconds=parsed)
                        raise RateLimitJailed(retry_after=parsed) from e
            raise
        else:
            # Reset pacing — retries consumed time, so measure from now
            with _rate_limit._rate_limit_lock:
                _rate_limit._last_request_time = self._time()
            if trace is not None:
                trace.record(
                    "http",
                    "request_complete",
                    status_code=response.status_code,
                    reason_phrase=response.reason_phrase,
                    final_url=str(response.url),
                    response_bytes=len(response.content),
                    redirect_count=len(response.history),
                    attempts=attempt_count,
                )
        return response

    def _get_selector(self, url: str) -> Selector:
        """Fetch a page (no redirects) and wrap the body in a parsel Selector.

        Parsed selectors are cached per URL on this instance, but the cache is
        only a parse-reuse layer: every call still goes through ``_get`` first
        so the HTTP cache/transport can perform normal freshness checks and
        revalidation. When the fetched body hash differs from the cached hash,
        the stale selector is replaced before parsing continues.
        """
        response = self._get(url=url, follow_redirects=False)
        response.raise_for_status()
        response_text = response.text
        response_text_sha256 = hashlib.sha256(response_text.encode("utf-8", errors="replace")).hexdigest()
        trace = current_debug_trace()

        with self._selector_cache_lock:
            cached = self._selector_cache.get(url)
            if cached is not None:
                cached_sha256, cached_selector = cached
                if cached_sha256 == response_text_sha256:
                    if trace is not None:
                        trace.record(
                            "http",
                            "selector_cache_hit",
                            url=url,
                            response_text_sha256=response_text_sha256,
                            cache_stats=self._selector_cache_stats(),
                        )
                    return cached_selector
                if trace is not None:
                    trace.record(
                        "http",
                        "selector_cache_stale",
                        url=url,
                        cached_response_text_sha256=cached_sha256,
                        response_text_sha256=response_text_sha256,
                        cache_stats=self._selector_cache_stats(),
                    )

        if trace is not None:
            trace.record(
                "http",
                "selector_created",
                url=str(response.url),
                response_text_length=len(response_text),
                response_text_sha256=response_text_sha256,
            )
        parse_context = trace.span("html_parse", stage="html_parse") if trace is not None else nullcontext()
        with parse_context:
            selector = Selector(text=response_text)
        with self._selector_cache_lock:
            self._selector_cache[url] = (response_text_sha256, selector)
        return selector

    def _selector_cache_stats(self) -> dict[str, int | float]:
        """Return cache_info()-style stats for the selector TTLCache.

        Mirrors the fields exposed by :func:`functools.lru_cache.cache_info`
        so consumers do not need to special-case the implementation.
        """
        return {
            "size": self._selector_cache.currsize,
            "maxsize": self._selector_cache.maxsize,
            "ttl": self._selector_cache.ttl,
        }
