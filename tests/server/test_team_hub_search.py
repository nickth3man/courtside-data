"""Tests for :meth:`TeamHubService.search`.

The team-hub search sits on top of the player-hub's ``search``
``EndpointSpec`` (which fans out over the no-``idx`` Basketball-
Reference ``/search/search.fcgi?search={term}`` page) and filters
the resulting ``SearchResultRow`` stream to entries with the
``type == "team"`` discriminator that the parser now stamps on
each card (see :mod:`courtside_data.parsing._rows_search` and
``ideas/br-search-idx-research-2026-06-28.md`` for the full
research background).

Contract:

* Input shorter than two characters raises
  :class:`courtside_data.errors.InvalidSearch` (matches the
  player-hub behaviour at ``PlayerHubService.search_players``).
* Input with no team rows returns ``[]`` (not an error — the UI
  shows the empty state).
* Input with team rows returns one :class:`TeamSearchResult` per
  distinct team ``identifier``. The franchise card (``teams``
  sub-`div`, ``/teams/BOS/``) appears in source before the
  per-season ``team_seasons`` cards for the same franchise, so
  dedupe-by-identifier keeping the first occurrence yields the
  franchise card and discards the per-season rows.
* Leagues come back as ``sorted([...])`` strings.
"""

from __future__ import annotations

from typing import Any

import pytest
from courtside_data.errors import InvalidSearch
from courtside_data.server.team_models import TeamSearchResult
from courtside_data.server.team_service import TeamHubService


class _FakeSearchRow:
    """Minimal row double that exposes both attribute access
    (Pydantic-style) and ``__getitem__`` + ``get`` (dict-style)
    so the search-filter path's ``getattr(r, "type", None)`` and
    ``r["identifier"]`` both work.
    """

    def __init__(self, **payload: object) -> None:
        self._payload = payload
        for key, value in payload.items():
            setattr(self, key, value)

    def __getitem__(self, key: str) -> object:
        return self._payload[key]

    def get(self, key: str, default: object = None) -> object:
        return self._payload.get(key, default)


class _FakeTeamSearchService(TeamHubService):
    """Test double: inject controlled search rows via ``fake_rows``."""

    def __init__(self, fake_rows: list[Any]) -> None:
        super().__init__(transport="fixture")
        self._fake_rows = fake_rows

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[Any]:
        if endpoint_name != "search":
            return []
        return list(self._fake_rows)


def test_team_search_rejects_short_term() -> None:
    """A term shorter than two characters must raise ``InvalidSearch``."""
    service = _FakeTeamSearchService(fake_rows=[])
    with pytest.raises(InvalidSearch):
        service.search("a")


def test_team_search_empty_for_no_team_rows() -> None:
    """A search that returns only player / coach / exec rows yields ``[]``."""
    rows = [
        _FakeSearchRow(name="LeBron James", identifier="jamesle01", leagues={"NBA"}, type="player"),
        _FakeSearchRow(name="Gregg Popovich", identifier="popovgr99c", leagues={"NBA"}, type="coach"),
        _FakeSearchRow(name="Danny Ainge", identifier="aingeda01x", leagues={"NBA"}, type="executive"),
    ]
    service = _FakeTeamSearchService(fake_rows=rows)
    assert service.search("lebron") == []


def test_team_search_returns_only_team_typed_rows() -> None:
    """Only ``type == "team"`` rows make it into the result list."""
    rows = [
        _FakeSearchRow(name="LeBron James", identifier="jamesle01", leagues={"NBA"}, type="player"),
        _FakeSearchRow(name="Boston Celtics", identifier="BOS", leagues={"NBA"}, type="team"),
        _FakeSearchRow(name="Los Angeles Lakers", identifier="LAL", leagues={"NBA"}, type="team"),
    ]
    service = _FakeTeamSearchService(fake_rows=rows)
    results = service.search("celtics")
    assert len(results) == 2
    assert all(isinstance(r, TeamSearchResult) for r in results)
    identifiers = {r.identifier for r in results}
    assert identifiers == {"BOS", "LAL"}


def test_team_search_dedupes_duplicate_identifiers() -> None:
    """The dedupe pass keeps the first occurrence of each ``identifier``.

    The pre-decided answer says "dedupe by identifier keeping first
    occurrence (franchise-level card appears first in source)". Two
    cards with the same identifier (e.g. two franchise cards
    accidentally emitted for the same team) collapse to one.
    """
    rows = [
        _FakeSearchRow(name="Boston Celtics", identifier="BOS", leagues={"NBA"}, type="team"),
        # Same identifier as the franchise card → deduped.
        _FakeSearchRow(name="Boston Celtics (alt)", identifier="BOS", leagues={"NBA"}, type="team"),
    ]
    service = _FakeTeamSearchService(fake_rows=rows)
    results = service.search("celtics")
    assert len(results) == 1
    assert results[0].identifier == "BOS"
    assert results[0].name == "Boston Celtics"


def test_team_search_dedupes_team_seasons_into_franchise() -> None:
    """A ``team_seasons`` card and the matching ``teams`` franchise
    card both share the same identifier after the parser extracts the
    team abbreviation from the per-season href
    (``/teams/UTA/1997.html`` → ``"UTA"``), so the dedupe pass
    collapses them to a single entry.

    Without the parser fix, ``team_seasons`` cards would have
    year-as-identifier (``"1997"``, ``"2024"``) and would leak
    through the dedupe as duplicate-looking team rows — and
    clicking such a row would 404 at the deep-link
    ``/teams/{identifier}/summary``. This test asserts the now-fixed
    behaviour.
    """
    rows = [
        # Franchise card from the ``teams`` sub-`div`.
        _FakeSearchRow(name="Utah Jazz", identifier="UTA", leagues={"NBA"}, type="team"),
        # Per-season cards from the ``team_seasons`` sub-`div` —
        # the parser now stamps them with the team abbreviation.
        _FakeSearchRow(name="1997 Utah Jazz", identifier="UTA", leagues={"NBA"}, type="team"),
        _FakeSearchRow(name="2024 Utah Jazz", identifier="UTA", leagues={"NBA"}, type="team"),
    ]
    service = _FakeTeamSearchService(fake_rows=rows)
    results = service.search("jazz")
    assert len(results) == 1
    assert results[0].identifier == "UTA"
    # The franchise card appears first in source, so dedupe-by-first
    # keeps the franchise row's name (not the per-season card name).
    assert results[0].name == "Utah Jazz"


def test_team_search_preserves_identifier_case() -> None:
    """The team identifier must NOT be lowercased — the deep-link
    ``/teams/{identifier}/summary`` is uppercase-only.
    """
    rows = [
        _FakeSearchRow(name="Boston Celtics", identifier="BOS", leagues={"NBA"}, type="team"),
    ]
    service = _FakeTeamSearchService(fake_rows=rows)
    results = service.search("celtics")
    assert results[0].identifier == "BOS"


def test_team_search_leagues_are_sorted_strings() -> None:
    """The ``leagues`` field is ``sorted([str(l) for l in …])``."""
    rows = [
        _FakeSearchRow(name="Boston Celtics", identifier="BOS", leagues={"NBA", "ABA", "BAA"}, type="team"),
    ]
    service = _FakeTeamSearchService(fake_rows=rows)
    results = service.search("celtics")
    assert results[0].leagues == ["ABA", "BAA", "NBA"]


def test_team_search_handles_missing_leagues() -> None:
    """Missing ``leagues`` (the player-direct branch) must default to ``[]``."""
    rows = [
        _FakeSearchRow(name="Boston Celtics", identifier="BOS", type="team"),
    ]
    service = _FakeTeamSearchService(fake_rows=rows)
    results = service.search("celtics")
    assert results[0].leagues == []
