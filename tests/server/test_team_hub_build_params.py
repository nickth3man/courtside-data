"""Tests for :meth:`TeamHubService._build_params` param-name mapping.

The mapping only knows three param names today
(``_TEAM_ABBREVIATION_PARAM``, ``_TEAM_SEASON_PARAM``,
``_TEAM_INCLUDE_INACTIVE_PARAM``). The first set of tests below
snapshots that surface area: for every team endpoint registered in
:data:`courtside_data.endpoints.ENDPOINTS`, ``_build_params`` must round-
trip without raising for a representative call.

The second test injects a fake spec with a novel param and asserts the
"unhandled param" branch surfaces a clear, actionable error message.
"""

from __future__ import annotations

from typing import Any

import pytest
from courtside_data.endpoints import (
    ENDPOINTS,
    EndpointDomain,
    EndpointKind,
    EndpointMetadata,
    EndpointScope,
    EndpointSpec,
    ParserShape,
    RequestShape,
)
from courtside_data.schemas._base import BRRow
from courtside_data.server.fixtures import TEAM_ENDPOINTS, TEAM_SEASON_ENDPOINTS
from courtside_data.server.team_service import (
    _TEAM_ABBREVIATION_PARAM,
    _TEAM_INCLUDE_INACTIVE_PARAM,
    _TEAM_SEASON_PARAM,
    TeamHubService,
)


class _DummyRow(BRRow):
    """Minimal row model for the fake spec; never actually parsed."""


def _minimal_metadata() -> EndpointMetadata:
    return EndpointMetadata(
        domain=EndpointDomain.TEAMS,
        kind=EndpointKind.GENERIC_TABLE,
        scope=EndpointScope.TEAM_SEASON,
        request_shape=RequestShape.SINGLE_REQUEST,
        parser_shape=ParserShape.TABLE,
    )


def _service() -> TeamHubService:
    return TeamHubService(transport="fixture")


# ---------------------------------------------------------------------------
# Parity / round-trip test: every registered team endpoint must be
# translatable to its native params dict.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("endpoint_name", sorted(TEAM_ENDPOINTS | TEAM_SEASON_ENDPOINTS))
def test_build_params_round_trips_for_every_team_endpoint(endpoint_name: str) -> None:
    """``_build_params`` must successfully translate public kwargs for every
    registered team endpoint that the service knows how to map today.

    For team-scope endpoints (``TEAM_ENDPOINTS``: contracts, franchise
    history, etc.) no season is required. For team-season endpoints
    (``TEAM_SEASON_ENDPOINTS``: roster, splits, …) the helper falls back
    to the calendar-driven resolver via the route layer, so passing
    ``season_end_year=2024`` exercises the season branch end-to-end.
    """
    spec = ENDPOINTS[endpoint_name]
    service = _service()
    kwargs: dict[str, Any] = {"team_identifier": "BOS"}
    if _TEAM_SEASON_PARAM in spec.params:
        kwargs["season_end_year"] = 2024
    if _TEAM_INCLUDE_INACTIVE_PARAM in spec.params:
        kwargs["include_inactive_games"] = False
    params = service._build_params(endpoint_name, **kwargs)

    # The abbreviation branch always contributes the team identifier.
    assert params[_TEAM_ABBREVIATION_PARAM] == "BOS"
    # No public kwarg leaks into the native dict as ``None`` — every
    # param the endpoint declares must be populated by one of the
    # mapped branches.
    assert all(v is not None for v in params.values()), (
        f"{endpoint_name!r}: _build_params produced a None value: {params!r}"
    )


# ---------------------------------------------------------------------------
# Negative test: the "unhandled param" raise must point the maintainer at
# the spec, not just at the endpoint name.
# ---------------------------------------------------------------------------


def test_build_params_unknown_param_raises_with_clear_message(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unhandled param in the spec must raise a clear, actionable error.

    The error message should:
      * quote the bad param name,
      * quote the endpoint name,
      * point at the ENDPOINTS registry entry's full ``params`` tuple.
    """
    fake_spec = EndpointSpec(
        path="/teams/{team_abbreviation}/{season_end_year}.html",
        row_model=_DummyRow,
        metadata=_minimal_metadata(),
        params=(_TEAM_ABBREVIATION_PARAM, _TEAM_SEASON_PARAM, "novel_param"),
    )
    monkeypatch.setitem(ENDPOINTS, "fake_team_ep", fake_spec)
    try:
        with pytest.raises(NotImplementedError) as excinfo:
            _service()._build_params(
                "fake_team_ep",
                team_identifier="BOS",
                season_end_year=2024,
            )
    finally:
        # Defensive cleanup in case the assertion failed before reaching here.
        ENDPOINTS.pop("fake_team_ep", None)

    message = str(excinfo.value)
    assert "novel_param" in message
    assert "fake_team_ep" in message
    # Tighter error: point at the spec's full params tuple so the
    # maintainer can see the full param surface area in one read.
    assert "Declared params" in message
    assert "novel_param" in fake_spec.params
