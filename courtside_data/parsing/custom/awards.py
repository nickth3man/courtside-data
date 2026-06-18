"""Awards voting endpoint (``season_awards_voting``).

The ``/awards/awards_{year}.html`` page carries one ``<table>`` per
NBA award; the table id is derived from the ``award`` parameter
(lowercased, dashes turned into underscores). An unknown award id
yields an empty list (the runner's schema-drift check fires on the
upstream ``TypeAdapter`` call, not on the missing-table path).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data.parsing import rows
from courtside_data.parsing.generic import find_table

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = ["season_awards_voting"]


def season_awards_voting(facade: FetchFacade, season_end_year: int, award: str) -> list[dict[str, Any]]:
    """Return one award voting table from ``/awards/awards_{year}.html``."""
    table_id = award.strip().lower().replace("-", "_")
    selector = facade.get_selector(facade.url(f"/awards/awards_{season_end_year}.html"))
    table = find_table(selector, table_id)
    if table is None:
        return []
    return [row for row, _ in rows.raw_rows_from_table(table)]
