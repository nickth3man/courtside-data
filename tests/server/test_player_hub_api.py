from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from courtside_data.errors import (
    InvalidPlayer,
    InvalidPlayerAndSeason,
    InvalidSearch,
    InvalidSeason,
    RateLimitJailed,
    SchemaDriftError,
)
from courtside_data.server.app import create_app
from fastapi import FastAPI
from fastapi.testclient import TestClient

pytestmark = pytest.mark.enable_socket


def _client() -> TestClient:
    return TestClient(create_app(transport="fixture"))


class _RaisingService:
    """Stand-in service that raises a fixed exception from every method."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def search_players(self, term: str) -> list[dict[str, Any]]:
        raise self._exc

    def summary(self, player_identifier: str) -> dict[str, Any]:
        raise self._exc

    def rows_for_dataset(self, dataset_id: str, params: dict[str, Any]) -> dict[str, Any]:
        raise self._exc

    def csv_for_dataset(self, dataset_id: str, params: dict[str, Any]) -> str:
        raise self._exc


def _client_raising(exc: Exception) -> TestClient:
    app: FastAPI = create_app(transport="fixture")
    app.state.player_hub_service = _RaisingService(exc)
    return TestClient(app)


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

    # AC-002: a term shorter than two characters is rejected as invalid_search (400).
    too_short = client.get("/api/players/search", params={"term": "a"})
    assert too_short.status_code == 400
    assert too_short.json()["detail"]["code"] == "invalid_search"

    response = client.get("/api/players/search", params={"term": "kobe"})
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert any(result["identifier"] == "bryanko01" for result in payload)

    # AC-003: a term that matches nobody is a valid empty-list response, not an error.
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


@pytest.mark.parametrize(
    ("exc", "expected_status", "expected_code"),
    [
        # §4.3 exception -> HTTP mapping table.
        (InvalidSearch("ab"), 400, "invalid_search"),
        (InvalidPlayer("x"), 404, "invalid_player"),
        (InvalidPlayerAndSeason("x", 2020), 404, "invalid_player"),
        (InvalidSeason(2020), 404, "invalid_season"),
        (
            SchemaDriftError(
                "player_career_stats",
                "https://www.basketball-reference.com/players/j/jamesle01.html",
                [{"type": "missing", "loc": ("season",), "msg": "Field required"}],
            ),
            500,
            "schema_drift",
        ),
        (RateLimitJailed(600.0), 429, "rate_limit_jailed"),
        (RuntimeError("boom"), 500, "internal_error"),
    ],
)
def test_exception_to_http_mapping(exc: Exception, expected_status: int, expected_code: str) -> None:
    # AC-010 / AC-011 plus the status-code contract for every domain exception in §4.3.
    response = _client_raising(exc).get("/api/players/x/summary")

    assert response.status_code == expected_status
    assert response.json()["detail"]["code"] == expected_code


def test_server_runtime_code_does_not_import_tests_package() -> None:
    server_root = Path(__file__).resolve().parents[2] / "courtside_data" / "server"
    for path in server_root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "from tests" not in source
        assert "import tests" not in source
