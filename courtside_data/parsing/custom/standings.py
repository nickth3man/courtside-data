"""League-wide standings endpoints (``standings``, ``standings_by_date``).

Both endpoints render the NBA's per-conference standings but at different
URLs and on different table shapes: ``standings`` reads the single
``/leagues/NBA_{year}.html`` page (which carries both the East and West
tables inline) and walks them via :func:`rows.parse_standings`;
``standings_by_date`` reads the template-driven ``/leagues/NBA_{year}_standings_by_date_…``
pages (one per conference) and flattens the rows with a manually
attached ``"conference"`` key.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data.endpoints import ENDPOINTS
from courtside_data.parsing import rows
from courtside_data.parsing.tables import GenericTable

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = ["standings", "standings_by_date"]


def standings(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return both-conference standings for ``season_end_year``."""
    url = facade.url(f"/leagues/NBA_{season_end_year}.html")
    selector = facade.get_selector(url=url)
    return rows.parse_standings(selector)


def standings_by_date(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return the standings on the season's last day, tagged with conference.

    The registry's ``standings_by_date`` path template embeds an internal
    ``conference`` placeholder (not exposed as a public call param); this
    function iterates the two conferences, fetches each page, and flattens
    every table row with a ``"conference"`` key set to the human name
    ("Eastern" / "Western").
    """
    endpoint = ENDPOINTS["standings_by_date"]
    standings_rows: list[dict[str, Any]] = []
    for conference, conference_name in [
        ("eastern_conference", "Eastern"),
        ("western_conference", "Western"),
    ]:
        url = facade.url(endpoint.path.format(season_end_year=season_end_year, conference=conference))
        selector = facade.get_selector(url=url)
        table_selector = selector.css(f"table#{endpoint.table_id}")
        if table_selector:
            table = GenericTable(table_selector[0])
            for row in table.rows:
                standings_rows.append({"conference": conference_name, **row.to_dict()})
    return standings_rows
