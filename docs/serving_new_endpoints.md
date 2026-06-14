# Serving new data — the endpoint recipe

The `raw/` corpus contains far more basketball-reference data than the project
serves. `scripts/audit_unserved_data.py` quantifies the gap and writes
[`docs/unserved_data_report.md`](unserved_data_report.md); this guide is the
companion that shows **how to turn any item in that report into a served
endpoint**.

The library is built for exactly this. `courtside_data/endpoints.py` says it
plainly: *"adding a new endpoint is a single registry entry."* The client
wrapper and the `courtside-data` CLI subcommand are generated from the registry,
so once the four pieces below exist, the endpoint is fully wired — public API,
CLI, JSON/CSV/DataFrame output, and the rate-limited HTTP path — with no extra
code.

---

## ⚠️ Precondition: fix sentinel-row handling first

Before adding **row-model** endpoints, address the validation robustness issue
documented in [`endpoint_smoke_report.md`](../endpoint_smoke_report.md): row
models reject basketball-reference *sentinel rows* (`"Did Not Play"`,
`"Did Not Dress"`, `"Not With Team"`, section headers, summary/aggregate rows),
and `_execute` validates the whole row list at once
(`adapter.validate_python(rows)`), so **one bad row aborts the entire endpoint**
with `SchemaDriftError`. 19 of the 50 current endpoints fail live for this exact
reason.

Any new trivial-scrape endpoint will hit the same wall the moment a sampled page
contains an inactive player or a section row. The two fixes (either is enough,
both is better):

1. **Tolerate sentinel rows in the models** — make `team_name_abbr` (and similar
   first-column enums) accept the sentinel strings as a nullable value.
2. **Per-row validation with skip-and-continue** — validate row-by-row and drop
   the rows that fail, instead of all-or-nothing on the list. Mirrors how the
   legacy `coerce_data`/`validate_rows` path already tolerates these rows.

This work is tracked separately and is **not** part of the inventory deliverable,
but it gates the value of every new row-model endpoint.

---

## Recipe A — a new single-table family (most of §A and §C)

Most unserved families are tagged *"Trivial table scrape"* in the report. Each
needs four edits. Worked example: serving `franchise_all_time_roster`
(`/teams/{ID}/players.html`, table `#franchise_register`).

### 1. Author the column contract from the fixture

The fixtures already exist in `raw/`, so authoring is offline. Add a temporary
stub entry to `ENDPOINTS` (path + `table_id` only), then ask the existing drift
auditor to print the real `data-stat` keys in document order:

```bash
python scripts/audit_table_coverage.py --keys --endpoint franchise_all_time_roster
# real (N): ['player', 'season_min', 'season_max', 'g', 'mp', 'fg', ...]
# missing-from-contract (N): [...]
```

The printed `real` list is the exact, ordered set of keys to model.

### 2. Column-name list → `courtside_data/output/columns.py`

```python
FRANCHISE_ALL_TIME_ROSTER_COLUMN_NAMES = [
    "player", "season_min", "season_max", "g", "mp", "fg", ...
]
```

### 3. Row model → `courtside_data/schemas/<domain>.py`

Add a `BRRow` subclass in the matching domain module (`teams.py`, `league.py`,
`players.py`, `playoffs.py`, …) and `register()` it. Use the **raw `data-stat`
key as the `validation_alias`** and reuse the coercion types in
`courtside_data/schemas/_fields.py` (`BRInt`, `BRIntOrNone`, `BRFloatOrNone`,
`BRPercentage`, `StrOrNone`, `PositionsField`):

```python
from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import BRInt, BRIntOrNone, BRPercentage

class FranchiseAllTimeRosterRow(BRRow):
    player: str = Field(validation_alias="player")
    season_min: BRIntOrNone = Field(default=None, validation_alias="season_min")
    g: BRIntOrNone = Field(default=None, validation_alias="g")
    fg_pct: BRPercentage = Field(default=None, validation_alias="fg_pct")
    # … one field per real key from step 1

register("franchise_all_time_roster", FranchiseAllTimeRosterRow)
```

`BRRow` carries `extra="ignore"`, so any key you omit is silently dropped — the
contract is exactly the fields you declare. (Conversely: a key that the report's
§B flags as *missing* is a key you forgot here.)

### 4. Registry entry → `courtside_data/endpoints.py`

One `TableEndpoint`, using the `_season` / `_team` / `_player` factory that
matches the URL's parameters (they wire the right `InvalidSeason` / `InvalidTeam`
/ `InvalidPlayer` error):

```python
"franchise_all_time_roster": _team(
    "/teams/{team_abbreviation}/players.html",
    params=("team_abbreviation",),
    table_id="franchise_register",
    row_model=teams.FranchiseAllTimeRosterRow,
    csv_columns=FRANCHISE_ALL_TIME_ROSTER_COLUMN_NAMES,
),
```

- Table hidden in an HTML comment? use `commented_table_id=` instead of
  `table_id=` (e.g. `franchise_career_leaders`, the playoff `_post` splits).
- No `data-stat` attributes (header-driven table)? add `use_header_fallback=True`.
- Don't add a client function or CLI command — both generate from the registry.

---

## Recipe B — recover dropped columns on an existing endpoint (§B)

No new endpoint. The §B table lists `data-stat` keys present in HTML but missing
from a served endpoint's contract. To recover them, **append the missing keys**
to that endpoint's row model (step 3) and its `*_COLUMN_NAMES` list (step 2).
Nothing else changes.

> The current report shows **0 actionable** §B items: every declarative
> endpoint's contract is already complete, and the listed keys belong to
> `custom`/`intentional_subset` endpoints whose wider key set is by design. Re-run
> the audit after each change to keep it that way.

---

## Recipe C — surface an orphan table on a page you already fetch (§C)

The §C section lists tables that sit on a page we already download for some
endpoint but that no endpoint declares — e.g. the playoff `_post` split tables
on league pages, `advanced`/`per_poss`/`adj_shooting`/`totals_stats` on a team
page, the per-quarter box tables. Serving one is **identical to Recipe A**, with
two conveniences:

- The fixture already exists under the sibling endpoint's `raw/` directory, so
  step 1's `--keys` works immediately against the existing corpus.
- Point the new `TableEndpoint` at the **same `path`** as the sibling endpoint,
  with the orphan id as its `table_id`/`commented_table_id`. Example: a
  `team_per_game_stats` endpoint reusing `/teams/{ID}/{YEAR}.html` with
  `table_id="per_game_stats"`.

If you want a dedicated example fixture, add a curated entry to
`scripts/raw_download.py`; otherwise the sibling's fixtures are enough to develop
and test against.

---

## Recipe D — bespoke multi-table pages (the §A "bespoke" group)

Pages with many anchored tables or non-`data-stat` structure — `coaches`,
`executives`, `referees`, `playoff_series_matchup`, the all-star game boxscores,
`league_ratings`, `boxscore_shot_chart` — cannot use the single-table fast path.
Mark the registry entry `custom=True` and implement a same-named method on
`HTTPService` that fetches the page and assembles rows itself (see the existing
`standings`, `players_season_totals`, and `team_box_scores` methods as
templates). Row models + `register()` still apply per logical table.

---

## Verify

1. **Offline first.** Develop and test against the committed `raw/` fixtures via
   the integration suite (`raw_fixtures.py`); no network needed.
2. **Zero drift.** Re-run `python scripts/audit_table_coverage.py --endpoint <name>`
   — confirm no `MISSING`, no `UNRESOLVED`, no `TABLE-ID MISMATCH`.
3. **Re-measure the gap.** Re-run `python scripts/audit_unserved_data.py`; the new
   endpoint should drop out of §A/§C and `served_endpoints` should tick up.
4. **Live smoke.** Add the endpoint to `scripts/smoke_test_endpoints.py` and run a
   single live call to confirm real-world rows validate (this is where the
   sentinel-row precondition above bites if unaddressed).
5. **Docs regenerate** from the registry via `scripts/generate_reference.py`.
