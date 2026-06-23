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
import sys
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson
from tests.fixture_manifest import ALL_CASES

from courtside_data.client._runner import _run_endpoint
from courtside_data.debug.sink import resolve_log_dir
from courtside_data.endpoints import ENDPOINTS
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
    "row_count",
    "duration_ms",
    "elapsed_ms",
    "trace_id",
    "trace_log_path",
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


def _sample_params_per_endpoint() -> dict[str, dict[str, Any]]:
    """Pick the first manifest case for each endpoint (stable sort by case id)."""
    params_by_endpoint: dict[str, dict[str, Any]] = {}
    for case in sorted(ALL_CASES, key=lambda item: item.id):
        if case.endpoint_name not in params_by_endpoint:
            params_by_endpoint[case.endpoint_name] = dict(case.params)
    for name, endpoint in ENDPOINTS.items():
        if name not in params_by_endpoint and not endpoint.params:
            params_by_endpoint[name] = {}
    return params_by_endpoint


def _row_count(data: Any) -> int | None:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            return len(data["data"])
        return len(data)
    return None


def _extract_stats(envelope: Any) -> dict[str, Any]:
    if not isinstance(envelope, dict) or "debug" not in envelope:
        return {}
    debug = envelope["debug"]
    if not isinstance(debug, dict):
        return {}
    metrics = debug.get("metrics") or {}
    status = debug.get("status") or {}
    return {
        "duration_ms": debug.get("duration_ms"),
        "status_code": status.get("code"),
        "error_type": status.get("error_type"),
        "error_message": status.get("error_message"),
        "row_count": _row_count(envelope.get("data")),
        "metrics": dict(metrics) if isinstance(metrics, dict) else {},
        "stage_counts": debug.get("stage_counts"),
        "trace_id": debug.get("trace_id"),
    }


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
    status_code = _string_cell(entry.get("status_code"))
    if status_code:
        return f"status {status_code}"
    return "no error detail reported"


def _has_token(*, error_type: str, error_message: str, tokens: Sequence[str]) -> bool:
    haystack = f"{error_type} {error_message}".lower()
    return any(token in haystack for token in tokens)


def _works(entry: Mapping[str, Any]) -> bool:
    return entry.get("ok") is True and entry.get("status_code") == "ok" and not entry.get("error_type")


def _failure_category(entry: Mapping[str, Any], *, works: bool) -> str:
    if works:
        return FAILURE_NONE

    error_type = _string_cell(entry.get("error_type"))
    error_message = _string_cell(entry.get("error_message"))
    status_code = _string_cell(entry.get("status_code"))

    if error_type == MISSING_SAMPLE_PARAMS_ERROR:
        return FAILURE_MISSING_SAMPLE_PARAMS
    if error_type == RateLimitJailed.__name__:
        return FAILURE_RATE_LIMITED
    if error_type in _EMPTY_RESULT_ERROR_TYPES:
        return FAILURE_EMPTY_RESULT
    if _has_token(error_type=error_type, error_message=error_message, tokens=("timeout", "timed out")):
        return FAILURE_TIMEOUT
    if error_type in _DOMAIN_HTTP_ERROR_TYPES or _has_token(
        error_type=error_type,
        error_message=error_message,
        tokens=_HTTP_ERROR_TOKENS,
    ):
        return FAILURE_HTTP_ERROR
    if error_type == SchemaDriftError.__name__ or _has_token(
        error_type=error_type,
        error_message=error_message,
        tokens=("validation", "schema drift", "pydantic"),
    ):
        return FAILURE_SCHEMA_VALIDATION
    if _has_token(error_type=error_type, error_message=error_message, tokens=_PARSE_ERROR_TOKENS):
        return FAILURE_PARSE_ERROR
    if entry.get("row_count") == 0 and status_code and status_code != "ok":
        return FAILURE_EMPTY_RESULT
    return FAILURE_UNEXPECTED_EXCEPTION


def _evaluation_sentence(entry: Mapping[str, Any], *, works: bool, failure_category: str) -> str:
    row_count = entry.get("row_count")
    if works:
        if row_count == 0:
            return "Endpoint completed successfully but returned zero rows."
        if isinstance(row_count, int):
            return f"Endpoint completed successfully with {row_count} rows."
        return "Endpoint completed successfully."

    detail = _failure_detail(entry)
    if failure_category == FAILURE_MISSING_SAMPLE_PARAMS:
        return "No fixture-manifest sample params are available, so the endpoint was not probed."
    if failure_category == FAILURE_RATE_LIMITED:
        return f"Endpoint hit Basketball-Reference rate-limit jail; probe stopped after this result. {detail}."
    if failure_category == FAILURE_HTTP_ERROR:
        return f"Endpoint failed during the HTTP/domain lookup stage. {detail}."
    if failure_category == FAILURE_TIMEOUT:
        return f"Endpoint timed out before it could complete. {detail}."
    if failure_category == FAILURE_SCHEMA_VALIDATION:
        return f"Endpoint failed schema validation. {detail}."
    if failure_category == FAILURE_PARSE_ERROR:
        return f"Endpoint failed while parsing or resolving Basketball-Reference tables. {detail}."
    if failure_category == FAILURE_EMPTY_RESULT:
        return f"Endpoint failed because the requested live result was empty or invalid. {detail}."
    return f"Endpoint failed with an unexpected exception. {detail}."


def _with_evaluation(entry: Mapping[str, Any]) -> dict[str, Any]:
    evaluated = dict(entry)
    works = _works(evaluated)
    failure_category = _failure_category(evaluated, works=works)
    evaluated["works"] = works
    evaluated["failure_category"] = failure_category
    evaluated["evaluation"] = _evaluation_sentence(evaluated, works=works, failure_category=failure_category)
    return evaluated


def _csv_row(entry: Mapping[str, Any]) -> dict[str, str]:
    evaluated = _with_evaluation(entry)
    return {
        "endpoint": _string_cell(evaluated.get("endpoint")),
        "params_json": _json_cell(evaluated.get("params")),
        "ok": _bool_cell(evaluated.get("ok")),
        "works": _bool_cell(evaluated.get("works")),
        "evaluation": _string_cell(evaluated.get("evaluation")),
        "failure_category": _string_cell(evaluated.get("failure_category")),
        "error_type": _string_cell(evaluated.get("error_type")),
        "error_message": _string_cell(evaluated.get("error_message")),
        "status_code": _string_cell(evaluated.get("status_code")),
        "row_count": _string_cell(evaluated.get("row_count")),
        "duration_ms": _string_cell(evaluated.get("duration_ms")),
        "elapsed_ms": _string_cell(evaluated.get("elapsed_ms")),
        "trace_id": _string_cell(evaluated.get("trace_id")),
        "trace_log_path": _string_cell(evaluated.get("trace_log_path")),
        "stage_counts_json": _json_cell(evaluated.get("stage_counts") or {}),
        "metrics_json": _json_cell(evaluated.get("metrics") or {}),
    }


def write_probe_csv_report(results: Sequence[Mapping[str, Any]], output_path: Path) -> None:
    """Write evaluated probe results to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(_csv_row(result))


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

    for name in endpoint_names:
        params = params_by_endpoint.get(name)
        entry: dict[str, Any] = {
            "endpoint": name,
            "params": params,
            "ok": False,
        }
        if params is None:
            entry["error_type"] = MISSING_SAMPLE_PARAMS_ERROR
            entry["error_message"] = "No fixture-manifest case available for this endpoint."
            results.append(_with_evaluation(entry))
            continue

        call_started = time.perf_counter()
        try:
            envelope = _run_endpoint(name, params, debug=True)
            stats = _extract_stats(envelope)
            entry.update(stats)
            entry["trace_log_path"] = _find_trace_log_path(envelope)
            entry["ok"] = stats.get("status_code") == "ok"
            entry["elapsed_ms"] = round((time.perf_counter() - call_started) * 1000, 2)
        except RateLimitJailed as exc:
            entry["error_type"] = type(exc).__name__
            entry["error_message"] = str(exc)
            entry["elapsed_ms"] = round((time.perf_counter() - call_started) * 1000, 2)
            results.append(_with_evaluation(entry))
            break
        except Exception as exc:
            entry["error_type"] = type(exc).__name__
            entry["error_message"] = str(exc)
            entry["elapsed_ms"] = round((time.perf_counter() - call_started) * 1000, 2)
        results.append(_with_evaluation(entry))

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
        write_probe_csv_report(results, csv_output_path)
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
