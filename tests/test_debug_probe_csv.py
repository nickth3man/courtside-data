from __future__ import annotations

import csv
import json
from pathlib import Path

from courtside_data.debug.probe import (
    _csv_row,
    _default_enrichment,
    _infer_output_type,
    _preview_result,
    _sample_params_per_endpoint,
    _summarize_debug_events,
    _summarize_report,
    _with_evaluation,
    write_probe_csv_report,
)
from courtside_data.debug.probe.samples import _ENDPOINT_GROUPS
from courtside_data.endpoints import ENDPOINTS


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
            "event": "parsed_rows_summary",
            "status": "ok",
            "attributes": {
                "parser_name": "generic_table",
                "parsed_row_count": 17,
                "parsed_field_count": 3,
                "parsed_fields": ["player", "age", "pts"],
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
            "stage": "runner",
            "event": "row_model_pipeline_start",
            "status": "ok",
            "attributes": {"row_model": "TeamRosterRow", "raw_row_count": 17, "raw_requested": False},
        },
        {
            "stage": "validation",
            "event": "pydantic_validation_complete",
            "status": "ok",
            "attributes": {
                "validation_status": "passed",
                "row_model": "TeamRosterRow",
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
        "stage_counts": {"http": 2, "parse": 1, "validation": 1, "runner": 1},
        "spans": [
            {
                "span_id": "span-http",
                "stage": "http",
                "duration_ms": 1200.0,
            },
            {
                "span_id": "span-validation",
                "stage": "validation",
                "duration_ms": 45.2,
            },
        ],
        "events": events,
    }


def test_probe_csv_happy_path_marks_endpoint_working(tmp_path: Path) -> None:
    output_path = tmp_path / "reports" / "probe.csv"
    debug = _successful_debug_envelope()
    summary = _summarize_debug_events(
        debug, data=[{"player": "Tatum", "age": 26, "pts": 26.9}], endpoint_name="team_roster"
    )
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
    assert row["endpoint_domain"] == "teams"
    assert row["endpoint_kind"] == "generic_table"
    assert row["endpoint_legacy_kind"] == "generic"
    assert row["sample_params_source"] == "fixture_manifest"
    assert row["parser_name"] == "generic_table"
    assert row["model_name"] == "TeamRosterRow"
    assert row["selected_table_id"] == "roster"
    assert json.loads(row["candidate_table_ids_json"]) == ["roster"]
    assert row["raw_table_row_count"] == "17"
    assert row["raw_table_column_count"] == "3"
    assert json.loads(row["raw_columns_json"]) == ["player", "age", "pts"]
    assert row["output_field_count"] == "3"
    assert json.loads(row["output_fields_json"]) == ["age", "player", "pts"]
    assert row["validation_status"] == "passed"
    assert row["validation_error_count"] == "0"
    assert json.loads(row["validation_error_paths_json"]) == []
    assert row["output_type"] == "list[TeamRosterRow]"
    assert row["row_count"] == "1"
    assert row["event_count"] == "10"
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
                    "exception.stacktrace": 'Traceback (most recent call last):\n  File "x.py", line 1, in <module>\n    raise Error\nError\n',
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
    assert row["validation_status"] == "failed"
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


def test_validation_success_sets_explicit_zero_values() -> None:
    debug = _successful_debug_envelope()
    summary = _summarize_debug_events(
        debug, data=[{"player": "Tatum", "age": 26, "pts": 26.9}], endpoint_name="team_roster"
    )
    row = _csv_row({"endpoint": "team_roster", "ok": True, **summary})

    assert row["validation_status"] == "passed"
    assert row["validation_error_count"] == "0"
    assert json.loads(row["validation_error_paths_json"]) == []


def test_raw_columns_and_output_fields_are_separate() -> None:
    debug = _successful_debug_envelope()
    summary = _summarize_debug_events(
        debug,
        data=[{"player": "Tatum", "age": 26, "pts": 26.9}],
        endpoint_name="team_roster",
    )

    assert summary["raw_columns_json"] == ["player", "age", "pts"]
    assert summary["output_fields_json"] == ["age", "player", "pts"]
    assert summary["validated_fields_json"]
    assert "number" in summary["validated_fields_json"]


def test_row_filtering_computes_dropped_count() -> None:
    events = [
        {
            "stage": "parse",
            "event": "parsed_rows_summary",
            "status": "ok",
            "attributes": {
                "parser_name": "generic_table",
                "parsed_row_count": 20,
                "parsed_field_count": 3,
                "parsed_fields": ["player", "age", "pts"],
            },
        },
        {
            "stage": "runner",
            "event": "row_model_pipeline_start",
            "status": "ok",
            "attributes": {"row_model": "TeamRosterRow", "raw_row_count": 20},
        },
        {
            "stage": "validation",
            "event": "rows_filtered",
            "status": "ok",
            "attributes": {
                "dropped_row_count": 3,
                "dropped_row_reason_counts": {"repeated_header": 2, "parser_excluded": 1},
            },
        },
        {
            "stage": "validation",
            "event": "pydantic_validation_complete",
            "status": "ok",
            "attributes": {
                "validation_status": "passed",
                "row_model": "TeamRosterRow",
                "validated_row_count": 17,
                "row_count": 17,
                "validation_error_count": 0,
                "validation_error_paths": [],
            },
        },
    ]
    debug = {
        "trace_id": "trace-rows",
        "duration_ms": 1.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {},
        "stage_counts": {},
        "events": events,
    }
    summary = _summarize_debug_events(debug, data=[{}] * 17, endpoint_name="team_roster")

    assert summary["parsed_row_count"] == 20
    assert summary["raw_row_count"] == 20
    assert summary["validated_row_count"] == 17
    assert summary["output_row_count"] == 17
    assert summary["dropped_row_count"] == 3
    assert summary["dropped_row_reason_counts_json"] == {"repeated_header": 2, "parser_excluded": 1}


def test_metrics_includes_span_timing() -> None:
    debug = _successful_debug_envelope()
    summary = _summarize_debug_events(debug, endpoint_name="team_roster")

    assert summary["metrics"]["debug.enabled"] is True
    assert summary["metrics"]["duration_ms.http"] == 1200.0
    assert summary["metrics"]["duration_ms.validation"] == 45.2
    assert summary["metrics"]["duration_ms.total"] == 12.5
    assert summary["metrics"]["response_bytes"] == 120_000


def test_output_type_inferred_from_data_and_model() -> None:
    assert _infer_output_type([{"a": 1}], "TeamRosterRow") == "list[TeamRosterRow]"
    assert _infer_output_type([{"a": 1}], None) == "list"
    assert _infer_output_type({"rows": []}, None) == "dict"


def test_custom_endpoint_has_no_raw_table_columns() -> None:
    debug = {
        "trace_id": "trace-custom",
        "duration_ms": 5.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {"debug.enabled": True},
        "stage_counts": {"endpoint": 2},
        "events": [
            {
                "stage": "endpoint",
                "event": "run_endpoint_start",
                "status": "ok",
                "attributes": {"row_model": "PlayByPlayRow", "custom": True},
            },
            {
                "stage": "endpoint",
                "event": "custom_service_dispatch",
                "status": "ok",
                "attributes": {"method": "play_by_play"},
            },
        ],
    }
    summary = _summarize_debug_events(
        debug,
        data=[{"period": 1, "description": "made shot"}],
        endpoint_name="play_by_play",
    )

    assert summary["parser_name"] == "custom"
    assert summary["raw_columns_json"] == []
    assert summary["raw_column_count"] is None
    assert summary["selected_table_id"] is None
    assert summary["parsed_event_count"] is None


def test_probe_grouping_comes_from_endpoint_metadata() -> None:
    groups_from_metadata = {
        name: endpoint.metadata.domain.value for name, endpoint in ENDPOINTS.items() if endpoint.metadata is not None
    }

    assert groups_from_metadata == _ENDPOINT_GROUPS


def test_custom_module_endpoint_uses_metadata_domain_not_custom_group() -> None:
    summary = _summarize_debug_events(
        {
            "trace_id": "trace-pbp-domain",
            "duration_ms": 1.0,
            "status": {"code": "ok", "error_type": None, "error_message": None},
            "metrics": {},
            "stage_counts": {},
            "events": [],
        },
        endpoint_name="play_by_play",
    )

    assert summary["endpoint_group"] == "games"
    assert summary["endpoint_domain"] == "games"
    assert summary["endpoint_kind"] == "workflow"
    assert summary["endpoint_legacy_kind"] == "custom"
    assert summary["endpoint_group"] != "custom"


def test_first_row_preview_truncation_flags() -> None:
    row = {f"field_{index}": "x" * 120 for index in range(15)}
    preview, truncated, preview_count, total_count = _preview_result(row)

    assert truncated is True
    assert preview_count == 8
    assert total_count == 15
    assert len(preview) == 8
    assert all(str(value).endswith("...") for value in preview.values())


def test_summarize_report_computes_rate_limit_and_trace_aggregates(tmp_path: Path) -> None:
    trace_a = tmp_path / "a.json"
    trace_b = tmp_path / "b.json"
    trace_a.write_text("a" * 10, encoding="utf-8")
    trace_b.write_text("b" * 20, encoding="utf-8")
    results = [
        {
            "endpoint": "team_roster",
            "elapsed_ms": 100.0,
            "rate_limit_wait_ms": 250.0,
            "trace_log_path": str(trace_a),
            "trace_log_size_bytes": trace_a.stat().st_size,
            "metrics": {"duration_ms.http": 80.0, "duration_ms.validation": 10.0},
        },
        {
            "endpoint": "play_by_play",
            "elapsed_ms": 500.0,
            "rate_limit_wait_ms": 750.0,
            "trace_log_path": str(trace_b),
            "trace_log_size_bytes": trace_b.stat().st_size,
            "metrics": {"duration_ms.http": 400.0},
        },
    ]

    summary = _summarize_report(results)

    assert summary["total_rate_limit_wait_ms"] == 1000.0
    assert summary["average_rate_limit_wait_ms"] == 500.0
    assert summary["max_rate_limit_wait_ms"] == 750.0
    assert summary["slowest_endpoint"] == "play_by_play"
    assert summary["slowest_endpoint_elapsed_ms"] == 500.0
    assert summary["slowest_stage"] == "http"
    assert summary["total_trace_log_size_bytes"] == trace_a.stat().st_size + trace_b.stat().st_size
    assert summary["largest_trace_log_path"] == str(trace_b)
    assert summary["largest_trace_log_size_bytes"] == trace_b.stat().st_size


def test_status_code_is_deprecated_alias_for_debug_status() -> None:
    debug = _successful_debug_envelope()
    summary = _summarize_debug_events(debug, endpoint_name="team_roster")
    evaluated = _with_evaluation({"endpoint": "team_roster", "ok": True, **summary})
    row = _csv_row(evaluated)

    assert row["debug_status"] == "ok"
    assert row["status_code"] == "ok"
    assert row["http_status_code"] == "200"


def test_probe_csv_data_quality_on_success(tmp_path) -> None:
    output_path = tmp_path / "probe.csv"
    result = {
        "endpoint": "league_per_game_stats",
        "ok": True,
        "dropped_row_count": 65,
        "dropped_row_reason_counts_json": {"repeated_header": 40, "aggregate_row": 25},
        "metrics": {"duration_ms.http_fetch": 1200.0, "duration_ms.row_parse": 45.0},
    }
    write_probe_csv_report([_with_evaluation(result)], output_path)
    row = _read_csv_rows(output_path)[0]
    assert row["data_quality_status"] in {"warnings", "clean"}
    assert row["expected_drop_count"] == "65"
    assert float(row["drop_rate"]) == 0.0


def test_stage_timing_metrics_exposed_in_csv() -> None:
    debug = _successful_debug_envelope()
    debug["spans"].extend(
        [
            {"span_id": "span-fetch", "stage": "http_fetch", "duration_ms": 900.0},
            {"span_id": "span-parse", "stage": "row_parse", "duration_ms": 120.0},
        ]
    )
    summary = _summarize_debug_events(debug, endpoint_name="team_injury_report")
    assert summary["metrics"]["duration_ms.http_fetch"] == 900.0
    assert summary["metrics"]["duration_ms.row_parse"] == 120.0


def test_zero_values_not_serialized_as_blank() -> None:
    debug = _successful_debug_envelope()
    summary = _summarize_debug_events(debug, endpoint_name="team_roster")
    row = _csv_row({"endpoint": "team_roster", "ok": True, **summary})

    assert row["validation_error_count"] == "0"
    assert row["redirect_count"] == "0"
    assert row["warning_count"] == "0"
    assert row["error_event_count"] == "0"


# ---------------------------------------------------------------------------
# Live probe sampler tests (live-audit overrides vs fixture manifest fallback)
# ---------------------------------------------------------------------------


def test_live_probe_sampler_uses_recent_overrides_for_known_noisy_endpoints() -> None:
    """Known historical fixture cases must not be returned for overridden endpoints."""
    samples = _sample_params_per_endpoint()

    # rookie_stats used 1980 (no team column) in historical fixture
    rs = samples["rookie_stats"]
    assert rs.params == {"season_end_year": 2024}
    assert rs.source == "live_audit"
    assert rs.case_id == "live_audit:rookie_stats"
    assert rs.params != {"season_end_year": 1980}

    # draft_picks used 1965 (historical team names causing invalid_team_value)
    dp = samples["draft_picks"]
    assert dp.params == {"season_end_year": 2024}
    assert dp.source == "live_audit"
    assert dp.case_id == "live_audit:draft_picks"
    assert dp.params != {"season_end_year": 1965}


def test_live_probe_sampler_overrides_historical_league_and_schedule_endpoints() -> None:
    samples = _sample_params_per_endpoint()

    for ep in ("league_per_game_stats", "league_totals", "season_schedule", "season_awards"):
        s = samples[ep]
        assert s.params == {"season_end_year": 2024}, f"{ep} should use live 2024"
        assert s.source == "live_audit"
        assert s.case_id == f"live_audit:{ep}"

    # team_and_opponent (required team + year) used 1974 historically
    tao = samples["team_and_opponent"]
    assert tao.params == {"team_abbreviation": "BOS", "season_end_year": 2024}
    assert tao.source == "live_audit"


def test_live_probe_sampler_falls_back_to_fixture_manifest_for_non_overridden() -> None:
    """Endpoints without a live override must keep their manifest-derived sample."""
    samples = _sample_params_per_endpoint()

    # team_roster is not overridden; must come from fixture manifest (or empty)
    tr = samples.get("team_roster")
    assert tr is not None
    assert tr.source == "fixture_manifest"
    # case_id should look like a manifest id (contains endpoint or year), not live_audit
    assert tr.case_id is None or "live_audit" not in str(tr.case_id)

    # attendance likewise
    att = samples.get("attendance")
    assert att is not None
    assert att.source == "fixture_manifest"


def test_live_probe_sampler_metadata_distinguishes_sources() -> None:
    """sample_params_source in enrichment must reflect live vs manifest."""
    samples = _sample_params_per_endpoint()

    # overridden
    rs = samples["rookie_stats"]
    enrich = _default_enrichment(endpoint_name="rookie_stats", sample=rs)
    assert enrich["sample_params_source"] == "live_audit"
    assert enrich["sample_case_id"] == "live_audit:rookie_stats"

    # fallback
    tr = samples.get("team_roster")
    if tr and tr.source == "fixture_manifest":
        enrich = _default_enrichment(endpoint_name="team_roster", sample=tr)
        assert enrich["sample_params_source"] == "fixture_manifest"
