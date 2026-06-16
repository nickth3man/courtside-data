# Offline Test Hardening — PDCA Plan

**Project:** courtside-data (Python 3.12 httpx scraper of basketball-reference.com, ~50 endpoints)
**Goal:** Revamp the broken test configuration and build an offline suite that hardens the scraper against rate limits using the 424 saved HTML fixtures in `/raw`. No live network, no rate-limit risk, no e2e changes.
**PDCA cycle:** 1 (of an expected 2)
**Status:** Wave 1 (foundation) COMPLETE &amp; verified. Wave 2 (test files) PENDING.
**Last updated:** 2026-06-16

---

## Context

`courtside-data` scrapes basketball-reference.com via `httpx` + `httpx-curl-cffi` (TLS impersonation), `hishel` (HTTP cache), `stamina` (retries), `parsel`/`lxml` (parsing), `pydantic` 2.13 (row validation). The legacy test config was broken: the old `requests-mock`-over-`respx` shim (`tests/http_mock.py`) had zero consumers, the ~160 old `m.get(...)` integration tests were gone, and `tests/new/` was empty. The `/raw` corpus holds **424 HTML files across 146 subdirs** captured from the live site. E2e tests (`tests/e2e/`) are live-only and gated by `RUN_LIVE_BASKETBALL_REFERENCE_TESTS=1` — out of scope.

**Research basis:** @oracle (architecture) + 5 parallel [@librarian](#openchamber-agent:librarian) lanes (awesome-pytest, awesome-web-scraping, data-validation, real-world httpx fixture-replay patterns, modern toolchain). Both converged on one architecture; competitor analysis confirmed **no existing basketball-reference Python scraper has a hermetic offline suite** (the 291★ `vishaalagartha/basketball_reference_scraper` hits the live API per assertion; `pybaseball` uses `sleep(6)` between tests = 15+ min suite).

---

## Architecture decision (the winning design)

A custom **`FixtureTransport(httpx.BaseTransport)`** maps `request.url` → on-disk HTML file in `/raw`, injected via `HTTPService(session=…)` and bound through the existing `_service_override` ContextVar (now first-class via a new `CourtsideClient(service=…)` param). This stubs exactly ONE line (`self._session.get` in `http_service.py:393`) while leaving every parser, the selector cache, table extraction, row-model validation, and error mapper fully exercised — maximum realism, zero network, zero coupling to respx or curl-cffi.

A **declarative fixture manifest** (`tests/new/fixture_manifest.py`) is the single source of truth for both URL→file mapping and pytest parametrization. Assertions are **tiered**: Tier 1 (every endpoint) pydantic validation as schema-drift canary + structural checks; Tier 2 (curated) golden deep-equality via `deepdiff`. Error/retry paths use respx; rate-limit/jail logic uses injected `time_func`/`sleep`/`random_func`.

---

## Research-grounded tool decisions

### ADOPT (9)
1. `pytest-randomly` — catch `HTTPService` ClassVar order-dependence (the #1 risk); CI verification pass, not default addopts.
2. `deepdiff` — readable Tier-2 golden failures (`DeepDiff(golden, actual, ignore_order=True, …)` instead of useless `assert ==` dumps).
3. `selectolax` (test-only) — second-parser oracle (Lexbor vs production lxml) to catch selector drift pydantic can&#x27;t.
4. `pytest-cov` + `covdefaults` — make the xdist coverage swap actually work; branch coverage + sane excludes.
5. `diff-cover` — gate PR coverage on changed lines (`--fail-under=80` vs `origin/main`).
6. Canonical `stamina.set_testing(True, attempts=3)` session autouse fixture (matches `_RETRY_ATTEMPTS=3`).
7. Ruff `PT` + `ASYNC` rule families; `tests/**` per-file-ignores `[&quot;E501&quot;,&quot;W291&quot;,&quot;S101&quot;,&quot;B011&quot;]`.
8. CI: `astral-sh/setup-uv` with `enable-cache: true`, pinned uv version.
9. Commit JSON Schema contract per endpoint via pydantic `model_json_schema()`; enrich `SchemaDriftError` with `ValidationInfo.field_name`.

### DEFER (2)
- D1 `pandera` — range/distribution drift on ~10-15 numeric endpoints only. Revisit after core suite lands.
- D2 `hypothesis` — property-based tests of `_fields.py` cell-coercion validators. Bonus, orthogonal.

### REJECTED
`pytest-httpx`, `pytest-recording`, `vcrpy`, `responses`, `requests-mock`, `pook`, `mitmproxy`, `pytest-httpserver` (wrong transport / too heavy); Great Expectations, Soda, Frictionless (paradigm wrong); `pytest-clarity`, `snapshottest`, `pytest-blockage`, `pytest-approvaltests` (unmaintained); `extruct`/`trafilatura` (wrong domain); second type checker alongside `ty` (beta, production-ready); `time-machine`/`freezegun` (none in use); `parametrize-from-file` (directory-tree convention wins per Lane 4).

---

## Phase 1 — PLAN

### Problem
Test config old and broken; no offline coverage of the 50 endpoints; any test run risks basketball-reference rate-limit IP bans.

### Current state (baseline)
- `tests/new/` empty; `tests/http_mock.py` dead (0 importers).
- E2e suite live-only, must stay serial, ~31 requests cap.
- `--disable-socket` + `impersonate=None` patch already in `tests/conftest.py` (good backstop).

### Root causes
- requests→httpx migration left the `http_mock.py` shim with no callers.
- curl-cffi&#x27;s `CurlTransport` is incompatible with respx (asserts `&quot;timeout&quot; in req.extensions`).
- `HTTPService` carries 4 `ClassVar` mutable fields (`_last_request_time`, `_jailed_until`, `_jail_state_loaded`, `_rate_limit_lock`) — cross-test leakage risk.
- `CourtsideClient` had no clean service-injection seam (only the private `_service_override` ContextVar).
- No drift canary: silent breakage when basketball-reference changes markup.

### Hypothesis
**If** we replay `/raw` via a custom `httpx.BaseTransport` (bypassing respx/curl-cffi) and use pydantic validation + a second-parser oracle as the drift canary, **then** the scraper becomes fully testable offline with zero rate-limit risk and high drift-detection confidence.

### Success criteria (measurable)
- [ ] ≥ 95% of registered endpoints have ≥1 offline case (Wave 1: 53/55 = 96% ✓).
- [ ] Full offline suite runs in &lt; 30s, parallel-safe (`-n auto`), no socket access.
- [ ] `pytest-randomly --randomly-seed=last` passes (proves no ClassVar order-coupling).
- [ ] `ruff check` + `ty check` clean under new PT/ASYNC rules.
- [ ] Tier-1 canary fires `SchemaDriftError` when a fixture is intentionally corrupted.
- [ ] Competitor parity: only BR scraper with a hermetic offline suite.

---

## Phase 2 — DO

### Wave 1 — Foundation (COMPLETE)

| # | File | Owner | Result |
|---|------|-------|--------|
| 1 | `pyproject.toml` | fix-config | +6 dev deps (pytest-randomly, deepdiff, selectolax, pytest-cov, covdefaults, diff-cover); removed pytest-freezer + `-p no:freezegun`; ruff select += PT,ASYNC; `tests/**` ignores += S101,B011; new `[tool.coverage.run]` (covdefaults, branch, relative_files, source=courtside_data, omit legacy/*). |
| 2 | `courtside_data/client/courtside_client.py` | fix-inject | Added keyword-only `service: HTTPService \| None = None`; when set, used as `self._service` (cache/headers/impersonate/timeout ignored). Default behavior byte-for-byte preserved. |
| 3 | `tests/new/__init__.py`, `tests/new/fixture_transport.py` | fix-transport | `FixtureTransport(httpx.BaseTransport)`; `FixtureValue = Path \| tuple[int,dict\|None]`; `build_client`, `build_service`. URL match: exact → strip-query → path-only. Missing → loud `FileNotFoundError` listing available keys. Content-Type by extension; tuple = error injection. |
| 4 | `tests/new/fixture_manifest.py` | fix-manifest | **217 cases**, `Case(endpoint_name, params, url_to_file, id)`; `ALL_CASES`, `GENERIC_CASES` (205), `ERROR_CASES` (3), `MULTI_REQUEST_ENDPOINTS` (5), `UNRESOLVED_ENDPOINTS` (2); `transport_map()`, `case_for()`. CWD-independent `RAW_ROOT`; `sorted()` everywhere (xdist-safe). |
| 5 | `tests/new/test_retry_logic.py`, `tests/new/test_rate_limit_and_jail.py` | fix-unit-tests | 37 tests (28 + 9); self-contained module-level stamina + ClassVar-reset autouse fixtures; injected `time_func`/`sleep`/`random_func` for pacing/jail; fake `_FakeSession` for 429→`RateLimitJailed`. |

### Wave 2 — Test files (PENDING)

**Wave 2a (parallel):**
- `fix-conftest` — `tests/new/conftest.py` (session autouse `stamina_testing`; function autouse ClassVar reset; `make_offline_client(case)-&gt;CourtsideClient` factory) + **edit the two Wave-1 unit-test files to remove their now-redundant module-level fixtures** (conftest owns them; avoids the stamina-teardown-disables-other-modules hazard).
- `fix-parser-oracle` — `tests/new/test_parser_oracle.py` (selectolax-vs-parsel selector agreement; independent of conftest — direct file reads).

**Wave 2b (parallel, after 2a — needs real conftest fixture API):**
- `fix-endpoint-tests` — `tests/new/test_endpoint_offline.py` (Tier-1 parametrized over `GENERIC_CASES`: call client fn, assert non-empty list of validated models, no raise = drift canary), `tests/new/test_manifest_coverage.py` (meta-test: every `ENDPOINTS` key covered or in `UNRESOLVED`), `tests/new/test_golden_outputs.py` (minimal auto-generate-on-first-run for a curated few).
- `fix-error-tests` — `tests/new/test_error_mapping.py` (`ERROR_CASES` 404 → domain exceptions; 429 tuple → `RateLimitJailed`).

### Deferred (later cycle)
- D1 `pandera` numeric drift; D2 `hypothesis` field-coercion; golden corpus expansion; CI wiring (`setup-uv`, `diff-cover`, randomly pass, xdist coverage job).

---

## Phase 3 — CHECK

### Wave 1 results vs success criteria
- Endpoint coverage: **53/55 = 96%** ✓ (target ≥95%).
- Offline unit tests: **37 passed in ~3s** ✓, under `--disable-socket`.
- `ruff check` + `ty check`: clean on all 4 new modules ✓.
- Manifest determinism: `sorted()` throughout; xdist-safe ✓.
- Transport loud-failure: missing URL → descriptive `FileNotFoundError` ✓.
- Injection API: default path byte-for-byte equivalent ✓.

### What worked
- The `FixtureTransport` design sidesteps the curl-cffi/respx incompatibility entirely (curl-cffi never enters the call path).
- Declarative manifest as single source of truth for both URL mapping and parametrization — clean.
- Self-contained unit tests (injected fakes) gave fast, hermetic retry/jail coverage with zero transport coupling.

### What failed / required adjustment
- **fix-4 (manifest, attempt 1) returned an empty result and wrote NO file.** Root cause: scope too large for one shot (424 files + multi-request href parsing). **Adjustment:** re-scoped to prioritize robust generic-endpoint coverage with best-effort multi-request and a loud `UNRESOLVED_ENDPOINTS` list; re-dispatched as fix-6 → succeeded (217 cases). **Lesson (→ ACT):** time-box complex discovery tasks; partial + loud-gaps beats over-scoped failure.
- **`Retry-After: &quot;1000&quot;`** returns `False` (not `60.0`) — the jail-threshold check (`&gt;300`) fires before the cap. Tests pinned to actual code behavior; documented.

### Known gaps (Wave 2 inputs)
- 2 endpoints unresolved: `friv_7_game_playoff_series_outcomes_team_is_tied` and `_team_is_up` — **no `/raw` fixture dirs exist** (only `_team_is_down`). Action: download fixtures or xfail.
- Stamina teardown hazard: Wave-1 unit-test module fixtures call `set_testing(False)` at module teardown, which would disable stamina testing for later modules. **Wave 2a conftest must own the stamina fixture** and the unit-test files must drop theirs.

---

## Phase 4 — ACT

### Standardize (Wave 1 — lock in)
- Established APIs (see Appendix) are now the contract for Wave 2 and future tests.
- `CourtsideClient(service=…)` is the supported injection seam; do NOT poke `_service_override` directly in new tests.
- Every new test module under `tests/new/` gets the autouse stamina + ClassVar reset from `tests/new/conftest.py` (once landed) — do not re-declare them.

### Adjust for Wave 2 (carried from CHECK)
- Wave 2a first: land conftest + strip the redundant unit-test fixtures before adding tests that depend on them.
- Respect the dependency: `fix-endpoint-tests` / `fix-error-tests` wait for the real conftest fixture API (do not parallelize against an unresolved contract).
- Keep zero write-overlap between parallel fixers (partition by file).

### Next cycle (Cycle 2)
1. Land Wave 2 (conftest + 4 test files).
2. Final verification: `uv run pytest tests/new -q` all green; `--randomly-seed=last` green; `ruff`/`ty` clean; corrupt one fixture and confirm `SchemaDriftError` fires.
3. CI wiring: `setup-uv` cache, xdist coverage job (`pytest --cov`), `diff-cover --fail-under=80`, nightly `--randomly-seed=last` determinism job.
4. Re-evaluate deferred D1/D2; expand golden corpus; resolve the 2 missing `friv_7_game` fixtures.

### Completion gate
Cycle 1 PDCA closes when the full `tests/new/` suite is green, parallel-safe, drift-detecting, and CI-wired. Monitor for 2 weeks; start Cycle 2 only if drift/coverage gaps surface.

---

## Appendix A — Established APIs (Wave 1 contract)

```python
# courtside_data.client.courtside_client.CourtsideClient
CourtsideClient(*, cache=True, headers=None, impersonate=&quot;chrome124&quot;,
                timeout=None, service: HTTPService | None = None)
# service= injects a pre-built HTTPService (e.g. fixture-wired); other kwargs ignored.

# tests.new.fixture_transport
FixtureValue = Path | tuple[int, dict[str, str] | None]
class FixtureTransport(httpx.BaseTransport):
    def __init__(self, url_to_path: dict[str, FixtureValue]) -&gt; None: ...
    def handle_request(self, request: httpx.Request) -&gt; httpx.Response: ...  # loud FileNotFoundError if missing
def build_client(transport, *, follow_redirects=True) -&gt; httpx.Client
def build_service(transport) -&gt; HTTPService

# tests.new.fixture_manifest
@dataclass(frozen=True, slots=True)
class Case:
    endpoint_name: str
    params: dict
    url_to_file: dict[str, FixtureValue]
    id: str
ALL_CASES: list[Case]            # 217
GENERIC_CASES: list[Case]        # 205 (ALL minus multi-request)
ERROR_CASES: list[Case]          # 3 (404 injection)
MULTI_REQUEST_ENDPOINTS: frozenset[str]   # {play_by_play, search, season_schedule, standings_by_date, team_box_scores}
UNRESOLVED_ENDPOINTS: list[str]  # 2 (friv_7_game_*_tied / _up)
def transport_map(endpoint_name, **params) -&gt; dict[str, FixtureValue]
def case_for(endpoint_name, **params) -&gt; Case | None
