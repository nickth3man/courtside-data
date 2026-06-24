"""Offline tests for multi-fetch custom endpoints (former e2e coverage).

Exercises ``season_schedule``, ``play_by_play``, ``team_box_scores``,
``standings_by_date``, and ``search`` through the fixture replay transport
so the multi-request orchestration is validated without live network calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from courtside_data.client.courtside_client import CourtsideClient
from courtside_data.data import TEAM_ABBREVIATIONS_TO_TEAM, PeriodType
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import InvalidDate
from courtside_data.parsing.custom import CustomEndpointHandler
from pydantic import BaseModel

from tests.fixture_manifest import MULTI_REQUEST_CASES, Case, case_for
from tests.fixture_transport import FixtureTransport, build_service

# Manifest cases with known fixture gaps — tracked separately until fixtures land.
MULTI_REQUEST_EXCLUDED_CASE_IDS: frozenset[str] = frozenset({"search-jaebaebae"})

MULTI_REQUEST_OFFLINE_CASES: list[Case] = [
    case for case in MULTI_REQUEST_CASES if case.id not in MULTI_REQUEST_EXCLUDED_CASE_IDS
]


def _resolved_params(case: Case) -> dict:
    params = dict(case.params)
    if case.endpoint_name == "play_by_play":
        abbr = params.pop("home_team")
        params["home_team"] = TEAM_ABBREVIATIONS_TO_TEAM[abbr]
    if case.endpoint_name == "standings_by_date":
        params.pop("conference", None)
    return params


def _season_schedule_case() -> Case:
    case = case_for("season_schedule", season_end_year=1980)
    assert case is not None
    return case


def _team_box_scores_case() -> Case:
    case = case_for("team_box_scores", day=1, month=1, year=2001)
    assert case is not None
    return case


def _serialized_rows(rows: list[BaseModel]) -> list[dict[str, Any]]:
    return [row.model_dump(mode="json") for row in rows]


@pytest.mark.parametrize("case", MULTI_REQUEST_OFFLINE_CASES, ids=[case.id for case in MULTI_REQUEST_OFFLINE_CASES])
def test_multi_request_endpoint_offline(case: Case, make_offline_client) -> None:
    client = make_offline_client(case)
    result = getattr(client, case.endpoint_name)(**_resolved_params(case))

    endpoint = ENDPOINTS[case.endpoint_name]
    row_model = endpoint.row_model
    assert row_model is not None, f"{case.id}: endpoint has no row_model"
    assert isinstance(result, list), f"{case.id}: expected list, got {type(result).__name__}"
    if case.id == "search-no-results":
        assert result == []
        return
    assert result, f"{case.id}: expected non-empty row list"
    assert all(isinstance(row, row_model) for row in result), (
        f"{case.id}: not all rows validated as {row_model.__name__}"
    )


def test_season_schedule_offline_output_matches_golden(make_offline_client) -> None:
    case = _season_schedule_case()
    client = make_offline_client(case)

    result = client.season_schedule(**case.params)

    golden_path = Path(__file__).parent / "golden" / f"{case.id}.json"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert _serialized_rows(result) == expected


def test_season_schedule_native_path_does_not_call_custom_handler(monkeypatch, make_offline_client) -> None:
    def fail_if_called(self: CustomEndpointHandler, season_end_year: int) -> list[dict]:
        raise AssertionError(f"CustomEndpointHandler.season_schedule was called for {season_end_year}")

    monkeypatch.setattr(CustomEndpointHandler, "season_schedule", fail_if_called)
    case = _season_schedule_case()
    client = make_offline_client(case)

    result = client.season_schedule(**case.params)

    assert result


def test_team_box_scores_offline_output_matches_legacy_custom_handler(make_offline_client) -> None:
    case = _team_box_scores_case()
    client = make_offline_client(case)
    legacy_service = build_service(FixtureTransport(case.url_to_file))
    legacy_rows = CustomEndpointHandler(legacy_service).team_box_scores(**case.params)

    result = client.team_box_scores(**case.params, raw=True)

    assert result == legacy_rows


def test_team_box_scores_native_path_does_not_call_custom_handler(monkeypatch, make_offline_client) -> None:
    def fail_if_called(self: CustomEndpointHandler, day: int, month: int, year: int) -> list[dict]:
        raise AssertionError(f"CustomEndpointHandler.team_box_scores was called for {year}-{month}-{day}")

    monkeypatch.setattr(CustomEndpointHandler, "team_box_scores", fail_if_called)
    case = _team_box_scores_case()
    client = make_offline_client(case)

    result = client.team_box_scores(**case.params)

    assert result


def test_team_box_scores_empty_daily_index_raises_invalid_date() -> None:
    params = {"day": 4, "month": 7, "year": 2024}
    fixture = Path(__file__).parent.parent / "raw" / "team_box_scores" / "2024_07_04" / "index.html"
    assert fixture.is_file()
    service = build_service(
        FixtureTransport(
            {
                "https://www.basketball-reference.com/boxscores/?day=4&month=7&year=2024": fixture,
            }
        )
    )
    client = CourtsideClient(service=service)

    with pytest.raises(InvalidDate):
        client.team_box_scores(**params)


def test_play_by_play_overtime_last_period(make_offline_client) -> None:
    """Regression for e2e overtime semantics: final play tagged as OT period 1."""
    overtime_endings: list[str] = []
    for case in MULTI_REQUEST_OFFLINE_CASES:
        if case.endpoint_name != "play_by_play":
            continue
        client = make_offline_client(case)
        plays = client.play_by_play(**_resolved_params(case))
        last = plays[-1]
        if last.period_type == PeriodType.OVERTIME:
            assert last.period == 1
            overtime_endings.append(case.id)

    assert overtime_endings, (
        "Expected at least one play_by_play fixture whose final play is overtime period 1; "
        f"checked {[c.id for c in MULTI_REQUEST_OFFLINE_CASES if c.endpoint_name == 'play_by_play']}"
    )
