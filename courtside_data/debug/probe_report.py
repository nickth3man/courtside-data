"""Backward-compatible facade for the probe report/evaluation code.

The evaluation/classification logic now lives in
:mod:`courtside_data.debug.probe.report` and the CSV serialization in
:mod:`courtside_data.debug.probe.csv_report`. This module re-exports every name
from those modules so existing ``courtside_data.debug.probe_report`` imports keep
working unchanged.
"""

from __future__ import annotations

from courtside_data.debug.probe.csv_report import (
    CSV_COLUMNS,
    _bool_cell,
    _csv_row,
    _json_cell,
    _StreamingCsvWriter,
    write_probe_csv_report,
)
from courtside_data.debug.probe.report import (
    _DOMAIN_HTTP_ERROR_TYPES,
    _EMPTY_RESULT_ERROR_TYPES,
    _HTTP_ERROR_TOKENS,
    _PARSE_ERROR_TOKENS,
    FAILURE_EMPTY_RESULT,
    FAILURE_HTTP_ERROR,
    FAILURE_MISSING_SAMPLE_PARAMS,
    FAILURE_NONE,
    FAILURE_PARSE_ERROR,
    FAILURE_RATE_LIMITED,
    FAILURE_SCHEMA_VALIDATION,
    FAILURE_TIMEOUT,
    FAILURE_UNEXPECTED_EXCEPTION,
    MISSING_SAMPLE_PARAMS_ERROR,
    _evaluation_sentence,
    _failure_category,
    _failure_detail,
    _has_token,
    _string_cell,
    _with_evaluation,
    _works,
)

__all__ = [
    "CSV_COLUMNS",
    "FAILURE_EMPTY_RESULT",
    "FAILURE_HTTP_ERROR",
    "FAILURE_MISSING_SAMPLE_PARAMS",
    "FAILURE_NONE",
    "FAILURE_PARSE_ERROR",
    "FAILURE_RATE_LIMITED",
    "FAILURE_SCHEMA_VALIDATION",
    "FAILURE_TIMEOUT",
    "FAILURE_UNEXPECTED_EXCEPTION",
    "MISSING_SAMPLE_PARAMS_ERROR",
    "_DOMAIN_HTTP_ERROR_TYPES",
    "_EMPTY_RESULT_ERROR_TYPES",
    "_HTTP_ERROR_TOKENS",
    "_PARSE_ERROR_TOKENS",
    "_StreamingCsvWriter",
    "_bool_cell",
    "_csv_row",
    "_evaluation_sentence",
    "_failure_category",
    "_failure_detail",
    "_has_token",
    "_json_cell",
    "_string_cell",
    "_with_evaluation",
    "_works",
    "write_probe_csv_report",
]
