"""Live endpoint probe: call each registry endpoint once and record outcomes.

This package is split into focused modules; this ``__init__`` is the stable
public facade that re-exports the names downstream tooling and tests depend on:

* :mod:`models` -- ``ProbeResult`` / ``SampleParamsInfo`` data types
* :mod:`samples` -- endpoint grouping and sample-parameter selection
* :mod:`previews` -- bounded row/value previews and output-shape inference
* :mod:`event_fields` -- low-level debug-event field extraction
* :mod:`event_summary` -- per-endpoint debug-event summarization
* :mod:`report_summary` -- cross-endpoint report aggregation
* :mod:`enrichment` -- envelope/trace -> enriched probe entry
* :mod:`report` -- works/failure-category/evaluation classification
* :mod:`csv_report` -- flat CSV serialization
* :mod:`runner` -- run orchestration (``probe_endpoints``)
* :mod:`cli` -- command-line entry point (``main``)

Usage::

    uv run python -m courtside_data.debug.probe
    uv run python -m courtside_data.debug.probe --output logs/my_report.json
    uv run python -m courtside_data.debug.probe -e play_by_play -e team_roster
    uv run python -m courtside_data.debug.probe --endpoint friv_7_game_playoff_series_outcomes_team_is_tied
"""

from __future__ import annotations

from courtside_data.debug.probe.cli import _build_parser, main
from courtside_data.debug.probe.csv_report import (
    CSV_COLUMNS,
    _bool_cell,
    _csv_row,
    _json_cell,
    _StreamingCsvWriter,
    write_probe_csv_report,
)

# Internal-but-preserved names: importable from the package (downstream tests
# reach for them) but intentionally kept out of ``__all__``, matching the
# pre-split surface. The ``as`` re-export form marks them as deliberate.
from courtside_data.debug.probe.enrichment import _default_enrichment as _default_enrichment
from courtside_data.debug.probe.event_summary import _summarize_debug_events as _summarize_debug_events
from courtside_data.debug.probe.event_summary import _summarize_row_counts as _summarize_row_counts
from courtside_data.debug.probe.models import ProbeResult, SampleParamsInfo
from courtside_data.debug.probe.previews import _infer_output_type as _infer_output_type
from courtside_data.debug.probe.previews import _preview_result as _preview_result
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
from courtside_data.debug.probe.report_summary import _summarize_report as _summarize_report
from courtside_data.debug.probe.runner import _resolve_endpoint_names, probe_endpoints
from courtside_data.debug.probe.samples import _sample_params_per_endpoint as _sample_params_per_endpoint

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
    "ProbeResult",
    "SampleParamsInfo",
    "_StreamingCsvWriter",
    "_bool_cell",
    "_build_parser",
    "_csv_row",
    "_evaluation_sentence",
    "_failure_category",
    "_failure_detail",
    "_has_token",
    "_json_cell",
    "_resolve_endpoint_names",
    "_string_cell",
    "_with_evaluation",
    "_works",
    "main",
    "probe_endpoints",
    "write_probe_csv_report",
]
