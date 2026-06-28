"""Contract tests for the endpoint metadata backfill."""

from __future__ import annotations

import pytest
from courtside_data.endpoints import (
    ENDPOINTS,
    EndpointDomain,
    EndpointFeature,
    EndpointKind,
    ParserShape,
    RequestShape,
    WorkflowStepKind,
)
from courtside_data.endpoints._draft_awards_leaders import DRAFT_AWARDS_LEADERS_ENDPOINTS
from courtside_data.endpoints._league import LEAGUE_ENDPOINTS
from courtside_data.endpoints._players import PLAYER_ENDPOINTS
from courtside_data.endpoints._playoffs import PLAYOFF_ENDPOINTS
from courtside_data.endpoints._teams import TEAM_ENDPOINTS
from courtside_data.endpoints._workflows import WORKFLOW_ENDPOINTS
from courtside_data.parsing.workflows import NATIVE_WORKFLOW_ENDPOINTS
from courtside_data.parsing.workflows._executor import workflow_execution_bindings
from courtside_data.server.team_catalog import TEAM_DATASETS

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
    **dict.fromkeys(WORKFLOW_ENDPOINTS, EndpointDomain.GAMES),
}


def test_every_endpoint_has_required_registry_contract() -> None:
    for name, endpoint in ENDPOINTS.items():
        assert endpoint.metadata.domain is _EXPECTED_DOMAINS[name]
        assert endpoint.row_model is not None


@pytest.mark.parametrize("name", ENDPOINTS)
def test_kind_is_derived_from_metadata(name: str) -> None:
    endpoint = ENDPOINTS[name]
    assert endpoint.kind is endpoint.metadata.kind


@pytest.mark.parametrize("name", ENDPOINTS)
def test_workflow_endpoints_declare_workflow_spec(name: str) -> None:
    endpoint = ENDPOINTS[name]
    if endpoint.metadata.kind is EndpointKind.WORKFLOW:
        assert endpoint.workflow is not None
        assert name in NATIVE_WORKFLOW_ENDPOINTS
        assert name in workflow_execution_bindings()


@pytest.mark.parametrize("name", ENDPOINTS)
def test_generic_table_endpoints_do_not_declare_workflow_spec(name: str) -> None:
    endpoint = ENDPOINTS[name]
    if endpoint.metadata.kind is EndpointKind.GENERIC_TABLE:
        assert endpoint.workflow is None
        assert name not in NATIVE_WORKFLOW_ENDPOINTS
        assert name not in workflow_execution_bindings()


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
        assert isinstance(step.kind, WorkflowStepKind)
        assert isinstance(step.inputs, tuple)
        assert isinstance(step.outputs, tuple)
        assert all(isinstance(value, str) for value in step.inputs)
        assert all(isinstance(value, str) for value in step.outputs)


@pytest.mark.parametrize("name", ENDPOINTS)
def test_metadata_domain_is_declared(name: str) -> None:
    endpoint = ENDPOINTS[name]
    assert endpoint.metadata.domain is _EXPECTED_DOMAINS[name]


@pytest.mark.parametrize("name", ENDPOINTS)
def test_low_level_feature_flags_match_endpoint_fields(name: str) -> None:
    endpoint = ENDPOINTS[name]

    for field_name, feature in _FIELD_FEATURES.items():
        field_is_enabled = bool(getattr(endpoint, field_name))
        assert (feature in endpoint.metadata.features) is field_is_enabled, (
            f"{name}: {feature.value} should match EndpointSpec.{field_name}"
        )


@pytest.mark.parametrize("name", ENDPOINTS)
def test_request_shape_matches_declared_capabilities(name: str) -> None:
    endpoint = ENDPOINTS[name]
    features = endpoint.metadata.features
    request_shape = endpoint.metadata.request_shape
    workflow_kinds = {step.kind for step in endpoint.workflow.steps} if endpoint.workflow is not None else set()

    if request_shape is RequestShape.SINGLE_REQUEST:
        assert EndpointFeature.PAGINATED not in features
        assert EndpointFeature.FANOUT_LINKS not in features
    elif request_shape is RequestShape.MULTI_REQUEST:
        assert EndpointFeature.FANOUT_LINKS in features
        assert workflow_kinds & {WorkflowStepKind.FANOUT, WorkflowStepKind.FETCH}
    elif request_shape is RequestShape.PAGINATED:
        assert EndpointFeature.PAGINATED in features
        assert WorkflowStepKind.BRANCH in workflow_kinds
    elif request_shape is RequestShape.REDIRECTING:
        assert EndpointFeature.REDIRECTS in features
    elif request_shape is RequestShape.STATIC:
        assert endpoint.params == ()


@pytest.mark.parametrize("name", ENDPOINTS)
def test_parser_shape_matches_declared_implementation(name: str) -> None:
    endpoint = ENDPOINTS[name]
    parser_shape = endpoint.metadata.parser_shape
    workflow_kinds = {step.kind for step in endpoint.workflow.steps} if endpoint.workflow is not None else set()

    if parser_shape is ParserShape.COMMENTED_TABLE:
        assert endpoint.commented_table_id is not None
    elif parser_shape is ParserShape.TRANSACTION_LIST:
        assert endpoint.transaction_list_fallback is True
    elif parser_shape is ParserShape.SEARCH_RESULTS:
        assert endpoint.metadata.kind is EndpointKind.WORKFLOW
        assert WorkflowStepKind.BRANCH in workflow_kinds
    elif parser_shape is ParserShape.PLAY_BY_PLAY:
        assert endpoint.metadata.kind is EndpointKind.WORKFLOW
        assert WorkflowStepKind.PARSE in workflow_kinds
        assert EndpointFeature.DERIVED_FIELDS in endpoint.metadata.features
    elif parser_shape in {ParserShape.BRACKET, ParserShape.STANDINGS_BLOCKS, ParserShape.MULTI_TABLE}:
        assert endpoint.metadata.kind is EndpointKind.WORKFLOW
        assert workflow_kinds & {WorkflowStepKind.PARSE, WorkflowStepKind.FANOUT}


@pytest.mark.parametrize("name", ENDPOINTS)
def test_workflow_feature_flags_are_backed_by_workflow_steps(name: str) -> None:
    endpoint = ENDPOINTS[name]
    if endpoint.workflow is None:
        return

    workflow_kinds = {step.kind for step in endpoint.workflow.steps}
    features = endpoint.metadata.features

    if EndpointFeature.WORKFLOW_DIAGNOSTICS in features:
        assert WorkflowStepKind.DIAGNOSTICS in workflow_kinds
    if EndpointFeature.FANOUT_LINKS in features:
        assert workflow_kinds & {WorkflowStepKind.FANOUT, WorkflowStepKind.FETCH}
    if EndpointFeature.PAGINATED in features:
        assert endpoint.metadata.request_shape is RequestShape.PAGINATED
        assert WorkflowStepKind.BRANCH in workflow_kinds
    if EndpointFeature.REDIRECTS in features:
        assert endpoint.metadata.request_shape in {RequestShape.REDIRECTING, RequestShape.PAGINATED}
        assert WorkflowStepKind.BRANCH in workflow_kinds
    if EndpointFeature.ENUM_PARAM_COERCION in features:
        assert "home_team" in endpoint.params


@pytest.mark.parametrize("dataset", TEAM_DATASETS, ids=lambda dataset: dataset.id)
def test_team_hub_scope_matches_endpoint_season_param(dataset) -> None:
    """Every :class:`TeamDataset` whose ``endpoint_name`` resolves to an
    :class:`EndpointSpec` whose ``params`` includes ``"season_end_year"``
    MUST be classified ``scope="team_season"``; every entry whose
    ``EndpointSpec.params`` does NOT include ``"season_end_year"`` MUST be
    classified ``scope="team"``. See
    :mod:`courtside_data.server.team_catalog` for the source-of-truth
    invariant.
    """
    spec = ENDPOINTS[dataset.endpoint_name]
    has_season_param = "season_end_year" in spec.params
    if has_season_param:
        assert dataset.scope == "team_season", (
            f"{dataset.id!r}: endpoint {dataset.endpoint_name!r} accepts season_end_year but scope is {dataset.scope!r}"
        )
    else:
        assert dataset.scope == "team", (
            f"{dataset.id!r}: endpoint {dataset.endpoint_name!r} does not "
            f"accept season_end_year but scope is {dataset.scope!r}"
        )


def test_team_hub_catalog_covers_every_team_endpoint() -> None:
    """No orphan team endpoint specs and no orphan catalog entries.

    Iterates every entry in :data:`TEAM_ENDPOINTS` and asserts the catalog
    has a matching :class:`TeamDataset` whose ``endpoint_name`` is in the
    set, and vice versa.
    """
    catalog_endpoint_names = {dataset.endpoint_name for dataset in TEAM_DATASETS}
    registry_endpoint_names = set(TEAM_ENDPOINTS)
    assert catalog_endpoint_names == registry_endpoint_names, (
        f"catalog/registry drift: catalog_only={catalog_endpoint_names - registry_endpoint_names}, "
        f"registry_only={registry_endpoint_names - catalog_endpoint_names}"
    )


@pytest.mark.parametrize("dataset", TEAM_DATASETS, ids=lambda dataset: dataset.id)
def test_team_hub_default_visible_columns_are_model_fields(dataset) -> None:
    fields = set(ENDPOINTS[dataset.endpoint_name].row_model.model_fields)

    assert dataset.default_visible_columns
    assert set(dataset.default_visible_columns) <= fields
