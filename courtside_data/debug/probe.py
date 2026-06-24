"""Live endpoint probe: call each registry endpoint once and record outcomes.

Sample params prefer explicit recent "live audit" overrides (see
courtside_data.debug.live_probe_cases) when present; otherwise fall back to
the first case from ``tests.fixture_manifest.ALL_CASES``. The
``debug=True`` path ensures every call writes a full trace envelope.
Emits a summary report JSON (with ``sample_params_source`` distinguishing
"live_audit" vs "fixture_manifest"), and optionally a CSV report.

Usage::

    uv run python -m courtside_data.debug.probe
    uv run python -m courtside_data.debug.probe --output logs/my_report.json
    uv run python -m courtside_data.debug.probe -e play_by_play -e team_roster
    uv run python -m courtside_data.debug.probe --endpoint friv_7_game_playoff_series_outcomes_team_is_tied
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict, cast

import orjson
from tests.fixture_manifest import ALL_CASES

from courtside_data.client._runner import _run_endpoint
from courtside_data.debug import DebugTrace
from courtside_data.debug.live_probe_cases import (
    LIVE_AUDIT_SOURCE,
    get_live_audit_sample,
)
from courtside_data.debug.probe_report import (
    _DOMAIN_HTTP_ERROR_TYPES,
    _EMPTY_RESULT_ERROR_TYPES,
    _HTTP_ERROR_TOKENS,
    _PARSE_ERROR_TOKENS,
    CSV_COLUMNS,
    FAILURE_EMPTY_RESULT,
    FAILURE_HTTP_ERROR,
    FAILURE_MISSING_SAMPLE_PARAMS,
    FAILURE_NONE,
    FAILURE_PARSE_ERROR,
    FAILURE_RATE_LIMITED,
    FAILURE_SCHEMA_VALIDATION,
    FAILURE_TIMEOUT,
    FAILURE_UNEXPECTED_EXCEPTION,
    MISSING_SAMPLE_PARAMS_ERROR,
    _bool_cell,
    _csv_row,
    _evaluation_sentence,
    _failure_category,
    _failure_detail,
    _has_token,
    _json_cell,
    _StreamingCsvWriter,
    _string_cell,
    _with_evaluation,
    _works,
    write_probe_csv_report,
)
from courtside_data.debug.sink import resolve_log_dir
from courtside_data.endpoints import ENDPOINTS
from courtside_data.endpoints._custom import CUSTOM_ENDPOINTS
from courtside_data.endpoints._draft_awards_leaders import DRAFT_AWARDS_LEADERS_ENDPOINTS
from courtside_data.endpoints._league import LEAGUE_ENDPOINTS
from courtside_data.endpoints._players import PLAYER_ENDPOINTS
from courtside_data.endpoints._playoffs import PLAYOFF_ENDPOINTS
from courtside_data.endpoints._teams import TEAM_ENDPOINTS
from courtside_data.errors import RateLimitJailed

_PREVIEW_MAX_KEYS = 8
_PREVIEW_MAX_STR_LEN = 80
_PREVIEW_MAX_NESTED_DEPTH = 2
_TRACEBACK_TAIL_LINES = 20

_HTTP_RESPONSE_EVENTS = frozenset({"attempt_response", "status_error", "request_complete"})


class ProbeResult(TypedDict, total=False):
    """Structured probe result fields stored in JSON report rows."""

    endpoint: str
    params: dict[str, Any] | None
    ok: bool
    works: bool
    evaluation: str
    failure_category: str
    error_type: str | None
    error_message: str | None
    status_code: str | None  # deprecated alias for debug_status
    debug_status: str | None
    http_status_code: int | None
    http_reason: str | None
    resolved_url: str | None
    content_type: str | None
    response_bytes: int | None
    redirect_count: int | None
    rate_limit_wait_ms: float | None
    endpoint_group: str | None
    endpoint_kind: str | None
    sample_case_id: str | None
    sample_params_source: str | None
    required_params_json: list[str] | None
    url_template: str | None
    failed_stage: str | None
    last_event: str | None
    last_successful_stage: str | None
    event_count: int
    warning_count: int
    error_event_count: int
    selected_table_id: str | None
    candidate_table_ids_json: list[str]
    raw_table_row_count: int | None
    raw_table_column_count: int | None
    parser_name: str | None
    model_name: str | None
    validation_status: str | None
    validation_error_count: int | None
    validation_error_paths_json: list[str]
    output_type: str | None
    raw_column_count: int | None
    raw_columns_json: list[str]
    parsed_field_count: int | None
    parsed_fields_json: list[str]
    validated_field_count: int | None
    validated_fields_json: list[str]
    output_field_count: int | None
    output_fields_json: list[str]
    raw_row_count: int | None
    parsed_row_count: int | None
    validated_row_count: int | None
    output_row_count: int | None
    dropped_row_count: int | None
    dropped_row_reason_counts_json: dict[str, int]
    data_quality_status: str | None
    data_quality_warnings_json: list[str]
    drop_rate: float | None
    drop_rate_warning: bool | None
    expected_drop_count: int | None
    unexpected_drop_count: int | None
    provenance_field_count: int | None
    provenance_final_none_count: int | None
    provenance_reason_counts_json: dict[str, int]
    provenance_none_reason_counts_json: dict[str, int]
    parser_missed_column_count: int | None
    schema_defaulted_field_count: int | None
    validator_coerced_field_count: int | None
    validator_transformed_field_count: int | None
    provenance_dropped_row_count: int | None
    provenance_dropped_row_reason_counts_json: dict[str, int]
    provenance_unresolved_drop_count: int | None
    custom_provenance_unavailable_count: int | None
    trace_truncated_artifact_count: int | None
    source_sections_json: list[str]
    parsed_event_count: int | None
    ignored_event_count: int | None
    ignored_event_reason_counts_json: dict[str, int]
    period_count: int | None
    score_event_count: int | None
    substitution_event_count: int | None
    custom_diagnostics_json: dict[str, Any]
    column_count: int | None  # deprecated; prefer output_field_count
    columns_json: list[str]  # deprecated; prefer raw_columns_json / output_fields_json
    first_row_preview_json: Any
    first_row_preview_truncated: bool | None
    first_row_preview_field_count: int | None
    first_row_total_field_count: int | None
    row_count: int | None
    duration_ms: float | None
    elapsed_ms: float | None
    trace_id: str | None
    trace_log_path: str | None
    trace_log_exists: bool
    trace_log_size_bytes: int | None
    traceback_tail: str | None
    traceback_hash: str | None
    stage_counts: dict[str, int]
    metrics: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SampleParamsInfo:
    """Fixture-manifest sample params metadata for one endpoint."""

    params: dict[str, Any]
    case_id: str | None
    source: str


def _endpoint_group_map() -> dict[str, str]:
    groups: dict[str, str] = {}
    for group_name, mapping in (
        ("league", LEAGUE_ENDPOINTS),
        ("playoffs", PLAYOFF_ENDPOINTS),
        ("draft_awards_leaders", DRAFT_AWARDS_LEADERS_ENDPOINTS),
        ("players", PLAYER_ENDPOINTS),
        ("teams", TEAM_ENDPOINTS),
        ("custom", CUSTOM_ENDPOINTS),
    ):
        for endpoint_name in mapping:
            groups[endpoint_name] = group_name
    return groups


_ENDPOINT_GROUPS = _endpoint_group_map()


def _sample_params_per_endpoint() -> dict[str, SampleParamsInfo]:
    """Build sample params for the live probe.

    Base set comes from the first sorted case in ``tests.fixture_manifest.ALL_CASES``
    (for backward compatibility and to cover every registered endpoint).

    Live-audit overrides (recent dense seasons) are applied on top for
    selected endpoints so that probe reports reflect modern tables instead
    of old historical fixtures that produce many expected nulls/drops.
    """
    params_by_endpoint: dict[str, SampleParamsInfo] = {}
    for case in sorted(ALL_CASES, key=lambda item: item.id):
        if case.endpoint_name not in params_by_endpoint:
            params_by_endpoint[case.endpoint_name] = SampleParamsInfo(
                params=dict(case.params),
                case_id=case.id,
                source="fixture_manifest",
            )
    for name, endpoint in ENDPOINTS.items():
        if name not in params_by_endpoint and not endpoint.params:
            params_by_endpoint[name] = SampleParamsInfo(params={}, case_id=None, source="empty_default")

    # Overlay explicit live-audit samples (preferred for the probe).
    # These do not affect ALL_CASES or any offline regression tests.
    for name in ENDPOINTS:
        live = get_live_audit_sample(name)
        if live is not None:
            params_by_endpoint[name] = SampleParamsInfo(
                params=dict(live),
                case_id=f"live_audit:{name}",
                source=LIVE_AUDIT_SOURCE,
            )

    return params_by_endpoint


def _row_count(data: Any) -> int | None:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            return len(data["data"])
        return len(data)
    return None


def _event_attributes(event: Mapping[str, Any]) -> dict[str, Any]:
    attributes = event.get("attributes")
    return dict(attributes) if isinstance(attributes, dict) else {}


def _event_label(event: Mapping[str, Any]) -> str:
    stage = event.get("stage")
    name = event.get("event")
    return f"{stage}/{name}" if stage and name else str(name or stage or "")


def _content_type_from_headers(headers: Any) -> str | None:
    if not isinstance(headers, dict):
        return None
    for key, value in headers.items():
        if str(key).lower() == "content-type":
            return str(value)
    return None


def _truncate_preview_value(value: Any, *, depth: int = 0) -> tuple[Any, bool]:
    """Return a bounded preview fragment and whether truncation occurred."""
    truncated = False
    if isinstance(value, str):
        if len(value) > _PREVIEW_MAX_STR_LEN:
            return f"{value[:_PREVIEW_MAX_STR_LEN]}...", True
        return value, False
    if depth >= _PREVIEW_MAX_NESTED_DEPTH:
        if isinstance(value, (dict, list, tuple)):
            return "...", True
        return value, False
    if isinstance(value, dict):
        preview: dict[str, Any] = {}
        for index, (key, nested) in enumerate(sorted(value.items())):
            if index >= _PREVIEW_MAX_KEYS:
                truncated = True
                break
            nested_preview, nested_truncated = _truncate_preview_value(nested, depth=depth + 1)
            preview[str(key)] = nested_preview
            truncated = truncated or nested_truncated
        return preview, truncated
    if isinstance(value, list):
        items: list[Any] = []
        for index, item in enumerate(value):
            if index >= _PREVIEW_MAX_KEYS:
                truncated = True
                break
            nested_preview, nested_truncated = _truncate_preview_value(item, depth=depth + 1)
            items.append(nested_preview)
            truncated = truncated or nested_truncated
        return items, truncated
    return value, False


def _preview_result(row: Any) -> tuple[Any, bool, int | None, int | None]:
    """Build a deterministic first-row preview with truncation metadata."""
    if not isinstance(row, dict):
        return row, False, None, None
    total_field_count = len(row)
    preview: dict[str, Any] = {}
    truncated = total_field_count > _PREVIEW_MAX_KEYS
    for index, (key, value) in enumerate(sorted(row.items())):
        if index >= _PREVIEW_MAX_KEYS:
            break
        preview_value, value_truncated = _truncate_preview_value(value)
        preview[str(key)] = preview_value
        truncated = truncated or value_truncated
    return preview, truncated, len(preview), total_field_count


def _field_names_from_row(row: Any) -> list[str]:
    if isinstance(row, dict):
        return sorted(row)
    if hasattr(row, "model_dump"):
        dumped = row.model_dump()
        if isinstance(dumped, dict):
            return sorted(dumped)
    return []


def _infer_output_type(data: Any, model_name: str | None) -> str | None:
    if data is None:
        return None
    if isinstance(data, list):
        return f"list[{model_name}]" if model_name else "list"
    if isinstance(data, dict):
        return "dict"
    return type(data).__name__


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


def _slowest_stage_from_metrics(metrics: Mapping[str, Any]) -> str | None:
    stage_durations: list[tuple[str, float]] = []
    for key, value in metrics.items():
        if not key.startswith("duration_ms.") or key == "duration_ms.total":
            continue
        if isinstance(value, int | float):
            stage_durations.append((key.removeprefix("duration_ms."), float(value)))
    if not stage_durations:
        return None
    return max(stage_durations, key=lambda item: item[1])[0]


def _summarize_report(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate per-endpoint probe rows into report-level diagnostics."""
    rate_limit_waits: list[float] = []
    elapsed_by_endpoint: list[tuple[str, float]] = []
    trace_sizes: list[tuple[str, int]] = []
    provenance_reason_counts: dict[str, int] = {}
    provenance_none_reason_counts: dict[str, int] = {}
    provenance_dropped_reason_counts: dict[str, int] = {}

    for result in results:
        wait_ms = result.get("rate_limit_wait_ms")
        if isinstance(wait_ms, int | float):
            rate_limit_waits.append(float(wait_ms))
        endpoint = result.get("endpoint")
        elapsed = result.get("elapsed_ms")
        if isinstance(endpoint, str) and isinstance(elapsed, int | float):
            elapsed_by_endpoint.append((endpoint, float(elapsed)))
        trace_path = result.get("trace_log_path")
        trace_size = result.get("trace_log_size_bytes")
        if isinstance(trace_path, str) and isinstance(trace_size, int):
            trace_sizes.append((trace_path, trace_size))
        for source_key, aggregate in (
            ("provenance_reason_counts_json", provenance_reason_counts),
            ("provenance_none_reason_counts_json", provenance_none_reason_counts),
            ("provenance_dropped_row_reason_counts_json", provenance_dropped_reason_counts),
        ):
            counts = result.get(source_key)
            if isinstance(counts, dict):
                for key, value in counts.items():
                    if isinstance(value, int | float):
                        reason_key = str(key)
                        aggregate[reason_key] = aggregate.get(reason_key, 0) + int(value)

    summary: dict[str, Any] = {
        "total_rate_limit_wait_ms": round(sum(rate_limit_waits), 3) if rate_limit_waits else None,
        "average_rate_limit_wait_ms": round(sum(rate_limit_waits) / len(rate_limit_waits), 3)
        if rate_limit_waits
        else None,
        "max_rate_limit_wait_ms": round(max(rate_limit_waits), 3) if rate_limit_waits else None,
        "slowest_endpoint": None,
        "slowest_endpoint_elapsed_ms": None,
        "slowest_stage": None,
        "total_trace_log_size_bytes": sum(size for _, size in trace_sizes) if trace_sizes else None,
        "largest_trace_log_path": None,
        "largest_trace_log_size_bytes": None,
        "total_provenance_field_count": sum(
            int(result.get("provenance_field_count") or 0)
            for result in results
            if isinstance(result.get("provenance_field_count"), int)
        ),
        "total_provenance_final_none_count": sum(
            int(result.get("provenance_final_none_count") or 0)
            for result in results
            if isinstance(result.get("provenance_final_none_count"), int)
        ),
        "total_parser_missed_column_count": sum(
            int(result.get("parser_missed_column_count") or 0)
            for result in results
            if isinstance(result.get("parser_missed_column_count"), int)
        ),
        "total_provenance_unresolved_drop_count": sum(
            int(result.get("provenance_unresolved_drop_count") or 0)
            for result in results
            if isinstance(result.get("provenance_unresolved_drop_count"), int)
        ),
        "provenance_reason_counts_json": provenance_reason_counts,
        "provenance_none_reason_counts_json": provenance_none_reason_counts,
        "provenance_dropped_row_reason_counts_json": provenance_dropped_reason_counts,
    }

    if elapsed_by_endpoint:
        slowest_endpoint, slowest_elapsed = max(elapsed_by_endpoint, key=lambda item: item[1])
        summary["slowest_endpoint"] = slowest_endpoint
        summary["slowest_endpoint_elapsed_ms"] = round(slowest_elapsed, 3)
        slowest_result = next(item for item in results if item.get("endpoint") == slowest_endpoint)
        metrics = slowest_result.get("metrics")
        if isinstance(metrics, dict):
            summary["slowest_stage"] = _slowest_stage_from_metrics(metrics)

    if trace_sizes:
        largest_path, largest_size = max(trace_sizes, key=lambda item: item[1])
        summary["largest_trace_log_path"] = largest_path
        summary["largest_trace_log_size_bytes"] = largest_size
        total_bytes = summary.get("total_trace_log_size_bytes")
        if isinstance(total_bytes, int):
            summary["total_trace_log_size_mb"] = round(total_bytes / (1024 * 1024), 3)

    truncated_counts = [
        int(result.get("trace_truncated_artifact_count") or 0)
        for result in results
        if isinstance(result.get("trace_truncated_artifact_count"), int)
    ]
    summary["total_trace_truncated_artifact_count"] = sum(truncated_counts) if truncated_counts else None

    completed = [item for item in results if item.get("ok")]
    if completed and len(completed) < len(results):
        avg_elapsed = sum(float(item.get("elapsed_ms") or 0) for item in completed) / len(completed)
        remaining = len(results) - len(completed)
        summary["estimated_remaining_runtime_ms"] = round(avg_elapsed * remaining, 3)

    return summary


def _preview_row(row: Any) -> Any:
    preview, _, _, _ = _preview_result(row if isinstance(row, dict) else {"value": row})
    return preview


def _validation_error_paths(errors: Any) -> list[str]:
    if not isinstance(errors, list):
        return []
    paths: list[str] = []
    for error in errors:
        if not isinstance(error, dict):
            continue
        location = error.get("loc")
        if isinstance(location, (list, tuple)):
            paths.append(".".join(str(part) for part in location))
        elif location is not None:
            paths.append(str(location))
    return paths


def _traceback_tail(stacktrace: str | None) -> str | None:
    if not stacktrace:
        return None
    lines = stacktrace.splitlines()
    if not lines:
        return None
    tail = lines[-_TRACEBACK_TAIL_LINES:]
    return "\n".join(tail)


def _traceback_hash(stacktrace: str | None) -> str | None:
    if not stacktrace:
        return None
    return hashlib.sha256(stacktrace.encode("utf-8")).hexdigest()[:16]


def _table_id_from_selector(selector: Any) -> str | None:
    if not isinstance(selector, str):
        return None
    prefix = "table[@id="
    if selector.startswith(prefix) and selector.endswith("]"):
        rendered = selector[len(prefix) : -1]
        return rendered.strip("'\"")
    return None


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


def _default_enrichment(*, endpoint_name: str, sample: SampleParamsInfo | None = None) -> dict[str, Any]:
    endpoint = ENDPOINTS.get(endpoint_name)
    enrichment: dict[str, Any] = {
        "endpoint_group": _ENDPOINT_GROUPS.get(endpoint_name),
        "endpoint_kind": "custom" if endpoint and endpoint.custom else "generic" if endpoint else None,
        "required_params_json": list(endpoint.params) if endpoint else [],
        "url_template": endpoint.path if endpoint else None,
        "sample_case_id": sample.case_id if sample else None,
        "sample_params_source": sample.source if sample else "missing",
        "event_count": 0,
        "warning_count": 0,
        "error_event_count": 0,
        "candidate_table_ids_json": [],
        "validation_error_paths_json": [],
        "raw_columns_json": [],
        "parsed_fields_json": [],
        "validated_fields_json": [],
        "output_fields_json": [],
        "columns_json": [],
        "dropped_row_reason_counts_json": {},
        "provenance_reason_counts_json": {},
        "provenance_none_reason_counts_json": {},
        "provenance_dropped_row_reason_counts_json": {},
        "source_sections_json": [],
        "ignored_event_reason_counts_json": {},
        "custom_diagnostics_json": {},
        "trace_log_exists": False,
        "validation_status": "not_run" if endpoint and endpoint.row_model is None else None,
    }
    if endpoint and endpoint.row_model is not None:
        enrichment["model_name"] = endpoint.row_model.__name__
        enrichment["validated_fields_json"] = sorted(endpoint.row_model.model_fields)
    return enrichment


def _extract_stats(envelope: Any, *, endpoint_name: str | None = None) -> dict[str, Any]:
    if not isinstance(envelope, dict) or "debug" not in envelope:
        return {}
    debug = envelope["debug"]
    if not isinstance(debug, dict):
        return {}
    trace_log_path = _find_trace_log_path(envelope)
    summary = _summarize_debug_events(
        debug,
        data=envelope.get("data"),
        endpoint_name=endpoint_name,
        trace_log_path=trace_log_path,
    )
    summary["trace_log_path"] = trace_log_path
    return summary


def _enrich_entry_from_trace(
    entry: dict[str, Any],
    trace: DebugTrace,
    *,
    data: Any = None,
) -> None:
    trace_log_path = None
    for event in trace.events:
        if event.get("event") == "trace_log":
            path = _event_attributes(event).get("path")
            if isinstance(path, str):
                trace_log_path = path
                break
    summary = _summarize_debug_events(
        trace.to_dict(),
        data=data,
        endpoint_name=entry.get("endpoint"),
        trace_log_path=trace_log_path,
    )
    summary["trace_log_path"] = trace_log_path
    entry.update(summary)


def _find_trace_log_path(envelope: Any) -> str | None:
    if not isinstance(envelope, dict):
        return None
    debug = envelope.get("debug")
    if not isinstance(debug, dict):
        return None
    for event in debug.get("events") or []:
        if not isinstance(event, dict):
            continue
        if event.get("event") == "trace_log":
            attributes = event.get("attributes") or {}
            path = attributes.get("path")
            if isinstance(path, str):
                return path
    return None


def _resolve_endpoint_names(names: list[str] | None) -> list[str]:
    """Validate and return sorted endpoint names to probe."""
    if not names:
        return sorted(ENDPOINTS)
    unknown = sorted(set(names) - set(ENDPOINTS))
    if unknown:
        known = ", ".join(sorted(ENDPOINTS))
        message = f"Unknown endpoint(s): {', '.join(unknown)}. Known endpoints: {known}"
        raise ValueError(message)
    return sorted(set(names))


def _capture_debug_traces() -> tuple[Any, list[DebugTrace]]:
    captured: list[DebugTrace] = []
    original_init = DebugTrace.__init__

    def capturing_init(self: DebugTrace, *args: Any, **kwargs: Any) -> None:
        original_init(self, *args, **kwargs)
        captured.append(self)

    DebugTrace.__init__ = cast(Any, capturing_init)
    return original_init, captured


def _restore_debug_trace_init(original_init: Any) -> None:
    DebugTrace.__init__ = original_init


def _load_resume_state(resume_path: Path | None) -> tuple[list[dict[str, Any]], set[str]]:
    """Load prior probe rows and the set of successfully probed endpoints."""
    if resume_path is None or not resume_path.exists():
        return [], set()
    if resume_path.suffix.lower() == ".csv":
        prior_rows = _read_csv_rows(resume_path)
        completed = {row["endpoint"] for row in prior_rows if row.get("ok") == "true" and row.get("endpoint")}
        return prior_rows, completed
    payload = orjson.loads(resume_path.read_bytes())
    prior_results = payload.get("results") if isinstance(payload, dict) else []
    if not isinstance(prior_results, list):
        return [], set()
    completed = {str(item["endpoint"]) for item in prior_results if isinstance(item, dict) and item.get("ok")}
    return prior_results, completed


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def probe_endpoints(
    *,
    endpoints: list[str] | None = None,
    output_path: Path | None = None,
    csv_output_path: Path | None = None,
    resume_from: Path | None = None,
    debug_detail_level: str | None = None,
    use_cache: bool | None = None,
    params_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run one live call per endpoint and return the summary report dict."""
    if debug_detail_level is not None:
        import os

        os.environ["COURTSIDE_DEBUG_DETAIL_LEVEL"] = debug_detail_level
    if use_cache is True:
        import os

        os.environ.setdefault("COURTSIDE_DATA_HTTP_CACHE", "1")

    endpoint_names = _resolve_endpoint_names(endpoints)
    if params_override is not None and len(endpoint_names) != 1:
        raise ValueError("--params-json can only be used when exactly one --endpoint is selected.")
    prior_results, completed_endpoints = _load_resume_state(resume_from)
    if completed_endpoints:
        endpoint_names = [name for name in endpoint_names if name not in completed_endpoints]
    params_by_endpoint = _sample_params_per_endpoint()
    if params_override is not None and endpoint_names:
        params_by_endpoint[endpoint_names[0]] = SampleParamsInfo(
            params=dict(params_override),
            case_id=f"params_override:{endpoint_names[0]}",
            source="params_override",
        )
    missing = sorted(set(endpoint_names) - set(params_by_endpoint))
    started_at = datetime.now(tz=UTC)
    results: list[dict[str, Any]] = list(prior_results)
    csv_writer: _StreamingCsvWriter | None = None

    if csv_output_path is not None:
        csv_writer = _StreamingCsvWriter(csv_output_path)

    original_init, captured_traces = _capture_debug_traces()
    try:
        for name in endpoint_names:
            captured_traces.clear()
            sample = params_by_endpoint.get(name)
            entry: dict[str, Any] = {
                "endpoint": name,
                "params": sample.params if sample else None,
                "ok": False,
            }
            entry.update(_default_enrichment(endpoint_name=name, sample=sample))

            if sample is None:
                entry["error_type"] = MISSING_SAMPLE_PARAMS_ERROR
                entry["error_message"] = "No fixture-manifest case available for this endpoint."
                entry["sample_params_source"] = "missing"
                evaluated = _with_evaluation(entry)
                results.append(evaluated)
                if csv_writer is not None:
                    csv_writer.write_row(evaluated)
                continue

            call_started = time.perf_counter()
            try:
                envelope = _run_endpoint(name, sample.params, debug=True)
                stats = _extract_stats(envelope, endpoint_name=name)
                entry.update(stats)
                entry["ok"] = stats.get("debug_status") == "ok"
                entry["elapsed_ms"] = round((time.perf_counter() - call_started) * 1000, 2)
            except RateLimitJailed as exc:
                entry["error_type"] = type(exc).__name__
                entry["error_message"] = str(exc)
                entry["elapsed_ms"] = round((time.perf_counter() - call_started) * 1000, 2)
                if captured_traces:
                    _enrich_entry_from_trace(entry, captured_traces[-1])
                evaluated = _with_evaluation(entry)
                results.append(evaluated)
                if csv_writer is not None:
                    csv_writer.write_row(evaluated)
                break
            except Exception as exc:
                entry["error_type"] = type(exc).__name__
                entry["error_message"] = str(exc)
                entry["elapsed_ms"] = round((time.perf_counter() - call_started) * 1000, 2)
                if captured_traces:
                    _enrich_entry_from_trace(entry, captured_traces[-1])
            else:
                if not entry.get("trace_log_path") and captured_traces:
                    _enrich_entry_from_trace(entry, captured_traces[-1], data=envelope.get("data"))

            evaluated = _with_evaluation(entry)
            results.append(evaluated)
            if csv_writer is not None:
                csv_writer.write_row(evaluated)
    finally:
        _restore_debug_trace_init(original_init)
        if csv_writer is not None:
            csv_writer.close()

    finished_at = datetime.now(tz=UTC)
    ok_count = sum(1 for item in results if item.get("ok"))
    failed = [item["endpoint"] for item in results if not item.get("ok")]
    report: dict[str, Any] = {
        "schema_version": 1,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "total_endpoints": len(_resolve_endpoint_names(endpoints)),
        "probed_endpoints": len(results),
        "requested_endpoints": _resolve_endpoint_names(endpoints),
        "resumed_from": str(resume_from) if resume_from else None,
        "skipped_completed_endpoints": sorted(completed_endpoints) if completed_endpoints else [],
        "ok_count": ok_count,
        "failed_count": len(results) - ok_count,
        "missing_sample_params": missing,
        "failed_endpoints": failed,
        "ok_endpoints": [item["endpoint"] for item in results if item.get("ok")],
        "debug_log_dir": str(resolve_log_dir()),
        "results": results,
        **_summarize_report(results),
    }

    if output_path is None:
        stamp = finished_at.strftime("%Y%m%d_%H%M%S")
        output_path = resolve_log_dir() / f"endpoint_probe_report_{stamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(orjson.dumps(report, option=orjson.OPT_INDENT_2, default=str))
    report["report_path"] = str(output_path)
    if csv_output_path is not None:
        report["csv_report_path"] = str(csv_output_path)
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe every courtside-data endpoint live and write a report.")
    parser.add_argument(
        "--endpoint",
        "-e",
        action="append",
        dest="endpoints",
        metavar="NAME",
        help="Probe only this endpoint (repeatable). Default: all registry endpoints.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Summary report path (default: <debug log dir>/endpoint_probe_report_<timestamp>.json)",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=None,
        help="Optional CSV report path. When omitted, only the JSON report is written.",
    )
    parser.add_argument(
        "--resume-from",
        type=Path,
        default=None,
        help="Resume a partial probe CSV/JSON report and skip endpoints already marked ok.",
    )
    parser.add_argument(
        "--debug-detail-level",
        choices=("summary", "normal", "full"),
        default=None,
        help="Trace artifact detail level (sets COURTSIDE_DEBUG_DETAIL_LEVEL).",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Enable hishel HTTP caching for repeated probe debugging runs.",
    )
    parser.add_argument(
        "--params-json",
        default=None,
        help="JSON object of endpoint params. Requires exactly one --endpoint and only affects this probe run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    params_override = None
    if args.params_json is not None:
        try:
            loaded = orjson.loads(args.params_json)
        except orjson.JSONDecodeError as exc:
            print(f"Invalid --params-json: {exc}", file=sys.stderr)
            return 2
        if not isinstance(loaded, dict):
            print("--params-json must decode to a JSON object.", file=sys.stderr)
            return 2
        params_override = dict(loaded)
    try:
        report = probe_endpoints(
            endpoints=args.endpoints,
            output_path=args.output,
            csv_output_path=args.csv_output,
            resume_from=args.resume_from,
            debug_detail_level=args.debug_detail_level,
            use_cache=args.use_cache,
            params_override=params_override,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    summary_keys = ("report_path", "csv_report_path", "ok_count", "failed_count", "failed_endpoints")
    summary = {key: report[key] for key in summary_keys if key in report}
    print(orjson.dumps(summary, option=orjson.OPT_INDENT_2).decode("utf-8"))
    return 0 if report["failed_count"] == 0 and not report["missing_sample_params"] else 1


__all__ = [
    "CSV_COLUMNS",
    "FAILURE_EMPTY_RESULT",
    "FAILURE_HTTP_ERROR",
    "FAILURE_MISSING_SAMPLE_PARAMS",
    "FAILURE_NONE",
    "FAILURE_PARSE_ERROR",
    "FAILURE_RATE_LIMITED",
    "FAILURE_SCHEMA_VALIDATION",
    "FAILURE_TIMEOUT",
    "FAILURE_UNEXPECTED_EXCEPTION",
    "MISSING_SAMPLE_PARAMS_ERROR",
    "_DOMAIN_HTTP_ERROR_TYPES",
    "_EMPTY_RESULT_ERROR_TYPES",
    "_HTTP_ERROR_TOKENS",
    "_PARSE_ERROR_TOKENS",
    "ProbeResult",
    "SampleParamsInfo",
    "_StreamingCsvWriter",
    "_bool_cell",
    "_csv_row",
    "_evaluation_sentence",
    "_failure_category",
    "_failure_detail",
    "_has_token",
    "_json_cell",
    "_string_cell",
    "_with_evaluation",
    "_works",
    "main",
    "probe_endpoints",
    "write_probe_csv_report",
]


if __name__ == "__main__":
    raise SystemExit(main())
