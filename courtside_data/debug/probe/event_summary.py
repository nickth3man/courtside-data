"""Per-endpoint debug-event summarization.

Walks the debug events from a single endpoint call and extracts probe-friendly
diagnostics: HTTP/response metadata, table resolution, parser/model identity,
validation status, provenance counts, row-count accounting, and a bounded
first-row preview. ``_summarize_debug_events`` is the entry point; the
``_summarize_*`` helpers cover metrics, row-count accounting, and trace-file
stats it depends on.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from courtside_data.debug.probe.event_fields import (
    _HTTP_RESPONSE_EVENTS,
    _content_type_from_headers,
    _event_attributes,
    _event_label,
    _table_id_from_selector,
    _traceback_hash,
    _traceback_tail,
    _validation_error_paths,
)
from courtside_data.debug.probe.previews import (
    _field_names_from_row,
    _infer_output_type,
    _preview_result,
    _row_count,
)
from courtside_data.debug.probe.samples import _ENDPOINT_GROUPS
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


def _summarize_debug_events(
    debug: Mapping[str, Any],
    *,
    data: Any = None,
    endpoint_name: str | None = None,
    trace_log_path: str | None = None,
) -> dict[str, Any]:
    """Walk debug events and extract probe-friendly diagnostics."""
    events = [event for event in (debug.get("events") or []) if isinstance(event, dict)]
    status_raw = debug.get("status")
    status = status_raw if isinstance(status_raw, dict) else {}
    stage_counts_raw = debug.get("stage_counts")
    stage_counts = stage_counts_raw if isinstance(stage_counts_raw, dict) else {}
    debug_status = status.get("code")

    output_row_count = _row_count(data)
    summary: dict[str, Any] = {
        "duration_ms": debug.get("duration_ms"),
        "status_code": debug_status,
        "debug_status": debug_status,
        "error_type": status.get("error_type"),
        "error_message": status.get("error_message"),
        "row_count": output_row_count,
        "stage_counts": dict(stage_counts),
        "trace_id": debug.get("trace_id"),
        "event_count": len(events),
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
        "custom_provenance_unavailable_count": None,
        "source_sections_json": [],
        "ignored_event_reason_counts_json": {},
        "custom_diagnostics_json": {},
        "first_row_preview_json": None,
        "first_row_preview_truncated": None,
        "first_row_preview_field_count": None,
        "first_row_total_field_count": None,
        **(_summarize_trace_file(trace_log_path)),
    }

    last_event: str | None = None
    last_successful_stage: str | None = None
    failed_stage: str | None = None
    http_status_code: int | None = None
    http_reason: str | None = None
    resolved_url: str | None = None
    content_type: str | None = None
    response_bytes: int | None = None
    redirect_count: int | None = None
    rate_limit_wait_ms = 0.0
    selected_table_id: str | None = None
    candidate_table_ids: list[str] = []
    raw_table_row_count: int | None = None
    raw_table_column_count: int | None = None
    raw_columns: list[str] = []
    parsed_fields: list[str] = []
    parser_name: str | None = None
    model_name: str | None = None
    validation_error_count: int | None = None
    validation_status: str | None = None
    output_type: str | None = None
    output_field_count: int | None = None
    output_fields: list[str] = []
    first_row_preview: Any = None
    first_row_preview_truncated: bool | None = None
    first_row_preview_field_count: int | None = None
    first_row_total_field_count: int | None = None
    traceback_text: str | None = None
    parsed_event_count: int | None = None
    ignored_event_count: int | None = None
    period_count: int | None = None
    score_event_count: int | None = None
    substitution_event_count: int | None = None
    source_sections: list[str] = []
    custom_diagnostics: dict[str, Any] = {}

    for event in events:
        event_name = str(event.get("event") or "")
        stage = str(event.get("stage") or "")
        event_status = str(event.get("status") or "ok")
        attributes = _event_attributes(event)
        label = _event_label(event)
        last_event = label

        if event_status == "error":
            summary["error_event_count"] += 1
            failed_stage = stage or failed_stage
        elif event_status in {"cancelled", "warn"} or str(event.get("severity_text") or "").upper() == "WARN":
            summary["warning_count"] += 1

        if event_status == "ok" and stage:
            last_successful_stage = stage

        if event_name in _HTTP_RESPONSE_EVENTS:
            status_code = attributes.get("status_code")
            if isinstance(status_code, int):
                http_status_code = status_code
            reason = attributes.get("reason_phrase")
            if isinstance(reason, str):
                http_reason = reason
            url = attributes.get("final_url") or attributes.get("url")
            if isinstance(url, str):
                resolved_url = url
            response_size = attributes.get("response_bytes")
            if isinstance(response_size, int):
                response_bytes = response_size
            redirects = attributes.get("redirect_count")
            if isinstance(redirects, int):
                redirect_count = redirects
            headers = attributes.get("headers")
            parsed_content_type = _content_type_from_headers(headers)
            if parsed_content_type is not None:
                content_type = parsed_content_type

        if stage == "rate_limit" and event_name == "sleep":
            wait_seconds = attributes.get("wait_seconds")
            if isinstance(wait_seconds, int | float):
                rate_limit_wait_ms += float(wait_seconds) * 1000.0

        if stage == "endpoint" and event_name == "run_endpoint_start":
            row_model = attributes.get("row_model")
            if isinstance(row_model, str):
                model_name = row_model
            if attributes.get("custom") is True:
                parser_name = "custom"
            elif parser_name is None:
                parser_name = "generic"

        if stage == "endpoint" and event_name == "custom_service_dispatch":
            parser_name = "custom"

        if stage == "endpoint" and event_name == "generic_service_dispatch":
            parser_name = "generic"

        if stage == "parse" and event_name == "parsed_rows_summary":
            summary_parser = attributes.get("parser_name")
            if isinstance(summary_parser, str):
                parser_name = summary_parser
            parsed_fields_attr = attributes.get("parsed_fields")
            if isinstance(parsed_fields_attr, list):
                parsed_fields = [str(name) for name in parsed_fields_attr]

        if stage == "parse" and event_name == "generic_table_parsed":
            parser_name = "generic_table"
            row_count_value = attributes.get("row_count")
            if isinstance(row_count_value, int):
                raw_table_row_count = row_count_value
            column_names = attributes.get("column_names")
            if isinstance(column_names, list):
                raw_table_column_count = len(column_names)
                raw_columns = [str(name) for name in column_names]
                if not parsed_fields:
                    parsed_fields = list(raw_columns)

        if stage == "parse" and event_name == "friv_playoff_outcomes_parsed":
            parser_name = "friv_playoff_outcomes"
            table_id = attributes.get("table_id")
            if isinstance(table_id, str):
                selected_table_id = table_id

        if stage == "parse" and event_name.endswith("_parsed"):
            custom_parser = attributes.get("parser_name")
            if isinstance(custom_parser, str):
                parser_name = custom_parser
            parsed_events = attributes.get("parsed_event_count")
            if isinstance(parsed_events, int):
                parsed_event_count = parsed_events
            ignored_events = attributes.get("ignored_event_count")
            if isinstance(ignored_events, int):
                ignored_event_count = ignored_events
            ignored_reasons = attributes.get("ignored_event_reason_counts")
            if isinstance(ignored_reasons, dict):
                summary["ignored_event_reason_counts_json"] = {
                    str(key): int(value) for key, value in ignored_reasons.items() if isinstance(value, int | float)
                }
            sections = attributes.get("source_sections")
            if isinstance(sections, list):
                source_sections = [str(section) for section in sections]
            periods = attributes.get("period_count")
            if isinstance(periods, int):
                period_count = periods
            score_events = attributes.get("score_event_count")
            if isinstance(score_events, int):
                score_event_count = score_events
            substitution_events = attributes.get("substitution_event_count")
            if isinstance(substitution_events, int):
                substitution_event_count = substitution_events
            custom_diag = attributes.get("custom_diagnostics")
            if isinstance(custom_diag, dict):
                custom_diagnostics.update({str(key): value for key, value in custom_diag.items() if value is not None})
            ignored_rows = attributes.get("ignored_row_reason_counts")
            if isinstance(ignored_rows, dict) and ignored_rows:
                custom_diagnostics.setdefault("ignored_row_reason_counts", {})
                existing_ignored_rows = custom_diagnostics["ignored_row_reason_counts"]
                if isinstance(existing_ignored_rows, dict):
                    for key, value in ignored_rows.items():
                        if isinstance(value, int | float):
                            reason_key = str(key)
                            existing_ignored_rows[reason_key] = existing_ignored_rows.get(reason_key, 0) + int(value)

        if stage == "validation" and event_name == "sentinel_rows_observed":
            sentinel_count = attributes.get("sentinel_row_count")
            if isinstance(sentinel_count, int):
                custom_diagnostics["sentinel_row_count"] = sentinel_count
            sentinel_types = attributes.get("sentinel_row_types")
            if isinstance(sentinel_types, dict):
                custom_diagnostics["sentinel_row_types"] = {
                    str(key): int(value) for key, value in sentinel_types.items() if isinstance(value, int | float)
                }

        if stage == "provenance" and event_name == "source_table_provenance":
            missed = attributes.get("parser_missed_column_count")
            if isinstance(missed, int):
                summary["parser_missed_column_count"] = missed

        if (
            stage == "provenance"
            and event_name == "custom_endpoint_provenance"
            and attributes.get("source_cell_mapping_available") is False
        ):
            summary["custom_provenance_unavailable_count"] = max(
                int(summary.get("custom_provenance_unavailable_count") or 0),
                1,
            )

        if stage == "provenance" and event_name == "field_provenance_summary":
            for key in (
                "provenance_field_count",
                "provenance_final_none_count",
                "parser_missed_column_count",
                "schema_defaulted_field_count",
                "validator_coerced_field_count",
                "validator_transformed_field_count",
                "provenance_dropped_row_count",
                "provenance_unresolved_drop_count",
                "custom_provenance_unavailable_count",
            ):
                value = attributes.get(key)
                if isinstance(value, int):
                    if key == "custom_provenance_unavailable_count":
                        summary[key] = max(int(summary.get(key) or 0), value)
                    else:
                        summary[key] = value
            for key in (
                "provenance_reason_counts",
                "provenance_none_reason_counts",
                "provenance_dropped_row_reason_counts",
            ):
                value = attributes.get(key)
                if isinstance(value, dict):
                    summary[f"{key}_json"] = {
                        str(reason): int(count) for reason, count in value.items() if isinstance(count, int | float)
                    }

        if stage == "table_resolution":
            selector = attributes.get("selector")
            table_id = _table_id_from_selector(selector)
            fallback_id = attributes.get("fallback_id")
            commented_id = attributes.get("table_id")
            for candidate in (table_id, fallback_id, commented_id):
                if isinstance(candidate, str) and candidate not in candidate_table_ids:
                    candidate_table_ids.append(candidate)
            if attributes.get("matched") is True:
                if isinstance(table_id, str):
                    selected_table_id = table_id
                elif isinstance(fallback_id, str):
                    selected_table_id = fallback_id
                elif isinstance(commented_id, str):
                    selected_table_id = commented_id

        if stage == "runner" and event_name == "row_model_pipeline_start":
            row_model = attributes.get("row_model")
            if isinstance(row_model, str):
                model_name = row_model

        if stage == "validation" and event_name == "pydantic_validation_complete":
            validation_status = str(attributes.get("validation_status") or "passed")
            explicit_error_count = attributes.get("validation_error_count")
            validation_error_count = explicit_error_count if isinstance(explicit_error_count, int) else 0
            explicit_paths = attributes.get("validation_error_paths")
            if isinstance(explicit_paths, list):
                summary["validation_error_paths_json"] = [str(path) for path in explicit_paths]
            else:
                summary["validation_error_paths_json"] = []

        if stage == "validation" and event_name == "pydantic_validation_failed":
            validation_status = str(attributes.get("validation_status") or "failed")
            explicit_error_count = attributes.get("validation_error_count")
            if isinstance(explicit_error_count, int):
                validation_error_count = explicit_error_count
            explicit_paths = attributes.get("validation_error_paths")
            if isinstance(explicit_paths, list):
                summary["validation_error_paths_json"] = [str(path) for path in explicit_paths]
            else:
                errors = attributes.get("errors")
                if isinstance(errors, list):
                    validation_error_count = len(errors) if validation_error_count is None else validation_error_count
                    summary["validation_error_paths_json"] = _validation_error_paths(errors)

        if stage == "diagnostics" and event_name == "rows_observed":
            observed_name = attributes.get("name")
            column_count_value = attributes.get("column_count")
            if observed_name == "result_data" and isinstance(column_count_value, int):
                output_field_count = column_count_value

        if event_name == "exception":
            failed_stage = stage or failed_stage
            stacktrace = attributes.get("exception.stacktrace")
            if isinstance(stacktrace, str):
                traceback_text = stacktrace

    endpoint = ENDPOINTS.get(endpoint_name) if endpoint_name is not None else None
    if endpoint is not None:
        summary["endpoint_group"] = _ENDPOINT_GROUPS.get(endpoint_name)
        summary["endpoint_kind"] = "custom" if endpoint.custom else "generic"
        summary["required_params_json"] = list(endpoint.params)
        summary["url_template"] = endpoint.path
        if model_name is None and endpoint.row_model is not None:
            model_name = endpoint.row_model.__name__
        if endpoint.row_model is not None:
            validated_fields = sorted(endpoint.row_model.model_fields)
            summary["validated_fields_json"] = validated_fields
        elif validation_status is None:
            validation_status = "not_run"
    elif validation_status is None:
        validation_status = "unknown"

    if validation_status is None and endpoint is not None and endpoint.row_model is not None:
        validation_status = "unknown"

    if isinstance(data, list) and data:
        first_item = data[0]
        if isinstance(first_item, dict):
            output_fields = _field_names_from_row(first_item)
            if output_field_count is None:
                output_field_count = len(output_fields)
            preview = _preview_result(first_item)
            first_row_preview = preview[0]
            first_row_preview_truncated = preview[1]
            first_row_preview_field_count = preview[2]
            first_row_total_field_count = preview[3]
        elif hasattr(first_item, "model_dump"):
            dumped = first_item.model_dump()
            if isinstance(dumped, dict):
                output_fields = _field_names_from_row(dumped)
                if output_field_count is None:
                    output_field_count = len(output_fields)
                preview = _preview_result(dumped)
                first_row_preview = preview[0]
                first_row_preview_truncated = preview[1]
                first_row_preview_field_count = preview[2]
                first_row_total_field_count = preview[3]
            else:
                first_row_preview = first_item
        else:
            first_row_preview = first_item

    if not output_fields and summary.get("validated_fields_json"):
        output_fields = list(summary["validated_fields_json"])
        if output_field_count is None:
            output_field_count = len(output_fields)

    if output_type is None:
        output_type = _infer_output_type(data, model_name)

    row_count_summary = _summarize_row_counts(
        events,
        output_row_count=output_row_count,
        raw_table_row_count=raw_table_row_count,
    )
    rounded_rate_limit_wait_ms = round(rate_limit_wait_ms, 3) if rate_limit_wait_ms else None
    metrics = _summarize_metrics(
        debug,
        duration_ms=summary["duration_ms"],
        response_bytes=response_bytes,
        rate_limit_wait_ms=rounded_rate_limit_wait_ms,
    )

    raw_column_count = raw_table_column_count if raw_table_column_count is not None else (len(raw_columns) or None)
    parsed_field_count = len(parsed_fields) if parsed_fields else raw_column_count
    validated_field_count = len(summary["validated_fields_json"]) if summary["validated_fields_json"] else None

    deprecated_columns = raw_columns or output_fields
    deprecated_column_count = output_field_count

    if selected_table_id is None:
        table_from_custom = custom_diagnostics.get("selected_table_id")
        if isinstance(table_from_custom, str):
            selected_table_id = table_from_custom
    if not candidate_table_ids:
        custom_candidates = custom_diagnostics.get("candidate_table_ids")
        if isinstance(custom_candidates, list):
            candidate_table_ids = [str(item) for item in custom_candidates]

    summary.update(
        {
            "metrics": metrics,
            "http_status_code": http_status_code,
            "http_reason": http_reason,
            "resolved_url": resolved_url,
            "content_type": content_type,
            "response_bytes": response_bytes,
            "redirect_count": redirect_count,
            "rate_limit_wait_ms": rounded_rate_limit_wait_ms,
            "failed_stage": failed_stage,
            "last_event": last_event,
            "last_successful_stage": last_successful_stage,
            "selected_table_id": selected_table_id,
            "candidate_table_ids_json": candidate_table_ids,
            "raw_table_row_count": raw_table_row_count,
            "raw_table_column_count": raw_table_column_count,
            "parser_name": parser_name,
            "model_name": model_name,
            "validation_status": validation_status,
            "validation_error_count": validation_error_count,
            "output_type": output_type,
            "raw_column_count": raw_column_count,
            "raw_columns_json": raw_columns,
            "parsed_field_count": parsed_field_count,
            "parsed_fields_json": parsed_fields,
            "validated_field_count": validated_field_count,
            "output_field_count": output_field_count,
            "output_fields_json": output_fields,
            "source_sections_json": source_sections,
            "parsed_event_count": parsed_event_count,
            "ignored_event_count": ignored_event_count,
            "period_count": period_count,
            "score_event_count": score_event_count,
            "substitution_event_count": substitution_event_count,
            "custom_diagnostics_json": custom_diagnostics,
            "column_count": deprecated_column_count,
            "columns_json": deprecated_columns,
            "first_row_preview_json": first_row_preview,
            "first_row_preview_truncated": first_row_preview_truncated,
            "first_row_preview_field_count": first_row_preview_field_count,
            "first_row_total_field_count": first_row_total_field_count,
            "trace_log_path": trace_log_path,
            "traceback_tail": _traceback_tail(traceback_text),
            "traceback_hash": _traceback_hash(traceback_text),
            **row_count_summary,
        }
    )
    return summary
