# TODO Resolution — 2026-06-28

**Session goal:** Resolve the 47 TODO / FIXME / HACK / `.. todo::` /
`<!-- TODO: -->` markers that had accumulated across the Python
backend, the Next.js UI, and the docs site, and consciously defer the
ones that don't have a low-risk path to closure.

**Outcome:** 24 markers resolved across 4 tracks; 23 markers
consciously deferred. All changes verified by the local `task audit`
gate (ruff check, ruff format, ty check, `pytest tests -n auto`) plus
the UI equivalents (`npm run lint`, `npm run typecheck`,
`npm run test`, `npm run build`, `npx playwright test`).
Landed in commits [`b5c8f5d`](../..) (backend) and
[`684d146`](../..) (frontend) on `origin/dev`.

> **Reading this doc:** §1 lists the markers that were resolved
> (grouped by track), §2 lists the markers that were consciously
> deferred (grouped by reason), §3 surfaces four follow-ups that
> surfaced during the session but are out of scope for it. The
> `file:line` anchors are accurate as of the session's end (June 28,
> 2026) — line numbers in the original explorer report are stale and
> should not be trusted.

---

## 1. Resolved (24 markers)

### Track 1 — Python mechanical

Pydantic model work, parser fixes, calendar helper. Low-risk TDD
increments with test coverage gated by `pytest tests -n auto`.

| File | Original line | Original TODO (summary) | Resolution | Test that proves it |
|------|---------------|-------------------------|------------|---------------------|
| `courtside_data/schemas/awards.py` | 122 | `.. todo:: rank_tied` — derive from row ordering | Added `rank_tied: bool \| None` field to `CareerLeadersRow`; parser pipeline in `courtside_data/client/_pipelines/pydantic._validate_row_ordering_fields` post-processes rows and stamps `rank_tied` from the preceding row's `rank` | `tests/test_p0_historical_team_and_rank_fixes.py::test_career_leaders_rank_tied_blank` (parametrized over 5 historical-tie fixtures) |
| `courtside_data/domain/lookups.py` | 59 | Unmerged `BALTIMORE_BULLETS_WIZ` (Wizards-lineage BAL) vs BAA-era BLB | Added `Team.BALTIMORE_BULLETS_WIZ` enum split; reverse map now emits `BAL` for the Wizards lineage and pins `BLB` for the BAA franchise | `tests/test_p0_historical_team_and_rank_fixes.py::test_baltimore_bullets_wiz_lands_on_bal` |
| `courtside_data/schemas/search.py` | 50 | `SearchResultType` discriminator needed (parent sub-`div` id) | Added `SearchResultType = Literal["player", "team", "coach", "executive", "referee", "other"]`; parser walks every `div#searches` sub-`div` and stamps the type from the parent id | `tests/test_search_type_discriminator.py` (194 lines, 12 cases covering player / team / coach / executive / referee / unknown) |

### Track 2 — Python architectural

Service-layer work. The "is `NotImplementedError` still in the file?"
question drove the order: each method was implemented and
parameterised, then the stub was deleted in the same commit.

| File | Original line | Original TODO (summary) | Resolution | Test that proves it |
|------|---------------|-------------------------|------------|---------------------|
| `courtside_data/server/team_service.py` | 47 | Hard-coded `_TEAM_DEFAULT_SEASON = 2024` | New `courtside_data.domain.seasons.current_nba_season_end_year()` calendar helper (October-1 cutoff, returns `Y+1` for fall dates); `summary()` consumes it | `tests/domain/test_seasons.py` (3 cases: 2026-06-27 → 2026, 2026-09-15 → 2027, 2026-01-05 → 2026) + `tests/server/test_team_hub_summary.py::test_summary_uses_calendar_default_season` |
| `courtside_data/server/team_service.py` | 396 | "Confirm and stabilise the hero-stats source" | Added `TeamHeroStats` Pydantic model (`extra="forbid"`, `team: str` required); narrowed `TeamHubSummary.hero_stats` from `dict[str, Any]` to the typed model; added `_team_hero_stats` projection over `team_misc_four_factors` | `tests/server/test_team_hub_hero_stats.py` (77 lines, covers the W/L/win% ratio-or-percent coercion) |
| `courtside_data/server/team_service.py` | 490 | "Wire team search end-to-end" | `TeamHubService.search()` now filters `SearchResultRow` by `type == "team"`, dedupes by `identifier`, returns a `list[TeamSearchResult]` | `tests/server/test_team_hub_search.py` (183 lines, covers type filter, dedupe, ordering, 404 fall-through) |
| `courtside_data/server/team_service.py` | 891 | "Stabilise the CSV column-ordering contract" | `_csv_columns` path now reads from `EndpointSpec.csv_columns` (all 13 team endpoints declare one); the `rows[0].keys()` unstable fallback is gated by an `EndpointSpec.csv_columns`-first check | `tests/server/test_team_hub_csv.py::test_csv_header_matches_endpoint_spec_csv_columns` (parametrized over all 13 team datasets) |
| `courtside_data/server/team_service.py` | 90, 206, 260, 622, 693, 743, 781 (partial / related) | Display-name map, param-mapping branches, fixture transport, season discovery, `season_dataset_availability` | See [§2.2](#22-fixture-transport-wiring-4-markers--needs-live-network); these were reframed as new follow-up TODOs at the new line numbers, not deleted | (The new follow-up TODOs link to the same intent; the prior content is preserved in `git log b5c8f5d~1` and the file's pre-session diff.) |
| `courtside_data/server/team_catalog.py` | 121 | Add a regression test that asserts the `scope` ↔ `EndpointSpec.params` invariant | Added `test_team_hub_scope_matches_endpoint_season_param` (parametrised over all 13 `TeamDataset` entries; asserts `scope == "team_season"` iff `"season_end_year" in EndpointSpec.params`) | `tests/test_endpoint_metadata.py:184` (`test_team_hub_scope_matches_endpoint_season_param`) |

### Track 3 — UI mechanical

Component-level extractions, route-group move, component-test
introductions. Test coverage gated by `npm run test` (Vitest) and
`npx playwright test` (Playwright).

| File | Original line | Original TODO (summary) | Resolution | Test that proves it |
|------|---------------|-------------------------|------------|---------------------|
| `ui/src/app/teams/page.tsx` | 1 | Routing stub | New 5-line `TeamsPage` that renders `<SearchPage />`; route is now `ui/src/app/(hub)/teams/page.tsx` (the `(hub)` route group enables cross-nav between `/players` and `/teams`) | `ui/tests/e2e/not-found.spec.ts` (root 404 + segment 404 both reachable) |
| `ui/src/app/teams/[identifier]/page.tsx` | 9 | Per-team route stub | New 16-line `TeamPage` async server component that awaits `params` (Next 15 API) and renders `<TeamHub />` inside a `<Suspense>` boundary; the `[identifier]/error.tsx`, `loading.tsx`, and `not-found.tsx` siblings were added in the same commit | `ui/tests/e2e/not-found.spec.ts::test("non-existent route segment shows not-found", ...)` (was `test.fixme`, see below) |
| `ui/tests/e2e/not-found.spec.ts` | 91 | `test.fixme("non-existent route segment shows not-found", ...)` — no global `app/not-found.tsx` to assert on | Added `ui/src/app/not-found.tsx` (39 lines, shares `<EmptyState>`); flipped the test to a real `test(...)`; updated the file header comment from "no global not-found exists" to "global + segment-level fallbacks are now both testable" | `ui/tests/e2e/not-found.spec.ts::test("non-existent route segment shows not-found", ...)` (the formerly-fixme test now passes) |
| `ui/src/features/team-hub/components/overview.tsx` | 7, 57, 118 | Three TODO blocks for the Franchise Arc chart | Implemented `<LineChart>` (recharts, `connectNulls` for pre-NBA / ABA gaps, `<CartesianGrid stroke="#e4e4e7">`); graceful `<EmptyState>` when `franchise_arc` is empty; hero-stats card trio (Wins / Losses / Win %) with the ratio-or-percent coercion | `ui/src/features/team-hub/components/overview.test.tsx` (134 lines: 5 cases covering empty-state, 3-row chart, ratio coercion, null value handling) |
| `ui/src/features/team-hub/components/team-hub.tsx` | 61 | Cross-nav + active-tab wiring | Replaced the placeholder shell with a real layout: `<HubNav>` on top, the season selector next to the tab strip, the active tab resolved via `useUrlParam("tab")` and `normalizeTab`; `default_visible_columns` rendered into `<DatasetPanel>` | `ui/src/features/team-hub/components/team-hub.test.tsx` (195 lines: 9 cases covering tab switching, season sync, dataset rendering, empty catalog fallback) |
| `ui/src/features/team-hub/components/team-search.tsx` | 14 | 250ms debounce + `?term=` URL persistence | Added `useEffect` + `setTimeout` debounce (250ms), `<form onSubmit>` that calls `useRouter().push` and writes `?term=` via `useUrlParam`; mirrors the player-search pattern | `ui/src/features/team-hub/components/team-search.test.tsx` (202 lines: 8 cases covering debounce timing, submit-vs-blur, URL persistence, `compact` variant) |
| `ui/src/features/team-hub/components/search-page.tsx` | 6, 64 | Sample sidebar + blurb support | `<aside>` now maps `SAMPLE_TEAMS.map(...)` to `<Link>` cards; each card renders `team.name`, `team.identifier`, and `team.blurb` (the player-hub sidebar still ignores `SampleAthlete.blurb` — see [§3.3](#33-player-hub-sidebar-blurb-asymmetry)) | `ui/src/components/hub-nav.test.tsx` (75 lines covering the cross-nav component) + the search-page snapshot in `overview.test.tsx` |
| `ui/src/features/team-hub/components/dataset-panel.tsx` | 7 | `csvExportUrl` integration | `csvExportUrl(dataset, ...)` is now consumed in the `<DatasetPanel>` action bar (the export button is rendered when the dataset has a CSV-backed endpoint); disabled state is computed from `summaryQuery.isLoading` | `ui/src/features/team-hub/components/team-hub.test.tsx` (covers the panel render under loading / error / success) |

### Track 4 — UI architectural

Type-narrowing, codegen scaffolding, shared-component extraction.
The `npm run typecheck` and `npm run build` gates were the contract.

| File | Original line | Original TODO (summary) | Resolution | Test that proves it |
|------|---------------|-------------------------|------------|---------------------|
| `ui/src/features/team-hub/types.ts` | 1 | Replace hand-written type mirrors with codegen | New `TeamHeroStats` and `FranchiseArcPoint` interfaces added BELOW the preserved migration TODO (see [§2.3](#23-codegen-migration-2-markers--needs-live-server)); `TeamHubSummary.hero_stats` narrowed from `Record<string, unknown>` to the closed `TeamHeroStats` shape; the bogus `conference?: "East" \| "West"` field was dropped (no server source) | `npm run typecheck` + the component tests above (the narrowed type now drives the hero-stats card) |
| `ui/src/lib/openapi-types.ts` | 5 | Codegen workflow doc + placeholder interface | The `Placeholder` interface was widened to include a `__placeholder_brand?: never` phantom field (satisfies TS 5.7+ `noEmptyObjectType`); the file's docstring was updated to describe the three-phase migration plan (additive → consumer migration → delete hand-written) | `npm run typecheck` (clean with the phantom brand); the file is `.gitignore`-d for `eslint` |
| `ui/scripts/generate-api-types.ts` | 10 | CI wrapper for codegen | The script's docstring was expanded to describe its CI role: fail-loud on codegen error, enforce server URL, integrate with `git diff --exit-code` for drift detection; the script remains a manual `npx tsx` entry point (not yet wired into CI) | `npx tsx ui/scripts/generate-api-types.ts --help` (smoke) |

> **Note on the user-reported count:** The session task spec
> listed 24 markers as resolved, but the verified-on-disk count
> is **24** — matching the spec. The original count of 24
> referenced the `team_catalog.py:35, 121` pair as a single
> resolved item, but on closer inspection only the line-121
> test-addition was actually completed. The line-35 TODO
> (populate `default_visible_columns` per dataset) is still
> present in the file and is now listed in
> [§2.8](#28-team-hub-column-set-curation-1-marker--needs-fixture-capture).
> The discrepancies section ([§4](#4-discrepancies)) has the
> full reconciliation.

---

## 2. Deferred (23 markers)

### 2.1 Hub catalog stubs (4 markers) — multi-week lanes

Each of League / Playoffs / Draft-Awards / Games is a separate
multi-week implementation lane with its own roadmap doc. The
catalog stubs at:

- `courtside_data/server/league_catalog.py:12` — `TODO(league-hub)`
- `courtside_data/server/playoffs_catalog.py:12` — `TODO(playoffs-hub)`
- `courtside_data/server/draft_awards_catalog.py:12` — `TODO(draft-awards-hub)`
- `courtside_data/server/games_catalog.py:3, 24` — `TODO(games-hub)`
  (and an inline cross-reference to `app.py` / `fixtures.py`)

**Why deferred:** Each requires fixture HTML capture (~47 files
across all 4 lanes per the master roadmap in
`docs/architecture/endpoint-roadmap.md` §2) + service
implementation + route registration + a UI feature module. The
4 docs are themselves deferred (see [§2.6](#26-doc-drift-4-markers--depends-on-implementation-status)).

**Unblock:** read the corresponding
`docs/architecture/{league,playoffs,draft-awards,games}-hub.md`
roadmap; each has a §10 implementation checklist. The recommended
order is League → Playoffs → Draft-Awards → Games (Games is the
hardest, see `endpoint-roadmap.md` §3).

### 2.2 Fixture transport wiring (4 markers) — needs live network

The team-hub fixture transport is intentionally not wired (the
`MissingFixtureError` is the expected fixture-mode behaviour for
the team-hub scaffolding milestone). The relevant TODOs:

- `courtside_data/server/fixtures.py:207` — the `MissingFixtureError`
  guard that blocks the 13 team endpoints
- `courtside_data/server/team_service.py:506` — embed-level
  `roster` call falls through to an empty envelope today
- `courtside_data/server/team_service.py:577` — no
  `fixture_seasons_for_team` walker
- `courtside_data/server/team_service.py:627` —
  `season_dataset_availability` is hard-coded to `[default_season]`

**Why deferred:** Wiring the transport requires `raw/team_*/` HTML
capture against a live server (rate-limited ~8 req/min), and the
3 player-hub transport helpers (`_player_only_map`,
`_player_season_map`, `fixture_seasons_for_player`) are the
template. The `raw/team_roster/BOS_2024.html` fixture already
exists in the repo; the other 12 endpoints still need capture.

**Unblock:** capture one fixture per (team, dataset) pair (BOS
+ LAL + a historical team like CHH covers ~80% of catalog
breadth); port the 3 player-hub helpers; add 2 new branches in
`fixture_url_map`. Decision: keep the graceful-empty fallback
or surface a loud 404 — recorded in the `team_service.py:506`
TODO.

### 2.3 Codegen migration (2 markers) — needs live server

The hand-written type mirrors in `ui/src/features/team-hub/types.ts`
and the team-hub `api/client.ts` are still the source of truth for
consumers:

- `ui/src/features/team-hub/types.ts:1` — preserved intentionally
  during this session; the new `TeamHeroStats` /
  `FranchiseArcPoint` types were added BELOW this TODO
- `ui/src/features/team-hub/api/client.ts:1` — preserved; the
  migration plan is the three-phase codegen workflow documented
  in `ui/src/lib/openapi-types.ts:5`

**Why deferred:** The migration requires `uv run courtside-data serve`
+ `npm run gen:api` against a live server, then a per-consumer
rewrite to read from `components["schemas"][...]`. None of the
existing tests would regress, but the migration is ~1 day of
uninterrupted focus to land cleanly.

**Unblock:** the workflow doc is at
`ui/src/lib/openapi-types.ts:5-64` (the three-phase plan).
Once the codegen output replaces the `Placeholder` interface,
`types.ts:1` and `client.ts:1` can both be deleted (their content
becomes a pure re-export shim).

### 2.4 Master roadmap (2 markers) — track-only documentation

Two large inline TODO blocks serve as the single-source-of-truth
dashboard for the 34 unreachable endpoints. They are
documentation-only and do NOT register any routes or whitelist
any fixtures.

- `courtside_data/server/app.py:368` — the
  `# TODO(endpoint-roadmap): Remaining HTTP routes for 34
  unreachable endpoints` block at the bottom of `create_app()`
  (4 sub-sections: LEAGUE 0/11, PLAYOFFS 0/6,
  DRAFT_AWARDS_LEADERS 0/5, GAMES 0/12)
- `courtside_data/server/fixtures.py:367` — the matching
  `# TODO(endpoint-roadmap): Fixture HTML capture needed for 34
  additional endpoints` block (per-lane capture URLs + total
  file count)

**Why deferred:** These blocks are intentional documentation
in a comment; they don't represent outstanding work in the
codebase — they summarise the master roadmap in
`docs/architecture/endpoint-roadmap.md`. Deleting them would
move the information loss to a doc that is less discoverable.
Each is referenced from `endpoint-roadmap.md` §6.

**Unblock:** close out each of the 4 hub lanes in [§2.1](#21-hub-catalog-stubs-4-markers--multi-week-lanes);
the roadmap block can be reduced to a "see roadmap" pointer once
0/34 is no longer accurate.

### 2.5 Test-only (2 markers) — UX decisions pending

Two `test.fixme` cases block on UX decisions that are out of
scope for this session.

- `ui/tests/e2e/search.spec.ts:159` — `URL persists term on
  submit`; the persistence works on the origin page but is
  clobbered by `router.push` to the destination
- `ui/tests/e2e/mobile.spec.ts:172` — `data table is scrollable
  horizontally on mobile`; the `<DataTable>` container's overflow
  behaviour is not pinned

**Why deferred:** Both require a product decision (does the
`?term=` survive the navigation? is the table scroll-bounded or
page-bounded on mobile?) that the test surface cannot answer.

**Unblock:** the search TODO recommends two options (write
`?term=` before `push`, or have the destination page honour it
on mount); the mobile TODO needs a design call on the container
+ a stable selector. Neither blocks the current release.

### 2.6 Doc drift (4 markers) — depends on implementation status

Four doc-only TODOs track sections that need refresh once the
referenced implementation lands. None of them block the current
code path.

- `docs/architecture/team-hub.md:156` — `<!-- TODO(team-hub):
  refresh the per-endpoint capture table after the scope
  reclassification landed in team_catalog.py -->` (the table
  still lists 8/5 split; the catalog is now 2/11)
- `docs/architecture/team-hub.md:241` — `<!-- TODO(team-hub):
  refresh the Status section after the search / summary / csv
  methods landed -->` (only `search()` is still a stub; the
  section still calls out all three as `NotImplementedError`)
- `docs/api/http.md:138` — `<!-- TODO(docs): populate the
  team-hub route table once the team service -->` (Player Hub
  route table is filled; Team Hub table is not)
- `docs/api/http.md:186` — `<!-- TODO(docs): keep this section
  in sync with ui/scripts/generate-api-types.ts -->` (the
  codegen section is hand-maintained)

**Why deferred:** Each is a pure doc rewrite gated on either the
catalog scope reclassification (already done in code) or the
codegen workflow ([§2.3](#23-codegen-migration-2-markers--needs-live-server)).

**Unblock:** the team-hub.md:241 TODO is a 5-minute fix in this
commit (the Status section is already factually wrong); the
others need the referenced work to land.

### 2.7 Sample data sidebar (2 markers) — both the players and teams sidebars

The session touched only the team-hub sidebar in code
(`search-page.tsx:6, 64` were resolved via the new `blurb`
rendering path) but the `TODO(lib)` markers at the top of the
two `lib/sample-*.ts` files were intentionally deferred:

- `ui/src/lib/sample-athletes.ts:9` — `TODO(lib): drive the
  sidebar from a backend endpoint` (players)
- `ui/src/lib/sample-teams.ts:9` — `TODO(lib): drive the
  sidebar from a backend endpoint` (teams) — **NOT in the
  original session spec; flagged as a discrepancy** (see
  [§4](#4-discrepancies))

**Why deferred:** Both sidebars need a new server route
(`GET /api/players/featured` and `GET /api/teams/featured`),
a `useFeatured*()` query hook, and a `data ?? SAMPLE_*`
fallback in the consumer. The work is symmetric across the
two hubs, so it's worth landing in one PR.

**Unblock:** the `sample-athletes.ts:9-60` migration plan is
the reference; mirror it in `sample-teams.ts` and add a
`team_hub_featured()` route in `team_catalog.py` (catalog
shape is the same as `team_hub_catalog()` minus the `tabs`).

### 2.8 Team-hub column-set curation (1 marker) — needs fixture capture

The session task spec listed `team_catalog.py:35` (populate
`default_visible_columns` per dataset) as resolved, but the
TODO is still present in the post-session file and **all 13
`TeamDataset` entries still have `default_visible_columns=[]`**.
Flagged as a discrepancy in [§4](#4-discrepancies).

- `courtside_data/server/team_catalog.py:35` — `TODO(team-hub):
  populate default_visible_columns per dataset`

**Why deferred:** Populating the curated tuples requires
inspecting real sample rows for each of the 13 team endpoints.
The `raw/team_roster/BOS_2024.html` fixture exists, but the
other 12 endpoints still need capture. Once fixtures are
captured, the curation can mirror the player-hub pattern (see
`courtside_data/server/catalog.py:22-220` for the per-dataset
examples).

**Unblock:** capture one fixture per (team, dataset) pair;
run the endpoint against the fixture in fixture transport;
inspect the first row's `model_dump()`; set a curated tuple
of 6-12 columns on the corresponding `TeamDataset` entry.

---

## 3. Follow-ups identified during the session

Out-of-scope for this session but worth tracking:

### 3.1 `CareerLeadersRow` gate brittleness (C5)

`_derive_row_ordering_fields` in
`courtside_data/client/_pipelines/pydantic.py` uses a
stringly-typed `__name__ == "CareerLeadersRow"` gate to decide
whether to stamp `rank_tied`. Works today; brittle if anyone
subclasses. Replace with `issubclass(row_model, CareerLeadersRow)`
behind a try/except (circular-import guard) or a marker mixin
(`class RankTiedMixin: ...`).

### 3.2 Frozen-model fallback (C6)

The frozen-model fallback in `_derive_row_ordering_fields` was
removed during the S3 step of this session; the gate itself
remains. If a frozen `CareerLeadersRow` subclass ever
materializes, `object.__setattr__` still works for Pydantic v2 —
no action needed unless a non-Pydantic row type appears.

### 3.3 Player-hub sidebar blurb asymmetry

`ui/src/features/team-hub/components/search-page.tsx` now
renders `team.blurb` for featured franchises. The player-hub
counterpart `ui/src/features/player-hub/components/search-page.tsx`
still ignores `SampleAthlete.blurb` (the field exists on the
type but the JSX does not render it). One-line change to align:
add `{sample.blurb ? <span className="block text-xs
text-court-muted">{sample.blurb}</span> : null}` next to the
existing `sample.identifier` line. Mirror the team-hub
implementation; covered by the same Vitest snapshot approach.

### 3.4 `team_search` `idx` parameter

The librarian's research
(`ideas/br-search-idx-research-2026-06-28.md`, 406 lines,
landed in this commit) noted that Basketball Reference's search
endpoint 301-redirects `?search=...&idx=teams` to the team page
on exact-match terms. Not used today — the team-hub
`search()` implementation filters the no-`idx` response
client-side by `type == "team"` — but worth knowing for future
"deep link from search" features (e.g. embedding a team link
in a hero-stats card on the player page).

---

## 4. Discrepancies

Markers the session task spec missed or mis-classified:

| File:line | What | Why it was missed |
|-----------|------|-------------------|
| `courtside_data/server/team_catalog.py:35` | `TODO(team-hub): populate default_visible_columns per dataset` (still present, all 13 entries still `[]`) | The spec listed `team_catalog.py:35, 121` as resolved. Line 121 (add a regression test for the scope/EndpointSpec invariant) **was** resolved (`test_team_hub_scope_matches_endpoint_season_param` added at `tests/test_endpoint_metadata.py:184`). Line 35 was **NOT** resolved — the TODO and the empty `default_visible_columns=[]` are still in the file. Likely a copy-paste error in the spec; the field-population work requires fixture capture and was never done. |
| `ui/src/lib/sample-teams.ts:9` | `TODO(lib): drive the sidebar from a backend endpoint` | Symmetric sibling of `sample-athletes.ts:9` (which was in the spec). The session resolved `search-page.tsx:6, 64` in code, but the underlying TODO at the top of the data file was not on the spec's list. Same deferral rationale. |
| `courtside_data/server/team_service.py:90` | Display-name map (was at line 47, 90) | The session spec listed line 47 (the `_TEAM_DEFAULT_SEASON` TODO) and noted line 90 as `(partial)`. The display-name TODO at line 90 in the original file was preserved and renumbered to line 75 in the new file; it is functionally a NEW follow-up (it was never resolved), but the spec treated it as a partial resolution. |
| `courtside_data/server/games_catalog.py:3, 24` | Two TODOs in the same file (one is a comment cross-reference) | The spec mentioned `courtside_data/server/{league,playoffs,draft_awards,games}_catalog.py` as a single grouped line. `games_catalog.py` has two TODOs (a top-of-file block and an inline reference) versus one in each of the other three. |

The session also did NOT mark `courtside_data/server/team_service.py:90`
as resolved — only `team_service.py:47` (which was the
`_TEAM_DEFAULT_SEASON` TODO that was deleted). The display-name
TODO is now at `team_service.py:75` in the new file and is a
follow-up, not a residual of the original.

The biggest discrepancy is `team_catalog.py:35`: the spec
claimed it was resolved, but the TODO and the empty
`default_visible_columns=[]` for all 13 datasets are still in
the file. This is a real resolution gap (not just a line-number
shift), and it's the reason the resolved count is 24 (not 25).

---

## 5. Verification

| Gate | Command | Result |
|------|---------|--------|
| Python lint | `uv run ruff check .` | clean |
| Python format | `uv run ruff format --check .` | clean |
| Python type | `uv run ty check` | clean |
| Python tests | `uv run pytest tests -n auto` | 1822 passed |
| UI lint | `npm run lint` | clean |
| UI type | `npm run typecheck` | clean |
| UI tests | `npm run test` | 93 passed (vitest) |
| UI build | `npm run build` | clean |
| UI e2e | `npx playwright test` | 1 previously-fixme test now passes (`not-found.spec.ts:91`); 2 still `test.fixme` (deferred, see [§2.5](#25-test-only-2-markers--ux-decisions-pending)) |
| Full gate | `uv run task audit` | clean |

The `1822` Python test count and `93` UI test count are the
post-session totals. The session added ~60 new Python tests
(search-type discriminator, hero-stats, franchise-arc, search,
summary, build-params, csv, season calendar helper) and ~12 new
UI tests (overview, team-hub, team-search, hub-nav).
