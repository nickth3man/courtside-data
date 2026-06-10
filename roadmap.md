# Roadmap: From Fork to Independent Project

## Why This Exists

This project started as a fork of [jaebradley/basketball_reference_web_scraper](https://github.com/jaebradley/basketball_reference_web_scraper). The original project is MIT-licensed and hasn't been actively maintained. This fork has grown significantly — from 10 endpoints to ~50, with new tooling, rate limiting, generic table parsing, and expanded test infrastructure.

The goal of this roadmap is to earn independent project status: a codebase that stands on its own, credits its origins, and offers enough new value that unforking on GitHub is clearly justified.

**Current state (as of Phase 1 completion):**
- Repo unforked and renamed to **Courtside Data** (`nickth3man/courtside-data`)
- ~44 commits ahead of upstream
- Runtime code grew 63% (3,483 → 5,667 lines)
- 80% of public endpoints are new (40 of ~50)
- Architecture is still mostly upstream's pattern
- LICENSE, pyproject.toml, and README updated with new identity and attribution
- Courtesy issue opened upstream ([#325](https://github.com/jaebradley/basketball_reference_web_scraper/issues/325))

---

## Phase 1: Identity & Attribution

**Goal:** The project presents itself honestly as a derived work with its own identity.

**Why first:** Everything else is cosmetic until the project has a name, a voice, and proper credit.

| #   | Task                                                                 | Priority | Effort | Status |
| --- | -------------------------------------------------------------------- | -------- | ------ | ------ |
| 1.1 | Choose a new project/package name                                     | High     | —      | ✅ Done — `courtside-data` |
| 1.2 | Update `pyproject.toml`: name, author, maintainer, URLs               | High     | 1h     | ✅ Done |
| 1.3 | Rewrite `README.md` in your own voice                                 | High     | 3-4h   | ✅ Done |
| 1.4 | Add "Lineage and Attribution" section to README (see template below) | High     | 30m    | ✅ Done |
| 1.5 | Update LICENSE with dual copyright (original + yours)                 | High     | 15m    | ✅ Done |
| 1.6 | Remove/replace upstream badges, logos, PyPI links                     | Medium   | 30m    | ✅ Done (removed in README rewrite) |
| 1.7 | Open a courtesy issue/PR upstream explaining the derivative           | Medium   | 15m    | ✅ Done — [#325](https://github.com/jaebradley/basketball_reference_web_scraper/issues/325) |

**Attribution template for README:**

```markdown
## Lineage and Attribution

This project is derived from
[Jae Bradley's basketball_reference_web_scraper](https://github.com/jaebradley/basketball_reference_web_scraper),
licensed under the [MIT License](LICENSE).

The original project provided the initial package structure, core NBA endpoints,
parsing pipeline, output writers, and test approach. This project is independently
maintained and extends that foundation with ~40 additional endpoints, generic table
parsing, rate limiting, fixture tooling, and updated packaging.

### Original Project Contributors
- [Jae Bradley](https://github.com/jaebradley) (creator)
- [See full list](https://github.com/jaebradley/basketball_reference_web_scraper/graphs/contributors)
```

**License template:**

```
MIT License

Original work:
Copyright (c) 2018 Jae Bradley

Modifications and additional work:
Copyright (c) 2026 [Your Name / GitHub Handle]

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

## Phase 2: Fix What's Broken

**Goal:** The new endpoints actually work and the tests prove it.

**Why now:** 40 new endpoints are the main claim to independence. If 8 of them fail tests and many passing tests only assert `isinstance(result, list)`, the claim is weak.

| #   | Task                                                                    | Priority | Effort | Status |
| --- | ----------------------------------------------------------------------- | -------- | ------ | ------ |
| 2.1 | Fix 8 failing integration tests (`test_new_endpoints.py`)                 | High     | 1-2d   |        |
| 2.2 | Verify table IDs match actual Basketball Reference HTML                 | High     | 1d     |        |
| 2.3 | Replace weak `isinstance(result, list)` assertions with real content checks | High | 1d     |        |
| 2.4 | Add expected output fixtures for representative seasons/players/teams   | High     | 2d     |        |
| 2.5 | Mark unstable/beta endpoints in docstrings and docs                    | Medium   | 2h     |        |
| 2.6 | Add endpoint status table to docs (stable / beta / fixture-covered)    | Medium   | 1h     |        |

**Test strength targets:**

```python
# WEAK (current for some endpoints):
assert isinstance(result, list)

# STRONG (target):
assert len(result) == 30  # 30 teams
assert result[0]["player"] != ""
assert result[0]["pts"] is not None
assert any(row["tm"] == "BOS" for row in result)
```

---

## Phase 3: Stale Documentation Cleanup

**Goal:** Docs reflect reality, not the upstream project's state.

| #   | Task                                                          | Priority | Effort | Status |
| --- | ------------------------------------------------------------- | -------- | ------ | ------ |
| 3.1 | Update `codemap.md` — now ~50 endpoints, not 10                | High     | 1h     |        |
| 3.2 | Update `courtside_data/codemap.md`           | Medium   | 30m    |        |
| 3.3 | Update `output/codemap.md`                                     | Low      | 15m    |        |
| 3.4 | Regenerate `REFERENCE.md` with new endpoint mappings           | Medium   | 1h     |        |
| 3.5 | Update MkDocs `docs/` to include new endpoints                | Medium   | 2h     |        |

---

## Phase 4: Architecture — Endpoint Registry

**Goal:** Replace 50 copy-pasted functions with a declarative endpoint spec.

**Why this matters for independence:** The current code is "upstream's pattern × 50." A registry model is a genuine architectural improvement that makes the project maintainable in a way the original never was.

| #   | Task                                                                   | Priority | Effort | Status |
| --- | ---------------------------------------------------------------------- | -------- | ------ | ------ |
| 4.1 | Define `EndpointSpec` dataclass (name, url_template, table_id, parser, columns, is_commented) | High | 1d | |
| 4.2 | Create `registry.py` with all ~50 endpoint definitions                | High     | 1d     |        |
| 4.3 | Build generic `fetch()` / `parse()` dispatch in client                | High     | 1d     |        |
| 4.4 | Migrate existing 10 endpoints to registry (keep backward compat)      | Medium   | 1d     |        |
| 4.5 | Migrate new 40 endpoints to registry                                  | Medium   | 1d     |        |
| 4.6 | Remove dead code from `http_service.py` and `client.py`                | Medium   | 2h     |        |

**Target pattern:**

```python
@dataclass(frozen=True)
class EndpointSpec:
    name: str
    url_template: str           # e.g. "/leagues/NBA_{season}_per_game.html"
    table_id: str | None        # e.g. "per_game_stats"
    parser: str                 # "generic_table", "standings", "box_score"
    column_names: tuple[str, ...]
    is_commented: bool = False
    cache_ttl: int = 3600

ENDPOINTS: tuple[EndpointSpec, ...] = (
    EndpointSpec("league_per_game", "/leagues/NBA_{season}_per_game.html",
                 "per_game_stats", "generic_table", LEAGUE_PER_GAME_COLUMNS),
    # ... ~50 total, each one line
)

class Client:
    def __init__(self):
        self._http = HTTPService()
        self._registry = {e.name: e for e in ENDPOINTS}

    def fetch(self, endpoint: str, **params) -> list[dict]:
        spec = self._registry[endpoint]
        url = f"{self._http.BASE_URL}{spec.url_template.format(**params)}"
        html = self._http.get(url)
        return self._parse(spec, html)
```

**Reference:** `nba_api` uses a similar `Endpoint` base class pattern. `sportsipy` uses CSS selector dicts in `constants.py`.

---

## Phase 5: Typed Return Models

**Goal:** Users get IDE autocomplete and type safety on return values.

**Why this matters for independence:** Neither `nba_api` nor `sportsreference` offer this. It's a genuine differentiator.

| #   | Task                                                                | Priority | Effort | Status |
| --- | ------------------------------------------------------------------- | -------- | ------ | ------ |
| 5.1 | Define `@dataclass` models for core endpoints (PlayerSeasonTotals, TeamStanding, etc.) | High | 2d | |
| 5.2 | Add `.to_dict()` method on all models for backward compat           | High     | 2h     |        |
| 5.3 | Add `as_dicts: bool = False` parameter to client functions           | High     | 1h     |        |
| 5.4 | Add `py.typed` marker for PEP 561                                   | Medium   | 15m    |        |
| 5.5 | Add type hints to all public API functions                          | Medium   | 1d     |        |
| 5.6 | Add `TypedDict` definitions for dict-based returns                   | Low      | 2h     |        |

**Target pattern:**

```python
from dataclasses import dataclass, asdict
from datetime import date

@dataclass(frozen=True)
class PlayerSeasonTotals:
    player_name: str
    team: str
    games_played: int
    points: int
    assists: int
    rebounds: int
    # ...

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

# Usage:
result = client.fetch("player_season_totals", season=2024, player_id="jamesle01")
result[0].points         # typed, autocompleted
result[0].to_dict()      # backward compat
```

**Reference:** `sportsipy` uses per-stat `@property` with type decorators. `pybaseball` returns `pd.DataFrame` exclusively. The dataclass approach gives users both IDE support and dict compatibility.

---

## Phase 6: HTTP Hardening

**Goal:** One shared session, retry logic, proper timeouts.

| #   | Task                                                          | Priority | Effort | Status |
| --- | ------------------------------------------------------------- | -------- | ------ | ------ |
| 6.1 | Make `HTTPService._session` a class-level singleton             | High     | 2h     |        |
| 6.2 | Add `urllib3.Retry` with exponential backoff (3 retries, 429/5xx) | High  | 2h     |        |
| 6.3 | Add default timeout (30s connect, 60s read)                   | Medium   | 30m    |        |
| 6.4 | Add configurable User-Agent string                            | Medium   | 30m    |        |
| 6.5 | Keep `requests` — do NOT migrate to httpx (not worth it for sync-only) | — | — | |

**Target pattern:**

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class HTTPService:
    _session: requests.Session | None = None

    @classmethod
    def get_session(cls) -> requests.Session:
        if cls._session is None:
            cls._session = requests.Session()
            retry = Retry(total=3, backoff_factor=1,
                          status_forcelist=[429, 500, 502, 503])
            adapter = HTTPAdapter(max_retries=retry)
            cls._session.mount("https://", adapter)
            cls._session.headers.update({"User-Agent": "bbref-client/1.0"})
        return cls._session
```

**Reference:** `nba_api` uses a class-level session singleton. `requests` docs recommend `HTTPAdapter` + `Retry` for production use.

---

## Phase 7: Differentiating Features

**Goal:** Features that make users choose this over `nba_api`, `sportsreference`, or `pybaseball`.

| #   | Feature                                      | Priority | Effort | Impact |
| --- | -------------------------------------------- | -------- | ------ | ------ |
| 7.1 | **Local SQLite cache** with TTL — don't re-scrape static pages | High | 1d | Very high |
| 7.2 | **Pandas integration** — `.to_dataframe()` on results | Medium | 2d | High |
| 7.3 | **Historical batch iterator** — `season_range(2000, 2024)` with rate limiting | Medium | 1d | High |
| 7.4 | **CLI tool** — `bbref players 2024 --format csv` | Low | 2d | Medium |
| 7.5 | **WNBA support** — first-class, not an afterthought | Low | 3-5d | High |

**Cache pattern (from pybaseball):**

```python
import sqlite3
import json
from functools import wraps
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "bbref"

def cached(ttl_seconds: int = 86400):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = f"{fn.__name__}:{args}:{kwargs}"
            db = sqlite3.connect(CACHE_DIR / "cache.db")
            # check if cached + not expired → return cached
            # otherwise call fn, store result, return
        return wrapper
    return decorator
```

**Pandas pattern (from nba_api):**

```python
# On result objects or client:
def to_dataframe(self) -> "pd.DataFrame":
    import pandas as pd
    return pd.DataFrame([r.to_dict() for r in self._results])
```

---

## Phase 8: Testing Modernization

**Goal:** Stronger tests, easier fixture management.

| #   | Task                                                           | Priority | Effort | Status |
| --- | -------------------------------------------------------------- | -------- | ------ | ------ |
| 8.1 | Add `pytest-recording` + `vcrpy` for HTTP cassette recording    | Medium   | 2h     |        |
| 8.2 | Record cassettes for all 50 endpoints (one representative call) | Medium   | 1d     |        |
| 8.3 | Keep existing HTML fixtures as unit test fallbacks              | Low      | —      |        |
| 8.4 | Add CI step: lint (`ruff`), type check (`mypy`), test           | Medium   | 2h     |        |
| 8.5 | Add coverage reporting                                         | Low      | 1h     |        |

**VCRpy workflow:**

```bash
# Record once:
pytest --record-mode=once

# Normal test run (replays from cassettes):
pytest

# Re-record after site changes:
rm tests/cassettes/*.yaml
pytest --record-mode=once
```

---

## Phase 9: Documentation Rewrite

**Goal:** Docs that belong to this project, not the upstream.

| #   | Task                                                          | Priority | Effort | Status |
| --- | ------------------------------------------------------------- | -------- | ------ | ------ |
| 9.1 | Set up `mkdocstrings` for auto-generated API reference         | High     | 2h     |        |
| 9.2 | Write "Getting Started" guide with 5-line example             | High     | 1h     |        |
| 9.3 | Write migration guide (upstream v4 → this project)            | High     | 2h     |        |
| 9.4 | Add Jupyter notebook example (`mkdocs-jupyter`)               | Medium   | 2h     |        |
| 9.5 | Document all endpoints with args, return types, examples      | Medium   | 2d     |        |
| 9.6 | Add "Ethical Scraping" section (rate limits, robots.txt, ToS) | Medium   | 30m    |        |

**Docs structure:**

```
docs/
  index.md                  # landing page + quickstart
  guides/
    getting-started.md      # pip install, first scrape
    migration-v4.md         # what changed from upstream
    caching.md              # how caching works
    pandas.md               # pandas integration
  api/
    client.md               # auto-generated from docstrings
    models.md               # dataclass reference
    errors.md               # exception hierarchy
  examples/
    basic-usage.ipynb       # notebook: scrape + explore
    team-analysis.ipynb     # notebook: pandas workflow
```

---

## Unfork Checklist

All pre-unfork items completed. Repo is now independent as of Phase 1.

- [x] New project name chosen and applied — **courtside-data**
- [x] `pyproject.toml` metadata updated (author, URLs, name)
- [x] README rewritten in your own voice
- [x] Attribution section in README (link to original, "derived from" language)
- [x] LICENSE updated with dual copyright
- [x] Courtesy issue opened upstream — [#325](https://github.com/jaebradley/basketball_reference_web_scraper/issues/325)
- [x] Repo unforked and renamed on GitHub

Remaining items (do before PyPI publish):

- [ ] `codemap.md` updated to reflect current state
- [ ] All 8 failing tests fixed
- [ ] New endpoint table IDs verified against real HTML
- [ ] At least weak→strong test assertions for all 40 new endpoints
- [ ] CI passes (lint + type check + tests)
- [ ] Endpoint registry refactor started (even if not complete)

---

## Priority Summary

| Phase | Focus                        | Priority | Total Effort | Status |
| ----- | ---------------------------- | -------- | ------------ | ------ |
| 1     | Identity & Attribution       | 🔴 High  | 1d           | ✅ Done |
| 2     | Fix Broken Tests             | 🔴 High  | 3-4d         | ⬜ Next |
| 3     | Stale Docs Cleanup           | 🟡 Med   | 0.5d         |        |
| 4     | Endpoint Registry            | 🔴 High  | 4-5d         |        |
| 5     | Typed Return Models          | 🔴 High  | 3-4d         |        |
| 6     | HTTP Hardening               | 🟡 Med   | 0.5d         |        |
| 7     | Differentiating Features     | 🟡 Med   | 4-8d         |        |
| 8     | Testing Modernization        | 🟡 Med   | 2d           |        |
| 9     | Documentation Rewrite        | 🔴 High  | 3-4d         |        |

**Unfork complete (Phase 1).** Repo is now independent.
**Minimum for PyPI publish:** Phases 2 + partial 3 (codemap update).
**To feel truly independent:** Phases 2–6 + 9.
**To be a compelling alternative:** All phases.

---

## References

- [nba_api](https://github.com/swar/nba_api) — endpoint class pattern, session reuse
- [sportsipy](https://github.com/roclark/sportsipy) — dataclass stat models, CSS scheme dicts
- [pybaseball](https://github.com/jjasghar/pybaseball) — pandas-first design, `@df_cache()` decorator
- [VCRpy](https://github.com/kevin1024/vcrpy) — HTTP cassette recording for tests
- [mkdocstrings](https://mkdocstrings.github.io/) — auto-generated API docs from docstrings
- [Original project](https://github.com/jaebradley/basketball_reference_web_scraper) — Jae Bradley's MIT-licensed library
