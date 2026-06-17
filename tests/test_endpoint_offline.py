"""Tier-1 offline endpoint tests: pydantic validation as a schema-drift canary.

Every generic manifest case replays saved HTML through the real client stack
(parsers, selector cache, row-model validation) and asserts a non-empty result.
A successful call with no :class:`~courtside_data.errors.SchemaDriftError` is
the drift canary — corrupted fixtures should fail here in CHECK verification.
"""

from __future__ import annotations

import pytest

from courtside_data.endpoints import ENDPOINTS
from tests.fixture_manifest import TIER1_CASES, Case


@pytest.mark.parametrize("case", TIER1_CASES, ids=[case.id for case in TIER1_CASES])
def test_generic_endpoint_offline(case: Case, make_offline_client) -> None:
    client = make_offline_client(case)
    method = getattr(client, case.endpoint_name)
    result = method(**case.params)

    assert isinstance(result, list), f"{case.id}: expected list, got {type(result).__name__}"
    assert result, f"{case.id}: expected non-empty row list"

    endpoint = ENDPOINTS[case.endpoint_name]
    row_model = endpoint.row_model
    assert row_model is not None, f"{case.id}: endpoint has no row_model"
    assert all(isinstance(row, row_model) for row in result), (
        f"{case.id}: not all rows validated as {row_model.__name__}"
    )
