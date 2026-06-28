---
sessionID: ses_0f4a0d8a6ffeV9oKd3fBsd75GR
baseMessageCount: 0
updatedAt: 2026-06-27T23:25:37.534Z
version: 1.0
date_created: 2026-06-27
owner: agent
tags: [spec, diagnostic]
---

# Courtside Data — Player Hub Server Specification

> **Subject:** `courtside_data/server` — the optional FastAPI "Player Hub" API server bundled with `courtside-data` (installed via the `[server]` extra).

# Introduction

This specification documents `courtside_data/server` — the optional FastAPI "Player Hub" API server bundled with `courtside-data`. It serves a player-centric browsing surface that aggregates multiple basketball-reference datasets behind a small REST API consumed by the Courtside Data UI.

The spec is **hybrid**: it captures the server's current state faithfully and explicitly flags known limitations as planned gaps. It is written primarily for **AI agents that will extend the server** — adding endpoints, datasets, or transport modes — so it is precise about contracts, conventions, and the wiring steps required to register a new dataset.

---

## 1. Purpose & Scope

**Purpose.** Provide a stable, machine-readable reference for the Player Hub server: its HTTP contract, its two transport modes (fixture replay vs. live scraping), its dataset/tab catalog, and the conventions an agent must follow to extend it without breaking existing routes or tests.

**Intended audience.**

- **Primary:** AI coding agents and contributors adding datasets, endpoints, or transport behavior.
- **Secondary:** maintainers reasoning about the server's architecture.
- **Tertiary:** frontend/UI developers consuming the REST API (covered via the Data Contracts section).

**In scope.**

- All seven modules under `courtside_data/server/` (`__init__`, `app`, `catalog`, `cli`, `fixtures`, `models`, `service`).
- The seven HTTP routes and their request/response contracts.
- The fixture-replay transport and the live transport.
- The dataset/tab catalog and column-metadata derivation.
- The `courtside-data serve` CLI subcommand and `[server]` extra.
- The single test module `tests/server/test_player_hub_api.py`.

**Out of scope.**

- The scraping/parsing core (`courtside_data/http`, `courtside_data/parsing`, `courtside_data/schemas`) — referenced only as dependencies.
- The endpoint CLI subcommands other than `serve`.
- The mkdocs site and `docs/` content (the server is currently undocumented there).
- Any production deployment topology (see deployment model below).

**Deployment model (assumption).** Local-dev / single-user only. The server is expected to run via `courtside-data serve` bound to `127.0.0.1:8765` to back the local UI. There is **no auth, no TLS, no multi-tenancy, and no horizontal-scalability requirement**. Non-local deployment is a future concern explicitly called out as a gap, not a current requirement.

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Player Hub** | The server package and the UI surface it backs; aggregates per-player datasets into one API. |
| **Transport mode** | How the server obtains upstream HTML: `"fixture"` (replay from local `raw/` files) or `"live"` (real HTTP via `curl-cffi`). |
| **Fixture** | A raw HTML file captured from basketball-reference, stored under `<repo>/raw/`, replayed by `FixtureTransport` to avoid network calls. |
| **Dataset** | A named, cataloged aggregation of rows from one endpoint (e.g. `career`, `splits`, `on-off`). Identified by a stable `id`. |
| **Tab** | A UI grouping of one or more datasets (e.g. `playoffs`, `shooting`). Defined in `catalog.TABS`. |
| **Dataset scope** | Either `"player"` (param is `player_identifier` only) or `"season"` (params include `season_end_year`). |
| **`EndpointSpec`** | The registry entry in `courtside_data.endpoints.ENDPOINTS` that defines one scraping endpoint, its row model, and param validation. |
| **`CourtsideClient`** | The high-level client in `courtside_data.client` the service layer calls to run endpoints. |
| **`raw/`** | Repo-local directory of captured HTML fixtures; resolved by `fixtures.default_raw_root()`. |
| **`TransportMode`** | `Literal["fixture", "live"]` defined in `models.py`. |
| **429 jail** | A persisted rate-limit state (`RateLimitJailed`) the live transport honors; fixture transport never triggers it. |

---

## 3. Requirements, Constraints & Guidelines

### 3.1 Functional requirements

- **REQ-001**: The server MUST expose seven GET routes (listed in §4) and return JSON conforming to the Pydantic models in `models.py`.
- **REQ-002**: The server MUST support two transport modes — `fixture` (default) and `live` — selected at app construction time via `create_app(transport=...)` or the `COURTSIDE_SERVER_TRANSPORT` env var.
- **REQ-003**: Catalog endpoints MUST be derivable from the `courtside_data.endpoints.ENDPOINTS` registry; no dataset may reference an endpoint not present in that registry.
- **REQ-004**: Player-scoped datasets MUST be fetchable via `/api/players/{id}/{dataset}`; season-scoped datasets MUST be fetchable via `/api/players/{id}/seasons/{year}/{dataset}`. A season-scoped request to a player-scoped dataset (and vice versa) MUST be rejected with 400.
- **REQ-005**: Player search MUST require `term` of length ≥ 2 and return a list of `PlayerSearchResult`; an empty result list is a valid (non-error) response.
- **REQ-006**: CSV export MUST stream a `text/csv` response with `Content-Disposition: attachment` and MUST NOT write any file to disk.
- **REQ-007**: The `/api/status` route MUST report the active transport, endpoint count, fixture root path, and whether that root exists.

### 3.2 Security constraints

- **SEC-001**: The server binds to `127.0.0.1` by default and is intended for single-user local use. There is no authentication or authorization layer.
- **SEC-002**: CORS is restricted to GET methods and four hard-coded localhost origins (`localhost:3000`, `127.0.0.1:3000`, `localhost:3001`, `127.0.0.1:3001`). `allow_credentials` is `False`.
- **SEC-003**: The server MUST NOT execute filesystem writes in response to any route (CSV export is streamed, not persisted).
- **SEC-004**: In live mode, the server MUST honor the upstream 429 rate-limit jail state (`RateLimitJailed`) and surface it as HTTP 429 rather than retrying indefinitely.

### 3.3 System constraints / technologies

- **CON-001**: Python 3.12+ (matches the repo floor).
- **CON-002**: `fastapi>=0.115.0` and `uvicorn[standard]>=0.30.0` are required, declared under `[project.optional-dependencies].server` and re-declared in the PEP 735 `dev` group.
- **CON-003**: HTTP layer uses `httpx` for the fixture transport (`httpx.BaseTransport`) and the project's `HTTPService`/`CourtsideClient` for live requests.
- **CON-004**: Response models use Pydantic v2 `BaseModel`; FastAPI handles validation and OpenAPI generation.
- **CON-005**: `uvicorn` is imported lazily inside `serve()`; the CLI raises a `RuntimeError` with install instructions if the `[server]` extra is absent.
- **CON-006**: The server imports only from `courtside_data.client`, `courtside_data.endpoints`, and `courtside_data.errors` — never from `schemas` or `parsing` directly.
- **CON-007**: Module-level `app = app_from_env()` exists so `uvicorn courtside_data.server.app:app` works without a factory.

### 3.4 Guidelines

- **GUD-001**: When adding a dataset, wire it in exactly the places enumerated in §7 (catalog `DATASETS`, a tab in `TABS`, fixture mapping in `fixtures.py`, scope-appropriate route handling). Missing any step is the most common extension bug.
- **GUD-002**: New response models MUST live in `models.py` and reuse `ColumnMeta` / `EndpointRowsResponse` shapes where possible; do not duplicate row-serialization logic.
- **GUD-003**: Runtime server code (`courtside_data/server/*.py`) MUST NOT import the `tests` package — enforced by a static guard test.
- **GUD-004**: Prefer extending the catalog over adding bespoke routes. If a new route is unavoidable, declare its OpenAPI error responses (400/404/429/500) as `ApiError`.
- **GUD-005**: All server tests MUST opt into network via `pytest.mark.enable_socket` (project default is `--disable-socket`) because `fastapi.testclient.TestClient` opens an in-process socket.

---

## 4. Interfaces & Data Contracts

### 4.1 HTTP routes (all in `app.py`, all GET)

| Route | Handler | Query / Path params | Response model | Error codes |
|-------|---------|--------------------|----------------|-------------|
| `/api/status` | `status` | none | `StatusResponse` | 500 |
| `/api/endpoints/player-hub` | `catalog` | none | `dict[str, object]` (catalog envelope) | 500 |
| `/api/players/search` | `player_search` | `term: str` (min length 2) | `list[PlayerSearchResult]` | 400, 500 |
| `/api/players/{player_identifier}/summary` | `player_summary` | path `player_identifier` | `PlayerHubSummary` | 404, 429, 500 |
| `/api/players/{player_identifier}/export` | `export_dataset` | path `player_identifier`; query `dataset`, `season_end_year?`, `include_inactive_games?` | `Response` (`text/csv`, attachment) | 400, 404, 429, 500 |
| `/api/players/{player_identifier}/seasons/{season_end_year}/{dataset}` | `season_dataset` | path `player_identifier`, `season_end_year: int`, `dataset` | `EndpointRowsResponse` | 400, 404, 429, 500 |
| `/api/players/{player_identifier}/{dataset}` | `player_dataset` | path `player_identifier`, `dataset` | `EndpointRowsResponse` | 400, 404, 429, 500 |

All error responses use the `ApiError` model: `{ code: str, message: str, detail: dict[str, Any] }`.

### 4.2 Pydantic models (`models.py`)

```python
TransportMode = Literal["fixture", "live"]
DatasetScope   = Literal["player", "season"]

class ApiError(BaseModel):              # code, message, detail
class ColumnMeta(BaseModel):            # key, label, default_visible=True, numeric=False
class PlayerSearchResult(BaseModel):    # name, identifier, leagues: list[str]
class PlayerHubTab(BaseModel):          # id, label, description, scope, datasets, default_dataset
class DatasetCatalogEntry(BaseModel):   # id, label, endpoint_name, scope, description,
                                        # columns: list[ColumnMeta],
                                        # default_visible_columns: list[str], supports_export=True
class EndpointRowsResponse(BaseModel):  # dataset, endpoint_name, params, row_count,
                                        # columns, default_visible_columns, rows, transport
class PlayerHubSummary(BaseModel):      # identifier, display_name, leagues, default_season,
                                        # available_seasons, hero_stats, career: EndpointRowsResponse,
                                        # season_dataset_availability, transport
class StatusResponse(BaseModel):        # ok, transport, endpoint_count, fixture_root, fixture_root_exists
```

### 4.3 Exception → HTTP mapping (`app._map_exception`)

| Domain exception (`courtside_data.errors`) | HTTP status | `code` |
|---------------------------------------------|-----------|--------|
| `InvalidSearch` | 400 | `invalid_search` |
| `InvalidPlayer` | 404 | `invalid_player` |
| `InvalidPlayerAndSeason` | 404 | `invalid_player_and_season` |
| `InvalidSeason` | 404 | `invalid_season` |
| `SchemaDriftError` | 500 | `schema_drift` |
| `RateLimitJailed` | 429 | `rate_limit_jailed` |
| Any other `Exception` | 500 | `internal_error` |

### 4.4 Service-layer contract (`service.PlayerHubService`)

```python
class PlayerHubService:
    def __init__(self, *, transport: TransportMode = "fixture", raw_root: Path | None = None)
    def rows_for_dataset(self, dataset_id: str, params: dict[str, object]) -> EndpointRowsResponse
    def search_players(self, term: str) -> list[PlayerSearchResult]
    def summary(self, player_identifier: str) -> PlayerHubSummary
    def csv_for_dataset(self, dataset_id: str, params: dict[str, object]) -> str
```

`PlayerHubService` is injected into routes via `ServiceDep = Annotated[PlayerHubService, Depends(_service_from_app)]`. The dependency reads the service off `request.app.state`, which `create_app()` populates.

### 4.5 Dataset catalog (`catalog.DATASETS`)

13 datasets, each mapping to one `EndpointSpec`:

| dataset id | endpoint_name | scope |
|------------|---------------|-------|
| `career` | `player_career_stats` | player |
| `playoff-series` | `player_playoff_series` | player |
| `adjusted-shooting` | `player_adjusted_shooting` | player |
| `derived-play-by-play` | `player_play_by_play` | player |
| `game-highs` | `player_game_highs` | player |
| `all-star` | `player_all_star` | player |
| `similarity` | `player_similarity_scores` | player |
| `salaries` | `player_salaries` | player |
| `splits` | `player_splits` | season |
| `on-off` | `player_on_off` | season |
| `shooting-breakdown` | `player_shot_charts` | season |
| `regular-games` | `regular_season_player_box_scores` | season |
| `playoff-games` | `playoff_player_box_scores` | season |

8 tabs in `catalog.TABS`: `overview`, `career`, `playoffs`, `shooting`, `splits`, `on-off`, `games`, `more`.

### 4.6 Transport selection contract

- `create_app(*, transport="fixture", raw_root=None)` constructs the app and stores a `PlayerHubService` on `app.state`.
- `app_from_env()` reads `COURTSIDE_SERVER_TRANSPORT` (default `"fixture"`) and `COURTSIDE_DATA_FIXTURE_ROOT` (default `<repo>/raw`) and delegates to `create_app`.
- In fixture mode, `fixtures.build_fixture_service(...)` wires a `FixtureTransport` into an `HTTPService`; in live mode, the standard `HTTPService`/`CourtsideClient` path is used.

---

## 5. Acceptance Criteria

- **AC-001**: Given the server started in fixture mode, when a client GETs `/api/status`, then the response body has `ok=true`, `transport="fixture"`, `endpoint_count` equal to `len(ENDPOINTS)`, and `fixture_root_exists` reflecting the local `raw/` directory.
- **AC-002**: Given a search term of length < 2, when a client GETs `/api/players/search?term=a`, then the server responds 400 with an `ApiError` whose `code="invalid_search"`.
- **AC-003**: Given a term that matches no players, when a client GETs `/api/players/search?term=zzzzz`, then the server responds 200 with an empty list `[]` (not an error).
- **AC-004**: Given a fixture-backed player identifier, when a client GETs `/api/players/{id}/summary`, then the response is a `PlayerHubSummary` with a non-empty `career` rows block, a derived `default_season`, and `transport="fixture"`.
- **AC-005**: Given any player-scoped dataset id (8 total), when a client GETs `/api/players/{id}/{dataset}`, then the response is an `EndpointRowsResponse` with `row_count` and `columns` populated.
- **AC-006**: Given a season-scoped dataset id, when a client GETs the player-scoped route `/api/players/{id}/{dataset}`, then the server responds 400 with `code="invalid_search"` (scope mismatch).
- **AC-007**: Given a season-scoped dataset with a valid fixture, when a client GETs `/api/players/{id}/seasons/{year}/{dataset}`, then the response is an `EndpointRowsResponse`.
- **AC-008**: Given a season-scoped dataset whose fixture file is missing, when a client GETs its season route, then the server responds 404.
- **AC-009**: Given any dataset, when a client GETs `/api/players/{id}/export?dataset=...`, then the response has `Content-Type: text/csv`, a `Content-Disposition: attachment` header, and no file is written to disk.
- **AC-010**: Given an unhandled `Exception` raised in a route, when `_map_exception` runs, then the client receives 500 with `code="internal_error"`.
- **AC-011**: Given a `RateLimitJailed` raised in live mode, when any dataset route is called, then the client receives 429 with `code="rate_limit_jailed"`.
- **AC-012**: Given the source tree, when the static guard test runs, then no file under `courtside_data/server/*.py` imports the `tests` package.

---

## 6. Test Automation Strategy

**Framework.** pytest with `fastapi.testclient.TestClient`, offline-fixture-replay philosophy (consistent with the rest of the repo's blocked-network default).

**Test location.** `tests/server/test_player_hub_api.py` (the only server test module). Note: `tests/server/` has no `__init__.py` today.

**Network handling.** Project `addopts` set `--disable-socket`. Every server test marks `pytestmark = pytest.mark.enable_socket` because `TestClient` opens an in-process ASGI socket — not because tests hit the internet. No real network calls occur in fixture mode.

**Parallelism.** Server tests participate in `pytest -n auto` like the rest of the suite.

**Existing coverage (8 test functions).**

1. `test_status_reports_fixture_mode` — AC-001.
2. `test_player_search_returns_json_objects_and_no_results_state` — AC-002, AC-003.
3. `test_player_summary_derives_season_and_embeds_career_rows` — AC-004.
4. `test_player_scoped_datasets_load_for_fixture_player` — AC-005 across all 8 player-scoped datasets.
5. `test_season_scoped_datasets_load_and_missing_fixture_maps_to_404` — AC-007, AC-008.
6. `test_csv_export_streams_rows_without_filesystem_output` — AC-009.
7. `test_season_dataset_rejects_player_scoped_dataset` — AC-006.
8. `test_server_runtime_code_does_not_import_tests_package` — AC-012 (static import guard).

**Mocking approach.** No mocking framework. Fixture mode itself is the test double: `FixtureTransport` replays captured HTML from `<repo>/raw`, so the service layer runs end-to-end against deterministic inputs. Live-mode paths (real HTTP, 429 jail) are **not** currently tested — see planned gaps.

**Adding tests for new datasets.** Append cases to `test_player_scoped_datasets_load_for_fixture_player` or `test_season_scoped_datasets_load_and_missing_fixture_maps_to_404` using the fixture player identifier already in use. Capture the corresponding HTML into `raw/` first.

---

## 7. Rationale & Context

### 7.1 Architectural decisions

**Why an *optional* extra.** The server depends on `fastapi` + `uvicorn`, which are heavier than the scraping core. Keeping them in `[project.optional-dependencies].server` lets the library stay lean for users who only want the CLI/SDK. The CLI imports `courtside_data.server.cli` lazily inside the `serve` branch so a missing extra never breaks other subcommands.

**Why fixture mode is the default.** The repo's whole test philosophy is offline fixture replay. Defaulting `create_app()` and `COURTSIDE_SERVER_TRANSPORT` to `fixture` means local development and CI exercise deterministic HTML, never hit basketball-reference, and never risk 429 jailing. Live mode is an opt-in for ad-hoc exploration.

**Why a service layer + FastAPI dependency injection.** `PlayerHubService` centralizes dataset→endpoint resolution, row serialization, season derivation, and hero-stat extraction. Routes stay thin. `ServiceDep` makes the service injectable, so tests construct `create_app(transport="fixture")` and get a fully wired service without monkeypatching globals.

**Why columns are derived from the registry.** `catalog.columns_for_dataset` reads `endpoint.row_model.model_fields` from the `EndpointSpec`, so adding fields to a `BRRow` subclass automatically flows into catalog metadata. `NUMERIC_HINTS` heuristically flags numeric columns for UI alignment.

### 7.2 How to add a dataset (extension contract)

An agent adding dataset `X` backed by endpoint `player_X` must touch, in order:

1. **`catalog.py`** — add a `PlayerHubDataset(id="X", endpoint_name="player_X", scope=...)` entry to `DATASETS`.
2. **`catalog.py`** — attach the dataset id to the appropriate `PlayerHubTab` in `TABS` (or add a tab).
3. **`fixtures.py`** — register the endpoint in `PLAYER_ONLY_ENDPOINTS` or `PLAYER_SEASON_ENDPOINTS`, and ensure `_player_only_map` / `_player_season_map` can resolve the fixture path under `raw/`.
4. **`fixtures.py`** — if the endpoint URL shape is non-standard, extend `_render_url`.
5. **`raw/`** — capture the fixture HTML file(s) for the test player.
6. **`tests/server/test_player_hub_api.py`** — add the new dataset id to the appropriate parametrized load test.
7. **`service.py`** — only if the dataset needs custom hero/summary logic; otherwise `rows_for_dataset` handles it generically.

Missing step 3 is the most common failure (the route 404s in fixture mode because the transport cannot find a fixture path).

---

## 8. Dependencies & External Integrations

- **EXT-001 (internal): `courtside_data.endpoints.ENDPOINTS`.** The registry of `EndpointSpec` objects. The catalog derives dataset→endpoint mappings and column metadata from it; the service resolves endpoint names through it. Adding a dataset that references an unknown endpoint name is a hard error.
- **EXT-002 (internal): `courtside_data.client.CourtsideClient`.** The service layer's live-mode entry point for running endpoints. In fixture mode, the service instead builds a `HTTPService` wired to `FixtureTransport` via `fixtures.build_fixture_service`.
- **EXT-003 (internal): `courtside_data.errors`.** Supplies the domain exceptions (`InvalidSearch`, `InvalidPlayer`, `InvalidPlayerAndSeason`, `InvalidSeason`, `RateLimitJailed`, `SchemaDriftError`) that `app._map_exception` translates to HTTP.
- **EXT-004 (internal): `courtside_data.http._constants.BASE_URL` and `courtside_data.http.HTTPService`.** Used by the fixture transport to render and replay URLs.
- **EXT-005 (external): `fastapi>=0.115.0`.** App construction, routing, dependency injection, Pydantic validation, OpenAPI.
- **EXT-006 (external): `uvicorn[standard]>=0.30.0`.** ASGI server, launched by `serve()` via `uvicorn.run("courtside_data.server.app:app", ...)`.
- **EXT-007 (external): `httpx`.** `FixtureTransport` subclasses `httpx.BaseTransport` and returns `httpx.Response` objects so the existing `HTTPService` consumes fixture data transparently.
- **EXT-008 (external): `pydantic` v2.** All response/request models.
- **EXT-009 (upstream, implicit): basketball-reference.com.** Live transport's eventual source of truth. Not a direct code dependency; reached only when `transport="live"`. Subject to the project's 429 rate-limit jail.

---

## 9. Examples & Edge Cases

### 9.1 Starting the server (fixture mode, default)

```bash
uv sync --group dev                 # installs fastapi + uvicorn via the dev group
uv run courtside-data serve         # 127.0.0.1:8765, transport=fixture, raw=<repo>/raw
```

### 9.2 Live mode with a custom fixture root

```bash
COURTSIDE_SERVER_TRANSPORT=live \
COURTSIDE_DATA_FIXTURE_ROOT=/tmp/raw \
uv run courtside-data serve --host 127.0.0.1 --port 9000 --reload
```

### 9.3 Example `/api/status` response (fixture mode)

```json
{
  "ok": true,
  "transport": "fixture",
  "endpoint_count": 55,
  "fixture_root": "/path/to/courtside-data/raw",
  "fixture_root_exists": true
}
```

### 9.4 Example `ApiError` (scope mismatch)

```json
{
  "code": "invalid_search",
  "message": "Dataset 'splits' is season-scoped and cannot be requested without a season",
  "detail": {"dataset": "splits", "scope": "season"}
}
```

### 9.5 Edge cases an agent must handle

- **Search term shorter than 2 chars** → 400 `invalid_search` (FastAPI `min_length=2`).
- **Search term matching nobody** → 200 `[]`, not an error.
- **Player-scoped dataset requested on the season route (or vice versa)** → 400.
- **Missing fixture file in fixture mode** → 404 (`MissingFixtureError` mapped to `invalid_player`/`invalid_player_and_season`).
- **Live mode tripping the 429 jail** → 429 `rate_limit_jailed`; the jail state persists across restarts via `BASKETBALL_REF_JAIL_STATE_PATH`.
- **`SchemaDriftError`** during parsing → 500 `schema_drift`.
- **Player not in `PLAYER_DISPLAY_NAMES`** → `summary.display_name` may fall back to a slug (see planned gaps).

---

## 10. Validation Criteria

Beyond the acceptance tests in §5, the following checks gate correctness:

- **VAL-001 (lint):** `uv run ruff check courtside_data/server` is clean under the repo's rule set (E, W, F, I, UP, B, PT, ASYNC, C4, SIM, PIE, RSE, RET, ISC, FLY, FURB, RUF, ERA).
- **VAL-002 (types):** `uv run ty check courtside_data/server` is clean.
- **VAL-003 (tests):** `uv run pytest tests/server -n auto` passes; the wider `uv run pytest tests -n auto` continues to pass.
- **VAL-004 (full gate):** `uv run task audit` (lint + format check + type + test) is green.
- **VAL-005 (import guard):** The static test `test_server_runtime_code_does_not_import_tests_package` passes — server modules must not depend on test code.
- **VAL-006 (transport parity):** Any new dataset must resolve in **both** transports via the same `PlayerHubService.rows_for_dataset` code path; fixture-only or live-only datasets are not permitted.
- **VAL-007 (catalog exhaustiveness):** Every dataset id referenced by `TABS[].datasets` and by `PlayerHubTab.default_dataset` must exist as a key in `DATASETS`.
- **VAL-008 (no disk writes):** CSV export must produce no side-effect files; verify by asserting the export route leaves the working tree clean.

---

## 11. Related Specifications / Further Reading

- **`courtside_data/endpoints/`** — the `EndpointSpec` registry and per-endpoint param/row-model contracts that the catalog and service depend on.
- **`courtside_data/schemas/`** — the `BRRow` Pydantic subclasses whose `model_fields` drive catalog column metadata.
- **`courtside_data/http/`** — `HTTPService`, `BASE_URL`, and the 429 rate-limit jail consumed by the live transport.
- **`courtside_data/errors.py`** — the domain exception taxonomy mapped to HTTP status codes in §4.3.
- **`AGENTS.md`** (repo root) — tooling, env vars (`BASKETBALL_REF_JAIL_STATE_PATH`, `BASKETBALL_REF_IMPERSONATE`), and the `uv run task audit` gate.
- **`docs/architecture/endpoints.md`** — endpoint architecture (does not yet cover the Player Hub server; a doc page is a candidate future-work item).

### 11.1 Planned gaps (future work, out of current scope)

These limitations are documented for completeness; none is a current requirement under the local-dev/single-user deployment model.

1. **Hardcoded player display names.** `service.PLAYER_DISPLAY_NAMES` is a 17-entry dict. Players outside it may render with a slug as `display_name`. *Future:* derive display names from search/roster data.
2. **Hardcoded CORS origins.** Only the four localhost origins are allowed; no env-driven configuration. *Future:* drive `allow_origins` from an env var before any non-local deployment.
3. **Fixture-only test coverage.** No test exercises `transport="live"`; the 429-jail path, retry classification, and real scraping are untested. *Future:* add a live-mode smoke test gated behind an opt-in marker.
4. **Static dataset catalog.** The 13 datasets and 8 tabs are hard-coded in `catalog.py`; adding one requires the multi-step wiring in §7. *Future:* consider data-driven catalog registration to reduce the touch points.

### 11.2 Candidate future enhancements (not committed)

- Health/readiness route distinct from `/api/status`.
- Pagination on dataset rows.
- A `docs/` page and mkdocstrings rendering for the server package.
- Auth, TLS, and observability if deployment scope ever expands beyond localhost.
