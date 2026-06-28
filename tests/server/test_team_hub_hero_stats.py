"""Team-hub hero-stats contract tests.

Pins the closed-type contract for :class:`TeamHeroStats` in fixture
mode: when the underlying ``team_misc_four_factors`` fixture is
missing, the summary must still return a typed
:class:`TeamHeroStats` instance with ``team`` populated to the
requested identifier and every stat field ``None`` (so the UI
can render a stable "no data" state without guarding on shape).
"""

from __future__ import annotations

from typing import Any

import pytest
from courtside_data.server.fixtures import MissingFixtureError
from courtside_data.server.team_models import TeamHeroStats
from courtside_data.server.team_service import TeamHubService
from pydantic import ValidationError


class _FakeTeamHubService(TeamHubService):
    """Test double: simulate a missing fixture for ``team_misc_four_factors``."""

    def __init__(self) -> None:
        super().__init__(transport="fixture")

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[Any]:
        if endpoint_name == "team_misc_four_factors":
            raise MissingFixtureError(f"simulated missing fixture for {endpoint_name!r}")
        return []


def test_team_hero_stats_missing_fixture_returns_typed_empty() -> None:
    """A missing fixture must yield a typed ``TeamHeroStats(team=...)`` with
    all stat fields ``None``.

    The ``team`` field is always populated with the requested team
    identifier so the UI can identify which team the (missing) stats
    are for. Every other field defaults to ``None`` — that is the
    graceful-empty contract.
    """
    service = _FakeTeamHubService()
    result = service._team_hero_stats("BOS", season_end_year=2024)
    assert isinstance(result, TeamHeroStats)
    assert result.team == "BOS"
    assert result.season is None
    assert result.wins is None
    assert result.losses is None
    assert result.win_pct is None
    assert result.wins_pyth is None
    assert result.losses_pyth is None
    assert result.mov is None
    assert result.srs is None
    assert result.off_rtg is None
    assert result.def_rtg is None
    assert result.pace is None


def test_team_hero_stats_empty_model_has_team_field_required() -> None:
    """Constructing the empty model without a ``team`` must fail (Pydantic v2).

    This pins the closed-type contract: ``team`` is the only required
    field; a future regression that drops the requirement would
    surface here as a validation error.
    """
    with pytest.raises(ValidationError):
        # Intentional: this is a contract assertion, not real usage.
        TeamHeroStats()  # ty: ignore[missing-argument]


def test_team_hero_stats_empty_model_rejects_unknown_fields() -> None:
    """The model has ``extra='forbid'`` — silently accepting a typo'd
    field name would mask schema drift downstream.
    """
    with pytest.raises(ValidationError):
        TeamHeroStats(team="BOS", not_a_real_field=1)  # ty: ignore[unknown-argument]
