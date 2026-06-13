"""Declarative registry for generic ("beta") Basketball Reference endpoints.

Each :class:`TableEndpoint` captures everything that distinguishes one
table-scraping endpoint from another: the URL path template, how to locate the
table on the page, which CSV columns the output contract promises, and which
domain error a failed lookup maps to. ``HTTPService.fetch_table`` and the
generated client functions consume these specs, so adding a new endpoint is a
single registry entry.

Path and table-id templates are ``str.format`` templates over the endpoint's
call parameters, e.g. ``"/players/{player_identifier[0]}/{player_identifier}.html"``.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from courtside_data.schemas._base import BRRow

from courtside_data.errors import (
    InvalidDate,
    InvalidPlayer,
    InvalidPlayerAndSeason,
    InvalidSearch,
    InvalidSeason,
    InvalidTeam,
)
from courtside_data.output.columns import (
    ATTENDANCE_COLUMN_NAMES,
    BOX_SCORE_COLUMN_NAMES,
    CAREER_LEADERS_COLUMN_NAMES,
    DRAFT_PICKS_COLUMN_NAMES,
    FRANCHISE_HISTORY_COLUMN_NAMES,
    LEAGUE_PER_36_COLUMN_NAMES,
    LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES,
    LEAGUE_PER_GAME_COLUMN_NAMES,
    LEAGUE_SHOOTING_COLUMN_NAMES,
    LEAGUE_TOTALS_COLUMN_NAMES,
    LEAGUE_TRANSACTIONS_COLUMN_NAMES,
    PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES,
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_ALL_STAR_COLUMN_NAMES,
    PLAYER_CAREER_STATS_COLUMN_NAMES,
    PLAYER_GAME_HIGHS_COLUMN_NAMES,
    PLAYER_ON_OFF_COLUMN_NAMES,
    PLAYER_PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_PLAYOFF_SERIES_COLUMN_NAMES,
    PLAYER_SALARIES_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SHOT_CHARTS_COLUMN_NAMES,
    PLAYER_SIMILARITY_SCORES_COLUMN_NAMES,
    PLAYER_SPLITS_COLUMN_NAMES,
    PLAYOFF_BRACKET_COLUMN_NAMES,
    PLAYOFF_PER_GAME_COLUMN_NAMES,
    PLAYOFF_TOTALS_COLUMN_NAMES,
    ROOKIE_STATS_COLUMN_NAMES,
    SCHEDULE_COLUMN_NAMES,
    SEASON_AWARDS_COLUMN_NAMES,
    SEASON_LEADERS_COLUMN_NAMES,
    STANDINGS_BY_DATE_COLUMN_NAMES,
    STANDINGS_COLUMNS_NAMES,
    TEAM_AND_OPPONENT_COLUMN_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
    TEAM_CONTRACTS_COLUMN_NAMES,
    TEAM_INJURY_REPORT_COLUMN_NAMES,
    TEAM_LINEUPS_COLUMN_NAMES,
    TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES,
    TEAM_ON_OFF_COLUMN_NAMES,
    TEAM_OPPONENT_STATS_COLUMN_NAMES,
    TEAM_ROSTER_COLUMN_NAMES,
    TEAM_SCHEDULE_COLUMN_NAMES,
    TEAM_SPLITS_COLUMN_NAMES,
    TEAM_STARTING_LINEUPS_COLUMN_NAMES,
    TEAM_TRANSACTIONS_COLUMN_NAMES,
)
from courtside_data.schemas import (
    boxscores,
    draft,
    league,
    playbyplay,
    players,
    playoffs,
    schedule,
    search,
    standings,
    teams,
)

NOT_FOUND = (int(httpx.codes.NOT_FOUND),)
NOT_FOUND_OR_SERVER_ERROR = (int(httpx.codes.NOT_FOUND), int(httpx.codes.INTERNAL_SERVER_ERROR))


@dataclass(frozen=True, slots=True)
class TableEndpoint:
    """Spec for one generic table endpoint.

    Table lookup order in ``HTTPService.fetch_table``:
    1. ``table_id`` via a CSS ``table#<id>`` query (if set),
    2. ``commented_table_id`` via :func:`extract_commented_table` (if set),
    3. transaction-list fallback (if ``transaction_list_fallback``),
    4. otherwise an empty result.
    """

    path: str
    # Ordered call-parameter names; defines the positional argument order of
    # the generated HTTPService delegates and client functions.
    params: tuple[str, ...] = ()
    table_id: str | None = None
    commented_table_id: str | None = None
    use_header_fallback: bool = False
    transaction_list_fallback: bool = False
    # True for endpoints with a bespoke HTTPService method (e.g. multi-request);
    # fetch_table() must not be used for these.
    custom: bool = False
    # If set, the runner validates each extracted row with this BRRow subclass
    # instead of the legacy coerce_data/validate_rows path. Endpoints with
    # row_model=None keep the legacy pipeline (strangler-fig coexistence).
    row_model: type[BRRow] | None = None
    # When set, fetch_table() projects each row down to exactly these keys
    # (missing keys become empty strings).
    projection: tuple[str, ...] | None = None
    csv_columns: Sequence[str] | None = None
    error: type[Exception] | None = None
    error_params: tuple[str, ...] = ()
    error_status_codes: tuple[int, ...] = NOT_FOUND

    def error_mappings(self, params: dict[str, object]) -> dict[int, Callable[[], Exception]] | None:
        """Build the per-call ``{status_code: exception_factory}`` mapping."""
        if self.error is None:
            return None
        error = self.error
        bound = {name: params[name] for name in self.error_params}

        def factory() -> Exception:
            return error(**bound)

        return dict.fromkeys(self.error_status_codes, factory)


def _endpoint(
    path: str,
    *,
    params: tuple[str, ...],
    error: type[Exception] | None,
    error_params: tuple[str, ...],
    error_status_codes: tuple[int, ...] = NOT_FOUND,
    table_id: str | None = None,
    commented_table_id: str | None = None,
    use_header_fallback: bool = False,
    transaction_list_fallback: bool = False,
    custom: bool = False,
    row_model: type[BRRow] | None = None,
    projection: tuple[str, ...] | None = None,
    csv_columns: Sequence[str] | None = None,
) -> TableEndpoint:
    return TableEndpoint(
        path=path,
        params=params,
        table_id=table_id,
        commented_table_id=commented_table_id,
        use_header_fallback=use_header_fallback,
        transaction_list_fallback=transaction_list_fallback,
        custom=custom,
        row_model=row_model,
        projection=projection,
        csv_columns=csv_columns,
        error=error,
        error_params=error_params,
        error_status_codes=error_status_codes,
    )


def _season(path: str, params: tuple[str, ...] = ("season_end_year",), **overrides: Any) -> TableEndpoint:
    return _endpoint(
        path,
        params=params,
        error=InvalidSeason,
        error_params=("season_end_year",),
        **overrides,
    )


def _team(
    path: str, params: tuple[str, ...] = ("team_abbreviation", "season_end_year"), **overrides: Any
) -> TableEndpoint:
    return _endpoint(
        path,
        params=params,
        error=InvalidTeam,
        error_params=("team_abbreviation",),
        **overrides,
    )


def _player(path: str, params: tuple[str, ...] = ("player_identifier",), **overrides: Any) -> TableEndpoint:
    return _endpoint(
        path,
        params=params,
        error=InvalidPlayer,
        error_params=("player_identifier",),
        **overrides,
    )


_PLAYER_PAGE = "/players/{player_identifier[0]}/{player_identifier}.html"

ENDPOINTS: dict[str, TableEndpoint] = {
    # ── League-wide season tables ──
    "league_per_game_stats": _season(
        "/leagues/NBA_{season_end_year}_per_game.html",
        table_id="per_game_stats",
        row_model=league.LeaguePerGameStatsRow,
        csv_columns=LEAGUE_PER_GAME_COLUMN_NAMES,
    ),
    "league_per_36_minutes": _season(
        "/leagues/NBA_{season_end_year}_per_minute.html",
        table_id="per_minute_stats",
        row_model=league.LeaguePer36MinutesRow,
        csv_columns=LEAGUE_PER_36_COLUMN_NAMES,
    ),
    "league_totals": _season(
        "/leagues/NBA_{season_end_year}_totals.html",
        table_id="totals_stats",
        row_model=league.LeagueTotalsRow,
        csv_columns=LEAGUE_TOTALS_COLUMN_NAMES,
    ),
    "league_per_100_possessions": _season(
        "/leagues/NBA_{season_end_year}_per_poss.html",
        table_id="per_poss",
        row_model=league.LeaguePer100PossessionsRow,
        csv_columns=LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES,
    ),
    "league_shooting": _season(
        "/leagues/NBA_{season_end_year}_shooting.html",
        table_id="shooting",
        row_model=league.LeagueShootingRow,
        csv_columns=LEAGUE_SHOOTING_COLUMN_NAMES,
    ),
    "league_transactions": _season(
        "/leagues/NBA_{season_end_year}_transactions.html",
        table_id="transactions",
        transaction_list_fallback=True,
        row_model=league.LeagueTransactionRow,
        csv_columns=LEAGUE_TRANSACTIONS_COLUMN_NAMES,
    ),
    "rookie_stats": _season(
        "/leagues/NBA_{season_end_year}_rookies.html",
        table_id="rookies",
        row_model=league.RookieStatsRow,
        csv_columns=ROOKIE_STATS_COLUMN_NAMES,
    ),
    # Backed by the bespoke HTTPService.standings (parses both conference tables).
    "standings": _season(
        "/leagues/NBA_{season_end_year}.html",
        custom=True,
        row_model=standings.StandingsRow,
        csv_columns=STANDINGS_COLUMNS_NAMES,
    ),
    "standings_by_date": _season(
        "/leagues/NBA_{season_end_year}_standings_by_date_{conference}.html",
        table_id="standings_by_date",
        custom=True,
        row_model=standings.StandingsByDateRow,
        csv_columns=STANDINGS_BY_DATE_COLUMN_NAMES,
    ),
    "attendance": _season(
        "/leagues/NBA_{season_end_year}.html",
        table_id="advanced-team",
        projection=("team", "arena_name", "attendance", "attendance_per_g"),
        row_model=league.AttendanceRow,
        csv_columns=ATTENDANCE_COLUMN_NAMES,
    ),
    # ── Playoffs ──
    "playoff_per_game": _season(
        "/leagues/NBA_{season_end_year}_per_game.html",
        table_id="per_game_stats_post",
        commented_table_id="per_game_stats_post",
        row_model=playoffs.PlayoffPerGameRow,
        csv_columns=PLAYOFF_PER_GAME_COLUMN_NAMES,
    ),
    "playoff_totals": _season(
        "/leagues/NBA_{season_end_year}_totals.html",
        table_id="totals_stats_post",
        commented_table_id="totals_stats_post",
        row_model=playoffs.PlayoffTotalsRow,
        csv_columns=PLAYOFF_TOTALS_COLUMN_NAMES,
    ),
    "playoff_bracket": _season(
        "/playoffs/NBA_{season_end_year}.html",
        table_id="all_playoffs",
        use_header_fallback=True,
        row_model=playoffs.PlayoffBracketRow,
        csv_columns=PLAYOFF_BRACKET_COLUMN_NAMES,
    ),
    # ── Draft, awards, leaders ──
    "draft_picks": _season(
        "/draft/NBA_{season_end_year}.html",
        table_id="stats",
        row_model=draft.DraftPicksRow,
        csv_columns=DRAFT_PICKS_COLUMN_NAMES,
    ),
    "season_awards": _season(
        "/awards/awards_{season_end_year}.html",
        table_id="mvp",
        row_model=league.SeasonAwardsRow,
        csv_columns=SEASON_AWARDS_COLUMN_NAMES,
    ),
    "season_leaders": TableEndpoint(
        path="/leaders/per_season.html",
        table_id="stats_TOT",
        use_header_fallback=True,
        row_model=league.SeasonLeadersRow,
        csv_columns=SEASON_LEADERS_COLUMN_NAMES,
    ),
    "career_leaders": TableEndpoint(
        path="/leaders/",
        table_id="leaders_index",
        use_header_fallback=True,
        row_model=league.CareerLeadersRow,
        csv_columns=CAREER_LEADERS_COLUMN_NAMES,
    ),
    # ── Player pages ──
    "player_career_stats": _player(
        _PLAYER_PAGE,
        table_id="per_game_stats",
        row_model=players.PlayerCareerStatsRow,
        csv_columns=PLAYER_CAREER_STATS_COLUMN_NAMES,
    ),
    "player_playoff_series": _player(
        _PLAYER_PAGE,
        commented_table_id="playoffs_series",
        row_model=players.PlayerPlayoffSeriesRow,
        csv_columns=PLAYER_PLAYOFF_SERIES_COLUMN_NAMES,
    ),
    "player_adjusted_shooting": _player(
        _PLAYER_PAGE,
        commented_table_id="adj_shooting",
        row_model=players.PlayerAdjustedShootingRow,
        csv_columns=PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES,
    ),
    "player_play_by_play": _player(
        _PLAYER_PAGE,
        commented_table_id="pbp_stats",
        row_model=players.PlayerPlayByPlayStatsRow,
        csv_columns=PLAYER_PLAY_BY_PLAY_COLUMN_NAMES,
    ),
    "player_game_highs": _player(
        _PLAYER_PAGE,
        commented_table_id="highs-reg-season",
        row_model=players.PlayerGameHighsRow,
        csv_columns=PLAYER_GAME_HIGHS_COLUMN_NAMES,
    ),
    "player_all_star": _player(
        _PLAYER_PAGE,
        commented_table_id="all_star",
        row_model=players.PlayerAllStarRow,
        csv_columns=PLAYER_ALL_STAR_COLUMN_NAMES,
    ),
    "player_similarity_scores": _player(
        _PLAYER_PAGE,
        commented_table_id="sims-career",
        row_model=players.PlayerSimilarityScoresRow,
        csv_columns=PLAYER_SIMILARITY_SCORES_COLUMN_NAMES,
    ),
    "player_salaries": _player(
        _PLAYER_PAGE,
        commented_table_id="all_salaries",
        row_model=players.PlayerSalariesRow,
        csv_columns=PLAYER_SALARIES_COLUMN_NAMES,
    ),
    "player_splits": _player(
        "/players/{player_identifier[0]}/{player_identifier}/splits/{season_end_year}",
        params=("player_identifier", "season_end_year"),
        table_id="splits",
        row_model=players.PlayerSplitsRow,
        csv_columns=PLAYER_SPLITS_COLUMN_NAMES,
    ),
    "player_on_off": _player(
        "/players/{player_identifier[0]}/{player_identifier}/on-off/{season_end_year}",
        params=("player_identifier", "season_end_year"),
        table_id="on-off",
        row_model=players.PlayerOnOffRow,
        csv_columns=PLAYER_ON_OFF_COLUMN_NAMES,
    ),
    # basketball-reference redirects .html for shooting pages, so no .html suffix
    "player_shot_charts": _player(
        "/players/{player_identifier[0]}/{player_identifier}/shooting/{season_end_year}",
        params=("player_identifier", "season_end_year"),
        table_id="shooting",
        row_model=players.PlayerShotChartsRow,
        csv_columns=PLAYER_SHOT_CHARTS_COLUMN_NAMES,
    ),
    # ── Team pages ──
    "team_roster": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        table_id="roster",
        row_model=teams.TeamRosterRow,
        csv_columns=TEAM_ROSTER_COLUMN_NAMES,
    ),
    # League-wide injury page; team/season parameters are accepted for API
    # symmetry but do not affect the request.
    "team_injury_report": _team(
        "/friv/injuries.fcgi",
        table_id="injuries",
        row_model=teams.TeamInjuryReportRow,
        csv_columns=TEAM_INJURY_REPORT_COLUMN_NAMES,
    ),
    "team_and_opponent": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        commented_table_id="team_and_opponent",
        row_model=teams.TeamAndOpponentRow,
        csv_columns=TEAM_AND_OPPONENT_COLUMN_NAMES,
    ),
    "team_misc_four_factors": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        commented_table_id="team_misc",
        row_model=teams.TeamMiscFourFactorsRow,
        csv_columns=TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES,
    ),
    # Scrapes the same #team_and_opponent table as team_and_opponent; kept as a
    # separate endpoint for backwards compatibility with its own column set.
    "team_opponent_stats": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        commented_table_id="team_and_opponent",
        row_model=teams.TeamOpponentStatsRow,
        csv_columns=TEAM_OPPONENT_STATS_COLUMN_NAMES,
    ),
    "team_schedule": _team(
        "/teams/{team_abbreviation}/{season_end_year}_games.html",
        table_id="games",
        row_model=schedule.TeamScheduleRow,
        csv_columns=TEAM_SCHEDULE_COLUMN_NAMES,
    ),
    "team_transactions": _team(
        "/teams/{team_abbreviation}/{season_end_year}_transactions.html",
        table_id="transactions",
        transaction_list_fallback=True,
        row_model=teams.TeamTransactionsRow,
        csv_columns=TEAM_TRANSACTIONS_COLUMN_NAMES,
    ),
    "team_splits": _team(
        "/teams/{team_abbreviation}/{season_end_year}/splits/",
        table_id="team_splits",
        row_model=teams.TeamSplitsRow,
        csv_columns=TEAM_SPLITS_COLUMN_NAMES,
    ),
    "team_contracts": _team(
        "/contracts/{team_abbreviation}.html",
        params=("team_abbreviation",),
        table_id="contracts",
        row_model=teams.TeamContractsRow,
        csv_columns=TEAM_CONTRACTS_COLUMN_NAMES,
    ),
    "team_lineups": _team(
        "/teams/{team_abbreviation}/{season_end_year}/lineups/",
        commented_table_id="lineups_5-man_",
        row_model=teams.TeamLineupsRow,
        csv_columns=TEAM_LINEUPS_COLUMN_NAMES,
    ),
    "team_starting_lineups": _team(
        "/teams/{team_abbreviation}/{season_end_year}_start.html",
        table_id="starting_lineups_po0",
        row_model=teams.TeamStartingLineupsRow,
        csv_columns=TEAM_STARTING_LINEUPS_COLUMN_NAMES,
    ),
    "team_on_off": _team(
        "/teams/{team_abbreviation}/{season_end_year}/on-off/",
        table_id="on_off",
        row_model=teams.TeamOnOffRow,
        csv_columns=TEAM_ON_OFF_COLUMN_NAMES,
    ),
    "franchise_history": _team(
        "/teams/{team_abbreviation}/",
        params=("team_abbreviation",),
        table_id="{team_abbreviation}",
        row_model=teams.FranchiseHistoryRow,
        csv_columns=FRANCHISE_HISTORY_COLUMN_NAMES,
    ),
    # ── Bespoke HTTPService endpoints (multi-step fetch/parse chains) ──
    # All custom=True: each is backed by the same-named HTTPService method.
    "player_box_scores": _endpoint(
        "/friv/dailyleaders.cgi?month={month}&day={day}&year={year}",
        params=("day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        custom=True,
        row_model=boxscores.PlayerBoxScoreRow,
        csv_columns=BOX_SCORE_COLUMN_NAMES,
    ),
    "team_box_scores": _endpoint(
        "/boxscores/?month={month}&day={day}&year={year}",
        params=("day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        custom=True,
        row_model=boxscores.TeamBoxScoreRow,
        csv_columns=TEAM_BOX_SCORES_COLUMN_NAMES,
    ),
    "play_by_play": _endpoint(
        "/boxscores/pbp/",
        params=("home_team", "day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        custom=True,
        row_model=playbyplay.PlayByPlayRow,
        csv_columns=PLAY_BY_PLAY_COLUMN_NAMES,
    ),
    "regular_season_player_box_scores": _endpoint(
        "/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}",
        params=("player_identifier", "season_end_year", "include_inactive_games"),
        error=InvalidPlayerAndSeason,
        error_params=("player_identifier", "season_end_year"),
        error_status_codes=NOT_FOUND_OR_SERVER_ERROR,
        custom=True,
        row_model=boxscores.RegularSeasonPlayerBoxScoreRow,
        csv_columns=PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    ),
    "playoff_player_box_scores": _endpoint(
        "/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}",
        params=("player_identifier", "season_end_year", "include_inactive_games"),
        error=InvalidPlayerAndSeason,
        error_params=("player_identifier", "season_end_year"),
        error_status_codes=NOT_FOUND_OR_SERVER_ERROR,
        custom=True,
        row_model=boxscores.PlayoffPlayerBoxScoreRow,
        csv_columns=PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    ),
    "season_schedule": _season(
        "/leagues/NBA_{season_end_year}_games.html",
        custom=True,
        row_model=schedule.SeasonScheduleRow,
        csv_columns=SCHEDULE_COLUMN_NAMES,
    ),
    "players_season_totals": _season(
        "/leagues/NBA_{season_end_year}_totals.html",
        custom=True,
        row_model=players.PlayerSeasonTotalsRow,
        csv_columns=PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    ),
    "players_advanced_season_totals": _season(
        "/leagues/NBA_{season_end_year}_advanced.html",
        params=("season_end_year", "include_combined_values"),
        custom=True,
        row_model=players.PlayerAdvancedSeasonTotalsRow,
        csv_columns=PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    ),
    # csv_columns omitted — auto-detected from data so empty columns are stripped
    "search": _endpoint(
        "/search/search.fcgi?search={term}",
        params=("term",),
        error=InvalidSearch,
        error_params=("term",),
        custom=True,
        row_model=search.SearchResultRow,
    ),
}
