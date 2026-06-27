"""Diagnostics-emitting workflow steps.

The :class:`EmitDiagnosticsStep` is a thin generic wrapper that invokes a
domain-specific emitter callable with the workflow execution context. The
module-level ``_emit_*`` helpers below carry the per-domain logic the
13 ``Emit*DiagnosticsStep`` dataclasses used to inline. Callers wrap them
with :func:`functools.partial` (when the call site needs to capture extra
constants) or pass them directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data._frozen import frozen_slot
from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.parsing.workflow_parsers._common import (
    _record_schedule_diagnostics,
    _record_standings_diagnostics,
)
from courtside_data.parsing.workflow_parsers._diagnostics import (
    emit_workflow_endpoint_diagnostics,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from courtside_data.parsing.workflows._context import WorkflowExecutionContext


@frozen_slot
class EmitDiagnosticsStep:
    """Generic step that invokes ``emitter(context)`` to record parser diagnostics.

    Replaces the 13 per-domain ``Emit*DiagnosticsStep`` classes whose
    ``execute()`` bodies were thin delegation to an emitter callable. The
    ``emitter`` is a closure (typically a :func:`functools.partial` wrapping
    one of the ``_emit_*`` helpers in this module) that captures any
    domain-specific constants and returns the value the workflow executor
    should pass to the next step.
    """

    emitter: Callable[[WorkflowExecutionContext], Any]

    def execute(self, context: WorkflowExecutionContext) -> Any:
        return self.emitter(context)


# --- per-domain emitter helpers --------------------------------------------
# These mirror the bodies of the 13 prior step classes. They are plain
# functions (not methods) so call sites can bind them with functools.partial
# or pass them straight to EmitDiagnosticsStep.


def _emit_player_game_log_diagnostics(
    context: WorkflowExecutionContext,
    *,
    parser_name: str,
    table_id: str,
) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    stats = {
        **context.scratch["parser_stats"],
        "season_count": 1,
        "selected_table_id": table_id,
    }
    emit_workflow_endpoint_diagnostics(
        parser_name=parser_name,
        endpoint_name=context.endpoint_name,
        rows=parsed_rows,
        source_sections=[f"table#{table_id}"],
        stats=stats,
        selected_table_id=table_id,
        candidate_table_ids=[table_id],
    )
    return parsed_rows


def _emit_player_totals_diagnostics(
    context: WorkflowExecutionContext,
    *,
    parser_name: str,
    table_id: str,
) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    emit_workflow_endpoint_diagnostics(
        parser_name=parser_name,
        endpoint_name=context.endpoint_name,
        rows=parsed_rows,
        source_sections=[f"table#{table_id}"],
        stats=context.scratch["parser_stats"],
        selected_table_id=table_id,
        candidate_table_ids=[table_id],
    )
    return parsed_rows


def _emit_award_voting_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    table_id = context.scratch["table_id"]
    trace = current_debug_trace()
    if trace is not None and context.scratch["award_table"] is not None:
        emit_parser_diagnostics(
            trace,
            parser_name="season_awards_voting",
            rows=parsed_rows,
            source_sections=[f"table#{table_id}"],
            workflow_diagnostics={"award_table_id": table_id},
        )
    return parsed_rows


def _emit_playoff_bracket_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    trace = current_debug_trace()
    if trace is not None and context.scratch["bracket_table"] is not None:
        emit_parser_diagnostics(
            trace,
            parser_name="playoff_bracket",
            rows=parsed_rows,
            source_sections=["table#all_playoffs"],
            workflow_diagnostics={"series_count": len(parsed_rows)},
        )
    return parsed_rows


def _emit_friv_outcomes_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    table_id = context.scratch["table_id"]
    trace = current_debug_trace()
    if trace is not None and context.scratch["outcome_table"] is not None:
        trace.record("parse", "friv_playoff_outcomes_parsed", table_id=table_id, row_count=len(parsed_rows))
        trace.artifact("raw_rows", parsed_rows)
        emit_parser_diagnostics(
            trace,
            parser_name="friv_playoff_outcomes",
            rows=parsed_rows,
            source_sections=[f"table#{table_id}"],
            workflow_diagnostics={"table_id": table_id},
        )
    return parsed_rows


def _emit_schedule_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    rows = context.scratch["rows"]
    _record_schedule_diagnostics(
        parser_name="season_schedule",
        parsed_rows=rows,
        stats=context.scratch["parser_stats"],
        month_page_count=context.scratch["month_page_count"],
    )
    return rows


def _emit_team_box_scores_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    emit_workflow_endpoint_diagnostics(
        parser_name="team_box_scores",
        endpoint_name="team_box_scores",
        rows=parsed_rows,
        source_sections=["td.gamelink a", 'table.stats_table[id$="-game-basic"]'],
        stats=context.scratch["parser_stats"],
    )
    return parsed_rows


def _emit_player_box_scores_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    emit_workflow_endpoint_diagnostics(
        parser_name="player_box_scores",
        endpoint_name="player_box_scores",
        rows=parsed_rows,
        source_sections=["table#stats"],
        stats=context.scratch["parser_stats"],
        selected_table_id="stats",
    )
    return parsed_rows


def _emit_box_score_diagnostics(
    context: WorkflowExecutionContext,
    *,
    parser_name: str,
    source_sections: tuple[str, ...],
) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    emit_workflow_endpoint_diagnostics(
        parser_name=parser_name,
        endpoint_name=context.endpoint_name,
        rows=parsed_rows,
        source_sections=source_sections,
        stats=context.scratch["parser_stats"],
    )
    return parsed_rows


def _emit_play_by_play_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    stats = context.scratch["parser_stats"]
    trace = current_debug_trace()
    if trace is not None:
        emit_parser_diagnostics(
            trace,
            parser_name="play_by_play",
            rows=parsed_rows,
            source_sections=["table#pbp"],
            parsed_event_count=stats["parsed_event_count"],
            ignored_event_count=stats["ignored_event_count"],
            ignored_event_reason_counts=stats["ignored_event_reason_counts"],
            period_count=stats["period_count"],
            score_event_count=stats["score_event_count"],
            substitution_event_count=stats["substitution_event_count"],
        )
    return parsed_rows


def _emit_standings_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    parsed_rows = context.scratch["rows"]
    _record_standings_diagnostics(
        parser_name="standings",
        parsed_rows=parsed_rows,
        source_sections=["table#divs_standings_E", "table#divs_standings_W"],
        stats=context.scratch["parser_stats"],
    )
    return parsed_rows


def _emit_standings_by_date_diagnostics(context: WorkflowExecutionContext) -> list[dict[str, Any]]:
    standings_rows = context.scratch["rows"]
    stats = context.scratch["parser_stats"]
    trace = current_debug_trace()
    if trace is not None:
        emit_parser_diagnostics(
            trace,
            parser_name="standings_by_date",
            rows=standings_rows,
            source_sections=stats["source_sections"],
            ignored_row_reason_counts=dict(stats["ignored_row_reason_counts"]),
            workflow_diagnostics={
                "conference_count": len(stats["conference_names"]),
                "team_count": len(standings_rows),
                "standings_section_count": len(stats["source_sections"]),
            },
        )
    return standings_rows


def _emit_search_diagnostics(context: WorkflowExecutionContext) -> dict[str, list[dict[str, Any]]]:
    player_results = context.scratch["search_player_results"]
    aggregate_stats = context.scratch["search_aggregate_stats"]
    ignored = aggregate_stats["ignored_result_reason_counts"]
    trace = current_debug_trace()
    if trace is not None:
        emit_parser_diagnostics(
            trace,
            parser_name="search",
            rows=player_results,
            source_sections=context.scratch["search_source_sections"],
            ignored_event_count=sum(ignored.values()) if ignored else None,
            ignored_event_reason_counts=dict(ignored) if ignored else None,
            workflow_diagnostics={
                "query": aggregate_stats["query"],
                "result_count": len(player_results),
                "candidate_count": aggregate_stats.get("candidate_count"),
                "matched_result_count": aggregate_stats.get("matched_result_count"),
                "ignored_result_reason_counts": dict(ignored) if ignored else {},
                "result_source": aggregate_stats.get("result_source"),
            },
        )
    return context.scratch["players"]
