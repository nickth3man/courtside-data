"""Playoff bracket endpoint (``playoff_bracket``).

Reads the ``/playoffs/NBA_{year}.html`` page and walks the single
``table#all_playoffs`` element. The row parser is a thin
:func:`rows.parse_playoff_bracket` shim around the table's ``<tbody>/<tr>``
hierarchy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data.parsing import rows
from courtside_data.parsing.generic import find_table

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = ["playoff_bracket"]


def playoff_bracket(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return the playoff bracket rows for ``season_end_year``."""
    url = facade.url(f"/playoffs/NBA_{season_end_year}.html")

    selector = facade.get_selector(url=url)
    table = find_table(selector, "all_playoffs")
    if table is None:
        return []
    return rows.parse_playoff_bracket(table)
