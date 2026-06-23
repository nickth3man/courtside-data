"""Live endpoint probe: call each registry endpoint once and record outcomes.

Uses fixture-manifest sample params (one case per endpoint) and the standard
``debug=True`` path so every call writes a full trace envelope to the debug
log directory. Emits a summary report JSON, and optionally a CSV report,
alongside those per-call traces.

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
from typing import Any, TypedDict

import orjson
from tests.fixture_manifest import ALL_CASES

from courtside_data.client._runner import _run_endpoint
from courtside_data.debug import DebugTrace
from courtside_data.debug.sink import resolve_log_dir
from courtside_data.endpoints import ENDPOINTS
from courtside_data.endpoints._custom import CUSTOM_ENDPOINTS
from courtside_data.endpoints._draft_awards_leaders import DRAFT_AWARDS_LEADERS_ENDPOINTS
from courtside_data.endpoints._league import LEAGUE_ENDPOINTS
from courtside_data.endpoints._players import PLAYER_ENDPOINTS
from courtside_data.endpoints._playoffs import PLAYOFF_ENDPOINTS
from courtside_data.endpoints._teams import TEAM_ENDPOINTS
from courtside_data.errors import RateLimitJailed, SchemaDriftError

FAILURE_NONE = "none"
FAILURE_MISSING_SAMPLE_PARAMS = "missing_sample_params"
FAILURE_RATE_LIMITED = "rate_limited"
FAILURE_HTTP_ERROR = "http_error"
FAILURE_TIMEOUT = "timeout"
FAILURE_SCHEMA_VALIDATION = "schema_validation"
FAILURE_PARSE_ERROR = "parse_error"
FAILURE_EMPTY_RESULT = "empty_result"
FAILURE_UNEXPECTED_EXCEPTION = "unexpected_exception"

MISSING_SAMPLE_PARAMS_ERROR = "MissingSampleParams"

_PREVIEW_MAX_KEYS = 8
_PREVIEW_MAX_STR_LEN = 80
_TRACEBACK_TAIL_LINES = 20

CSV_COLUMNS: tuple[str, ...] = (
    "endpoint",
    "params_json",
    "ok",
    "works",
    "evaluation",
    "failure_category",
    "error_type",
    "error_message",
    "status_code",
    "debug_status",
    "http_status_code",
    "http_reason",
    "resolved_url",
    "content_type",
    "response_bytes",
    "redirect_count",
    "rate_limit_wait_ms",
    "endpoint_group",
    "endpoint_kind",
    "sample_case_id",
    "sample_params_source",
    "required_params_json",
    "url_template",
    "failed_stage",
    "last_event",
    "last_successful_stage",
    "event_count",
    "warning_count",
    "error_event_count",
    "selected_table_id",
    "candidate_table_ids_json",
    "raw_table_row_count",
    "raw_table_column_count",
    "parser_name",
    "model_name",
    "validation_error_count",
    "validation_error_paths_json",
    "output_type",
    "column_count",
    "columns_json",
    "first_row_preview_json",
    "row_count",
    "duration_ms",
    "elapsed_ms",
    "trace_id",
    "trace_log_path",
    "trace_log_exists",
    "trace_log_size_bytes",
    "traceback_tail",
    "traceback_hash",
    "stage_counts_json",
    "metrics_json",
)

_DOMAIN_HTTP_ERROR_TYPES = {
    "InvalidDate",
    "InvalidPlayer",
    "InvalidPlayerAndSeason",
    "InvalidSeason",
    "InvalidTeam",
}
_EMPTY_RESULT_ERROR_TYPES = {"InvalidSearch"}
_HTTP_ERROR_TOKENS = (
    "connecterror",
    "decodingerror",
    "httperror",
    "httpstatuserror",
    "networkerror",
    "protocolerror",
    "proxyerror",
    "readerror",
    "remoteprotocolerror",
    "requesterror",
    "status code",
    "status error",
    "writeerror",
)
_PARSE_ERROR_TOKENS = (
    "parse",
    "parser",
    "selector",
    "table",
    "xpath",
    "xmlsyntax",
    "missingplayerslug",
)
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
    status_code: str | None
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
    validation_error_count: int | None
    validation_error_paths_json: list[str]
    output_type: str | None
    column_count: int | None
    columns_json: list[str]
    first_row_preview_json: Any
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
    """Pick the first manifest case for each endpoint (stable sort by case id)."""
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


def _preview_row(row: Any) -> Any:
    if not isinstance(row, dict):
        return row
    preview: dict[str, Any] = {}
    for index, (key, value) in enumerate(sorted(row.items())):
        if index >= _PREVIEW_MAX_KEYS:
            break
        if isinstance(value, str) and len(value) > _PREVIEW_MAX_STR_LEN:
            preview[key] = f"{value[:_PREVIEW_MAX_STR_LEN]}..."
        else:
            preview[key] = value
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
    status = debug.get("status") if isinstance(debug.get("status"), dict) else {}
    metrics = debug.get("metrics") if isinstance(debug.get("metrics"), dict) else {}
    stage_counts = debug.get("stage_counts") if isinstance(debug.get("stage_counts"), dict) else {}

    summary: dict[str, Any] = {
        "duration_ms": debug.get("duration_ms"),
        "status_code": status.get("code"),
        "debug_status": status.get("code"),
        "error_type": status.get("error_type"),
        "error_message": status.get("error_message"),
        "row_count": _row_count(data),
        "metrics": dict(metrics),
        "stage_counts": dict(stage_counts),
        "trace_id": debug.get("trace_id"),
        "event_count": len(events),
        "warning_count": 0,
        "error_event_count": 0,
        "candidate_table_ids_json": [],
        "validation_error_paths_json": [],
        "columns_json": [],
        "first_row_preview_json": None,
        "trace_log_exists": False,
        "trace_log_size_bytes": None,
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
    parser_name: str | None = None
    model_name: str | None = None
    validation_error_count: int | None = None
    output_type: str | None = None
    column_count: int | None = None
    columns: list[str] = []
    first_row_preview: Any = None
    traceback_text: str | None = None

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

        if stage == "parse" and event_name == "generic_table_parsed":
            parser_name = "generic_table"
            row_count_value = attributes.get("row_count")
            if isinstance(row_count_value, int):
                raw_table_row_count = row_count_value
            column_names = attributes.get("column_names")
            if isinstance(column_names, list):
                raw_table_column_count = len(column_names)
                columns = [str(name) for name in column_names]

        if stage == "parse" and event_name == "friv_playoff_outcomes_parsed":
            parser_name = "friv_playoff_outcomes"
            table_id = attributes.get("table_id")
            if isinstance(table_id, str):
                selected_table_id = table_id

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

        if stage == "runner" and event_name == "execute_start":
            output_type_value = attributes.get("output_type")
            if output_type_value is not None:
                output_type = str(output_type_value)

        if stage == "runner" and event_name == "row_model_pipeline_start":
            row_model = attributes.get("row_model")
            if isinstance(row_model, str):
                model_name = row_model

        if stage == "validation" and event_name == "pydantic_validation_failed":
            errors = attributes.get("errors")
            if isinstance(errors, list):
                validation_error_count = len(errors)
                summary["validation_error_paths_json"] = _validation_error_paths(errors)

        if stage == "diagnostics" and event_name == "rows_observed" and attributes.get("name") == "result_data":
            column_count_value = attributes.get("column_count")
            if isinstance(column_count_value, int):
                column_count = column_count_value

        if event_name == "exception":
            failed_stage = stage or failed_stage
            stacktrace = attributes.get("exception.stacktrace")
            if isinstance(stacktrace, str):
                traceback_text = stacktrace

    if endpoint_name is not None and endpoint_name in ENDPOINTS:
        endpoint = ENDPOINTS[endpoint_name]
        summary["endpoint_group"] = _ENDPOINT_GROUPS.get(endpoint_name)
        summary["endpoint_kind"] = "custom" if endpoint.custom else "generic"
        summary["required_params_json"] = list(endpoint.params)
        summary["url_template"] = endpoint.path
        if model_name is None and endpoint.row_model is not None:
            model_name = endpoint.row_model.__name__

    if isinstance(data, list) and data:
        first_item = data[0]
        if isinstance(first_item, dict):
            if not columns:
                columns = sorted(first_item)
            if column_count is None:
                column_count = len(first_item)
            first_row_preview = _preview_row(first_item)
        else:
            first_row_preview = first_item
            if hasattr(first_item, "model_dump"):
                dumped = first_item.model_dump()
                if isinstance(dumped, dict):
                    if not columns:
                        columns = sorted(dumped)
                    if column_count is None:
                        column_count = len(dumped)
                    first_row_preview = _preview_row(dumped)

    if trace_log_path:
        trace_path = Path(trace_log_path)
        if trace_path.exists():
            summary["trace_log_exists"] = True
            summary["trace_log_size_bytes"] = trace_path.stat().st_size

    summary.update(
        {
            "http_status_code": http_status_code,
            "http_reason": http_reason,
            "resolved_url": resolved_url,
            "content_type": content_type,
            "response_bytes": response_bytes,
            "redirect_count": redirect_count,
            "rate_limit_wait_ms": round(rate_limit_wait_ms, 3) if rate_limit_wait_ms else None,
            "failed_stage": failed_stage,
            "last_event": last_event,
            "last_successful_stage": last_successful_stage,
            "selected_table_id": selected_table_id,
            "candidate_table_ids_json": candidate_table_ids,
            "raw_table_row_count": raw_table_row_count,
            "raw_table_column_count": raw_table_column_count,
            "parser_name": parser_name,
            "model_name": model_name,
            "validation_error_count": validation_error_count,
            "output_type": output_type,
            "column_count": column_count,
            "columns_json": columns,
            "first_row_preview_json": first_row_preview,
            "trace_log_path": trace_log_path,
            "traceback_tail": _traceback_tail(traceback_text),
            "traceback_hash": _traceback_hash(traceback_text),
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
        "columns_json": [],
        "trace_log_exists": False,
    }
    if endpoint and endpoint.row_model is not None:
        enrichment["model_name"] = endpoint.row_model.__name__
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


def _json_cell(value: Any) -> str:
    return orjson.dumps(value, option=orjson.OPT_SORT_KEYS, default=str).decode("utf-8")


def _string_cell(value: Any) -> str:
    return "" if value is None else str(value)


def _bool_cell(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return _string_cell(value)


def _failure_detail(entry: Mapping[str, Any]) -> str:
    error_type = _string_cell(entry.get("error_type"))
    error_message = _string_cell(entry.get("error_message"))
    if error_type and error_message:
        return f"{error_type}: {error_message}"
    if error_type:
        return error_type
    if error_message:
        return error_message
    debug_status = _string_cell(entry.get("debug_status") or entry.get("status_code"))
    if debug_status:
        return f"status {debug_status}"
    http_status = entry.get("http_status_code")
    if http_status is not None:
        return f"HTTP {http_status}"
    return "no error detail reported"


def _has_token(*, error_type: str, error_message: str, tokens: Sequence[str]) -> bool:
    haystack = f"{error_type} {error_message}".lower()
    return any(token in haystack for token in tokens)


def _works(entry: Mapping[str, Any]) -> bool:
    debug_status = entry.get("debug_status", entry.get("status_code"))
    return entry.get("ok") is True and debug_status == "ok" and not entry.get("error_type")


def _failure_category(entry: Mapping[str, Any], *, works: bool) -> str:
    if works:
        return FAILURE_NONE

    error_type = _string_cell(entry.get("error_type"))
    error_message = _string_cell(entry.get("error_message"))
    debug_status = _string_cell(entry.get("debug_status") or entry.get("status_code"))
    failed_stage = _string_cell(entry.get("failed_stage"))
    http_status_code = entry.get("http_status_code")

    if error_type == MISSING_SAMPLE_PARAMS_ERROR:
        return FAILURE_MISSING_SAMPLE_PARAMS
    if error_type == RateLimitJailed.__name__:
        return FAILURE_RATE_LIMITED
    if error_type in _EMPTY_RESULT_ERROR_TYPES:
        return FAILURE_EMPTY_RESULT
    if _has_token(error_type=error_type, error_message=error_message, tokens=("timeout", "timed out")):
        return FAILURE_TIMEOUT
    if (
        error_type in _DOMAIN_HTTP_ERROR_TYPES
        or failed_stage == "http"
        or (isinstance(http_status_code, int) and http_status_code >= 400)
        or _has_token(error_type=error_type, error_message=error_message, tokens=_HTTP_ERROR_TOKENS)
    ):
        return FAILURE_HTTP_ERROR
    if (
        error_type == SchemaDriftError.__name__
        or failed_stage == "validation"
        or entry.get("validation_error_count")
        or _has_token(
            error_type=error_type,
            error_message=error_message,
            tokens=("validation", "schema drift", "pydantic"),
        )
    ):
        return FAILURE_SCHEMA_VALIDATION
    if (
        failed_stage in {"parse", "table_resolution"}
        or _has_token(error_type=error_type, error_message=error_message, tokens=_PARSE_ERROR_TOKENS)
    ):
        return FAILURE_PARSE_ERROR
    if entry.get("row_count") == 0 and debug_status and debug_status != "ok":
        return FAILURE_EMPTY_RESULT
    return FAILURE_UNEXPECTED_EXCEPTION


def _evaluation_sentence(entry: Mapping[str, Any], *, works: bool, failure_category: str) -> str:
    row_count = entry.get("row_count")
    if works:
        parts = ["Endpoint completed successfully"]
        if isinstance(entry.get("http_status_code"), int):
            http_part = f"HTTP {entry['http_status_code']}"
            if entry.get("http_reason"):
                http_part = f"{http_part} {entry['http_reason']}"
            parts.append(http_part)
        if entry.get("resolved_url"):
            parts.append(f"url={entry['resolved_url']}")
        if entry.get("parser_name"):
            parts.append(f"parser={entry['parser_name']}")
        if entry.get("selected_table_id"):
            parts.append(f"table={entry['selected_table_id']}")
        if isinstance(row_count, int):
            parts.append(f"rows={row_count}")
        elif row_count == 0:
            parts.append("rows=0")
        if entry.get("trace_log_exists"):
            parts.append("trace log written")
        return "; ".join(parts) + "."

    detail = _failure_detail(entry)
    if failure_category == FAILURE_MISSING_SAMPLE_PARAMS:
        source = entry.get("sample_params_source") or "missing"
        return f"No fixture-manifest sample params are available (source={source}), so the endpoint was not probed."
    if failure_category == FAILURE_RATE_LIMITED:
        return f"Endpoint hit Basketball-Reference rate-limit jail; probe stopped after this result. {detail}."
    if failure_category == FAILURE_HTTP_ERROR:
        stage = entry.get("failed_stage") or "http"
        http_status = entry.get("http_status_code")
        http_reason = entry.get("http_reason")
        http_summary = f"HTTP {http_status}" if isinstance(http_status, int) else "HTTP error"
        if isinstance(http_reason, str) and http_reason:
            http_summary = f"{http_summary} {http_reason}"
        return f"Endpoint failed during {stage}. {http_summary}. {detail}."
    if failure_category == FAILURE_TIMEOUT:
        return f"Endpoint timed out before it could complete. {detail}."
    if failure_category == FAILURE_SCHEMA_VALIDATION:
        paths = entry.get("validation_error_paths_json") or []
        path_summary = f" paths={paths[:5]}" if paths else ""
        return f"Endpoint failed schema validation.{path_summary} {detail}."
    if failure_category == FAILURE_PARSE_ERROR:
        table_summary = ""
        if entry.get("selected_table_id"):
            table_summary = f" selected_table={entry['selected_table_id']}"
        elif entry.get("candidate_table_ids_json"):
            table_summary = f" candidates={entry['candidate_table_ids_json']}"
        return f"Endpoint failed while parsing or resolving Basketball-Reference tables.{table_summary} {detail}."
    if failure_category == FAILURE_EMPTY_RESULT:
        return f"Endpoint failed because the requested live result was empty or invalid. {detail}."
    stage = entry.get("failed_stage")
    if stage:
        return f"Endpoint failed at stage {stage}. {detail}."
    return f"Endpoint failed with an unexpected exception. {detail}."


def _with_evaluation(entry: Mapping[str, Any]) -> dict[str, Any]:
    evaluated = dict(entry)
    if evaluated.get("debug_status") is None and evaluated.get("status_code") is not None:
        evaluated["debug_status"] = evaluated["status_code"]
    works = _works(evaluated)
    failure_category = _failure_category(evaluated, works=works)
    evaluated["works"] = works
    evaluated["failure_category"] = failure_category
    evaluated["evaluation"] = _evaluation_sentence(evaluated, works=works, failure_category=failure_category)
    return evaluated


def _csv_row(entry: Mapping[str, Any]) -> dict[str, str]:
    evaluated = _with_evaluation(entry)
    json_field_map = {
        "params_json": "params",
        "stage_counts_json": "stage_counts",
        "metrics_json": "metrics",
        "required_params_json": "required_params_json",
        "candidate_table_ids_json": "candidate_table_ids_json",
        "validation_error_paths_json": "validation_error_paths_json",
        "columns_json": "columns_json",
        "first_row_preview_json": "first_row_preview_json",
    }
    bool_fields = {"ok", "works", "trace_log_exists"}
    row: dict[str, str] = {}
    for column in CSV_COLUMNS:
        if column in json_field_map:
            source_key = json_field_map[column]
            value = evaluated.get(source_key)
            if value is None:
                value = {} if source_key in {"stage_counts", "metrics"} else []
            row[column] = _json_cell(value)
        elif column in bool_fields:
            row[column] = _bool_cell(evaluated.get(column))
        else:
            row[column] = _string_cell(evaluated.get(column))
    return row


class _StreamingCsvWriter:
    """Write probe CSV rows incrementally so partial runs survive interruption."""

    def __init__(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = output_path.open("w", encoding="utf-8", newline="")
        self._writer = csv.DictWriter(self._file, fieldnames=CSV_COLUMNS)
        self._writer.writeheader()
        self._file.flush()

    def write_row(self, entry: Mapping[str, Any]) -> None:
        self._writer.writerow(_csv_row(entry))
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def write_probe_csv_report(results: Sequence[Mapping[str, Any]], output_path: Path) -> None:
    """Write evaluated probe results to CSV."""
    writer = _StreamingCsvWriter(output_path)
    try:
        for result in results:
            writer.write_row(result)
    finally:
        writer.close()


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

    DebugTrace.__init__ = capturing_init  # type: ignore[method-assign]
    return original_init, captured


def _restore_debug_trace_init(original_init: Any) -> None:
    DebugTrace.__init__ = original_init  # type: ignore[method-assign]


def probe_endpoints(
    *,
    endpoints: list[str] | None = None,
    output_path: Path | None = None,
    csv_output_path: Path | None = None,
) -> dict[str, Any]:
    """Run one live call per endpoint and return the summary report dict."""
    endpoint_names = _resolve_endpoint_names(endpoints)
    params_by_endpoint = _sample_params_per_endpoint()
    missing = sorted(set(endpoint_names) - set(params_by_endpoint))
    started_at = datetime.now(tz=UTC)
    results: list[dict[str, Any]] = []
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
        "total_endpoints": len(endpoint_names),
        "probed_endpoints": len(results),
        "requested_endpoints": endpoint_names,
        "ok_count": ok_count,
        "failed_count": len(results) - ok_count,
        "missing_sample_params": missing,
        "failed_endpoints": failed,
        "ok_endpoints": [item["endpoint"] for item in results if item.get("ok")],
        "debug_log_dir": str(resolve_log_dir()),
        "results": results,
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = probe_endpoints(endpoints=args.endpoints, output_path=args.output, csv_output_path=args.csv_output)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    summary_keys = ("report_path", "csv_report_path", "ok_count", "failed_count", "failed_endpoints")
    summary = {key: report[key] for key in summary_keys if key in report}
    print(orjson.dumps(summary, option=orjson.OPT_INDENT_2).decode("utf-8"))
    return 0 if report["failed_count"] == 0 and not report["missing_sample_params"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
