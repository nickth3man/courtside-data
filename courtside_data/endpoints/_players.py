"""Player-page endpoint registrations."""

from __future__ import annotations

from courtside_data.endpoints._metadata import (
    EndpointDomain,
    EndpointFeature,
    EndpointKind,
    EndpointMetadata,
    EndpointScope,
    ParserShape,
    RequestShape,
)
from courtside_data.endpoints._table import _player
from courtside_data.output.columns import (
    PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES,
    PLAYER_ALL_STAR_COLUMN_NAMES,
    PLAYER_CAREER_STATS_COLUMN_NAMES,
    PLAYER_GAME_HIGHS_COLUMN_NAMES,
    PLAYER_ON_OFF_COLUMN_NAMES,
    PLAYER_PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_PLAYOFF_SERIES_COLUMN_NAMES,
    PLAYER_SALARIES_COLUMN_NAMES,
    PLAYER_SHOT_CHARTS_COLUMN_NAMES,
    PLAYER_SIMILARITY_SCORES_COLUMN_NAMES,
    PLAYER_SPLITS_COLUMN_NAMES,
)
from courtside_data.schemas import players

_PLAYER_PAGE = "/players/{player_identifier[0]}/{player_identifier}.html"

PLAYER_ENDPOINTS = {
    "player_career_stats": _player(
        _PLAYER_PAGE,
        table_id="per_game_stats",
        row_model=players.PlayerCareerStatsRow,
        csv_columns=PLAYER_CAREER_STATS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "player_playoff_series": _player(
        _PLAYER_PAGE,
        commented_table_id="playoffs_series",
        row_model=players.PlayerPlayoffSeriesRow,
        csv_columns=PLAYER_PLAYOFF_SERIES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "player_adjusted_shooting": _player(
        _PLAYER_PAGE,
        commented_table_id="adj_shooting",
        row_model=players.PlayerAdjustedShootingRow,
        csv_columns=PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "player_play_by_play": _player(
        _PLAYER_PAGE,
        commented_table_id="pbp_stats",
        row_model=players.PlayerPlayByPlayStatsRow,
        csv_columns=PLAYER_PLAY_BY_PLAY_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "player_game_highs": _player(
        _PLAYER_PAGE,
        commented_table_id="highs-reg-season",
        row_model=players.PlayerGameHighsRow,
        csv_columns=PLAYER_GAME_HIGHS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "player_all_star": _player(
        _PLAYER_PAGE,
        commented_table_id="all_star",
        row_model=players.PlayerAllStarRow,
        csv_columns=PLAYER_ALL_STAR_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "player_similarity_scores": _player(
        _PLAYER_PAGE,
        commented_table_id="sims-career",
        row_model=players.PlayerSimilarityScoresRow,
        csv_columns=PLAYER_SIMILARITY_SCORES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "player_salaries": _player(
        _PLAYER_PAGE,
        commented_table_id="all_salaries",
        row_model=players.PlayerSalariesRow,
        csv_columns=PLAYER_SALARIES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "player_splits": _player(
        "/players/{player_identifier[0]}/{player_identifier}/splits/{season_end_year}",
        params=("player_identifier", "season_end_year"),
        table_id="splits",
        row_model=players.PlayerSplitsRow,
        csv_columns=PLAYER_SPLITS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "player_on_off": _player(
        "/players/{player_identifier[0]}/{player_identifier}/on-off/{season_end_year}",
        params=("player_identifier", "season_end_year"),
        table_id="on-off",
        row_model=players.PlayerOnOffRow,
        csv_columns=PLAYER_ON_OFF_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    # basketball-reference redirects .html for shooting pages, so no .html suffix
    "player_shot_charts": _player(
        "/players/{player_identifier[0]}/{player_identifier}/shooting/{season_end_year}",
        params=("player_identifier", "season_end_year"),
        table_id="shooting",
        row_model=players.PlayerShotChartsRow,
        csv_columns=PLAYER_SHOT_CHARTS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.PLAYER_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
}
