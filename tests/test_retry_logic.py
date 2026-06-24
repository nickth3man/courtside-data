"""Unit tests for the pure-function retry helpers in :mod:`courtside_data.http_service`.

These tests cover two private functions:

* :func:`_parse_retry_after` — parse the ``Retry-After`` header per RFC 9110.
* :func:`_should_retry` — custom stamina retry predicate that decides whether
  a given exception should be retried, how long to wait, or whether the
  session is considered "jailed" and the caller should bail out.

They are pure-function tests, so they need no HTTPService, no transport, and
no manifest. Shared autouse fixtures (stamina testing mode and ClassVar
reset) live in :mod:`tests.conftest`.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import pytest
from courtside_data.http_service import (
    _JAIL_THRESHOLD_SECONDS,
    _MAX_RETRY_AFTER_WAIT,
    _parse_retry_after,
    _should_retry,
)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_retry_after_date(seconds_from_now: int) -> str:
    """Return an RFC 822/2822 HTTP-date string for a UTC moment offset by N seconds.

    ``email.utils.parsedate_tz`` is the parser used by ``_parse_retry_after``;
    it accepts the three legacy GMT formats defined in RFC 9110 §5.1.1. The
    explicit ``GMT`` suffix keeps the test fixture format-agnostic.
    """
    moment = datetime.now(UTC) + timedelta(seconds=seconds_from_now)
    return moment.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _http_status_error(status_code: int, retry_after: str | None = None) -> httpx.HTTPStatusError:
    """Build an ``httpx.HTTPStatusError`` carrying a status code and optional Retry-After header.

    The httpx constructor requires a real ``Request``/``Response`` pair (the
    requests-style ``HTTPError(response=...)`` idiom doesn't translate).
    The pattern mirrors the helper in ``tests/http_mock.py`` but is kept local
    to avoid pulling respx into a pure-function test.
    """
    request = httpx.Request("GET", "https://www.basketball-reference.com/test")
    headers: dict[str, str] = {}
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    response = httpx.Response(status_code, headers=headers, request=request)
    return httpx.HTTPStatusError(f"HTTP {status_code}", request=request, response=response)


# ─── _parse_retry_after ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", 0.0),
        ("30", 30.0),
        ("600", 600.0),
    ],
)
def test_parse_retry_after_integer_seconds(raw, expected):
    assert _parse_retry_after(raw) == pytest.approx(expected)


def test_parse_retry_after_float_seconds():
    # Floats encoded as a string (rare but valid) round-trip exactly.
    assert _parse_retry_after("12.5") == pytest.approx(12.5)


def test_parse_retry_after_future_http_date_is_positive():
    raw = _make_retry_after_date(seconds_from_now=120)
    parsed = _parse_retry_after(raw)
    assert parsed > 0.0
    # Allow generous slack for clock drift between the helper call and the
    # function call (the function reads ``datetime.now(UTC)`` internally).
    assert parsed == pytest.approx(120.0, abs=5.0)


def test_parse_retry_after_past_http_date_floors_to_one():
    # A date ten years in the past would yield a very negative wait.
    # The function clamps to 1.0s to prevent tight retry loops.
    raw = _make_retry_after_date(seconds_from_now=-10 * 365 * 24 * 3600)
    assert _parse_retry_after(raw) == pytest.approx(1.0)


@pytest.mark.parametrize("raw", ["not-a-date", ""])
def test_parse_retry_after_unparseable_returns_default(raw):
    assert _parse_retry_after(raw) == 5.0


def test_parse_retry_after_none_raises_typeerror():
    # The signature is `value: str`; the function does NOT handle ``None``
    # gracefully — ``float(None)`` raises ``TypeError`` (not ``ValueError``),
    # and the except clause only catches ``ValueError``. This documents the
    # current behaviour; callers are expected to pass a string.
    with pytest.raises(TypeError):
        _parse_retry_after(None)  # type: ignore


# ─── _should_retry ───────────────────────────────────────────────────────────


def test_should_retry_transport_error_returns_true():
    assert _should_retry(httpx.TransportError("connection reset")) is True


def test_should_retry_connect_error_returns_true():
    # ``httpx.ConnectError`` is a subclass of ``httpx.TransportError`` and
    # must hit the same retry branch.
    assert _should_retry(httpx.ConnectError("dns")) is True


def test_should_retry_429_with_retry_after_10_seconds():
    exc = _http_status_error(429, retry_after="10")
    assert _should_retry(exc) == pytest.approx(10.0)


def test_should_retry_429_with_retry_after_below_max_returns_parsed():
    # 30 < 60 (max cap) → return the parsed value verbatim.
    exc = _http_status_error(429, retry_after="30")
    assert _should_retry(exc) == pytest.approx(30.0)


def test_should_retry_429_with_retry_after_at_threshold():
    # 300 == threshold, NOT strictly greater → fall through to the cap path.
    # ``min(300, _MAX_RETRY_AFTER_WAIT=60) == 60``.
    exc = _http_status_error(429, retry_after=str(int(_JAIL_THRESHOLD_SECONDS)))
    assert _should_retry(exc) == pytest.approx(_MAX_RETRY_AFTER_WAIT)


def test_should_retry_429_with_retry_after_just_above_threshold_returns_false():
    # 301 > 300 → jail, do NOT retry. This is the boundary case that
    # determines the difference between "long wait" and "jailed".
    exc = _http_status_error(429, retry_after="301")
    assert _should_retry(exc) is False


def test_should_retry_429_with_retry_after_well_above_threshold_returns_false():
    # 600 > 300 → jail. The caller (``HTTPService._get``) catches the
    # HTTPStatusError separately and converts it into ``RateLimitJailed``.
    exc = _http_status_error(429, retry_after="600")
    assert _should_retry(exc) is False


def test_should_retry_429_with_retry_after_1000_returns_false():
    # The spec draft mentioned ``min(1000, 60) == 60``, but the predicate's
    # ``parsed > _JAIL_THRESHOLD_SECONDS`` check (300) intercepts first and
    # returns False. This test pins down the actual current behaviour.
    exc = _http_status_error(429, retry_after="1000")
    assert _should_retry(exc) is False


def test_should_retry_429_with_retry_after_capped_at_max():
    # 250 is between the cap (60) and the threshold (300) → ``min(250, 60) == 60``.
    # This documents the cap behaviour for the common case where Basketball-
    # Reference sends a moderate Retry-After.
    exc = _http_status_error(429, retry_after="250")
    assert _should_retry(exc) == pytest.approx(_MAX_RETRY_AFTER_WAIT)


@pytest.mark.parametrize("status_code", [502, 503, 504])
def test_should_retry_5xx_without_retry_after_returns_true(status_code):
    exc = _http_status_error(status_code)
    assert _should_retry(exc) is True


@pytest.mark.parametrize("status_code", [400, 403, 404])
def test_should_retry_other_4xx_returns_false(status_code):
    exc = _http_status_error(status_code)
    assert _should_retry(exc) is False


def test_should_retry_500_returns_false():
    # 500 is a server error but NOT in the retry-allowing set (429/502/503/504).
    # Basketball-Reference should never return a bare 500 in steady state, and
    # retrying could mask a real bug.
    exc = _http_status_error(500)
    assert _should_retry(exc) is False


@pytest.mark.parametrize("exc", [ValueError("not httpx"), RuntimeError("not httpx"), KeyError("k")])
def test_should_retry_non_httpx_exception_returns_false(exc):
    assert _should_retry(exc) is False
