"""Draft / Awards / Leaders Hub dataset catalog (STUB).

See ``docs/architecture/draft-awards-hub.md`` for the full
implementation roadmap. This file is a placeholder - populate it by
mirroring :mod:`courtside_data.server.team_catalog`.
"""

from __future__ import annotations

from typing import Literal

# TODO(draft-awards-hub): Implement the Draft/Awards/Leaders Hub
# catalog by mirroring courtside_data/server/team_catalog.py. Full
# plan in docs/architecture/draft-awards-hub.md.
#
# What: define ``DRAFT_AWARDS_DATASETS`` (5 entries),
# ``DRAFT_AWARDS_TABS``, :func:`draft_awards_hub_catalog`, and
# column-derivation helpers. Mirror
# :class:`courtside_data.server.team_catalog.TeamDataset` as
# :class:`DraftAwardsDataset`.
# Where (read first):
#   - courtside_data/server/team_catalog.py  (the 426-line proven
#     pattern).
#   - courtside_data/server/team_models.py  (mirror the
#     :class:`TeamDatasetCatalogEntry` / :class:`TeamHubTab`
#     Pydantic models as
#     :class:`DraftAwardsDatasetCatalogEntry` and
#     :class:`DraftAwardsHubTab`).
#   - courtside_data/endpoints/_draft_awards_leaders.py:65-163
#     (the 5 :data:`DRAFT_AWARDS_LEADERS_ENDPOINTS` entries;
#     verify ``params`` and ``metadata.scope`` for each - 3 are
#     SEASON, 2 are STATIC).
#   - courtside_data/schemas/draft.py:27  (``DraftPicksRow``).
#   - courtside_data/schemas/awards.py:25,61,89,111  (``SeasonAwardsRow``,
#     ``SeasonAwardsVotingRow``, ``SeasonLeadersRow``,
#     ``CareerLeadersRow``).
# How (per the roadmap in docs/architecture/draft-awards-hub.md
# section 4):
#   1. Define :class:`DraftAwardsDatasetScope` literal (this
#      module, already drafted below).
#   2. Define the :class:`DraftAwardsDataset` frozen dataclass
#      (mirror :class:`TeamDataset`).
#   3. Populate :data:`DRAFT_AWARDS_DATASETS` with 5 entries -
#      the per-endpoint shape is documented as a comment block
#      below.
#   4. Group the 5 datasets into :data:`DRAFT_AWARDS_TABS`
#      (proposed grouping in the roadmap section 4: "Draft" /
#      "Awards" / "Leaders"). The ``season_awards_voting`` workflow
#      needs a tab-level ``award`` selector (MVP, DPOY, ROY, ...) -
#      the design decision is documented in the roadmap section 8.
#   5. Implement :func:`draft_awards_hub_catalog` returning
#      ``{"tabs": [...], "datasets": [...]}``.
#   6. Implement :func:`draft_awards_columns_for_dataset` and
#      :func:`draft_awards_column_meta_for_key` (mirror
#      :func:`team_columns_for_dataset`; widen the numeric-hint
#      set to cover awards-specific columns like ``votes``, ``age``,
#      ``team``, ``games``, ``minutes_played``).
# Decision needed: how to expose ``season_awards_voting``. The
# EndpointSpec takes ``params=("season_end_year", "award")`` and
# uses ``fallback_table_ids=("mvp", "roy", "dpoy", "smoy", "mip",
# "clutch_poy", "coy", "leading_all_nba", "leading_all_defense",
# "leading_all_rookie")`` (10 awards). The UI can either:
#   (a) Show one ``season_awards_voting`` tab with an "award"
#       selector (dropdown of the 10 awards). The route signature
#       becomes ``/api/draft-awards/seasons/{year}/awards-voting?
#       award=mvp``.
#   (b) Create 10 sub-datasets, one per award (e.g. ``mvp-voting``,
#       ``roy-voting``). The route is per-dataset with no extra
#       query param.
#   (c) One dataset for the default ``mvp`` table plus a
#       query-param override for the other 9. Compromise between
#       (a) and (b).
# The roadmap recommends (a) for UI flexibility; (b) is the cleanest
# catalog surface; (c) is the smallest implementation delta.
# Verify: ``uv run pytest tests -n auto`` must stay green (this
#   stub does not export any code that other modules import yet).
#   After implementation: a manual
#   ``TestClient(create_app(transport='live')).get(
#   '/api/endpoints/draft-awards-hub')`` returns the catalog with
#   5 datasets.

DraftAwardsDatasetScope = Literal["draft_awards_season", "draft_awards_static"]
"""Scope values for Draft/Awards/Leaders Hub datasets.

- ``draft_awards_season``: keyed by ``season_end_year``
  (``draft_picks``, ``season_awards``, ``season_awards_voting``;
  the last also takes an ``award`` param per the
  EndpointSpec.fallback_table_ids list).
- ``draft_awards_static``: no params (``season_leaders``,
  ``career_leaders``).

This mirrors :data:`courtside_data.server.team_models.TeamDatasetScope`
and :data:`courtside_data.server.playoffs_catalog.PlayoffsDatasetScope`.
Note that ``season_leaders`` and ``career_leaders`` are
*endpoint-namespace* STATIC, not *cross-season* static: the
``per_season.html`` page (for ``season_leaders``) does have an
implicit season selector on the page itself; if a future endpoint
wants a per-season "leaders" page it would need its own
``season_end_year`` param. For today both are no-param.
"""


# ---------------------------------------------------------------------------
# Proposed DRAFT_AWARDS_DATASETS structure (5 entries)
# ---------------------------------------------------------------------------
#
# Mirror :data:`courtside_data.server.team_catalog.TEAM_DATASETS`.
# Scope is derived from the EndpointSpec ``metadata.scope``:
# - 3 are ``draft_awards_season``
# - 2 are ``draft_awards_static``
#
# Draft tab (1 entry; GENERIC_TABLE / TABLE):
#
#   draft-picks         draft_picks                   draft_awards_season
#     spec: _draft_awards_leaders.py:66
#     row_model: DraftPicksRow (schemas/draft.py:27)
#     parser shape: TABLE
#
# Awards tab (2 entries; the second is a WORKFLOW):
#
#   season-awards       season_awards                 draft_awards_season
#     spec: _draft_awards_leaders.py:79
#     row_model: SeasonAwardsRow (schemas/awards.py:25)
#     parser shape: TABLE
#     Notes: fallback_table_ids is ("nba_mvp",) per the EndpointSpec;
#     the page also exposes a sibling "roy" table but the EndpointSpec
#     only defaults to MVP today.
#
#   season-awards-voting  season_awards_voting        draft_awards_season
#     spec: _draft_awards_leaders.py:94
#     row_model: SeasonAwardsVotingRow (schemas/awards.py:61)
#     parser shape: TABLE (workflow normalises the ``award`` param
#       into a table_id via the normalize_award_id step)
#     Notes: declared params are ("season_end_year", "award");
#     fallback_table_ids lists 10 awards (mvp, roy, dpoy, smoy, mip,
#     clutch_poy, coy, leading_all_nba, leading_all_defense,
#     leading_all_rookie). The route layer MUST accept ``award``
#     as a query param or path segment; see the Decision needed
#     above for the 3 options.
#
# Leaders tab (2 entries; both STATIC, both with value_column=True):
#
#   season-leaders      season_leaders                draft_awards_static
#     spec: _draft_awards_leaders.py:122
#     row_model: SeasonLeadersRow (schemas/awards.py:89)
#     parser shape: TABLE
#     Notes: EndpointSpec.value_column=True (the third column header
#     rotates with the active stat category: "per", "pts", "ast"...);
#     the parser renames it to a stable "value" key so the row
#     model validates.
#
#   career-leaders      career_leaders                draft_awards_static
#     spec: _draft_awards_leaders.py:141
#     row_model: CareerLeadersRow (schemas/awards.py:111)
#     parser shape: TABLE
#     Notes: as above (value_column=True). The path
#     /leaders/pts_career.html is the canonical career-points
#     leaderboard (table#tot, columns Rank/Player/PTS); this is
#     re-registered from /leaders/ (a navigation index) which
#     BR changed to a non-rank/player/value layout.


__all__ = [
    "DraftAwardsDatasetScope",
]
