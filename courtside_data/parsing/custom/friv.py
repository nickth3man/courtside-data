"""7-game playoff series outcome matrices (``friv_7_game_playoff_series_outcomes_*``).

The three endpoints all read the same single Basketball Reference
friv page — they just point at three different ``<table id="…">``
elements (``team-is-down``, ``team-is-tied``, ``team-is-up``). The shared
extraction logic lives in :func:`_friv_7_game_playoff_series_outcomes`;
each endpoint is a one-line wrapper that supplies the right ``table_id``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.parsing import rows
from courtside_data.parsing.generic import find_table

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

_FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_PATH = "/friv/7-game-playoff-series-outcomes-22111.html"

__all__ = [
    "_friv_7_game_playoff_series_outcomes",
    "friv_7_game_playoff_series_outcomes_team_is_down",
    "friv_7_game_playoff_series_outcomes_team_is_tied",
    "friv_7_game_playoff_series_outcomes_team_is_up",
]


def _friv_7_game_playoff_series_outcomes(facade: FetchFacade, table_id: str) -> list[dict[str, Any]]:
    """Return one of the three 7-game series outcome matrices.

    Fetches the single friv page once, locates the named ``<table>``,
    and walks ``tbody tr:not(.thead)`` rows that have ``<td>`` children
    through :func:`rows.parse_friv_playoff_outcomes_row`. Records a
    ``parse/friv_playoff_outcomes_parsed`` trace event with the row
    count and attaches ``raw_rows`` as an artifact for debug replay.
    """
    url = facade.url(_FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_PATH)
    selector = facade.get_selector(url=url)
    table = find_table(selector, table_id)
    if table is None:
        return []
    parsed_rows = [
        rows.parse_friv_playoff_outcomes_row(row) for row in table.css("tbody tr:not(.thead)") if row.css("td")
    ]
    trace = current_debug_trace()
    if trace is not None:
        trace.record("parse", "friv_playoff_outcomes_parsed", table_id=table_id, row_count=len(parsed_rows))
        trace.artifact("raw_rows", parsed_rows)
        emit_parser_diagnostics(
            trace,
            parser_name="friv_playoff_outcomes",
            rows=parsed_rows,
            source_sections=[f"table#{table_id}"],
            custom_diagnostics={"table_id": table_id},
        )
    return parsed_rows


def friv_7_game_playoff_series_outcomes_team_is_down(facade: FetchFacade) -> list[dict[str, Any]]:
    """Return the team-is-down matrix from the seven-game series outcomes page."""
    return _friv_7_game_playoff_series_outcomes(facade, "team-is-down")


def friv_7_game_playoff_series_outcomes_team_is_tied(facade: FetchFacade) -> list[dict[str, Any]]:
    """Return the team-is-tied matrix from the seven-game series outcomes page."""
    return _friv_7_game_playoff_series_outcomes(facade, "team-is-tied")


def friv_7_game_playoff_series_outcomes_team_is_up(facade: FetchFacade) -> list[dict[str, Any]]:
    """Return the team-is-up matrix from the seven-game series outcomes page."""
    return _friv_7_game_playoff_series_outcomes(facade, "team-is-up")
