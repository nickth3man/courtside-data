# Draft / Awards / Leaders Hub

Implementation roadmap for the Draft / Awards / Leaders Hub, the
fifth entity-Hub domain in the Player Hub / Team Hub / League Hub /
Playoffs Hub / Draft-Awards-Leaders Hub family. The hub exposes 5
Basketball-Reference tables: 3 season-scoped (draft picks, season
awards, season awards voting) and 2 static (season leaders, career
leaders).

The proven pattern lives in `docs/architecture/team-hub.md` (and the
sibling roadmaps at `docs/architecture/league-hub.md` and
`docs/architecture/playoffs-hub.md`). The Draft/Awards/Leaders Hub
is the most diverse of the new hubs because the 5 endpoints span 4
distinct row models, 2 `EndpointKind`s (GENERIC_TABLE and
WORKFLOW), and a unique "tab-level award selector" interaction for
`season_awards_voting`.

## 1. Overview

The Draft / Awards / Leaders Hub surfaces a small but
high-signal set of Basketball-Reference tables:

- **Draft picks** for a season (round / pick / player / team).
- **Season awards** for a season (per-award winner summary).
- **Season awards voting** for a season (per-award voting detail,
  10 awards selectable).
- **Season leaders** (no params; default per-game stat category).
- **Career leaders** (no params; default PTS).

How it relates to the existing hubs:

- **Player Hub**: player-centric; the Draft Hub is one
  season's worth of *new* players (the entry point to the
  player hub).
- **Team Hub**: team-centric; the Draft Hub is one
  season's worth of *new* team rosters.
- **League Hub** (see `docs/architecture/league-hub.md`):
  league-wide tables. The Draft / Awards / Leaders Hub
  complements it with "non-tabular" data (draft picks, award
  voting, leaderboards).
- **Playoffs Hub** (see `docs/architecture/playoffs-hub.md`):
  playoff-specific. The Draft / Awards / Leaders Hub is the
  non-playoff, non-league-aggregate complement.

The Draft / Awards / Leaders Hub has a unique challenge: the
`season_awards_voting` endpoint accepts an additional `award`
param (one of 10) on top of `season_end_year`. The route layer
must surface this as a tab-level "award" selector (see
[§8 Design decisions](#8-design-decisions-needed-before-implementation)).

## 2. Endpoint inventory

The 5 Draft / Awards / Leaders Hub datasets are mapped 1:1 onto
the `courtside_data.endpoints._draft_awards_leaders.DRAFT_AWARDS_LEADERS_ENDPOINTS`
registry entries (164 lines; see `_draft_awards_leaders.py:65-163`).
The table below verifies the params / scope / row model for each
entry.

| Dataset id            | endpoint_name           | params                          | EndpointSpec scope | row model                  | EndpointKind  | ParserShape | spec                              |
|-----------------------|-------------------------|---------------------------------|--------------------|----------------------------|---------------|-------------|-----------------------------------|
| `draft-picks`         | `draft_picks`           | `season_end_year`               | SEASON             | `DraftPicksRow`            | GENERIC_TABLE | TABLE       | `_draft_awards_leaders.py:66`     |
| `season-awards`       | `season_awards`         | `season_end_year`               | SEASON             | `SeasonAwardsRow`          | GENERIC_TABLE | TABLE       | `_draft_awards_leaders.py:79`     |
| `season-awards-voting` | `season_awards_voting` | `season_end_year`, `award`      | SEASON             | `SeasonAwardsVotingRow`    | WORKFLOW      | TABLE       | `_draft_awards_leaders.py:94`     |
| `season-leaders`      | `season_leaders`        | (none)                          | STATIC             | `SeasonLeadersRow`         | GENERIC_TABLE | TABLE       | `_draft_awards_leaders.py:122`    |
| `career-leaders`      | `career_leaders`        | (none)                          | STATIC             | `CareerLeadersRow`         | GENERIC_TABLE | TABLE       | `_draft_awards_leaders.py:141`    |

Row model file:line references:

- `DraftPicksRow` - `courtside_data/schemas/draft.py:27`
- `SeasonAwardsRow` - `courtside_data/schemas/awards.py:25`
- `SeasonAwardsVotingRow` - `courtside_data/schemas/awards.py:61`
  (inherits from `SeasonAwardsRow`)
- `SeasonLeadersRow` - `courtside_data/schemas/awards.py:89`
- `CareerLeadersRow` - `courtside_data/schemas/awards.py:111`

URL templates:

| dataset id               | URL template                                                |
|--------------------------|-------------------------------------------------------------|
| `draft-picks`            | `/draft/NBA_{YEAR}.html`                                    |
| `season-awards`          | `/awards/awards_{YEAR}.html` (table `mvp` w/ fallback `nba_mvp`) |
| `season-awards-voting`   | `/awards/awards_{YEAR}.html` (table selected by `award` param)  |
| `season-leaders`         | `/leaders/per_season.html` (table `stats_TOT`)              |
| `career-leaders`         | `/leaders/pts_career.html` (table `tot`)                    |

Special notes:

- `season_awards_voting` declares
  `fallback_table_ids=("mvp", "roy", "dpoy", "smoy", "mip",
  "clutch_poy", "coy", "leading_all_nba", "leading_all_defense",
  "leading_all_rookie")` - 10 awards. The route layer must
  accept the `award` param and pass it through to the workflow
  runner; the workflow's `normalize_award_id` step maps the
  award string to a `table_id` for the page selector.
- `season_leaders` and `career_leaders` both have
  `value_column=True` (the rightmost column header rotates with
  the active stat category; the parser renames it to a stable
  "value" key so the row model validates).
- `season_leaders` actually points at
  `/leaders/per_season.html` despite the dataset id
  suggesting a per-season selector. The page has an implicit
  season selector on the page itself; if a future product
  requirement wants a per-season "leaders" page, that needs a
  new EndpointSpec with `params=("season_end_year",)`. Today
  this is a no-param endpoint.

## 3. HTTP route design

Mirror the League Hub / Playoffs Hub flat shape. The proposed
routes:

| Method | Path                                                                          | Response                                |
|--------|-------------------------------------------------------------------------------|-----------------------------------------|
| `GET`  | `/api/endpoints/draft-awards-hub`                                             | `dict[str, object]` (catalog)            |
| `GET`  | `/api/draft-awards/{dataset}?season_end_year={YEAR}`                          | `EndpointRowsResponse`                  |
| `GET`  | `/api/draft-awards/season-awards-voting?season_end_year={YEAR}&award={award}` | `EndpointRowsResponse`                  |
| `GET`  | `/api/draft-awards/season-leaders`, `/career-leaders` (the 2 static endpoints)| `EndpointRowsResponse` (no params)      |
| `GET`  | `/api/draft-awards/{dataset}/export?season_end_year={YEAR}`                   | CSV `Response`                          |

### Why no `/api/draft-awards/search`

No entity to search for. Same as League Hub / Playoffs Hub.

### Why a `season-awards-voting` route with an `award` query param

The `season_awards_voting` EndpointSpec declares
`params=("season_end_year", "award")`. The route layer must
accept the `award` param (one of 10 string values - see
`fallback_table_ids` in the EndpointSpec). The cleanest
URL is `/api/draft-awards/season-awards-voting?season_end_year=
{YEAR}&award=mvp` (or any of the 9 other award ids). The
service passes both params through to the workflow executor.

The alternative - 10 separate routes for the 10 awards - is
considered in [§8 Design decisions](#8-design-decisions-needed-before-implementation).

### Why the 2 static endpoints get plain routes (no `?season=...`)

`season_leaders` and `career_leaders` are STATIC, no-params
endpoints. The route is just
`/api/draft-awards/season-leaders` and
`/api/draft-awards/career-leaders`. No query params, no
season picker. The data is the same on every fetch.

## 4. Catalog design

The catalog mirrors `courtside_data/server/team_catalog.py` (the
proven pattern). The new files:

- `courtside_data/server/draft_awards_catalog.py` - the catalog
  stub (already created; see the `TODO(draft-awards-hub)` block
  at the top).
- `courtside_data/server/draft_awards_models.py` - Pydantic
  response models (`DraftAwardsDatasetCatalogEntry`,
  `DraftAwardsHubTab`, `DraftAwardsHubCatalog`; reuse
  `EndpointRowsResponse` from `courtside_data/server/models.py`).

The proposed `DRAFT_AWARDS_DATASETS` tuple (5 entries) is
documented in `courtside_data/server/draft_awards_catalog.py` as
a comment block. The proposed `DRAFT_AWARDS_TABS` grouping:

| Tab id       | Scope                  | Datasets                                | Default dataset |
|--------------|------------------------|-----------------------------------------|-----------------|
| `draft`      | `draft_awards_season`  | `draft-picks`                           | `draft-picks`   |
| `awards`     | `draft_awards_season`  | `season-awards`, `season-awards-voting` | `season-awards` |
| `leaders`    | `draft_awards_static`  | `season-leaders`, `career-leaders`      | `season-leaders`|

Notes on the tab grouping:

- The `awards` tab groups the per-award summary
  (`season-awards`) with the per-award voting detail
  (`season-awards-voting`) because they share the same source
  page (`/awards/awards_{YEAR}.html`) and a tab-level "award"
  selector controls which award to surface.
- The `leaders` tab is the only STATIC tab; the user picks
  between the 2 datasets via a sub-tab (or radio).

`default_visible_columns` per dataset: leave the tuples empty in
the first pass (mirror the team-hub scaffolding). The
team-hub TODO at `courtside_data/server/team_catalog.py:35` is
the reference curation pattern.

## 5. Service design

The new service class is `DraftAwardsHubService` in
`courtside_data/server/draft_awards_service.py`. It mirrors
`TeamHubService` with the same simplifications as the Playoffs
Hub (no entity identifier, no date scoping, no hero stats).

### Public API surface

```text
class DraftAwardsHubService:
    def dataset(
        self,
        dataset_id: str,
        season_end_year: int | None,  # required for season datasets, None for static
        award: str | None = None,     # only for season-awards-voting
    ) -> EndpointRowsResponse: ...

    def csv(
        self,
        dataset_id: str,
        season_end_year: int | None,
        award: str | None = None,
    ) -> str: ...
```

For STATIC datasets, `season_end_year` and `award` are both
`None`. The service dispatches by `dataset.scope`:

- `draft_awards_season`: requires `season_end_year`;
  `season-awards-voting` additionally requires `award`. Both
  raise `ValueError` if missing.
- `draft_awards_static`: ignores both params.

### Workflow endpoints

`season_awards_voting` (workflow,
`_SEASON_AWARDS_VOTING_WORKFLOW` at
`_draft_awards_leaders.py:25-63`) needs no special service
handling beyond passing the `award` param through. The
workflow's `normalize_award_id` step maps the award string to
a `table_id`; the workflow's `select_award_table` step then
fetches the matching `<table>` from the page.

### CSV column order

For each dataset, the CSV `fieldnames` come from
`endpoint.csv_columns` (declared on the EndpointSpec) - all 5
endpoints have a `csv_columns=` declaration. The
`PlayerHubService.csv_for_dataset` at `service.py:127` is the
reference pattern; the Draft/Awards/Leaders Hub version is the
same minus the entity-identifier plumbing.

## 6. UI feature design

The new UI feature module lives at
`ui/src/features/draft-awards-hub/` and mirrors
`ui/src/features/team-hub/` (the proven pattern). The
components:

| Component file        | Role                                                       |
|-----------------------|------------------------------------------------------------|
| `draft-awards-hub.tsx`| Top-level shell: season picker + tab strip.                |
| `season-picker.tsx`   | Reuse the League Hub / Playoffs Hub's season picker.        |
| `award-selector.tsx`  | Tab-level dropdown for the 10 awards (only on the `awards` tab). |
| `data-table.tsx`      | Reuse from `ui/src/features/team-hub/`.                    |
| `dataset-panel.tsx`   | Reuse from `ui/src/features/team-hub/`.                    |
| `leader-cards.tsx`    | Optional: render the 2 leader datasets as a "Top 5" card grid (rank / player / value), not a flat table. |

Primary interaction model:

- For the `draft` and `awards` tabs: **season picker first**,
  then dataset (`draft-picks` or `season-awards` /
  `season-awards-voting`).
- For the `awards` tab with `season-awards-voting` active: an
  additional **award selector** dropdown (default `mvp`).
- For the `leaders` tab: **no picker at all**; the 2 datasets
  (`season-leaders` / `career-leaders`) are static. The user
  picks between them via a sub-tab.

What differs from the team-hub pattern:

- No entity search.
- No entity-identifier URL; routes are flat
  (`/api/draft-awards/{dataset}`).
- One tab (`awards`) has an additional level of interaction
  (the award selector).
- The `leaders` tab is STATIC, no season picker.

Cross-reference: `ui/src/features/team-hub/team-hub.tsx` for
the shell template; `ui/src/features/league-hub/season-picker.tsx`
(once the League Hub lands) for the shared season picker.

## 7. Fixture capture plan

To enable fixture mode, capture one HTML per endpoint (for
STATIC endpoints, just one file; for SEASON-scoped endpoints,
one per season).

Per-endpoint URL capture list (with a sample season of **2024**):

| Dataset id               | URL                                              | raw/ file                                                |
|--------------------------|--------------------------------------------------|----------------------------------------------------------|
| `draft-picks`            | `/draft/NBA_2024.html`                           | `raw/draft_picks/2024.html`                              |
| `season-awards`          | `/awards/awards_2024.html`                       | `raw/season_awards/2024.html`                            |
| `season-awards-voting`   | `/awards/awards_2024.html`                       | `raw/season_awards_voting/2024.html` (same HTML as above; the workflow selects by `award`) |
| `season-leaders`         | `/leaders/per_season.html`                       | `raw/season_leaders/default.html` (one file)             |
| `career-leaders`         | `/leaders/pts_career.html`                       | `raw/career_leaders/default.html` (one file)              |

Note: `season_awards` and `season_awards_voting` both hit
`/awards/awards_2024.html` but select different `<table>`
elements (and `season_awards_voting` switches by `award`). The
single raw HTML page satisfies both fetches; the
`raw/` directory must contain a single copy per (year, page) and
the fixture URL map uses the same path to look up both
endpoints.

For `season_awards_voting`, the route layer can pass the
`award` param to the workflow runner even in fixture mode - the
workflow's `normalize_award_id` step does the param-to-table-id
mapping, and the fixture URL map returns the same file. The
award selector is therefore free at the fixture layer.

Capture command:

```bash
curl -A 'Mozilla/5.0' \
  -o raw/draft_picks/2024.html \
  'https://www.basketball-reference.com/draft/NBA_2024.html'
# repeat for each row above
```

Basketball-Reference rate-limits aggressively (~8-9 req/min);
space the captures accordingly.

## 8. Design decisions needed (BEFORE implementation)

1. **How to surface the 10 `season_awards_voting` award options?**
   - (a) 1 route + tab-level award selector (dropdown of 10
     awards). Route:
     `/api/draft-awards/season-awards-voting?season_end_year=
     {YEAR}&award=mvp`. UI: dropdown in the `awards` tab.
   - (b) 10 separate datasets, one per award
     (`season-awards-voting-mvp`, `-roy`, etc.). 10 routes,
     10 catalog entries. No dropdown needed.
   - (c) 1 default `mvp` route + a query-param override
     (`/season-awards-voting` defaults to mvp; add
     `?award=roy` to switch).
   - **Recommended: (a) for UI flexibility and the smallest
     catalog surface**; (b) is the cleanest per-endpoint mapping
     but bloats the catalog (10 entries vs. 1); (c) is a
     compromise. Mirror the conclusion from the
     `team-hub` search TODO at
     `courtside_data/server/team_service.py:288-308` (the
     implementer will read that for cross-context).
2. **Route shape: season in path or query string?**
   - Same as League Hub / Playoffs Hub: **query param**
     (`/api/draft-awards/{dataset}?season_end_year={YEAR}`).
3. **Are `season_leaders` and `career_leaders` truly static?**
   - Today: yes, both have `EndpointSpec.scope=STATIC` and
     `params=()`. The page that `season_leaders` points at
     (`/leaders/per_season.html`) does have an implicit
     season selector on the page, but the EndpointSpec does
     not surface it as a parameter. If a future product
     requirement wants a per-season leaders endpoint, that
     needs a new EndpointSpec - not a route-layer change.
4. **Are the draft picks team- or season-identifier?**
   - The EndpointSpec declares `params=("season_end_year",)`
     only; team is a column on the row. The
     draft_picks route is `/api/draft-awards/draft-picks?
     season_end_year={YEAR}` (no team identifier). Users who
     want to drill into a single draft class' player use
     the Player Hub (`/api/players/{player_identifier}/...`)
     - the draft is the entry point to the player.
5. **`season_awards` default to MVP?**
   - The EndpointSpec declares
     `fallback_table_ids=("nba_mvp",)`. The default table is
     MVP; the route layer doesn't need to do anything special
     to surface other awards (they're not currently
     selectable on this endpoint). If product wants
     per-award navigation on `season-awards` (not just
     `season_awards_voting`), the EndpointSpec needs a new
     `award` param. Today this is out of scope.

## 9. Dependencies and priority

**What must exist first:**

- The Team Hub pattern (proven). This hub is the most
  diverse of the new three (4 distinct row models, 2
  EndpointKinds, the unique `season_awards_voting` award
  selector) but is still a "copy and adapt" exercise from the
  team-hub pattern.

**What this Hub unblocks:**

- A "Draft Hub" landing page (current year's draft picks
  for the upcoming draft; historical drafts for prior years).
- An "Awards" section in the UI (per-year awards + voting
  detail; one of the most-linked basketball-reference
  pages).
- A "Leaders" section (top-5 per stat for the current season
  and all-time). The UI today doesn't have a dedicated
  leaders surface.

**Effort estimate relative to Team Hub:**

The Draft / Awards / Leaders Hub is **similar in size** to
the Team Hub but **simpler in shape**. Reasoning:

- 5 datasets vs. 13.
- Two scopes (`draft_awards_season` / `draft_awards_static`)
  but STATIC datasets require no service logic.
- No entity identifier.
- No hero stats.
- 4 distinct row models in 1 schema file (`schemas/awards.py`),
  plus 1 in `schemas/draft.py`. All already exist.
- The `season_awards_voting` award selector is a unique
  interaction (no other Hub has a tab-level non-season
  param), but it's a small addition to the service / route
  layer.

Realistic effort: **~50% of the Team Hub lane** if the
implementer is fluent with the team-hub pattern, **~70%** for
a first-time pass.

## 10. Implementation checklist

1. Create `courtside_data/server/draft_awards_models.py`
   (Pydantic models: `DraftAwardsDatasetCatalogEntry`,
   `DraftAwardsHubTab`, `DraftAwardsHubCatalog`).
2. Populate `courtside_data/server/draft_awards_catalog.py`
   (the stub already exists; add `DraftAwardsDataset`,
   `DRAFT_AWARDS_DATASETS`, `DRAFT_AWARDS_TABS`,
   `draft_awards_hub_catalog()`; mirror `TEAM_DATASETS`).
3. Create `courtside_data/server/draft_awards_service.py`
   (`DraftAwardsHubService` class with `dataset` and `csv`;
   the `award` param is the new addition).
4. Add the 4 routes to `courtside_data/server/app.py`
   (catalog, season-route, awards-voting-route with `award`
   param, export).
5. Add the `DRAFT_AWARDS_LEADERS_ENDPOINTS` whitelist entry
   to `courtside_data/server/fixtures.py` (mirror the
   `TEAM_ENDPOINTS` / `TEAM_SEASON_ENDPOINTS` whitelists at
   `fixtures.py:41-62`; add `DRAFT_AWARDS_ENDPOINTS` and
   `DRAFT_AWARDS_STATIC_ENDPOINTS` frozensets).
6. Wire the draft-awards-hub fixture transport
   (`_draft_awards_season_map` and
   `_draft_awards_static_map` helpers in `fixtures.py`; the
   static one is a single `{page_path: html_file}` lookup).
7. Capture the fixture HTML files (see
   [§7](#7-fixture-capture-plan)).
8. Create the UI feature module
   (`ui/src/features/draft-awards-hub/`).
9. Write tests (`tests/server/test_draft_awards_hub_api.py`).
10. Run `uv run task audit`.

When this checklist is done, the Draft / Awards / Leaders
Hub is feature-complete and parity with the Team Hub
scaffolding.

<!-- TODO(draft-awards-hub): start the implementation lane.

What: kick off the Draft / Awards / Leaders Hub
implementation by following the §10 checklist in this doc.
This is the most diverse of the 3 new hubs (5 datasets
across 4 distinct row models, 2 EndpointKinds, and the
unique tab-level award selector for season_awards_voting).

Where:
  - courtside_data/server/draft_awards_catalog.py  (the stub;
    see the TODO(draft-awards-hub) block at the top).
  - courtside_data/server/team_catalog.py  (the 426-line
    pattern to mirror).
  - courtside_data/server/team_service.py  (the 510-line
    pattern to mirror for the service layer; remove the
    team-identifier plumbing and the summary/_team_hero_stats
    methods; the new addition is the award param).
  - courtside_data/endpoints/_draft_awards_leaders.py:65-163
    (the 5 DRAFT_AWARDS_LEADERS_ENDPOINTS entries; the
    season_awards_voting entry has fallback_table_ids for 10
    awards).

How:
  1. Create courtside_data/server/draft_awards_models.py with
     Pydantic models (DraftAwardsDatasetCatalogEntry,
     DraftAwardsHubTab, DraftAwardsHubCatalog; reuse
     EndpointRowsResponse from courtside_data/server/models.py).
  2. Populate courtside_data/server/draft_awards_catalog.py:
     add DraftAwardsDataset (mirror TeamDataset),
     DRAFT_AWARDS_DATASETS (5 entries, see the comment block
     in the stub), DRAFT_AWARDS_TABS (3 tabs: draft / awards
     / leaders), and the draft_awards_hub_catalog() function.
  3. Create courtside_data/server/draft_awards_service.py
     with the DraftAwardsHubService class. The service has
     just two public methods: dataset(dataset_id,
     season_end_year, award=None) and csv(dataset_id,
     season_end_year, award=None). The award param is the new
     addition (only used for season_awards_voting).
  4. Add the routes to courtside_data/server/app.py. Mirror
     the league-hub / playoffs-hub route shape (flat query-
     param URLs); add a separate route for
     season_awards_voting that accepts the award query param.
  5. Add the DRAFT_AWARDS_ENDPOINTS and
     DRAFT_AWARDS_STATIC_ENDPOINTS whitelists + the
     draft-awards fixture transport to
     courtside_data/server/fixtures.py.
  6. Capture the fixture HTML files (see §7 in this doc).
  7. Create ui/src/features/draft-awards-hub/ (mirror
     ui/src/features/team-hub/ structurally; the awards tab
     has an additional award-selector dropdown for the
     season_awards_voting sub-dataset).
  8. Write tests in tests/server/test_draft_awards_hub_api.py.
  9. Run uv run task audit.

Decision needed: confirm the §8 design decisions before
starting (the season_awards_voting routing: 1 dropdown
vs 10 sub-datasets vs 1 default + query-param override; the
season_leaders / career_leaders static-data assumption; the
draft_picks team-or-season-identifier question; the
season_awards default-to-MVP behavior). The recommendations
in this doc are defaults; the implementer should confirm or
override them in the lane's first PR description.

Verify: uv run pytest tests -n auto (must stay green
throughout) and TestClient(create_app(transport='live')).
get('/api/endpoints/draft-awards-hub').status_code == 200
after the catalog and routes land.
-->
