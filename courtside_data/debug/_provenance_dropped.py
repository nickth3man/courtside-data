"""Dropped-row provenance records.

Per-row provenance for rows that the Pydantic adapter rejected: the raw
values, the matching source cells, the drop reason, and whether the drop
is "expected" (BREF sentinel/header) or "unresolved" (likely a real bug).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from courtside_data.client._pipelines._drop_reasons import (
    EXPECTED_DROP_REASONS,
    UNRESOLVED_DROP_REASONS,
    row_drop_reason,
    validation_error_drop_reason,
)
from courtside_data.debug._provenance_constants import (
    PROVENANCE_ROW_DROPPED_EXPECTED_REASON,
    PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR,
)
from courtside_data.debug._provenance_types import ProvenanceContext


def build_dropped_row_provenance_records(
    *,
    endpoint_name: str | None,
    endpoint_params: Mapping[str, Any] | None,
    raw_rows: Sequence[Mapping[str, Any]],
    dropped: Sequence[Mapping[str, Any]],
    context: ProvenanceContext | None,
    custom: bool,
) -> list[dict[str, Any]]:
    snapshot = context.source_snapshot if context is not None else None
    records: list[dict[str, Any]] = []
    for drop in dropped:
        row_index = int(drop["row_index"])
        row = raw_rows[row_index] if 0 <= row_index < len(raw_rows) else {}
        reason = str(drop["reason"])
        errors = list(drop.get("errors") or [])
        fields = _validation_error_fields(errors)
        raw_values = {field_name: row.get(field_name) for field_name in fields if field_name in row}
        source_cells: dict[str, Any] = {}
        if snapshot is not None:
            for field_name in fields:
                cell = snapshot.cell(row_index, field_name)
                if cell is not None:
                    source_cells[field_name] = {
                        "source_data_stat": cell.data_stat,
                        "source_header_text": cell.header_text,
                        "source_cell_raw": cell.raw_text,
                    }
        unresolved = bool(drop.get("unresolved"))
        records.append(
            {
                "endpoint_name": endpoint_name,
                "params": dict(endpoint_params or {}),
                "row_index": row_index,
                "raw_row": dict(row),
                "validation_errors": errors,
                "row_drop_reason": row_drop_reason(dict(row)),
                "validation_error_drop_reason": reason,
                "expected_drop": not unresolved,
                "unresolved_drop": unresolved,
                "fields_involved": fields,
                "raw_values": raw_values,
                "source_cells": source_cells,
                "custom": custom,
                "provenance_reason": (
                    PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR
                    if unresolved
                    else PROVENANCE_ROW_DROPPED_EXPECTED_REASON
                ),
            }
        )
    return records


def classify_validation_drop(errors: Sequence[Mapping[str, Any]], row: Mapping[str, Any]) -> tuple[str, bool]:
    """Return ``(reason, unresolved)`` for a failed Pydantic row."""
    reason = validation_error_drop_reason(errors, row=row)
    unresolved = reason in UNRESOLVED_DROP_REASONS or reason not in EXPECTED_DROP_REASONS
    return reason, unresolved


def _validation_error_fields(errors: Iterable[Mapping[str, Any]]) -> list[str]:
    fields: list[str] = []
    for error in errors:
        loc = error.get("loc")
        parts: Iterable[Any]
        if isinstance(loc, tuple | list):
            parts = loc
        elif loc is None:
            parts = ()
        else:
            parts = (loc,)
        for part in parts:
            name = str(part)
            if name not in fields:
                fields.append(name)
    return fields
