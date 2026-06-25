"""Flat CSV serialization of evaluated probe results.

Maps an evaluated probe entry (see :mod:`report`) onto the fixed
:data:`CSV_COLUMNS` schema and writes rows incrementally so a partial run
survives interruption.
"""

from __future__ import annotations

import csv
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import orjson

from courtside_data.debug.probe.report import _string_cell, _with_evaluation

# Canonical endpoint/probe terminology uses endpoint_domain, endpoint_kind, and
# workflow_* diagnostics.
CSV_COLUMNS: tuple[str, ...] = (
    "endpoint",
    "params_json",
    "ok",
    "works",
    "evaluation",
    "failure_category",
    "error_type",
    "error_message",
    "debug_status",
    "http_status_code",
    "http_reason",
    "resolved_url",
    "content_type",
    "response_bytes",
    "redirect_count",
    "rate_limit_wait_ms",
    "endpoint_domain",
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
    "validation_status",
    "validation_error_count",
    "validation_error_paths_json",
    "output_type",
    "raw_column_count",
    "raw_columns_json",
    "parsed_field_count",
    "parsed_fields_json",
    "validated_field_count",
    "validated_fields_json",
    "output_field_count",
    "output_fields_json",
    "raw_row_count",
    "parsed_row_count",
    "validated_row_count",
    "output_row_count",
    "dropped_row_count",
    "dropped_row_reason_counts_json",
    "data_quality_status",
    "data_quality_warnings_json",
    "drop_rate",
    "drop_rate_warning",
    "expected_drop_count",
    "unexpected_drop_count",
    "provenance_field_count",
    "provenance_final_none_count",
    "provenance_reason_counts_json",
    "provenance_none_reason_counts_json",
    "parser_missed_column_count",
    "schema_defaulted_field_count",
    "validator_coerced_field_count",
    "validator_transformed_field_count",
    "provenance_dropped_row_count",
    "provenance_dropped_row_reason_counts_json",
    "provenance_unresolved_drop_count",
    "workflow_provenance_unavailable_count",
    "trace_truncated_artifact_count",
    "source_sections_json",
    "parsed_event_count",
    "ignored_event_count",
    "ignored_event_reason_counts_json",
    "period_count",
    "score_event_count",
    "substitution_event_count",
    "workflow_diagnostics_json",
    "first_row_preview_json",
    "first_row_preview_truncated",
    "first_row_preview_field_count",
    "first_row_total_field_count",
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


def _json_cell(value: Any) -> str:
    return orjson.dumps(value, option=orjson.OPT_SORT_KEYS, default=str).decode("utf-8")


def _bool_cell(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return _string_cell(value)


def _csv_row(entry: Mapping[str, Any]) -> dict[str, str]:
    evaluated = _with_evaluation(entry)
    json_field_map = {
        "params_json": "params",
        "stage_counts_json": "stage_counts",
        "metrics_json": "metrics",
        "required_params_json": "required_params_json",
        "candidate_table_ids_json": "candidate_table_ids_json",
        "validation_error_paths_json": "validation_error_paths_json",
        "raw_columns_json": "raw_columns_json",
        "parsed_fields_json": "parsed_fields_json",
        "validated_fields_json": "validated_fields_json",
        "output_fields_json": "output_fields_json",
        "dropped_row_reason_counts_json": "dropped_row_reason_counts_json",
        "provenance_reason_counts_json": "provenance_reason_counts_json",
        "provenance_none_reason_counts_json": "provenance_none_reason_counts_json",
        "provenance_dropped_row_reason_counts_json": "provenance_dropped_row_reason_counts_json",
        "data_quality_warnings_json": "data_quality_warnings_json",
        "source_sections_json": "source_sections_json",
        "ignored_event_reason_counts_json": "ignored_event_reason_counts_json",
        "workflow_diagnostics_json": "workflow_diagnostics_json",
        "first_row_preview_json": "first_row_preview_json",
    }
    json_defaults: dict[str, Any] = {
        "stage_counts": {},
        "metrics": {},
        "dropped_row_reason_counts_json": {},
        "provenance_reason_counts_json": {},
        "provenance_none_reason_counts_json": {},
        "provenance_dropped_row_reason_counts_json": {},
        "data_quality_warnings_json": [],
        "ignored_event_reason_counts_json": {},
        "workflow_diagnostics_json": {},
    }
    bool_fields = {"ok", "works", "trace_log_exists", "first_row_preview_truncated", "drop_rate_warning"}
    row: dict[str, str] = {}
    for column in CSV_COLUMNS:
        if column in json_field_map:
            source_key = json_field_map[column]
            value = evaluated.get(source_key)
            if value is None:
                value = json_defaults.get(source_key, [])
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
