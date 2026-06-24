"""Provenance reason constants and types.

The strings and :data:`ProvenanceReason` literal here are the persisted
vocabulary for debug-envelope artifacts and downstream report JSON.
Renaming any of them is a breaking change.
"""

from __future__ import annotations

from typing import Literal

PROVENANCE_SOURCE_VALUE_PRESENT = "source_value_present"
PROVENANCE_SOURCE_COLUMN_ABSENT = "source_column_absent"
PROVENANCE_SOURCE_CELL_BLANK = "source_cell_blank"
PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL = "source_cell_dash_or_sentinel"
PROVENANCE_PARSER_EMITTED_VALUE = "parser_emitted_value"
PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN = "parser_omitted_present_column"
PROVENANCE_SCHEMA_DEFAULT_USED = "schema_default_used"
PROVENANCE_VALIDATOR_COERCED_TO_NONE = "validator_coerced_to_none"
PROVENANCE_VALIDATOR_TRANSFORMED_VALUE = "validator_transformed_value"
PROVENANCE_ROW_DROPPED_EXPECTED_REASON = "row_dropped_expected_reason"
PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR = "row_dropped_unresolved_validation_error"
PROVENANCE_CUSTOM_PARSER_VALUE = "custom_parser_value"
PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE = "custom_parser_metadata_unavailable"
PROVENANCE_DEBUG_UNAVAILABLE = "debug_provenance_unavailable"
PROVENANCE_UNKNOWN = "unknown"

ProvenanceReason = Literal[
    "source_value_present",
    "source_column_absent",
    "source_cell_blank",
    "source_cell_dash_or_sentinel",
    "parser_emitted_value",
    "parser_omitted_present_column",
    "schema_default_used",
    "validator_coerced_to_none",
    "validator_transformed_value",
    "row_dropped_expected_reason",
    "row_dropped_unresolved_validation_error",
    "custom_parser_value",
    "custom_parser_metadata_unavailable",
    "debug_provenance_unavailable",
    "unknown",
]

_DASH_OR_SENTINEL_VALUES = frozenset({"-", "\u2013", "\u2014", "n/a", "na", "none"})
