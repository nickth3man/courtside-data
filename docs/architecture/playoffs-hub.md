# Playoffs Hub

Implementation roadmap for the Playoffs Hub, the fourth entity-Hub
domain in the Player Hub / Team Hub / League Hub / Playoffs Hub
family. The hub exposes 6 Basketball-Reference tables: 3
playoff-specific season-scoped stat tables (per-game / totals /
bracket) and 3 static (no-params) "seven-game series outcome"
matrices (team-is-up / tied / down).

The proven pattern lives in `docs/architecture/team-hub.md` (and
the `docs/architecture/league-hub.md` roadmap that's a sibling of
this doc). The Playoffs Hub is a "copy and adapt" exercise from
that pattern, with the entity swap (league -> playoffs) and a
**two-scope** scope set (`playoffs_season` for the per-season
tables; `playoffs_static` for the 3 friv_7 matrices).

## 1. Overview

The Playoffs Hub surfaces **playoff-specific Basketball-Reference
tables** - both season-keyed stat tables (per-game / totals /
bracket) and three static "what happens next" matrices
(seven-game series outcomes when a team is up 3-2, tied 2-2, or
down 2-3). It is the only Hub with a meaningful STATIC component
(no-params endpoints) besides the Draft/Awards/Leaders Hub.

How it relates to the existing hubs:

- **Player Hub** (`courtside_data.server.service.PlayerHubService`):
  entity is the player; primary interaction is the search box
  plus a player-identifier URL.
- **Team Hub** (`courtside_data.server.team_service.TeamHubService`):
  entity is the team; 13 datasets across two scopes
  (`team` / `team_season`).
- **League Hub** (see `docs/architecture/league-hub.md`): entity
  is the season; uniform season-scoped shape.
- **Playoffs Hub** (this roadmap): 3 season-scoped stat tables +
  3 static "friv" matrices. Primary interaction is a season
  picker for the stat tables; the friv matrices have no
  interaction (they're static).

The Playoffs Hub is a thin cousin of the League Hub: same
season-scoped shape for 3 of its 6 datasets, plus 3 no-param
endpoints. The service is the simplest of the four hubs because
there is no entity identifier and no date scoping - just
season-scoped and static.

## 2. Endpoint inventory

The 6 Playoffs Hub datasets are mapped 1:1 onto the
`courtside_data.endpoints._playoffs.PLAYOFF_ENDPOINTS` registry
entries (181 lines; see `_playoffs.py:89-181`). The table below
verifies the params / scope / row model for each entry.

| Dataset id                  | endpoint_name                                          | params            | EndpointSpec scope | row model                            | EndpointKind  | ParserShape      | spec    |
|-----------------------------|--------------------------------------------------------|-------------------|--------------------|--------------------------------------|---------------|------------------|---------|
| `per-game`                  | `playoff_per_game`                                     | `season_end_year` | SEASON             | `PlayoffPerGameRow`                  | GENERIC_TABLE | COMMENTED_TABLE  | `_playoffs.py:90`  |
| `totals`                    | `playoff_totals`                                       | `season_end_year` | SEASON             | `PlayoffTotalsRow`                   | GENERIC_TABLE | COMMENTED_TABLE  | `_playoffs.py:106` |
| `bracket`                   | `playoff_bracket`                                      | `season_end_year` | SEASON             | `PlayoffBracketRow`                  | WORKFLOW      | BRACKET          | `_playoffs.py:122` |
| `series-pattern-team-is-up` | `friv_7_game_playoff_series_outcomes_team_is_up`       | (none)            | STATIC             | `SevenGamePlayoffSeriesOutcomesRow`  | WORKFLOW      | TABLE            | `_playoffs.py:166` |
| `series-pattern-team-is-tied` | `friv_7_game_playoff_series_outcomes_team_is_tied`   | (none)            | STATIC             | `SevenGamePlayoffSeriesOutcomesRow`  | WORKFLOW      | TABLE            | `_playoffs.py:151` |
| `series-pattern-team-is-down` | `friv_7_game_playoff_series_outcomes_team_is_down`   | (none)            | STATIC             | `SevenGamePlayoffSeriesOutcomesRow`  | WORKFLOW      | TABLE            | `_playoffs.py:136` |

Row model file:line references:

- `PlayoffPerGameRow` - `courtside_data/schemas/playoffs.py:49`
- `PlayoffTotalsRow` - `courtside_data/schemas/playoffs.py:68`
- `PlayoffBracketRow` - `courtside_data/schemas/playoffs.py:101`
- `SevenGamePlayoffSeriesOutcomesRow` -
  `courtside_data/schemas/playoffs.py:134` (shared by all 3
  friv_7 endpoints)

URL templates (per the EndpointSpec `path` field):

| dataset id                | URL template                                                |
|---------------------------|-------------------------------------------------------------|
| `per-game`                | `/leagues/NBA_{YEAR}_per_game.html` (table `per_game_stats_post` inside a comment) |
| `totals`                  | `/leagues/NBA_{YEAR}_totals.html` (table `totals_stats_post` inside a comment) |
| `bracket`                 | `/playoffs/NBA_{YEAR}.html` (workflow selects table `all_playoffs`) |
| `series-pattern-team-is-up` | `/friv/7-game-playoff-series-outcomes-22111.html` (table `team-is-up`) |
| `series-pattern-team-is-tied` | `/friv/7-game-playoff-series-outcomes-22111.html` (table `team-is-tied`) |
| `series-pattern-team-is-down` | `/friv/7-game-playoff-series-outcomes-22111.html` (table `team-is-down`) |

Note: the 3 friv_7 endpoints hit the **same URL** but select
**different `<table>` elements** within the page (the page
repeats the same matrix for "team is up", "team is tied", and
"team is down"). The EndpointSpec's `table_id` differs per
endpoint; the `raw/` fixture file is the same HTML page.

## 3. HTTP route design

Mirror the League Hub's flat shape. The proposed routes:

| Method | Path                                                                | Response                                |
|--------|---------------------------------------------------------------------|-----------------------------------------|
| `GET`  | `/api/endpoints/playoffs-hub`                                       | `dict[str, object]` (catalog)            |
| `GET`  | `/api/playoffs/{dataset}?season_end_year={YEAR}`                    | `EndpointRowsResponse`                  |
| `GET`  | `/api/playoffs/series-pattern-*` (the 3 static friv_7 datasets)     | `EndpointRowsResponse` (no season param) |
| `GET`  | `/api/playoffs/{dataset}/export?season_end_year={YEAR}`             | CSV `Response`                          |

### Why no `/api/playoffs/search`

No entity to search for. The League Hub makes the same
argument; mirror the rationale from
`docs/architecture/league-hub.md` §3.

### Why no `/api/playoffs/{playoff_identifier}/summary`

The Playoffs Hub has no entity identifier. The 3 season-scoped
endpoints are selected by season; the 3 static endpoints have
no parameters at all. Skip the summary route.

### Why a single flat season route (no `seasons/{year}/` path)

Same as League Hub: the hub is uniformly season-scoped (or
static), so a path-segment-based route is just noise. Query
params keep the URL flat.

### How the 3 friv_7 endpoints are routed

Each of the 3 friv_7 endpoints has a distinct dataset id
(`series-pattern-team-is-up`, `series-pattern-team-is-tied`,
`series-pattern-team-is-down`) and a distinct path on the route
tree:

```text
GET /api/playoffs/series-pattern-team-is-up
GET /api/playoffs/series-pattern-team-is-tied
GET /api/playoffs/series-pattern-team-is-down
```

The route layer dispatches by dataset id to the matching
EndpointSpec, and the `CourtsideClient` runs the workflow
selector with the configured `table_id` (`team-is-up` / `team-is-tied`
/ `team-is-down`). See the design decision in §8 for the
rationale.

## 4. Catalog design

The catalog mirrors `courtside_data/server/team_catalog.py` (the
proven pattern). The new files:

- `courtside_data/server/playoffs_catalog.py` - the catalog stub
  (already created; see the `TODO(playoffs-hub)` block at the top).
- `courtside_data/server/playoffs_models.py` - Pydantic response
  models (`PlayoffsDatasetCatalogEntry`, `PlayoffsHubTab`,
  `PlayoffsHubCatalog`; reuse `EndpointRowsResponse` from
  `courtside_data/server/models.py`).

The proposed `PLAYOFFS_DATASETS` tuple (6 entries) is documented
in `courtside_data/server/playoffs_catalog.py` as a comment block.
The proposed `PLAYOFFS_TABS` grouping:

| Tab id            | Scope             | Datasets                                          | Default dataset |
|-------------------|-------------------|---------------------------------------------------|-----------------|
| `player-stats`    | `playoffs_season` | `per-game`, `totals`                              | `per-game`      |
| `bracket`         | `playoffs_season` | `bracket`                                         | `bracket`       |
| `series-patterns` | `playoffs_static` | `series-pattern-team-is-up`, `-tied`, `-down`     | `series-pattern-team-is-up` |

Notes on the tab grouping:

- The `player-stats` tab groups per-game and totals because
  they share the same source page (`/leagues/NBA_{YEAR}_per_game.html`
  and `/leagues/NBA_{YEAR}_totals.html`) and the same column
  shape (per-game rates / counting stats). Mirror the
  League Hub's `stats` tab structure.
- The `bracket` tab is workflow-only; the row model is
  `PlayoffBracketRow` with the manually-laid-out series / team
  / result columns. The UI likely renders this as a tree
  (round-of-16 -> conf semis -> conf finals -> finals) rather
  than a flat table; coordinate with product.
- The `series-patterns` tab is the only STATIC tab across all
  four hubs. No season picker, no other controls - just
  the three matrices. The UI is likely 3 sub-tabs
  ("Up 3-2" / "Tied 2-2" / "Down 2-3") or a single page with
  3 stacked sections.

`default_visible_columns` per dataset: leave the tuples empty in
the first pass (mirror the team-hub scaffolding). The
team-hub TODO at `courtside_data/server/team_catalog.py:35` is
the reference curation pattern.

## 5. Service design

The new service class is `PlayoffsHubService` in
`courtside_data/server/playoffs_service.py`. It is the simplest
of the four hubs:

1. No entity identifier (no `team_identifier` plumbing).
2. No date scoping (no `month` / `day` / `year` params).
3. No hero stats to assemble.
4. No display-name mapping.

### Public API surface

```text
class PlayoffsHubService:
    def dataset(
        self,
        dataset_id: str,
        season_end_year: int | None,  # required for season datasets, None for static
    ) -> EndpointRowsResponse: ...

    def csv(
        self,
        dataset_id: str,
        season_end_year: int | None,
    ) -> str: ...
```

For STATIC datasets, `season_end_year` is `None` (or just
ignored). The service dispatches by `dataset.scope`:

- `playoffs_season`: requires `season_end_year`; raises
  `ValueError` if missing (mirror `TeamHubService._build_params`
  at `team_service.py:204-220`).
- `playoffs_static`: ignores `season_end_year`; the underlying
  EndpointSpec declares no params.

This two-mode public API matches the pattern that the
`TeamHubService.dataset` / `TeamHubService.season_dataset` pair
uses (the team hub has the same scope split).

### Workflow endpoints

`playoff_bracket` (workflow, `_PLAYOFF_BRACKET_WORKFLOW` at
`_playoffs.py:24-55`) and the 3 friv_7 endpoints (workflow,
`_FRIV_7_GAME_PLAYOFF_OUTCOMES_WORKFLOW` at `_playoffs.py:57-87`)
need no special service-level handling. They run through the
standard workflow executor; the service just serializes the
resulting rows.

The `playoff_bracket` workflow's first step is a `FETCH` keyed
by `season_end_year` (the only declared param). The
`friv_7_game_*` workflows have no declared params - the
`FETCH` step just hits the static URL.

### CSV column order

For each dataset, the CSV `fieldnames` come from
`endpoint.csv_columns` (declared on the EndpointSpec) - all 6
endpoints have a `csv_columns=` declaration. The
`PlayerHubService.csv_for_dataset` at `service.py:127` is the
reference pattern; the Playoffs Hub version is the same minus
the entity-identifier plumbing.

## 6. UI feature design

The new UI feature module lives at
`ui/src/features/playoffs-hub/` and mirrors
`ui/src/features/team-hub/` (the proven pattern). The
components:

| Component file         | Role                                                  |
|------------------------|-------------------------------------------------------|
| `playoffs-hub.tsx`     | Top-level shell: season picker + tab strip.           |
| `season-picker.tsx`    | Reuse the League Hub's season picker (extract to a shared module). |
| `static-tab.tsx`       | For the 3 static datasets: a 3-way tab inside the `series-patterns` tab ("Up 3-2" / "Tied 2-2" / "Down 2-3"). |
| `data-table.tsx`       | Reuse from `ui/src/features/team-hub/`.               |
| `dataset-panel.tsx`    | Reuse from `ui/src/features/team-hub/`.               |
| `bracket-tree.tsx`     | Optional: render the `bracket` dataset as a tree (rounds -> series -> teams), not a flat table. Coordinate with product. |

Primary interaction model:

- For the `player-stats` and `bracket` tabs: **season picker
  first**, then dataset.
- For the `series-patterns` tab: **no picker at all** - the
  3 matrices are static and identical across all seasons. The
  tab content is constant once the page loads; the user just
  switches between the 3 sub-tabs.

What differs from the team-hub pattern:

- No entity search.
- No entity-identifier URL; routes are flat
  (`/api/playoffs/{dataset}`).
- The `series-patterns` tab is the only STATIC tab; no
  season picker.

Cross-reference: `ui/src/features/team-hub/team-hub.tsx` for
the shell template; `ui/src/features/league-hub/season-picker.tsx`
(once the League Hub lands) for the shared season picker.

## 7. Fixture capture plan

To enable fixture mode, capture one HTML per endpoint (for
STATIC endpoints, just one file; for SEASON-scoped endpoints,
one per season).

Per-endpoint URL capture list (with a sample season of **2024**):

| Dataset id                  | URL                                                    | raw/ file                                                |
|-----------------------------|--------------------------------------------------------|----------------------------------------------------------|
| `per-game`                  | `/leagues/NBA_2024_per_game.html`                      | `raw/playoff_per_game/2024.html`                         |
| `totals`                    | `/leagues/NBA_2024_totals.html`                        | `raw/playoff_totals/2024.html`                           |
| `bracket`                   | `/playoffs/NBA_2024.html`                              | `raw/playoff_bracket/2024.html`                          |
| `series-pattern-team-is-up` | `/friv/7-game-playoff-series-outcomes-22111.html`      | `raw/friv_7_game_playoff_series_outcomes/22111.html` (or 3 copies split by state) |
| `series-pattern-team-is-tied` | `/friv/7-game-playoff-series-outcomes-22111.html`    | (same file as above)                                     |
| `series-pattern-team-is-down` | `/friv/7-game-playoff-series-outcomes-22111.html`    | (same file as above)                                     |

Note: the 3 friv_7 endpoints share a single underlying HTML
page. The fixture walker needs to map all 3 EndpointSpec names
to the same file but with different `table_id` selectors. One
option: store the file once at
`raw/friv_7_game_playoff_series_outcomes/22111.html` and have
the walker look it up for all 3 endpoint names. Another
option: store 3 copies at
`raw/friv_7_game_playoff_series_outcomes_team_is_up/22111.html`
etc. (matches the team-hub one-file-per-endpoint convention but
duplicates the bytes). The first option is cleaner; the walker
is a one-time write.

Capture command:

```bash
curl -A 'Mozilla/5.0' \
  -o raw/playoff_per_game/2024.html \
  'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'
# repeat for each row above
```

Basketball-Reference rate-limits aggressively (~8-9 req/min);
space the captures accordingly.

## 8. Design decisions needed (BEFORE implementation)

1. **How to surface the 3 friv_7 endpoints?**
   - (a) 3 separate routes under one tab, one per state
     (`/api/playoffs/series-pattern-team-is-up`, etc.).
   - (b) 1 route with a `state` query param
     (`/api/playoffs/series-pattern?state=up`).
   - (c) 1 route with no params; the dataset id is the state
     (`/api/playoffs/series-pattern-up`, `-tied`, `-down`).
   - **Recommended: (a) for parity with the EndpointSpec
     registry and a clean catalog surface**; (c) is functionally
     equivalent but routes 3 endpoints without a common prefix;
     (b) requires a new EndpointSpec wrapper or a query-param
     switch in the service. The team-hub TODO at
     `courtside_data/server/team_service.py:288-308` documents a
     similar decision (search-result type discriminator); mirror
     the conclusion.
2. **Route shape: season in path or query string?**
   - Same as League Hub: **query param**
     (`/api/playoffs/{dataset}?season_end_year={YEAR}`).
3. **`playoff_bracket` UI rendering: flat table or tree?**
   - The bracket endpoint emits one row per (series, team)
     pair, with the `result` column as free-form text. The
     BR page renders this as a tree (rounds), but the
     `PlayoffBracketRow` schema is flat.
   - (a) UI renders flat - simpler, mirrors the team-hub data
     table.
   - (b) UI groups by series and renders as a tree.
   - **Recommended: (a) for the first pass**; product can
     request a tree view later. The data shape is flat, the
     tree is a UI concern.
4. **Are the 3 friv_7 endpoints' "static" data truly static?**
   - Yes - the page is a single canonical document, BR has
     not changed its content since launch, and there is no
     season selector on the page. Verify with one or two
     captures across years (or just trust the EndpointSpec
     `scope=STATIC` declaration).

## 9. Dependencies and priority

**What must exist first:**

- The Team Hub pattern (proven) and the League Hub pattern
  (if available; this roadmap doesn't depend on the League
  Hub landing first - the two hubs are independent).

**What this Hub unblocks:**

- A "Playoffs Hub" landing page in the UI: current
  season's per-game / totals / bracket.
- The "Series Patterns" fun-facts section (3 matrices, no
  other UI surface exposes this data today).
- A "playoff bracket tree" view (UI layer only, depends on
  product priority).

**Effort estimate relative to Team Hub:**

The Playoffs Hub is **simpler** than the Team Hub. Reasoning:

- 6 datasets vs. 13.
- Two scopes (`playoffs_season` / `playoffs_static`) but
  STATIC datasets require no season logic in the service.
- No entity identifier.
- No hero stats.
- 4 row models in 1 schema file (`schemas/playoffs.py`), all
  already exist.
- The 3 friv_7 endpoints share one row model, so the catalog
  has only 4 distinct row models to surface.

Realistic effort: **~40% of the Team Hub lane** if the
implementer is fluent with the team-hub pattern, **~60%** for
a first-time pass.

## 10. Implementation checklist

1. Create `courtside_data/server/playoffs_models.py`
   (Pydantic models: `PlayoffsDatasetCatalogEntry`,
   `PlayoffsHubTab`, `PlayoffsHubCatalog`).
2. Populate `courtside_data/server/playoffs_catalog.py`
   (the stub already exists; add `PlayoffsDataset`,
   `PLAYOFFS_DATASETS`, `PLAYOFFS_TABS`,
   `playoffs_hub_catalog()`; mirror `TEAM_DATASETS`).
3. Create `courtside_data/server/playoffs_service.py`
   (`PlayoffsHubService` class with `dataset` and `csv`).
4. Add the 4 routes to `courtside_data/server/app.py`
   (catalog, season-route, static-routes for the 3 friv_7,
   export; mirror the existing team-hub route block at
   `app.py:218-332`).
5. Add the `PLAYOFF_ENDPOINTS` whitelist entry to
   `courtside_data/server/fixtures.py` (mirror the
   `TEAM_ENDPOINTS` / `TEAM_SEASON_ENDPOINTS` whitelists at
   `fixtures.py:41-62`; add `PLAYOFFS_ENDPOINTS` and
   `PLAYOFFS_STATIC_ENDPOINTS` frozensets).
6. Wire the playoffs-hub fixture transport
   (`_playoffs_season_map` and `_playoffs_static_map` helpers
   in `fixtures.py`; the static one is just a single
   `{page_path: html_file}` lookup).
7. Capture the fixture HTML files (see [§7](#7-fixture-capture-plan)).
8. Create the UI feature module
   (`ui/src/features/playoffs-hub/`).
9. Write tests (`tests/server/test_playoffs_hub_api.py`).
10. Run `uv run task audit`.

When this checklist is done, the Playoffs Hub is
feature-complete and parity with the Team Hub scaffolding.

<!-- TODO(playoffs-hub): start the implementation lane.

What: kick off the Playoffs Hub implementation by following
the §10 checklist in this doc. The Playoffs Hub is the
smallest of the 3 new hubs (6 datasets, 2 scopes, no entity
identifier) and is the recommended first new-hub lane to
land after this planning doc is reviewed.

Where:
  - courtside_data/server/playoffs_catalog.py  (the stub; see
    the TODO(playoffs-hub) block at the top).
  - courtside_data/server/team_catalog.py  (the 426-line
    pattern to mirror).
  - courtside_data/server/team_service.py  (the 510-line
    pattern to mirror for the service layer; remove the
    team-identifier plumbing and the summary/_team_hero_stats
    methods).
  - courtside_data/endpoints/_playoffs.py:89-181  (the 6
    PLAYOFF_ENDPOINTS entries; verify the table_id selectors
    for the 3 friv_7 endpoints).

How:
  1. Create courtside_data/server/playoffs_models.py with
     Pydantic models (PlayoffsDatasetCatalogEntry,
     PlayoffsHubTab, PlayoffsHubCatalog; reuse
     EndpointRowsResponse from courtside_data/server/models.py).
  2. Populate courtside_data/server/playoffs_catalog.py: add
     PlayoffsDataset (mirror TeamDataset), PLAYOFFS_DATASETS
     (6 entries, see the comment block in the stub),
     PLAYOFFS_TABS (3 tabs: player-stats / bracket /
     series-patterns), and the playoffs_hub_catalog()
     function.
  3. Create courtside_data/server/playoffs_service.py with
     the PlayoffsHubService class. The service has just two
     public methods: dataset(dataset_id, season_end_year) and
     csv(dataset_id, season_end_year). For STATIC datasets,
     season_end_year is None and ignored.
  4. Add the routes to courtside_data/server/app.py. Mirror
     the league-hub route shape (flat query-param URLs);
     add a separate route group for the 3 STATIC friv_7
     endpoints (no season param).
  5. Add the PLAYOFFS_ENDPOINTS and PLAYOFFS_STATIC_ENDPOINTS
     whitelists + the playoffs fixture transport to
     courtside_data/server/fixtures.py. The static
     transport is just a single {page_path: html_file}
     lookup (the 3 friv_7 endpoints share one HTML page).
  6. Capture the fixture HTML files (see §7 in this doc).
     3 season-scoped + 1 shared static page = 4 raw/ files.
  7. Create ui/src/features/playoffs-hub/ (mirror
     ui/src/features/team-hub/ structurally; reuse the
     league-hub season picker once the league-hub lane
     lands; the series-patterns tab is a 3-way sub-tab
     inside the parent tab).
  8. Write tests in tests/server/test_playoffs_hub_api.py.
  9. Run uv run task audit.

Decision needed: confirm the §8 design decisions before
starting (the friv_7 routing: 3 separate routes vs 1 query-
param route vs 1 state-as-segment route; the bracket UI
shape: flat table vs tree; the static-data assumption for
season_leaders / career_leaders). The recommendations in
this doc are defaults; the implementer should confirm or
override them in the lane's first PR description.

Verify: uv run pytest tests -n auto (must stay green
throughout) and TestClient(create_app(transport='live')).
get('/api/endpoints/playoffs-hub').status_code == 200 after
the catalog and routes land.
-->
