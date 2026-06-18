"""Tests for the strict-first, dateparser-fallback date/datetime validators.

Covers :func:`courtside_data.schemas._fields._br_date` and
:func:`courtside_data.schemas._fields._br_datetime`, plus the
``BRDate`` / ``BRDatetime`` :class:`Annotated` aliases that expose them
to pydantic models.

The project's contract: **strict first, tolerant fallback**. The
hard-coded ``strptime`` formats must still parse unchanged (no behavior
change for the common case); drifted formats now route through
``dateparser``; and genuinely unparseable inputs still raise.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest
from courtside_data.schemas._fields import (
    BRDate,
    BRDatetime,
    _br_date,
    _br_datetime,
)

# ---------------------------------------------------------------------------
# (a) Strict formats — unchanged behavior
# ---------------------------------------------------------------------------


class TestBrDateStrict:
    def test_br_weekday_format(self) -> None:
        assert _br_date("Mon, Jan 01, 2024") == date(2024, 1, 1)

    def test_br_iso_format(self) -> None:
        assert _br_date("2024-01-01") == date(2024, 1, 1)

    def test_date_passthrough(self) -> None:
        d = date(2024, 1, 1)
        assert _br_date(d) is d

    def test_datetime_passthrough_returns_date(self) -> None:
        # A datetime input returns its .date() part — no midnight normalization
        dt = datetime(2024, 1, 1, 15, 30, tzinfo=UTC)
        assert _br_date(dt) == date(2024, 1, 1)


class TestBrDatetimeStrict:
    def test_weekday_with_pm_time(self) -> None:
        # 8:30 PM US/Eastern on Jan 1, 2024 == 01:30 UTC on Jan 2, 2024
        # (US/Eastern is UTC-5 in January / standard time).
        result = _br_datetime(("Mon, Jan 01, 2024", "8:30 PM"))
        assert result == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)
        assert result.tzinfo is UTC

    def test_weekday_with_am_time(self) -> None:
        result = _br_datetime(("Mon, Jan 01, 2024", "9:30 AM"))
        assert result == datetime(2024, 1, 1, 14, 30, tzinfo=UTC)
        assert result.tzinfo is UTC

    def test_weekday_with_p_suffix(self) -> None:
        # Newer BR format: "8:30p" (no "m"); validator adds the "m" for %p.
        result = _br_datetime(("Mon, Jan 01, 2024", "8:30p"))
        assert result == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)

    def test_weekday_with_a_suffix(self) -> None:
        result = _br_datetime(("Mon, Jan 01, 2024", "9:30a"))
        assert result == datetime(2024, 1, 1, 14, 30, tzinfo=UTC)

    def test_empty_time_of_day(self) -> None:
        # No time component → midnight US/Eastern.
        result = _br_datetime(("Mon, Jan 01, 2024", ""))
        assert result == datetime(2024, 1, 1, 5, 0, tzinfo=UTC)

    def test_single_string_input(self) -> None:
        # When the value is a single string, time_of_day is None and defaults
        # to midnight US/Eastern.
        result = _br_datetime("Mon, Jan 01, 2024")
        assert result == datetime(2024, 1, 1, 5, 0, tzinfo=UTC)

    def test_datetime_passthrough_is_converted_to_utc(self) -> None:
        # Aware non-UTC datetime is converted to UTC, not stripped.
        eastern = ZoneInfo("US/Eastern")
        dt = datetime(2024, 1, 1, 8, 30, tzinfo=eastern)
        result = _br_datetime(dt)
        assert result.tzinfo is UTC
        assert result == datetime(2024, 1, 1, 13, 30, tzinfo=UTC)

    def test_tuple_must_have_length_two(self) -> None:
        with pytest.raises(ValueError, match="Invalid datetime value"):
            _br_datetime(("Mon, Jan 01, 2024", "8:30 PM", "extra"))


# ---------------------------------------------------------------------------
# (b) Tolerant fallback — drifted / new date formats
# ---------------------------------------------------------------------------


class TestBrDateFallback:
    @pytest.mark.parametrize(
        "raw",
        [
            "January 1, 2024",
            "Jan 1, 2024",
            "1/1/2024",
            "01 Jan 2024",
            "Jan 1 2024",
        ],
    )
    def test_drifted_formats_parse_via_fallback(self, raw: str) -> None:
        assert _br_date(raw) == date(2024, 1, 1)

    def test_fallback_returns_date_not_datetime(self) -> None:
        result = _br_date("January 1, 2024")
        assert type(result) is date  # not datetime

    def test_whitespace_is_tolerated(self) -> None:
        # The strict path strips first; the fallback should still cope with
        # leading/trailing whitespace if any sneaks through.
        assert _br_date("  January 1, 2024  ") == date(2024, 1, 1)


class TestBrDatetimeFallback:
    def test_drifted_date_with_strict_time(self) -> None:
        # Date format drifted; time component is still the standard "8:30 PM".
        result = _br_datetime(("January 1, 2024", "8:30 PM"))
        assert result == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)
        assert result.tzinfo is UTC

    def test_drifted_date_with_drifted_time(self) -> None:
        # Both date AND time have drifted away from the strict formats.
        result = _br_datetime(("January 1, 2024", "8:30PM"))
        assert result == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)

    def test_drifted_date_with_24h_time(self) -> None:
        # 24-hour time component (no AM/PM) on a drifted date.
        result = _br_datetime(("January 1, 2024", "20:30"))
        assert result == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)

    def test_fallback_preserves_us_eastern_to_utc_conversion(self) -> None:
        # The fallback MUST apply the same US/Eastern → UTC conversion as the
        # strict path. A 8:30 PM local time in January (EST = UTC-5) becomes
        # 01:30 UTC the next day.
        result = _br_datetime(("Jan 1, 2024", "8:30 PM"))
        assert result == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)

    def test_fallback_with_empty_time(self) -> None:
        # Drifted date, no time-of-day → midnight US/Eastern.
        result = _br_datetime(("January 1, 2024", ""))
        assert result == datetime(2024, 1, 1, 5, 0, tzinfo=UTC)

    def test_fallback_with_single_string_input(self) -> None:
        result = _br_datetime("January 1, 2024")
        assert result == datetime(2024, 1, 1, 5, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# (c) Unparseable inputs — still raise
# ---------------------------------------------------------------------------


class TestUnparseableInputs:
    @pytest.mark.parametrize("raw", ["", "not a date", "xyz123", "   "])
    def test_br_date_raises_for_unparseable(self, raw: str) -> None:
        with pytest.raises(ValueError, match="Invalid date value"):
            _br_date(raw)

    @pytest.mark.parametrize(
        "raw",
        [
            ("not a date", "8:30 PM"),
            ("Mon, Jan 01, 2024", "not a time"),
            ("January 1, 2024", "garbage"),
        ],
    )
    def test_br_datetime_raises_for_unparseable(self, raw: tuple[str, str]) -> None:
        with pytest.raises(ValueError, match="Invalid datetime value"):
            _br_datetime(raw)


# ---------------------------------------------------------------------------
# Annotation types — pydantic integration
# ---------------------------------------------------------------------------


class TestAnnotations:
    def test_br_date_typed_model(self) -> None:
        from pydantic import BaseModel

        class M(BaseModel):
            d: BRDate

        m = M(d="Mon, Jan 01, 2024")  # type: ignore
        assert m.d == date(2024, 1, 1)
        assert type(m.d) is date

    def test_br_date_fallback_via_pydantic(self) -> None:
        from pydantic import BaseModel

        class M(BaseModel):
            d: BRDate

        m = M(d="January 1, 2024")  # type: ignore
        assert m.d == date(2024, 1, 1)

    def test_br_datetime_typed_model(self) -> None:
        from pydantic import BaseModel

        class M(BaseModel):
            dt: BRDatetime

        m = M(dt=("Mon, Jan 01, 2024", "8:30 PM"))  # type: ignore
        assert m.dt == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)
        assert m.dt.tzinfo is UTC

    def test_br_datetime_fallback_via_pydantic(self) -> None:
        from pydantic import BaseModel

        class M(BaseModel):
            dt: BRDatetime

        m = M(dt=("January 1, 2024", "8:30 PM"))  # type: ignore
        assert m.dt == datetime(2024, 1, 2, 1, 30, tzinfo=UTC)
