# Team Hub

The Team Hub is a sibling surface to the Player Hub (`courtside_data.server`).
It exposes 13 team-scoped Basketball Reference datasets behind 6 FastAPI
routes and reuses the same `CourtsideClient` + `CourtsideData` plumbing as
the player hub. The catalog, service, fixture transport, and routes are
wired end-to-end for the current 13 team datasets.

## HTTP contract

All routes return JSON unless noted. Error responses use the same
`ApiError` shape (`{"code", "message", "detail"}`) and HTTP status codes
as the player hub.

| Method | Path | Response |
|--------|------|----------|
| `GET` | `/api/endpoints/team-hub` | `dict[str, object]` (static catalog: `tabs` + `datasets`) |
| `GET` | `/api/teams/search?term=…` | `list[TeamSearchResult]` |
| `GET` | `/api/teams/{team_identifier}/summary` | `TeamHubSummary` |
| `GET` | `/api/teams/{team_identifier}/{dataset}` | `EndpointRowsResponse` (scope = `team`) |
| `GET` | `/api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}?include_inactive_games=bool` | `EndpointRowsResponse` (scope = `team_season`) |
| `GET` | `/api/teams/{team_identifier}/export?dataset=…&season_end_year=…&include_inactive_games=…` | CSV `Response` |

### Route semantics

- **`/api/endpoints/team-hub`** — returns the static catalog payload
  (5 tabs, 13 dataset entries). Implemented by
  `courtside_data.server.team_catalog.team_hub_catalog()`. Same return
  shape as `/api/endpoints/player-hub`.
- **`/api/teams/search`** — reuses the Basketball-Reference search
  endpoint and filters parsed cards to team results.
- **`/api/teams/{team_identifier}/summary`** —
  builds display name, default season, available seasons, hero stats,
  roster rows, per-dataset season availability, and franchise arc.
- **`/api/teams/{team_identifier}/{dataset}`** — `team` scope datasets
  only. Returns `400 bad_request` if a `team_season` dataset is
  requested through this route.
- **`/api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}`** —
  `team_season` scope datasets only. Returns `400 bad_request` if a
  `team` scope dataset is requested through this route. The
  `include_inactive_games` query parameter is accepted for forward
  compatibility with future team-box-score endpoints (no current
  endpoint consumes it).
- **`/api/teams/{team_identifier}/export`** — serializes the requested
  team dataset to CSV using the endpoint's declared `csv_columns`
  when present.

## Backing endpoint specs

The 13 datasets are mapped 1:1 onto the
`courtside_data.endpoints._teams.TEAM_ENDPOINTS` registry entries. The
`scope` column drives the route split (see [HTTP contract](#http-contract))
and is encoded in `courtside_data.server.team_catalog.TEAM_DATASETS`.

| Dataset id | `endpoint_name` | Scope | Endpoint path template |
|------------|-----------------|-------|------------------------|
| `roster` | `team_roster` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `contracts` | `team_contracts` | `team` | `/contracts/{team_abbreviation}.html` |
| `transactions` | `team_transactions` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}_transactions.html` |
| `lineups` | `team_lineups` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}/lineups/` |
| `starting-lineups` | `team_starting_lineups` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}_start.html` |
| `on-off` | `team_on_off` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}/on-off/` |
| `franchise-history` | `franchise_history` | `team` | `/teams/{team_abbreviation}/` |
| `injury-report` | `team_injury_report` | `team_season` | `/friv/injuries.fcgi` |
| `splits` | `team_splits` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}/splits/` |
| `and-opponent` | `team_and_opponent` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `opponent-stats` | `team_opponent_stats` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `misc-four-factors` | `team_misc_four_factors` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `schedule` | `team_schedule` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}_games.html` |

The two `team` scope datasets do not require `season_end_year`.
Every endpoint whose `EndpointSpec.params` includes `season_end_year`
is classified as `team_season`; the invariant is tested in
`tests/test_endpoint_metadata.py`.

## Transport modes

The Team Hub supports the same two transports as the Player Hub,
selected by the `COURTSIDE_SERVER_TRANSPORT` env var (default:
`fixture`).

### Live mode (`COURTSIDE_SERVER_TRANSPORT=live`)

All 13 team endpoints work today via `CourtsideClient` (rate-limited,
TLS-impersonated, optionally cached). No fixture HTML is required.

### Fixture mode (`COURTSIDE_SERVER_TRANSPORT=fixture`)

The 13 team endpoint names are whitelisted in
`courtside_data.server.fixtures.TEAM_ENDPOINTS` and
`TEAM_SEASON_ENDPOINTS`. `fixture_url_map` maps team-only requests to
`raw/{endpoint_name}/{team_abbreviation}.html` and team-season requests
to `raw/{endpoint_name}/{team_abbreviation}_{season_end_year}.html`.
`team_injury_report` short-circuits to `raw/team_injury_report/default.html`
or `offseason.html` because Basketball Reference ignores team and
season params for that page.

## Fixture HTML needed

To enable fixture mode for the Team Hub, capture one or more
representative pages per endpoint under `raw/` (the project root
directory; see `courtside_data.server.fixtures.default_raw_root()`).
The naming convention mirrors the player hub:

- **team-only** endpoints (`team_contracts`, `franchise_history`):
  one HTML per team identifier, named
  `raw/{endpoint_name}/{team_abbreviation}.html`.
- **team-season** endpoints (and the "team" scope endpoints that
  embed a season): one HTML per `(team_abbreviation, season_end_year)`
  pair, named `raw/{endpoint_name}/{team_abbreviation}_{season_end_year}.html`.

Missing fixture files raise `MissingFixtureError`, which the API maps
to a `404 missing_fixture` error. Captured fixture seasons are surfaced
by `fixture_seasons_for_team()` and used by `TeamHubService.summary()`
for default-season and per-dataset availability.

### Per-endpoint capture list

For each of the 13 team endpoints, the table below lists the expected
fixture path layout and the canonical Basketball Reference page(s) to
capture. URLs are relative to `https://www.basketball-reference.com`.

| Dataset id | `endpoint_name` | `scope` | Fixture file (under `raw/`) | Page URL |
|------------|-----------------|---------|----------------------------|----------|
| `roster` | `team_roster` | `team_season` | `team_roster/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `contracts` | `team_contracts` | `team` | `team_contracts/{team_abbreviation}.html` | `/contracts/{team_abbreviation}.html` |
| `transactions` | `team_transactions` | `team_season` | `team_transactions/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}_transactions.html` |
| `lineups` | `team_lineups` | `team_season` | `team_lineups/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}/lineups/` |
| `starting-lineups` | `team_starting_lineups` | `team_season` | `team_starting_lineups/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}_start.html` |
| `on-off` | `team_on_off` | `team_season` | `team_on_off/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}/on-off/` |
| `franchise-history` | `franchise_history` | `team` | `franchise_history/{team_abbreviation}.html` | `/teams/{team_abbreviation}/` |
| `injury-report` | `team_injury_report` | `team_season` | `team_injury_report/default.html` (or `offseason.html`) | `/friv/injuries.fcgi` (team/season params ignored by the page) |
| `splits` | `team_splits` | `team_season` | `team_splits/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}/splits/` |
| `and-opponent` | `team_and_opponent` | `team_season` | `team_and_opponent/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `opponent-stats` | `team_opponent_stats` | `team_season` | `team_opponent_stats/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` (same page as `and-opponent`) |
| `misc-four-factors` | `team_misc_four_factors` | `team_season` | `team_misc_four_factors/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `schedule` | `team_schedule` | `team_season` | `team_schedule/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}_games.html` |

The `[team]` directory `raw/team_injury_report/` already contains
`default.html` and `offseason.html` fixtures (the page ignores
team/season parameters); the team-hub fixture helper short-circuits
to `default.html` before falling back to `offseason.html`.

## Source layout

| File | Purpose |
|------|---------|
| `courtside_data/server/team_models.py` | Pydantic response models (`TeamSearchResult`, `TeamHubTab`, `TeamDatasetCatalogEntry`, `TeamHubCatalog`, `TeamHubSummary`) and `TeamDatasetScope` literal. |
| `courtside_data/server/team_catalog.py` | `TEAM_DATASETS` tuple, `TEAM_TABS` tuple, `TeamDataset` dataclass, `team_hub_catalog()`, and column helpers. |
| `courtside_data/server/team_service.py` | `TeamHubService` search, summary, dataset, season-dataset, and CSV orchestration. |
| `courtside_data/server/app.py` | 6 new team routes + `team_hub_service` app state. Existing player routes untouched. |
| `courtside_data/server/fixtures.py` | `TEAM_ENDPOINTS` and `TEAM_SEASON_ENDPOINTS` whitelists, team fixture URL maps, and fixture-season discovery. |

## Status

**Implemented for the current Team Hub surface.** The six Team Hub
routes are registered and the service methods return typed responses.
Fixture mode is backed by the checked-in `raw/team_*` and
`raw/franchise_history` files where present; missing files produce the
same `404 missing_fixture` envelope used by the Player Hub.

The only `NotImplementedError` in `TeamHubService` is the defensive
unknown-parameter branch in `_build_params()`. It is reached only if a
future team endpoint declares a new parameter name without adding the
public kwarg mapping.
