"""League-wide endpoint registrations."""

from __future__ import annotations

from courtside_data.endpoints._table import _season
from courtside_data.output.columns import (
    ATTENDANCE_COLUMN_NAMES,
    LEAGUE_PER_36_COLUMN_NAMES,
    LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES,
    LEAGUE_PER_GAME_COLUMN_NAMES,
    LEAGUE_PLAY_BY_PLAY_COLUMN_NAMES,
    LEAGUE_SHOOTING_COLUMN_NAMES,
    LEAGUE_TOTALS_COLUMN_NAMES,
    LEAGUE_TRANSACTIONS_COLUMN_NAMES,
    ROOKIE_STATS_COLUMN_NAMES,
    STANDINGS_BY_DATE_COLUMN_NAMES,
    STANDINGS_COLUMNS_NAMES,
)
from courtside_data.schemas import league, standings

LEAGUE_ENDPOINTS = {
    "league_per_game_stats": _season(
        "/leagues/NBA_{season_end_year}_per_game.html",
        table_id="per_game_stats",
        exclude_summary_rows=True,
        row_model=league.LeaguePerGameStatsRow,
        csv_columns=LEAGUE_PER_GAME_COLUMN_NAMES,
    ),
    "league_per_36_minutes": _season(
        "/leagues/NBA_{season_end_year}_per_minute.html",
        table_id="per_minute_stats",
        exclude_summary_rows=True,
        row_model=league.LeaguePer36MinutesRow,
        csv_columns=LEAGUE_PER_36_COLUMN_NAMES,
    ),
    "league_totals": _season(
        "/leagues/NBA_{season_end_year}_totals.html",
        table_id="totals_stats",
        exclude_summary_rows=True,
        row_model=league.LeagueTotalsRow,
        csv_columns=LEAGUE_TOTALS_COLUMN_NAMES,
    ),
    "league_per_100_possessions": _season(
        "/leagues/NBA_{season_end_year}_per_poss.html",
        table_id="per_poss",
        exclude_summary_rows=True,
        min_year=1974,
        row_model=league.LeaguePer100PossessionsRow,
        csv_columns=LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES,
    ),
    "league_shooting": _season(
        "/leagues/NBA_{season_end_year}_shooting.html",
        table_id="shooting",
        exclude_summary_rows=True,
        row_model=league.LeagueShootingRow,
        csv_columns=LEAGUE_SHOOTING_COLUMN_NAMES,
    ),
    "league_play_by_play": _season(
        "/leagues/NBA_{season_end_year}_play-by-play.html",
        table_id="pbp_stats",
        exclude_summary_rows=True,
        row_model=league.LeaguePlayByPlayRow,
        csv_columns=LEAGUE_PLAY_BY_PLAY_COLUMN_NAMES,
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
        # The bespoke HTTPService.standings_by_date fetches both conferences
        # internally; ``conference`` is an internal template placeholder, not a
        # call parameter. Declaring only ``season_end_year`` here keeps the
        # contract-test signature check honest and matches the public API.
        params=("season_end_year",),
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
}
