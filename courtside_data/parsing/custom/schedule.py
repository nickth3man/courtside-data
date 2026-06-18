"""Schedule endpoints (``season_schedule``, ``schedule_for_month``).

The season-schedule page (``/leagues/NBA_{year}_games.html``) is a
month-tabbed view: the "current" month's table is inline, and the other
months are sibling links in ``div#content div.filter
div:not([class*="current"]) a``. The handler reads the current month
first, then iterates every other month link and reads its page in
turn, accumulating the rows.

The per-month endpoint is exposed publicly (``schedule_for_month``) so
the runner can dispatch it when only a single month's page is wanted
(the generic registry path is also available via
:func:`courtside_data.parsing.generic.GenericEndpointHandler.fetch_table`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data.parsing.custom._common import _schedule_rows

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = ["schedule_for_month", "season_schedule"]


def schedule_for_month(facade: FetchFacade, url: str) -> list[dict[str, Any]]:
    """Return the schedule rows for one month page at absolute ``url``."""
    return _schedule_rows(facade.get_selector(url=url))


def season_schedule(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return the schedule rows for every month of ``season_end_year``.

    Reads the season index page (the inline current month is the first
    batch) and then walks the month links in ``div.filter`` to read the
    other months.
    """
    url = facade.url(f"/leagues/NBA_{season_end_year}_games.html")

    selector = facade.get_selector(url=url)
    season_schedule_values = _schedule_rows(selector)

    for month_url_path in [
        link.attrib["href"] for link in selector.css('div#content div.filter div:not([class*="current"]) a')
    ]:
        url = facade.url(month_url_path)
        monthly_schedule = schedule_for_month(facade, url=url)
        season_schedule_values.extend(monthly_schedule)

    return season_schedule_values
