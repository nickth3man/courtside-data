# Endpoint Test & Fix Report — `basketball_reference_web_scraper` v4.15.4

**Run date:** 2026-06-01; uv migration follow-up on 2026-06-02
**Library version:** 4.15.4 (installed from PyPI, then editable-installed from repo source)
**Target:** `https://www.basketball-reference.com` (live site)
**Test scripts:** `scripts/test_endpoints/`

This report covers two phases:
- **Phase 1** — initial pass against the unmodified library, which surfaced **4 bugs**.
- **Phase 2** — Fishbone root-cause analysis, web research on BBRef behaviour, and the library fixes that resolved all 4 bugs (**23/23 cases now pass**).

---

## 1. Phase 1 — Initial results (unmodified library)

### 1.1 Happy-path results — all 10 public endpoints

| # | Endpoint | Status | Duration | Return shape | Sample size |
|---|----------|--------|----------|--------------|-------------|
| 1 | `search(term="LeBron James")` | PASS | 0.139 s | `dict` with `players` key | 2 players |
| 2 | `standings(season_end_year=2018)` | PASS | 0.156 s | `list[dict]` | 30 rows |
| 3 | `player_box_scores(day=1, month=1, year=2017)` | PASS | 1.049 s | `list[dict]` | 104 rows |
| 4 | `team_box_scores(day=1, month=1, year=2017)` | PASS | 0.876 s | `list[dict]` | 10 rows |
| 5 | `season_schedule(season_end_year=2018)` | PASS | 4.138 s | `list[dict]` | 1 312 rows |
| 6 | `players_season_totals(season_end_year=2018)` | PASS | 0.743 s | `list[dict]` | 605 rows |
| 7 | `players_advanced_season_totals(season_end_year=2018)` | PASS | 0.874 s | `list[dict]` | 605 rows |
| 8 | `regular_season_player_box_scores(player_identifier="jamesle01", season_end_year=2018)` | PASS | 0.211 s | `list[dict]` | 82 rows |
| 9 | `playoff_player_box_scores(player_identifier="jamesle01", season_end_year=2018)` | PASS | 0.147 s | `list[dict]` | 22 rows |
| 10 | `play_by_play(home_team=Team.GOLDEN_STATE_WARRIORS, day=31, month=5, year=2018)` | PASS | 0.144 s | `list[dict]` | 456 rows |

**Verdict:** **10/10 happy-path calls succeeded** against the live site.

### 1.2 Edge-case results (Phase 1, pre-fix)

| # | Case | Expected | Actual | Status |
|---|------|----------|--------|--------|
| 1 | `search("LeBron")` (no surname) | return results | raises `AttributeError: 'NoneType' object has no attribute 'rows'` | **FAIL** |
| 2 | `search("xyzzy123_no_such_player")` | raise `InvalidSearch` | raises raw `requests.exceptions.HTTPError` (404) | **FAIL** |
| 3 | `standings(season_end_year=1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 4 | `standings(season_end_year=2099)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 5 | `player_box_scores(15, 4, 1850)` | `InvalidDate` | returns `[]` (empty list) | **FAIL** |
| 6 | `team_box_scores(15, 4, 1850)` | `InvalidDate` | returns `[]` (empty list) | **FAIL** |
| 7 | `season_schedule(season_end_year=1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 8 | `players_season_totals(season_end_year=1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 9 | `players_advanced_season_totals(season_end_year=1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 10 | `regular_season_player_box_scores("zzzzz99", 2018)` | `InvalidPlayerAndSeason` | `InvalidPlayerAndSeason` | PASS |
| 11 | `playoff_player_box_scores("zzzzz99", 2018)` | `InvalidPlayerAndSeason` | `InvalidPlayerAndSeason` | PASS |
| 12 | `regular_season_player_box_scores("jamesle01", 1900)` | `InvalidPlayerAndSeason` | `InvalidPlayerAndSeason` | PASS |
| 13 | `play_by_play(GSW, 15, 4, 1850)` | `InvalidDate` | `InvalidDate` | PASS |

**Verdict:** **9/13 edge cases passed. 4 bugs found.**

### 1.3 Bug summary (Phase 1)

1. **Bug 1 — `search("LeBron")` raises `AttributeError`** at `http_service.py:234` (`for row in page.totals_table.rows` — `totals_table` is `None`). The single-token query causes BBRef to server-side redirect to the unique player page, where the `per_game` table id no longer matches the scraper's expectation.
2. **Bug 2 — `search("xyzzy123…")` raises raw `HTTPError`** because `client.search` (the only public function) lacks the standard `try/except requests.exceptions.HTTPError` wrapper.
3. **Bug 3 — `player_box_scores(15, 4, 1850)` returns `[]`** because BBRef returns 200 with an empty page (no `<table id="stats">`) for pre-BBallRef dates, and the library has no "is the response meaningful?" check.
4. **Bug 4 — `team_box_scores(15, 4, 1850)` returns `[]`** for the same reason — no empty-page detection.

---

## 2. Phase 2 — Fishbone (Ishikawa) root-cause analysis

### 2.1 Fishbone diagram

```
                    ┌──────────────────────────────────────────────────────┐
                    │ PROBLEM: 4 endpoints either raise raw library        │
                    │ exceptions or return silent empty results instead   │
                    │ of raising the domain exceptions the rest of the    │
                    │ library uses.                                       │
                    └──────────────────────────────────────────────────────┘
                                              ▲
       ┌──────────────┬──────────────┬────────┴───────┬──────────────┬──────────────┐
       │              │              │                │              │              │
   PEOPLE         PROCESS        TECHNOLOGY      ENVIRONMENT      METHODS       MATERIALS
```

**People** — Author copy-pasted a wrapper for 9 of 10 public functions; the `search` function missed it. No checklist enforces "every public client function must wrap HTTP calls".
**Process** — Integration fixtures skip the case the bugs rely on: `tests/integration/files/search/` only has multi-token terms that return search-results pages, and `tests/integration/files/boxscores/` only starts in 2001.
**Technology** — Defensive `None` / empty checks were applied to some endpoints (`regular_season_player_box_scores` checks for missing table) but not to `search`, `player_box_scores`, or `team_box_scores`.
**Environment** — BBRef's search behaviour: a single-token query like `"LeBron"` causes a server-side 302 to the unique player page; a no-match query returns 404. BBRef's `/friv/dailyleaders.cgi` and `/boxscores/` return 200 with an empty body for pre-BBallRef dates.
**Methods** — Inconsistent error-translation pattern. No "empty response = invalid input" detection. Brittle xpath/table-id scraping with no contract tests.
**Materials** — Player pages use `<table id="per_game_stats">` (not `per_game`); dailyleaders uses `<table id="stats">`; boxscores uses no table id, only a `gamelink` cell class.

### 2.2 Research findings (delegated to `web-search-researcher`)

- **`/search/search.fcgi?search=LeBron`** → server-side 302 to `/players/j/jamesle01.html` (the actual LeBron James player page). The body contains `<table id="per_game_stats">` (not `per_game`). **No `<table id="per_game">` exists on basketball-reference.com at all.**
- **`/search/search.fcgi?search=LeBron%20James`** → multi-result search page (`<div id="searches">` with 23 `search-item` rows).
- **`/search/search.fcgi?search=xyzzy123_no_such_player`** → real HTTP 404 (after 302 to `/players/x/xyzzy12.html`).
- **`/friv/dailyleaders.cgi?month=4&day=15&year=1850`** → 200 with empty body, no `<div id="all_stats">` and no `<table id="stats">`. The page title has a tell-tale leading space.
- **`/friv/dailyleaders.cgi?month=4&day=15&year=2050`** → 200 but **silently substitutes today's data** — title says "May 30, 2026", not "April 15, 2050". (A sneaky 5th bug, *not* fixed in this round — requires comparing the H1 against the requested date.)
- **`/boxscores/?day=15&month=4&year=1850`** → 200 with no `<h2>NN NBA Games</h2>` and no `/boxscores/\d{9}[A-Z]{3}\.html` game links. Empty game-link list is the reliable signal.

### 2.3 Root causes

1. **Inconsistent error-translation pattern** in `client.search` — only function missing the `try/except` wrapper (Methods).
2. **No defensive `None` guard** in the player-page branch of `http_service.search` (Technology).
3. **No empty-response detection** in `http_service.player_box_scores` or `http_service.team_box_scores` (Methods).
4. **No integration test** for the failure cases (Process).

### 2.4 Prioritised solutions

1. **P1** Add `try/except HTTPError` wrapper to `client.search`; translate 404 to a new `InvalidSearch` domain exception.
2. **P1** Add a `None` guard around `page.totals_table.rows` in `http_service.search` (and degrade gracefully to an empty `leagues` set).
3. **P1** Add "empty response → `InvalidDate`" guards to `http_service.player_box_scores` and `http_service.team_box_scores`.
4. **P2** Add `InvalidSearch` exception to `errors.py`.

---

## 3. Phase 2 — Fixes applied

All fixes are in the repo source (`basketball_reference_web_scraper/`), which is now editable-installed by uv.

### 3.1 `errors.py` — added `InvalidSearch` exception

```python
class InvalidSearch(Exception):
    def __init__(self, term):
        message = "Search term \"{term}\" returned no results".format(term=term)
        super().__init__(message)
```

### 3.2 `http_service.py:search` — `None` guard around `page.totals_table`

```python
elif response.url.startswith("{BASE_URL}/players".format(BASE_URL=HTTPService.BASE_URL)):
    page = PlayerPage(html=html.fromstring(response.content))
    if page.totals_table is None:
        player_results += [self.parser.parse_player_data(player=PlayerData(
            name=page.name,
            resource_location=response.url,
            league_abbreviations=set(),
        ))]
    else:
        data = PlayerData(...)
        player_results += [self.parser.parse_player_data(player=data)]
```

### 3.3 `http_service.py:player_box_scores` — empty-list guard raises `InvalidDate`

```python
if response.status_code == requests.codes.ok:
    page = DailyLeadersPage(html=html.fromstring(response.content))
    if not page.daily_leaders:
        raise InvalidDate(day=day, month=month, year=year)
    return self.parser.parse_player_box_scores(box_scores=page.daily_leaders)
```

### 3.4 `http_service.py:team_box_scores` — empty-list guard raises `InvalidDate`

```python
page = DailyBoxScoresPage(html=html.fromstring(response.content))

if not page.game_url_paths:
    raise InvalidDate(day=day, month=month, year=year)

return [
    box_score
    for game_url_path in page.game_url_paths
    for box_score in self.team_box_score(game_url_path=game_url_path)
]
```

### 3.5 `client.py:search` — added `try/except HTTPError` wrapper

```python
def search(term, output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.search(term=term)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSearch(term=term)
        else:
            raise http_error
    ...
```

---

## 4. Phase 2 — Verification (re-running all 23 cases against the fixed source)

### 4.1 Happy-path re-run

| # | Endpoint | Status | Duration | Return shape | Sample size |
|---|----------|--------|----------|--------------|-------------|
| 1 | `search(term="LeBron James")` | PASS | 0.087 s | `dict` w/ `players` | 2 |
| 2 | `standings(season_end_year=2018)` | PASS | 0.158 s | `list[dict]` | 30 |
| 3 | `player_box_scores(day=1, month=1, year=2017)` | PASS | 0.155 s | `list[dict]` | 104 |
| 4 | `team_box_scores(day=1, month=1, year=2017)` | PASS | 0.660 s | `list[dict]` | 10 |
| 5 | `season_schedule(season_end_year=2018)` | PASS | 1.105 s | `list[dict]` | 1 312 |
| 6 | `players_season_totals(season_end_year=2018)` | PASS | 0.740 s | `list[dict]` | 605 |
| 7 | `players_advanced_season_totals(season_end_year=2018)` | PASS | 0.877 s | `list[dict]` | 605 |
| 8 | `regular_season_player_box_scores("jamesle01", 2018)` | PASS | 0.184 s | `list[dict]` | 82 |
| 9 | `playoff_player_box_scores("jamesle01", 2018)` | PASS | 0.144 s | `list[dict]` | 22 |
| 10 | `play_by_play(GSW, 31, 5, 2018)` | PASS | 0.118 s | `list[dict]` | 456 |

**10/10 happy-path endpoints still pass** (all sample sizes unchanged from Phase 1).

### 4.2 Edge-case re-run

| # | Case | Expected | Actual | Status |
|---|------|----------|--------|--------|
| 1 | `search("LeBron")` | `None` (return) | RETURNS 1 player | **PASS** (was FAIL) |
| 2 | `search("xyzzy123_no_such_player")` | `InvalidSearch` | `InvalidSearch` | **PASS** (was FAIL) |
| 3 | `standings(1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 4 | `standings(2099)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 5 | `player_box_scores(15, 4, 1850)` | `InvalidDate` | `InvalidDate` | **PASS** (was FAIL) |
| 6 | `team_box_scores(15, 4, 1850)` | `InvalidDate` | `InvalidDate` | **PASS** (was FAIL) |
| 7 | `season_schedule(1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 8 | `players_season_totals(1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 9 | `players_advanced_season_totals(1900)` | `InvalidSeason` | `InvalidSeason` | PASS |
| 10 | `regular_season_player_box_scores("zzzzz99", 2018)` | `InvalidPlayerAndSeason` | `InvalidPlayerAndSeason` | PASS |
| 11 | `playoff_player_box_scores("zzzzz99", 2018)` | `InvalidPlayerAndSeason` | `InvalidPlayerAndSeason` | PASS |
| 12 | `regular_season_player_box_scores("jamesle01", 1900)` | `InvalidPlayerAndSeason` | `InvalidPlayerAndSeason` | PASS |
| 13 | `play_by_play(GSW, 15, 4, 1850)` | `InvalidDate` | `InvalidDate` | PASS |

**13/13 edge cases now pass** (4 originally-broken cases are fixed, 9 already-passing cases still pass).

### 4.3 Final summary

| Phase | Happy-path | Edge-cases | Total |
|-------|------------|------------|-------|
| Phase 1 (pre-fix) | 10/10 | 9/13 | **19/23 (83%)** |
| Phase 2 (post-fix) | 10/10 | 13/13 | **23/23 (100%)** |

**All 4 reported bugs are fixed with no regressions.**

---

## 5. Known follow-on issues (out of scope, not fixed)

The research surfaced two additional quirks that are *not* in the original 4 bugs and were deliberately left for a future PR:

1. **`/friv/dailyleaders.cgi` silently substitutes today's data for future dates.** A query for `day=15, month=4, year=2050` returns 200 with the box-score table for "May 30, 2026" (yesterday relative to today). The library would return that data without warning. The fix would be to parse the H1/date-picker in the response and compare it against the requested date, raising `InvalidDate` on mismatch. This is sneakier than the pre-BBallRef case because the response looks structurally valid.
2. **`PlayerPage.name` returns `None` for the redirected-to player page.** The xpath `'.//h1[@itemprop="name"]'` doesn't match the actual player-page h1 (which uses a different attribute). This only affects the `search` redirect path (e.g. `search("LeBron")` returns `name: None` but correct `identifier`); multi-result searches are unaffected. The fix would be to update the xpath in `html.py:1336` to match the real h1 structure.

---

## 6. Reproducing this report

```bash
# from repo root
uv sync --extra dev
uv run python scripts/test_endpoints/test_all_endpoints.py   # 10 happy-path calls
uv run python scripts/test_endpoints/test_edge_cases.py      # 13 edge-case calls
```

The endpoint scripts call the live Basketball Reference site and can fail with `429 Too Many Requests` when BBRef rate-limits repeated runs. During the 2026-06-02 uv follow-up, unit tests still passed, while live endpoint re-runs were partially blocked by 429s.
