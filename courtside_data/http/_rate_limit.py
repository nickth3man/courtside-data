"""Process-wide rate-limit pacing and persistent circuit-breaker ("jail") state.

This module owns the singleton state that used to live as ``ClassVar`` on
:class:`courtside_data.http_service.HTTPService`:

* :data:`_last_request_time` — monotonic pacing anchor.
* :data:`_jailed_until` — monotonic jail deadline (``0.0`` = not jailed).
* :data:`_jail_state_loaded` — one-shot guard around :func:`_read_persisted_jail`.
* :data:`_rate_limit_lock` — re-entrant lock that serializes every pacing
  decision across every :class:`~courtside_data.http_service.HTTPService`
  instance in the process.

The state is intentionally module-level (not class-level) so that any
refactor splitting :class:`HTTPService` into smaller units still shares
one pacing budget per process. The on-disk jail blob lives at
:func:`courtside_data.config.jail_state_path` and survives process
restarts, so a freshly-started process honors a jail that was set by a
previous one.

Layout:

* :data:`_JAIL_THRESHOLD_SECONDS` — cutoff above which a ``Retry-After``
  value flips the circuit breaker open.
* :func:`_read_persisted_jail` / :func:`_persist_jail` — best-effort
  read/write of the on-disk jail blob.
* :func:`apply_rate_limiting` — the pacing primitive called once per
  HTTP request. Loads the persisted jail, raises
  :class:`~courtside_data.errors.RateLimitJailed` while jailed, and
  otherwise enforces the configured ``interval + jitter`` floor.
* :func:`detect_jail` — engages the circuit breaker when a 429 carries a
  ``Retry-After`` above the threshold; persists the deadline and raises.
"""

from __future__ import annotations

import contextlib
import logging
import threading
import time
from collections.abc import Callable

import httpx
import orjson

from courtside_data import config
from courtside_data.debug import current_debug_trace
from courtside_data.errors import RateLimitJailed
from courtside_data.http._constants import _JAIL_THRESHOLD_SECONDS

logger = logging.getLogger(__name__)

# 5 minutes — cutoff above which a ``Retry-After`` value flips the circuit
# breaker open. Imported from ``_constants`` so there is a single source of truth.

# Process-wide (singleton) pacing + jail state. Every read and write is
# serialized by :data:`_rate_limit_lock`. Kept as module-level (not
# ``ClassVar``) so any future split of ``HTTPService`` still shares one
# budget per process.
_last_request_time: float = float("-inf")
_jailed_until: float = 0.0  # monotonic timestamp; 0.0 = not jailed
_jail_state_loaded: bool = False  # persisted jail state is read at most once per process
_rate_limit_lock: threading.RLock = threading.RLock()


def _read_persisted_jail() -> float | None:
    """Return the persisted jailed-until UNIX timestamp if it is still active.

    Stale or unreadable state files are removed/ignored (best effort).
    """
    path = config.jail_state_path()
    if path is None:
        return None
    try:
        payload = orjson.loads(path.read_bytes())
        jailed_until_epoch = float(payload["jailed_until_epoch"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if jailed_until_epoch <= time.time():
        with contextlib.suppress(OSError):
            path.unlink()
        return None
    return jailed_until_epoch


def _persist_jail(jailed_until_epoch: float) -> None:
    """Best-effort write of the jail-state blob.

    Failures are logged and swallowed; persistence is informational and
    must never break a request.
    """
    path = config.jail_state_path()
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # orjson returns bytes; write in binary mode to match.
        path.write_bytes(orjson.dumps({"jailed_until_epoch": jailed_until_epoch}))
    except OSError:
        logger.warning("Could not persist rate-limit jail state to %s", path)


def apply_rate_limiting(
    time_func: Callable[[], float],
    sleep: Callable[[float], None],
    random_func: Callable[[float, float], float],
    interval: float | None = None,
    jitter: float | None = None,
) -> None:
    """Sleep for pacing, then update the singleton pacing anchor.

    The persisted jail is loaded on first call (guarded by
    :data:`_jail_state_loaded`). If the singleton is currently jailed,
    raises :class:`~courtside_data.errors.RateLimitJailed` immediately.
    Otherwise enforces a floor of ``interval + uniform(0, jitter)``
    seconds between consecutive HTTP calls.

    ``time_func``/``sleep``/``random_func`` are injectable so callers
    (and tests) can drive the clock deterministically. ``interval`` and
    ``jitter`` default to :func:`courtside_data.config.rate_limit_interval`
    and :func:`courtside_data.config.rate_limit_jitter` respectively.
    """
    global _jail_state_loaded, _jailed_until, _last_request_time
    if interval is None:
        interval = config.rate_limit_interval()
    if jitter is None:
        jitter = config.rate_limit_jitter()

    wait = 0.0
    trace = current_debug_trace()
    with _rate_limit_lock:
        # A jail set by a previous process (persisted to disk) carries over.
        if not _jail_state_loaded:
            _jail_state_loaded = True
            jailed_until_epoch = _read_persisted_jail()
            if jailed_until_epoch is not None:
                remaining = jailed_until_epoch - time.time()
                _jailed_until = time_func() + remaining
                logger.warning("Loaded persisted jail state: %.0fs remaining", remaining)
                if trace is not None:
                    trace.record("rate_limit", "persisted_jail_loaded", remaining_seconds=remaining)

        # Circuit breaker: if jailed, refuse all requests immediately.
        current_time = time_func()
        if current_time < _jailed_until:
            remaining = _jailed_until - current_time
            if trace is not None:
                trace.record("rate_limit", "jailed_request_rejected", remaining_seconds=remaining)
            raise RateLimitJailed(retry_after=remaining)

        time_since_last = current_time - _last_request_time
        if interval > 0 and time_since_last < interval:
            jitter_sample = random_func(0.0, jitter)
            wait = (interval - time_since_last) + jitter_sample
            if trace is not None:
                trace.record(
                    "rate_limit",
                    "sleep",
                    interval_seconds=interval,
                    jitter_seconds=jitter_sample,
                    wait_seconds=wait,
                    seconds_since_last_request=time_since_last,
                )
            _last_request_time = current_time + wait
        else:
            if trace is not None:
                trace.record(
                    "rate_limit",
                    "no_sleep",
                    interval_seconds=interval,
                    seconds_since_last_request=time_since_last,
                )
            _last_request_time = current_time

    if wait > 0.0:
        logger.debug("Rate-limit pacing: sleeping %.2fs", wait)
        sleep(wait)


def detect_jail(response: httpx.Response, retry_after: float) -> None:
    """Engage the circuit breaker when ``Retry-After`` exceeds the threshold.

    On a 429 with ``retry_after > _JAIL_THRESHOLD_SECONDS``, sets the
    singleton :data:`_jailed_until` monotonic deadline, persists the
    wall-clock equivalent so a restarted process honors it, and raises
    :class:`~courtside_data.errors.RateLimitJailed`.

    If ``retry_after`` is at or below the threshold, this function is a
    no-op and returns ``None``; the caller should let the ordinary
    retry/backoff path handle the response.

    ``response`` is accepted for symmetry with the 429 catch site (and
    for future trace enrichment); the current implementation keys off
    ``retry_after`` only.
    """
    if retry_after <= _JAIL_THRESHOLD_SECONDS:
        return

    # Set the circuit breaker so future calls fail fast, and persist it
    # so restarted processes honor it too.
    global _jailed_until
    with _rate_limit_lock:
        _jailed_until = time.monotonic() + retry_after
    _persist_jail(time.time() + retry_after)
    logger.warning("Session jailed by Basketball-Reference for %.0fs", retry_after)
    trace = current_debug_trace()
    if trace is not None:
        trace.record("rate_limit", "jail_detected", retry_after_seconds=retry_after)
    raise RateLimitJailed(retry_after=retry_after)
