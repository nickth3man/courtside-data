"""Bespoke multi-step endpoint registrations."""

from __future__ import annotations

from courtside_data.endpoints._error_mapping import NOT_FOUND_OR_SERVER_ERROR
from courtside_data.endpoints._metadata import (
    EndpointDomain,
    EndpointFeature,
    EndpointKind,
    EndpointMetadata,
    EndpointScope,
    ParserShape,
    RequestShape,
)
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
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.REQUIRES_NON_EMPTY, EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
    "team_box_scores": _endpoint(
        "/boxscores/?month={month}&day={day}&year={year}",
        params=("day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        custom=True,
        row_model=boxscores.TeamBoxScoreRow,
        csv_columns=TEAM_BOX_SCORES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE,
            request_shape=RequestShape.MULTI_REQUEST,
            parser_shape=ParserShape.MULTI_TABLE,
            features=frozenset(
                {
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.AGGREGATES_ROWS,
                    EndpointFeature.CUSTOM_DIAGNOSTICS,
                }
            ),
        ),
    ),
    "play_by_play": _endpoint(
        "/boxscores/pbp/",
        params=("home_team", "day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        custom=True,
        row_model=playbyplay.PlayByPlayRow,
        csv_columns=PLAY_BY_PLAY_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE_TEAM,
            request_shape=RequestShape.MULTI_REQUEST,
            parser_shape=ParserShape.PLAY_BY_PLAY,
            features=frozenset(
                {
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.ENUM_PARAM_COERCION,
                    EndpointFeature.DERIVED_FIELDS,
                    EndpointFeature.CUSTOM_DIAGNOSTICS,
                }
            ),
        ),
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
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.PLAYER_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
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
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.PLAYER_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
    "season_schedule": _season(
        "/leagues/NBA_{season_end_year}_games.html",
        custom=True,
        row_model=schedule.SeasonScheduleRow,
        csv_columns=SCHEDULE_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.MULTI_REQUEST,
            parser_shape=ParserShape.MULTI_TABLE,
            features=frozenset(
                {
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.AGGREGATES_ROWS,
                    EndpointFeature.CUSTOM_DIAGNOSTICS,
                }
            ),
        ),
    ),
    "players_season_totals": _season(
        "/leagues/NBA_{season_end_year}_totals.html",
        custom=True,
        row_model=players.PlayerSeasonTotalsRow,
        csv_columns=PLAYER_SEASON_TOTALS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
    "players_advanced_season_totals": _season(
        "/leagues/NBA_{season_end_year}_advanced.html",
        params=("season_end_year", "include_combined_values"),
        custom=True,
        row_model=players.PlayerAdvancedSeasonTotalsRow,
        csv_columns=PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.DERIVED_FIELDS, EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
    # csv_columns omitted - auto-detected from data so empty columns are stripped.
    "search": _endpoint(
        "/search/search.fcgi?search={term}",
        params=("term",),
        error=InvalidSearch,
        error_params=("term",),
        custom=True,
        row_model=search.SearchResultRow,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEARCH,
            request_shape=RequestShape.PAGINATED,
            parser_shape=ParserShape.SEARCH_RESULTS,
            features=frozenset(
                {
                    EndpointFeature.PAGINATED,
                    EndpointFeature.REDIRECTS,
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.CUSTOM_DIAGNOSTICS,
                }
            ),
        ),
    ),
}
