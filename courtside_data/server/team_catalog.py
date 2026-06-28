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
    default_visible_columns: tuple[str, ...]


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
# ``courtside_data.endpoints._teams``; the invariant is enforced by
# ``tests/test_endpoint_metadata.py::test_team_hub_scope_matches_endpoint_season_param``
# (parametrized over :data:`TEAM_DATASETS`) and the catalog/registry
# parity check ``tests/test_endpoint_metadata.py::test_team_hub_catalog_covers_every_team_endpoint``.
#
# Scope classification is derived from the endpoint's ``params`` tuple
# (see ``courtside_data.endpoints._table._team``):
# - ``"team"`` → the EndpointSpec accepts only ``team_abbreviation``
#   (no season). Reachable from
#   ``/api/teams/{team_identifier}/{dataset}``.
# - ``"team_season"`` → the EndpointSpec accepts ``team_abbreviation`` and
#   ``season_end_year``. Reachable only from
#   ``/api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}``.
# Every :class:`TeamDataset` whose ``endpoint_name`` resolves to an
# :class:`EndpointSpec` whose ``params`` includes ``"season_end_year"``
# MUST be classified ``scope="team_season"``; every entry whose
# ``EndpointSpec.params`` does NOT include ``"season_end_year"`` MUST
# be classified ``scope="team"``. The regression tests catch drift if
# a new team endpoint is added to :mod:`courtside_data.endpoints._teams`
# without updating this catalog.
TEAM_DATASETS: tuple[TeamDataset, ...] = (
    # ---- "team" scope: reachable from /api/teams/{team_identifier}/{dataset}
    # Only endpoints with no ``season_end_year`` param belong here.
    TeamDataset(
        id="contracts",
        label="Contracts",
        endpoint_name="team_contracts",
        scope="team",
        description="Multi-year contract obligations for the current roster.",
        default_visible_columns=("player", "age_today", "y1", "y2", "y3", "remain_gtd"),
    ),
    TeamDataset(
        id="franchise-history",
        label="Franchise History",
        endpoint_name="franchise_history",
        scope="team",
        description="All-time franchise record, championships, and retired numbers.",
        default_visible_columns=("season", "lg_id", "team_name", "wins", "losses", "win_loss_pct", "rank_team"),
    ),
    # ---- "team_season" scope: reachable from /api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}
    # All endpoints whose EndpointSpec.params include ``season_end_year``.
    TeamDataset(
        id="roster",
        label="Roster",
        endpoint_name="team_roster",
        scope="team_season",
        description="Active roster with player bios, physicals, and contract status.",
        default_visible_columns=("player", "number", "positions", "height", "weight", "years_experience", "college"),
    ),
    TeamDataset(
        id="transactions",
        label="Transactions",
        endpoint_name="team_transactions",
        scope="team_season",
        description="In-season trades, signings, waivers, and other moves.",
        default_visible_columns=("date", "transaction", "from_team_abbreviations", "to_team_abbreviations"),
    ),
    TeamDataset(
        id="lineups",
        label="Lineups",
        endpoint_name="team_lineups",
        scope="team_season",
        description="Most-used five-man lineup combinations and their net rating.",
        default_visible_columns=("lineup", "seconds_played", "diff_pts", "diff_efg_pct", "diff_trb_pct", "diff_ast"),
    ),
    TeamDataset(
        id="starting-lineups",
        label="Starting Lineups",
        endpoint_name="team_starting_lineups",
        scope="team_season",
        description="Per-game starting lineups and their net production.",
        default_visible_columns=("g", "date_game", "opp_name", "game_result", "pts", "opp_pts", "game_starters"),
    ),
    TeamDataset(
        id="on-off",
        label="On/Off",
        endpoint_name="team_on_off",
        scope="team_season",
        description="Team performance with each player on vs. off the floor.",
        default_visible_columns=("player", "split_id", "mp", "off_rtg", "opp_off_rtg", "diff_off_rtg", "diff_efg_pct"),
    ),
    TeamDataset(
        id="injury-report",
        label="Injury Report",
        endpoint_name="team_injury_report",
        scope="team_season",
        description="Current league-wide injury list (team/season params accepted for API symmetry).",
        default_visible_columns=("player", "team_name", "date_update", "note"),
    ),
    TeamDataset(
        id="splits",
        label="Splits",
        endpoint_name="team_splits",
        scope="team_season",
        description="Win/loss, home/away, conference, and monthly splits for a season.",
        default_visible_columns=("split_value", "g", "wins", "losses", "pts", "opp_pts", "fg_pct", "opp_fg_pct"),
    ),
    TeamDataset(
        id="and-opponent",
        label="Team & Opponent",
        endpoint_name="team_and_opponent",
        scope="team_season",
        description="Side-by-side team and opponent totals and rates.",
        default_visible_columns=("g", "pts", "opp_pts", "fg_pct", "opp_fg_pct", "trb", "opp_trb", "ast"),
    ),
    TeamDataset(
        id="opponent-stats",
        label="Opponent Stats",
        endpoint_name="team_opponent_stats",
        scope="team_season",
        description="Opponent production allowed (same table as Team & Opponent, opponent column set).",
        default_visible_columns=("g", "opp_pts", "opp_fg_pct", "opp_fg3_pct", "opp_ft_pct", "opp_trb", "opp_ast"),
    ),
    TeamDataset(
        id="misc-four-factors",
        label="Misc / Four Factors",
        endpoint_name="team_misc_four_factors",
        scope="team_season",
        description="Dean Oliver's four factors and miscellaneous team metrics for a season.",
        default_visible_columns=("wins", "losses", "mov", "srs", "off_rtg", "def_rtg", "pace", "efg_pct"),
    ),
    TeamDataset(
        id="schedule",
        label="Schedule",
        endpoint_name="team_schedule",
        scope="team_season",
        description="Game-by-game schedule and box-score links for a season.",
        default_visible_columns=("g", "date_game", "opp_name", "game_result", "pts", "opp_pts", "wins", "losses"),
    ),
)


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
    default-visible set is read from ``dataset.default_visible_columns``.
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
