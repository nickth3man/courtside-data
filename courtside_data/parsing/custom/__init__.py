"""Bespoke (``custom=True``) endpoint handlers — domain-split package.

The package contains the per-domain free functions used by the
:class:`CustomEndpointHandler` dispatcher, plus the dispatcher itself.

The legacy monolithic :mod:`courtside_data.parsing.custom` module grew
to ~300 LOC and reached into private members of
:class:`~courtside_data.http_service.HTTPService` from every method.
Phase 4 of the courtside-data refactor reverses that coupling by:

1. Introducing :class:`~courtside_data.parsing.custom._fetch.FetchFacade`
   — the public surface bespoke handlers use to talk to the transport.
2. Splitting the per-endpoint logic into per-domain modules under
   :mod:`courtside_data.parsing.custom` (one module per BR page family).
3. Turning the four shared ``_xxx_rows`` helpers into free functions in
   :mod:`courtside_data.parsing.custom._common`.
4. Re-introducing :class:`CustomEndpointHandler` here as a thin
   dispatcher — one method per endpoint, each delegating to a domain
   function with a :class:`FetchFacade` in hand.

The public surface is unchanged: ``from courtside_data.parsing.custom
import CustomEndpointHandler, dispatch_custom_endpoint`` still works
and every method signature is preserved exactly (the runner reflects
on the dispatcher via :func:`inspect.signature` to drive param
coercion).
"""

from __future__ import annotations

from typing import Any

from courtside_data.data import Team
from courtside_data.http_service import HTTPService
from courtside_data.parsing.custom import (
    awards,
    boxscores,
    friv,
    players,
    playoffs,
    schedule,
    search,
    standings,
)
from courtside_data.parsing.custom._fetch import FetchFacade
from courtside_data.schemas._fields import _team_field

__all__ = [
    "CustomEndpointHandler",
    "dispatch_custom_endpoint",
]


class CustomEndpointHandler:
    """Slim dispatcher that delegates each endpoint to a domain function.

    The handler holds one :class:`FetchFacade` for the lifetime of the
    instance. Each public method is a one-liner that forwards to the
    free function in the matching domain module; the method signatures
    must stay byte-for-byte identical to the historic
    :class:`CustomEndpointHandler` so :func:`inspect.signature`-driven
    param coercion in :mod:`courtside_data.client._runtime._coerce`
    continues to work.
    """

    def __init__(self, http: HTTPService) -> None:
        self._http = http
        self._fetch = FetchFacade(http)

    # ── friv (3 endpoints, one private helper) ─────────────────────────
    def _friv_7_game_playoff_series_outcomes(self, table_id: str) -> list[dict[str, Any]]:
        return friv._friv_7_game_playoff_series_outcomes(self._fetch, table_id=table_id)

    def friv_7_game_playoff_series_outcomes_team_is_down(self) -> list[dict[str, Any]]:
        """Return the team-is-down matrix from the seven-game series outcomes page."""
        return friv._friv_7_game_playoff_series_outcomes(self._fetch, "team-is-down")

    def friv_7_game_playoff_series_outcomes_team_is_tied(self) -> list[dict[str, Any]]:
        """Return the team-is-tied matrix from the seven-game series outcomes page."""
        return friv._friv_7_game_playoff_series_outcomes(self._fetch, "team-is-tied")

    def friv_7_game_playoff_series_outcomes_team_is_up(self) -> list[dict[str, Any]]:
        """Return the team-is-up matrix from the seven-game series outcomes page."""
        return friv._friv_7_game_playoff_series_outcomes(self._fetch, "team-is-up")

    # ── awards ──────────────────────────────────────────────────────────
    def season_awards_voting(self, season_end_year: int, award: str) -> list[dict[str, Any]]:
        """Return one award voting table from ``/awards/awards_{year}.html``."""
        return awards.season_awards_voting(self._fetch, season_end_year=season_end_year, award=award)

    # ── standings ───────────────────────────────────────────────────────
    def standings(self, season_end_year: int) -> list[dict[str, Any]]:
        return standings.standings(self._fetch, season_end_year=season_end_year)

    def standings_by_date(self, season_end_year: int) -> list[dict[str, Any]]:
        return standings.standings_by_date(self._fetch, season_end_year=season_end_year)

    # ── boxscores (4 endpoints: player_box_scores, team_box_score(s), play_by_play) ──
    def player_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        return boxscores.player_box_scores(self._fetch, day=day, month=month, year=year)

    def team_box_score(self, game_url_path: str) -> list[dict[str, Any]]:
        return boxscores.team_box_score(self._fetch, game_url_path=game_url_path)

    def team_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        return boxscores.team_box_scores(self._fetch, day=day, month=month, year=year)

    def play_by_play(self, home_team: Team, day: int, month: int, year: int) -> list[dict[str, Any]]:
        if isinstance(home_team, str):
            home_team = _team_field(home_team)
        return boxscores.play_by_play(self._fetch, home_team=home_team, day=day, month=month, year=year)

    # ── players (4 endpoints) ──────────────────────────────────────────
    def regular_season_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        return players.regular_season_player_box_scores(
            self._fetch,
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )

    def playoff_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        return players.playoff_player_box_scores(
            self._fetch,
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )

    def players_advanced_season_totals(
        self, season_end_year: int, include_combined_values: bool = False
    ) -> list[dict[str, Any]]:
        return players.players_advanced_season_totals(
            self._fetch,
            season_end_year=season_end_year,
            include_combined_values=include_combined_values,
        )

    def players_season_totals(self, season_end_year: int) -> list[dict[str, Any]]:
        return players.players_season_totals(self._fetch, season_end_year=season_end_year)

    # ── playoffs ────────────────────────────────────────────────────────
    def playoff_bracket(self, season_end_year: int) -> list[dict[str, Any]]:
        return playoffs.playoff_bracket(self._fetch, season_end_year=season_end_year)

    # ── schedule ────────────────────────────────────────────────────────
    def schedule_for_month(self, url: str) -> list[dict[str, Any]]:
        return schedule.schedule_for_month(self._fetch, url=url)

    def season_schedule(self, season_end_year: int) -> list[dict[str, Any]]:
        return schedule.season_schedule(self._fetch, season_end_year=season_end_year)

    # ── search ──────────────────────────────────────────────────────────
    def search(self, term: str) -> dict[str, list[dict[str, Any]]]:
        return search.search(self._fetch, term=term)


def dispatch_custom_endpoint(http: HTTPService, name: str, **params: Any) -> Any:
    """Invoke a bespoke endpoint handler by registry name.

    The runner passes the resolved :class:`HTTPService` and the
    endpoint name; the function constructs one
    :class:`CustomEndpointHandler` per call and resolves the named
    method through ``getattr`` (the same dispatch shape as the historic
    free function).
    """
    handler = CustomEndpointHandler(http)
    return getattr(handler, name)(**params)
