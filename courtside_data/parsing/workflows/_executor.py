"""Workflow endpoint execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from courtside_data.parsing.workflows._context import WorkflowExecutionContext
from courtside_data.parsing.workflows._steps import (
    CallCustomHandlerStep,
    EmitAwardVotingDiagnosticsStep,
    EmitFrivOutcomesDiagnosticsStep,
    EmitPlayerGameLogDiagnosticsStep,
    EmitPlayerTotalsDiagnosticsStep,
    EmitPlayoffBracketDiagnosticsStep,
    EmitScheduleDiagnosticsStep,
    EmitTeamBoxScoresDiagnosticsStep,
    FetchDailyBoxScoresIndexStep,
    FetchEndpointPathStep,
    FetchScheduleMonthsStep,
    FetchSeasonScheduleIndexStep,
    MergeScheduleRowsStep,
    MergeTeamBoxScoreRowsStep,
    MergeTeamBoxScoreStatsStep,
    NormalizeAwardIdStep,
    ParseEachTeamBoxScoreStep,
    ParseInlineScheduleMonthStep,
    ParseOptionalTableRowsStep,
    ParsePlayerGameLogStep,
    ParsePlayerTotalsStep,
    ParseScheduleMonthsStep,
    RequireGameLinksStep,
    SelectGameLinksStep,
    SelectScheduleMonthLinksStep,
    SelectTableStep,
)

if TYPE_CHECKING:
    from courtside_data.endpoints import TableEndpoint
    from courtside_data.http_service import HTTPService


NATIVE_WORKFLOW_ENDPOINTS: frozenset[str] = frozenset(
    {
        "friv_7_game_playoff_series_outcomes_team_is_down",
        "friv_7_game_playoff_series_outcomes_team_is_tied",
        "friv_7_game_playoff_series_outcomes_team_is_up",
        "playoff_bracket",
        "playoff_player_box_scores",
        "players_advanced_season_totals",
        "players_season_totals",
        "regular_season_player_box_scores",
        "season_awards_voting",
        "season_schedule",
        "team_box_scores",
    }
)

_NATIVE_STEP_HANDLERS = {
    "team_box_scores": {
        "fetch_daily_index": FetchDailyBoxScoresIndexStep,
        "select_game_links": SelectGameLinksStep,
        "require_game_links": RequireGameLinksStep,
        "fetch_and_parse_each_game": ParseEachTeamBoxScoreStep,
        "merge_rows": MergeTeamBoxScoreRowsStep,
        "merge_parser_stats": MergeTeamBoxScoreStatsStep,
        "emit_diagnostics": EmitTeamBoxScoresDiagnosticsStep(),
    },
    "season_schedule": {
        "fetch_season_index": FetchSeasonScheduleIndexStep(),
        "parse_inline_month": ParseInlineScheduleMonthStep(),
        "select_month_links": SelectScheduleMonthLinksStep(),
        "fetch_months": FetchScheduleMonthsStep(),
        "parse_months": ParseScheduleMonthsStep(),
        "merge_rows": MergeScheduleRowsStep(),
        "emit_diagnostics": EmitScheduleDiagnosticsStep(),
    },
    "regular_season_player_box_scores": {
        "fetch_player_gamelog": FetchEndpointPathStep(output_var="gamelog_page"),
        "select_regular_season_table": SelectTableStep(
            selector_var="gamelog_page",
            output_var="game_log_table",
            table_id="player_game_log_reg",
            raise_invalid_player_and_season=True,
        ),
        "parse_player_game_log": ParsePlayerGameLogStep(),
        "emit_diagnostics": EmitPlayerGameLogDiagnosticsStep(
            parser_name="regular_season_player_box_scores",
            table_id="player_game_log_reg",
        ),
    },
    "playoff_player_box_scores": {
        "fetch_player_gamelog": FetchEndpointPathStep(output_var="gamelog_page"),
        "select_playoff_table": SelectTableStep(
            selector_var="gamelog_page",
            output_var="game_log_table",
            table_id="player_game_log_post",
            raise_invalid_player_and_season=True,
        ),
        "parse_player_game_log": ParsePlayerGameLogStep(),
        "emit_diagnostics": EmitPlayerGameLogDiagnosticsStep(
            parser_name="playoff_player_box_scores",
            table_id="player_game_log_post",
        ),
    },
    "players_season_totals": {
        "fetch_totals_page": FetchEndpointPathStep(output_var="totals_page"),
        "select_totals_table": SelectTableStep(
            selector_var="totals_page",
            output_var="totals_table",
            table_id="totals_stats",
        ),
        "parse_player_totals": ParsePlayerTotalsStep(table_id="totals_stats"),
        "emit_diagnostics": EmitPlayerTotalsDiagnosticsStep(
            parser_name="players_season_totals",
            table_id="totals_stats",
        ),
    },
    "players_advanced_season_totals": {
        "fetch_advanced_page": FetchEndpointPathStep(output_var="totals_page"),
        "select_advanced_table": SelectTableStep(
            selector_var="totals_page",
            output_var="advanced_table",
            table_id="advanced",
        ),
        "parse_advanced_totals": ParsePlayerTotalsStep(
            table_id="advanced",
            include_combined_param="include_combined_values",
        ),
        "emit_diagnostics": EmitPlayerTotalsDiagnosticsStep(
            parser_name="players_advanced_season_totals",
            table_id="advanced",
        ),
    },
    "season_awards_voting": {
        "normalize_award_id": NormalizeAwardIdStep(),
        "fetch_awards_page": FetchEndpointPathStep(output_var="awards_page"),
        "select_award_table": SelectTableStep(
            selector_var="awards_page",
            output_var="award_table",
            table_id_var="table_id",
        ),
        "parse_award_rows": ParseOptionalTableRowsStep(
            table_var="award_table",
            parser_id="awards_voting_table",
        ),
        "emit_diagnostics": EmitAwardVotingDiagnosticsStep(),
    },
    "playoff_bracket": {
        "fetch_playoff_page": FetchEndpointPathStep(output_var="playoff_page"),
        "select_bracket_table": SelectTableStep(
            selector_var="playoff_page",
            output_var="bracket_table",
            table_id="all_playoffs",
        ),
        "parse_playoff_bracket": ParseOptionalTableRowsStep(
            table_var="bracket_table",
            parser_id="playoff_bracket_table",
        ),
        "emit_diagnostics": EmitPlayoffBracketDiagnosticsStep(),
    },
    "friv_7_game_playoff_series_outcomes_team_is_down": {
        "fetch_friv_page": FetchEndpointPathStep(output_var="friv_page"),
        "select_outcome_table": SelectTableStep(selector_var="friv_page", output_var="outcome_table"),
        "parse_outcome_rows": ParseOptionalTableRowsStep(
            table_var="outcome_table",
            parser_id="friv_playoff_outcomes_table",
        ),
        "emit_diagnostics": EmitFrivOutcomesDiagnosticsStep(),
    },
    "friv_7_game_playoff_series_outcomes_team_is_tied": {
        "fetch_friv_page": FetchEndpointPathStep(output_var="friv_page"),
        "select_outcome_table": SelectTableStep(selector_var="friv_page", output_var="outcome_table"),
        "parse_outcome_rows": ParseOptionalTableRowsStep(
            table_var="outcome_table",
            parser_id="friv_playoff_outcomes_table",
        ),
        "emit_diagnostics": EmitFrivOutcomesDiagnosticsStep(),
    },
    "friv_7_game_playoff_series_outcomes_team_is_up": {
        "fetch_friv_page": FetchEndpointPathStep(output_var="friv_page"),
        "select_outcome_table": SelectTableStep(selector_var="friv_page", output_var="outcome_table"),
        "parse_outcome_rows": ParseOptionalTableRowsStep(
            table_var="outcome_table",
            parser_id="friv_playoff_outcomes_table",
        ),
        "emit_diagnostics": EmitFrivOutcomesDiagnosticsStep(),
    },
}


def is_native_workflow_endpoint(endpoint_name: str) -> bool:
    """Return whether ``endpoint_name`` is executed by concrete workflow steps."""
    return endpoint_name in NATIVE_WORKFLOW_ENDPOINTS


@dataclass(frozen=True, slots=True)
class WorkflowEndpointHandler:
    """Execute a registry-described workflow endpoint."""

    http: HTTPService

    def execute(self, endpoint_name: str, endpoint: TableEndpoint, params: dict[str, Any]) -> Any:
        """Run a workflow endpoint through native steps or the compatibility step."""
        if endpoint.workflow is None:
            raise ValueError(f"Endpoint {endpoint_name!r} does not declare a workflow spec.")
        context = WorkflowExecutionContext.from_http(
            self.http,
            endpoint_name=endpoint_name,
            endpoint=endpoint,
            params=params,
        )
        if is_native_workflow_endpoint(endpoint_name):
            result: Any = None
            handlers = _NATIVE_STEP_HANDLERS[endpoint_name]
            for step in endpoint.workflow.steps:
                result = handlers[step.id].execute(context)
            result_key = endpoint.workflow.result
            return result if result is not None else context.scratch[result_key]
        return CallCustomHandlerStep().execute(context)


def execute_workflow(http: HTTPService, endpoint_name: str, endpoint: TableEndpoint, params: dict[str, Any]) -> Any:
    """Execute one workflow endpoint with bound call params."""
    return WorkflowEndpointHandler(http).execute(endpoint_name, endpoint, params)
