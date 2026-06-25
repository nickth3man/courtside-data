"""Turn raw endpoint envelopes / captured traces into enriched probe entries.

``_default_enrichment`` seeds an entry from registry metadata before a call is
made; ``_extract_stats`` and ``_enrich_entry_from_trace`` fold the post-call
debug summary back into the entry. ``_find_trace_log_path`` locates the written
trace log inside an envelope.
"""

from __future__ import annotations

from typing import Any

from courtside_data.debug import DebugTrace
from courtside_data.debug.probe.event_fields import _event_attributes
from courtside_data.debug.probe.event_summary import _summarize_debug_events
from courtside_data.debug.probe.models import SampleParamsInfo
from courtside_data.debug.probe.samples import _endpoint_domain, _endpoint_kind
from courtside_data.endpoints import ENDPOINTS


def _default_enrichment(*, endpoint_name: str, sample: SampleParamsInfo | None = None) -> dict[str, Any]:
    endpoint = ENDPOINTS.get(endpoint_name)
    enrichment: dict[str, Any] = {
        "endpoint_domain": _endpoint_domain(endpoint),
        "endpoint_kind": _endpoint_kind(endpoint),
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
        "workflow_provenance_unavailable_count": None,
        "source_sections_json": [],
        "ignored_event_reason_counts_json": {},
        "workflow_diagnostics_json": {},
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
