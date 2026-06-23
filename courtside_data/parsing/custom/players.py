"""Per-player endpoints (``regular_season_player_box_scores``,
``playoff_player_box_scores``, ``players_season_totals``,
``players_advanced_season_totals``).

The four endpoints split into two families:

* The per-game-log endpoints read ``/players/{id[0]}/{id}/gamelog/{year}``
  and pull either the ``player_game_log_reg`` or ``player_game_log_post``
  table through :func:`courtside_data.parsing.custom._common._player_season_box_score_rows`.
  Both raise :class:`InvalidPlayerAndSeason` when the page is missing
  (404) or the expected table isn't there.
* The two league-wide season-totals endpoints read
  ``/leagues/NBA_{year}_totals.html`` and
  ``/leagues/NBA_{year}_advanced.html`` and run them through
  :func:`courtside_data.parsing.custom._common._player_totals_rows`.
  The advanced variant tags every multi-team row with
  ``is_combined_totals`` for downstream filtering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from parsel import Selector

from courtside_data.errors import InvalidPlayerAndSeason
from courtside_data.parsing.custom._common import (
    _player_season_box_score_rows_with_stats,
    _player_totals_rows_with_stats,
)
from courtside_data.parsing.custom._diagnostics import emit_custom_endpoint_diagnostics
from courtside_data.parsing.generic import find_table

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = [
    "players_advanced_season_totals",
    "players_season_totals",
    "playoff_player_box_scores",
    "regular_season_player_box_scores",
]


def _player_season_box_scores_selector(facade: FetchFacade, player_identifier: str, season_end_year: int) -> Selector:
    """Fetch the per-player season game-log page (one per endpoint)."""
    url = facade.url(f"/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}")
    return facade.get_selector(url=url)


def _emit_player_game_log_diagnostics(
    *,
    parser_name: str,
    endpoint_name: str,
    parsed_rows: list[dict[str, Any]],
    stats: dict[str, Any],
    table_id: str,
) -> None:
    stats = {
        **stats,
        "season_count": 1,
        "selected_table_id": table_id,
    }
    emit_custom_endpoint_diagnostics(
        parser_name=parser_name,
        endpoint_name=endpoint_name,
        rows=parsed_rows,
        source_sections=[f"table#{table_id}"],
        stats=stats,
        selected_table_id=table_id,
        candidate_table_ids=[table_id],
    )


def regular_season_player_box_scores(
    facade: FetchFacade,
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
) -> list[dict[str, Any]]:
    """Return the regular-season game log for ``player_identifier``."""
    selector = _player_season_box_scores_selector(facade, player_identifier, season_end_year)
    table_id = "player_game_log_reg"
    table = find_table(selector, table_id)
    if table is None:
        raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

    parsed_rows, stats = _player_season_box_score_rows_with_stats(table, include_inactive_games=include_inactive_games)
    _emit_player_game_log_diagnostics(
        parser_name="regular_season_player_box_scores",
        endpoint_name="regular_season_player_box_scores",
        parsed_rows=parsed_rows,
        stats=stats,
        table_id=table_id,
    )
    return parsed_rows


def playoff_player_box_scores(
    facade: FetchFacade,
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
) -> list[dict[str, Any]]:
    """Return the playoff game log for ``player_identifier``."""
    selector = _player_season_box_scores_selector(facade, player_identifier, season_end_year)
    table_id = "player_game_log_post"
    table = find_table(selector, table_id)
    if table is None:
        raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

    parsed_rows, stats = _player_season_box_score_rows_with_stats(table, include_inactive_games=include_inactive_games)
    _emit_player_game_log_diagnostics(
        parser_name="playoff_player_box_scores",
        endpoint_name="playoff_player_box_scores",
        parsed_rows=parsed_rows,
        stats=stats,
        table_id=table_id,
    )
    return parsed_rows


def players_advanced_season_totals(
    facade: FetchFacade,
    season_end_year: int,
    include_combined_values: bool = False,
) -> list[dict[str, Any]]:
    """Return the league-wide advanced season totals table."""
    url = facade.url(f"/leagues/NBA_{season_end_year}_advanced.html")

    selector = facade.get_selector(url=url)
    table_id = "advanced"
    parsed_rows, stats = _player_totals_rows_with_stats(selector, table_id, include_combined=include_combined_values)
    emit_custom_endpoint_diagnostics(
        parser_name="players_advanced_season_totals",
        endpoint_name="players_advanced_season_totals",
        rows=parsed_rows,
        source_sections=[f"table#{table_id}"],
        stats=stats,
        selected_table_id=table_id,
        candidate_table_ids=[table_id],
    )
    return parsed_rows


def players_season_totals(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return the league-wide regular season totals table (no combined-team rows)."""
    url = facade.url(f"/leagues/NBA_{season_end_year}_totals.html")

    selector = facade.get_selector(url=url)
    table_id = "totals_stats"
    parsed_rows, stats = _player_totals_rows_with_stats(selector, table_id, include_combined=False)
    emit_custom_endpoint_diagnostics(
        parser_name="players_season_totals",
        endpoint_name="players_season_totals",
        rows=parsed_rows,
        source_sections=[f"table#{table_id}"],
        stats=stats,
        selected_table_id=table_id,
        candidate_table_ids=[table_id],
    )
    return parsed_rows
