from __future__ import annotations

import csv
import json
from pathlib import Path

from courtside_data.debug.probe import write_probe_csv_report


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def test_probe_csv_happy_path_marks_endpoint_working(tmp_path: Path) -> None:
    # Arrange
    output_path = tmp_path / "reports" / "probe.csv"
    result = {
        "endpoint": "team_roster",
        "params": {"season_end_year": 2024, "team_abbreviation": "BOS"},
        "ok": True,
        "status_code": "ok",
        "row_count": 17,
        "duration_ms": 12.5,
        "elapsed_ms": 13.0,
        "trace_id": "trace-1",
        "trace_log_path": "logs/team_roster.json",
        "stage_counts": {"runner": 4},
        "metrics": {"debug.enabled": True},
    }

    # Act
    write_probe_csv_report([result], output_path)

    # Assert
    rows = _read_csv_rows(output_path)
    assert len(rows) == 1
    assert rows[0]["endpoint"] == "team_roster"
    assert rows[0]["ok"] == "true"
    assert rows[0]["works"] == "true"
    assert rows[0]["failure_category"] == "none"
    assert rows[0]["evaluation"] == "Endpoint completed successfully with 17 rows."


def test_probe_csv_failure_path_includes_category_and_evaluation(tmp_path: Path) -> None:
    # Arrange
    output_path = tmp_path / "probe.csv"
    result = {
        "endpoint": "player_career_stats",
        "params": {"player_identifier": "jamesle01"},
        "ok": False,
        "error_type": "SchemaDriftError",
        "error_message": "Schema drift detected for endpoint 'player_career_stats': missing field/alias 'fg3_pct'",
        "elapsed_ms": 8.25,
    }

    # Act
    write_probe_csv_report([result], output_path)

    # Assert
    rows = _read_csv_rows(output_path)
    assert len(rows) == 1
    assert rows[0]["works"] == "false"
    assert rows[0]["failure_category"] == "schema_validation"
    assert "schema validation" in rows[0]["evaluation"]
    assert "SchemaDriftError" in rows[0]["evaluation"]
    assert "fg3_pct" in rows[0]["evaluation"]


def test_probe_csv_serializes_nested_fields_as_json(tmp_path: Path) -> None:
    # Arrange
    output_path = tmp_path / "probe.csv"
    params = {"filters": {"teams": ["BOS", "ATL"]}, "season_end_year": 2024}
    metrics = {"debug.enabled": True, "validation.rows": 3}
    stage_counts = {"http": 2, "runner": 5, "validation": 1}
    result = {
        "endpoint": "league_player_stats",
        "params": params,
        "ok": True,
        "status_code": "ok",
        "row_count": 3,
        "metrics": metrics,
        "stage_counts": stage_counts,
    }

    # Act
    write_probe_csv_report([result], output_path)

    # Assert
    row = _read_csv_rows(output_path)[0]
    assert json.loads(row["params_json"]) == params
    assert json.loads(row["metrics_json"]) == metrics
    assert json.loads(row["stage_counts_json"]) == stage_counts
