"""Probe result evaluation: ``works`` / ``failure_category`` / ``evaluation``.

Classifies a raw per-endpoint probe entry into a success/failure verdict, a
failure category, and a human-readable evaluation sentence, folding in the
data-quality rollup from :func:`evaluate_data_quality`. CSV serialization of the
evaluated entry lives in the sibling :mod:`csv_report` module.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from courtside_data.client._pipelines._data_quality import evaluate_data_quality
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


def _string_cell(value: Any) -> str:
    return "" if value is None else str(value)


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
    if failed_stage in {"parse", "table_resolution"} or _has_token(
        error_type=error_type, error_message=error_message, tokens=_PARSE_ERROR_TOKENS
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
    if evaluated.get("status_code") is None and evaluated.get("debug_status") is not None:
        evaluated["status_code"] = evaluated["debug_status"]
    works = _works(evaluated)
    failure_category = _failure_category(evaluated, works=works)
    evaluated["works"] = works
    evaluated["failure_category"] = failure_category
    evaluated["evaluation"] = _evaluation_sentence(evaluated, works=works, failure_category=failure_category)

    custom_diag = evaluated.get("custom_diagnostics_json")
    parser_ignored = None
    if isinstance(custom_diag, dict):
        parser_ignored = custom_diag.get("ignored_row_reason_counts")

    metrics = evaluated.get("metrics")
    truncated_artifacts = None
    if isinstance(metrics, dict):
        truncated_artifacts = metrics.get("trace.truncated_artifact_count")
    evaluated["trace_truncated_artifact_count"] = truncated_artifacts

    quality = evaluate_data_quality(
        ok=bool(evaluated.get("ok")),
        dropped_row_count=evaluated.get("dropped_row_count"),
        dropped_row_reason_counts=evaluated.get("dropped_row_reason_counts_json"),
        parser_ignored_row_reason_counts=parser_ignored if isinstance(parser_ignored, dict) else None,
    )
    evaluated.update(quality)
    return evaluated
