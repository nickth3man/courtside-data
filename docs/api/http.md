# HTTP server

The Player Hub ships an optional FastAPI server that exposes the same
Player Hub data the CLI returns, but over HTTP. The UI talks to it
exclusively; the CLI and library paths remain unchanged.

## Run it

```bash
uv run courtside-data serve
```

Defaults: `127.0.0.1:8765`, transport `fixture`, raw-root
`COURTSIDE_DATA_FIXTURE_ROOT` (or the package default). Override with
`--host`, `--port`, `--transport {fixture,live}`, `--raw-root`, `--reload`.

```bash
uv run courtside-data serve --transport live --port 9000 --reload
```

Transport and root are also honored from the environment via
`app_from_env` (`COURTSIDE_SERVER_TRANSPORT`, `COURTSIDE_DATA_FIXTURE_ROOT`).

## Routes

All routes are `GET`. The CORS middleware only allows the UI origins
(see below), so cross-origin browsers cannot reach this server unless
they impersonate one of them.

| Method | Path | Params | Response model |
|--------|------|--------|----------------|
| GET | `/api/status` | — | `StatusResponse` |
| GET | `/api/endpoints/player-hub` | — | `PlayerHubCatalog` (untyped dict in source) |
| GET | `/api/players/search` | `term: str` (query) | `list[PlayerSearchResult]` |
| GET | `/api/players/{player_identifier}/summary` | `player_identifier: str` (path) | `PlayerHubSummary` |
| GET | `/api/players/{player_identifier}/export` | `player_identifier`, `dataset: str` (required), `season_end_year: int \| None`, `include_inactive_games: bool` | `text/csv` |
| GET | `/api/players/{player_identifier}/seasons/{season_end_year}/{dataset}` | path params + `include_inactive_games: bool` | `EndpointRowsResponse` |
| GET | `/api/players/{player_identifier}/{dataset}` | `player_identifier`, `dataset` (path) | `EndpointRowsResponse` |

The CSV export is the only non-JSON response; everything else is
`application/json` and conforms to the Pydantic models in
`courtside_data/server/models.py`.

## UI side

The UI defaults to `http://127.0.0.1:8765` and reads
`process.env.NEXT_PUBLIC_COURTSIDE_API_URL` first
(`ui/src/lib/api-client.ts`). Set it before `next dev`:

```bash
NEXT_PUBLIC_COURTSIDE_API_URL=http://127.0.0.1:9000 npm run dev
```

A mismatched URL produces `TypedApiError` with `code: "internal_error"`
and `status: 0` (the fetch failed before the server could reply), or
`code: "internal_error"` with a non-zero status if the server replied
with an unmapped exception.

## CORS

Configured in `courtside_data/server/app.py` (`CORSMiddleware`,
`allow_methods=["GET"]`):

| Origin |
|--------|
| `http://localhost:3000` |
| `http://127.0.0.1:3000` |
| `http://localhost:3001` |
| `http://127.0.0.1:3001` |

`allow_credentials=False`; any header is accepted (`allow_headers=["*"]`).
Adding a new dev port means editing the allowlist — the server is
intentionally not a public API.

## Transport modes

The server is constructed with a `TransportMode` of either `"fixture"`
or `"live"`. The mode is selected at startup time and surfaced via
`StatusResponse.transport`.

`fixture` mode reads the parquet/raw JSON written by
`courtside_data.server.fixtures` from the local
`COURTSIDE_DATA_FIXTURE_ROOT` directory. `live` mode hits Basketball
Reference directly through the standard pipeline. Both modes return
identical Pydantic shapes.

`StatusResponse.fixture_root` and `fixture_root_exists` describe the
configured raw fixture directory:

- `fixture` transport: both fields are populated. `fixture_root` is the
  absolute path the server is reading from; `fixture_root_exists` is
  `True` if the directory was found on disk, `False` if not (in which
  case data calls will return `code: "missing_fixture"`).
- `live` transport: both fields are `None` — there is no local fixture
  root to report on.

## Error codes

The FastAPI envelope is `{ detail: { code, message, detail } }`. The UI
narrows `code` to the `ApiErrorCode` union in
`ui/src/lib/api-errors.ts`; anything outside the known set becomes
`"unknown"`. Mapping source of truth:
`courtside_data/server/app.py::_map_exception`.

| Code | HTTP | Origin (server) | Meaning |
|------|------|-----------------|---------|
| `invalid_search` | 400 | `InvalidSearch` | Player search term was empty or malformed. |
| `bad_request` | 400 | `ValueError`, Pydantic `ValidationError` | Generic input validation failure. |
| `invalid_player` | 404 | `InvalidPlayer`, `InvalidPlayerAndSeason` | Player identifier not found in the active dataset. |
| `invalid_season` | 404 | `InvalidSeason` | Season path component is outside the supported range. |
| `missing_fixture` | 404 | `MissingFixtureError` | Fixture mode and the on-disk fixture is not present. |
| `rate_limit_jailed` | 429 | `RateLimitJailed` | Basketball Reference rate-limit cap was hit; `detail.retry_after` carries seconds until the jail lifts. The UI retries once automatically. |
| `schema_drift` | 500 | `SchemaDriftError` | Upstream HTML/table shape changed; Pydantic rejected the rows. The endpoint is broken until the schema migrates. |
| `internal_error` | 500 | any other `Exception` | Unmapped server-side failure. The Python exception type is preserved in `detail.error_type`. |
| `unknown` | any | malformed body | Body did not match the FastAPI envelope; the UI fell back to `"unknown"`. |

`rate_limit_jailed` is the only code the UI retries on: `apiFetch`
honors `Retry-After` (header or `detail.retry_after`) and waits up to
one retry before propagating the error. A second 429, or a 429 with no
finite `Retry-After`, throws immediately.

## OpenAPI

FastAPI exposes the full schema at:

- `GET /openapi.json` — raw OpenAPI 3.x JSON, the input to
  `openapi-typescript` (see `npm run gen:api` and
  `ui/scripts/generate-api-types.ts`).
- `GET /docs` — Swagger UI (FastAPI default).
- `GET /redoc` — ReDoc (FastAPI default).

The UI consumes the generated types from `ui/src/lib/openapi-types.ts`
once the codegen has run; before that the file ships a placeholder
export so imports compile.
