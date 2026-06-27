"""Pydantic row-model validation pipeline.

Used by :func:`courtside_data.client._runner._execute` when the endpoint
declares a ``row_model``. Wraps each raw row through the Pydantic adapter,
drops BREF sentinel/header rows, and surfaces :class:`SchemaDriftError`
when no row in a non-empty table validates.

Output formatting is the runner's responsibility: this module returns
``(data, csv_column_names)`` and never touches the output service.
"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from pydantic import ValidationError

from courtside_data.client._pipelines.drop_reasons import (
    DROP_REASON_SCHEMA_VALIDATION_ERROR,
    row_drop_reason,
    sentinel_row_diagnostics,
)
from courtside_data.debug import DebugTrace
from courtside_data.debug._pipeline_events import (
    record_rows_filtered,
    record_sentinel_rows,
    record_validation_failed,
    record_validation_passed,
)
from courtside_data.debug.provenance import (
    PROVENANCE_WORKFLOW_PARSER_METADATA_UNAVAILABLE,
    build_dropped_row_provenance_records,
    build_field_provenance_records,
    classify_validation_drop,
    emit_field_provenance,
    get_trace_context,
)
from courtside_data.domain import OutputType
from courtside_data.errors import SchemaDriftError
from courtside_data.http._constants import BASE_URL
from courtside_data.schemas import ROW_ADAPTERS

if TYPE_CHECKING:
    from pydantic_core import InitErrorDetails


def _row_as_mapping(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    if hasattr(row, "model_dump"):
        dumped = row.model_dump()
        if isinstance(dumped, dict):
            return dumped
    return {}


def _extract_raw_rows(values: Any) -> list[dict[str, Any]]:
    """Pull raw rows out of row-model endpoint output, preserving empty results."""
    if isinstance(values, list):
        if all(isinstance(row, dict) for row in values):
            return values
        return []
    if isinstance(values, dict):
        for v in values.values():
            if isinstance(v, list) and all(isinstance(row, dict) for row in v):
                return v
    return []


def _validate_row_model_rows(
    row_model: Any,
    raw_rows: list[dict[str, Any]],
) -> tuple[list[Any], dict[str, int]]:
    values, dropped_reasons, _kept_indices, _dropped_details, drift_errors = _validate_row_model_rows_detailed(
        row_model,
        raw_rows,
    )
    if drift_errors and not values:
        raise ValidationError.from_exception_data(row_model.__name__, cast("list[InitErrorDetails]", drift_errors))
    return values, dropped_reasons


def _validate_row_model_rows_detailed(
    row_model: Any,
    raw_rows: list[dict[str, Any]],
) -> tuple[list[Any], dict[str, int], list[int], list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate rows one at a time, dropping invalid BREF sentinel/header rows.

    Basketball-Reference can interleave non-data rows with otherwise valid
    table rows. Keep the validated rows instead of failing the whole table, but
    still surface schema drift when no row in a non-empty table validates.
    """
    values: list[Any] = []
    kept_indices: list[int] = []
    drift_errors: list[dict[str, Any]] = []
    dropped_details: list[dict[str, Any]] = []
    dropped_reasons: dict[str, int] = {}
    for index, row in enumerate(raw_rows):
        try:
            values.append(row_model.model_validate(row))
            kept_indices.append(index)
        except ValidationError as exc:
            drop_reason = row_drop_reason(row)
            if drop_reason is not None:
                dropped_reasons[drop_reason] = dropped_reasons.get(drop_reason, 0) + 1
                dropped_details.append(
                    {
                        "row_index": index,
                        "reason": drop_reason,
                        "errors": exc.errors(),
                        "unresolved": False,
                    }
                )
                continue
            reason, unresolved = classify_validation_drop(exc.errors(), row=row)
            dropped_reasons[reason] = dropped_reasons.get(reason, 0) + 1
            dropped_details.append(
                {
                    "row_index": index,
                    "reason": reason,
                    "errors": exc.errors(),
                    "unresolved": unresolved,
                }
            )
            if reason == DROP_REASON_SCHEMA_VALIDATION_ERROR:
                for error in exc.errors():
                    enriched = dict(error)
                    enriched["row_index"] = index
                    drift_errors.append(enriched)
    return values, dropped_reasons, kept_indices, dropped_details, drift_errors


def _endpoint_url_context(endpoint: Any, params: dict[str, Any] | None) -> str:
    if endpoint is None:
        return "<unknown>"
    path = getattr(endpoint, "path", "<unknown>")
    if params:
        with contextlib.suppress(IndexError, KeyError, TypeError, ValueError):
            path = path.format(**params)
    if isinstance(path, str) and path.startswith("/"):
        return f"{BASE_URL}{path}"
    return str(path)


def validate_rows_pydantic(
    values: Any,
    *,
    row_model: Any,
    endpoint: Any,
    endpoint_name: str | None,
    endpoint_params: dict[str, Any] | None,
    csv_column_names: Sequence[str] | None,
    output_type: OutputType | None,
    raw: bool,
    trace: DebugTrace | None,
) -> tuple[Any, Sequence[str] | None]:
    """Validate ``values`` against ``row_model`` and return ``(data, csv_column_names)``.

    When ``raw=True``, the data is the unvalidated rows and the caller is
    responsible for the output envelope. When ``raw=False``, the data is
    the list of validated Pydantic instances, and ``SchemaDriftError`` is
    raised if no row in a non-empty table validates.
    """
    raw_rows = _extract_raw_rows(values)
    if trace is not None:
        trace.record(
            "runner",
            "row_model_pipeline_start",
            row_model=row_model.__name__,
            raw_row_count=len(raw_rows),
            raw_requested=raw,
        )
        trace.observe_rows("raw_rows", raw_rows, expected_columns=csv_column_names)
    if raw:
        return raw_rows, csv_column_names

    if ROW_ADAPTERS.get(endpoint_name) is None:
        raise RuntimeError(
            f"Endpoint {endpoint_name!r} declares row_model {row_model.__name__!r} but no adapter is registered."
        )
    try:
        if trace is not None:
            with trace.span("pydantic_validation", stage="validation", row_model=row_model.__name__):
                (
                    validated,
                    dropped_reasons,
                    kept_indices,
                    dropped_details,
                    drift_errors,
                ) = _validate_row_model_rows_detailed(row_model, raw_rows)
        else:
            (
                validated,
                dropped_reasons,
                kept_indices,
                dropped_details,
                drift_errors,
            ) = _validate_row_model_rows_detailed(row_model, raw_rows)
        if trace is not None:
            context = get_trace_context(trace)
            is_workflow_endpoint = getattr(getattr(endpoint, "kind", None), "value", None) == "workflow"
            if is_workflow_endpoint:
                trace.record(
                    "provenance",
                    "workflow_endpoint_provenance",
                    source_cell_mapping_available=False,
                    provenance_reason=PROVENANCE_WORKFLOW_PARSER_METADATA_UNAVAILABLE,
                )
            field_records = build_field_provenance_records(
                endpoint_name=endpoint_name,
                endpoint_params=endpoint_params,
                row_model=row_model,
                raw_rows=raw_rows,
                validated_rows=validated,
                kept_row_indices=kept_indices,
                context=context,
                workflow=is_workflow_endpoint,
            )
            dropped_records = build_dropped_row_provenance_records(
                endpoint_name=endpoint_name,
                endpoint_params=endpoint_params,
                raw_rows=raw_rows,
                dropped=dropped_details,
                context=context,
                workflow=is_workflow_endpoint,
            )
            emit_field_provenance(trace, field_records=field_records, dropped_records=dropped_records)
            record_rows_filtered(trace, dropped_row_reason_counts=dropped_reasons)
        if drift_errors and not validated:
            raise ValidationError.from_exception_data(row_model.__name__, cast("list[InitErrorDetails]", drift_errors))
        if trace is not None:
            sentinel_stats = sentinel_row_diagnostics([_row_as_mapping(row) for row in validated])
            record_sentinel_rows(
                trace,
                sentinel_row_count=sentinel_stats["sentinel_row_count"],
                sentinel_row_types=sentinel_stats["sentinel_row_types"],
            )
            record_validation_passed(
                trace,
                row_model=row_model.__name__,
                validated_row_count=len(validated),
            )
    except ValidationError as exc:
        if trace is not None:
            record_validation_failed(trace, row_model=row_model.__name__, errors=exc.errors())
            trace.record_exception(exc, stage="validation")
        raise SchemaDriftError(
            endpoint_name=endpoint_name or "<unknown>",
            url=_endpoint_url_context(endpoint, endpoint_params),
            pydantic_errors=cast("list[dict[str, Any]]", exc.errors()),
        ) from exc

    if output_type in (OutputType.CSV, OutputType.DATAFRAME):
        csv_column_names = tuple(row_model.model_fields)
    if trace is not None:
        trace.artifact("validated_rows", validated)
        trace.observe_rows("validated_rows", validated, expected_columns=tuple(row_model.model_fields))

    return validated, csv_column_names
