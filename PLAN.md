# Basketball Reference Web Scraper - Expansion Plan (FINALIZED)

## Executive Summary

This plan outlines the expansion of `basketball_reference_web_scraper` from 10 endpoints to 50+ endpoints, covering all major data categories on basketball-reference.com: player statistics, team data, league-wide metrics, draft picks, awards, and historical records.

### Finalized Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Framework** | Stay with `requests` + `lxml` + `pytz` | Scrapy is a poor fit for a client library (reactor lifecycle, import overhead, breaking changes) |
| **HTML Parsing** | Add `parsel` library | CSS selectors + XPath in one API; reduces `html.py` from 1524 lines to ~300 lines |
| **Type Hints** | Add to ALL code (existing + new) | Full type coverage for IDE support, error prevention, documentation |
| **Rate Limiting** | Constructor parameter + env var fallback | Flexible for programmatic use and CI/CD; default 3.5s interval |
| **Testing** | Fixtures only (no live site in CI) | Deterministic, fast, no rate limit concerns during testing |
| **Migration** | Gradual (keep existing Row classes, add new endpoints with GenericTable) | Zero breaking changes; existing code untouched until Phase 5 |
| **Versioning** | No version bump yet | Version will be determined after all changes are complete |
| **Git** | Push to fork only | User's fork; no upstream changes |

**Estimated Effort:** 18-27 days across 6 phases

---

## Framework Decision Analysis

### Current Stack
- **HTTP:** `requests` (synchronous)
- **Parsing:** `lxml` with XPath
- **Timezone:** `pytz`
- **Output:** Custom CSV/JSON writers
- **Type Hints:** None

### Scrapy Analysis (Deep Dive)

After extensive research, Scrapy is a poor fit for this project:

| Issue | Impact | Severity |
|-------|--------|----------|
| **Library vs Framework Conflict** | Scrapy is designed as a CLI framework. Using it as a library requires `CrawlerProcess` which starts Twisted reactor — **not restartable**. Multiple function calls crash. | 🔴 Critical |
| **Import Overhead** | 3 deps → 15+ deps. Install size: ~15MB → ~80MB. Cold import: 0.1s → 1s. | 🟡 High |
| **Breaking Changes** | All 10 existing functions need complete rewrite. Error handling model changes entirely. | 🔴 Critical |
| **Performance Ceiling** | At 20 req/min rate limit, async provides zero benefit. | 🟢 Low |

### Decision Matrix (Weighted)

| Factor (Weight) | A: Current + Abstractions | B: Full Scrapy | C: Parsel Only | D: Hybrid |
|-----------------|---------------------------|----------------|----------------|-----------|
| **Ease of Implementation (30%)** | 9 | 2 | 7 | 7 |
| **Performance (20%)** | 7 | 5 | 7 | 7 |
| **Maintainability (20%)** | 6 | 4 | 8 | 8 |
| **Backward Compatibility (15%)** | 10 | 3 | 9 | 9 |
| **Testing (15%)** | 8 | 3 | 7 | 7 |
| **Weighted Total** | **7.85** | **3.25** | **7.40** | **7.55** |

### Final Decision: Hybrid (requests + Parsel)

**What we're using:**
- `requests` — HTTP transport (unchanged)
- `lxml` — HTML parsing engine (unchanged, Parsel wraps it)
- `parsel` — NEW: CSS + XPath selectors, cleaner API
- `pytz` — Timezone handling (unchanged)

**What we're adding:**
- Generic table parser (replaces 15,000+ lines of boilerplate)
- Commented DOM extractor utility
- Rate limiting in HTTPService
- Connection pooling via `requests.Session()`
- Type hints across entire codebase
- New error classes for better error handling

---

## Architecture Overview

### Current Architecture (10 endpoints)
```
client.py (module-level functions)
    │
    ├──▶ HTTPService._get()  ──▶  requests.get(url)
    │       │
    │       ▼
    │     lxml.html.fromstring(...)
    │       │
    │       ▼
    │     html.py Row/Table classes  (per-endpoint, ~20 properties each)
    │       │
    │       ▼
    │     ParserService  ──▶  parsers.py
    │
    ├──▶ errors.py  (InvalidSeason / InvalidDate / etc.)
    │
    ▼
    OutputService  ──▶  CSVWriter / JSONWriter
```

### Expanded Architecture (50+ endpoints)
```
client.py (module-level functions)
    │
    ├──▶ HTTPService._get()
    │       │
    │       ├──▶ Rate Limiter (configurable, default 3.5s + jitter)
    │       │
    │       ▼
    │     parsel.Selector(text=response.text)
    │       │
    │       ├──▶ extract_commented_table(selector, table_id)  [NEW]
    │       │       │
    │       │       ▼
    │       │     Selector(text=comment_text)
    │       │
    │       ▼
    │     GenericTable / GenericTableRow  [NEW]
    │       │
    │       ▼
    │     ParserService  ──▶  parsers.py (generic parser)
    │
    ├──▶ errors.py  (+ InvalidPlayer, InvalidTeam)
    │
    ▼
    OutputService  ──▶  CSVWriter / JSONWriter
```

### Key New Abstractions

#### 1. Parsel Integration

Replace lxml wrapper classes with Parsel selectors:

```python
from parsel import Selector

# Old way (lxml + wrapper classes)
class PlayerRow:
    @property
    def minutes_played(self):
        cells = self.html.xpath('td[@data-stat="mp"]')
        return cells[0].text_content() if cells else ''

# New way (Parsel)
selector = Selector(text=html_content)
rows = selector.css('table#per_game tbody tr:not(.thead)')
for row in rows:
    minutes = row.css('td[data-stat="mp"]::text').get('')
    player = row.css('td[data-stat="player"] a::text').get('')
```

**Impact:** Reduces `html.py` from 1524 lines to ~300 lines.

#### 2. GenericTable / GenericTableRow

Replaces per-endpoint Row classes for new endpoints:

```python
from typing import Optional
from parsel import Selector

class GenericTableRow:
    """Extracts data from any table row using data-stat attributes."""
    
    def __init__(self, selector: Selector) -> None:
        self._data: dict[str, str] = {}
        for cell in selector.css('td, th'):
            stat: Optional[str] = cell.attrib.get('data-stat')
            if stat:
                self._data[stat] = cell.css('::text').get('').strip().replace('*', '')
    
    def get(self, stat_name: str, default: str = '') -> str:
        return self._data.get(stat_name, default)
    
    def to_dict(self) -> dict[str, str]:
        return self._data.copy()


class GenericTable:
    """Extracts rows from any table, filtering header rows."""
    
    def __init__(self, table_selector: Selector) -> None:
        self.rows: list[GenericTableRow] = []
        for row in table_selector.css('tbody tr:not(.thead)'):
            self.rows.append(GenericTableRow(row))
```

**Impact:** This single class replaces ~15,000 lines of boilerplate Row classes across 40+ endpoints.

#### 3. Commented DOM Extractor

Extracts tables hidden in HTML comments:

```python
from typing import Optional
from parsel import Selector
from lxml import html

def extract_commented_table(selector: Selector, table_id: str) -> Optional[Selector]:
    """
    Finds a table inside HTML comments and returns it as a Selector.
    Basketball-reference wraps some tables in comments to speed up page load.
    """
    for comment in selector.xpath('//comment()').getall():
        if f'id="{table_id}"' in comment or f"id='{table_id}'" in comment:
            # Strip comment tags
            clean_html = comment.replace('<!--', '').replace('-->', '').strip()
            fragment = Selector(text=clean_html)
            table = fragment.css(f'table#{table_id}')
            if table:
                return table[0]
    return None
```

#### 4. Rate Limiter

Added to `HTTPService._get()` with constructor configuration:

```python
import time
import random
import os
from typing import Optional

class HTTPService:
    BASE_URL: str = 'https://www.basketball-reference.com'
    
    def __init__(
        self,
        parser: ParserService,
        rate_limit_interval: Optional[float] = None,
        rate_limit_jitter: Optional[float] = None,
    ) -> None:
        self.parser = parser
        # Constructor param > env var > default
        self._rate_limit_interval: float = (
            rate_limit_interval
            or float(os.environ.get('BASKETBALL_REF_RATE_LIMIT_INTERVAL', '3.5'))
        )
        self._rate_limit_jitter: float = (
            rate_limit_jitter
            or float(os.environ.get('BASKETBALL_REF_RATE_LIMIT_JITTER', '1.2'))
        )
        self._last_request_time: float = 0.0
        self._session: requests.Session = requests.Session()
    
    def _apply_rate_limiting(self) -> None:
        current_time: float = time.time()
        time_since_last: float = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_interval:
            jitter: float = random.uniform(0.0, self._rate_limit_jitter)
            time.sleep((self._rate_limit_interval - time_since_last) + jitter)
        
        self._last_request_time = time.time()
    
    def _get(self, url: str, **kwargs: object) -> requests.Response:
        self._apply_rate_limiting()
        return self._session.get(url=url, **kwargs)
```

**Configuration Options:**
1. **Constructor parameter** (programmatic): `HTTPService(parser=p, rate_limit_interval=3.5)`
2. **Environment variable** (CI/CD): `BASKETBALL_REF_RATE_LIMIT_INTERVAL=3.5`
3. **Default** (fallback): 3.5 seconds

---

## Endpoint Implementation Plan

### Phase 0: Infrastructure (1-2 days)

**Goal:** Build shared abstractions that unlock all subsequent phases.

| Task | Description | Files Modified |
|------|-------------|----------------|
| 0.1 | Add `parsel` to `pyproject.toml` dependencies | `pyproject.toml` |
| 0.2 | Add `GenericTable` and `GenericTableRow` to `html.py` | `html.py` |
| 0.3 | Add `extract_commented_table()` utility to `html.py` | `html.py` |
| 0.4 | Add rate limiting with constructor config to `HTTPService` | `http_service.py` |
| 0.5 | Add connection pooling via `requests.Session()` | `http_service.py` |
| 0.6 | Add `InvalidPlayer` and `InvalidTeam` error classes | `errors.py` |
| 0.7 | Add generic parser method to `ParserService` | `parser_service.py` |
| 0.8 | Add type hints to all existing modules | All `.py` files |

**Validation:** Write unit tests for `GenericTable`, `extract_commented_table()`, and rate limiter.

---

### Phase 1: League-Level Endpoints (3-5 days)

**Goal:** Add 11 league-wide statistics endpoints.

These share the simplest pattern: single URL, single table, no multi-page aggregation.

| # | Endpoint | URL Pattern | Table ID | DOM Type | Priority |
|---|----------|-------------|----------|----------|----------|
| 1 | Per Game (League-wide) | `/leagues/NBA_{year}_per_game.html` | `per_game_stats` | Standard | High |
| 2 | Per 36 Minutes | `/leagues/NBA_{year}_per_minute.html` | `per_minute_stats` | Standard | High |
| 3 | Per 100 Possessions | `/leagues/NBA_{year}_per_poss.html` | `per_poss_stats` | Commented | High |
| 4 | Shooting by Distance | `/leagues/NBA_{year}_shooting.html` | `shooting_stats` | Commented | Medium |
| 5 | League Totals | `/leagues/NBA_{year}_totals.html` | `totals_stats` | Standard | High |
| 6 | Rookie Stats | `/leagues/NBA_{year}_rookies.html` | `rookies` | Standard | Medium |
| 7 | Playoff Player Per Game | `/leagues/NBA_{year}_per_game.html` | `playoffs_per_game` | Commented | Medium |
| 8 | Playoff Player Totals | `/leagues/NBA_{year}_totals.html` | `playoffs_totals` | Commented | Medium |
| 9 | Standings by Date | `/leagues/NBA_{year}_standings_by_date.html` | `standings` | Standard | Medium |
| 10 | Attendance | `/leagues/NBA_{year}_attendance.html` | `attendance` | Standard | Low |
| 11 | League Transactions | `/leagues/NBA_{year}_transactions.html` | `transactions` | Standard | Low |

**Implementation Pattern:**
```python
from typing import Optional

def league_per_game_stats(
    season_end_year: int,
    output_type: Optional[str] = None,
    output_file_path: Optional[str] = None,
    output_write_option: Optional[str] = None,
    json_options: Optional[dict] = None,
) -> list[dict[str, str]]:
    http_service: HTTPService = HTTPService(parser=ParserService())
    values: list[dict[str, str]] = http_service.league_per_game_stats(
        season_end_year=season_end_year
    )
    # ... output handling ...
    return values
```

---

### Phase 2: Draft & Awards (2-3 days)

**Goal:** Add 5 draft, awards, and historical endpoints.

| # | Endpoint | URL Pattern | Table ID | DOM Type | Priority |
|---|----------|-------------|----------|----------|----------|
| 12 | Draft Picks | `/draft/NBA_{year}.html` | `stats` | Standard | High |
| 13 | Season Leaders | `/leaders/per_season.html` | `leaders` | Standard | Medium |
| 14 | Career Leaders | `/leaders/` | `leaders` | Standard | Medium |
| 15 | Playoff Bracket | `/playoffs/NBA_{year}.html` | `bracket` | Standard | Medium |
| 16 | Season Awards | `/awards/awards_{year}.html` | `awards` | Standard | Low |

---

### Phase 3: Player Data Endpoints (5-7 days)

**Goal:** Add 11 player-specific endpoints.

These are more complex because they fetch from player pages where multiple tables coexist.

| # | Endpoint | URL Pattern | Table ID | DOM Type | Priority |
|---|----------|-------------|----------|----------|----------|
| 17 | Career Stats | `/players/{initial}/{player_id}.html` | `per_game` | Standard | High |
| 18 | Playoff Series | `/players/{initial}/{player_id}.html` | `playoffs_per_game` | Standard | Medium |
| 19 | Adjusted Shooting | `/players/{initial}/{player_id}.html` | `adj_shooting` | Commented | Medium |
| 20 | Play-by-Play Stats | `/players/{initial}/{player_id}.html` | `pbp` | Commented | Medium |
| 21 | Game Highs | `/players/{initial}/{player_id}.html` | `highs_totals` | Commented | Medium |
| 22 | All-Star Game | `/players/{initial}/{player_id}.html` | `all_star_g_stats` | Commented | Low |
| 23 | Similarity Scores | `/players/{initial}/{player_id}.html` | `sim_career` | Commented | Low |
| 24 | Salaries | `/players/{initial}/{player_id}.html` | `salaries` | Commented | High |
| 25 | Splits | `/players/{player_id}/splits/{year}` | `splits` | Standard | Medium |
| 26 | On/Off Court | `/players/{player_id}/on-off/{year}` | `on-off` | Standard | Medium |
| 27 | Shot Charts | `/players/{player_id}/shooting/{year}` | `shot_charts` | Standard | Medium |

**Note:** Player pages contain 10+ tables. Use `extract_commented_table(selector, table_id)` to target specific tables.

---

### Phase 4: Team Data Endpoints (5-7 days)

**Goal:** Add 13 team-specific endpoints.

Most diverse group with the most varied URL patterns.

| # | Endpoint | URL Pattern | Table ID | DOM Type | Priority |
|---|----------|-------------|----------|----------|----------|
| 28 | Roster | `/teams/{team}/{year}.html` | `roster` | Standard | High |
| 29 | Injury Report | `/teams/{team}/{year}.html` | `injuries` | Standard | Medium |
| 30 | Team & Opponent | `/teams/{team}/{year}.html` | `team_and_opponent` | Commented | Medium |
| 31 | Team Misc / Four Factors | `/teams/{team}/{year}.html` | `team_misc` | Commented | Medium |
| 32 | Team Schedule & Results | `/teams/{team}/{year}_games.html` | `games` | Standard | High |
| 33 | Team Transactions | `/teams/{team}/{year}_transactions.html` | `transactions` | Standard | Low |
| 34 | Team Splits | `/teams/{team}/{year}/splits/` | `team_splits` | Standard | Medium |
| 35 | Contracts | `/contracts/{team}.html` | `contracts` | Standard | Medium |
| 36 | Lineups | `/teams/{team}/{year}/lineups/` | `lineups` | Standard | Medium |
| 37 | Starting Lineups | `/teams/{team}/{year}_start.html` | `starting_lineups` | Standard | Medium |
| 38 | On/Off Impact | `/teams/{team}/{year}/on-off/` | `on-off` | Standard | Medium |
| 39 | Opponent Stats | `/teams/{team}/{year}_opp.html` | `opp_stats` | Standard | Low |
| 40 | Franchise History | `/teams/{team}/` | `history` | Standard | Low |

---

### Phase 5: Refactor Existing Endpoints (3-5 days)

**Goal:** Migrate existing 10 endpoints to use GenericTable/Parsel for consistency.

| Task | Description | Files Modified |
|------|-------------|----------------|
| 5.1 | Refactor `html.py` to use Parsel selectors | `html.py` |
| 5.2 | Migrate existing Row classes to GenericTableRow pattern | `html.py` |
| 5.3 | Update existing parsers to use new abstractions | `parsers.py`, `parser_service.py` |
| 5.4 | Ensure all existing tests pass after refactor | `tests/` |

**Note:** This phase does NOT change any public API. All 10 existing functions keep their signatures and return types.

---

### Phase 6: Polish & Documentation (2-3 days)

**Goal:** Documentation, testing, and preparation.

| Task | Description |
|------|-------------|
| 6.1 | Update `output/columns.py` with all new column schemas |
| 6.2 | Integration tests for all 40 new endpoints |
| 6.3 | Update MkDocs documentation with new API reference |
| 6.4 | Update README.md with usage examples |
| 6.5 | Update CHANGELOG.md |

---

## Testing Strategy

### Test Structure

For each endpoint, create:

1. **Fixture file** (`tests/fixtures/{endpoint_name}.html`)
   - Real HTML downloaded from basketball-reference
   - Covers both standard DOM and commented DOM tables
   - Committed to git for reproducibility

2. **Unit test** (`tests/unit/test_{endpoint_name}.py`)
   - Tests `GenericTable` extraction from fixture
   - Tests `extract_commented_table()` for commented DOM endpoints
   - Tests parser output matches expected `list[dict]`

3. **Integration test** (`tests/integration/test_{endpoint_name}.py`)
   - Mocks `requests.get` with fixture HTML
   - Tests full pipeline: client function → HTTPService → ParserService → Output

### Test Pattern

```python
import pytest
from parsel import Selector
from basketball_reference_web_scraper.html import GenericTable

@pytest.fixture
def per_game_html() -> str:
    with open('tests/fixtures/league_per_game.html') as f:
        return f.read()

def test_generic_table_extracts_rows(per_game_html: str) -> None:
    selector: Selector = Selector(text=per_game_html)
    table: Selector = selector.css('table#per_game_stats')[0]
    generic: GenericTable = GenericTable(table)
    
    assert len(generic.rows) > 0
    assert generic.rows[0].get('player') != ''
    assert generic.rows[0].get('g') != ''
```

### Fixture Download Script

```python
# scripts/download_fixtures.py
"""
Downloads HTML fixtures from basketball-reference for offline testing.
Respects rate limiting (3.5s between requests).
"""
import time
import requests
from pathlib import Path

ENDPOINTS = {
    'league_per_game': '/leagues/NBA_2024_per_game.html',
    'league_per_36': '/leagues/NBA_2024_per_minute.html',
    # ... etc
}

def download_fixtures(output_dir: str = 'tests/fixtures') -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for name, path in ENDPOINTS.items():
        url = f'https://www.basketball-reference.com{path}'
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 ...'})
        
        with open(f'{output_dir}/{name}.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f'Downloaded: {name}')
        time.sleep(3.5)  # Rate limiting

if __name__ == '__main__':
    download_fixtures()
```

---

## Rate Limiting Strategy

### Configuration Hierarchy

1. **Constructor parameter** (highest priority):
   ```python
   http_service = HTTPService(parser=ParserService(), rate_limit_interval=5.0)
   ```

2. **Environment variable** (CI/CD):
   ```bash
   export BASKETBALL_REF_RATE_LIMIT_INTERVAL=3.5
   export BASKETBALL_REF_RATE_LIMIT_JITTER=1.2
   ```

3. **Default value** (fallback):
   - `rate_limit_interval`: 3.5 seconds
   - `rate_limit_jitter`: 1.2 seconds

### Exponential Backoff

On HTTP 429 (rate limit exceeded):

```python
def execute_request_with_backoff(
    self,
    url: str,
    max_retries: int = 3,
    **kwargs: object,
) -> requests.Response:
    retry_count: int = 0
    
    while retry_count < max_retries:
        try:
            self._apply_rate_limiting()
            return self._session.get(url=url, **kwargs)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 429:
                retry_count += 1
                if retry_count >= max_retries:
                    raise
                backoff: float = (60.0 * (2.0 ** (retry_count - 1))) + random.uniform(0.0, 5.0)
                time.sleep(backoff)
            else:
                raise
```

---

## Data Model Changes

### New Error Classes

```python
# errors.py

class InvalidPlayer(Exception):
    def __init__(self, player_identifier: str) -> None:
        self.player_identifier = player_identifier
        super().__init__(f"Invalid player: {player_identifier}")

class InvalidTeam(Exception):
    def __init__(self, team_abbreviation: str) -> None:
        self.team_abbreviation = team_abbreviation
        super().__init__(f"Invalid team: {team_abbreviation}")
```

### New Dependencies

Add to `pyproject.toml`:

```toml
dependencies = [
    "lxml>=5.1.0",
    "parsel>=1.8.0",  # NEW: CSS + XPath selectors
    "pytz>=2024.1",
    "requests>=2.31.0",
]
```

### Type Hints Strategy

All modules will receive type hints:

```python
# Example: client.py with full type hints
from typing import Optional

def standings(
    season_end_year: int,
    output_type: Optional[str] = None,
    output_file_path: Optional[str] = None,
    output_write_option: Optional[str] = None,
    json_options: Optional[dict[str, object]] = None,
) -> list[dict[str, object]]:
    """Retrieve NBA standings for a given season."""
    try:
        http_service: HTTPService = HTTPService(parser=ParserService())
        values: list[dict[str, object]] = http_service.standings(
            season_end_year=season_end_year
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    
    options: OutputOptions = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": STANDINGS_COLUMNS_NAMES}
    )
    output_service: OutputService = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)
```

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Basketball-reference changes HTML structure | Medium | High | Parse by `data-stat` not column index; fixture-based tests catch regressions |
| Rate limiting blocks during testing | High | Medium | Fixtures only in CI; rate limiter in HTTPService; batch fixture downloads |
| Commented DOM tables have inconsistent structure | Medium | Medium | Defensive parsing; handle missing tables gracefully |
| `data-stat` attribute names vary across tables | Medium | Medium | Build a `data-stat` → friendly-name mapping per endpoint; validate against fixtures |
| Type hints break existing type checker configs | Low | Medium | Add `py.typed` marker; update mypy config if needed |
| Parsel dependency conflicts | Low | Low | Parsel is lightweight (~50KB), well-maintained by Scrapy team |

---

## Effort Estimate

| Phase | Endpoints | Estimated Days | Cumulative |
|-------|-----------|----------------|------------|
| Phase 0: Infrastructure | 0 | 1-2 | 1-2 |
| Phase 1: League Data | 11 | 3-5 | 4-7 |
| Phase 2: Draft & Awards | 5 | 2-3 | 6-10 |
| Phase 3: Player Data | 11 | 5-7 | 11-17 |
| Phase 4: Team Data | 13 | 5-7 | 16-24 |
| Phase 5: Refactor Existing | 0 | 3-5 | 19-29 |
| Phase 6: Polish | 0 | 2-3 | 21-32 |
| **Total** | **40** | **21-32 days** | |

---

## References

- [Basketball-Reference Scraping Guide](https://nthakkar.github.io/bballref/)
- [basketball_reference_scraper (vishaalagartha)](https://github.com/vishaalagartha/basketball_reference_scraper)
- [Parsel Documentation](https://parsel.readthedocs.io/)
- [Current project codemap](codemap.md)
- [REFERENCE.md](REFERENCE.md) - Full endpoint mapping with XPath selectors
