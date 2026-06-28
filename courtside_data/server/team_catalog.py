"""Team Hub dataset and tab catalog.

Mirrors :mod:`courtside_data.server.catalog` (Player Hub catalog) for the
13 team endpoint specs registered in
:mod:`courtside_data.endpoints._teams`. The static catalog is surfaced
via ``GET /api/endpoints/team-hub``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from courtside_data.endpoints import ENDPOINTS
from courtside_data.server.catalog import column_label
from courtside_data.server.models import ColumnMeta
from courtside_data.server.team_models import TeamDatasetCatalogEntry, TeamDatasetScope, TeamHubTab


@dataclass(frozen=True, slots=True)
class TeamDataset:
    """Static metadata for one Team Hub dataset.

    Mirrors :class:`courtside_data.server.catalog.PlayerHubDataset`. The
    ``scope`` is ``"team"`` for datasets that the UI exposes without a
    season in the URL and ``"team_season"`` for those that require an
    explicit ``season_end_year`` in the route.
    """

    id: str
    label: str
    endpoint_name: str
    scope: TeamDatasetScope
    description: str
    # TODO(team-hub): populate ``default_visible_columns`` per dataset.
    #
    # What: each :class:`TeamDataset` currently has
    # ``default_visible_columns=[]`` (the empty list), which means
    # the team-hub UI renders every column from
    # :func:`team_columns_for_dataset`. Once the fixture HTML is
    # captured and we can inspect a real sample row, the right
    # default-visible set is a curated subset (~6-12 columns per
    # dataset) that the UI uses as the initial render — the player
    # hub's :class:`PlayerHubDataset` entries already declare a
    # non-empty default set (see
    # ``courtside_data/server/catalog.py:22-220`` for the
    # per-dataset examples).
    # Where:
    #   - courtside_data/server/catalog.py:331
    #     (the :func:`columns_for_dataset` helper that produces a
    #     :class:`ColumnMeta` list per dataset, marking
    #     ``default_visible`` from the dataset's
    #     ``default_visible_columns`` tuple).
    #   - courtside_data/server/catalog.py:22  (the player-hub
    #     ``DATASETS`` map — see ``career``,
    #     ``playoff-series``, ``adjusted-shooting`` etc. for
    #     real default-visible tuples; the team-hub entries
    #     should follow the same pattern).
    #   - the 13 ``TeamDataset(...)`` entries below — each
    #     ``default_visible_columns=[]`` needs to be replaced
    #     with a curated tuple.
    #   - courtside_data/schemas/teams.py  (the 13 row-model
    #     classes that define the column set per dataset:
    #     ``TeamRosterRow`` :23, ``TeamInjuryReportRow`` :40,
    #     ``TeamAndOpponentRow`` :52, ``TeamMiscFourFactorsRow``
    #     :62, ``TeamOpponentStatsRow`` :93,
    #     ``TeamTransactionsRow`` :100, ``TeamSplitsRow`` :119,
    #     ``TeamContractsRow`` :170, ``TeamLineupsRow`` :191,
    #     ``TeamStartingLineupsRow`` :223, ``TeamOnOffRow`` :245,
    #     ``FranchiseHistoryRow`` :286; plus
    #     ``TeamScheduleRow`` in
    #     ``courtside_data/schemas/schedule.py:30``).
    # How (per dataset, mirror the player-hub entry):
    #   1. Capture at least one fixture HTML per dataset (the
    #     per-endpoint capture list in
    #     ``docs/architecture/team-hub.md`` is the source of
    #     truth for which URLs to save). For each dataset, use
    #     a "current" team and season (e.g. LAL, 2024) so the
    #     sample row is dense.
    #   2. Run the endpoint against the fixture in fixture
    #     transport and inspect the first row's
    #     ``.model_dump()`` to see the full column set.
    #   3. Pick the ~6-12 most-informative columns (matching
    #     the player hub's curation density) and set
    #     ``default_visible_columns=("col1", "col2", ...)`` on
    #     the corresponding :class:`TeamDataset` entry.
    #   4. Confirm the UI renders the curated set on first
    #     load (the column toggle should still reveal the
    #     full set from :attr:`TeamDatasetCatalogEntry.columns`).
    # Decision needed: column-set ownership. The team-hub UI
    # is the consumer; the team-hub catalog should expose the
    # curated set as a *suggestion* (the player hub's
    # :attr:`ColumnMeta.default_visible` is a suggestion, not
    # a hard constraint). If the UI needs a "personal default"
    # per user, that lives in a per-user prefs store, not in
    # this catalog.
    # Verify: for each :class:`TeamDataset`, snapshot the
    #   catalog response and confirm
    #   ``entry['default_visible_columns']`` is non-empty AND
    #   a subset of ``set(c['key'] for c in entry['columns'])``.
    #   Then load ``/api/teams/BOS/{dataset}`` and confirm the
    #   UI's initial-render list matches.
    default_visible_columns: list[str]


# 13 team endpoint specs registered in ``courtside_data.endpoints._teams``.
# Keep this tuple ordered for stable catalog output.
#
# Scope classification is derived from the endpoint's ``params`` tuple
# (see ``courtside_data.endpoints._table._team``):
# - ``"team"`` → the EndpointSpec accepts only ``team_abbreviation``
#   (no season). Reachable from
#   ``/api/teams/{team_identifier}/{dataset}``.
# - ``"team_season"`` → the EndpointSpec accepts ``team_abbreviation`` and
#   ``season_end_year``. Reachable only from
#   ``/api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}``.
# This must stay in sync with the EndpointSpec declarations in
# ``courtside_data.endpoints._teams``; see ``tests/test_endpoint_metadata.py``
# for the cross-validation test.
#
# TODO(team-hub): add a regression test that asserts the
# scope/EndpointSpec params invariant below.
#
# What: every :class:`TeamDataset` whose ``endpoint_name`` resolves
# to an :class:`EndpointSpec` whose ``params`` includes
# ``"season_end_year"`` MUST be classified ``scope="team_season"``,
# and every :class:`TeamDataset` whose ``EndpointSpec.params`` does
# NOT include ``"season_end_year"`` MUST be classified
# ``scope="team"``. This invariant is hand-enforced today; a
# regression test in ``tests/test_endpoint_metadata.py`` would
# catch drift if a new team endpoint is added to
# :mod:`courtside_data.endpoints._teams` without updating this
# catalog.
# Where:
#   - courtside_data/endpoints/_table.py:170  (the ``_team``
#     helper whose default ``params=("team_abbreviation",
#     "season_end_year")`` is the source of the invariant).
#   - courtside_data/endpoints/_table.py:51  (the
#     ``EndpointSpec.params`` tuple declaration).
#   - tests/test_endpoint_metadata.py  (the cross-validation
#     test module that already loads ``TEAM_ENDPOINTS`` at line
#     19 — extend the existing test to also load
#     :data:`TEAM_DATASETS` and assert the invariant).
# How:
#   1. In ``tests/test_endpoint_metadata.py`` add a parametrized
#     test that, for every entry in :data:`TEAM_DATASETS`, looks
#     up ``ENDPOINTS[dataset.endpoint_name].params`` and asserts
#     ``("season_end_year" in spec.params) == (dataset.scope ==
#     "team_season")``.
#   2. Conversely, iterate every key in
#     :data:`courtside_data.endpoints._teams.TEAM_ENDPOINTS` and
#     assert the catalog has a matching entry whose
#     ``endpoint_name`` matches (no orphan endpoints, no orphan
#     catalog entries).
# Decision needed: parametrize vs. fixture-snapshot. The
# parametrized form (``@pytest.mark.parametrize`` over
# ``TEAM_DATASETS``) is one line per dataset; the snapshot form
# catches silent reclassifications but is harder to maintain
# when the dataset set grows.
# Verify: ``uv run pytest tests/test_endpoint_metadata.py -k
#   team_hub_scope_invariant -v`` -> all 13 entries pass.
#   Negative check: temporarily flip ``contracts`` to
#   ``scope="team_season"`` and re-run; the new test should
#   fail with a clear message.
TEAM_DATASETS: tuple[TeamDataset, ...] = (
    # ---- "team" scope: reachable from /api/teams/{team_identifier}/{dataset}
    # Only endpoints with no ``season_end_year`` param belong here.
    TeamDataset(
        id="contracts",
        label="Contracts",
        endpoint_name="team_contracts",
        scope="team",
        description="Multi-year contract obligations for the current roster.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="franchise-history",
        label="Franchise History",
        endpoint_name="franchise_history",
        scope="team",
        description="All-time franchise record, championships, and retired numbers.",
        default_visible_columns=[],
    ),
    # ---- "team_season" scope: reachable from /api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}
    # All endpoints whose EndpointSpec.params include ``season_end_year``.
    TeamDataset(
        id="roster",
        label="Roster",
        endpoint_name="team_roster",
        scope="team_season",
        description="Active roster with player bios, physicals, and contract status.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="transactions",
        label="Transactions",
        endpoint_name="team_transactions",
        scope="team_season",
        description="In-season trades, signings, waivers, and other moves.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="lineups",
        label="Lineups",
        endpoint_name="team_lineups",
        scope="team_season",
        description="Most-used five-man lineup combinations and their net rating.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="starting-lineups",
        label="Starting Lineups",
        endpoint_name="team_starting_lineups",
        scope="team_season",
        description="Per-game starting lineups and their net production.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="on-off",
        label="On/Off",
        endpoint_name="team_on_off",
        scope="team_season",
        description="Team performance with each player on vs. off the floor.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="injury-report",
        label="Injury Report",
        endpoint_name="team_injury_report",
        scope="team_season",
        description="Current league-wide injury list (team/season params accepted for API symmetry).",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="splits",
        label="Splits",
        endpoint_name="team_splits",
        scope="team_season",
        description="Win/loss, home/away, conference, and monthly splits for a season.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="and-opponent",
        label="Team & Opponent",
        endpoint_name="team_and_opponent",
        scope="team_season",
        description="Side-by-side team and opponent totals and rates.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="opponent-stats",
        label="Opponent Stats",
        endpoint_name="team_opponent_stats",
        scope="team_season",
        description="Opponent production allowed (same table as Team & Opponent, opponent column set).",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="misc-four-factors",
        label="Misc / Four Factors",
        endpoint_name="team_misc_four_factors",
        scope="team_season",
        description="Dean Oliver's four factors and miscellaneous team metrics for a season.",
        default_visible_columns=[],
    ),
    TeamDataset(
        id="schedule",
        label="Schedule",
        endpoint_name="team_schedule",
        scope="team_season",
        description="Game-by-game schedule and box-score links for a season.",
        default_visible_columns=[],
    ),
)


# Re-export the module-level helper under the team_catalog namespace so the
# service layer can call ``team_columns_for_dataset`` symmetrically.
column_label = column_label


_TEAM_NUMERIC_HINTS = (
    "games",
    "points",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "percentage",
    "rating",
    "minutes",
    "wins",
    "losses",
    "made_",
    "attempted_",
    "plus_minus",
    "rank",
    "year",
    "age",
    "salary",
    "height",
    "weight",
    "score",
)


def team_column_meta_for_key(key: str, *, default_visible: bool) -> ColumnMeta:
    """Build a :class:`ColumnMeta` for one team-hub column key.

    Mirrors :func:`courtside_data.server.catalog.column_meta_for_key`; the
    hint set is widened for team-specific column shapes (rank, score, year,
    age, salary, height, weight, etc.).
    """
    lowered = key.lower()
    numeric = any(hint in lowered for hint in _TEAM_NUMERIC_HINTS)
    return ColumnMeta(key=key, label=column_label(key), default_visible=default_visible, numeric=numeric)


def team_columns_for_dataset(dataset: TeamDataset, sample_row: dict[str, Any] | None = None) -> list[ColumnMeta]:
    """Resolve the :class:`ColumnMeta` list for a team dataset.

    Mirrors :func:`courtside_data.server.catalog.columns_for_dataset`; the
    default-visible set is read from ``dataset.default_visible_columns``
    (which is empty in the current scaffolding — see the TODO on
    :class:`TeamDataset`).
    """
    endpoint = ENDPOINTS[dataset.endpoint_name]
    keys = list(sample_row) if sample_row is not None else list(endpoint.row_model.model_fields)
    defaults = set(dataset.default_visible_columns)
    return [team_column_meta_for_key(key, default_visible=key in defaults) for key in keys]


def team_dataset_entry(dataset: TeamDataset) -> TeamDatasetCatalogEntry:
    """Build a :class:`TeamDatasetCatalogEntry` payload for one dataset.

    Mirrors :func:`courtside_data.server.catalog.dataset_entry`; uses the
    team-scope literal for ``scope``.
    """
    return TeamDatasetCatalogEntry(
        id=dataset.id,
        label=dataset.label,
        endpoint_name=dataset.endpoint_name,
        scope=dataset.scope,
        description=dataset.description,
        columns=team_columns_for_dataset(dataset),
        default_visible_columns=list(dataset.default_visible_columns),
    )


def team_dataset_by_id(dataset_id: str) -> TeamDataset:
    """Look up a :class:`TeamDataset` by its catalog id.

    Raises :class:`ValueError` (mirroring ``catalog.dataset_by_id``) if the
    id is not registered.
    """
    for dataset in TEAM_DATASETS:
        if dataset.id == dataset_id:
            return dataset
    raise ValueError(f"Unknown Team Hub dataset: {dataset_id}")


# Tabs group the 13 datasets into a small set of UI surfaces. They mirror
# the ``TABS`` tuple in catalog.py but are reshaped for team content.
#
# A tab's ``scope`` is its *primary* scope (drives the default landing
# route); the tab may contain datasets of either scope, mirroring how
# the player hub's ``playoffs`` tab groups a ``player``-scoped dataset
# with a ``season``-scoped one. The dataset-level ``scope`` is what the
# route guard checks, not the tab's.
TEAM_TABS: tuple[TeamHubTab, ...] = (
    TeamHubTab(
        id="overview",
        label="Overview",
        description="Franchise history, hero metrics, and current roster.",
        scope="team",
        datasets=["franchise-history", "contracts", "roster", "injury-report"],
        default_dataset="franchise-history",
    ),
    TeamHubTab(
        id="roster",
        label="Roster",
        description="Roster, contracts, and injury report.",
        scope="team_season",
        datasets=["roster", "contracts", "injury-report"],
        default_dataset="roster",
    ),
    TeamHubTab(
        id="season",
        label="Season",
        description="Selected-season team-level splits, on/off, and four factors.",
        scope="team_season",
        datasets=["splits", "on-off", "and-opponent", "opponent-stats", "misc-four-factors"],
        default_dataset="splits",
    ),
    TeamHubTab(
        id="lineups",
        label="Lineups",
        description="Five-man lineups and per-game starting lineups.",
        scope="team_season",
        datasets=["lineups", "starting-lineups"],
        default_dataset="lineups",
    ),
    TeamHubTab(
        id="schedule",
        label="Schedule & Transactions",
        description="Game schedule and in-season transactions.",
        scope="team_season",
        datasets=["schedule", "transactions"],
        default_dataset="schedule",
    ),
)


def team_hub_catalog() -> dict[str, object]:
    """Return the Team Hub catalog payload.

    Return shape mirrors :func:`courtside_data.server.catalog.player_hub_catalog`:
    a dict with a ``tabs`` list and a ``datasets`` list of catalog-entry
    dicts. The ``datasets`` key is a list (not a map) to match the player
    hub shape exactly; clients index by ``entry["id"]``.
    """
    return {
        "tabs": [tab.model_dump(mode="json") for tab in TEAM_TABS],
        "datasets": [team_dataset_entry(dataset).model_dump(mode="json") for dataset in TEAM_DATASETS],
    }
