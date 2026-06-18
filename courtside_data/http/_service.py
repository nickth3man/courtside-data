"""Slim :class:`HTTPService` — the rate-limited, retried, cache-aware transport.

Phase 2C of the courtside-data refactor. Pure state + I/O lives here;
rate-limit pacing and the persistent circuit-breaker ("jail") state live
in :mod:`courtside_data.http._rate_limit`, retry predicates in
:mod:`courtside_data.http._retry`, transport construction in
:mod:`courtside_data.http._transport`, and module-level constants in
:mod:`courtside_data.http._constants`.

Behavior is identical to the previous
:class:`courtside_data.http_service.HTTPService` implementation. The
:class:`HTTPService` symbol is re-exported from the
:mod:`courtside_data.http` package and from the back-compat shim
:mod:`courtside_data.http_service` so existing imports keep working.

Backwards-compatibility class attribute surface
-----------------------------------------------

The previous implementation carried the process-wide pacing state as
``ClassVar`` on :class:`HTTPService` and let tests reset it via direct
assignment::

    HTTPService._last_request_time = float("-inf")
    HTTPService._jailed_until = 0.0
    HTTPService._jail_state_loaded = False

In Phase 2C the state moved to
:mod:`courtside_data.http._rate_limit` (so a future split of this class
still shares one budget per process). The :class:`_ClassStateMeta`
metaclass re-routes the four legacy names — ``_last_request_time``,
``_jailed_until``, ``_jail_state_loaded``, and ``_rate_limit_lock`` —
through to the module-level singleton so the test surface and any
external code that pokes at those names keep working unchanged. The
forwarder list is meant to be removed in a future major release once
the new module path is the public surface.
"""

from __future__ import annotations

import hashlib
import logging
import random
import time
from collections.abc import Callable
from typing import Any, ClassVar

import cachetools
import httpx
import stamina
from parsel import Selector

from courtside_data import config
from courtside_data.debug import current_debug_trace
from courtside_data.errors import RateLimitJailed
from courtside_data.http import _rate_limit, _retry
from courtside_data.http._constants import (
    _DEFAULT_TIMEOUT,
    _JAIL_THRESHOLD_SECONDS,
    _RETRY_ATTEMPTS,
    _SELECTOR_CACHE_SIZE,
    _SELECTOR_CACHE_TTL,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.basketball-reference.com"


def _build_client(
    *,
    cache: bool,
    timeout: httpx.Timeout,
    headers: dict[str, str] | None,
    impersonate: str | None,
) -> httpx.Client:
    """Late-bound reference to the shim's :func:`build_client`.

    The :mod:`tests.conftest` session fixture patches
    :data:`courtside_data.http_service.build_client` to force
    ``impersonate=None`` so the offline suite doesn't drag in
    ``httpx-curl-cffi``. Resolving through the shim — rather than
    importing :mod:`courtside_data.http._transport` directly here —
    means the patch flows through to the new
    :class:`HTTPService` constructor.

    The import is delayed until the first :class:`HTTPService` is
    constructed, which is after both the shim and
    :mod:`courtside_data.http._transport` are fully loaded, so the
    late import cannot create a cycle.
    """
    from courtside_data import http_service as _shim

    return _shim.build_client(
        cache=cache,
        timeout=timeout,
        headers=headers,
        impersonate=impersonate,
    )


class _ClassStateMeta(type):
    """Metaclass that forwards class-level attribute access to a module singleton.

    The forwarder list is fixed per subclass (set via the ``_FORWARDED``
    class attribute) so the metaclass itself stays small and trivial.
    A read or write to one of the listed names on the class is
    re-routed to the same-named module attribute on
    :mod:`courtside_data.http._rate_limit`.

    Only class-level access is intercepted: ``HTTPService._foo`` is
    forwarded, ``instance._foo`` is not (matches the previous
    ``ClassVar`` semantics, where the test fixture wrote
    ``HTTPService._foo = ...`` and read it back the same way).
    """

    _FORWARDED: ClassVar[tuple[str, ...]] = ()

    def __getattr__(cls, name: str) -> Any:
        if name in cls._FORWARDED:
            from courtside_data.http import _rate_limit as _rl

            return getattr(_rl, name)
        raise AttributeError(f"{cls.__name__!r} has no attribute {name!r}")

    def __setattr__(cls, name: str, value: Any) -> None:
        if name in cls._FORWARDED:
            from courtside_data.http import _rate_limit as _rl

            setattr(_rl, name, value)
        else:
            super().__setattr__(name, value)


class HTTPService(metaclass=_ClassStateMeta):
    """Rate-limited HTTP client with selector caching for Basketball Reference."""

    BASE_URL: ClassVar[str] = BASE_URL
    # Class-level forwarder list — see :class:`_ClassStateMeta`. Reads
    # and writes to these names on the class go through to
    # :mod:`courtside_data.http._rate_limit` so test resets
    # (``HTTPService._last_request_time = float('-inf')``) keep working
    # without code changes.
    _FORWARDED: ClassVar[tuple[str, ...]] = (
        "_last_request_time",
        "_jailed_until",
        "_jail_state_loaded",
        "_rate_limit_lock",
    )
    # Bare ClassVar annotations (no value) so ty sees the expected types
    # while the metaclass still intercepts reads/writes at runtime (bare
    # annotations do not create __dict__ entries).
    _last_request_time: ClassVar[float]
    _jailed_until: ClassVar[float]
    _jail_state_loaded: ClassVar[bool]

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
            # http_service.build_client flows through.
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
        # the same URL share one fetch and one parse. TTLCache evicts on age
        # (10 min) *and* size, so long-lived clients cannot accumulate stale
        # Selectors and selectors for time-sensitive pages do not outlive their
        # validity window.
        self._selector_cache: cachetools.TTLCache[str, Selector] = cachetools.TTLCache(
            maxsize=_SELECTOR_CACHE_SIZE, ttl=_SELECTOR_CACHE_TTL
        )

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
                            url=str(response.url),
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
                    url=str(e.response.url),
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
            trace = current_debug_trace()
            if trace is not None:
                trace.record(
                    "http",
                    "selector_cache_hit",
                    url=url,
                    cache_stats=self._selector_cache_stats(),
                )
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
