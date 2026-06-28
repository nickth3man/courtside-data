# Team Hub

The Team Hub is a sibling surface to the Player Hub (`courtside_data.server`).
It exposes 13 team-scoped Basketball Reference datasets behind 6 FastAPI
routes and reuses the same `CourtsideClient` + `CourtsideData` plumbing as
the player hub. The implementation is currently **scaffolding** — the
catalog, service, and routes are wired end-to-end, but two service
methods are `NotImplementedError` stubs pending wiring decisions (see
[Status](#status)).

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
- **`/api/teams/search`** — `TeamHubService.search()` stub. Returns
  `500 internal_error` until the team-search wiring decision is made
  (see [Status](#status)).
- **`/api/teams/{team_identifier}/summary`** —
  `TeamHubService.summary()` stub. Returns `500 internal_error` until
  the team-summary wiring decision is made.
- **`/api/teams/{team_identifier}/{dataset}`** — `team` scope datasets
  only. Returns `400 bad_request` if a `team_season` dataset is
  requested through this route.
- **`/api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}`** —
  `team_season` scope datasets only. Returns `400 bad_request` if a
  `team` scope dataset is requested through this route. The
  `include_inactive_games` query parameter is accepted for forward
  compatibility with future team-box-score endpoints (no current
  endpoint consumes it).
- **`/api/teams/{team_identifier}/export`** — `TeamHubService.csv()`
  stub. Returns `500 internal_error` until the team-CSV wiring
  decision is made.

## Backing endpoint specs

The 13 datasets are mapped 1:1 onto the
`courtside_data.endpoints._teams.TEAM_ENDPOINTS` registry entries. The
`scope` column drives the route split (see [HTTP contract](#http-contract))
and is encoded in `courtside_data.server.team_catalog.TEAM_DATASETS`.

| Dataset id | `endpoint_name` | Scope | Endpoint path template |
|------------|-----------------|-------|------------------------|
| `roster` | `team_roster` | `team` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `contracts` | `team_contracts` | `team` | `/contracts/{team_abbreviation}.html` |
| `transactions` | `team_transactions` | `team` | `/teams/{team_abbreviation}/{season_end_year}_transactions.html` |
| `lineups` | `team_lineups` | `team` | `/teams/{team_abbreviation}/{season_end_year}/lineups/` |
| `starting-lineups` | `team_starting_lineups` | `team` | `/teams/{team_abbreviation}/{season_end_year}_start.html` |
| `on-off` | `team_on_off` | `team` | `/teams/{team_abbreviation}/{season_end_year}/on-off/` |
| `franchise-history` | `franchise_history` | `team` | `/teams/{team_abbreviation}/` |
| `injury-report` | `team_injury_report` | `team` | `/friv/injuries.fcgi` |
| `splits` | `team_splits` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}/splits/` |
| `and-opponent` | `team_and_opponent` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `opponent-stats` | `team_opponent_stats` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `misc-four-factors` | `team_misc_four_factors` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `schedule` | `team_schedule` | `team_season` | `/teams/{team_abbreviation}/{season_end_year}_games.html` |

Most "team" scope endpoints technically require `season_end_year` at the
endpoint level (e.g. `team_roster`, `team_lineups`); they are classified
`team` here because the Team Hub intends to surface them from the
no-season route with a default-season resolution that the service does
not yet implement (see [Status](#status)). The two endpoints that
truly do not require a season are `team_contracts` and
`franchise_history` (their `_team(..., params=("team_abbreviation",))`
declaration in `courtside_data.endpoints._teams` confirms this).

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
`TEAM_SEASON_ENDPOINTS`; `fixture_url_map` recognizes them but raises
`MissingFixtureError` (mapped to HTTP 404 by `_map_exception`) until
the per-endpoint fixture-transport helpers are added. The 6 team
routes therefore return 404 in fixture mode today — this is the
expected behaviour for the scaffolding milestone.

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

After the fixtures are captured, extend
`courtside_data.server.fixtures.fixture_url_map` with two helpers
(`_team_only_map` and `_team_season_map`) that mirror
`_player_only_map` / `_player_season_map`. The whitelists in
`TEAM_ENDPOINTS` and `TEAM_SEASON_ENDPOINTS` are already in place; the
guard at the bottom of `fixture_url_map` will then route the team
endpoints into the new helpers instead of raising
`MissingFixtureError`.

### Per-endpoint capture list

For each of the 13 team endpoints, the table below lists the expected
fixture path layout and the canonical Basketball Reference page(s) to
capture. URLs are relative to `https://www.basketball-reference.com`.

| Dataset id | `endpoint_name` | `scope` | Fixture file (under `raw/`) | Page URL |
|------------|-----------------|---------|----------------------------|----------|
| `roster` | `team_roster` | `team` | `team_roster/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `contracts` | `team_contracts` | `team` | `team_contracts/{team_abbreviation}.html` | `/contracts/{team_abbreviation}.html` |
| `transactions` | `team_transactions` | `team` | `team_transactions/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}_transactions.html` |
| `lineups` | `team_lineups` | `team` | `team_lineups/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}/lineups/` |
| `starting-lineups` | `team_starting_lineups` | `team` | `team_starting_lineups/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}_start.html` |
| `on-off` | `team_on_off` | `team` | `team_on_off/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}/on-off/` |
| `franchise-history` | `franchise_history` | `team` | `franchise_history/{team_abbreviation}.html` | `/teams/{team_abbreviation}/` |
| `injury-report` | `team_injury_report` | `team` | `team_injury_report/{team_abbreviation}_{season_end_year}.html` (or `default.html` / `offseason.html`) | `/friv/injuries.fcgi` (team/season params ignored by the page) |
| `splits` | `team_splits` | `team_season` | `team_splits/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}/splits/` |
| `and-opponent` | `team_and_opponent` | `team_season` | `team_and_opponent/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `opponent-stats` | `team_opponent_stats` | `team_season` | `team_opponent_stats/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` (same page as `and-opponent`) |
| `misc-four-factors` | `team_misc_four_factors` | `team_season` | `team_misc_four_factors/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}.html` |
| `schedule` | `team_schedule` | `team_season` | `team_schedule/{team_abbreviation}_{season_end_year}.html` | `/teams/{team_abbreviation}/{season_end_year}_games.html` |

The `[team]` directory `raw/team_injury_report/` already contains
`default.html` and `offseason.html` fixtures (the page ignores
team/season parameters); the team-hub fixture helper should be
allowed to short-circuit to `default.html` for the injury-report
endpoint, mirroring the `default`-style fallbacks the player hub
uses elsewhere.

<!-- TODO(team-hub): refresh the per-endpoint capture table after the
scope reclassification landed in team_catalog.py.

What: the table above lists 8 datasets at "team" scope and 5 at
"team_season" scope. The current authoritative classification
(after the 6-dataset reclassification in
courtside_data/server/team_catalog.py) is:

  team scope (2):      contracts, franchise-history
  team_season scope (11): roster, transactions, lineups,
                          starting-lineups, on-off, injury-report,
                          splits, and-opponent, opponent-stats,
                          misc-four-factors, schedule

Update the "scope" column of the table to match this authoritative
set, and add a regression test in
tests/test_endpoint_metadata.py that asserts the catalog and
EndpointSpec stay in sync (see the TODO in
courtside_data/server/team_catalog.py for the test design).

Where:
  - courtside_data/server/team_catalog.py:54-163  (the
    authoritative :data:`TEAM_DATASETS` tuple).
  - courtside_data/endpoints/_teams.py  (the 13 EndpointSpec
    declarations; the source of truth for ``params`` and
    therefore scope).
  - tests/test_endpoint_metadata.py  (the cross-validation test
    module).

How:
  1. Edit the table above: change the ``scope`` cell of
     ``roster``, ``transactions``, ``lineups``,
     ``starting-lineups``, ``on-off``, and ``injury-report`` from
     ``team`` to ``team_season``.
  2. Add the parametrized test in
     tests/test_endpoint_metadata.py as described in the
     team_catalog.py TODO.
  3. Verify the doc table matches the catalog by running
     ``uv run python -c "from
     courtside_data.server.team_catalog import TEAM_DATASETS;
     print({d.id: d.scope for d in TEAM_DATASETS})"`` and
     diffing the output against the table.

Decision needed: the doc table is a hand-maintained artifact
today. A future improvement would be to generate it from the
catalog (mkdocstrings / sphinx-style autodoc) so drift is
impossible. The current scaffolding milestone accepts the
hand-maintained form.

Verify: ``uv run pytest tests/test_endpoint_metadata.py -k
  team_hub_scope_invariant -v`` -> all 13 entries pass after the
  test is added.
-->

## Source layout

| File | Purpose |
|------|---------|
| `courtside_data/server/team_models.py` | Pydantic response models (`TeamSearchResult`, `TeamHubTab`, `TeamDatasetCatalogEntry`, `TeamHubCatalog`, `TeamHubSummary`) and `TeamDatasetScope` literal. |
| `courtside_data/server/team_catalog.py` | `TEAM_DATASETS` tuple, `TEAM_TABS` tuple, `TeamDataset` dataclass, `team_hub_catalog()`, and column helpers. |
| `courtside_data/server/team_service.py` | `TeamHubService` (search/summary stubs; `dataset`/`season_dataset` implemented; `csv` stub). |
| `courtside_data/server/app.py` | 6 new team routes + `team_hub_service` app state. Existing player routes untouched. |
| `courtside_data/server/fixtures.py` | `TEAM_ENDPOINTS` and `TEAM_SEASON_ENDPOINTS` whitelists; `fixture_url_map` guard updated. |

## Status

**Scaffolding.** Two service methods are `NotImplementedError` stubs:

1. **`TeamHubService.search(term)`** — `search` EndpointSpec
   (currently used for the player hub) is not known to support team
   search. Decision needed: reuse the existing `search` spec with a
   new `domain` filter, or register a dedicated `team_search` spec.
2. **`TeamHubService.summary(team_identifier)`** — needs the
   `team_roster` embed + hero-stats composition logic. The shape is
   defined in `TeamHubSummary`; the wiring is not.
3. **`TeamHubService.csv(...)`** — needs the team column-order
   contract. The Player Hub's `PlayerHubService.csv_for_dataset`
   is the model to mirror.

Until those three methods are implemented, the corresponding routes
return `500 internal_error` (the `_map_exception` fallback). All
other routes are fully wired and return the expected
`MissingFixtureError` (404) in fixture mode or the live `CourtsideClient`
data in live mode.

<!-- TODO(team-hub): refresh the Status section after the search /
summary / csv methods landed.

What: the Status section above states that all three of
``search()`` / ``summary()`` / ``csv()`` are
``NotImplementedError`` stubs. As of the team-hub
implementation lane that closed out this scaffolding, only
``search()`` is still a stub (it raises ``NotImplementedError``
with a precise TODO citing
``courtside_data/schemas/search.py:50``); ``summary()`` and
``csv()`` are implemented and return data in live mode. The
``/api/teams/{team_identifier}/summary`` and
``/api/teams/{team_identifier}/export`` routes therefore return
the same shape as their player-hub counterparts today, modulo
fixture-mode behavior (the team fixture transport is not yet
wired, so embedded datasets fall back to empty envelopes — see
the TODO in ``courtside_data/server/team_service.py`` on
:meth:`TeamHubService.summary`).

Where:
  - courtside_data/server/team_service.py:287  (the
    :meth:`TeamHubService.search` ``NotImplementedError``).
  - courtside_data/server/team_service.py:383  (the
    :meth:`TeamHubService.summary` implementation).
  - courtside_data/server/team_service.py:519  (the
    :meth:`TeamHubService.csv` implementation).

How:
  1. Move the ``search()`` description into a new
     "still pending" subsection.
  2. Move the ``summary()`` and ``csv()`` items into an
     "implemented" subsection that links to the corresponding
     TODOs for the data-driven refinements (default season,
     ``fixture_seasons_for_team``, hero-stats source, CSV
     column contract).
  3. Add a "fixture mode" subsection that documents the
     graceful-empty fallback behavior and links to the
     team-hub fixture capture TODO in
     ``docs/architecture/team-hub.md`` (this file) and
     ``courtside_data/server/fixtures.py``.

Decision needed: whether to keep this Status section hand-
maintained or to auto-generate it from the service's
``NotImplementedError`` audit (a small pytest plugin could
collect every ``raise NotImplementedError(...)`` in the team
service and produce a status table). The hand-maintained form
is more readable; the auto-generated form is more honest.

Verify: read the team service's :func:`ast` for
``raise NotImplementedError`` and confirm only ``search()``
matches (and the ``else`` branch in :meth:`_build_params`,
which is reachable only for a custom-param team endpoint that
does not yet exist).
-->
