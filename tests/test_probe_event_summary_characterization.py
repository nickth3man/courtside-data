"""Characterization (golden-master) test for the probe event-summary walker.

This test locks the **full output dict** of
:func:`courtside_data.debug.probe.event_summary._summarize_debug_events` across a
battery of debug envelopes that, between them, exercise every branch of the
event-walk state machine: HTTP-response extraction, rate-limit accounting,
endpoint dispatch, generic / custom / friv parse events, sentinel rows,
provenance summaries, the table-resolution ladder, validation success and
failure, diagnostics, exceptions, post-loop endpoint-registry enrichment, and
first-row preview.

It exists to make the *structural* decomposition of ``event_summary.py`` safe:
the per-key assertions in ``test_debug_probe_csv.py`` cover the common keys, but
this test pins the entire dict so a subtle merge/ordering regression fails
loudly.

The expected outputs live in ``tests/golden/probe_event_summary.json``. They are
generated from the canonical implementation by running
``generate_golden()`` (see ``__main__`` guard below) and are never regenerated
automatically — if a future change *intends* to alter the summary shape, a human
regenerates and reviews the diff.

The envelope inputs are defined in Python here (not loaded from the golden) so
that only the *expected output* round-trips through JSON; the inputs stay
byte-identical between generation and assertion.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from courtside_data.debug.probe.event_summary import _summarize_debug_events

_GOLDEN_PATH = Path(__file__).parent / "golden" / "probe_event_summary.json"


# ---------------------------------------------------------------------------
# Envelope battery — each builder returns (debug_envelope, summarize_kwargs).
# ---------------------------------------------------------------------------


def _generic_success() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "schema_version": 3,
        "trace_id": "trace-success",
        "duration_ms": 12.5,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {"debug.enabled": True},
        "stage_counts": {"http": 2, "parse": 1, "validation": 1, "runner": 1},
        "spans": [
            {"span_id": "span-http", "stage": "http", "duration_ms": 1200.0},
            {"span_id": "span-validation", "stage": "validation", "duration_ms": 45.2},
        ],
        "events": [
            {
                "stage": "endpoint",
                "event": "run_endpoint_start",
                "status": "ok",
                "attributes": {"row_model": "TeamRosterRow", "custom": False},
            },
            {"stage": "rate_limit", "event": "sleep", "status": "ok", "attributes": {"wait_seconds": 0.25}},
            {
                "stage": "http",
                "event": "request_complete",
                "status": "ok",
                "attributes": {
                    "status_code": 200,
                    "reason_phrase": "OK",
                    "final_url": "https://www.basketball-reference.com/teams/BOS/2024.html",
                    "response_bytes": 120_000,
                    "redirect_count": 0,
                    "headers": {"content-type": "text/html; charset=utf-8"},
                },
            },
            {
                "stage": "table_resolution",
                "event": "table_id_lookup",
                "status": "ok",
                "attributes": {"selector": "table[@id='roster']", "matched": True, "match_count": 1},
            },
            {
                "stage": "parse",
                "event": "parsed_rows_summary",
                "status": "ok",
                "attributes": {
                    "parser_name": "generic_table",
                    "parsed_row_count": 17,
                    "parsed_fields": ["player", "age", "pts"],
                },
            },
            {
                "stage": "parse",
                "event": "generic_table_parsed",
                "status": "ok",
                "attributes": {"source": "table_id", "row_count": 17, "column_names": ["player", "age", "pts"]},
            },
            {
                "stage": "runner",
                "event": "row_model_pipeline_start",
                "status": "ok",
                "attributes": {"row_model": "TeamRosterRow", "raw_row_count": 17},
            },
            {
                "stage": "validation",
                "event": "pydantic_validation_complete",
                "status": "ok",
                "attributes": {
                    "validation_status": "passed",
                    "validated_row_count": 17,
                    "row_count": 17,
                    "validation_error_count": 0,
                    "validation_error_paths": [],
                },
            },
            {
                "stage": "diagnostics",
                "event": "rows_observed",
                "status": "ok",
                "attributes": {"name": "result_data", "column_count": 3, "row_count": 17},
            },
        ],
    }
    kwargs = {
        "data": [{"player": "Tatum", "age": 26, "pts": 26.9}],
        "endpoint_name": "team_roster",
    }
    return debug, kwargs


def _generic_success_no_data() -> tuple[dict[str, Any], dict[str, Any]]:
    debug, _ = _generic_success()
    return debug, {"endpoint_name": "team_roster"}


def _custom_play_by_play() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "trace_id": "trace-pbp",
        "duration_ms": 30.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {"debug.enabled": True},
        "stage_counts": {"parse": 1},
        "spans": [{"span_id": "s1", "stage": "row_parse", "duration_ms": 120.0}],
        "events": [
            {
                "stage": "endpoint",
                "event": "run_endpoint_start",
                "status": "ok",
                "attributes": {"row_model": None, "custom": True},
            },
            {"stage": "endpoint", "event": "custom_service_dispatch", "status": "ok", "attributes": {}},
            {
                "stage": "http",
                "event": "attempt_response",
                "status": "ok",
                "attributes": {
                    "status_code": 200,
                    "reason_phrase": "OK",
                    "url": "https://www.basketball-reference.com/boxscores/pbp/x.html",
                    "response_bytes": 90_000,
                    "redirect_count": 0,
                    "headers": {"Content-Type": "text/html"},
                },
            },
            {
                "stage": "parse",
                "event": "play_by_play_parsed",
                "status": "ok",
                "attributes": {
                    "parser_name": "play_by_play",
                    "parsed_event_count": 450,
                    "ignored_event_count": 12,
                    "ignored_event_reason_counts": {"unparseable": 12},
                    "source_sections": ["q1", "q2", "q3", "q4"],
                    "period_count": 4,
                    "score_event_count": 210,
                    "substitution_event_count": 40,
                    "custom_diagnostics": {"selected_table_id": "pbp", "candidate_table_ids": ["pbp"]},
                    "ignored_row_reason_counts": {"blank": 3},
                },
            },
            {
                "stage": "validation",
                "event": "sentinel_rows_observed",
                "status": "ok",
                "attributes": {"sentinel_row_count": 2, "sentinel_row_types": {"quarter_header": 2}},
            },
        ],
    }
    kwargs = {
        "data": [{"period": 1, "description": "made shot"}],
        "endpoint_name": "play_by_play",
    }
    return debug, kwargs


def _validation_failed() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "trace_id": "trace-validation",
        "duration_ms": 8.25,
        "status": {"code": "error", "error_type": "SchemaDriftError", "error_message": "missing field fg3_pct"},
        "metrics": {"debug.enabled": True},
        "stage_counts": {"validation": 2},
        "events": [
            {
                "stage": "validation",
                "event": "pydantic_validation_failed",
                "status": "error",
                "attributes": {
                    "row_model": "PlayerCareerStatsRow",
                    "errors": [{"loc": ["fg3_pct"], "msg": "Field required"}],
                },
            },
            {
                "stage": "validation",
                "event": "exception",
                "status": "error",
                "attributes": {
                    "exception.type": "ValidationError",
                    "exception.message": "validation failed",
                    "exception.stacktrace": 'Traceback (most recent call last):\n  File "x.py", line 1\nError\n',
                },
            },
        ],
    }
    return debug, {"endpoint_name": "player_career_stats"}


def _http_error() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "trace_id": "trace-http",
        "duration_ms": 4.0,
        "status": {"code": "error", "error_type": "InvalidTeam", "error_message": "Invalid team ATL"},
        "metrics": {},
        "stage_counts": {"http": 3},
        "events": [
            {
                "stage": "http",
                "event": "status_error",
                "status": "error",
                "attributes": {
                    "status_code": 404,
                    "reason_phrase": "Not Found",
                    "url": "https://www.basketball-reference.com/teams/ATL/2024.html",
                    "response_bytes": 512,
                    "redirect_count": 1,
                },
            },
            {
                "stage": "http",
                "event": "exception",
                "status": "error",
                "attributes": {"exception.type": "InvalidTeam", "exception.message": "Invalid team ATL"},
            },
        ],
    }
    return debug, {"endpoint_name": "team_roster"}


def _provenance() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "trace_id": "trace-prov",
        "duration_ms": 15.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {},
        "stage_counts": {"provenance": 1},
        "events": [
            {
                "stage": "provenance",
                "event": "source_table_provenance",
                "status": "ok",
                "attributes": {"parser_missed_column_count": 1},
            },
            {
                "stage": "provenance",
                "event": "custom_endpoint_provenance",
                "status": "ok",
                "attributes": {"source_cell_mapping_available": False},
            },
            {
                "stage": "provenance",
                "event": "field_provenance_summary",
                "status": "ok",
                "attributes": {
                    "provenance_field_count": 4,
                    "provenance_final_none_count": 2,
                    "parser_missed_column_count": 0,
                    "schema_defaulted_field_count": 1,
                    "validator_coerced_field_count": 1,
                    "validator_transformed_field_count": 0,
                    "provenance_dropped_row_count": 1,
                    "provenance_unresolved_drop_count": 0,
                    "custom_provenance_unavailable_count": 0,
                    "provenance_reason_counts": {"source_value_present": 2},
                    "provenance_none_reason_counts": {"source_column_absent": 2},
                    "provenance_dropped_row_reason_counts": {"row_dropped_expected_reason": 1},
                },
            },
        ],
    }
    return debug, {"endpoint_name": "team_roster"}


def _friv_with_fallback_table() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "trace_id": "trace-friv",
        "duration_ms": 9.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {},
        "stage_counts": {"parse": 1},
        "events": [
            {
                "stage": "table_resolution",
                "event": "fallback_lookup",
                "status": "warn",
                "severity_text": "WARN",
                "attributes": {"selector": "table[@id='primary']", "fallback_id": "secondary", "matched": False},
            },
            {
                "stage": "table_resolution",
                "event": "commented_lookup",
                "status": "ok",
                "attributes": {"table_id": "commented_one", "matched": True},
            },
            {
                "stage": "parse",
                "event": "friv_playoff_outcomes_parsed",
                "status": "ok",
                "attributes": {"table_id": "playoff_series", "parser_name": "friv_playoff_outcomes"},
            },
        ],
    }
    return debug, {"endpoint_name": "friv_7_game_playoff_series_outcomes_team_is_tied"}


def _empty_events() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "trace_id": "trace-empty",
        "duration_ms": 1.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {},
        "stage_counts": {},
        "events": [],
    }
    return debug, {"endpoint_name": "team_roster"}


def _unknown_endpoint() -> tuple[dict[str, Any], dict[str, Any]]:
    debug, _ = _generic_success()
    return debug, {"data": [{"a": 1}], "endpoint_name": None}


def _row_filtering() -> tuple[dict[str, Any], dict[str, Any]]:
    debug = {
        "trace_id": "trace-filter",
        "duration_ms": 5.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {},
        "stage_counts": {},
        "events": [
            {
                "stage": "runner",
                "event": "row_model_pipeline_start",
                "status": "ok",
                "attributes": {"row_model": "TeamRosterRow", "raw_row_count": 20},
            },
            {
                "stage": "parse",
                "event": "generic_table_parsed",
                "status": "ok",
                "attributes": {"row_count": 20, "column_names": ["a", "b"]},
            },
            {
                "stage": "validation",
                "event": "rows_filtered",
                "status": "ok",
                "attributes": {"dropped_row_reason_counts": {"sentinel": 3}},
            },
            {
                "stage": "validation",
                "event": "pydantic_validation_complete",
                "status": "ok",
                "attributes": {"validation_status": "passed", "validated_row_count": 17},
            },
        ],
    }
    return debug, {"data": [{}] * 17, "endpoint_name": "team_roster"}


# Registry of named cases. Keep names stable — they key the golden file.
CASES: dict[str, Callable[[], tuple[dict[str, Any], dict[str, Any]]]] = {
    "generic_success": _generic_success,
    "generic_success_no_data": _generic_success_no_data,
    "custom_play_by_play": _custom_play_by_play,
    "validation_failed": _validation_failed,
    "http_error": _http_error,
    "provenance": _provenance,
    "friv_with_fallback_table": _friv_with_fallback_table,
    "empty_events": _empty_events,
    "unknown_endpoint": _unknown_endpoint,
    "row_filtering": _row_filtering,
}


def _load_golden() -> dict[str, Any]:
    with _GOLDEN_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.mark.parametrize("case_name", sorted(CASES))
def test_event_summary_matches_golden(case_name: str) -> None:
    """``_summarize_debug_events`` output must equal the frozen golden snapshot."""
    golden = _load_golden()
    assert case_name in golden, f"golden missing case {case_name!r}; regenerate with generate_golden()"

    debug, kwargs = CASES[case_name]()
    actual = _summarize_debug_events(debug, **kwargs)

    # Round-trip the actual through JSON so the comparison matches the golden's
    # JSON-native types exactly (no tuples, etc.).
    actual_json = json.loads(json.dumps(actual))
    assert actual_json == golden[case_name]


def generate_golden() -> None:
    """Regenerate the golden file from the *current* implementation.

    Invoked deliberately by a human (never from a test). Run with::

        uv run python -m tests.test_probe_event_summary_characterization
    """
    snapshot: dict[str, Any] = {}
    for name, builder in CASES.items():
        debug, kwargs = builder()
        snapshot[name] = _summarize_debug_events(debug, **kwargs)
    _GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _GOLDEN_PATH.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    generate_golden()
    print(f"wrote {_GOLDEN_PATH}")
