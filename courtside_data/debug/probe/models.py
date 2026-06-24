"""Structured result/model types for the endpoint probe.

These are pure data declarations with no behavior; isolating them keeps the
heavier orchestration and summarization modules focused on logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


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
