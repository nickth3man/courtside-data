"""Workflow endpoint execution."""

from __future__ import annotations

from collections.abc import Mapping
from functools import partial
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Protocol

from courtside_data._frozen import frozen_slot
from courtside_data.parsing.workflows._context import WorkflowExecutionContext
from courtside_data.parsing.workflows._steps import (
    AttachStandingsConferenceStep,
    BranchSearchResultsStep,
    BuildSearchResultStep,
    EmitDiagnosticsStep,
    ExpandStandingsConferencesStep,
    FetchDailyBoxScoresIndexStep,
    FetchEndpointPathStep,
    FetchPlayByPlayPageStep,
    FetchResponseStep,
    FetchScheduleMonthsStep,
    FetchSearchResponseStep,
    FetchSeasonScheduleIndexStep,
    FetchStandingsConferencePagesStep,
    MergeScheduleRowsStep,
    MergeTeamBoxScoreRowsStep,
    MergeTeamBoxScoreStatsStep,
    NormalizeAwardIdStep,
    PaginateSearchResultsStep,
    ParseBoxScoreGameInfoStep,
    ParseBoxScoreLineScoreStep,
    ParseBoxScorePlayerAdvancedStep,
    ParseBoxScorePlayerBasicStep,
    ParseBoxScorePlayerQuarterSplitsStep,
    ParseBoxScoreTeamFourFactorsStep,
    ParseEachTeamBoxScoreStep,
    ParseInlineScheduleMonthStep,
    ParseOptionalTableRowsStep,
    ParsePlayByPlayStep,
    ParsePlayerBoxScoresStep,
    ParsePlayerGameLogStep,
    ParsePlayerTotalsStep,
    ParseScheduleMonthsStep,
    ParseStandingsBlocksStep,
    ParseStandingsConferenceTablesStep,
    RequireGameLinksStep,
    ResolvePlayByPlayGameLinkStep,
    ResolvePlayByPlayTeamLabelsStep,
    SelectDailyLeadersStatsTableStep,
    SelectGameLinksStep,
    SelectScheduleMonthLinksStep,
    SelectTableStep,
)
from courtside_data.parsing.workflows._steps._emit import (
    _emit_award_voting_diagnostics,
    _emit_box_score_diagnostics,
    _emit_friv_outcomes_diagnostics,
    _emit_play_by_play_diagnostics,
    _emit_player_box_scores_diagnostics,
    _emit_player_game_log_diagnostics,
    _emit_player_totals_diagnostics,
    _emit_playoff_bracket_diagnostics,
    _emit_schedule_diagnostics,
    _emit_search_diagnostics,
    _emit_standings_by_date_diagnostics,
    _emit_standings_diagnostics,
    _emit_team_box_scores_diagnostics,
)

if TYPE_CHECKING:
    from courtside_data.endpoints import EndpointSpec
    from courtside_data.http import HTTPService


class WorkflowStepHandler(Protocol):
    """Executable object bound to one declared workflow step id."""

    def execute(self, context: WorkflowExecutionContext) -> Any:
        """Execute the step against the shared workflow context."""


@frozen_slot
class WorkflowExecutionBinding:
    """Native execution binding for one ``EndpointKind.WORKFLOW`` endpoint."""

    endpoint_name: str
    step_handlers: Mapping[str, WorkflowStepHandler]
    result: str = "rows"

    def __post_init__(self) -> None:
        object.__setattr__(self, "step_handlers", MappingProxyType(dict(self.step_handlers)))


def _binding(
    endpoint_name: str,
    step_handlers: Mapping[str, WorkflowStepHandler],
    *,
    result: str = "rows",
) -> WorkflowExecutionBinding:
    return WorkflowExecutionBinding(endpoint_name=endpoint_name, step_handlers=step_handlers, result=result)


def _binding_registry(bindings: tuple[WorkflowExecutionBinding, ...]) -> Mapping[str, WorkflowExecutionBinding]:
    by_endpoint: dict[str, WorkflowExecutionBinding] = {}
    for binding in bindings:
        if binding.endpoint_name in by_endpoint:
            raise ValueError(f"Duplicate workflow binding for {binding.endpoint_name!r}.")
        by_endpoint[binding.endpoint_name] = binding
    return MappingProxyType(by_endpoint)


_WORKFLOW_EXECUTION_BINDINGS: tuple[WorkflowExecutionBinding, ...] = (
    _binding(
        "box_score_player_basic",
        {
            "fetch_box_score": FetchEndpointPathStep(output_var="box_score_page"),
            "parse_player_basic": ParseBoxScorePlayerBasicStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_box_score_diagnostics,
                    parser_name="box_score_player_basic",
                    source_sections=('table.stats_table[id$="-game-basic"]', "div.scorebox"),
                ),
            ),
        },
    ),
    _binding(
        "box_score_game_info",
        {
            "fetch_box_score": FetchEndpointPathStep(output_var="box_score_page"),
            "parse_game_info": ParseBoxScoreGameInfoStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_box_score_diagnostics,
                    parser_name="box_score_game_info",
                    source_sections=("div.scorebox", "div.scorebox_meta", "#content > div"),
                ),
            ),
        },
    ),
    _binding(
        "box_score_player_advanced",
        {
            "fetch_box_score": FetchEndpointPathStep(output_var="box_score_page"),
            "parse_player_advanced": ParseBoxScorePlayerAdvancedStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_box_score_diagnostics,
                    parser_name="box_score_player_advanced",
                    source_sections=('table.stats_table[id$="-game-advanced"]', "div.scorebox"),
                ),
            ),
        },
    ),
    _binding(
        "box_score_line_score",
        {
            "fetch_box_score": FetchEndpointPathStep(output_var="box_score_page"),
            "parse_line_score": ParseBoxScoreLineScoreStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_box_score_diagnostics,
                    parser_name="box_score_line_score",
                    source_sections=("table#line_score",),
                ),
            ),
        },
    ),
    _binding(
        "box_score_player_quarter_splits",
        {
            "fetch_box_score": FetchEndpointPathStep(output_var="box_score_page"),
            "parse_player_quarter_splits": ParseBoxScorePlayerQuarterSplitsStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_box_score_diagnostics,
                    parser_name="box_score_player_quarter_splits",
                    source_sections=('table.stats_table[id*="-basic"]', "div.scorebox"),
                ),
            ),
        },
    ),
    _binding(
        "box_score_team_four_factors",
        {
            "fetch_box_score": FetchEndpointPathStep(output_var="box_score_page"),
            "parse_team_four_factors": ParseBoxScoreTeamFourFactorsStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_box_score_diagnostics,
                    parser_name="box_score_team_four_factors",
                    source_sections=("table#four_factors",),
                ),
            ),
        },
    ),
    _binding(
        "team_box_scores",
        {
            "fetch_daily_index": FetchDailyBoxScoresIndexStep,
            "select_game_links": SelectGameLinksStep,
            "require_game_links": RequireGameLinksStep,
            "fetch_and_parse_each_game": ParseEachTeamBoxScoreStep,
            "merge_rows": MergeTeamBoxScoreRowsStep,
            "merge_parser_stats": MergeTeamBoxScoreStatsStep,
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_team_box_scores_diagnostics),
        },
    ),
    _binding(
        "player_box_scores",
        {
            "fetch_daily_leaders": FetchResponseStep(
                "/friv/dailyleaders.cgi?month={month}&day={day}&year={year}",
                output_var="daily_leaders_response",
                follow_redirects=False,
            ),
            "select_stats_table": SelectDailyLeadersStatsTableStep(),
            "parse_player_box_scores": ParsePlayerBoxScoresStep(),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_player_box_scores_diagnostics),
        },
    ),
    _binding(
        "play_by_play",
        {
            "fetch_daily_index": FetchDailyBoxScoresIndexStep,
            "resolve_game_link": ResolvePlayByPlayGameLinkStep(),
            "fetch_play_by_play": FetchPlayByPlayPageStep(),
            "resolve_team_labels": ResolvePlayByPlayTeamLabelsStep(),
            "parse_play_by_play": ParsePlayByPlayStep(),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_play_by_play_diagnostics),
        },
    ),
    _binding(
        "standings",
        {
            "fetch_league_page": FetchEndpointPathStep(output_var="league_page"),
            "parse_standings_blocks": ParseStandingsBlocksStep(),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_standings_diagnostics),
        },
    ),
    _binding(
        "standings_by_date",
        {
            "expand_conferences": ExpandStandingsConferencesStep(),
            "fetch_conference_pages": FetchStandingsConferencePagesStep(),
            "parse_conference_tables": ParseStandingsConferenceTablesStep(),
            "attach_conference": AttachStandingsConferenceStep(),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_standings_by_date_diagnostics),
        },
    ),
    _binding(
        "search",
        {
            "fetch_search": FetchSearchResponseStep(),
            "branch_redirect_or_results": BranchSearchResultsStep(),
            "paginate_results": PaginateSearchResultsStep(),
            "parse_search_results": BuildSearchResultStep(),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_search_diagnostics),
        },
        result="players",
    ),
    _binding(
        "season_schedule",
        {
            "fetch_season_index": FetchSeasonScheduleIndexStep(),
            "parse_inline_month": ParseInlineScheduleMonthStep(),
            "select_month_links": SelectScheduleMonthLinksStep(),
            "fetch_months": FetchScheduleMonthsStep(),
            "parse_months": ParseScheduleMonthsStep(),
            "merge_rows": MergeScheduleRowsStep(),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_schedule_diagnostics),
        },
    ),
    _binding(
        "regular_season_player_box_scores",
        {
            "fetch_player_gamelog": FetchEndpointPathStep(output_var="gamelog_page"),
            "select_regular_season_table": SelectTableStep(
                selector_var="gamelog_page",
                output_var="game_log_table",
                table_id="player_game_log_reg",
                raise_invalid_player_and_season=True,
            ),
            "parse_player_game_log": ParsePlayerGameLogStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_player_game_log_diagnostics,
                    parser_name="regular_season_player_box_scores",
                    table_id="player_game_log_reg",
                ),
            ),
        },
    ),
    _binding(
        "playoff_player_box_scores",
        {
            "fetch_player_gamelog": FetchEndpointPathStep(output_var="gamelog_page"),
            "select_playoff_table": SelectTableStep(
                selector_var="gamelog_page",
                output_var="game_log_table",
                table_id="player_game_log_post",
                raise_invalid_player_and_season=True,
            ),
            "parse_player_game_log": ParsePlayerGameLogStep(),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_player_game_log_diagnostics,
                    parser_name="playoff_player_box_scores",
                    table_id="player_game_log_post",
                ),
            ),
        },
    ),
    _binding(
        "players_season_totals",
        {
            "fetch_totals_page": FetchEndpointPathStep(output_var="totals_page"),
            "select_totals_table": SelectTableStep(
                selector_var="totals_page",
                output_var="totals_table",
                table_id="totals_stats",
            ),
            "parse_player_totals": ParsePlayerTotalsStep(
                table_id="totals_stats",
                include_combined_param="include_combined_values",
            ),
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_player_totals_diagnostics,
                    parser_name="players_season_totals",
                    table_id="totals_stats",
                ),
            ),
        },
    ),
    _binding(
        "players_advanced_season_totals",
        {
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
            "emit_diagnostics": EmitDiagnosticsStep(
                emitter=partial(
                    _emit_player_totals_diagnostics,
                    parser_name="players_advanced_season_totals",
                    table_id="advanced",
                ),
            ),
        },
    ),
    _binding(
        "season_awards_voting",
        {
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
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_award_voting_diagnostics),
        },
    ),
    _binding(
        "playoff_bracket",
        {
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
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_playoff_bracket_diagnostics),
        },
    ),
    _binding(
        "friv_7_game_playoff_series_outcomes_team_is_down",
        {
            "fetch_friv_page": FetchEndpointPathStep(output_var="friv_page"),
            "select_outcome_table": SelectTableStep(selector_var="friv_page", output_var="outcome_table"),
            "parse_outcome_rows": ParseOptionalTableRowsStep(
                table_var="outcome_table",
                parser_id="friv_playoff_outcomes_table",
            ),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_friv_outcomes_diagnostics),
        },
    ),
    _binding(
        "friv_7_game_playoff_series_outcomes_team_is_tied",
        {
            "fetch_friv_page": FetchEndpointPathStep(output_var="friv_page"),
            "select_outcome_table": SelectTableStep(selector_var="friv_page", output_var="outcome_table"),
            "parse_outcome_rows": ParseOptionalTableRowsStep(
                table_var="outcome_table",
                parser_id="friv_playoff_outcomes_table",
            ),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_friv_outcomes_diagnostics),
        },
    ),
    _binding(
        "friv_7_game_playoff_series_outcomes_team_is_up",
        {
            "fetch_friv_page": FetchEndpointPathStep(output_var="friv_page"),
            "select_outcome_table": SelectTableStep(selector_var="friv_page", output_var="outcome_table"),
            "parse_outcome_rows": ParseOptionalTableRowsStep(
                table_var="outcome_table",
                parser_id="friv_playoff_outcomes_table",
            ),
            "emit_diagnostics": EmitDiagnosticsStep(emitter=_emit_friv_outcomes_diagnostics),
        },
    ),
)


_WORKFLOW_BINDINGS = _binding_registry(_WORKFLOW_EXECUTION_BINDINGS)

# Native workflow endpoints: every endpoint with an explicit execution binding.
NATIVE_WORKFLOW_ENDPOINTS: frozenset[str] = frozenset(_WORKFLOW_BINDINGS)


def workflow_execution_bindings() -> Mapping[str, WorkflowExecutionBinding]:
    """Return the native workflow execution bindings keyed by endpoint name."""
    return _WORKFLOW_BINDINGS


def is_native_workflow_endpoint(endpoint_name: str) -> bool:
    """Return whether ``endpoint_name`` is executed by concrete workflow steps."""
    return endpoint_name in NATIVE_WORKFLOW_ENDPOINTS


def _validate_binding(endpoint_name: str, endpoint: EndpointSpec, binding: WorkflowExecutionBinding) -> None:
    if endpoint.workflow is None:
        raise ValueError(f"Endpoint {endpoint_name!r} does not declare a workflow spec.")

    declared_step_ids = {step.id for step in endpoint.workflow.steps}
    bound_step_ids = set(binding.step_handlers)
    missing = sorted(declared_step_ids - bound_step_ids)
    extra = sorted(bound_step_ids - declared_step_ids)
    if missing or extra:
        raise ValueError(
            f"Workflow binding for {endpoint_name!r} does not match the declared workflow steps: "
            f"missing={missing}, extra={extra}."
        )

    if endpoint.workflow.result != binding.result:
        raise ValueError(
            f"Workflow binding for {endpoint_name!r} returns {binding.result!r}, "
            f"but the workflow spec declares {endpoint.workflow.result!r}."
        )


@frozen_slot
class WorkflowEndpointHandler:
    """Execute a registry-described workflow endpoint."""

    http: HTTPService

    def execute(self, endpoint_name: str, endpoint: EndpointSpec, params: dict[str, Any]) -> Any:
        """Run a workflow endpoint through its explicit native execution binding."""
        if endpoint.workflow is None:
            raise ValueError(f"Endpoint {endpoint_name!r} does not declare a workflow spec.")
        binding = _WORKFLOW_BINDINGS.get(endpoint_name)
        if binding is None:
            raise ValueError(f"Workflow endpoint {endpoint_name!r} does not have a native execution binding.")
        _validate_binding(endpoint_name, endpoint, binding)

        context = WorkflowExecutionContext.from_http(
            self.http,
            endpoint_name=endpoint_name,
            endpoint=endpoint,
            params=params,
        )
        result: Any = None
        for step in endpoint.workflow.steps:
            result = binding.step_handlers[step.id].execute(context)
        return result if result is not None else context.scratch[binding.result]


def execute_workflow(http: HTTPService, endpoint_name: str, endpoint: EndpointSpec, params: dict[str, Any]) -> Any:
    """Execute one workflow endpoint with bound call params."""
    return WorkflowEndpointHandler(http).execute(endpoint_name, endpoint, params)
