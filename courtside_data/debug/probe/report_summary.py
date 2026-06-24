"""Cross-endpoint aggregation of probe result rows into report-level diagnostics.

Where :mod:`event_summary` distills one endpoint call, this rolls the full set of
result rows up into report-wide totals: rate-limit waits, slowest endpoint/stage,
trace-log sizes, and aggregate provenance reason counts.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


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
