"""Meta-tests for fixture manifest completeness against the endpoint registry."""

from __future__ import annotations

from courtside_data.endpoints import ENDPOINTS, EndpointFeature, RequestShape

from tests.fixture_manifest import (
    ALL_CASES,
    MULTI_REQUEST_ENDPOINTS,
    TIER1_CASES,
    TIER1_EXCLUDED_CASE_IDS,
    UNRESOLVED_ENDPOINTS,
)


def _unresolved_endpoint_names() -> set[str]:
    return {entry.split(" (", 1)[0] for entry in UNRESOLVED_ENDPOINTS}


def test_every_endpoint_has_fixture_or_is_unresolved() -> None:
    covered = {case.endpoint_name for case in ALL_CASES}
    unresolved = _unresolved_endpoint_names()
    missing = set(ENDPOINTS) - covered - unresolved
    assert not missing, f"Endpoints with no fixture and not listed as unresolved: {sorted(missing)}"


def test_unresolved_endpoints_are_documented_gaps() -> None:
    unresolved = _unresolved_endpoint_names()
    # Accept empty list as success; otherwise validate they are real endpoints.
    for name in unresolved:
        assert name in ENDPOINTS, f"Unresolved entry {name!r} is not in ENDPOINTS"


def test_multi_request_endpoints_have_cases() -> None:
    covered = {case.endpoint_name for case in ALL_CASES}
    missing = MULTI_REQUEST_ENDPOINTS - covered
    assert not missing, f"Multi-request endpoints missing manifest cases: {sorted(missing)}"


def test_multi_request_endpoint_set_is_metadata_derived() -> None:
    metadata_multi_request_endpoints = {
        name
        for name, endpoint in ENDPOINTS.items()
        if (
            endpoint.metadata.request_shape is RequestShape.MULTI_REQUEST
            or EndpointFeature.FANOUT_LINKS in endpoint.metadata.features
        )
    }

    assert metadata_multi_request_endpoints == MULTI_REQUEST_ENDPOINTS


def test_manifest_meets_coverage_target() -> None:
    covered_endpoints = {case.endpoint_name for case in ALL_CASES}
    total = len(ENDPOINTS)
    ratio = len(covered_endpoints) / total
    assert ratio >= 0.95, f"Coverage {len(covered_endpoints)}/{total} = {ratio:.1%} below 95% target"


def test_tier1_exclusions_are_documented_gaps() -> None:
    generic_ids = {case.id for case in ALL_CASES if case.endpoint_name not in MULTI_REQUEST_ENDPOINTS}
    assert generic_ids >= TIER1_EXCLUDED_CASE_IDS
    expected_ids = generic_ids - TIER1_EXCLUDED_CASE_IDS
    assert {case.id for case in TIER1_CASES} == expected_ids


def test_multi_request_exclusions_are_documented_gaps() -> None:
    from tests.test_multi_request_endpoints import MULTI_REQUEST_EXCLUDED_CASE_IDS

    multi_ids = {case.id for case in ALL_CASES if case.endpoint_name in MULTI_REQUEST_ENDPOINTS}
    assert multi_ids >= MULTI_REQUEST_EXCLUDED_CASE_IDS


def test_tier1_subset_still_substantial() -> None:
    assert len(TIER1_CASES) >= 180, f"Tier-1 subset too small: {len(TIER1_CASES)} cases"
