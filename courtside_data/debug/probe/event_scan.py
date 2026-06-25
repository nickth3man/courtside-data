"""Single-pass event-walk state machine for the probe summary.

:func:`scan_events` walks the ordered debug events from one endpoint call once
and accumulates every value the probe summary needs into an :class:`_EventScan`.
Each concern (HTTP response, rate-limit, dispatch, parse, provenance, table
resolution, validation, diagnostics, exception) reads as its own focused handler.

The per-event handlers run in the **same order** as the original inline code,
so fields written by more than one concern (``parser_name``, ``model_name``,
``selected_table_id``,
``validation_status``) keep their original last-write-wins semantics. The
post-loop enrichment (endpoint-registry metadata, first-row preview, derived
counts, final assembly) stays in :mod:`event_summary`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from courtside_data.debug.probe.event_fields import (
    _HTTP_RESPONSE_EVENTS,
    _content_type_from_headers,
    _event_attributes,
    _event_label,
    _table_id_from_selector,
    _validation_error_paths,
)

# Provenance integer counters carried straight through to the summary dict.
_PROVENANCE_INT_FIELDS = (
    "provenance_field_count",
    "provenance_final_none_count",
    "parser_missed_column_count",
    "schema_defaulted_field_count",
    "validator_coerced_field_count",
    "validator_transformed_field_count",
    "provenance_dropped_row_count",
    "provenance_unresolved_drop_count",
    "workflow_provenance_unavailable_count",
)
# Provenance reason-count maps; stored without the ``_json`` suffix here and
# re-exposed as ``<name>_json`` keys by the summary assembler.
_PROVENANCE_REASON_FIELDS = (
    "provenance_reason_counts",
    "provenance_none_reason_counts",
    "provenance_dropped_row_reason_counts",
)


@dataclass
class _EventScan:
    """Mutable accumulator for one walk over an endpoint call's debug events."""

    # --- event-status accounting ---
    last_event: str | None = None
    last_successful_stage: str | None = None
    failed_stage: str | None = None
    error_event_count: int = 0
    warning_count: int = 0

    # --- HTTP response ---
    http_status_code: int | None = None
    http_reason: str | None = None
    resolved_url: str | None = None
    content_type: str | None = None
    response_bytes: int | None = None
    redirect_count: int | None = None

    # --- rate limiting ---
    rate_limit_wait_ms: float = 0.0

    # --- table resolution ---
    selected_table_id: str | None = None
    candidate_table_ids: list[str] = field(default_factory=list)

    # --- parse output ---
    raw_table_row_count: int | None = None
    raw_table_column_count: int | None = None
    raw_columns: list[str] = field(default_factory=list)
    parsed_fields: list[str] = field(default_factory=list)
    parser_name: str | None = None
    model_name: str | None = None
    source_sections: list[str] = field(default_factory=list)
    parsed_event_count: int | None = None
    ignored_event_count: int | None = None
    period_count: int | None = None
    score_event_count: int | None = None
    substitution_event_count: int | None = None
    workflow_diagnostics: dict[str, Any] = field(default_factory=dict)
    ignored_event_reason_counts: dict[str, int] = field(default_factory=dict)

    # --- validation ---
    validation_error_count: int | None = None
    validation_status: str | None = None
    validation_error_paths: list[str] = field(default_factory=list)

    # --- diagnostics / exception ---
    output_field_count: int | None = None
    traceback_text: str | None = None

    # --- provenance (written straight into the summary by the assembler) ---
    parser_missed_column_count: int | None = None
    workflow_provenance_unavailable_count: int | None = None
    provenance_field_count: int | None = None
    provenance_final_none_count: int | None = None
    schema_defaulted_field_count: int | None = None
    validator_coerced_field_count: int | None = None
    validator_transformed_field_count: int | None = None
    provenance_dropped_row_count: int | None = None
    provenance_unresolved_drop_count: int | None = None
    provenance_reason_counts: dict[str, int] = field(default_factory=dict)
    provenance_none_reason_counts: dict[str, int] = field(default_factory=dict)
    provenance_dropped_row_reason_counts: dict[str, int] = field(default_factory=dict)

    def consume(self, event: Mapping[str, Any]) -> None:
        """Fold a single debug event into the accumulator.

        Handlers run in the same textual order as the original inline loop so
        cross-concern last-write-wins semantics are preserved exactly.
        """
        event_name = str(event.get("event") or "")
        stage = str(event.get("stage") or "")
        event_status = str(event.get("status") or "ok")
        attributes = _event_attributes(event)
        self.last_event = _event_label(event)

        self._consume_status(event, stage=stage, event_status=event_status)
        self._consume_http(event_name=event_name, attributes=attributes)
        self._consume_rate_limit(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_dispatch(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_parse(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_sentinel(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_provenance(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_table_resolution(stage=stage, attributes=attributes)
        self._consume_runner(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_validation(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_diagnostics(stage=stage, event_name=event_name, attributes=attributes)
        self._consume_exception(event_name=event_name, stage=stage, attributes=attributes)

    # -- handlers ----------------------------------------------------------

    def _consume_status(self, event: Mapping[str, Any], *, stage: str, event_status: str) -> None:
        if event_status == "error":
            self.error_event_count += 1
            self.failed_stage = stage or self.failed_stage
        elif event_status in {"cancelled", "warn"} or str(event.get("severity_text") or "").upper() == "WARN":
            self.warning_count += 1
        if event_status == "ok" and stage:
            self.last_successful_stage = stage

    def _consume_http(self, *, event_name: str, attributes: Mapping[str, Any]) -> None:
        if event_name not in _HTTP_RESPONSE_EVENTS:
            return
        status_code = attributes.get("status_code")
        if isinstance(status_code, int):
            self.http_status_code = status_code
        reason = attributes.get("reason_phrase")
        if isinstance(reason, str):
            self.http_reason = reason
        url = attributes.get("final_url") or attributes.get("url")
        if isinstance(url, str):
            self.resolved_url = url
        response_size = attributes.get("response_bytes")
        if isinstance(response_size, int):
            self.response_bytes = response_size
        redirects = attributes.get("redirect_count")
        if isinstance(redirects, int):
            self.redirect_count = redirects
        parsed_content_type = _content_type_from_headers(attributes.get("headers"))
        if parsed_content_type is not None:
            self.content_type = parsed_content_type

    def _consume_rate_limit(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage == "rate_limit" and event_name == "sleep":
            wait_seconds = attributes.get("wait_seconds")
            if isinstance(wait_seconds, int | float):
                self.rate_limit_wait_ms += float(wait_seconds) * 1000.0

    def _consume_dispatch(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage != "endpoint":
            return
        if event_name == "run_endpoint_start":
            row_model = attributes.get("row_model")
            if isinstance(row_model, str):
                self.model_name = row_model
            endpoint_kind = attributes.get("endpoint_kind")
            if endpoint_kind == "workflow":
                self.parser_name = "workflow"
            elif self.parser_name is None:
                self.parser_name = "generic"
        elif event_name == "workflow_service_dispatch":
            self.parser_name = "workflow"
        elif event_name == "generic_service_dispatch":
            self.parser_name = "generic"

    def _consume_parse(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage != "parse":
            return

        if event_name == "parsed_rows_summary":
            summary_parser = attributes.get("parser_name")
            if isinstance(summary_parser, str):
                self.parser_name = summary_parser
            parsed_fields_attr = attributes.get("parsed_fields")
            if isinstance(parsed_fields_attr, list):
                self.parsed_fields = [str(name) for name in parsed_fields_attr]

        if event_name == "generic_table_parsed":
            self.parser_name = "generic_table"
            row_count_value = attributes.get("row_count")
            if isinstance(row_count_value, int):
                self.raw_table_row_count = row_count_value
            column_names = attributes.get("column_names")
            if isinstance(column_names, list):
                self.raw_table_column_count = len(column_names)
                self.raw_columns = [str(name) for name in column_names]
                if not self.parsed_fields:
                    self.parsed_fields = list(self.raw_columns)

        if event_name == "friv_playoff_outcomes_parsed":
            self.parser_name = "friv_playoff_outcomes"
            table_id = attributes.get("table_id")
            if isinstance(table_id, str):
                self.selected_table_id = table_id

        if event_name.endswith("_parsed"):
            self._consume_workflow_parsed(attributes)

    def _consume_workflow_parsed(self, attributes: Mapping[str, Any]) -> None:
        workflow_parser = attributes.get("parser_name")
        if isinstance(workflow_parser, str):
            self.parser_name = workflow_parser
        parsed_events = attributes.get("parsed_event_count")
        if isinstance(parsed_events, int):
            self.parsed_event_count = parsed_events
        ignored_events = attributes.get("ignored_event_count")
        if isinstance(ignored_events, int):
            self.ignored_event_count = ignored_events
        ignored_reasons = attributes.get("ignored_event_reason_counts")
        if isinstance(ignored_reasons, dict):
            self.ignored_event_reason_counts = {
                str(key): int(value) for key, value in ignored_reasons.items() if isinstance(value, int | float)
            }
        sections = attributes.get("source_sections")
        if isinstance(sections, list):
            self.source_sections = [str(section) for section in sections]
        periods = attributes.get("period_count")
        if isinstance(periods, int):
            self.period_count = periods
        score_events = attributes.get("score_event_count")
        if isinstance(score_events, int):
            self.score_event_count = score_events
        substitution_events = attributes.get("substitution_event_count")
        if isinstance(substitution_events, int):
            self.substitution_event_count = substitution_events
        workflow_diag = attributes.get("workflow_diagnostics")
        if isinstance(workflow_diag, dict):
            self.workflow_diagnostics.update(
                {str(key): value for key, value in workflow_diag.items() if value is not None}
            )
        ignored_rows = attributes.get("ignored_row_reason_counts")
        if isinstance(ignored_rows, dict) and ignored_rows:
            self.workflow_diagnostics.setdefault("ignored_row_reason_counts", {})
            existing_ignored_rows = self.workflow_diagnostics["ignored_row_reason_counts"]
            if isinstance(existing_ignored_rows, dict):
                for key, value in ignored_rows.items():
                    if isinstance(value, int | float):
                        reason_key = str(key)
                        existing_ignored_rows[reason_key] = existing_ignored_rows.get(reason_key, 0) + int(value)

    def _consume_sentinel(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage != "validation" or event_name != "sentinel_rows_observed":
            return
        sentinel_count = attributes.get("sentinel_row_count")
        if isinstance(sentinel_count, int):
            self.workflow_diagnostics["sentinel_row_count"] = sentinel_count
        sentinel_types = attributes.get("sentinel_row_types")
        if isinstance(sentinel_types, dict):
            self.workflow_diagnostics["sentinel_row_types"] = {
                str(key): int(value) for key, value in sentinel_types.items() if isinstance(value, int | float)
            }

    def _consume_provenance(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage != "provenance":
            return

        if event_name == "source_table_provenance":
            missed = attributes.get("parser_missed_column_count")
            if isinstance(missed, int):
                self.parser_missed_column_count = missed

        if event_name == "workflow_endpoint_provenance" and attributes.get("source_cell_mapping_available") is False:
            self.workflow_provenance_unavailable_count = max(int(self.workflow_provenance_unavailable_count or 0), 1)

        if event_name == "field_provenance_summary":
            for key in _PROVENANCE_INT_FIELDS:
                value = attributes.get(key)
                if isinstance(value, int):
                    if key == "workflow_provenance_unavailable_count":
                        self.workflow_provenance_unavailable_count = max(
                            int(self.workflow_provenance_unavailable_count or 0), value
                        )
                    else:
                        setattr(self, key, value)
            for key in _PROVENANCE_REASON_FIELDS:
                value = attributes.get(key)
                if isinstance(value, dict):
                    setattr(
                        self,
                        key,
                        {str(reason): int(count) for reason, count in value.items() if isinstance(count, int | float)},
                    )

    def _consume_table_resolution(self, *, stage: str, attributes: Mapping[str, Any]) -> None:
        if stage != "table_resolution":
            return
        table_id = _table_id_from_selector(attributes.get("selector"))
        fallback_id = attributes.get("fallback_id")
        commented_id = attributes.get("table_id")
        for candidate in (table_id, fallback_id, commented_id):
            if isinstance(candidate, str) and candidate not in self.candidate_table_ids:
                self.candidate_table_ids.append(candidate)
        if attributes.get("matched") is True:
            if isinstance(table_id, str):
                self.selected_table_id = table_id
            elif isinstance(fallback_id, str):
                self.selected_table_id = fallback_id
            elif isinstance(commented_id, str):
                self.selected_table_id = commented_id

    def _consume_runner(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage == "runner" and event_name == "row_model_pipeline_start":
            row_model = attributes.get("row_model")
            if isinstance(row_model, str):
                self.model_name = row_model

    def _consume_validation(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage != "validation":
            return

        if event_name == "pydantic_validation_complete":
            self.validation_status = str(attributes.get("validation_status") or "passed")
            explicit_error_count = attributes.get("validation_error_count")
            self.validation_error_count = explicit_error_count if isinstance(explicit_error_count, int) else 0
            explicit_paths = attributes.get("validation_error_paths")
            self.validation_error_paths = (
                [str(path) for path in explicit_paths] if isinstance(explicit_paths, list) else []
            )

        if event_name == "pydantic_validation_failed":
            self.validation_status = str(attributes.get("validation_status") or "failed")
            explicit_error_count = attributes.get("validation_error_count")
            if isinstance(explicit_error_count, int):
                self.validation_error_count = explicit_error_count
            explicit_paths = attributes.get("validation_error_paths")
            if isinstance(explicit_paths, list):
                self.validation_error_paths = [str(path) for path in explicit_paths]
            else:
                errors = attributes.get("errors")
                if isinstance(errors, list):
                    self.validation_error_count = (
                        len(errors) if self.validation_error_count is None else self.validation_error_count
                    )
                    self.validation_error_paths = _validation_error_paths(errors)

    def _consume_diagnostics(self, *, stage: str, event_name: str, attributes: Mapping[str, Any]) -> None:
        if stage == "diagnostics" and event_name == "rows_observed":
            observed_name = attributes.get("name")
            column_count_value = attributes.get("column_count")
            if observed_name == "result_data" and isinstance(column_count_value, int):
                self.output_field_count = column_count_value

    def _consume_exception(self, *, event_name: str, stage: str, attributes: Mapping[str, Any]) -> None:
        if event_name != "exception":
            return
        self.failed_stage = stage or self.failed_stage
        stacktrace = attributes.get("exception.stacktrace")
        if isinstance(stacktrace, str):
            self.traceback_text = stacktrace


def scan_events(events: Iterable[Mapping[str, Any]]) -> _EventScan:
    """Walk ``events`` once and return the populated :class:`_EventScan`."""
    scan = _EventScan()
    for event in events:
        scan.consume(event)
    return scan
