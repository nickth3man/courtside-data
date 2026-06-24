"""Debug-only source/value provenance helpers (re-export facade)."""

from __future__ import annotations

from courtside_data.debug._provenance_constants import (
    PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE,
    PROVENANCE_CUSTOM_PARSER_VALUE,
    PROVENANCE_DEBUG_UNAVAILABLE,
    PROVENANCE_PARSER_EMITTED_VALUE,
    PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN,
    PROVENANCE_ROW_DROPPED_EXPECTED_REASON,
    PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR,
    PROVENANCE_SCHEMA_DEFAULT_USED,
    PROVENANCE_SOURCE_CELL_BLANK,
    PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL,
    PROVENANCE_SOURCE_COLUMN_ABSENT,
    PROVENANCE_SOURCE_VALUE_PRESENT,
    PROVENANCE_UNKNOWN,
    PROVENANCE_VALIDATOR_COERCED_TO_NONE,
    PROVENANCE_VALIDATOR_TRANSFORMED_VALUE,
    ProvenanceReason,
)
from courtside_data.debug._provenance_context import (
    _SAMPLE_LIMIT,
    _TRACE_CONTEXTS,
    get_trace_context,
    trace_context,
)
from courtside_data.debug._provenance_dropped import (
    build_dropped_row_provenance_records,
    classify_validation_drop,
)
from courtside_data.debug._provenance_emission import (
    emit_field_provenance,
    summarize_provenance,
)
from courtside_data.debug._provenance_field import (
    accepted_input_keys,
    build_field_provenance_records,
    expected_model_source_keys,
)
from courtside_data.debug._provenance_snapshot import (
    build_source_table_snapshot,
    record_table_provenance,
    record_unavailable_table_provenance,
)
from courtside_data.debug._provenance_types import (
    ProvenanceContext,
    SourceCell,
    SourceColumn,
    SourceTableSnapshot,
)

__all__ = [
    # Reason constants
    "PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE",
    "PROVENANCE_CUSTOM_PARSER_VALUE",
    "PROVENANCE_DEBUG_UNAVAILABLE",
    "PROVENANCE_PARSER_EMITTED_VALUE",
    "PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN",
    "PROVENANCE_ROW_DROPPED_EXPECTED_REASON",
    "PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR",
    "PROVENANCE_SCHEMA_DEFAULT_USED",
    "PROVENANCE_SOURCE_CELL_BLANK",
    "PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL",
    "PROVENANCE_SOURCE_COLUMN_ABSENT",
    "PROVENANCE_SOURCE_VALUE_PRESENT",
    "PROVENANCE_UNKNOWN",
    "PROVENANCE_VALIDATOR_COERCED_TO_NONE",
    "PROVENANCE_VALIDATOR_TRANSFORMED_VALUE",
    # Internal-but-preserved names (originally underscore-prefixed module
    # attributes that callers historically reached for; kept here so the
    # facade is a true drop-in for the pre-split module).
    "_SAMPLE_LIMIT",
    "_TRACE_CONTEXTS",
    # Types
    "ProvenanceContext",
    "ProvenanceReason",
    "SourceCell",
    "SourceColumn",
    "SourceTableSnapshot",
    # Public functions
    "accepted_input_keys",
    "build_dropped_row_provenance_records",
    "build_field_provenance_records",
    "build_source_table_snapshot",
    "classify_validation_drop",
    "emit_field_provenance",
    "expected_model_source_keys",
    "get_trace_context",
    "record_table_provenance",
    "record_unavailable_table_provenance",
    "summarize_provenance",
    "trace_context",
]
