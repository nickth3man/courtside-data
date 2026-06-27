"""Workflow execution contract tests."""

from __future__ import annotations

from typing import Any

import courtside_data.client._runner as runner
import pytest
from courtside_data.client._runner import _run_endpoint
from courtside_data.client._runtime._coerce import _coerce_params
from courtside_data.domain import Team
from courtside_data.endpoints import ENDPOINTS, EndpointKind
from courtside_data.parsing.generic import GenericEndpointHandler
from courtside_data.parsing.workflows import (
    NATIVE_WORKFLOW_ENDPOINTS,
    WorkflowEndpointHandler,
    is_native_workflow_endpoint,
)
from courtside_data.parsing.workflows._executor import workflow_execution_bindings

from tests.fixture_manifest import case_for
from tests.fixture_transport import FixtureTransport, build_service


def test_workflow_endpoint_without_native_binding_raises_configuration_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "courtside_data.parsing.workflows._executor._WORKFLOW_BINDINGS",
        {},
    )

    with pytest.raises(ValueError, match="native execution binding"):
        WorkflowEndpointHandler(build_service(FixtureTransport({}))).execute(
            "play_by_play",
            ENDPOINTS["play_by_play"],
            {"home_team": Team.ATLANTA_HAWKS, "day": 1, "month": 1, "year": 2024},
        )


def test_workflow_param_coercion_is_metadata_driven() -> None:
    params = _coerce_params("play_by_play", {"home_team": "ATL", "day": 1, "month": 1, "year": 2024})

    assert params["home_team"] is Team.ATLANTA_HAWKS


def test_generic_table_endpoint_dispatches_to_generic_handler(monkeypatch) -> None:
    calls: list[tuple[str | None, dict[str, Any]]] = []

    def fake_fetch_table(
        self: GenericEndpointHandler,
        endpoint,
        *,
        endpoint_name: str | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        calls.append((endpoint_name, params))
        return [{"name": "stub"}]

    def fail_workflow(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("generic-table endpoint dispatched to workflow executor")

    def execute_service_only(*, service_call, **kwargs: Any) -> Any:
        return service_call()

    monkeypatch.setattr(GenericEndpointHandler, "fetch_table", fake_fetch_table)
    monkeypatch.setattr(runner, "execute_workflow", fail_workflow)
    monkeypatch.setattr(runner, "_execute", execute_service_only)

    result = _run_endpoint("team_roster", {"team_abbreviation": "BOS", "season_end_year": 2024})

    assert result == [{"name": "stub"}]
    assert calls == [("team_roster", {"team_abbreviation": "BOS", "season_end_year": 2024})]


@pytest.mark.parametrize(
    ("endpoint_name", "params"),
    [
        ("box_score_player_basic", {"game_id": "201701010ATL"}),
        ("box_score_game_info", {"game_id": "201701010ATL"}),
        ("box_score_player_advanced", {"game_id": "201701010ATL"}),
        ("box_score_line_score", {"game_id": "201701010ATL"}),
        ("box_score_player_quarter_splits", {"game_id": "201701010ATL", "period": "q1"}),
        ("box_score_team_four_factors", {"game_id": "201701010ATL"}),
        ("players_season_totals", {"season_end_year": 2002, "include_combined_values": False}),
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
def test_single_page_workflow_endpoints_execute_from_bindings(
    endpoint_name: str,
    params: dict[str, Any],
    make_offline_client,
) -> None:
    case = case_for(endpoint_name, **params)
    assert case is not None
    client = make_offline_client(case)

    result = getattr(client, endpoint_name)(**params)

    assert result


def _workflow_endpoint_names() -> list[str]:
    return [
        name
        for name, endpoint in ENDPOINTS.items()
        if endpoint.metadata is not None and endpoint.metadata.kind is EndpointKind.WORKFLOW
    ]


def test_every_workflow_endpoint_executes_natively() -> None:
    """Every ``EndpointKind.WORKFLOW`` endpoint must run through native steps."""
    workflow_endpoints = _workflow_endpoint_names()
    assert workflow_endpoints, "expected at least one workflow endpoint"

    non_native = sorted(name for name in workflow_endpoints if not is_native_workflow_endpoint(name))

    assert non_native == [], f"workflow endpoints without native bindings: {non_native}"


def test_native_workflow_set_matches_workflow_endpoint_kind() -> None:
    """The native set must be exactly the registered workflow endpoints — no stale names."""
    assert set(NATIVE_WORKFLOW_ENDPOINTS) == set(_workflow_endpoint_names())


@pytest.mark.parametrize("name", sorted(NATIVE_WORKFLOW_ENDPOINTS))
def test_native_workflow_endpoint_has_exact_binding_for_declared_steps(name: str) -> None:
    """Each native endpoint binding must exactly match the declared workflow spec."""
    endpoint = ENDPOINTS[name]
    assert endpoint.workflow is not None, f"{name} declares no workflow spec"
    binding = workflow_execution_bindings()[name]

    declared = {step.id for step in endpoint.workflow.steps}
    bound = set(binding.step_handlers)

    assert binding.endpoint_name == name
    assert bound == declared
    assert binding.result == endpoint.workflow.result


# (lookup params, client call params) for one representative case per
# workflow endpoint family. play_by_play needs the typed ``Team`` enum.
_MIGRATED_ENDPOINT_CASES = [
    ("player_box_scores", {"year": 2001, "month": 1, "day": 1}, {"year": 2001, "month": 1, "day": 1}),
    (
        "play_by_play",
        {"home_team": "ATL", "day": 1, "month": 1, "year": 2017},
        {"home_team": Team.ATLANTA_HAWKS, "day": 1, "month": 1, "year": 2017},
    ),
    ("standings", {"season_end_year": 2024}, {"season_end_year": 2024}),
    ("standings_by_date", {"season_end_year": 2018}, {"season_end_year": 2018}),
    ("search", {"term": "kobe"}, {"term": "kobe"}),
]


@pytest.mark.parametrize(
    ("name", "lookup", "call"),
    _MIGRATED_ENDPOINT_CASES,
    ids=[entry[0] for entry in _MIGRATED_ENDPOINT_CASES],
)
def test_representative_workflow_endpoint_executes_from_fixture(
    name: str,
    lookup: dict[str, Any],
    call: dict[str, Any],
    make_offline_client,
) -> None:
    case = case_for(name, **lookup)
    assert case is not None, f"missing fixture case for {name} {lookup}"

    client = make_offline_client(case)
    native = getattr(client, name)(**call, raw=True)

    assert native, f"{name}: expected a non-empty result"
