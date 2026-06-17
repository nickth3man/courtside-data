"""Offline tests for multi-fetch custom endpoints (former e2e coverage).

Exercises ``season_schedule``, ``play_by_play``, ``team_box_scores``,
``standings_by_date``, and ``search`` through the fixture replay transport
so the multi-request orchestration is validated without live network calls.
"""

from __future__ import annotations

import pytest
from courtside_data.data import TEAM_ABBREVIATIONS_TO_TEAM, PeriodType
from courtside_data.endpoints import ENDPOINTS

from tests.fixture_manifest import MULTI_REQUEST_CASES, Case

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
