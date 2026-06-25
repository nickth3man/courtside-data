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
from courtside_data.endpoints._table import EndpointSpec, _season
from courtside_data.endpoints._workflow import WorkflowSpec, WorkflowStep, WorkflowStepKind
from courtside_data.output.columns import (
    FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
    PLAYOFF_BRACKET_COLUMN_NAMES,
    PLAYOFF_PER_GAME_COLUMN_NAMES,
    PLAYOFF_TOTALS_COLUMN_NAMES,
)
from courtside_data.schemas import playoffs

_PLAYOFF_BRACKET_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_playoff_page",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the season playoff page.",
            inputs=("season_end_year",),
            outputs=("playoff_page",),
        ),
        WorkflowStep(
            id="select_bracket_table",
            kind=WorkflowStepKind.SELECT,
            description="Select table#all_playoffs, returning no rows when it is absent.",
            inputs=("playoff_page",),
            outputs=("bracket_table",),
        ),
        WorkflowStep(
            id="parse_playoff_bracket",
            kind=WorkflowStepKind.PARSE,
            description="Parse the playoff bracket table hierarchy into series rows.",
            inputs=("bracket_table",),
            outputs=("rows",),
            parser_id="playoff_bracket_table",
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics including the parsed series count.",
            inputs=("rows",),
        ),
    ),
)

_FRIV_7_GAME_PLAYOFF_OUTCOMES_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_friv_page",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the static seven-game playoff series outcomes page.",
            outputs=("friv_page",),
        ),
        WorkflowStep(
            id="select_outcome_table",
            kind=WorkflowStepKind.SELECT,
            description="Select the configured outcome table, returning no rows when it is absent.",
            inputs=("friv_page", "table_id"),
            outputs=("outcome_table",),
        ),
        WorkflowStep(
            id="parse_outcome_rows",
            kind=WorkflowStepKind.PARSE,
            description="Parse tbody rows from the selected outcome matrix.",
            inputs=("outcome_table",),
            outputs=("rows",),
            parser_id="friv_playoff_outcomes_table",
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics and raw row artifacts for the selected table.",
            inputs=("rows", "table_id"),
        ),
    ),
)

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
        row_model=playoffs.PlayoffBracketRow,
        csv_columns=PLAYOFF_BRACKET_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.BRACKET,
            features=frozenset({EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_PLAYOFF_BRACKET_WORKFLOW,
    ),
    "friv_7_game_playoff_series_outcomes_team_is_down": EndpointSpec(
        path="/friv/7-game-playoff-series-outcomes-22111.html",
        table_id="team-is-down",
        row_model=playoffs.SevenGamePlayoffSeriesOutcomesRow,
        csv_columns=FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_FRIV_7_GAME_PLAYOFF_OUTCOMES_WORKFLOW,
    ),
    "friv_7_game_playoff_series_outcomes_team_is_tied": EndpointSpec(
        path="/friv/7-game-playoff-series-outcomes-22111.html",
        table_id="team-is-tied",
        row_model=playoffs.SevenGamePlayoffSeriesOutcomesRow,
        csv_columns=FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_FRIV_7_GAME_PLAYOFF_OUTCOMES_WORKFLOW,
    ),
    "friv_7_game_playoff_series_outcomes_team_is_up": EndpointSpec(
        path="/friv/7-game-playoff-series-outcomes-22111.html",
        table_id="team-is-up",
        row_model=playoffs.SevenGamePlayoffSeriesOutcomesRow,
        csv_columns=FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.PLAYOFFS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_FRIV_7_GAME_PLAYOFF_OUTCOMES_WORKFLOW,
    ),
}
