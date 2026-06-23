from __future__ import annotations

import csv
import json
from pathlib import Path

from courtside_data.debug.probe import (
    _csv_row,
    _default_enrichment,
    _summarize_debug_events,
    _with_evaluation,
    write_probe_csv_report,
)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _successful_debug_envelope(*, trace_log_path: str | None = None) -> dict:
    events = [
        {
            "stage": "endpoint",
            "event": "run_endpoint_start",
            "status": "ok",
            "attributes": {
                "path_template": "teams/{team_abbreviation}/{season_end_year}.html",
                "row_model": "TeamRosterRow",
                "custom": False,
            },
        },
        {
            "stage": "rate_limit",
            "event": "sleep",
            "status": "ok",
            "attributes": {"wait_seconds": 0.25},
        },
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
            "attributes": {
                "selector": "table[@id='roster']",
                "matched": True,
                "match_count": 1,
            },
        },
        {
            "stage": "parse",
            "event": "generic_table_parsed",
            "status": "ok",
            "attributes": {
                "source": "table_id",
                "row_count": 17,
                "column_names": ["player", "age", "pts"],
            },
        },
        {
            "stage": "validation",
            "event": "pydantic_validation_complete",
            "status": "ok",
            "attributes": {"row_model": "TeamRosterRow", "row_count": 17},
        },
        {
            "stage": "diagnostics",
            "event": "rows_observed",
            "status": "ok",
            "attributes": {"name": "result_data", "column_count": 3, "row_count": 17},
        },
        {
            "stage": "output",
            "event": "trace_log",
            "status": "ok",
            "attributes": {"path": trace_log_path or "logs/team_roster.json"},
        },
    ]
    return {
        "schema_version": 3,
        "trace_id": "trace-success",
        "duration_ms": 12.5,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {"debug.enabled": True},
        "stage_counts": {"http": 2, "parse": 1, "validation": 1},
        "events": events,
    }


def test_probe_csv_happy_path_marks_endpoint_working(tmp_path: Path) -> None:
    output_path = tmp_path / "reports" / "probe.csv"
    debug = _successful_debug_envelope()
    summary = _summarize_debug_events(debug, data=[{"player": "Tatum", "age": 26, "pts": 26.9}], endpoint_name="team_roster")
    result = {
        "endpoint": "team_roster",
        "params": {"season_end_year": 2024, "team_abbreviation": "BOS"},
        "ok": True,
        "sample_case_id": "team_roster_BOS_2024",
        "sample_params_source": "fixture_manifest",
        **summary,
    }

    write_probe_csv_report([result], output_path)

    rows = _read_csv_rows(output_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["endpoint"] == "team_roster"
    assert row["ok"] == "true"
    assert row["works"] == "true"
    assert row["failure_category"] == "none"
    assert row["debug_status"] == "ok"
    assert row["http_status_code"] == "200"
    assert row["http_reason"] == "OK"
    assert "basketball-reference.com/teams/BOS/2024.html" in row["resolved_url"]
    assert row["content_type"] == "text/html; charset=utf-8"
    assert row["response_bytes"] == "120000"
    assert row["redirect_count"] == "0"
    assert row["rate_limit_wait_ms"] == "250.0"
    assert row["endpoint_group"] == "teams"
    assert row["endpoint_kind"] == "generic"
    assert row["sample_params_source"] == "fixture_manifest"
    assert row["parser_name"] == "generic_table"
    assert row["model_name"] == "TeamRosterRow"
    assert row["selected_table_id"] == "roster"
    assert json.loads(row["candidate_table_ids_json"]) == ["roster"]
    assert row["raw_table_row_count"] == "17"
    assert row["raw_table_column_count"] == "3"
    assert row["row_count"] == "1"
    assert row["event_count"] == "8"
    assert "HTTP 200 OK" in row["evaluation"]
    assert "parser=generic_table" in row["evaluation"]
    assert "table=roster" in row["evaluation"]


def test_probe_csv_failure_path_includes_category_and_evaluation(tmp_path: Path) -> None:
    output_path = tmp_path / "probe.csv"
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
                    "errors": [{"loc": ("fg3_pct",), "msg": "Field required"}],
                },
            },
            {
                "stage": "validation",
                "event": "exception",
                "status": "error",
                "attributes": {
                    "exception.type": "ValidationError",
                    "exception.message": "validation failed",
                    "exception.stacktrace": "Traceback (most recent call last):\n  File \"x.py\", line 1, in <module>\n    raise Error\nError\n",
                },
            },
        ],
    }
    summary = _summarize_debug_events(debug, endpoint_name="player_career_stats")
    result = {
        "endpoint": "player_career_stats",
        "params": {"player_identifier": "jamesle01"},
        "ok": False,
        "error_type": "SchemaDriftError",
        "error_message": "Schema drift detected for endpoint 'player_career_stats': missing field/alias 'fg3_pct'",
        "elapsed_ms": 8.25,
        **summary,
    }

    write_probe_csv_report([result], output_path)

    rows = _read_csv_rows(output_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["works"] == "false"
    assert row["failure_category"] == "schema_validation"
    assert row["failed_stage"] == "validation"
    assert row["validation_error_count"] == "1"
    assert json.loads(row["validation_error_paths_json"]) == ["fg3_pct"]
    assert "schema validation" in row["evaluation"]
    assert "SchemaDriftError" in row["evaluation"]
    assert "fg3_pct" in row["evaluation"]
    assert row["traceback_tail"]
    assert row["traceback_hash"]


def test_probe_csv_http_failure_includes_http_diagnostics(tmp_path: Path) -> None:
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
                "attributes": {
                    "exception.type": "InvalidTeam",
                    "exception.message": "Invalid team ATL",
                },
            },
        ],
    }
    summary = _summarize_debug_events(debug, endpoint_name="team_roster")
    evaluated = _with_evaluation(
        {
            "endpoint": "team_roster",
            "params": {"team_abbreviation": "ATL", "season_end_year": 2024},
            "ok": False,
            "error_type": "InvalidTeam",
            "error_message": "Invalid team ATL",
            **summary,
        }
    )
    row = _csv_row(evaluated)

    assert row["failure_category"] == "http_error"
    assert row["failed_stage"] == "http"
    assert row["http_status_code"] == "404"
    assert row["http_reason"] == "Not Found"
    assert row["redirect_count"] == "1"
    assert "failed during http" in row["evaluation"]
    assert "HTTP 404 Not Found" in row["evaluation"]


def test_probe_csv_table_resolution_failure_includes_table_diagnostics(tmp_path: Path) -> None:
    debug = {
        "trace_id": "trace-table",
        "duration_ms": 6.0,
        "status": {"code": "error", "error_type": "RuntimeError", "error_message": "no table found"},
        "metrics": {},
        "stage_counts": {"table_resolution": 2},
        "events": [
            {
                "stage": "table_resolution",
                "event": "table_id_lookup",
                "status": "ok",
                "attributes": {
                    "selector": "table[@id='missing_table']",
                    "matched": False,
                    "match_count": 0,
                },
            },
            {
                "stage": "table_resolution",
                "event": "no_table_found",
                "status": "error",
                "attributes": {"returned_row_count": 0},
            },
        ],
    }
    summary = _summarize_debug_events(debug, endpoint_name="team_roster")
    evaluated = _with_evaluation(
        {
            "endpoint": "team_roster",
            "params": {"team_abbreviation": "BOS", "season_end_year": 2024},
            "ok": False,
            "error_type": "RuntimeError",
            "error_message": "no table found",
            **summary,
        }
    )
    row = _csv_row(evaluated)

    assert row["failure_category"] == "parse_error"
    assert row["failed_stage"] == "table_resolution"
    assert json.loads(row["candidate_table_ids_json"]) == ["missing_table"]
    assert "parsing or resolving Basketball-Reference tables" in row["evaluation"]
    assert "candidates=" in row["evaluation"]


def test_probe_csv_missing_fixture_params_does_not_crash(tmp_path: Path) -> None:
    output_path = tmp_path / "probe.csv"
    result = {
        "endpoint": "unknown_endpoint",
        "params": None,
        "ok": False,
        "error_type": "MissingSampleParams",
        "error_message": "No fixture-manifest case available for this endpoint.",
        **_default_enrichment(endpoint_name="unknown_endpoint"),
        "sample_params_source": "missing",
    }

    write_probe_csv_report([result], output_path)

    rows = _read_csv_rows(output_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["works"] == "false"
    assert row["failure_category"] == "missing_sample_params"
    assert row["sample_params_source"] == "missing"
    assert row["event_count"] == "0"
    assert "source=missing" in row["evaluation"]


def test_probe_csv_serializes_nested_fields_as_json(tmp_path: Path) -> None:
    output_path = tmp_path / "probe.csv"
    params = {"filters": {"teams": ["BOS", "ATL"]}, "season_end_year": 2024}
    metrics = {"debug.enabled": True, "validation.rows": 3}
    stage_counts = {"http": 2, "runner": 5, "validation": 1}
    result = {
        **_default_enrichment(endpoint_name="league_player_stats"),
        "endpoint": "league_player_stats",
        "params": params,
        "ok": True,
        "status_code": "ok",
        "debug_status": "ok",
        "row_count": 3,
        "metrics": metrics,
        "stage_counts": stage_counts,
        "required_params_json": ["season_end_year"],
        "candidate_table_ids_json": ["stats"],
        "validation_error_paths_json": [],
        "columns_json": ["player", "pts"],
        "first_row_preview_json": {"player": "Tatum", "pts": 26.9},
    }

    write_probe_csv_report([result], output_path)

    row = _read_csv_rows(output_path)[0]
    assert json.loads(row["params_json"]) == params
    assert json.loads(row["metrics_json"]) == metrics
    assert json.loads(row["stage_counts_json"]) == stage_counts
    assert json.loads(row["required_params_json"]) == ["season_end_year"]
    assert json.loads(row["candidate_table_ids_json"]) == ["stats"]
    assert json.loads(row["columns_json"]) == ["player", "pts"]
    assert json.loads(row["first_row_preview_json"]) == {"player": "Tatum", "pts": 26.9}


def test_probe_csv_trace_file_fields_populated_when_trace_exists(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.json"
    trace_path.write_text('{"debug": true}', encoding="utf-8")
    debug = _successful_debug_envelope(trace_log_path=str(trace_path))
    summary = _summarize_debug_events(debug, endpoint_name="team_roster", trace_log_path=str(trace_path))
    evaluated = _with_evaluation(
        {
            "endpoint": "team_roster",
            "params": {"team_abbreviation": "BOS", "season_end_year": 2024},
            "ok": True,
            **summary,
        }
    )
    row = _csv_row(evaluated)

    assert row["trace_log_exists"] == "true"
    assert row["trace_log_size_bytes"] == str(trace_path.stat().st_size)
    assert row["trace_log_path"] == str(trace_path)
