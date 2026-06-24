"""Workflow execution compatibility tests."""

from __future__ import annotations

from typing import Any

import pytest
from courtside_data.client._runner import _run_endpoint
from courtside_data.data import Team
from courtside_data.parsing.custom import CustomEndpointHandler
from courtside_data.parsing.workflows import CallCustomHandlerStep, WorkflowExecutionContext

from tests.fixture_manifest import case_for


def test_workflow_endpoint_dispatches_through_compatibility_step(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_execute(self: CallCustomHandlerStep, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        calls.append((context.endpoint_name, dict(context.params)))
        context.scratch["rows"] = []
        return []

    monkeypatch.setattr(CallCustomHandlerStep, "execute", fake_execute)

    result = _run_endpoint(
        "play_by_play",
        {"home_team": Team.ATLANTA_HAWKS, "day": 1, "month": 1, "year": 2024},
    )

    assert result == []
    assert calls == [
        (
            "play_by_play",
            {"home_team": Team.ATLANTA_HAWKS, "day": 1, "month": 1, "year": 2024},
        )
    ]


@pytest.mark.parametrize(
    ("endpoint_name", "params"),
    [
        ("players_season_totals", {"season_end_year": 2002}),
        ("players_advanced_season_totals", {"season_end_year": 1985, "include_combined_values": False}),
        (
            "regular_season_player_box_scores",
            {"player_identifier": "westbru01", "season_end_year": 2020, "include_inactive_games": False},
        ),
        (
            "playoff_player_box_scores",
            {"player_identifier": "westbru01", "season_end_year": 2020, "include_inactive_games": False},
        ),
        ("season_awards_voting", {"season_end_year": 2025, "award": "mvp"}),
        ("playoff_bracket", {"season_end_year": 2024}),
        ("friv_7_game_playoff_series_outcomes_team_is_down", {}),
        ("friv_7_game_playoff_series_outcomes_team_is_tied", {}),
        ("friv_7_game_playoff_series_outcomes_team_is_up", {}),
    ],
)
def test_single_page_workflow_endpoints_do_not_call_custom_handler(
    endpoint_name: str,
    params: dict[str, Any],
    monkeypatch,
    make_offline_client,
) -> None:
    def fail_if_called(self: CustomEndpointHandler, **kwargs: Any) -> list[dict[str, Any]]:
        raise AssertionError(f"CustomEndpointHandler.{endpoint_name} was called with {kwargs}")

    monkeypatch.setattr(CustomEndpointHandler, endpoint_name, fail_if_called)
    case = case_for(endpoint_name, **params)
    assert case is not None
    client = make_offline_client(case)

    result = getattr(client, endpoint_name)(**params)

    assert result
