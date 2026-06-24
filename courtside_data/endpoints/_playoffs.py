"""Playoff endpoint registrations."""

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
from courtside_data.endpoints._table import TableEndpoint, _season
from courtside_data.output.columns import (
    FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
    PLAYOFF_BRACKET_COLUMN_NAMES,
    PLAYOFF_PER_GAME_COLUMN_NAMES,
    PLAYOFF_TOTALS_COLUMN_NAMES,
)
from courtside_data.schemas import playoffs

PLAYOFF_ENDPOINTS = {
    "playoff_per_game": _season(
        "/leagues/NBA_{season_end_year}_per_game.html",
        table_id="per_game_stats_post",
        commented_table_id="per_game_stats_post",
        exclude_summary_rows=True,
        row_model=playoffs.PlayoffPerGameRow,
        csv_columns=PLAYOFF_PER_GAME_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE, EndpointFeature.EXCLUDE_SUMMARY_ROWS}),
        ),
    ),
    "playoff_totals": _season(
        "/leagues/NBA_{season_end_year}_totals.html",
        table_id="totals_stats_post",
        commented_table_id="totals_stats_post",
        exclude_summary_rows=True,
        row_model=playoffs.PlayoffTotalsRow,
        csv_columns=PLAYOFF_TOTALS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE, EndpointFeature.EXCLUDE_SUMMARY_ROWS}),
        ),
    ),
    "playoff_bracket": _season(
        "/playoffs/NBA_{season_end_year}.html",
        custom=True,
        row_model=playoffs.PlayoffBracketRow,
        csv_columns=PLAYOFF_BRACKET_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.BRACKET,
            features=frozenset({EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
    "friv_7_game_playoff_series_outcomes_team_is_down": TableEndpoint(
        path="/friv/7-game-playoff-series-outcomes-22111.html",
        table_id="team-is-down",
        custom=True,
        row_model=playoffs.SevenGamePlayoffSeriesOutcomesRow,
        csv_columns=FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
    "friv_7_game_playoff_series_outcomes_team_is_tied": TableEndpoint(
        path="/friv/7-game-playoff-series-outcomes-22111.html",
        table_id="team-is-tied",
        custom=True,
        row_model=playoffs.SevenGamePlayoffSeriesOutcomesRow,
        csv_columns=FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
    "friv_7_game_playoff_series_outcomes_team_is_up": TableEndpoint(
        path="/friv/7-game-playoff-series-outcomes-22111.html",
        table_id="team-is-up",
        custom=True,
        row_model=playoffs.SevenGamePlayoffSeriesOutcomesRow,
        csv_columns=FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
    ),
}
