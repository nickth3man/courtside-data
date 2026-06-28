"""League Hub dataset catalog (STUB).

See ``docs/architecture/league-hub.md`` for the full implementation
roadmap. This file is a placeholder - populate it by mirroring
:mod:`courtside_data.server.team_catalog`.
"""

from __future__ import annotations

from typing import Literal

# TODO(league-hub): Implement the League Hub catalog by mirroring
# courtside_data/server/team_catalog.py. Full plan in
# docs/architecture/league-hub.md.
#
# What: define ``LEAGUE_DATASETS`` (11 entries), ``LEAGUE_TABS``,
# :func:`league_hub_catalog`, and column-derivation helpers. Mirror
# the :class:`courtside_data.server.team_catalog.TeamDataset` frozen
# dataclass as :class:`LeagueDataset` (same field set, swapped
# ``scope`` literal).
# Where (read first):
#   - courtside_data/server/team_catalog.py  (the 426-line proven
#     pattern; same shape, same field names).
#   - courtside_data/server/team_models.py  (the
#     :class:`TeamDatasetCatalogEntry` / :class:`TeamHubTab`
#     Pydantic models - mirror as
#     :class:`LeagueDatasetCatalogEntry` and :class:`LeagueHubTab`).
#   - courtside_data/endpoints/_league.py:96-256  (the 11
#     :data:`LEAGUE_ENDPOINTS` entries; the source of truth for
#     ``params``, ``path``, ``metadata.scope``, and ``metadata.kind``).
#   - courtside_data/schemas/league.py  (the 9 row models; locations
#     in the next comment block).
#   - courtside_data/schemas/standings.py:28,53  (``StandingsRow``
#     and ``StandingsByDateRow``).
# How (per the roadmap in docs/architecture/league-hub.md section 4):
#   1. Define :class:`LeagueDatasetScope` literal (this module,
#      already drafted below).
#   2. Define the :class:`LeagueDataset` frozen dataclass (mirror
#      :class:`TeamDataset` exactly).
#   3. Populate :data:`LEAGUE_DATASETS` with 11 entries - the
#      per-endpoint shape is documented as a comment block below
#      (read :mod:`courtside_data.endpoints._league` to verify the
#      params, scope, and row model for each).
#   4. Group the 11 datasets into :data:`LEAGUE_TABS` (proposed
#      grouping in the roadmap section 4).
#   5. Implement :func:`league_hub_catalog` returning
#      ``{"tabs": [...], "datasets": [...]}`` (mirror
#      :func:`courtside_data.server.team_catalog.team_hub_catalog`).
#   6. Implement :func:`league_columns_for_dataset` and
#      :func:`league_column_meta_for_key` (mirror
#      :func:`team_columns_for_dataset`; widen the numeric-hint
#      set to cover league-specific columns like ``arena_name``,
#      ``attendance_per_g``).
#   7. Implement :func:`league_dataset_entry` returning a
#      :class:`LeagueDatasetCatalogEntry`.
# Decision needed: whether :class:`LeagueDatasetScope` is a brand
# new literal (``"league" / "league_season" / "league_date"``) or
# reuses the existing :data:`courtside_data.server.models.DatasetScope`
# literal (``"player" / "season"``). The first option is
# consistent with the team hub's brand-new ``"team" / "team_season"``
# literal; the second option reuses an existing literal. The roadmap
# recommends a brand-new literal for symmetry with Team Hub.
# Verify: ``uv run pytest tests -n auto`` (must stay green - this
#   stub does not export any code that other modules import yet),
#   then a manual ``TestClient(create_app(transport='live')).get(
#   '/api/endpoints/league-hub')`` once the implementation lands.

LeagueDatasetScope = Literal["league", "league_season", "league_date", "league_static"]
"""Scope values for League Hub datasets.

Mirrors :data:`courtside_data.server.team_models.TeamDatasetScope`
but adds a ``league_date`` literal for ``standings_by_date`` (whose
EndpointSpec has ``scope=EndpointScope.SEASON`` but conceptually
operates on a month/day/year triple, not a single season). All
other league endpoints are ``league_season``. ``league_static`` is
reserved for future endpoints with no params (none exist in the
LEAGUE_ENDPOINTS registry today; STATIC is currently a
PLAYOFFS/DRAFT_AWARDS_LEADERS concern).
"""


# ---------------------------------------------------------------------------
# Proposed LEAGUE_DATASETS structure (11 entries, in catalog order)
# ---------------------------------------------------------------------------
#
# Mirror :data:`courtside_data.server.team_catalog.TEAM_DATASETS`.
# Scope is derived from the EndpointSpec ``scope`` and ``params``:
# every LEAGUE_ENDPOINTS entry has ``params=("season_end_year",)``
# (or ``("month", "day", "year")`` for standings_by_date), so all 11
# are ``league_season`` or ``league_date``. The proposed group order
# matches the UI's "Stats" / "Transactions" / "Standings" /
# "Attendance" tab structure documented in
# docs/architecture/league-hub.md section 4.
#
# Stats tab (6 entries; all GENERIC_TABLE / TABLE):
#
#   per-game            league_per_game_stats          league_season
#     spec: _league.py:96
#     row_model: LeaguePerGameStatsRow (schemas/league.py:68)
#
#   per-36-minutes      league_per_36_minutes         league_season
#     spec: _league.py:111
#     row_model: LeaguePer36MinutesRow (schemas/league.py:161)
#
#   totals              league_totals                 league_season
#     spec: _league.py:126
#     row_model: LeagueTotalsRow (schemas/league.py:86)
#
#   per-100-possessions league_per_100_possessions    league_season
#     spec: _league.py:141 (min_year=1974)
#     row_model: LeaguePer100PossessionsRow (schemas/league.py:205)
#
#   shooting            league_shooting               league_season
#     spec: _league.py:157
#     row_model: LeagueShootingRow (schemas/league.py:252)
#
#   play-by-play        league_play_by_play           league_season
#     spec: _league.py:172
#     row_model: LeaguePlayByPlayRow (schemas/league.py:313)
#
# Transactions tab (2 entries):
#
#   transactions        league_transactions           league_season
#     spec: _league.py:187
#     row_model: LeagueTransactionRow (schemas/league.py:350)
#     parser shape: TRANSACTION_LIST (uses the transaction-list parser)
#
#   rookies             rookie_stats                  league_season
#     spec: _league.py:202
#     row_model: RookieStatsRow (schemas/league.py:113)
#
# Standings tab (2 entries; both WORKFLOW):
#
#   standings           standings                     league_season
#     spec: _league.py:216
#     row_model: StandingsRow (schemas/standings.py:28)
#     parser shape: STANDINGS_BLOCKS (workflow endpoint; both conference
#       tables parsed by the workflow)
#
#   standings-by-date   standings_by_date             league_date
#     spec: _league.py:230
#     row_model: StandingsByDateRow (schemas/standings.py:53)
#     parser shape: MULTI_TABLE (workflow fans out to both conferences)
#     Notes: UNIQUE across all 3 new hubs - this is the only
#     date-scoped dataset. Declared params are ("season_end_year",)
#     at the EndpointSpec level but the route layer is expected to
#     accept month/day/year query params per the workflow's
#     expand_conferences step.
#
# Attendance tab (1 entry):
#
#   attendance          attendance                     league_season
#     spec: _league.py:256
#     row_model: AttendanceRow (schemas/league.py:371)
#     Notes: EndpointSpec.projection is a 4-tuple narrowing the row
#     payload to (team, arena_name, attendance, attendance_per_g).


__all__ = [
    "LeagueDatasetScope",
]
