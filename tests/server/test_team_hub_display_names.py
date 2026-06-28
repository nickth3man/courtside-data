"""Tests for :meth:`TeamHubService._team_display_name` and the
``TeamHubSummary.display_name`` field.

The display-name lookup is data-driven: it calls
``franchise_history`` once per ``team_identifier``, picks the
``team_name`` from the most-recent row, and caches the result for
the lifetime of the service instance. On any failure to read the
endpoint (``MissingFixtureError`` or empty rows) the helper falls
back to the static :data:`TEAM_DISPLAY_NAMES` dict, then to the
raw ``team_identifier`` — the same graceful-degrade pattern that
:meth:`TeamHubService._franchise_arc` uses.
"""

from __future__ import annotations

from typing import Any

from courtside_data.server.fixtures import MissingFixtureError
from courtside_data.server.team_service import TEAM_DISPLAY_NAMES, TeamHubService


class _FakeFranchiseHistoryRow:
    """Minimal BRRow double carrying the fields the display-name
    projection reads (``team_name`` and ``season``)."""

    def __init__(self, **payload: object) -> None:
        self._payload = payload
        for key, value in payload.items():
            setattr(self, key, value)

    def __getitem__(self, key: str) -> object:
        return self._payload[key]

    def get(self, key: str, default: object = None) -> object:
        return self._payload.get(key, default)


class _FakeDisplayNameService(TeamHubService):
    """Test double: inject controlled ``franchise_history`` rows
    (and a call counter) for the display-name helper.

    All other endpoints (used by :meth:`summary` for roster, hero
    stats, etc.) return ``[]`` so the summary's graceful-empty
    envelope path runs.
    """

    def __init__(
        self,
        fake_rows: list[Any] | None = None,
        *,
        raise_missing: bool = False,
        raise_missing_for: set[str] | None = None,
    ) -> None:
        super().__init__(transport="fixture")
        self._fake_rows = fake_rows or []
        self._raise_missing = raise_missing
        self._raise_missing_for = raise_missing_for or set()
        self._franchise_history_calls: int = 0

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[Any]:
        if endpoint_name == "franchise_history":
            self._franchise_history_calls += 1
            team_id = params.get("team_abbreviation")
            if self._raise_missing or (team_id is not None and team_id in self._raise_missing_for):
                raise MissingFixtureError(f"simulated missing franchise_history fixture for {team_id!r}")
            return list(self._fake_rows)
        # Every other endpoint (used by the embedded roster /
        # hero-stats path) returns empty so the summary's
        # graceful-empty envelope renders.
        return []


# ---------------------------------------------------------------------------
# Direct tests of :meth:`_team_display_name`
# ---------------------------------------------------------------------------


def test_display_name_uses_latest_team_name_from_franchise_history() -> None:
    """When ``franchise_history`` returns rows, the display name is
    the ``team_name`` of the row with the latest ``season_end_year``.

    The rows arrive in the BR source order (most recent first), so
    the helper must explicitly pick the max by parsed season-end-year
    rather than blindly taking ``rows[0]["team_name"]`` — that
    protects against future BR reorderings and against relocated
    franchises whose latest ``team_name`` differs from older ones
    (e.g. Seattle SuperSonics -> OKC Thunder).
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics", wins=61, losses=21),
        _FakeFranchiseHistoryRow(season="2023-24", team_name="Boston Celtics", wins=64, losses=18),
        _FakeFranchiseHistoryRow(season="2022-23", team_name="Boston Celtics", wins=57, losses=25),
    ]
    service = _FakeDisplayNameService(fake_rows=rows)

    assert service._team_display_name("BOS") == "Boston Celtics"


def test_display_name_picks_max_season_when_rows_are_unsorted() -> None:
    """Even if the source rows come in ascending season order, the
    helper picks the max (latest) season, not the first row.
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2022-23", team_name="Old Name", wins=10, losses=10),
        _FakeFranchiseHistoryRow(season="2023-24", team_name="Middle Name", wins=10, losses=10),
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Latest Name", wins=10, losses=10),
    ]
    service = _FakeDisplayNameService(fake_rows=rows)

    assert service._team_display_name("SEA") == "Latest Name"


def test_display_name_falls_back_to_static_dict_on_missing_fixture() -> None:
    """When ``franchise_history`` raises ``MissingFixtureError`` the
    helper falls back to the static :data:`TEAM_DISPLAY_NAMES` dict.

    This is the graceful-degrade path that keeps the summary
    rendering in fixture mode before the team-hub fixture transport
    is wired (see ``team_service.py:506`` for the parallel "roster"
    fallback).
    """
    service = _FakeDisplayNameService(raise_missing=True)

    assert service._team_display_name("BOS") == TEAM_DISPLAY_NAMES["BOS"] == "Boston Celtics"


def test_display_name_falls_back_to_static_dict_on_empty_result() -> None:
    """When ``franchise_history`` returns ``[]`` (valid HTML, no rows)
    the helper also falls back to the static dict.
    """
    service = _FakeDisplayNameService(fake_rows=[])

    assert service._team_display_name("LAL") == TEAM_DISPLAY_NAMES["LAL"] == "Los Angeles Lakers"


def test_display_name_falls_back_to_raw_identifier_when_unknown_team() -> None:
    """When the team identifier is missing from both the data source
    AND the static dict, the helper falls back to the raw identifier.

    This is the same behavior the static-dict path already had
    (``TEAM_DISPLAY_NAMES.get(team_identifier, team_identifier)``),
    preserved for the new data-driven path so an unknown team
    identifier doesn't crash the summary.
    """
    service = _FakeDisplayNameService(raise_missing=True)

    assert service._team_display_name("UNKNOWN_TEAM") == "UNKNOWN_TEAM"


def test_display_name_uses_franchise_history_not_static_dict() -> None:
    """The data-driven path wins over the static dict.

    A team whose static entry is stale (e.g. a relocated franchise
    still listed under its old name) gets the new name from the
    endpoint. This is the whole point of the migration.
    """
    # ``SEA`` is "Seattle SuperSonics" in the static dict. The
    # endpoint now returns "Oklahoma City Thunder" because the
    # franchise relocated. The helper must surface the live name.
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Oklahoma City Thunder"),
    ]
    service = _FakeDisplayNameService(fake_rows=rows)

    assert service._team_display_name("SEA") == "Oklahoma City Thunder"


def test_display_name_cached_per_service_instance() -> None:
    """A second call for the same team does not re-hit the endpoint.

    The cache lives on the service instance (one fixture-mode
    service per test), so the helper memoizes per-identifier for
    the process lifetime of the service. This avoids a re-fetch on
    every summary call (e.g. the UI's tab-switch handler hitting
    the summary route repeatedly).
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics"),
    ]
    service = _FakeDisplayNameService(fake_rows=rows)

    first = service._team_display_name("BOS")
    second = service._team_display_name("BOS")
    third = service._team_display_name("BOS")

    assert first == "Boston Celtics"
    assert second == "Boston Celtics"
    assert third == "Boston Celtics"
    assert service._franchise_history_calls == 1, "Second and third calls must be served from the in-process cache"


def test_display_name_cache_keyed_per_team() -> None:
    """The cache is per-team-identifier — a lookup for a second team
    triggers its own ``_run`` call.

    The fake service returns the BOS row for any team, but raises
    :class:`MissingFixtureError` for ``"LAL"`` so we can assert that
    the second identifier took its own code path (and the LAL
    fallback hit the static dict).
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics"),
    ]
    service = _FakeDisplayNameService(fake_rows=rows, raise_missing_for={"LAL"})

    assert service._team_display_name("BOS") == "Boston Celtics"
    assert service._team_display_name("LAL") == TEAM_DISPLAY_NAMES["LAL"] == "Los Angeles Lakers"
    # The cache must not collapse the two identifiers into one entry:
    # BOS had a real lookup (1 call) and LAL took its own (1 call) =
    # 2 calls total. If the cache was keyed by something other than
    # the team identifier, the second call would be served without
    # re-invoking ``_run``.
    assert service._franchise_history_calls == 2


# ---------------------------------------------------------------------------
# End-to-end: the ``summary`` payload must surface the data-driven name
# ---------------------------------------------------------------------------


def test_summary_uses_franchise_history_team_name_for_display_name() -> None:
    """The summary's ``display_name`` is sourced from
    ``franchise_history`` via :meth:`_team_display_name`, not the
    static dict.

    Same data shape as the direct test, but exercises the public
    ``summary()`` entry point end-to-end so the wiring
    (``summary`` -> ``_team_display_name``) is locked in.
    """
    rows = [
        _FakeFranchiseHistoryRow(season="2024-25", team_name="Boston Celtics"),
        _FakeFranchiseHistoryRow(season="2023-24", team_name="Boston Celtics"),
    ]
    service = _FakeDisplayNameService(fake_rows=rows)

    summary = service.summary("BOS")

    assert summary.display_name == "Boston Celtics"


def test_summary_falls_back_to_static_dict_on_missing_fixture() -> None:
    """End-to-end: the summary falls back to the static dict when
    ``franchise_history`` raises ``MissingFixtureError``.
    """
    service = _FakeDisplayNameService(raise_missing=True)

    summary = service.summary("BOS")

    assert summary.display_name == TEAM_DISPLAY_NAMES["BOS"] == "Boston Celtics"
