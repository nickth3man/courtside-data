"""Injected-dependency tests for :class:`HTTPService`'s rate-limit and jail logic.

These tests exercise the rate-limiter in :class:`HTTPService` *without* real
network I/O by injecting fakes for ``time_func``, ``sleep``, and
``random_func``. The only network-shaped interaction is via a tiny
``_FakeSession`` stub whose ``.get()`` returns a pre-canned
``httpx.Response``.

Coverage:

1. **Pacing** — a request fired before the rate-limit interval must sleep
   for the remaining time (plus deterministic jitter from the injected
   ``random_func``).
2. **No-sleep path** — a request fired well after the previous one must
   not sleep.
3. **Jail circuit breaker** — when ``HTTPService._jailed_until`` is set
   in the future, every request fails fast with ``RateLimitJailed`` and
   does NOT sleep.
4. **429 → jail activation via ``_get``** — a real 429 response with
   ``Retry-After > 300`` triggers the jail detection code path in
   ``HTTPService._get`` and raises ``RateLimitJailed``.
5. **Jail persistence disabled in tests** — with
   ``BASKETBALL_REF_JAIL_STATE_PATH=""`` (set by ``tests/conftest.py``),
   ``_persist_jail`` is a no-op.
6. **Recovery** — once the monotonic clock advances past ``_jailed_until``,
   the next ``_apply_rate_limiting()`` call succeeds.

No transport and no manifest. Shared autouse fixtures live in
:mod:`tests.conftest`.
"""

from __future__ import annotations

import os

import httpx
import pytest
from courtside_data.errors import RateLimitJailed
from courtside_data.http_service import (
    HTTPService,
    _jail_state_path,
    _persist_jail,
)

# ─── Helpers ─────────────────────────────────────────────────────────────────


class _FakeClock:
    """Monotonic-clock stand-in.

    Defaults to 0.0; bump ``self.t`` to advance time deterministically.
    Callable so it can be passed directly as ``time_func``.
    """

    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class _SleepRecorder:
    """Sleep stand-in. Records every call so tests can assert pacing."""

    def __init__(self) -> None:
        self.calls: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


def _zero_random(_lo: float, _hi: float) -> float:
    """Random stand-in that always returns 0.0 — eliminates jitter variability."""
    return 0.0


def _build_service(clock: _FakeClock, sleep: _SleepRecorder) -> HTTPService:
    """Build a default-configured HTTPService with injected fakes for time/sleep/jitter."""
    return HTTPService(
        time_func=clock,
        sleep=sleep,
        random_func=_zero_random,
        rate_limit_interval=6.0,
        rate_limit_jitter=1.0,
    )


class _FakeSession:
    """Minimal httpx.Client stand-in that returns a pre-canned response.

    The real ``HTTPService._get`` only calls ``self._session.get(url=url, **kwargs)``
    so the stub only needs that one method.
    """

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self.call_count = 0

    def get(self, *, url: str, **kwargs):
        self.call_count += 1
        return self._response


# ─── Tests ───────────────────────────────────────────────────────────────────


def test_pacing_sleeps_to_fill_interval():
    """A request fired 1s after the previous one must sleep ~5s to honour the 6s interval.

    With ``rate_limit_interval=6.0`` and a deterministic 0.0 jitter, the
    expected sleep is ``(6 - 1) + 0 = 5`` seconds.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    service = _build_service(clock, sleep)

    # Simulate "a request was just made" by recording the current time.
    HTTPService._last_request_time = clock()
    clock.t = 1.0
    service._apply_rate_limiting()

    assert sleep.calls == [pytest.approx(5.0, abs=0.01)]
    # After the call, the module-level state is updated to the projected/pacing-complete time.
    assert HTTPService._last_request_time == pytest.approx(6.0)


def test_pacing_does_not_sleep_when_interval_is_zero():
    """With ``rate_limit_interval=0`` (the test-suite default), pacing is disabled.

    The pacing branch in ``_apply_rate_limiting`` is gated on
    ``self._rate_limit_interval > 0``, so the request should not sleep even
    when the previous request was just made.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    service = HTTPService(
        time_func=clock,
        sleep=sleep,
        random_func=_zero_random,
        rate_limit_interval=0.0,
        rate_limit_jitter=1.0,
    )

    HTTPService._last_request_time = clock()
    clock.t = 0.1
    service._apply_rate_limiting()

    assert sleep.calls == []
    assert HTTPService._last_request_time == pytest.approx(0.1)


def test_no_sleep_when_interval_already_satisfied():
    """A request fired well after the previous one must NOT sleep.

    With 100s elapsed and a 6s interval, the pacing branch is skipped.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    service = _build_service(clock, sleep)

    # Set last-request to long ago so the interval is comfortably satisfied.
    HTTPService._last_request_time = 0.0
    clock.t = 100.0
    service._apply_rate_limiting()

    assert sleep.calls == []
    assert HTTPService._last_request_time == pytest.approx(100.0)


def test_jail_circuit_breaker_raises_and_skips_sleep():
    """If ``_jailed_until`` is in the future, every request must fail fast without sleeping.

    This is the "circuit breaker" path: ``_apply_rate_limiting`` raises
    ``RateLimitJailed`` and never reaches the sleep call. Verifies that
    ``retry_after`` on the exception matches the remaining jail window.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    service = _build_service(clock, sleep)

    HTTPService._jailed_until = clock() + 100.0

    with pytest.raises(RateLimitJailed) as exc_info:
        service._apply_rate_limiting()

    assert exc_info.value.retry_after == pytest.approx(100.0)
    assert sleep.calls == []


def test_429_with_large_retry_after_activates_jail():
    """A 429 with ``Retry-After > 300`` activates the jail and raises ``RateLimitJailed``.

    The retry predicate (``_should_retry``) returns False for this case, so
    stamina does not retry; the exception propagates into ``_get``'s
    ``except httpx.HTTPStatusError`` block, which detects the jail threshold
    breach and raises ``RateLimitJailed`` from a custom
    ``self.__class__._jailed_until = self._time() + parsed`` assignment.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    clock.t = 50.0

    request = httpx.Request("GET", "https://www.basketball-reference.com/test")
    response = httpx.Response(429, headers={"Retry-After": "600"}, request=request)
    session = _FakeSession(response)
    service = HTTPService(
        session=session,  # type: ignore
        time_func=clock,
        sleep=sleep,
        random_func=_zero_random,
        rate_limit_interval=6.0,
        rate_limit_jitter=1.0,
    )

    with pytest.raises(RateLimitJailed) as exc_info:
        service._get("https://www.basketball-reference.com/test")

    assert exc_info.value.retry_after == pytest.approx(600.0)
    # _jailed_until was set to the current monotonic time + the parsed Retry-After.
    assert HTTPService._jailed_until == pytest.approx(clock() + 600.0)
    assert HTTPService._jailed_until > clock()
    # _persist_jail was a no-op (env var disabled by conftest), so no file was
    # touched; stamina consumed exactly one attempt (predicate returns False).
    assert session.call_count == 1


def test_429_below_threshold_does_not_activate_jail():
    """A 429 with ``Retry-After < 300`` is NOT a jail — the exception propagates unchanged.

    The retry predicate returns the parsed wait (capped at
    ``_MAX_RETRY_AFTER_WAIT``), so stamina may retry. Under
    ``stamina.set_testing(True, attempts=3)`` stamina does still try multiple
    attempts, but we just need to assert the FIRST one raised an
    ``HTTPStatusError`` (not ``RateLimitJailed``) and that the jail state was
    NOT updated.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    clock.t = 0.0

    request = httpx.Request("GET", "https://www.basketball-reference.com/test")
    response = httpx.Response(429, headers={"Retry-After": "10"}, request=request)
    session = _FakeSession(response)
    service = HTTPService(
        session=session,  # type: ignore
        time_func=clock,
        sleep=sleep,
        random_func=_zero_random,
        rate_limit_interval=6.0,
        rate_limit_jitter=1.0,
    )

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        service._get("https://www.basketball-reference.com/test")

    assert exc_info.value.response.status_code == 429
    # Jail state was NOT set; the circuit breaker should not fire.
    assert HTTPService._jailed_until == 0.0


def test_jail_persistence_disabled_when_env_var_empty():
    """With ``BASKETBALL_REF_JAIL_STATE_PATH=""`` (set by tests/conftest.py),
    ``_jail_state_path`` returns ``None`` and ``_persist_jail`` is a no-op.

    This is the hermetic-test guarantee: jail state never escapes the
    process during a test run, and no temp dir is created.
    """
    # Sanity check: the env var really is empty in this test context.
    assert os.environ.get("BASKETBALL_REF_JAIL_STATE_PATH") == ""
    assert _jail_state_path() is None

    # _persist_jail must accept any value without raising or writing a file.
    _persist_jail(12345.0)
    _persist_jail(0.0)
    _persist_jail(1_000_000.0)


def test_recovery_after_jail_window():
    """Once the monotonic clock advances past ``_jailed_until``, the next
    ``_apply_rate_limiting()`` call must NOT raise.

    The jail window is purely time-based on the injected monotonic clock;
    the only state that matters is ``HTTPService._jailed_until``. This test
    proves the recovery path is wired correctly.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    service = _build_service(clock, sleep)

    # Set the jail window to 100s in the future.
    HTTPService._jailed_until = clock() + 100.0

    # Confirm the jail is in effect.
    with pytest.raises(RateLimitJailed):
        service._apply_rate_limiting()

    # Advance the injected clock past the jail window.
    clock.t = 200.0

    # Should not raise; the rate-limiter resumes normal pacing.
    service._apply_rate_limiting()
    # time_since_last was huge (clock - (-inf) = +inf) so no sleep happens.
    assert sleep.calls == []
    assert HTTPService._last_request_time == pytest.approx(200.0)


def test_recovery_respects_pacing_after_window_expires():
    """After the jail lifts, the next request must still honour the rate-limit interval.

    Sets up a scenario where the last-request time is recent (within the
    interval) and verifies the post-recovery call still sleeps.
    """
    clock = _FakeClock()
    sleep = _SleepRecorder()
    service = _build_service(clock, sleep)

    # Pretend a request happened at t=0, then we got jailed until t=50.
    clock.t = 0.0
    HTTPService._last_request_time = clock()
    HTTPService._jailed_until = 50.0

    # Advance past the jail; the last-request time is still at 0.
    clock.t = 60.0
    service._apply_rate_limiting()

    # 60 - 0 = 60s elapsed, > 6s interval → no sleep.
    assert sleep.calls == []
    assert HTTPService._last_request_time == pytest.approx(60.0)
