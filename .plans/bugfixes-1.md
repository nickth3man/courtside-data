# Plan: Fix scraper-vs-fixture defects surfaced by the four-angle evaluation (PDCA cycle 1)

## Context

**The evaluation.** Four independent `@oracle` lanes audited the `courtside_data/` scraper against the
`raw/` fixture corpus, each forced to read actual scraper source and actual HTML (no reliance on the
offline scripts or derived reports):

| Angle | Lane  | Question                                                                | Verdict                                                                       |
| ----- | ----- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| A     | Coverage  | Which scraper paths have no fixture, and which fixtures have no typed endpoint? | Capture is complete; **~65% of the corpus (95 of 147 families) is untyped**.       |
| B     | Schema-drift | Do typed endpoints silently drop columns the page exposes?                | Reliable where typed (13/15 fully captured); **2 severe silent-drop cases**.        |
| C     | Parse-correctness | Given a fixture, does the scraper emit correct structured rows?           | ~85% correct; **`playoff_bracket` broken, 6 league tables leak a phantom row**. |
| D     | Health     | What is broken right now (`_failures/`, error path, manifest)?             | Corpus healthy; **1 stale failure; no `SchemaDriftError` ever fired**.            |

**The meta-finding (why these bugs survived).** Two structural blind spots in the existing audit
machinery explain every defect below:

1. **Corpus acquisition never runs the parser.** `scripts/raw_download.py` validates fetch-time gates
   (size, blocked markers, title, table-id presence) — *not* parse output. A fixture can be "healthy"
   while the endpoint that consumes it returns garbage. This is why `playoff_bracket`'s brokenness is
   invisible to D's health sweep.
2. **`extra="ignore"` swallows dropped columns** (`courtside_data/schemas/_base.py:25`). Silent drops
   never raise, so B's missing-column cases can't surface as failures — only an explicit alias/`data-stat`
   diff catches them.

Net: the project has good *capture* health and good *schema-existence* coverage, but no automated check
that ties **fixture → parse → expected output** for the typed endpoints. That gap is exactly where the
bugs live.

**Scope of this plan ("fix all").** The 7 confirmed defects below, ranked by severity, **plus a
regression gate (Deliverable 8) that makes the evaluation repeatable** — fixing the bugs without the
gate guarantees they recur. Promoting the 95 untyped families to typed endpoints is explicitly **out of
scope** (separate, slower track; they don't *fail*, they're just loose).

**Reconciliation note (one finding retracted).** C reported `season_schedule`'s multi-page logic was
"completely untested by the fixture corpus (only a 404 exists)." Direct verification contradicts this:
`raw/season_schedule/` holds **79 real multi-page fixtures** (`1980/april.html`, `1980/index.html`, …)
plus one `not_found.html`. C inspected only the top level and missed the per-season subdir layout
documented in `raw/codemap.md`. **No fix is needed for `season_schedule`.**

---

## Baseline (PLAN — current state, all directly verified)

| Metric                                                                     | Baseline | Target after cycle 1                            |
| -------------------------------------------------------------------------- | -------- | ----------------------------------------------- |
| Typed endpoints returning `col_N` fallback keys (parse failure)            | ≥ 1 (`playoff_bracket`) | 0                                               |
| Real `data-stat` columns captured by `PlayerSeasonTotalsRow`               | 22 / 32  | 32 / 32                                         |
| Real `data-stat` columns captured by `PlayerAdvancedSeasonTotalsRow`       | 27 / 29  | 29 / 29                                         |
| League-wide tables leaking "League Average" phantom row                    | 6        | 0                                               |
| Stale entries in `raw/_failures/`                                          | 1        | 0                                               |
| Derived reports declaring an already-curated endpoint as "unserved"        | 1 (`league_play_by_play`) | 0                                               |
| Typed endpoints covered by a fixture → parse → expected regression test    | unknown / ad hoc | 54 / 54                                         |

### Root causes

| Defect                                                                | Root cause                                                                                                   | Code locus                                              |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `playoff_bracket` returns garbage (112 rows, `col_1/2/3`, nested leakage) | `all_playoffs` has empty `<thead>` → `_fallback_headers` returns `[]`; descendant `tbody tr:not(.thead)` pulls rows from the **nested** per-game `<table>`. | `tables.py:62,86-93`; `schemas/playoffs.py:166-183`       |
| `players_season_totals` drops `trb` + all shooting %s                 | Schema lifted from legacy parser without re-walking the page; `extra="ignore"` hid the gap.                  | `schemas/players.py:409-440`                              |
| `players_advanced_season_totals` drops `games_started`, `awards`      | Same as above.                                                                                               | `schemas/players.py:446-489`                              |
| 6 league tables leak "League Average" row                             | `GenericTable` filters `.thead` but not `.norank`; BR emits the aggregate as `<tr class="norank">` in `<tbody>`. | `tables.py:62`                                            |
| `slug` is a required non-`data-stat` field in 3 custom endpoints       | `slug` is injected from `data-append-csv` in the bespoke fetcher; declared `required` with no defensive gate. | `schemas/players.py:419,459`; `schemas/boxscores.py:110`    |
| Transaction parser fragile to invalid nested-`<p>` (suspected double-emit) | `./p[normalize-space()]` matches both the outer (recovered) `<p>` and the inner `<p class="transaction">`.     | `tables.py:130-168`                                       |
| Stale artifacts mislead auditors                                      | URL migration completed at endpoint layer but failure snapshot / derived reports never reconciled.             | `raw/_failures/`, `docs/*.json`, `scripts/raw_download.py` |

---

## DO — Deliverables

Sequenced low-risk-first. **Each fix lands with its own regression test (the per-fix CHECK); Deliverable 8
is the consolidated standardization (the ACT).** No fix touches the 290 auto-generated endpoints.

### Deliverable 1 — `playoff_bracket` bespoke parser  *(highest severity)*

**File:** `courtside_data/http_service.py` (new method, mirroring `play_by_play()` at `:877-932` and
`standings()` at `:794-825`); `courtside_data/endpoints.py` (flip `playoff_bracket` to `custom=True` and
route to the new method).

**Why bespoke:** the `all_playoffs` table is a manually-laid-out bracket, not a `data-stat` grid. Two
compounding failures make the generic path unfixable without polluting `GenericTable`:
empty `<thead>` defeats header discovery, and the descendant row selector reaches into the nested
per-game table. Bracket-shaped tables need a dedicated extractor (same decision the project already
made for `play_by_play` / `standings` / `search`).

**Change shape:**
- New `HTTPService.playoff_bracket(self, ...)` that locates `table#all_playoffs`, walks only the
  top-level series rows (direct-child `<tr>`, exclude `tr.toggleable` / nested `<table>`), and maps each
  to `{series, team, result}` against the existing `PlayoffBracketRow` contract (`schemas/playoffs.py:166-183`).
- Set `custom=True` on the `playoff_bracket` `TableEndpoint` and wire the dispatch.
- Keep `PlayoffBracketRow` as-is (its docstring promise is correct; the parser is what failed to honor it).

**Acceptance (CHECK):** against `raw/playoff_bracket/2024.html`, the endpoint returns N rows (N =
top-level series count, ≈15 for 2024), every row validates as `PlayoffBracketRow` with `series/team/result`
keys, and zero rows carry `col_N` keys or come from the nested per-game table.

**Risk:** medium. Bracket layout varies by era; design the parser against ≥2 fixtures (recent + older)
from `raw/playoff_bracket/`.

---

### Deliverable 2 — Widen `PlayerSeasonTotalsRow` and `PlayerAdvancedSeasonTotalsRow`  *(silent data loss)*

**Files:** `courtside_data/schemas/players.py:409-440` and `:446-489`; corresponding CSV column lists in
`courtside_data/output/columns.py` (e.g. `PLAYER_SEASON_TOTALS_COLUMN_NAMES`) so new fields reach CSV output.

**Change shape — add to `PlayerSeasonTotalsRow`** (verify each `validation_alias` against the
`totals_stats` table in `raw/players_season_totals/2024.html` before merge):
```python
total_rebounds: BRIntOrNone = Field(default=None, validation_alias="trb")
field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
made_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2")
attempted_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2a")
two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
triple_doubles: BRIntOrNone = Field(default=None, validation_alias="tpl_dbl")
awards: StrOrNone = Field(default=None, validation_alias="awards")
```

**Change shape — add to `PlayerAdvancedSeasonTotalsRow`:**
```python
games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")  # confirm alias (may be "gs")
awards: StrOrNone = Field(default=None, validation_alias="awards")
```

**Acceptance (CHECK):** `players_season_totals` captures 32/32 real `data-stat` columns;
`players_advanced_season_totals` captures 29/29. Existing rows still validate (all new fields
`default=None`). CSV output includes the new columns.

**Risk:** low. Purely additive fields with defaults; no existing consumer breaks. The `trb`/percentage
additions are the high-value part (rebounding leaders + efficiency were silently missing).

---

### Deliverable 3 — Exclude the "League Average" phantom row  *(systematic, 6 endpoints)*

**Files:** `courtside_data/endpoints.py` (new declarative flag); `courtside_data/tables.py`
(`GenericTable` honors the flag); set the flag on the 6 league-wide `_season` endpoints.

**Approach (opt-in flag, NOT a global `GenericTable` change):** `GenericTable` is consumed by all 344
endpoints including the 290 auto-generated ones, so changing its row filter globally is high blast radius.
Instead mirror the existing declarative pattern (`use_header_fallback`, `transaction_list_fallback`):
add `exclude_summary_rows: bool = False` to `TableEndpoint`; in `GenericTable.__init__`, when set, extend
the row filter to `tbody tr:not(.thead):not(.norank)` (the League Average row is `<tr class="norank">`).
Set `exclude_summary_rows=True` on: `league_per_game_stats`, `league_totals`, `league_per_36_minutes`,
`league_per_100_possessions`, `league_shooting`, `league_play_by_play` (and verify
`playoff_per_game` / `playoff_totals` against their fixtures — same template, likely same flag).

**Acceptance (CHECK):** each of the 6 endpoints returns exactly N real player rows (no trailing
`name_display == "League Average"` row). Row counts drop by exactly 1 per affected table. A consumer
computing mean/count/stddev over `league_per_game_stats` is now correct.

**Risk:** low–medium. The `.norank` discriminator must be confirmed not to exclude legitimate data rows
elsewhere — gating it behind an explicit per-endpoint flag (default off) contains the blast radius. Verify
no other `<tr class="norank">` appears in these tables' `<tbody>` besides the aggregate.

---

### Deliverable 4 — Harden `slug` injection against single-point-of-failure  *(latent)*

**Files:** `courtside_data/http_service.py` (the bespoke fetchers for `players_season_totals`,
`players_advanced_season_totals`, `player_box_scores`); `courtside_data/schemas/players.py:419,459` and
`schemas/boxscores.py:110`.

**Problem:** `slug` is a *required* `BRRow` field but is **not** a real `data-stat` — it's injected from
the cell's `data-append-csv` attribute by the custom fetcher. If that injection step ever regresses,
**every row fails validation** (hard failure of the whole endpoint, not graceful degradation).

**Change shape:**
- Keep `slug` required (it is identity; loosening to optional weakens the contract).
- In each bespoke fetcher, after row extraction, add an explicit defensive check: if a row's `slug` is
  empty/missing, raise a descriptive domain error (e.g. extend `errors.py`) naming the endpoint + the
  offending row — *before* Pydantic surfaces it as an opaque `SchemaDriftError`.
- Add a regression test that feeds a fixture row with the `data-append-csv` attribute stripped and
  asserts the new error (not a generic validation traceback).

**Acceptance (CHECK):** the three endpoints still succeed against their fixtures; a stripped-`slug`
fixture triggers the named error with the endpoint identity in the message.

**Risk:** low. Purely defensive; no happy-path behavior change.

---

### Deliverable 5 — Stabilize the transaction-list parser against nested-`<p>`  *(fragile, verify-first)*

**File:** `courtside_data/tables.py:130-168` (`parse_transaction_list`).

**Verify before fixing (C flagged this as *suspected* double-emission but UNTESTED):** write a probe test
that runs `parse_transaction_list` against `raw/team_transactions/BOS_2024.html` and
`raw/league_transactions/2024.html` and asserts the per-date transaction count. BR wraps each transaction
in invalid `<p><p class="transaction">…</p></p>`; lxml's recovery turns this into two sibling `<p>`s, and
the current `./p[normalize-space()]` may match both → duplicate rows.

**Change shape (only if double-emission confirmed):** tighten the xpath to target the inner transaction
paragraph specifically, e.g. `./p[@class="transaction"]` (or `./p[contains(@class,"transaction")]`),
falling back to `./p[normalize-space()]` only if the class is absent (older fixtures).

**Acceptance (CHECK):** per-date transaction count matches the fixture's visible transactions exactly
(no duplicates); existing `league_transactions` / `team_transactions` tests still pass.

**Risk:** low. Constrain the change to the transaction path; confirm against both modern
(class-attributed) and any older fixtures.

---

### Deliverable 6 — Clean stale artifacts  *(cosmetic / accountability)*

**Files / artifacts:**
- `raw/_failures/friv_7_game_playoff_series_outcomes__7-game-playoff-series-outcomes.html.failed.html`
  + its `.failed.meta.json` — **delete**. The endpoints migrated to `-22111` (`endpoints.py:314-331`);
  this snapshot is dead weight from the pre-migration URL. Also remove the stale legacy URL row in
  `scripts/build_bref_inventory_csv.py:1374-1375`.
- `docs/raw_coverage_backlog.json` — remove `league_play_by_play` from `unserved_families` (it is
  curated at `endpoints.py:252-257` with `row_model=league.LeaguePlayByPlayRow`). Decide whether to keep
  shipping the older `docs/unserved_data_report.json` alongside it (they diverge: 1 vs 18
  `orphan_tables`) — recommend deleting the superseded one to remove the maintenance hazard.
- `scripts/raw_download.py` `write_manifest` (`:1658-1692`) — add a `persistent_failures` field (count
  of `raw/_failures/*.failed.html`) so `manifest.stats.failed` no longer reads as "0 known failures"
  when `_failures/` is non-empty. Optional: rename `endpoints_covered` →
  `endpoint_names_with_fixtures` for clarity (it is 148, not the 344 registered endpoints).
- `raw/league_per_100_possessions/1973.html` — a 404 page (pre-1974 seasons have no per-poss data)
  currently counted as a regular fixture in `endpoint_counts`. Either move it under `raw/errors/` or add
  a `category: "negative"` flag to its sidecar and teach the manifest builder to separate positive vs.
  negative fixtures. (Runtime is safe — `error_mappings` maps 404 → `InvalidSeason` — this is a
  classification cleanup only.)

**Acceptance (CHECK):** `raw/_failures/` is empty; backlog JSON contains no already-curated endpoints;
`manifest` exposes a non-misleading failure count; the 1973 per-poss page is not counted as a positive
fixture.

**Risk:** very low. Documentation/classification only; no runtime behavior change.

---

### Deliverable 7 — Regression gate: fixture → parse → expected for all typed endpoints  *(the ACT / standardization)*

**New:** `tests/integration/client/test_typed_endpoints_golden.py` (or extend the existing
`tests/integration/client/` harness + `raw_fixtures.py`).

**Why this is the load-bearing deliverable:** it closes the meta-finding. Without it, Deliverables 1–6
are one-off fixes that silently rot back. With it, the evaluation becomes a repeatable CI check, and
the two structural blind spots (acquisition-doesn't-parse; `extra="ignore"` swallows drops) are closed
for the typed surface.

**Change shape:**
- For each of the 54 typed endpoints, parametrize a test that: loads its fixture(s) from `raw/`, runs
  the **offline** parse path (feed the fixture HTML straight into `HTTPService.fetch_table` /
  `GenericTable` / `extract_commented_table` / the bespoke method, bypassing HTTP), and asserts:
  1. **No `col_N` fallback keys** appear in any row (catches `playoff_bracket`-class header failures).
  2. **Row count** matches a committed expected count (catches League-Average leakage / nested-table
     leakage).
  3. **Captured column set** for the sample matches the fixture's real `data-stat` set (catches B-class
     silent drops — the `extra="ignore"` blind spot).
  4. Every row validates as its declared `BRRow` subclass.
- Reuse existing primitives: `courtside_data.tables.GenericTable`,
  `courtside_data.tables.extract_commented_table`, `tests/integration/client/raw_fixtures.py`.
- Commit expected outputs under `tests/integration/client/expected/` (or `docs/expected/`) — these are
  the golden masters; regenerate via a small script when BR.com legitimately changes a page shape
  (reviewed diff, not silent).

**Acceptance (CHECK):** the gate runs offline (no network), is green for all 54 typed endpoints on a
clean tree, and would have flagged every defect fixed in Deliverables 1–6. Add to CI.

**Risk:** medium effort, low runtime risk. This is the largest single deliverable; build it
incrementally — land it covering the 6 league endpoints + `playoff_bracket` + `players_season_totals`
first (the fixes), then expand to all 54.

---

## CHECK — cycle-level success criteria

The cycle is complete when **all** hold:

1. `python -m pytest tests/` is green, including the new golden-master gate covering 54/54 typed endpoints.
2. No typed endpoint emits a row with a `col_N` key (probe: assert across all typed-endpoint fixtures).
3. `PlayerSeasonTotalsRow` captures 32/32 and `PlayerAdvancedSeasonTotalsRow` 29/29 real columns; CSV
   output reflects the new columns.
4. Zero league-wide `_season` tables emit a `name_display == "League Average"` row.
5. `playoff_bracket` returns only top-level series rows validating as `PlayoffBracketRow`.
6. Transaction parser emits each dated transaction exactly once (verified against both team + league fixtures).
7. `raw/_failures/` is empty; `manifest` exposes a truthful failure count; no derived report lists an
   already-curated endpoint as unserved.
8. Re-running the four-angle evaluation (or the golden gate) against the updated tree surfaces **no new**
   silent-drop or parse-correctness defect in the typed surface.

---

## ACT — standardize

- The golden-master gate (Deliverable 7) becomes the durable version of this evaluation: it runs in CI
  on every change touching `courtside_data/`, `endpoints.py`, `schemas/`, or `tables.py`.
- Document the two closed blind spots in `courtside_data/codemap.md` so future contributors know the gate
  exists *because* acquisition doesn't parse and `extra="ignore"` swallows drops.
- The 95 untyped families remain on the separate, slower promotion track (per `data-serving.md`); this
  cycle explicitly does **not** touch them.

## What would change this plan

- If consumers only ever use the typed core and never aggregate over `league_*` or call `playoff_bracket`,
  Deliverables 1 and 3 still ship (they're real defects) but their priority drops below 2.
- If onboarding many long-tail consumers is imminent, pause Deliverable 7's expansion at the fix-related
  endpoints and instead prioritize typed-endpoint promotion for the highest-demand untyped families — the
  gate then grows with the typed surface rather than reaching for 54 upfront.
- If `.norank` turns out to mark legitimate data rows in some table, Deliverable 3's opt-in flag stays but
  the discriminator changes (e.g. filter on `name_display == "League Average"` at the runner layer instead).
