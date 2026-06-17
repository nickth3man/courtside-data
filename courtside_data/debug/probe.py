"""Live endpoint probe: call each registry endpoint once and record outcomes.

Uses fixture-manifest sample params (one case per endpoint) and the standard
``debug=True`` path so every call writes a full trace envelope to the debug
log directory. Emits a summary report JSON alongside those per-call traces.

Usage::

    uv run python -m courtside_data.debug.probe
    uv run python -m courtside_data.debug.probe --output logs/my_report.json
    uv run python -m courtside_data.debug.probe -e play_by_play -e team_roster
    uv run python -m courtside_data.debug.probe --endpoint friv_7_game_playoff_series_outcomes_team_is_tied
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.debug.sink import resolve_log_dir
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import RateLimitJailed
from tests.fixture_manifest import ALL_CASES


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


def _resolve_endpoint_names(names: list[str] | None) -> list[str]:
    """Validate and return sorted endpoint names to probe."""
    if not names:
        return sorted(ENDPOINTS)
    unknown = sorted(set(names) - set(ENDPOINTS))
    if unknown:
        known = ", ".join(sorted(ENDPOINTS))
        msg = f"Unknown endpoint(s): {', '.join(unknown)}. Known endpoints: {known}"
        raise ValueError(msg)
    return sorted(set(names))


def probe_endpoints(*, endpoints: list[str] | None = None, output_path: Path | None = None) -> dict[str, Any]:
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
            entry["error_type"] = "MissingSampleParams"
            entry["error_message"] = "No fixture-manifest case available for this endpoint."
            results.append(entry)
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
            results.append(entry)
            break
        except Exception as exc:
            entry["error_type"] = type(exc).__name__
            entry["error_message"] = str(exc)
            entry["elapsed_ms"] = round((time.perf_counter() - call_started) * 1000, 2)
        results.append(entry)

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
    output_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    report["report_path"] = str(output_path)
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe every courtside-data endpoint live and write a JSON report.")
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = probe_endpoints(endpoints=args.endpoints, output_path=args.output)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    summary_keys = ("report_path", "ok_count", "failed_count", "failed_endpoints")
    print(json.dumps({key: report[key] for key in summary_keys}, indent=2))
    return 0 if report["failed_count"] == 0 and not report["missing_sample_params"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
