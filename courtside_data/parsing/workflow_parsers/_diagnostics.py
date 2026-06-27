"""Shared parser instrumentation constants and emit helpers."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from courtside_data._row_exclusion import RowExclusionReason
from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics

# Parser-level ignored-row reasons (emitted before validation). Each constant
# is an alias of the corresponding ``RowExclusionReason`` member's ``.value``
# so the emitted string is byte-identical to the original. See
# :mod:`courtside_data._row_exclusion` for the canonical registry.
IGNORE_MISSING_DATE = RowExclusionReason.PARSER_MISSING_DATE.value
IGNORE_INACTIVE_GAME = RowExclusionReason.PARSER_INACTIVE_GAME.value
IGNORE_MISSING_NAME_OR_TEAM = RowExclusionReason.PARSER_MISSING_NAME_OR_TEAM.value
IGNORE_COMBINED_TEAM = RowExclusionReason.PARSER_COMBINED_TEAM.value
IGNORE_MISSING_TABLE = RowExclusionReason.PARSER_MISSING_TABLE.value
IGNORE_MISSING_FOOTER = RowExclusionReason.PARSER_MISSING_FOOTER.value
IGNORE_EMPTY_TABLE = RowExclusionReason.PARSER_EMPTY_TABLE.value

_WORKFLOW_DIAGNOSTIC_KEYS = (
    "game_count",
    "team_count",
    "player_count",
    "active_player_count",
    "inactive_player_count",
    "starter_count",
    "bench_count",
    "official_count",
    "scorebox_meta_count",
    "stat_table_count",
    "basic_table_count",
    "advanced_table_count",
    "missing_table_count",
    "empty_table_count",
    "season_count",
    "ranked_row_count",
    "repeated_header_count",
    "raw_row_count",
    "raw_column_count",
)


def increment_ignored(ignored: dict[str, int], reason: str) -> None:
    ignored[reason] = ignored.get(reason, 0) + 1


def merge_ignored_counts(aggregate: Counter[str], page: Mapping[str, int]) -> None:
    for reason, count in page.items():
        aggregate[reason] += int(count)


def merge_numeric_stats(aggregate: dict[str, Any], page: Mapping[str, Any], *, keys: Sequence[str]) -> None:
    for key in keys:
        value = page.get(key)
        if isinstance(value, int | float):
            aggregate[key] = int(aggregate.get(key, 0)) + int(value)


def emit_workflow_endpoint_diagnostics(
    *,
    parser_name: str,
    endpoint_name: str,
    rows: Sequence[Mapping[str, Any]],
    source_sections: Sequence[str],
    stats: Mapping[str, Any],
    selected_table_id: str | None = None,
    candidate_table_ids: Sequence[str] | None = None,
) -> None:
    """Emit compact parser summary events when a debug trace is active."""
    trace = current_debug_trace()
    if trace is None:
        return

    ignored = stats.get("ignored_row_reason_counts") or {}
    ignored_mapping = dict(ignored) if isinstance(ignored, Mapping) else {}
    workflow: dict[str, Any] = {"endpoint_name": endpoint_name}
    for key in _WORKFLOW_DIAGNOSTIC_KEYS:
        if key in stats and stats[key] is not None:
            workflow[key] = stats[key]

    table_id = selected_table_id or stats.get("selected_table_id")
    if isinstance(table_id, str):
        workflow["selected_table_id"] = table_id
    if candidate_table_ids:
        workflow["candidate_table_ids"] = [str(table_id) for table_id in candidate_table_ids]
    elif isinstance(stats.get("candidate_table_ids"), list):
        workflow["candidate_table_ids"] = [str(table_id) for table_id in stats["candidate_table_ids"]]

    emit_parser_diagnostics(
        trace,
        parser_name=parser_name,
        rows=rows,
        source_sections=source_sections,
        ignored_event_count=sum(ignored_mapping.values()) if ignored_mapping else None,
        ignored_event_reason_counts=ignored_mapping,
        ignored_row_reason_counts=ignored_mapping,
        workflow_diagnostics=workflow,
    )
