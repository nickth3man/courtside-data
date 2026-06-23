"""Bespoke multi-step endpoint registrations."""

from __future__ import annotations

from courtside_data.endpoints._error_mapping import NOT_FOUND_OR_SERVER_ERROR
from courtside_data.endpoints._table import _endpoint, _season
from courtside_data.errors import InvalidDate, InvalidPlayerAndSeason, InvalidSearch
from courtside_data.output.columns import (
    BOX_SCORE_COLUMN_NAMES,
    PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    SCHEDULE_COLUMN_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
)
from courtside_data.schemas import boxscores, playbyplay, players, schedule, search

CUSTOM_ENDPOINTS = {
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
    # csv_columns omitted - auto-detected from data so empty columns are stripped.
    "search": _endpoint(
        "/search/search.fcgi?search={term}",
        params=("term",),
        error=InvalidSearch,
        error_params=("term",),
        custom=True,
        row_model=search.SearchResultRow,
    ),
}
