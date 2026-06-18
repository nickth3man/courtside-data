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
    _player_season_box_score_rows,
    _player_totals_rows,
)
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


def regular_season_player_box_scores(
    facade: FetchFacade,
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
) -> list[dict[str, Any]]:
    """Return the regular-season game log for ``player_identifier``."""
    selector = _player_season_box_scores_selector(facade, player_identifier, season_end_year)
    table = find_table(selector, "player_game_log_reg")
    if table is None:
        raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

    return _player_season_box_score_rows(table, include_inactive_games=include_inactive_games)


def playoff_player_box_scores(
    facade: FetchFacade,
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
) -> list[dict[str, Any]]:
    """Return the playoff game log for ``player_identifier``."""
    selector = _player_season_box_scores_selector(facade, player_identifier, season_end_year)
    table = find_table(selector, "player_game_log_post")
    if table is None:
        raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

    return _player_season_box_score_rows(table, include_inactive_games=include_inactive_games)


def players_advanced_season_totals(
    facade: FetchFacade,
    season_end_year: int,
    include_combined_values: bool = False,
) -> list[dict[str, Any]]:
    """Return the league-wide advanced season totals table."""
    url = facade.url(f"/leagues/NBA_{season_end_year}_advanced.html")

    selector = facade.get_selector(url=url)
    return _player_totals_rows(selector, "advanced", include_combined=include_combined_values)


def players_season_totals(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return the league-wide regular season totals table (no combined-team rows)."""
    url = facade.url(f"/leagues/NBA_{season_end_year}_totals.html")

    selector = facade.get_selector(url=url)
    return _player_totals_rows(selector, "totals_stats", include_combined=False)
