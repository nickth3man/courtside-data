"""Playoffs Hub dataset catalog (STUB).

See ``docs/architecture/playoffs-hub.md`` for the full implementation
roadmap. This file is a placeholder - populate it by mirroring
:mod:`courtside_data.server.team_catalog`.
"""

from __future__ import annotations

from typing import Literal

# TODO(playoffs-hub): Implement the Playoffs Hub catalog by mirroring
# courtside_data/server/team_catalog.py. Full plan in
# docs/architecture/playoffs-hub.md.
#
# What: define ``PLAYOFFS_DATASETS`` (6 entries), ``PLAYOFFS_TABS``,
# :func:`playoffs_hub_catalog`, and column-derivation helpers. Mirror
# the :class:`courtside_data.server.team_catalog.TeamDataset` frozen
# dataclass as :class:`PlayoffsDataset`.
# Where (read first):
#   - courtside_data/server/team_catalog.py  (the 426-line proven
#     pattern).
#   - courtside_data/server/team_models.py  (mirror
#     :class:`TeamDatasetCatalogEntry` as
#     :class:`PlayoffsDatasetCatalogEntry` and
#     :class:`TeamHubTab` as :class:`PlayoffsHubTab`).
#   - courtside_data/endpoints/_playoffs.py:90-181  (the 6
#     :data:`PLAYOFF_ENDPOINTS` entries; verify the
#     ``metadata.scope`` for each: 3 are SEASON, 3 are STATIC).
#   - courtside_data/schemas/playoffs.py:49,68,101,134  (the 4
#     distinct row models - the 3 friv_7 endpoints share
#     :class:`SevenGamePlayoffSeriesOutcomesRow`).
# How (per the roadmap in docs/architecture/playoffs-hub.md section 4):
#   1. Define :class:`PlayoffsDatasetScope` literal (this module,
#      already drafted below).
#   2. Define the :class:`PlayoffsDataset` frozen dataclass (mirror
#      :class:`TeamDataset` exactly).
#   3. Populate :data:`PLAYOFFS_DATASETS` with 6 entries - the
#      per-endpoint shape is documented as a comment block below
#      (read :mod:`courtside_data.endpoints._playoffs` to verify).
#   4. Group the 6 datasets into :data:`PLAYOFFS_TABS` (proposed
#      grouping in the roadmap section 4: "Player Stats" /
#      "Bracket" / "Series Patterns").
#   5. Implement :func:`playoffs_hub_catalog` returning
#      ``{"tabs": [...], "datasets": [...]}``.
#   6. Implement :func:`playoffs_columns_for_dataset` and
#      :func:`playoffs_column_meta_for_key` (mirror
#      :func:`team_columns_for_dataset`; widen the numeric-hint
#      set to cover playoff-specific columns like ``series``,
#      ``result``, ``games_played``, ``wins``, ``losses``).
# Decision needed: where to put the 3
# ``friv_7_game_playoff_series_outcomes_*`` endpoints (3 STATIC
# endpoints with the same row model). Three options:
#   (a) one tab "Series Patterns" with 3 datasets
#   (b) one dataset "seven-game-series-patterns" with a
#       "state" param (``up`` / ``down`` / ``tied``) - this requires
#       a new EndpointSpec wrapper or a query-param switch in
#       the route
#   (c) 3 separate routes under a single tab, one per state
# The roadmap recommends (c) for parity with how the EndpointSpec
# splits them today; (a) is functionally equivalent and a
# cleaner UI surface.
# Verify: ``uv run pytest tests -n auto`` must stay green (this
#   stub does not export any code that other modules import yet).
#   After implementation: a manual
#   ``TestClient(create_app(transport='live')).get(
#   '/api/endpoints/playoffs-hub')`` returns the catalog with
#   6 datasets and 3 tabs.

PlayoffsDatasetScope = Literal["playoffs_season", "playoffs_static"]
"""Scope values for Playoffs Hub datasets.

- ``playoffs_season``: keyed by ``season_end_year`` (``playoff_per_game``,
  ``playoff_totals``, ``playoff_bracket``). Reachable from
  ``/api/playoffs/seasons/{season_end_year}/{dataset}``.
- ``playoffs_static``: no params (the 3
  ``friv_7_game_playoff_series_outcomes_*`` endpoints). Reachable
  from ``/api/playoffs/{dataset}``.

This mirrors the :data:`courtside_data.server.team_models.TeamDatasetScope`
split (``"team"`` / ``"team_season"``) and is the smallest of the
three new hubs' scope sets (only 2 values, no date scope).
"""


# ---------------------------------------------------------------------------
# Proposed PLAYOFFS_DATASETS structure (6 entries)
# ---------------------------------------------------------------------------
#
# Mirror :data:`courtside_data.server.team_catalog.TEAM_DATASETS`.
# Scope is derived from the EndpointSpec ``metadata.scope``:
# - 3 are ``playoffs_season`` (all keyed by ``season_end_year``)
# - 3 are ``playoffs_static`` (the 3 friv_7 endpoints, no params)
#
# Player Stats tab (2 entries; GENERIC_TABLE / COMMENTED_TABLE):
#
#   per-game            playoff_per_game              playoffs_season
#     spec: _playoffs.py:90
#     row_model: PlayoffPerGameRow (schemas/playoffs.py:49)
#     parser shape: COMMENTED_TABLE (table id "per_game_stats_post"
#       inside an HTML comment block on the league per-game page)
#
#   totals              playoff_totals                playoffs_season
#     spec: _playoffs.py:106
#     row_model: PlayoffTotalsRow (schemas/playoffs.py:68)
#     parser shape: COMMENTED_TABLE
#
# Bracket tab (1 entry; WORKFLOW):
#
#   bracket             playoff_bracket               playoffs_season
#     spec: _playoffs.py:122
#     row_model: PlayoffBracketRow (schemas/playoffs.py:101)
#     parser shape: BRACKET (workflow fetches the playoff page,
#       selects table#all_playoffs, parses the series/team/result rows)
#     Notes: the table is manually-laid-out and cells often lack
#       data-stat attributes, so the row model uses normalised
#       header text as validation_alias keys.
#
# Series Patterns tab (3 entries; WORKFLOW / STATIC):
#
#   series-pattern-team-is-up      friv_7_game_playoff_series_outcomes_team_is_up       playoffs_static
#     spec: _playoffs.py:166
#     row_model: SevenGamePlayoffSeriesOutcomesRow (schemas/playoffs.py:134)
#     parser shape: TABLE (workflow selects table#team-is-up, parses
#       the W-L outcome matrix for the "up 3-2" state)
#     Notes: no params. The page is the single static
#       /friv/7-game-playoff-series-outcomes-22111.html which carries
#       three sibling tables (one per state); the table_id differs
#       per endpoint.
#
#   series-pattern-team-is-tied    friv_7_game_playoff_series_outcomes_team_is_tied     playoffs_static
#     spec: _playoffs.py:151
#     row_model: SevenGamePlayoffSeriesOutcomesRow (schemas/playoffs.py:134)
#     parser shape: TABLE (selects table#team-is-tied)
#
#   series-pattern-team-is-down    friv_7_game_playoff_series_outcomes_team_is_down     playoffs_static
#     spec: _playoffs.py:136
#     row_model: SevenGamePlayoffSeriesOutcomesRow (schemas/playoffs.py:134)
#     parser shape: TABLE (selects table#team-is-down)
#     Notes: All three friv_7 endpoints share the same
#       SevenGamePlayoffSeriesOutcomesRow schema; the only
#       difference is the table_id selector and the dataset id.


__all__ = [
    "PlayoffsDatasetScope",
]
