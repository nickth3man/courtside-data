"""Games/Browser Hub dataset and tab catalog stub.

TODO(games-hub): replace this scaffolding with the real catalog once the
Games/Browser Hub lane lands.

See ``docs/architecture/games-browser-hub.md`` for the full design context.
That document is the source of truth for:

  - Why this domain does NOT fit the entity-Hub pattern (Player Hub,
    Team Hub) and instead spans four different interaction models
    (per-game box scores, daily leaders, play-by-play, league-season
    tables).
  - The game-identification scheme that drives the per-game box-score
    routes (the format ``{YYYYMMDD}0{HOMETEAM_ABBR}`` -- see
    ``_workflows.py:541-642`` for the 6 box-score endpoint
    registrations and ``games-browser-hub.md`` section 3 for the full
    rationale).
  - Why the catalog concept does NOT apply cleanly here, and what the
    proposed alternative is (a fixed six-tab box-score viewer plus a
    separate "league season" view for the SEASON-scoped datasets that
    architecturally belong in the League Hub).

What lives in this module today is just enough surface for the
inline TODOs in ``courtside_data/server/app.py`` and
``courtside_data/server/fixtures.py`` to point at without circular
imports. The :data:`GamesDatasetScope` literal mirrors the three
non-entity scopes the GAMES domain actually uses; the 12 endpoint
names are documented as comments for cross-referencing only.

Why a stub, not a full port of the Team Hub catalog pattern
============================================================

The Team Hub catalog (``courtside_data/server/team_catalog.py``) is
shaped around the "team" entity: 13 datasets grouped into 5 tabs
(overview / roster / season / lineups / schedule), each driven by a
``team_identifier`` path parameter and (for the team-season scope) a
``season_end_year`` path parameter.

The GAMES domain has NO such anchor entity. Its 12 unreachable
endpoints split across four different interaction models (see
``docs/architecture/games-browser-hub.md`` section 1), each with its
own URL shape:

  1. Six per-game box scores share one URL
     (``/boxscores/{game_id}.html``) and are accessed via a fixed set
     of 6 tabs in the UI. There is no "catalog" of box-score datasets
     to enumerate -- every game exposes the same 6.
  2. Two daily-leaders endpoints (``player_box_scores``,
     ``team_box_scores``) take ``day/month/year`` and return every
     game that happened on that date. The natural UI surface is a
     date picker, not a catalog.
  3. One play-by-play endpoint (``play_by_play``) takes
     ``day/month/year/home_team`` and returns the event stream for
     one game. Same date-picker + game-list UX as daily leaders.
  4. Three season-scoped endpoints (``season_schedule``,
     ``players_season_totals``, ``players_advanced_season_totals``)
     take ``season_end_year`` and return league-wide tables. These
     architecturally belong in the **League Hub** (see
     ``docs/architecture/endpoint-roadmap.md``) and the recommended
     design decision (section 9 of the games doc) is to move them.

For the box-score viewer (interaction model 1), the catalog shape is
fixed and known at compile time -- there is no benefit in serializing
it from this module. A constant here would duplicate the EndpointSpec
list verbatim; the route layer can hard-code the six box-score
dataset ids in the same way that the catalog has historically been a
hand-maintained mirror of the EndpointSpec registry.

For the season-scoped datasets (interaction model 4), the right home
is the League Hub catalog (a future ``courtside_data/server/
league_catalog.py``), not a Games Hub catalog. Moving them keeps the
"Games Browser" surface honest about being per-game / per-date
content only.

What to do when the lane lands
==============================

When the Games Hub implementation lane opens, the actual catalog
shape that should ship is roughly::

    # Six fixed box-score datasets -- one per game, no per-game
    # catalog to enumerate.
    BOX_SCORE_DATASETS: tuple[BoxScoreDataset, ...] = (
        BoxScoreDataset(id="box-score-player-basic", ...),
        BoxScoreDataset(id="box-score-player-advanced", ...),
        BoxScoreDataset(id="box-score-player-quarter-splits", ...),
        BoxScoreDataset(id="box-score-line-score", ...),
        BoxScoreDataset(id="box-score-team-four-factors", ...),
        BoxScoreDataset(id="box-score-game-info", ...),
    )

    # Daily leaders -- no per-game catalog, the URL params ARE
    # the selector.
    DAILY_LEADERS_DATASETS: tuple[DailyDataset, ...] = (
        DailyDataset(id="player-box-scores", endpoint_name=..., ...),
        DailyDataset(id="team-box-scores",   endpoint_name=..., ...),
    )

    # Play-by-play -- a single endpoint, no catalog needed.
    PBP_DATASET = PBPDataset(endpoint_name=..., ...)

…and the three season-scoped datasets move to a new
``league_catalog.py`` module as part of the League Hub lane (the
exact module/file name is decided in the League Hub design doc).

Source layout once the Games Hub lane lands
============================================

| File | Purpose |
|------|---------|
| ``courtside_data/server/games_models.py`` | Pydantic response models. |
| ``courtside_data/server/games_catalog.py`` | Catalog constants + ``games_hub_catalog()``. |
| ``courtside_data/server/games_service.py`` | ``GamesHubService``. |
| ``courtside_data/server/app.py`` | New games routes appended to the existing app. |
| ``courtside_data/server/fixtures.py`` | New per-scope whitelists + fixture map builders. |

For now, this file is a documentation pointer plus the scope literal.
The module is import-safe -- no side effects, no runtime state.
"""

from __future__ import annotations

from typing import Literal

# Scope literal -----------------------------------------------------------
#
# Mirrors the three non-entity scopes the GAMES domain uses. The four
# other scopes (``player``, ``player_season``, ``team``, ``team_season``,
# ``season``, ``static``, ``search``) are either entity-scoped (and
# therefore belong to the corresponding entity Hub) or are
# re-classified as part of the League Hub move in section 9 of the
# games doc.
#
# The ``GAME`` scope is the per-game box-score scope (game_id param).
# The ``DATE`` scope is the daily-leaders scope (day/month/year).
# The ``DATE_TEAM`` scope is the play-by-play scope (day/month/year
# plus home_team). The ``SEASON`` scope is the season-scope that we
# recommend moving to the League Hub (see games-browser-hub.md
# section 9); it is included here only so the cross-references in
# this module can name it without lying about the eventual target.
GamesDatasetScope = Literal["game", "date", "date_team", "season"]


# 12 GAMES endpoint cross-references (documentation only) ----------------
#
# Listed in registry order from
# ``courtside_data/endpoints/_workflows.py:541-792``. These are
# comments (not constants) because the canonical home is the
# EndpointSpec registry; the catalog module mirrors that registry
# when it ships (see the "What to do when the lane lands" section
# above). The 3 endpoints that are already HTTP-reachable via the
# Player Hub (regular_season_player_box_scores,
# playoff_player_box_scores) and the player-search endpoint
# (``search``) are NOT listed here -- they are reachable through the
# Player Hub routes today
# (``/api/players/{player_identifier}/...``) and
# ``/api/players/search?term=...`` respectively.
#
# Per-game box scores (6, scope GAME, all use /boxscores/{game_id}.html):
#   - box_score_player_basic:        row model BoxScorePlayerBasicRow
#   - box_score_game_info:            row model BoxScoreGameInfoRow
#   - box_score_player_advanced:     row model BoxScorePlayerAdvancedRow
#   - box_score_line_score:           row model BoxScoreLineScoreRow
#   - box_score_player_quarter_splits: row model BoxScorePlayerQuarterSplitRow
#   - box_score_team_four_factors:    row model BoxScoreTeamFourFactorsRow
#
# Daily leaders (2, scope DATE):
#   - player_box_scores: row model PlayerBoxScoreRow
#   - team_box_scores:   row model TeamBoxScoreRow
#
# Play-by-play (1, scope DATE_TEAM):
#   - play_by_play: row model PlayByPlayRow
#
# Season-scoped (3, scope SEASON) -- RECOMMEND MOVE TO LEAGUE HUB:
#   - season_schedule:                row model SeasonScheduleRow
#   - players_season_totals:          row model PlayerSeasonTotalsRow
#   - players_advanced_season_totals: row model PlayerAdvancedSeasonTotalsRow
#
# Note on the period parameter (box_score_player_quarter_splits):
# The EndpointSpec accepts a free-form period string. The legal
# values are q1, q2, h1, q3, q4, h2 -- see the comments in
# ``courtside_data/schemas/boxscores.py:266-272``. It is a
# WITHIN-GAME sub-request, not a separate dataset; the route layer
# passes it as a query parameter on the same per-game box-score
# route. See games-browser-hub.md section 4 for the route shape.
#
# Note on the include_combined_values parameter (season totals):
# Boolean toggle that controls whether the workflow emits a single
# combined-totals row per player aggregating any mid-season trades.
# Has no Games Browser analogue; the parameter is the main reason
# the season totals feel like league-wide season tables (interaction
# model 4) rather than per-game content.
#
# Row-model cross-references:
#   - BoxScorePlayerBasicRow        -> courtside_data/schemas/boxscores.py:308
#   - BoxScoreGameInfoRow           -> courtside_data/schemas/boxscores.py:284
#   - BoxScorePlayerAdvancedRow     -> courtside_data/schemas/boxscores.py:211
#   - BoxScoreLineScoreRow          -> courtside_data/schemas/boxscores.py:247
#   - BoxScorePlayerQuarterSplitRow -> courtside_data/schemas/boxscores.py:266
#   - BoxScoreTeamFourFactorsRow    -> courtside_data/schemas/boxscores.py:229
#   - PlayerBoxScoreRow             -> courtside_data/schemas/boxscores.py:108
#   - TeamBoxScoreRow               -> courtside_data/schemas/boxscores.py:172
#   - PlayByPlayRow                 -> courtside_data/schemas/playbyplay.py:47
#   - SeasonScheduleRow             -> courtside_data/schemas/schedule.py:55
#   - PlayerSeasonTotalsRow         -> courtside_data/schemas/player_totals.py:19
#   - PlayerAdvancedSeasonTotalsRow -> courtside_data/schemas/player_totals.py:47

__all__ = ["GamesDatasetScope"]
