"""Tests for :meth:`TeamHubService._franchise_arc` and the
``TeamHubSummary.franchise_arc`` field.

Two contracts pinned here:

* The arc is a list of :class:`FranchiseArcPoint` sorted by
  ``season_end_year`` ascending. ``win_pct = wins / (wins + losses)``
  when both are present, ``None`` otherwise.
* On :class:`MissingFixtureError` the helper returns ``[]`` (no
  raise) so the summary still renders.
"""

from __future__ import annotations

from typing import Any

import pytest
from courtside_data.server.fixtures import MissingFixtureError
from courtside_data.server.team_models import FranchiseArcPoint
from courtside_data.server.team_service import TeamHubService
from pydantic import ValidationError


class _FakeFranchiseHistoryRow:
    """Minimal BRRow double carrying the fields the arc projection reads."""

    def __init__(self, **payload: object) -> None:
        self._payload = payload
        for key, value in payload.items():
            setattr(self, key, value)

    def __getitem__(self, key: str) -> object:
        return self._payload[key]

    def get(self, key: str, default: object = None) -> object:
        return self._payload.get(key, default)


class _FakeTeamArcService(TeamHubService):
    """Test double: inject controlled ``franchise_history`` rows."""

    def __init__(self, fake_rows: list[Any] | None = None, *, raise_missing: bool = False) -> None:
        super().__init__(transport="fixture")
        self._fake_rows = fake_rows or []
        self._raise_missing = raise_missing

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[Any]:
        if endpoint_name != "franchise_history":
            return []
        if self._raise_missing:
            raise MissingFixtureError("simulated missing franchise_history fixture")
        return list(self._fake_rows)


def test_franchise_arc_sorted_by_season_end_year_ascending() -> None:
    """The arc is sorted by ``season_end_year`` ascending.

    Even if the source rows come in reverse-chronological order
    (which is the BR convention), the helper re-sorts to ascending
    so the consumer can plot a left-to-right time series.
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2023-24", team_name="Boston Celtics", wins=64, losses=18),
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics", wins=61, losses=21),
        _FakeFranchiseHistoryRow(season="2022-23", team_name="Boston Celtics", wins=57, losses=25),
    ]
    service = _FakeTeamArcService(fake_rows=rows)
    arc = service._franchise_arc("BOS")

    assert [p.season_end_year for p in arc] == [2023, 2024, 2025]
    assert all(isinstance(p, FranchiseArcPoint) for p in arc)


def test_franchise_arc_win_pct_computed_when_wins_and_losses_present() -> None:
    """``win_pct = wins / (wins + losses)`` when both are non-null positive ints."""
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics", wins=61, losses=21),
    ]
    service = _FakeTeamArcService(fake_rows=rows)
    arc = service._franchise_arc("BOS")
    assert len(arc) == 1
    assert arc[0].wins == 61
    assert arc[0].losses == 21
    assert arc[0].win_pct == pytest.approx(61 / 82)


def test_franchise_arc_win_pct_none_when_wins_or_losses_missing() -> None:
    """``win_pct`` is ``None`` if either ``wins`` or ``losses`` is missing/zero.

    Zero-division protection: if both are zero (e.g. an in-progress
    season the page rendered as 0-0), ``win_pct`` must still be
    ``None``, not a ``ZeroDivisionError``.
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics", wins=10, losses=None),
        _FakeFranchiseHistoryRow(season="2023-24", team_name="Boston Celtics", wins=None, losses=18),
        _FakeFranchiseHistoryRow(season="2022-23", team_name="Boston Celtics", wins=0, losses=0),
    ]
    service = _FakeTeamArcService(fake_rows=rows)
    arc = service._franchise_arc("BOS")
    assert [p.season_end_year for p in arc] == [2023, 2024, 2025]
    assert all(p.win_pct is None for p in arc)


def test_franchise_arc_skips_rows_with_unparseable_season() -> None:
    """Rows whose ``season`` field doesn't match ``YYYY-YY`` are skipped.

    Defensive: the source schema has ``season: StrOrNone``; a future
    row that doesn't carry a season string must not crash the
    helper or pollute the arc with garbage.
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics", wins=61, losses=21),
        _FakeFranchiseHistoryRow(season="garbage", team_name="Boston Celtics", wins=10, losses=10),
        _FakeFranchiseHistoryRow(season=None, team_name="Boston Celtics", wins=10, losses=10),
    ]
    service = _FakeTeamArcService(fake_rows=rows)
    arc = service._franchise_arc("BOS")
    assert len(arc) == 1
    assert arc[0].season_end_year == 2025


def test_franchise_arc_missing_fixture_returns_empty_list() -> None:
    """A missing fixture yields ``[]`` (graceful-empty contract)."""
    service = _FakeTeamArcService(raise_missing=True)
    assert service._franchise_arc("BOS") == []


def test_franchise_arc_empty_result_for_no_rows() -> None:
    """An empty row set (valid HTML, no rows) yields ``[]``."""
    service = _FakeTeamArcService(fake_rows=[])
    assert service._franchise_arc("BOS") == []


def test_franchise_arc_point_model_rejects_unknown_fields() -> None:
    """The model has ``extra='forbid'`` — silent typo'd fields would
    mask schema drift downstream.
    """
    with pytest.raises(ValidationError):
        FranchiseArcPoint(season_end_year=2024, not_a_real_field=1)  # ty: ignore[unknown-argument]
