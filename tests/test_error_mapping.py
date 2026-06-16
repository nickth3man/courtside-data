"""Offline tests for HTTP status → domain error mapping."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from courtside_data.client.courtside_client import CourtsideClient
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import InvalidPlayer, InvalidSeason, InvalidTeam, RateLimitJailed
from tests.fixture_manifest import ERROR_CASES, Case
from tests.fixture_transport import FixtureTransport, build_service

# ERROR_CASES use synthetic endpoint_name values; map them to the real client
# method and expected domain exception.
_ERROR_EXPECTATIONS: dict[str, tuple[str, type[Exception]]] = {
    "error-invalid_team": ("team_roster", InvalidTeam),
    "error-invalid_player": ("player_career_stats", InvalidPlayer),
    "error-invalid_season": ("draft_picks", InvalidSeason),
}


@pytest.mark.parametrize("case", ERROR_CASES, ids=[case.id for case in ERROR_CASES])
def test_error_case_maps_to_domain_exception(case: Case, make_offline_client) -> None:
    method_name, expected_error = _ERROR_EXPECTATIONS[case.endpoint_name]
    client = make_offline_client(case)

    with pytest.raises(expected_error) as exc_info:
        getattr(client, method_name)(**case.params)

    _assert_error_params(case, expected_error, exc_info.value)


def _assert_error_params(case: Case, expected_error: type[Exception], raised: BaseException) -> None:
    if expected_error is InvalidTeam:
        assert isinstance(raised, InvalidTeam)
        assert raised.team_abbreviation == case.params["team_abbreviation"]
    elif expected_error is InvalidPlayer:
        assert isinstance(raised, InvalidPlayer)
        assert raised.player_identifier == case.params["player_identifier"]
    elif expected_error is InvalidSeason:
        assert isinstance(raised, InvalidSeason)
        assert str(case.params["season_end_year"]) in str(raised)


def test_429_with_large_retry_after_raises_rate_limit_jailed() -> None:
    """A synthetic 429 with Retry-After > 300 maps to RateLimitJailed via _get."""
    params = {"team_abbreviation": "BOS", "season_end_year": 2024}
    endpoint = ENDPOINTS["team_roster"]
    url = f"https://www.basketball-reference.com{endpoint.path.format(**params)}"
    transport = FixtureTransport({url: (429, {"Retry-After": "600"})})
    client = CourtsideClient(service=build_service(transport))

    with pytest.raises(RateLimitJailed) as exc_info:
        client.team_roster(**params)

    assert exc_info.value.retry_after == pytest.approx(600.0)


def test_429_below_jail_threshold_propagates_http_status_error() -> None:
    """A 429 below the jail threshold is not converted to RateLimitJailed."""
    params: dict[str, Any] = {"team_abbreviation": "BOS", "season_end_year": 2024}
    endpoint = ENDPOINTS["team_roster"]
    url = f"https://www.basketball-reference.com{endpoint.path.format(**params)}"
    transport = FixtureTransport({url: (429, {"Retry-After": "10"})})
    client = CourtsideClient(service=build_service(transport))

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client.team_roster(**params)

    assert exc_info.value.response.status_code == 429
