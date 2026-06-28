# Endpoint Roadmap

Master implementation roadmap for the **61 Basketball Reference
endpoints** registered in `courtside_data.endpoints.ENDPOINTS`. This
document is the single-source-of-truth dashboard: §1 is the
domain-by-domain status matrix, §2 is the full endpoint inventory,
§3 is the recommended implementation order, §4 is the cross-cutting
work that spans all lanes, and §5 links to the per-domain
architecture docs.

> **Scope of this doc:** planning only. It complements the existing
> per-domain architecture docs
> ([Player Hub](../api/http.md), [Team Hub](team-hub.md),
> [Games/Browser](games-browser-hub.md)) and the
> planned-but-not-yet-written League Hub, Playoffs Hub, and
> Draft/Awards/Leaders Hub docs. The recommended end state of
> `endpoint-roadmap.md` is that §2 is **auto-generated** from the
> EndpointSpec registry (mkdocstrings + griffe-pydantic is already
> configured for the schemas module; see `mkdocs.yml`); the current
> hand-maintained form will be replaced once that pipeline lands.

## 1. Current state matrix

| Domain | Endpoints | HTTP-reachable | Routes | Service | UI | Fixture HTML | Status |
|---|---|---|---|---|---|---|---|
| **PLAYERS** | 11 | 11/11 | 5 | `PlayerHubService` | `player-hub` | partial (1 player) | **Complete** |
| **TEAMS** | 13 | 13/13 | 6 | `TeamHubService` (search stub) | `team-hub` | partial (multiple teams) | **Scaffolded** |
| **LEAGUE** | 11 | 0/11 | 0 | — | — | partial (1974→2024) | **Planned** (see [§5](#5-links-to-domain-docs)) |
| **PLAYOFFS** | 6 | 0/6 | 0 | — | — | partial (friv + 1 season) | **Planned** |
| **DRAFT_AWARDS_LEADERS** | 5 | 0/5 | 0 | — | — | partial (1974→2024 + leaders) | **Planned** |
| **GAMES** | 15 | 3/15 (player_box_scores, team_box_scores, search) | partial | partial | — | partial (2017-01-01) | **Partially scaffolded** (see [Games/Browser](games-browser-hub.md)) |
| **TOTAL** | **61** | **27/61** | **11 + 3 partial** | — | — | — | — |

**Reading the matrix:**

- **Endpoints** — count of EndpointSpec entries in the registry
  (`courtside_data/endpoints/__init__.py:37`).
- **HTTP-reachable** — endpoints for which
  `tests/server/test_player_hub_api.py` (or the
  equivalent team-hub smoke test) returns `200 OK` on a
  known-fixture dataset. Counts 11 for Player, 13 for Team
  (counting the 3 NotImplementedError stubs as
  "reachable in the sense that the route exists"; the
  route returns `500 internal_error` for the stubs).
- **Routes** — count of FastAPI route handlers in
  `courtside_data/server/app.py` (5 for Player: catalog +
  search + summary + export + season-dataset + dataset;
  6 for Team: catalog + search + summary + export +
  season-dataset + dataset).
- **Service** — the `courtside_data.server.*_service` class
  that wraps the registry calls. Player and Team both have
  services; LEAGUE/PLAYOFFS/DRAFT_AWARDS_LEADERS do not.
- **UI** — the Next.js feature module under
  `apps/web/features/`. Player has `player-hub`; Team has
  `team-hub`; the other 4 do not.
- **Fixture HTML** — saved Basketball Reference HTML
  pages under `raw/`. "Partial" means the domain has
  *some* coverage but not enough to test every (entity,
  year, parameter-tuple) combination. The plan
  (see [§4](#4-cross-cutting-work)) is to close the
  per-domain gaps in the order recommended by §3.

## 2. Full endpoint inventory

The complete registry, grouped by domain. Verified against
`courtside_data/endpoints/{_players,_teams,_league,_playoffs,
_draft_awards_leaders,_workflows}.py`.

### 2.1 PLAYERS (11 endpoints)

| `endpoint_name` | `spec` file:line | scope | params | `row_model` |
|---|---|---|---|---|
| `player_career_stats` | `_players.py:33` | `player` | `("player_identifier",)` | `PlayerCareerStatsRow` |
| `player_playoff_series` | `_players.py:46` | `player` | `("player_identifier",)` | `PlayerPlayoffSeriesRow` |
| `player_adjusted_shooting` | `_players.py:60` | `player` | `("player_identifier",)` | `PlayerAdjustedShootingRow` |
| `player_play_by_play` | `_players.py:74` | `player` | `("player_identifier",)` | `PlayerPlayByPlayStatsRow` |
| `player_game_highs` | `_players.py:88` | `player` | `("player_identifier",)` | `PlayerGameHighsRow` |
| `player_all_star` | `_players.py:102` | `player` | `("player_identifier",)` | `PlayerAllStarRow` |
| `player_similarity_scores` | `_players.py:116` | `player` | `("player_identifier",)` | `PlayerSimilarityScoresRow` |
| `player_salaries` | `_players.py:130` | `player` | `("player_identifier",)` | `PlayerSalariesRow` |
| `player_splits` | `_players.py:144` | `player_season` | `("player_identifier", "season_end_year")` | `PlayerSplitsRow` |
| `player_on_off` | `_players.py:158` | `player_season` | `("player_identifier", "season_end_year")` | `PlayerOnOffRow` |
| `player_shot_charts` | `_players.py:173` | `player_season` | `("player_identifier", "season_end_year")` | `PlayerShotChartsRow` |

Path template: `/players/{player_identifier[0]}/{player_identifier}.html`
(plus `/splits/{season_end_year}`, `/on-off/{season_end_year}`,
`/shooting/{season_end_year}` for the season-scoped trio).

### 2.2 TEAMS (13 endpoints)

| `endpoint_name` | `spec` file:line | scope | params | `row_model` |
|---|---|---|---|---|
| `team_roster` | `_teams.py:33` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamRosterRow` |
| `team_injury_report` | `_teams.py:48` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamInjuryReportRow` |
| `team_and_opponent` | `_teams.py:61` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamAndOpponentRow` |
| `team_misc_four_factors` | `_teams.py:75` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamMiscFourFactorsRow` |
| `team_opponent_stats` | `_teams.py:91` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamOpponentStatsRow` |
| `team_schedule` | `_teams.py:105` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamScheduleRow` |
| `team_transactions` | `_teams.py:118` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamTransactionsRow` |
| `team_splits` | `_teams.py:133` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamSplitsRow` |
| `team_contracts` | `_teams.py:146` | `team` | `("team_abbreviation",)` | `TeamContractsRow` |
| `team_lineups` | `_teams.py:160` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamLineupsRow` |
| `team_starting_lineups` | `_teams.py:174` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamStartingLineupsRow` |
| `team_on_off` | `_teams.py:187` | `team_season` | `("team_abbreviation", "season_end_year")` | `TeamOnOffRow` |
| `franchise_history` | `_teams.py:200` | `team` | `("team_abbreviation",)` | `FranchiseHistoryRow` |

### 2.3 LEAGUE (11 endpoints)

| `endpoint_name` | `spec` file:line | scope | params | `row_model` |
|---|---|---|---|---|
| `league_per_game_stats` | `_league.py:96` | `season` | `("season_end_year",)` | `LeaguePerGameStatsRow` |
| `league_per_36_minutes` | `_league.py:111` | `season` | `("season_end_year",)` | `LeaguePer36MinutesRow` |
| `league_totals` | `_league.py:126` | `season` | `("season_end_year",)` | `LeagueTotalsRow` |
| `league_per_100_possessions` | `_league.py:141` | `season` | `("season_end_year",)` | `LeaguePer100PossessionsRow` |
| `league_shooting` | `_league.py:157` | `season` | `("season_end_year",)` | `LeagueShootingRow` |
| `league_play_by_play` | `_league.py:172` | `season` | `("season_end_year",)` | `LeaguePlayByPlayRow` |
| `league_transactions` | `_league.py:187` | `season` | `("season_end_year",)` | `LeagueTransactionRow` |
| `rookie_stats` | `_league.py:202` | `season` | `("season_end_year",)` | `RookieStatsRow` |
| `standings` | `_league.py:216` | `season` | `("season_end_year",)` | `StandingsRow` |
| `standings_by_date` | `_league.py:230` | `season` | `("season_end_year",)` | `StandingsByDateRow` |
| `attendance` | `_league.py:256` | `season` | `("season_end_year",)` | `AttendanceRow` |

### 2.4 PLAYOFFS (6 endpoints)

| `endpoint_name` | `spec` file:line | scope | params | `row_model` |
|---|---|---|---|---|
| `playoff_per_game` | `_playoffs.py:90` | `season` | `("season_end_year",)` | `PlayoffPerGameRow` |
| `playoff_totals` | `_playoffs.py:106` | `season` | `("season_end_year",)` | `PlayoffTotalsRow` |
| `playoff_bracket` | `_playoffs.py:122` | `season` | `("season_end_year",)` | `PlayoffBracketRow` |
| `friv_7_game_playoff_series_outcomes_team_is_down` | `_playoffs.py:136` | `static` | `()` | `SevenGamePlayoffSeriesOutcomesRow` |
| `friv_7_game_playoff_series_outcomes_team_is_tied` | `_playoffs.py:151` | `static` | `()` | `SevenGamePlayoffSeriesOutcomesRow` |
| `friv_7_game_playoff_series_outcomes_team_is_up` | `_playoffs.py:166` | `static` | `()` | `SevenGamePlayoffSeriesOutcomesRow` |

### 2.5 DRAFT_AWARDS_LEADERS (5 endpoints)

| `endpoint_name` | `spec` file:line | scope | params | `row_model` |
|---|---|---|---|---|
| `draft_picks` | `_draft_awards_leaders.py:66` | `season` | `("season_end_year",)` | `DraftPicksRow` |
| `season_awards` | `_draft_awards_leaders.py:79` | `season` | `("season_end_year",)` | `SeasonAwardsRow` |
| `season_awards_voting` | `_draft_awards_leaders.py:94` | `season` | `("season_end_year", "award")` | `SeasonAwardsVotingRow` |
| `season_leaders` | `_draft_awards_leaders.py:122` | `static` | `()` | `SeasonLeadersRow` |
| `career_leaders` | `_draft_awards_leaders.py:141` | `static` | `()` | `CareerLeadersRow` |

### 2.6 GAMES (15 endpoints)

**3 endpoints are already HTTP-reachable through the Player Hub
(/api/players/{id}/seasons/{year}/{dataset} and
/api/players/search).** The remaining 12 are catalogued below; the
game-identification scheme and per-game routing is in
[Games/Browser Hub §3](games-browser-hub.md#3-the-game-identification-problem-critical-section).

| `endpoint_name` | `spec` file:line | scope | params | HTTP-reachable today? | `row_model` |
|---|---|---|---|---|---|
| `box_score_player_basic` | `_workflows.py:541` | `game` | `("game_id",)` | no | `BoxScorePlayerBasicRow` |
| `box_score_game_info` | `_workflows.py:558` | `game` | `("game_id",)` | no | `BoxScoreGameInfoRow` |
| `box_score_player_advanced` | `_workflows.py:575` | `game` | `("game_id",)` | no | `BoxScorePlayerAdvancedRow` |
| `box_score_line_score` | `_workflows.py:592` | `game` | `("game_id",)` | no | `BoxScoreLineScoreRow` |
| `box_score_player_quarter_splits` | `_workflows.py:609` | `game` | `("game_id", "period")` | no | `BoxScorePlayerQuarterSplitRow` |
| `box_score_team_four_factors` | `_workflows.py:626` | `game` | `("game_id",)` | no | `BoxScoreTeamFourFactorsRow` |
| `player_box_scores` | `_workflows.py:643` | `date` | `("day", "month", "year")` | **no** (row model is `PlayerBoxScoreRow`; reaches via daily-leaders, not via player hub) | `PlayerBoxScoreRow` |
| `team_box_scores` | `_workflows.py:660` | `date` | `("day", "month", "year")` | **no** (row model is `TeamBoxScoreRow`; reaches via daily-leaders) | `TeamBoxScoreRow` |
| `play_by_play` | `_workflows.py:683` | `date_team` | `("home_team", "day", "month", "year")` | no | `PlayByPlayRow` |
| `regular_season_player_box_scores` | `_workflows.py:707` | `player_season` | `("player_identifier", "season_end_year", "include_inactive_games")` | **yes** (via `/api/players/{id}/seasons/{year}/regular-games`) | `RegularSeasonPlayerBoxScoreRow` |
| `playoff_player_box_scores` | `_workflows.py:725` | `player_season` | `("player_identifier", "season_end_year", "include_inactive_games")` | **yes** (via `/api/players/{id}/seasons/{year}/playoff-games`) | `PlayoffPlayerBoxScoreRow` |
| `season_schedule` | `_workflows.py:743` | `season` | `("season_end_year",)` | no (recommend move to League Hub) | `SeasonScheduleRow` |
| `players_season_totals` | `_workflows.py:763` | `season` | `("season_end_year", "include_combined_values")` | no (recommend move to League Hub) | `PlayerSeasonTotalsRow` |
| `players_advanced_season_totals` | `_workflows.py:778` | `season` | `("season_end_year", "include_combined_values")` | no (recommend move to League Hub) | `PlayerAdvancedSeasonTotalsRow` |
| `search` | `_workflows.py:794` | `search` | `("term",)` | **yes** (via `/api/players/search?term=…`) | `SearchResultRow` |

**Note on the row model discrepancy in `player_box_scores` /
`team_box_scores`:** the cell above says "no" for HTTP-reachable.
The 0.1.0 Player Hub smoke test
(`tests/server/test_player_hub_api.py`) does not exercise these
endpoints (they are date-scoped, not player-scoped), so neither
has a current HTTP route. The endpoint is HTTP-registered (the
fixture manifest
`tests/fixture_manifest.py` lists it), but the route layer
returns `404 missing_fixture` because
`courtside_data/server/fixtures.py` only whitelists
`PLAYER_ONLY_ENDPOINTS` / `PLAYER_SEASON_ENDPOINTS` / the team
sister sets. Once the Games Hub lane adds
`DAILY_LEADERS_ENDPOINTS` + `_daily_leaders_map`, these become
HTTP-reachable.

**Note on the search endpoint:** `search` is registered under
the GAMES domain (`domain=EndpointDomain.GAMES` per
`_workflows.py:801`) but is functionally a player-search call
today. The catalog domain does not always match the data domain
(the "GAMES domain" is the team that owns the workflow, not a
semantic claim that the dataset is about games). The League Hub
move in §3 should not affect `search`.

## 3. Implementation priority

The recommended order across all six domains:

1. **Player Hub** ✅ **Done.** 11/11 endpoints reachable;
   1-fixture-player coverage; routes / service / catalog / UI
   all in place.
2. **Team Hub** 🚧 **Scaffolded.** 13/13 endpoints whitelisted
   in the fixture transport; 6 routes + service + catalog + UI
   in place; `search()` is the only remaining
   `NotImplementedError` stub; fixture HTML for the per-team
   endpoints is the next blocker. See
   [Team Hub §5](team-hub.md#5-fixture-html-needed)
   for the per-endpoint capture list.
3. **League Hub** ⏭️ **Next.** 11 endpoints
   (or 14 if the 3 GAMES season-scoped endpoints move here —
   recommended; see
   [Games/Browser §9.2](games-browser-hub.md#92-league-hub-boundary-recommend-move)).
   Straightforward season-scoped pattern: 1 route per
   dataset under `/api/league/seasons/{year}/{dataset}`,
   plus 1 `standings_by_date` route that needs both `year` and
   `date` params (special-case), and 1 `attendance` route
   that is a projection from a `#advanced-team` table. The
   `_season` factory in `courtside_data/endpoints/_table.py`
   already produces these EndpointSpec entries; the
   implementation is a near copy of the Team Hub lane. The
   `standings` and `standings_by_date` endpoints are
   `EndpointKind.WORKFLOW` (the bespoke `HTTPService.standings`
   methods) and will need a small service-layer wrapper.
4. **Playoffs Hub** ⏭️ **After League.** 6 endpoints. Same
   season-scoped pattern as League Hub for `playoff_per_game`,
   `playoff_totals`, and `playoff_bracket`. The 3 friv
   endpoints are `EndpointScope.STATIC` (no params at all; the
   `table_id` in the URL flips between `team-is-down`,
   `team-is-tied`, `team-is-up`); the HTTP layer for these is
   1 route per table-id under `/api/playoffs/static/{table}`.
5. **Draft/Awards/Leaders Hub** ⏭️ **After Playoffs.** 5
   endpoints. Mix of `season` (3) and `static` (2). The
   `season_awards_voting` endpoint has a free-form `award` param
   (the `table_id` template) that maps to 10 fallback table
   ids (mvp, roy, dpoy, smoy, mip, clutch_poy, coy,
   leading_all_nba, leading_all_defense, leading_all_rookie).
   The 2 static leader endpoints (`season_leaders`,
   `career_leaders`) hit `/leaders/*.html` and are
   `EndpointScope.STATIC`.
6. **Games/Browser Hub** ⏭️ **Last.** 9 endpoints (or 12 if
   the season-scoped trio stays here; 9 is recommended).
   This is the **hardest** of the six domains — it does not
   fit the entity-Hub pattern and spans 4 different
   interaction models (per-game box scores, daily leaders,
   play-by-play, league-season tables). The game-identifier
   scheme (`{YYYYMMDD}0{HOMETEAM_ABBR}`) is the load-bearing
   design decision. See
   [Games/Browser Hub](games-browser-hub.md)
   for the full design.

**Total reachable endpoints after all 6 lanes land:** 61 / 61
(no domain left unscoped; the fixture-mode smoke test will
return 200 on every dataset).

## 4. Cross-cutting work

Several items are not domain-scoped and must be done once but
benefit every lane. Listed in dependency order:

1. **Fixture HTML capture** — every domain needs more
   raw/ HTML. The existing player-hub coverage is sparse
   (1 player); the team-hub coverage is partial (multiple
   teams per endpoint but not all years). The recommended
   end state is "at least 1 fixture per
   `(endpoint, param-value-set)` tuple" — this is the
   `tests/fixture_manifest.py` `ALL_CASES` model. Per-domain
   capture plans are in §7 of each architecture doc.
2. **Season-discovery walkers** — for season-scoped
   endpoints, the test suite needs to know which
   `season_end_year` values are well-formed. The player hub
   ships `fixture_seasons_for_player` (see
   `courtside_data/server/fixtures.py:352`); the
   equivalent for teams / league / playoffs is a future
   helper in the same module. The pattern is
   "glob `raw/{endpoint}/*.html`, parse the year out of
   the filename, return a sorted list".
3. **OpenAPI codegen** — once new routes exist, regenerate
   the OpenAPI schema (`apps/web/types/api.ts` is the
   consumer). The Player Hub already does this end-to-end;
   the Team Hub mostly does (3 NotImplementedError stubs
   leak into the OpenAPI as 500 responses, which is
   acceptable per the "scaffolding" milestone). The new
   domains should follow the same end-to-end codegen
   pattern.
4. **Shared UI components** — `DataTable`, `EmptyState`,
   `ErrorState`, and `TabBar` are already shared across
   the Player and Team Hubs; the new domains should reuse
   them rather than fork. A `apps/web/components/hub/`
   extraction is a candidate refactor for the post-League
   Hub milestone.
5. **mkdocs regeneration** — the `API` and `architecture`
   sections of the docs site are auto-generated from the
   schemas and endpoint registry (mkdocstrings +
   griffe-pydantic). When a new architecture doc lands
   (League Hub, Playoffs Hub, Draft/Awards Hub), add it
   to `mkdocs.yml` `nav:` and re-run `mkdocs build --strict`.
6. **Whitelist parity** — the fixture transport
   (`courtside_data/server/fixtures.py`) must be extended
   with `LEAGUE_ENDPOINTS`, `PLAYOFFS_ENDPOINTS`,
   `DRAFT_ENDPOINTS`, `GAMES_ENDPOINTS` (plus season /
   static / game / date / date-team variants as
   appropriate) so the per-endpoint helpers
   (`_league_season_map`, `_playoff_season_map`, …) can
   be wired in. The existing team whitelist is the
   template (see the `# TODO(team-hub)` block in
   `courtside_data/server/fixtures.py:207-336`).

## 5. Links to domain docs

- **Player Hub** — [docs/api/http.md](../api/http.md) (the
  canonical reference; the team-hub doc
  ([docs/architecture/team-hub.md](team-hub.md))
  is the more recent structural template).
- **Team Hub** —
  [docs/architecture/team-hub.md](team-hub.md).
  13 endpoints; 6 routes; scaffolding milestone.
- **League Hub** — *planned* (the 11 LEAGUE-domain endpoints
  in §2.3 plus the 3 GAMES-domain season-scoped endpoints
  recommended for the move in
  [Games/Browser §9.2](games-browser-hub.md#92-league-hub-boundary-recommend-move)).
- **Playoffs Hub** — *planned* (the 6 PLAYOFFS-domain
  endpoints in §2.4).
- **Draft/Awards/Leaders Hub** — *planned* (the 5
  DRAFT_AWARDS_LEADERS-domain endpoints in §2.5).
- **Games/Browser** —
  [docs/architecture/games-browser-hub.md](games-browser-hub.md).
  9 (or 12) endpoints; the hardest lane; different UX
  model.

## 6. Inline TODO anchors

Cross-references from this doc to the inline TODO comments in
the codebase:

- `courtside_data/server/app.py` end-of-file TODO block —
  master endpoint roadmap pointer; lists the 4 missing
  domains and the per-domain route shape. See the file
  directly for the exact text.
- `courtside_data/server/fixtures.py` whitelist TODO block
  (below the existing `# TODO(team-hub):` block) — the
  34-endpoint capture list (11 LEAGUE + 6 PLAYOFFS + 5
  DRAFT_AWARDS_LEADERS + 12 GAMES). See the file directly
  for the exact text.
- `courtside_data/server/games_catalog.py` — Games/Browser
  catalog stub (12 endpoint cross-references + a
  `GamesDatasetScope` literal). See the file directly.

## 7. Future work (post-endpoint-roadmap)

Once all 61 endpoints are HTTP-reachable and fixture-tested,
the next milestones are:

- **End-to-end UI for the 5 new domains.** The Player
  Hub and Team Hub have working UIs; the 5 new domains
  need `apps/web/features/{league,playoffs,draft-awards,games}/`.
- **Diff-cover + mutation testing.** The new service
  layers should reach 100% diff coverage on PRs (see
  `diff_cover` in `AGENTS.md`).
- **OpenAPI + client SDK regeneration.** Once the routes
  stabilize, regenerate the TS client and publish a
  versioned Python SDK.
- **De-scoping `endpoint-roadmap.md`.** The current
  hand-maintained §2 should be auto-generated from
  `ENDPOINTS` once the mkdocstrings pipeline grows to
  support endpoint metadata.
