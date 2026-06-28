# League Hub

Implementation roadmap for the League Hub, the third entity-Hub domain
in the Player Hub / Team Hub / League Hub family. The hub exposes 11
league-wide Basketball-Reference tables behind a season-scoped FastAPI
surface and reuses the same `CourtsideClient` + `CourtsideData`
plumbing as the player and team hubs. The implementation is currently
**unscaffolded** - this document is the planning blueprint for the next
implementer.

The proven pattern lives in `docs/architecture/team-hub.md` and the
backend scaffolding it points at
(`courtside_data/server/team_catalog.py`,
`courtside_data/server/team_service.py`,
`courtside_data/server/team_models.py`,
`courtside_data/server/app.py`). The League Hub is a
"copy and adapt" exercise from that pattern, with the entity swap
(player -> league) and a smaller scope set (only one season-scoped
shape, no entity-identifier routing).

## 1. Overview

The League Hub surfaces **league-wide tables for a selected NBA
season** - per-game / per-36 / per-100-possessions / totals / shooting
/ play-by-play averages, league transactions, rookie stats, final
standings, standings on a specific date, and per-team attendance. It
is centered on the **(season, league)** tuple rather than on a player
or team entity, so the primary interaction is a **season picker**
(not an entity search).

How it relates to the existing hubs:

- **Player Hub** (`courtside_data.server.service.PlayerHubService`):
  entity is the player, primary interaction is the search box
  (`/api/players/search`) plus a player-identifier URL
  (`/api/players/{player_identifier}/{dataset}`).
- **Team Hub** (`courtside_data.server.team_service.TeamHubService`):
  entity is the team, primary interaction is the team-identifier URL
  (`/api/teams/{team_identifier}/...`) - 13 datasets across two
  scopes (`team` / `team_season`).
- **League Hub** (this roadmap): entity is the season, primary
  interaction is a **season picker** + (for `standings_by_date`) a
  **date picker**. No identifier URL; routes are
  `/api/league/{dataset}?season_end_year=2024` and (for the date
  dataset) `/api/league/standings-by-date?month=...&day=...&year=...`.

The League Hub shares infrastructure (HTTP plumbing, Pydantic
response models, FastAPI dependency injection, the `EndpointRowsResponse`
envelope) with the other two hubs. The new work is the catalog, the
service class, the route registrations, and a small UI feature module.

## 2. Endpoint inventory

The 11 League Hub datasets are mapped 1:1 onto the
`courtside_data.endpoints._league.LEAGUE_ENDPOINTS` registry entries
(271 lines; see `_league.py:96-256`). The table below verifies the
params / scope / row model for each entry.

| Dataset id        | endpoint_name               | params                          | EndpointSpec scope | row model                  | EndpointKind       | ParserShape           | spec    |
|-------------------|-----------------------------|---------------------------------|--------------------|----------------------------|--------------------|-----------------------|---------|
| `per-game`        | `league_per_game_stats`     | `season_end_year`               | SEASON             | `LeaguePerGameStatsRow`    | GENERIC_TABLE      | TABLE                 | `_league.py:96`   |
| `per-36-minutes`  | `league_per_36_minutes`     | `season_end_year` (min=1947)    | SEASON             | `LeaguePer36MinutesRow`    | GENERIC_TABLE      | TABLE                 | `_league.py:111`  |
| `totals`          | `league_totals`             | `season_end_year`               | SEASON             | `LeagueTotalsRow`          | GENERIC_TABLE      | TABLE                 | `_league.py:126`  |
| `per-100-possessions` | `league_per_100_possessions` | `season_end_year` (min=1974) | SEASON             | `LeaguePer100PossessionsRow` | GENERIC_TABLE    | TABLE                 | `_league.py:141`  |
| `shooting`        | `league_shooting`           | `season_end_year`               | SEASON             | `LeagueShootingRow`        | GENERIC_TABLE      | TABLE                 | `_league.py:157`  |
| `play-by-play`    | `league_play_by_play`       | `season_end_year`               | SEASON             | `LeaguePlayByPlayRow`      | GENERIC_TABLE      | TABLE                 | `_league.py:172`  |
| `transactions`    | `league_transactions`       | `season_end_year`               | SEASON             | `LeagueTransactionRow`     | GENERIC_TABLE      | TRANSACTION_LIST      | `_league.py:187`  |
| `rookies`         | `rookie_stats`              | `season_end_year`               | SEASON             | `RookieStatsRow`           | GENERIC_TABLE      | TABLE                 | `_league.py:202`  |
| `standings`       | `standings`                 | `season_end_year`               | SEASON             | `StandingsRow`             | WORKFLOW           | STANDINGS_BLOCKS      | `_league.py:216`  |
| `standings-by-date` | `standings_by_date`       | `season_end_year` (route: month/day/year) | SEASON  | `StandingsByDateRow`       | WORKFLOW           | MULTI_TABLE           | `_league.py:230`  |
| `attendance`      | `attendance`                | `season_end_year`               | SEASON             | `AttendanceRow`            | GENERIC_TABLE      | TABLE (projection)    | `_league.py:256`  |

Row model file:line references (for the implementer):

- `LeaguePerGameStatsRow` - `courtside_data/schemas/league.py:68`
- `LeaguePer36MinutesRow` - `courtside_data/schemas/league.py:161`
- `LeagueTotalsRow` - `courtside_data/schemas/league.py:86`
- `LeaguePer100PossessionsRow` - `courtside_data/schemas/league.py:205`
- `LeagueShootingRow` - `courtside_data/schemas/league.py:252`
- `LeaguePlayByPlayRow` - `courtside_data/schemas/league.py:313`
- `LeagueTransactionRow` - `courtside_data/schemas/league.py:350`
- `RookieStatsRow` - `courtside_data/schemas/league.py:113`
- `StandingsRow` - `courtside_data/schemas/standings.py:28`
- `StandingsByDateRow` - `courtside_data/schemas/standings.py:53`
- `AttendanceRow` - `courtside_data/schemas/league.py:371`

URL templates (per the EndpointSpec `path` field, with the season
token replaced by `{YEAR}` and the team/conference tokens either
removed or marked `{TEAM}`):

| dataset id          | URL template                                              |
|---------------------|-----------------------------------------------------------|
| `per-game`          | `/leagues/NBA_{YEAR}_per_game.html`                       |
| `per-36-minutes`    | `/leagues/NBA_{YEAR}_per_minute.html`                     |
| `totals`            | `/leagues/NBA_{YEAR}_totals.html`                         |
| `per-100-possessions` | `/leagues/NBA_{YEAR}_per_poss.html`                     |
| `shooting`          | `/leagues/NBA_{YEAR}_shooting.html`                       |
| `play-by-play`      | `/leagues/NBA_{YEAR}_play-by-play.html`                   |
| `transactions`      | `/leagues/NBA_{YEAR}_transactions.html`                   |
| `rookies`           | `/leagues/NBA_{YEAR}_rookies.html`                        |
| `standings`         | `/leagues/NBA_{YEAR}.html` (workflow parses both conf tables) |
| `standings-by-date` | `/leagues/NBA_{YEAR}_standings_by_date_{conference}.html` (internal token) |
| `attendance`        | `/leagues/NBA_{YEAR}.html` (table#advanced-team)          |

Note: `standings` and `attendance` hit the **same page**
(`/leagues/NBA_{YEAR}.html`) but parse different `<table>` elements
and expose different row models. The fixture file path under `raw/`
must disambiguate them (see [§7 Fixture capture plan](#7-fixture-capture-plan)).

## 3. HTTP route design

Mirror the Team Hub's 6-route pattern but collapse `dataset` /
`season_dataset` into a single season-keyed route (because there is
no entity identifier in the URL - only a season). The proposed
routes:

| Method | Path                                                              | Response                                |
|--------|-------------------------------------------------------------------|-----------------------------------------|
| `GET`  | `/api/endpoints/league-hub`                                       | `dict[str, object]` (catalog)            |
| `GET`  | `/api/league/{dataset}?season_end_year={YEAR}`                    | `EndpointRowsResponse`                  |
| `GET`  | `/api/league/standings-by-date?season_end_year={YEAR}&month={M}&day={D}&year={Y}` | `EndpointRowsResponse`         |
| `GET`  | `/api/league/{dataset}/export?season_end_year={YEAR}`             | CSV `Response`                          |

### Why no `/api/league/search`

There is no entity to search for. The Player Hub's `search` endpoint
exists because basketball-reference's `/search/search.fcgi` is
player-only (see the `NotImplementedError` TODO in
`courtside_data/server/team_service.py` for the team-hub
analog). The League Hub has no analogous endpoint - it is
season-scoped, not entity-scoped. Skip the search route.

### Why no `/api/league/{league_identifier}/summary`

There is no "league" entity with a stable identifier at the URL
level. The summary, if needed, is just the current season's
overview - and that's the catalog page itself (`/api/endpoints/
league-hub` plus the user-selected season picker). Skip the
summary route.

### Why no `{team_identifier}` path segment

The team endpoint of every league row is a *column* on the row
(`team_name_abbr`), not an identifier in the URL. Users who want
to drill into a single team use the Team Hub
(`/api/teams/{team_identifier}/{dataset}`). Skip team scoping on
the League Hub routes.

### Why a single season-keyed route instead of `dataset` + `season_dataset`

The Team Hub has two routes because some team datasets are
entity-scoped (no season) and some are season-scoped. The League
Hub is uniform: every dataset needs a `season_end_year`, with the
single exception of `standings_by_date` which additionally needs a
date. So:

- `/api/league/{dataset}?season_end_year={YEAR}` is the canonical
  route for all 10 season-scoped datasets.
- `/api/league/standings-by-date?season_end_year={YEAR}&month=...`
  is the route for the one date-scoped dataset. (The
  `season_end_year` is still required because the EndpointSpec
  declares it; the workflow's `expand_conferences` step derives the
  per-conference URLs from `season_end_year`.)

The route layer must validate that the dataset id is in
`LEAGUE_DATASETS` and reject unknown ids with 404. The
season/date parsing is a FastAPI `Query(...)` parameter with a
Pydantic validation layer; mirror
`_params_for_dataset` in `courtside_data/server/app.py:336-353`
for the player-hub pattern.

## 4. Catalog design

The catalog mirrors `courtside_data/server/team_catalog.py` (the
proven pattern). The new files are:

- `courtside_data/server/league_catalog.py` - the catalog stub
  (already created; see the `TODO(league-hub)` block at the top).
- `courtside_data/server/league_models.py` - the Pydantic response
  models (`LeagueDatasetCatalogEntry`, `LeagueHubTab`, `LeagueHubCatalog`,
  `LeagueHubSummary` if needed; the entity-agnostic
  `EndpointRowsResponse` is reused from `courtside_data/server/models.py`).

The proposed `LEAGUE_DATASETS` tuple (11 entries) is documented
in `courtside_data/server/league_catalog.py` as a comment block
(see the file's "Proposed LEAGUE_DATASETS structure" section). The
proposed `LEAGUE_TABS` grouping:

| Tab id         | Scope            | Datasets                                                                                  | Default dataset |
|----------------|------------------|-------------------------------------------------------------------------------------------|-----------------|
| `stats`        | `league_season`  | `per-game`, `per-36-minutes`, `totals`, `per-100-possessions`, `shooting`, `play-by-play` | `per-game`      |
| `transactions` | `league_season`  | `transactions`, `rookies`                                                                  | `transactions`  |
| `standings`    | `league_season`  | `standings`, `standings-by-date`                                                           | `standings`     |
| `attendance`   | `league_season`  | `attendance`                                                                              | `attendance`    |

Notes on the tab grouping:

- The `standings-by-date` dataset is grouped under the `standings`
  tab even though its scope is `league_date` - the tab's primary
  scope (`league_season`) drives the season picker; the date
  picker is an additional control on the same tab.
- The `transactions` tab groups the league-wide transactions
  table with the rookies table because both are "league-wide
  people movements" - a thin narrative connection. If product
  wants them on separate tabs, split.
- There is no `overview` tab. An "overview" tab needs hero stats
  from a source endpoint, and there is no obvious League Hub
  equivalent (no team misc-four-factors row, no player career
  row). Skip the tab; the catalog is season-picker-first.

`default_visible_columns` per dataset: leave the tuples empty in
the first pass (mirror the team-hub scaffolding). The
team-hub TODO in `courtside_data/server/team_catalog.py:35` (the
expanded TODO from this lane) describes the per-dataset
curation pattern - reuse it for each League Hub entry.

## 5. Service design

The new service class is `LeagueHubService` in
`courtside_data/server/league_service.py`. It mirrors
`TeamHubService` with two simplifications:

1. No entity identifier (`team_identifier` -> nothing). The
   service's public surface is just `(dataset_id, season_end_year)`
   for the season route and `(dataset_id, season_end_year, month,
   day, year)` for the date route.
2. No `_team_hero_stats` (no entity-specific hero stats to
   assemble). The `summary()` method, if added, would be a thin
   wrapper over the catalog response; the roadmap recommends
   skipping it entirely.

### Public API surface

```text
class LeagueHubService:
    def dataset(
        self,
        dataset_id: str,
        season_end_year: int,
    ) -> EndpointRowsResponse: ...

    def csv(
        self,
        dataset_id: str,
        season_end_year: int,
    ) -> str: ...
```

Both methods are straightforward wrappers over
`self._run(dataset.endpoint_name, params)` + the column / CSV
serialization helpers. The Team Hub's
`season_dataset` / `csv` private helpers
(`courtside_data/server/team_service.py:383,519`) are the
reference implementations - just delete the team-identifier
parameter.

### Season default resolution

`season_end_year` is required at the route layer (not optional).
The service should reject calls that omit it (mirror
`TeamHubService._build_params` at `team_service.py:204-220`).
This is simpler than the team-hub default-season resolver because
every League Hub endpoint genuinely requires a season - there is
no entity-scoped fallback.

### Workflow endpoints

`standings` (workflow, `_STANDINGS_WORKFLOW`) and
`standings_by_date` (workflow, `_STANDINGS_BY_DATE_WORKFLOW`) need
no special handling in the service. Both run through the
standard workflow executor (`courtside_data.client.CourtsideClient`
delegates the work to the workflow runner), and the service just
serializes the resulting rows. The Player Hub's
`PlayerHubService.rows_for_dataset` (which is what workflow
endpoints also go through) is the reference pattern.

The only workflow-specific concern is `standings_by_date`'s
internal `conference` template parameter. The EndpointSpec
declares only `("season_end_year",)` (no `conference`); the
workflow's `expand_conferences` step derives the two conference
URLs from `season_end_year`. The service just needs to pass
`season_end_year` (and the route layer accepts the
`month/day/year` query params that the workflow's parser
ultimately uses to filter the rows). Verify the workflow's
parameter surface by reading
`courtside_data/endpoints/_workflows.py` and
`courtside_data/parsing/workflows/_steps/_expand.py`.

### `attendance` projection

The `attendance` EndpointSpec declares a 4-tuple
`projection=("team", "arena_name", "attendance", "attendance_per_g")`.
The generic-table fetcher narrows the row payload to those 4
columns; the service does not need to do anything special. The
`AttendanceRow` schema
(`courtside_data/schemas/league.py:371`) is the row model
the Pydantic validator uses.

## 6. UI feature design

The new UI feature module lives at
`ui/src/features/league-hub/` and mirrors
`ui/src/features/team-hub/` (the proven pattern). The
components:

| Component file                | Role                                                              |
|-------------------------------|-------------------------------------------------------------------|
| `league-hub.tsx`              | Top-level shell: season picker, tab strip, active-tab renderer.  |
| `season-picker.tsx`           | Season dropdown (1947 -> present; bounded by per-endpoint min_year). |
| `date-picker.tsx`             | Month/day/year inputs (for `standings-by-date`).                  |
| `data-table.tsx`              | Reuse from `ui/src/features/team-hub/components/dataset-panel.tsx` (or extract to a shared module). |
| `dataset-panel.tsx`           | Reuse (or extract).                                               |
| `overview.tsx`                | Optional - if the team-hub "hero stats" pattern is wanted, surface league-level "average team age" / "total games" / "average attendance" stats derived from the active dataset. |

Primary interaction model: **season picker first**, then
tab/dataset selection. The user picks a season (e.g. 2024), the
UI fetches the default dataset for each tab, and the user can
switch tabs to see other league-wide tables. The `standings` tab
additionally exposes the date picker, which switches the
`standings-by-date` dataset to a specific calendar date within
the selected season.

What differs from the team-hub pattern:

- No search box (no entity to search for).
- No team-identifier URL; the route shape is
  `/league/{season}/{dataset}` or `/league?season=...&dataset=...`.
- The season picker is the central control, not a sidebar /
  subnav element. The team-hub UI has the team identifier baked
  into the URL; the league-hub UI carries it in component state
  and query params.

Cross-reference: `ui/src/features/team-hub/team-hub.tsx` and
`ui/src/features/team-hub/components/overview.tsx` for the
structural template; the player-hub UI
(`ui/src/features/player-hub/`) for the season-picker pattern
(both player-hub season-scoped datasets and league-hub datasets
share the "season drives everything" interaction model).

## 7. Fixture capture plan

To enable fixture mode, capture one HTML per (endpoint, season)
pair under `raw/`. The naming convention mirrors the player-hub
walker at `courtside_data/server/fixtures.py:142,150` and the
team-hub walker that's documented in the TODO at
`courtside_data/server/fixtures.py:207`:

- For each season-scoped endpoint, the fixture file is
  `raw/{endpoint_name}/{season_end_year}.html` (no per-team
  segment; league endpoints are team-agnostic).
- For workflow endpoints, the fixture file is the same
  (the workflow's first step is a `FETCH` that hits the same
  URL the generic table would hit).
- For `standings-by-date` (`MULTI_TABLE` workflow, fans out to
  two conferences), the fixture is
  `raw/standings_by_date/{season_end_year}_eastern.html` and
  `{season_end_year}_western.html` - or one combined
  `{season_end_year}.html` if the BR page renders both
  conferences in a single document. Verify by capturing
  `/leagues/NBA_2024.html` and inspecting.

Per-endpoint URL capture list (with a sample season of **2024**):

| Dataset id            | URL                                              | raw/ file                                |
|-----------------------|--------------------------------------------------|------------------------------------------|
| `per-game`            | `/leagues/NBA_2024_per_game.html`                | `raw/league_per_game_stats/2024.html`     |
| `per-36-minutes`      | `/leagues/NBA_2024_per_minute.html`              | `raw/league_per_36_minutes/2024.html`     |
| `totals`              | `/leagues/NBA_2024_totals.html`                  | `raw/league_totals/2024.html`             |
| `per-100-possessions` | `/leagues/NBA_2024_per_poss.html`                | `raw/league_per_100_possessions/2024.html`|
| `shooting`            | `/leagues/NBA_2024_shooting.html`                | `raw/league_shooting/2024.html`           |
| `play-by-play`        | `/leagues/NBA_2024_play-by-play.html`            | `raw/league_play_by_play/2024.html`       |
| `transactions`        | `/leagues/NBA_2024_transactions.html`            | `raw/league_transactions/2024.html`       |
| `rookies`             | `/leagues/NBA_2024_rookies.html`                 | `raw/rookie_stats/2024.html`              |
| `standings`           | `/leagues/NBA_2024.html` (table#confs_standings_E/W) | `raw/standings/2024.html`             |
| `standings-by-date`   | `/leagues/NBA_2024_standings_by_date_Eastern.html` + `_Western.html` | `raw/standings_by_date/2024_eastern.html` + `2024_western.html` |
| `attendance`          | `/leagues/NBA_2024.html` (table#advanced-team)   | `raw/attendance/2024.html`                |

Note: `standings` and `attendance` both hit
`/leagues/NBA_2024.html` but parse different `<table>` elements.
The same raw HTML page satisfies both fetches; the `raw/`
directory must contain a single copy per (year, page) and the
fixture URL map uses the same path to look up both endpoints
(see `courtside_data/server/fixtures.py:142` for the
single-file-per-endpoint pattern).

Capture command (Linux / macOS / WSL):

```bash
curl -A 'Mozilla/5.0' \
  -o raw/league_per_game_stats/2024.html \
  'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'
# repeat for each row in the table above
```

Basketball-Reference rate-limits aggressively (~8-9 req/min);
space the captures accordingly. Save the HTML as-is (no
post-processing). The team-hub fixture capture TODO at
`courtside_data/server/fixtures.py:207` has the full per-endpoint
plan for that hub; the league-hub walker is a stripped-down
version (no per-team segment, no per-conference branching for
the static season-scoped endpoints).

## 8. Design decisions needed (BEFORE implementation)

Surface every decision that blocks implementation. Each item
lists the options, the recommended choice, and the rationale.

1. **Route shape: season in path or query string?**
   - (a) `/api/league/seasons/{season_end_year}/{dataset}` (path
     segment, mirrors team-hub)
   - (b) `/api/league/{dataset}?season_end_year={YEAR}` (query
     param)
   - **Recommended: (b)**. The League Hub is uniformly
     season-scoped (no entity identifier in the URL), so a
     path-segment-based route just adds noise. Query-param
     keeps the URL flat and matches the existing export
     endpoint (`/api/players/{id}/export?dataset=...&season=...`).
2. **`standings_by_date` - separate Hub, or dataset within
   League Hub?**
   - (a) Separate Hub (Date Hub)
   - (b) Dataset within League Hub with `league_date` scope
   - **Recommended: (b)**. The 1-dataset "Date Hub" is
     overkill; the workflow fans out to per-conference pages
     which are already keyed by `season_end_year` (the
     `conference` token is internal). A single
     `league_date` scope is the smallest delta from the
     team-hub pattern.
3. **Should `season_schedule`, `players_season_totals`
   (currently in the GAMES / PLAYER domain) be part of the
   League Hub?**
   - (a) Yes - league-wide per-season tables belong with the
     league hub.
   - (b) No - they remain in their existing domain.
   - **Recommended: (b) for the initial League Hub lane**.
     `season_schedule` is a season-wide schedule (no
     league-aggregate stats) and `players_season_totals` is a
     player-aggregated table. Both have an existing home. A
     future "Schedule Hub" or "Players Aggregate Hub" lane can
     re-evaluate.
4. **`standings_by_date` query-param shape**
   - (a) `?month=...&day=...&year=...` (3 query params)
   - (b) `?date=YYYY-MM-DD` (ISO 8601)
   - (c) `?month=X&day=Y&season_end_year=Z` (BR's internal
     params)
   - **Recommended: (b)** for the public API; the route layer
     parses the ISO date and derives `month` / `day` /
     `season_end_year` (or `season_start_year` for the
     pre-cutoff month) before calling the service. ISO 8601 is
     familiar, timezone-free, and trivially validated with
     Pydantic.
5. **Are 3 `friv_7_game_*` endpoints in scope?**
   - The 3 friv_7 endpoints are in the PLAYOFFS domain (not
     LEAGUE). They are listed in the Playoffs Hub roadmap, not
     this one. If the implementer wants to surface "League
     Fun Facts" or "League History" as a separate section, see
     the Playoffs Hub roadmap.

## 9. Dependencies and priority

**What must exist first:**

- The Team Hub pattern is proven (`docs/architecture/team-hub.md`,
  `courtside_data/server/team_catalog.py`,
  `courtside_data/server/team_service.py`). The League Hub is
  a "copy and adapt" exercise.
- The team-hub fixture transport (the TODO at
  `courtside_data/server/fixtures.py:207` for the
  `_team_only_map` / `_team_season_map` helpers) is **not** a
  hard prerequisite - the league-hub fixture transport can be
  wired independently and run before the team-hub one.

**What this Hub unblocks:**

- A dedicated "league landing page" in the UI: current
  season's stats, standings, transactions.
- A standings-by-date tool (no current UI surface exposes this
  data).
- A canonical home for league-wide per-game / per-100 /
  shooting / play-by-play averages (the player-hub
  `splits` and `on-off` datasets are per-team, not league-wide;
  the league-hub `per-game` is the league-aggregate equivalent).

**Effort estimate relative to Team Hub:**

The League Hub is **simpler** than the Team Hub. Reasoning:

- 11 datasets vs. 13.
- Uniform scope (all season-scoped, one date-scoped) vs. Team
  Hub's two scopes (`team` / `team_season`).
- No entity identifier (no `team_identifier` plumbing) vs. Team
  Hub's 6 routes including search/summary.
- No `_team_hero_stats` (no team-specific hero stats to
  assemble).
- No `TEAM_DISPLAY_NAMES` (no per-entity branding).
- 11 row models in two schema files (`schemas/league.py` and
  `schemas/standings.py`), all already exist.

Realistic effort: **~50% of the Team Hub lane** if the
implementer is fluent with the team-hub pattern, **~75%** for
a first-time pass.

## 10. Implementation checklist

Step-by-step checklist for the next implementer:

1. Create `courtside_data/server/league_models.py`
   (Pydantic models: `LeagueDatasetCatalogEntry`, `LeagueHubTab`,
   `LeagueHubCatalog`; reuse `EndpointRowsResponse` and
   `TransportMode` from `courtside_data/server/models.py`).
2. Populate `courtside_data/server/league_catalog.py`
   (the stub already exists; add the `LeagueDataset` frozen
   dataclass, `LEAGUE_DATASETS`, `LEAGUE_TABS`, `league_hub_catalog()`,
   and the column-helper functions, following the
   `TEAM_DATASETS` pattern line-for-line).
3. Create `courtside_data/server/league_service.py`
   (the `LeagueHubService` class with `dataset` and `csv`;
   mirror `courtside_data/server/team_service.py` but drop the
   entity-identifier plumbing and the `summary` / `_team_hero_stats`
   methods).
4. Add the 4 routes to `courtside_data/server/app.py`
   (catalog, season-route, date-route, export; mirror the
   existing team-hub route block at `app.py:218-332` but
   collapse to a flat URL shape).
5. Add the `LEAGUE_ENDPOINTS` whitelist entry to
   `courtside_data/server/fixtures.py` (mirror the
   `TEAM_ENDPOINTS` / `TEAM_SEASON_ENDPOINTS` whitelists at
   `fixtures.py:41-62`; add a new `LEAGUE_ENDPOINTS` frozenset
   covering the 11 entries).
6. Wire the league-hub fixture transport
   (`_league_season_map` helper in `fixtures.py`; mirror
   `_team_season_map` at `fixtures.py:150` but without the
   per-team segment).
7. Capture the 11 fixture HTML files (see [§7](#7-fixture-capture-plan)).
8. Create the UI feature module
   (`ui/src/features/league-hub/`; mirror `ui/src/features/team-hub/`
   structurally).
9. Write tests (`tests/server/test_league_hub_api.py`; mirror
   `tests/server/test_player_hub_api.py`).
10. Run `uv run task audit` to confirm lint / format / type /
    test are all green.

When this checklist is done, the League Hub is feature-complete
and parity with the Team Hub scaffolding.

<!-- TODO(league-hub): start the implementation lane.

What: kick off the League Hub implementation by following the
§10 checklist in this doc. Start with the catalog stub
(courtside_data/server/league_catalog.py - already created,
needs the LeagueDataset dataclass, LEAGUE_DATASETS tuple, and
LEAGUE_TABS) and the Pydantic models
(courtside_data/server/league_models.py - new file).

Where:
  - courtside_data/server/league_catalog.py  (the stub; see
    the TODO(league-hub) block at the top).
  - courtside_data/server/team_catalog.py  (the 426-line
    pattern to mirror; this is the canonical "how to build
    a Hub catalog" reference).
  - courtside_data/server/team_service.py  (the 510-line
    pattern to mirror for the service layer; remove the
    team-identifier plumbing and the summary/_team_hero_stats
    methods).
  - docs/architecture/team-hub.md  (the proven doc structure
    and HTTP contract; mirror its § HTTP contract and
    § Fixture HTML needed sections for the new hub).

How:
  1. Create courtside_data/server/league_models.py with the
     Pydantic models (LeagueDatasetCatalogEntry, LeagueHubTab,
     LeagueHubCatalog; reuse EndpointRowsResponse and
     TransportMode from courtside_data/server/models.py).
  2. Populate courtside_data/server/league_catalog.py: add
     LeagueDataset (mirror TeamDataset), LEAGUE_DATASETS (11
     entries, see the comment block in the stub), LEAGUE_TABS
     (4 tabs: stats / transactions / standings / attendance),
     and the league_hub_catalog() function.
  3. Create courtside_data/server/league_service.py with the
     LeagueHubService class. The service has just two public
     methods: dataset(dataset_id, season_end_year) and
     csv(dataset_id, season_end_year). No summary, no search,
     no team-identifier plumbing.
  4. Add the 4 routes to courtside_data/server/app.py.
  5. Add the LEAGUE_ENDPOINTS whitelist + league fixture
     transport to courtside_data/server/fixtures.py.
  6. Capture the 11 fixture HTML files (see §7 in this doc).
  7. Create ui/src/features/league-hub/ (mirror
     ui/src/features/team-hub/ structurally; the season
     picker is the central control).
  8. Write tests in tests/server/test_league_hub_api.py
     (mirror tests/server/test_player_hub_api.py).
  9. Run uv run task audit.

Decision needed: which design decisions in §8 the team
agrees with before starting (the route shape, the
standings_by_date scope, the home for season_schedule /
players_season_totals, the date-param shape). The
recommendations in this doc are defaults; the implementer
should confirm or override them in the lane's first PR
description.

Verify: uv run pytest tests -n auto (must stay green
throughout) and TestClient(create_app(transport='live')).
get('/api/endpoints/league-hub').status_code == 200 after
the catalog and routes land.
-->
