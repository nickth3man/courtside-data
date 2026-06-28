"""Calendar helpers for NBA season-end-year resolution.

The Team Hub and any other hub that needs a calendar-driven "current
season" pick can use :func:`current_nba_season_end_year` to anchor on the
calendar date without depending on a hard-coded year.
"""

from __future__ import annotations

import re
from datetime import date

# October is the regular-season tip-off month; the season starting in
# October of year ``Y-1`` ends in spring of year ``Y`` (its
# ``season_end_year == Y``).
_SEASON_START_MONTH = 10

# Matches Basketball-Reference season strings like ``"2024-25"``,
# ``"1999-00"`` (the two-digit year-end of a millennium boundary),
# and the all-time "1999-2000" four-digit spelling. Returns the
# end-year as an integer (``2025``, ``2000``).
SEASON_RE = re.compile(r"^(?P<start>\d{4})-(?P<end>\d{2,4})$")


def current_nba_season_end_year(today: date | None = None) -> int:
    """End-year of the current or most-recently-completed NBA season.

    The season starting in October of year ``Y`` ends in spring of
    ``Y + 1``, so its ``season_end_year == Y + 1``. The cutoff is
    October 1: on/after that date, the new season is considered
    current (end year ``today.year + 1``); before it, the most-recent
    season ended in spring of ``today.year``.

    Pass an explicit ``today`` to make the call deterministic in
    tests; omit it to use the system date.
    """
    today = today or date.today()
    return today.year + 1 if today.month >= _SEASON_START_MONTH else today.year


def season_end_year(season: object) -> int | None:
    """Parse a Basketball-Reference season string into an end-year.

    Accepts the BR spelling ``"YYYY-YY"`` (``"2024-25"`` -> ``2025``)
    and the four-digit form ``"YYYY-YYYY"`` (``"1999-2000"`` -> ``2000``).
    Returns ``None`` for any other input (including ``None`` and
    non-string types).
    """
    if not isinstance(season, str):
        return None
    match = SEASON_RE.match(season)
    if match is None:
        return None
    start_year = int(match.group("start"))
    end_str = match.group("end")
    if len(end_str) == 2:
        century = start_year // 100 * 100
        candidate = century + int(end_str)
        if candidate <= start_year:
            candidate += 100
        return candidate
    # Four-digit end-year (``"1999-2000"``): just return it as an int.
    return int(end_str)


__all__ = ["current_nba_season_end_year", "season_end_year"]
