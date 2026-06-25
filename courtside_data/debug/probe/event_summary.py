"""Per-endpoint debug-event summarization.

Turns the debug events from a single endpoint call into the flat, probe-friendly
summary dict consumed by the report/CSV layers. :func:`_summarize_debug_events`
is the entry point; it:

1. walks the events once via :func:`courtside_data.debug.probe.event_scan.scan_events`
   (HTTP/response metadata, table resolution, parser/model identity, validation
   status, provenance counts, row-count accounting),
2. folds in endpoint-registry metadata and a bounded first-row preview, then
3. assembles the final summary.

The ``_summarize_metrics`` / ``_summarize_row_counts`` / ``_summarize_trace_file``
helpers cover metrics, row-count accounting, and trace-file stats it depends on.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from courtside_data.debug.probe.event_fields import _event_attributes, _traceback_hash, _traceback_tail
from courtside_data.debug.probe.event_scan import _EventScan, scan_events
from courtside_data.debug.probe.previews import (
    _field_names_from_row,
    _infer_output_type,
    _preview_result,
    _row_count,
)
from courtside_data.debug.probe.samples import _endpoint_domain, _endpoint_kind
from courtside_data.endpoints import ENDPOINTS


def _summarize_metrics(
    debug: Mapping[str, Any],
    *,
    duration_ms: Any = None,
    response_bytes: int | None = None,
    rate_limit_wait_ms: float | None = None,
) -> dict[str, Any]:
    """Merge trace metrics with span timings and known probe counters."""
    base = dict(debug.get("metrics") or {})
    if isinstance(duration_ms, int | float):
        base["duration_ms.total"] = round(float(duration_ms), 3)
    if isinstance(response_bytes, int):
        base["response_bytes"] = response_bytes
    if isinstance(rate_limit_wait_ms, int | float) and rate_limit_wait_ms:
        base["rate_limit_wait_ms"] = round(float(rate_limit_wait_ms), 3)
    for span in debug.get("spans") or []:
        if not isinstance(span, dict):
            continue
        stage = span.get("stage")
        duration = span.get("duration_ms")
        if isinstance(stage, str) and isinstance(duration, int | float):
            key = f"duration_ms.{stage}"
            base[key] = round(float(base.get(key, 0.0)) + float(duration), 3)
    return base


def _summarize_row_counts(
    events: Sequence[Mapping[str, Any]],
    *,
    output_row_count: int | None,
    raw_table_row_count: int | None,
) -> dict[str, Any]:
    """Cross-reference pipeline events to explain row filtering."""
    raw_row_count: int | None = None
    parsed_row_count: int | None = None
    validated_row_count: int | None = None
    dropped_reasons: dict[str, int] = {}

    for event in events:
        stage = str(event.get("stage") or "")
        event_name = str(event.get("event") or "")
        attributes = _event_attributes(event)

        if stage == "runner" and event_name == "row_model_pipeline_start":
            pipeline_raw = attributes.get("raw_row_count")
            if isinstance(pipeline_raw, int):
                raw_row_count = pipeline_raw

        if stage == "parse" and event_name == "parsed_rows_summary":
            explicit_parsed = attributes.get("parsed_row_count")
            if isinstance(explicit_parsed, int):
                parsed_row_count = explicit_parsed

        if stage == "parse" and event_name == "generic_table_parsed":
            table_rows = attributes.get("row_count")
            if isinstance(table_rows, int) and parsed_row_count is None:
                parsed_row_count = table_rows

        if stage == "validation" and event_name == "pydantic_validation_complete":
            validated = attributes.get("validated_row_count")
            if not isinstance(validated, int):
                validated = attributes.get("row_count")
            if isinstance(validated, int):
                validated_row_count = validated

        if stage == "validation" and event_name == "rows_filtered":
            reason_counts = attributes.get("dropped_row_reason_counts")
            if isinstance(reason_counts, dict):
                for key, value in reason_counts.items():
                    if isinstance(value, int | float):
                        reason_key = str(key)
                        dropped_reasons[reason_key] = dropped_reasons.get(reason_key, 0) + int(value)

        if event_name in {"rows_dropped", "row_dropped"}:
            reason = attributes.get("reason")
            count = attributes.get("count", 1)
            if isinstance(count, int | float):
                key = str(reason) if reason is not None else "unknown"
                dropped_reasons[key] = dropped_reasons.get(key, 0) + int(count)

    if raw_row_count is None and isinstance(raw_table_row_count, int):
        raw_row_count = raw_table_row_count
    if parsed_row_count is None and isinstance(raw_table_row_count, int):
        parsed_row_count = raw_table_row_count

    baseline = raw_row_count if raw_row_count is not None else parsed_row_count
    after_validation = validated_row_count if validated_row_count is not None else output_row_count
    dropped_row_count: int | None = None
    if dropped_reasons:
        dropped_row_count = sum(dropped_reasons.values())
    elif isinstance(baseline, int) and isinstance(after_validation, int) and baseline > after_validation:
        dropped_row_count = baseline - after_validation
        dropped_reasons = {"unknown": dropped_row_count}

    return {
        "raw_row_count": raw_row_count,
        "parsed_row_count": parsed_row_count,
        "validated_row_count": validated_row_count,
        "output_row_count": output_row_count,
        "dropped_row_count": dropped_row_count,
        "dropped_row_reason_counts_json": dropped_reasons,
    }


def _summarize_trace_file(trace_log_path: str | None) -> dict[str, Any]:
    if not trace_log_path:
        return {"trace_log_exists": False, "trace_log_size_bytes": None}
    trace_path = Path(trace_log_path)
    if not trace_path.is_absolute():
        trace_path = Path.cwd() / trace_path
    if trace_path.exists():
        return {"trace_log_exists": True, "trace_log_size_bytes": trace_path.stat().st_size}
    return {"trace_log_exists": False, "trace_log_size_bytes": None}


def _initial_summary(
    debug: Mapping[str, Any],
    *,
    output_row_count: int | None,
    trace_log_path: str | None,
) -> dict[str, Any]:
    """Seed the summary dict with defaults + envelope-level status fields."""
    status_raw = debug.get("status")
    status = status_raw if isinstance(status_raw, dict) else {}
    stage_counts_raw = debug.get("stage_counts")
    stage_counts = stage_counts_raw if isinstance(stage_counts_raw, dict) else {}
    debug_status = status.get("code")

    return {
        "duration_ms": debug.get("duration_ms"),
        "debug_status": debug_status,
        "error_type": status.get("error_type"),
        "error_message": status.get("error_message"),
        "row_count": output_row_count,
        "stage_counts": dict(stage_counts),
        "trace_id": debug.get("trace_id"),
        "event_count": 0,
        "warning_count": 0,
        "error_event_count": 0,
        "candidate_table_ids_json": [],
        "validation_error_paths_json": [],
        "validation_status": None,
        "raw_columns_json": [],
        "parsed_fields_json": [],
        "validated_fields_json": [],
        "output_fields_json": [],
        "dropped_row_reason_counts_json": {},
        "provenance_field_count": None,
        "provenance_final_none_count": None,
        "provenance_reason_counts_json": {},
        "provenance_none_reason_counts_json": {},
        "parser_missed_column_count": None,
        "schema_defaulted_field_count": None,
        "validator_coerced_field_count": None,
        "validator_transformed_field_count": None,
        "provenance_dropped_row_count": None,
        "provenance_dropped_row_reason_counts_json": {},
        "provenance_unresolved_drop_count": None,
        "workflow_provenance_unavailable_count": None,
        "source_sections_json": [],
        "ignored_event_reason_counts_json": {},
        "workflow_diagnostics_json": {},
        "first_row_preview_json": None,
        "first_row_preview_truncated": None,
        "first_row_preview_field_count": None,
        "first_row_total_field_count": None,
        **(_summarize_trace_file(trace_log_path)),
    }


def _merge_scan_counts(summary: dict[str, Any], scan: _EventScan) -> None:
    """Copy the loop-accumulated counters/provenance maps onto the summary.

    These keys were written into the summary mid-loop in the original
    implementation; the scan now owns them and they are folded back here.
    """
    summary["error_event_count"] = scan.error_event_count
    summary["warning_count"] = scan.warning_count
    summary["ignored_event_reason_counts_json"] = scan.ignored_event_reason_counts
    summary["validation_error_paths_json"] = scan.validation_error_paths
    summary["parser_missed_column_count"] = scan.parser_missed_column_count
    summary["workflow_provenance_unavailable_count"] = scan.workflow_provenance_unavailable_count
    summary["provenance_field_count"] = scan.provenance_field_count
    summary["provenance_final_none_count"] = scan.provenance_final_none_count
    summary["schema_defaulted_field_count"] = scan.schema_defaulted_field_count
    summary["validator_coerced_field_count"] = scan.validator_coerced_field_count
    summary["validator_transformed_field_count"] = scan.validator_transformed_field_count
    summary["provenance_dropped_row_count"] = scan.provenance_dropped_row_count
    summary["provenance_unresolved_drop_count"] = scan.provenance_unresolved_drop_count
    summary["provenance_reason_counts_json"] = scan.provenance_reason_counts
    summary["provenance_none_reason_counts_json"] = scan.provenance_none_reason_counts
    summary["provenance_dropped_row_reason_counts_json"] = scan.provenance_dropped_row_reason_counts


def _apply_endpoint_metadata(summary: dict[str, Any], scan: _EventScan, endpoint_name: str | None) -> None:
    """Fold endpoint-registry metadata into the summary + scan identity fields."""
    endpoint = ENDPOINTS.get(endpoint_name) if endpoint_name is not None else None
    if endpoint is not None:
        summary["endpoint_domain"] = _endpoint_domain(endpoint)
        summary["endpoint_kind"] = _endpoint_kind(endpoint)
        summary["required_params_json"] = list(endpoint.params)
        summary["url_template"] = endpoint.path
        if scan.model_name is None and endpoint.row_model is not None:
            scan.model_name = endpoint.row_model.__name__
        if endpoint.row_model is not None:
            summary["validated_fields_json"] = sorted(endpoint.row_model.model_fields)
        elif scan.validation_status is None:
            scan.validation_status = "not_run"
    elif scan.validation_status is None:
        scan.validation_status = "unknown"

    if scan.validation_status is None and endpoint is not None and endpoint.row_model is not None:
        scan.validation_status = "unknown"


@dataclass
class _OutputShape:
    """Output-field and first-row-preview values derived from the result ``data``."""

    output_fields: list[str]
    output_field_count: int | None
    output_type: str | None
    first_row_preview: Any
    first_row_preview_truncated: bool | None
    first_row_preview_field_count: int | None
    first_row_total_field_count: int | None


def _resolve_output_shape(summary: Mapping[str, Any], scan: _EventScan, data: Any) -> _OutputShape:
    """Derive output field names + a bounded first-row preview from ``data``."""
    output_fields: list[str] = []
    output_field_count = scan.output_field_count
    first_row_preview: Any = None
    first_row_preview_truncated: bool | None = None
    first_row_preview_field_count: int | None = None
    first_row_total_field_count: int | None = None

    if isinstance(data, list) and data:
        first_item = data[0]
        row: dict[str, Any] | None = None
        if isinstance(first_item, dict):
            row = first_item
        elif hasattr(first_item, "model_dump"):
            dumped = first_item.model_dump()
            row = dumped if isinstance(dumped, dict) else None
            if row is None:
                first_row_preview = first_item
        else:
            first_row_preview = first_item

        if row is not None:
            output_fields = _field_names_from_row(row)
            if output_field_count is None:
                output_field_count = len(output_fields)
            preview = _preview_result(row)
            first_row_preview = preview[0]
            first_row_preview_truncated = preview[1]
            first_row_preview_field_count = preview[2]
            first_row_total_field_count = preview[3]

    if not output_fields and summary.get("validated_fields_json"):
        output_fields = list(summary["validated_fields_json"])
        if output_field_count is None:
            output_field_count = len(output_fields)

    return _OutputShape(
        output_fields=output_fields,
        output_field_count=output_field_count,
        output_type=_infer_output_type(data, scan.model_name),
        first_row_preview=first_row_preview,
        first_row_preview_truncated=first_row_preview_truncated,
        first_row_preview_field_count=first_row_preview_field_count,
        first_row_total_field_count=first_row_total_field_count,
    )


def _summarize_debug_events(
    debug: Mapping[str, Any],
    *,
    data: Any = None,
    endpoint_name: str | None = None,
    trace_log_path: str | None = None,
) -> dict[str, Any]:
    """Walk debug events and extract probe-friendly diagnostics."""
    events = [event for event in (debug.get("events") or []) if isinstance(event, dict)]
    output_row_count = _row_count(data)

    summary = _initial_summary(debug, output_row_count=output_row_count, trace_log_path=trace_log_path)
    summary["event_count"] = len(events)

    scan = scan_events(events)
    _merge_scan_counts(summary, scan)
    _apply_endpoint_metadata(summary, scan, endpoint_name)
    shape = _resolve_output_shape(summary, scan, data)

    # Workflow parsers can surface table-id hints through diagnostics when a
    # generic table-resolution event was not emitted.
    selected_table_id = scan.selected_table_id
    candidate_table_ids = scan.candidate_table_ids
    if selected_table_id is None:
        table_from_workflow = scan.workflow_diagnostics.get("selected_table_id")
        if isinstance(table_from_workflow, str):
            selected_table_id = table_from_workflow
    if not candidate_table_ids:
        workflow_candidates = scan.workflow_diagnostics.get("candidate_table_ids")
        if isinstance(workflow_candidates, list):
            candidate_table_ids = [str(item) for item in workflow_candidates]

    rounded_rate_limit_wait_ms = round(scan.rate_limit_wait_ms, 3) if scan.rate_limit_wait_ms else None
    metrics = _summarize_metrics(
        debug,
        duration_ms=summary["duration_ms"],
        response_bytes=scan.response_bytes,
        rate_limit_wait_ms=rounded_rate_limit_wait_ms,
    )
    row_count_summary = _summarize_row_counts(
        events,
        output_row_count=output_row_count,
        raw_table_row_count=scan.raw_table_row_count,
    )

    raw_column_count = (
        scan.raw_table_column_count if scan.raw_table_column_count is not None else (len(scan.raw_columns) or None)
    )
    parsed_field_count = len(scan.parsed_fields) if scan.parsed_fields else raw_column_count
    validated_field_count = len(summary["validated_fields_json"]) if summary["validated_fields_json"] else None

    summary.update(
        {
            "metrics": metrics,
            "http_status_code": scan.http_status_code,
            "http_reason": scan.http_reason,
            "resolved_url": scan.resolved_url,
            "content_type": scan.content_type,
            "response_bytes": scan.response_bytes,
            "redirect_count": scan.redirect_count,
            "rate_limit_wait_ms": rounded_rate_limit_wait_ms,
            "failed_stage": scan.failed_stage,
            "last_event": scan.last_event,
            "last_successful_stage": scan.last_successful_stage,
            "selected_table_id": selected_table_id,
            "candidate_table_ids_json": candidate_table_ids,
            "raw_table_row_count": scan.raw_table_row_count,
            "raw_table_column_count": scan.raw_table_column_count,
            "parser_name": scan.parser_name,
            "model_name": scan.model_name,
            "validation_status": scan.validation_status,
            "validation_error_count": scan.validation_error_count,
            "output_type": shape.output_type,
            "raw_column_count": raw_column_count,
            "raw_columns_json": scan.raw_columns,
            "parsed_field_count": parsed_field_count,
            "parsed_fields_json": scan.parsed_fields,
            "validated_field_count": validated_field_count,
            "output_field_count": shape.output_field_count,
            "output_fields_json": shape.output_fields,
            "source_sections_json": scan.source_sections,
            "parsed_event_count": scan.parsed_event_count,
            "ignored_event_count": scan.ignored_event_count,
            "period_count": scan.period_count,
            "score_event_count": scan.score_event_count,
            "substitution_event_count": scan.substitution_event_count,
            "workflow_diagnostics_json": scan.workflow_diagnostics,
            "first_row_preview_json": shape.first_row_preview,
            "first_row_preview_truncated": shape.first_row_preview_truncated,
            "first_row_preview_field_count": shape.first_row_preview_field_count,
            "first_row_total_field_count": shape.first_row_total_field_count,
            "trace_log_path": trace_log_path,
            "traceback_tail": _traceback_tail(scan.traceback_text),
            "traceback_hash": _traceback_hash(scan.traceback_text),
            **row_count_summary,
        }
    )
    return summary
