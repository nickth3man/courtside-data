from __future__ import annotations

from pathlib import Path

import pytest
from courtside_data.server.app import create_app
from fastapi.testclient import TestClient

pytestmark = pytest.mark.enable_socket


def _client() -> TestClient:
    return TestClient(create_app(transport="fixture"))


def test_status_reports_fixture_mode() -> None:
    response = _client().get("/api/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["transport"] == "fixture"
    assert payload["endpoint_count"] >= 61
    assert payload["fixture_root_exists"] is True


def test_player_search_returns_json_objects_and_no_results_state() -> None:
    client = _client()

    response = client.get("/api/players/search", params={"term": "kobe"})
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert any(result["identifier"] == "bryanko01" for result in payload)

    no_results = client.get("/api/players/search", params={"term": "no_results"})
    assert no_results.status_code == 200
    assert no_results.json() == []


def test_player_summary_derives_season_and_embeds_career_rows() -> None:
    response = _client().get("/api/players/jamesle01/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["identifier"] == "jamesle01"
    assert payload["display_name"] == "LeBron James"
    assert payload["default_season"] == 2024
    assert 2024 in payload["available_seasons"]
    assert payload["career"]["dataset"] == "career"
    assert isinstance(payload["career"]["rows"], list)
    assert isinstance(payload["career"]["rows"][0], dict)
    assert payload["career"]["row_count"] == len(payload["career"]["rows"])
    assert "points_per_game" in payload["hero_stats"]


def test_player_scoped_datasets_load_for_fixture_player() -> None:
    client = _client()

    for dataset in (
        "career",
        "playoff-series",
        "adjusted-shooting",
        "derived-play-by-play",
        "game-highs",
        "all-star",
        "similarity",
        "salaries",
    ):
        response = client.get(f"/api/players/jamesle01/{dataset}")
        assert response.status_code == 200, dataset
        payload = response.json()
        assert payload["dataset"] == dataset
        assert payload["row_count"] == len(payload["rows"])
        assert isinstance(payload["rows"][0], dict)


def test_season_scoped_datasets_load_and_missing_fixture_maps_to_404() -> None:
    client = _client()

    for dataset in ("splits", "on-off", "shooting-breakdown"):
        response = client.get(f"/api/players/jamesle01/seasons/2024/{dataset}")
        assert response.status_code == 200, dataset
        assert response.json()["dataset"] == dataset

    playoff_games = client.get("/api/players/jamesle01/seasons/2023/playoff-games")
    assert playoff_games.status_code == 200
    assert playoff_games.json()["dataset"] == "playoff-games"

    missing = client.get("/api/players/jamesle01/seasons/2024/regular-games")
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "missing_fixture"


def test_csv_export_streams_rows_without_filesystem_output() -> None:
    response = _client().get("/api/players/jamesle01/export", params={"dataset": "career"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    assert "season,age,team_name_abbr" in response.text


def test_season_dataset_rejects_player_scoped_dataset() -> None:
    response = _client().get("/api/players/jamesle01/seasons/2024/career")

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "bad_request"


def test_server_runtime_code_does_not_import_tests_package() -> None:
    server_root = Path(__file__).resolve().parents[2] / "courtside_data" / "server"
    for path in server_root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "from tests" not in source
        assert "import tests" not in source
