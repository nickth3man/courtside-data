"""Provenance emission and summary.

Emits field / dropped-row provenance records to a :class:`DebugTrace` and
builds the per-endpoint summary dict that the probe / report layers
consume. The sampler here is also the single source of "detail" vs.
"summary" decisioning when ``trace.config.detail_level != "full"``.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from courtside_data.debug._provenance_constants import (
    PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN,
    PROVENANCE_UNKNOWN,
    PROVENANCE_WORKFLOW_PARSER_METADATA_UNAVAILABLE,
)
from courtside_data.debug._provenance_context import _SAMPLE_LIMIT
from courtside_data.debug.trace import DebugTrace


def emit_field_provenance(
    trace: DebugTrace,
    *,
    field_records: Sequence[Mapping[str, Any]],
    dropped_records: Sequence[Mapping[str, Any]],
) -> None:
    summary = summarize_provenance(field_records=field_records, dropped_records=dropped_records)
    detail_records = list(field_records)
    detail_drops = list(dropped_records)
    if trace.config.detail_level != "full":
        detail_records = _sample_records_by_reason(detail_records)
        detail_drops = _sample_records_by_reason(detail_drops)

    trace.artifact("field_provenance", detail_records)
    if detail_drops:
        trace.artifact("dropped_row_provenance", detail_drops)
    trace.record("provenance", "field_provenance_summary", **summary)


def summarize_provenance(
    *,
    field_records: Sequence[Mapping[str, Any]],
    dropped_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    reason_counts: Counter[str] = Counter(
        str(record.get("provenance_reason") or PROVENANCE_UNKNOWN) for record in field_records
    )
    none_reason_counts: Counter[str] = Counter(
        str(record.get("provenance_reason") or PROVENANCE_UNKNOWN)
        for record in field_records
        if record.get("final_value") is None
    )
    dropped_reason_counts: Counter[str] = Counter(
        str(record.get("validation_error_drop_reason") or record.get("row_drop_reason") or PROVENANCE_UNKNOWN)
        for record in dropped_records
    )
    parser_missed = sum(
        1 for record in field_records if record.get("provenance_reason") == PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN
    )
    return {
        "provenance_field_count": len(field_records),
        "provenance_final_none_count": sum(1 for record in field_records if record.get("final_value") is None),
        "provenance_reason_counts": dict(sorted(reason_counts.items())),
        "provenance_none_reason_counts": dict(sorted(none_reason_counts.items())),
        "parser_missed_column_count": parser_missed,
        "schema_defaulted_field_count": sum(1 for record in field_records if record.get("schema_default_used") is True),
        "validator_coerced_field_count": sum(
            1 for record in field_records if record.get("validator_coerced_to_none") is True
        ),
        "validator_transformed_field_count": sum(
            1 for record in field_records if record.get("validator_transformed") is True
        ),
        "provenance_dropped_row_count": len(dropped_records),
        "provenance_dropped_row_reason_counts": dict(sorted(dropped_reason_counts.items())),
        "provenance_unresolved_drop_count": sum(
            1 for record in dropped_records if record.get("unresolved_drop") is True
        ),
        "workflow_provenance_unavailable_count": sum(
            1
            for record in field_records
            if record.get("provenance_reason") == PROVENANCE_WORKFLOW_PARSER_METADATA_UNAVAILABLE
        ),
    }


def _sample_records_by_reason(records: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    by_reason: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        reason = str(record.get("provenance_reason") or PROVENANCE_UNKNOWN)
        if len(by_reason[reason]) < _SAMPLE_LIMIT:
            by_reason[reason].append(record)
    sampled: list[Mapping[str, Any]] = []
    for reason in sorted(by_reason):
        sampled.extend(by_reason[reason])
    return sampled
