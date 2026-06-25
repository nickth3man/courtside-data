"""Workflow execution compatibility tests."""

from __future__ import annotations

from typing import Any

import courtside_data.client._runner as runner
import pytest
from courtside_data.client._runner import _run_endpoint
from courtside_data.client._runtime._coerce import _coerce_params
from courtside_data.data import Team
from courtside_data.endpoints import ENDPOINTS, EndpointKind
from courtside_data.parsing.custom import CustomEndpointHandler
from courtside_data.parsing.generic import GenericEndpointHandler
from courtside_data.parsing.workflows import (
    CallCustomHandlerStep,
    WorkflowExecutionContext,
    is_native_workflow_endpoint,
)
from courtside_data.parsing.workflows._executor import _NATIVE_STEP_HANDLERS, NATIVE_WORKFLOW_ENDPOINTS

from tests.fixture_manifest import case_for
from tests.fixture_transport import FixtureTransport, build_service


def test_workflow_endpoint_uses_compatibility_step_when_not_native(monkeypatch) -> None:
    """A workflow endpoint not registered as native still runs via the compatibility step.

    Every registered workflow endpoint is now native, so to keep the
    compatibility fallback in ``WorkflowEndpointHandler.execute`` covered we
    force ``play_by_play`` down the non-native branch.
    """
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_execute(self: CallCustomHandlerStep, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        calls.append((context.endpoint_name, dict(context.params)))
        context.scratch["rows"] = []
        return []

    monkeypatch.setattr(CallCustomHandlerStep, "execute", fake_execute)
    monkeypatch.setattr(
        "courtside_data.parsing.workflows._executor.is_native_workflow_endpoint",
        lambda name: False,
    )

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


def test_workflow_param_coercion_is_metadata_driven(monkeypatch) -> None:
    """Workflow enum coercion must not depend on the retained compatibility handler."""
    monkeypatch.delattr(CustomEndpointHandler, "play_by_play")

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

    assert non_native == [], f"workflow endpoints still on the compatibility step: {non_native}"


def test_native_workflow_set_matches_workflow_endpoint_kind() -> None:
    """The native set must be exactly the registered workflow endpoints — no stale names."""
    assert set(NATIVE_WORKFLOW_ENDPOINTS) == set(_workflow_endpoint_names())


@pytest.mark.parametrize("name", sorted(NATIVE_WORKFLOW_ENDPOINTS))
def test_native_workflow_endpoint_has_a_handler_for_every_step(name: str) -> None:
    """Each native endpoint must supply a step handler for every declared workflow step."""
    endpoint = ENDPOINTS[name]
    assert endpoint.workflow is not None, f"{name} declares no workflow spec"
    handlers = _NATIVE_STEP_HANDLERS[name]

    missing = [step.id for step in endpoint.workflow.steps if step.id not in handlers]

    assert missing == [], f"{name}: workflow steps without a native handler: {missing}"


# (lookup params, client/legacy call params) for one representative case per
# newly-migrated workflow endpoint. play_by_play needs the typed ``Team`` enum.
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
def test_migrated_workflow_endpoint_matches_legacy_without_compatibility_step(
    name: str,
    lookup: dict[str, Any],
    call: dict[str, Any],
    monkeypatch,
    make_offline_client,
) -> None:
    """Native execution must reproduce the legacy handler output without the compatibility step."""
    case = case_for(name, **lookup)
    assert case is not None, f"missing fixture case for {name} {lookup}"

    # Capture the legacy bespoke-handler output before disabling the fallback.
    legacy_handler = CustomEndpointHandler(build_service(FixtureTransport(case.url_to_file)))
    legacy = getattr(legacy_handler, name)(**call)
    expected = legacy["players"] if name == "search" else legacy

    def fail(self: CallCustomHandlerStep, context: WorkflowExecutionContext) -> Any:
        raise AssertionError(f"compatibility step used for native endpoint {context.endpoint_name!r}")

    monkeypatch.setattr(CallCustomHandlerStep, "execute", fail)

    client = make_offline_client(case)
    native = getattr(client, name)(**call, raw=True)

    assert native == expected
    assert native, f"{name}: expected a non-empty result"
