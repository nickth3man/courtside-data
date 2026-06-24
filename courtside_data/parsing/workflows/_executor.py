"""Workflow endpoint execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from courtside_data.parsing.workflows._context import WorkflowExecutionContext
from courtside_data.parsing.workflows._steps import (
    CallCustomHandlerStep,
    EmitScheduleDiagnosticsStep,
    EmitTeamBoxScoresDiagnosticsStep,
    FetchDailyBoxScoresIndexStep,
    FetchScheduleMonthsStep,
    FetchSeasonScheduleIndexStep,
    MergeScheduleRowsStep,
    MergeTeamBoxScoreRowsStep,
    MergeTeamBoxScoreStatsStep,
    ParseEachTeamBoxScoreStep,
    ParseInlineScheduleMonthStep,
    ParseScheduleMonthsStep,
    RequireGameLinksStep,
    SelectGameLinksStep,
    SelectScheduleMonthLinksStep,
)

if TYPE_CHECKING:
    from courtside_data.endpoints import TableEndpoint
    from courtside_data.http_service import HTTPService


NATIVE_WORKFLOW_ENDPOINTS: frozenset[str] = frozenset({"season_schedule", "team_box_scores"})

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
