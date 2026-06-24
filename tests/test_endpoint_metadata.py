"""Contract tests for the endpoint metadata backfill."""

from __future__ import annotations

import pytest
from courtside_data.endpoints import ENDPOINTS, EndpointDomain, EndpointFeature, EndpointKind
from courtside_data.endpoints._custom import CUSTOM_ENDPOINTS
from courtside_data.endpoints._draft_awards_leaders import DRAFT_AWARDS_LEADERS_ENDPOINTS
from courtside_data.endpoints._league import LEAGUE_ENDPOINTS
from courtside_data.endpoints._players import PLAYER_ENDPOINTS
from courtside_data.endpoints._playoffs import PLAYOFF_ENDPOINTS
from courtside_data.endpoints._teams import TEAM_ENDPOINTS

_FIELD_FEATURES = {
    "commented_table_id": EndpointFeature.COMMENTED_TABLE,
    "fallback_table_ids": EndpointFeature.FALLBACK_TABLE_IDS,
    "transaction_list_fallback": EndpointFeature.TRANSACTION_LIST_FALLBACK,
    "exclude_summary_rows": EndpointFeature.EXCLUDE_SUMMARY_ROWS,
    "use_header_fallback": EndpointFeature.HEADER_FALLBACK,
    "value_column": EndpointFeature.VALUE_COLUMN,
    "projection": EndpointFeature.PROJECTION,
}

_EXPECTED_DOMAINS = {
    **dict.fromkeys(LEAGUE_ENDPOINTS, EndpointDomain.LEAGUE),
    **dict.fromkeys(PLAYOFF_ENDPOINTS, EndpointDomain.PLAYOFFS),
    **dict.fromkeys(DRAFT_AWARDS_LEADERS_ENDPOINTS, EndpointDomain.DRAFT_AWARDS_LEADERS),
    **dict.fromkeys(PLAYER_ENDPOINTS, EndpointDomain.PLAYERS),
    **dict.fromkeys(TEAM_ENDPOINTS, EndpointDomain.TEAMS),
    **dict.fromkeys(CUSTOM_ENDPOINTS, EndpointDomain.GAMES),
}


def test_every_endpoint_has_metadata() -> None:
    missing = [name for name, endpoint in ENDPOINTS.items() if endpoint.metadata is None]
    assert not missing


@pytest.mark.parametrize("name", ENDPOINTS)
def test_metadata_kind_matches_custom_flag(name: str) -> None:
    endpoint = ENDPOINTS[name]
    assert endpoint.metadata is not None
    expected = EndpointKind.WORKFLOW if endpoint.custom else EndpointKind.GENERIC_TABLE
    assert endpoint.metadata.kind is expected


@pytest.mark.parametrize("name", ENDPOINTS)
def test_workflow_endpoints_declare_workflow_spec(name: str) -> None:
    endpoint = ENDPOINTS[name]
    assert endpoint.metadata is not None
    if endpoint.metadata.kind is EndpointKind.WORKFLOW:
        assert endpoint.workflow is not None


@pytest.mark.parametrize("name", ENDPOINTS)
def test_generic_table_endpoints_do_not_declare_workflow_spec(name: str) -> None:
    endpoint = ENDPOINTS[name]
    assert endpoint.metadata is not None
    if endpoint.metadata.kind is EndpointKind.GENERIC_TABLE:
        assert endpoint.workflow is None


@pytest.mark.parametrize("name", ENDPOINTS)
def test_workflow_step_ids_are_unique_per_endpoint(name: str) -> None:
    endpoint = ENDPOINTS[name]
    if endpoint.workflow is None:
        return

    step_ids = [step.id for step in endpoint.workflow.steps]
    assert len(step_ids) == len(set(step_ids))


@pytest.mark.parametrize("name", ENDPOINTS)
def test_workflow_step_inputs_outputs_are_stable_strings(name: str) -> None:
    endpoint = ENDPOINTS[name]
    if endpoint.workflow is None:
        return

    for step in endpoint.workflow.steps:
        assert isinstance(step.inputs, tuple)
        assert isinstance(step.outputs, tuple)
        assert all(isinstance(value, str) for value in step.inputs)
        assert all(isinstance(value, str) for value in step.outputs)


@pytest.mark.parametrize("name", ENDPOINTS)
def test_metadata_domain_is_declared(name: str) -> None:
    endpoint = ENDPOINTS[name]
    assert endpoint.metadata is not None
    assert endpoint.metadata.domain is not None
    assert endpoint.metadata.domain is _EXPECTED_DOMAINS[name]


@pytest.mark.parametrize("name", ENDPOINTS)
def test_low_level_feature_flags_match_endpoint_fields(name: str) -> None:
    endpoint = ENDPOINTS[name]
    assert endpoint.metadata is not None

    for field_name, feature in _FIELD_FEATURES.items():
        field_is_enabled = bool(getattr(endpoint, field_name))
        assert (feature in endpoint.metadata.features) is field_is_enabled, (
            f"{name}: {feature.value} should match TableEndpoint.{field_name}"
        )
