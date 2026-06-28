"""Tests for calendar-based NBA season-end-year resolution.

Covers :func:`courtside_data.domain.seasons.current_nba_season_end_year`
which the Team Hub (and any other hub that needs a calendar-driven default
season) uses to anchor its "current season" pick on the calendar date.

The cutoff is October 1: on/after it, the new season starting that October
is considered current (its end year is ``today.year + 1``); before it, the
most-recent season ended in spring of ``today.year``.
"""

from __future__ import annotations

from datetime import date

import pytest
from courtside_data.domain.seasons import current_nba_season_end_year


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        (date(2026, 6, 27), 2026),  # playoffs of 2025-26 season
        (date(2026, 7, 15), 2026),  # offseason, most-recent = 2025-26
        (date(2026, 9, 30), 2026),  # last day of offseason (pre-cutoff)
        (date(2026, 10, 1), 2027),  # 2026-27 season deemed current
        (date(2025, 11, 1), 2026),  # 2025-26 season just started
        (date(2025, 1, 5), 2025),  # 2024-25 in progress
    ],
)
def test_current_nba_season_end_year(today: date, expected: int) -> None:
    """The resolver picks the end-year of the current or most-recent NBA season."""
    assert current_nba_season_end_year(today) == expected


def test_current_nba_season_end_year_defaults_to_today() -> None:
    """When no date is provided, the resolver uses ``date.today()``."""
    # Just verify it returns an int; we don't pin the value because
    # ``date.today()`` is calendar-dependent at runtime.
    result = current_nba_season_end_year()
    assert isinstance(result, int)
    # And it must be within ±1 of the calendar year, since the
    # resolver's output is at most one off from ``date.today().year``.
    from datetime import date as _date

    today = _date.today()
    assert result in (today.year - 1, today.year, today.year + 1)
