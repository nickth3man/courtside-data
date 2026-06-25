"""Dict-based coerce/validate pipeline.

Used by :func:`courtside_data.client._runner._execute` when an endpoint
intentionally omits a Pydantic row model. Coerces raw
``list[dict]`` values through
:func:`courtside_data.output.field_types.coerce_data` and (when enabled)
runs the row validator over the result.

Output formatting is the runner's responsibility: this module returns
``(data, csv_column_names)`` and never touches the output service.
"""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import Any

from courtside_data.data import OutputType
from courtside_data.debug import DebugTrace
from courtside_data.output.field_types import coerce_data
from courtside_data.output.type_validator import validate_rows


def _extract_rows(values: Any) -> list[dict[str, Any]] | None:
    """Pull the row list out of endpoint output (list[dict] or dict[str, list[dict]])."""
    if isinstance(values, list) and values and isinstance(values[0], dict):
        return values
    if isinstance(values, dict):
        for v in values.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return None


def _detect_csv_columns(rows: list[dict[str, Any]]) -> Sequence[str]:
    """Auto-detect CSV column names from row keys, stripping all-empty columns.

    Only used when an endpoint doesn't declare explicit column names; declared
    columns keep their contract even when empty.
    """
    column_names = list(rows[0].keys())
    non_empty = [k for k in column_names if any(row.get(k) not in (None, "", set(), []) for row in rows)]
    return non_empty or column_names


def validate_rows_legacy(
    values: Any,
    *,
    csv_column_names: Sequence[str] | None,
    output_type: OutputType | None,
    validate_output: bool,
    trace: DebugTrace | None,
) -> tuple[Any, Sequence[str] | None]:
    """Coerce and validate ``values`` using the legacy pipeline.

    Returns ``(data, csv_column_names)``. When ``csv_column_names`` is
    ``None`` and ``output_type`` is CSV/DataFrame, the columns are
    auto-detected from the coerced row keys.
    """
    if trace is not None:
        trace.record("runner", "coerce_data_start")
    if trace is not None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            with trace.span("coerce_data", stage="runner"):
                values = coerce_data(values)
        trace.metric("warnings.coerce_data.count", len(caught_warnings))
        if caught_warnings:
            trace.artifact(
                "coerce_data_warnings",
                [
                    {
                        "category": warning.category.__name__,
                        "message": str(warning.message),
                        "filename": warning.filename,
                        "lineno": warning.lineno,
                    }
                    for warning in caught_warnings
                ],
            )
    else:
        values = coerce_data(values)
    if trace is not None:
        trace.record("runner", "coerce_data_complete", value_type=type(values).__name__)
        trace.artifact("coerced_values", values)
        trace.observe_rows("coerced_values", values, expected_columns=csv_column_names)

    if output_type in (OutputType.CSV, OutputType.DATAFRAME) and csv_column_names is None:
        rows = _extract_rows(values)
        if rows is not None:
            csv_column_names = _detect_csv_columns(rows)
            if trace is not None:
                trace.record("output", "csv_columns_detected", column_names=list(csv_column_names))

    if validate_output and isinstance(values, list) and values and isinstance(values[0], dict):
        if trace is not None:
            with trace.span("legacy_validate_rows", stage="validation"):
                report = validate_rows(values, expected_columns=csv_column_names)
        else:
            report = validate_rows(values, expected_columns=csv_column_names)
        if trace is not None:
            trace.record(
                "validation",
                "legacy_validation_complete",
                ok=report.is_ok,
                error_count=report.error_count,
                errors=[str(error) for error in report.errors],
            )
        if not report.is_ok:
            error = ValueError(str(report))
            if trace is not None:
                trace.record_exception(error, stage="validation")
            raise error

    return values, csv_column_names
