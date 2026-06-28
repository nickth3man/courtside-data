"""Tests for :meth:`TeamHubService.summary`.

The team-hub landing state has two contracts pinned here:

* The summary's ``leagues`` field is always ``["NBA"]`` (every NBA
  team belongs to the NBA league; the simpler correct value beats
  the empty ``default_factory=list`` fallback, which previously made
  the UI render a dangling ``·`` separator next to the team
  identifier).
* The summary's ``roster`` and ``hero_stats`` payloads are
  graceful-empty envelopes when the underlying endpoints are not
  wired in fixture mode — the field shape is closed-typed, so the
  UI can render a stable empty state without guarding on field
  presence. (See ``test_team_hub_hero_stats.py`` and
  ``test_team_hub_franchise_arc.py`` for the per-field assertions.)
"""

from __future__ import annotations

from typing import Any

from courtside_data.server.team_service import TeamHubService


class _FakeTeamSummaryService(TeamHubService):
    """Test double: every endpoint returns an empty row set (no
    fixture data), so the summary exercises the graceful-empty
    envelope path.
    """

    def __init__(self) -> None:
        super().__init__(transport="fixture")

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[Any]:
        # Return ``[]`` for every endpoint — no ``MissingFixtureError``,
        # so the ``roster`` and ``hero_stats`` paths go through their
        # empty-envelope code paths (no exception catch needed).
        return []


def test_summary_leagues_is_nba() -> None:
    """The summary's ``leagues`` field is always ``["NBA"]``.

    Every NBA team is in the NBA league, so the simplest correct
    value is a single-element list. The previous behaviour
    (``default_factory=list`` with no explicit kwarg) shipped
    ``leagues=[]``, which the team-hub header rendered as a
    dangling ``·`` separator.
    """
    service = _FakeTeamSummaryService()
    summary = service.summary("BOS")

    assert summary.leagues == ["NBA"]
