"""Probe run orchestration: one live call per endpoint into a summary report.

Resolves which endpoints to probe, loads any resume state, runs each endpoint
with ``debug=True`` (capturing the trace), enriches/evaluates each result, and
writes the JSON (and optional streaming CSV) report.
"""

from __future__ import annotations

import csv
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import orjson

from courtside_data.client._runner import _run_endpoint
from courtside_data.debug import DebugTrace
from courtside_data.debug.probe.csv_report import _StreamingCsvWriter
from courtside_data.debug.probe.enrichment import (
    _default_enrichment,
    _enrich_entry_from_trace,
    _extract_stats,
)
from courtside_data.debug.probe.models import SampleParamsInfo
from courtside_data.debug.probe.report import MISSING_SAMPLE_PARAMS_ERROR, _with_evaluation
from courtside_data.debug.probe.report_summary import _summarize_report
from courtside_data.debug.probe.samples import _sample_params_per_endpoint
from courtside_data.debug.sink import resolve_log_dir
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import RateLimitJailed


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
