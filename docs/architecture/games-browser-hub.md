# Games/Browser Hub

The Games/Browser Hub is the **hardest** of the six endpoint domains: it
does not fit the entity-Hub pattern (Player Hub, Team Hub) and instead
spans four different interaction models with very different URL shapes,
UI surfaces, and fixture-capture strategies. This document is the
implementation roadmap; the source-of-truth inventory of all 12
unreachable GAMES-domain endpoints is in §2, the game-identification
problem (the single most important design decision) is in §3, and the
recommended domain boundary (3 of the 12 endpoints should move to
the **League Hub**) is in §9.

> **Status:** Planning only. The catalog stub is in
> `courtside_data/server/games_catalog.py`. No routes, services, or
> fixture HTML exist yet for this domain. The recommended
> implementation order (see
> `docs/architecture/endpoint-roadmap.md` §3) is to ship League Hub,
> Playoffs Hub, and Draft/Awards/Leaders Hub first, then tackle this
> domain.

## 1. Overview

### Why this domain is fundamentally different from entity Hubs

Player Hub and Team Hub both share a "one entity, many datasets" model:

- The user picks **one** anchor entity (a player or a team).
- The Hub exposes a catalog of N datasets (career / splits / on-off /
  shot-charts / etc. for Player; roster / contracts / schedule / etc.
  for Team).
- Each dataset is fetched with the same anchor identifier
  (`/api/players/{player_identifier}/{dataset}` or
  `/api/teams/{team_identifier}/seasons/{year}/{dataset}`).
- The UI is a tabbed viewer; switching tabs is the only navigation.

The GAMES domain has **no such anchor entity**. Its 12 unreachable
endpoints split across four very different interaction models:

1. **Per-game box scores (6 endpoints)** — all share the URL
   `/boxscores/{game_id}.html` and are always fetched together as a
   six-tab box-score viewer (Player Basic, Player Advanced, Quarter
   Splits, Line Score, Four Factors, Game Info). There is no catalog
   of "which box-score datasets exist for a game" — every game
   exposes the same six. See §3 for the game-identification scheme.
2. **Daily leaders (2 endpoints)** — `player_box_scores` and
   `team_box_scores` take `day/month/year` and return every game that
   happened on that date. The natural UI surface is a date picker
   that drives a single daily-leaders call.
3. **Play-by-play (1 endpoint)** — `play_by_play` takes
   `day/month/year/home_team` and returns the event stream for one
   game. Same date-picker entry point as daily leaders; the
   home-team parameter drills into a single game.
4. **League-wide season tables (3 endpoints)** — `season_schedule`,
   `players_season_totals`, `players_advanced_season_totals` take
   `season_end_year` and return league-wide tables. **These
   architecturally belong in the League Hub** (see §9), not in a
   Games Browser — they have no per-game or per-date character.

This split is why the Team Hub catalog pattern (a 13-entry
`TEAM_DATASETS` tuple grouped into 5 tabs in
`courtside_data/server/team_catalog.py`) does not port cleanly: a
games catalog would have to be a 4-way union of incompatible scopes
(game / date / date_team / season), three of which (the season-scoped
ones) are really League Hub content.

### The game-identification challenge (preview)

Every per-game box score is fetched with `game_id` (the only call
param for five of the six; the sixth — `box_score_player_quarter_splits` —
adds a `period` sub-param). The EndpointSpec
(`courtside_data/endpoints/_workflows.py:541-642`) declares
`game_id` as a free-form `str` and uses
`/boxscores/{game_id}.html` as the path template. **The actual
game_id format is the load-bearing design decision for this whole
domain** — §3 walks through what basketball-reference uses and how
the HTTP routes should mirror it.

## 2. Endpoint inventory

All 12 unreachable GAMES-domain endpoints, with verified params and
row models (read directly from
`courtside_data/endpoints/_workflows.py:541-792`). The table is the
single source of truth for the lane; the `path` column gives the
exact BR URL template the EndpointSpec declares.

### 2.1 Per-game box scores (6 endpoints, scope = `GAME`)

All six share the path `/boxscores/{game_id}.html`; `game_id` is a
free-form `str`. Verified format in §3.

| `endpoint_name` | `_workflows.py` line | params | `row_model` | schema location |
|---|---|---|---|---|
| `box_score_player_basic` | 541 | `("game_id",)` | `BoxScorePlayerBasicRow` | `schemas/boxscores.py:308` |
| `box_score_game_info` | 558 | `("game_id",)` | `BoxScoreGameInfoRow` | `schemas/boxscores.py:284` |
| `box_score_player_advanced` | 575 | `("game_id",)` | `BoxScorePlayerAdvancedRow` | `schemas/boxscores.py:211` |
| `box_score_line_score` | 592 | `("game_id",)` | `BoxScoreLineScoreRow` | `schemas/boxscores.py:247` |
| `box_score_player_quarter_splits` | 609 | `("game_id", "period")` | `BoxScorePlayerQuarterSplitRow` | `schemas/boxscores.py:266` |
| `box_score_team_four_factors` | 626 | `("game_id",)` | `BoxScoreTeamFourFactorsRow` | `schemas/boxscores.py:229` |

All six are `kind=EndpointKind.WORKFLOW` and carry the
`WORKFLOW_DIAGNOSTICS` feature flag. Five are
`parser_shape=ParserShape.TABLE`; `box_score_game_info` is
`parser_shape=ParserShape.PAGE_BLOCKS` (it is assembled from
scorebox + prose footer sections, not one `<table>`).

`box_score_player_quarter_splits` is the only one with a second
call param: `period` is a free-form `str` (the EndpointSpec comments
list the legal values as `q1`/`q2`/`h1`/`q3`/`q4`/`h2`; see
`schemas/boxscores.py:266-272`). It is a **within-game sub-request**,
not a separate dataset — the route layer passes it as a query
parameter on the same per-game box-score route (see §4).

### 2.2 Daily leaders (2 endpoints, scope = `DATE`)

| `endpoint_name` | `_workflows.py` line | params | path | `row_model` | schema location |
|---|---|---|---|---|---|
| `player_box_scores` | 643 | `("day", "month", "year")` | `/friv/dailyleaders.cgi?month={month}&day={day}&year={year}` | `PlayerBoxScoreRow` | `schemas/boxscores.py:108` |
| `team_box_scores` | 660 | `("day", "month", "year")` | `/boxscores/?month={month}&day={day}&year={year}` | `TeamBoxScoreRow` | `schemas/boxscores.py:172` |

Both have `error=InvalidDate` and `error_params=("day", "month",
"year")` (a non-existent date returns 404, mapped to
`InvalidDate` in the error pipeline). `player_box_scores` is
`RequestShape.SINGLE_REQUEST`; `team_box_scores` is
`RequestShape.MULTI_REQUEST` with `features=FANOUT_LINKS` because
the workflow fetches each game's individual box-score footer rows
and aggregates them. The two share an inherent
chicken-and-egg relationship with the game-id scheme (the daily
leaders call effectively returns "the game_ids of all games that
happened on this date" as a side effect of the per-team row
assembly) — see §3.

### 2.3 Play-by-play (1 endpoint, scope = `DATE_TEAM`)

| `endpoint_name` | `_workflows.py` line | params | path | `row_model` | schema location |
|---|---|---|---|---|---|
| `play_by_play` | 683 | `("home_team", "day", "month", "year")` | `/boxscores/pbp/` | `PlayByPlayRow` | `schemas/playbyplay.py:47` |

`home_team` is a `Team` enum (coerced by the
`ENUM_PARAM_COERCION` feature flag). The workflow uses
`FANOUT_LINKS` to fetch the daily scoreboard at
`/boxscores/?day={day}&month={month}&year={year}` and resolve
which game corresponds to `(home_team, day, month, year)` — so the
endpoint does not take `game_id` directly; it reconstructs the
game from the date + home team combination. The
`parser_shape=ParserShape.PLAY_BY_PLAY` distinguishes it from the
daily-leaders tables.

### 2.4 League-wide season tables (3 endpoints, scope = `SEASON`)

**RECOMMEND MOVING TO LEAGUE HUB — see §9 for the full rationale.**

| `endpoint_name` | `_workflows.py` line | params | path | `row_model` | schema location |
|---|---|---|---|---|---|
| `season_schedule` | 743 | `("season_end_year",)` | `/leagues/NBA_{season_end_year}_games.html` | `SeasonScheduleRow` | `schemas/schedule.py:55` |
| `players_season_totals` | 763 | `("season_end_year", "include_combined_values")` | `/leagues/NBA_{season_end_year}_totals.html` | `PlayerSeasonTotalsRow` | `schemas/player_totals.py:19` |
| `players_advanced_season_totals` | 778 | `("season_end_year", "include_combined_values")` | `/leagues/NBA_{season_end_year}_advanced.html` | `PlayerAdvancedSeasonTotalsRow` | `schemas/player_totals.py:47` |

The `players_*_season_totals` endpoints add the
`include_combined_values` boolean param (a workflow toggle for
"emit a single combined-totals row per player aggregating any
mid-season trades"; see `schemas/player_totals.py:79` for the
`is_combined_totals` field).

### 2.5 Classification summary

| Scope | Count | Endpoints | UX model |
|---|---|---|---|
| `GAME` | 6 | 6× `box_score_*` | 6-tab box-score viewer for one game |
| `DATE` | 2 | `player_box_scores`, `team_box_scores` | Date picker → daily leaders table |
| `DATE_TEAM` | 1 | `play_by_play` | Date picker + home-team pick → PBP stream |
| `SEASON` | 3 | `season_schedule`, `players_season_totals`, `players_advanced_season_totals` | **Move to League Hub** (no per-game content) |

## 3. The game-identification problem (CRITICAL SECTION)

**This is the single most important design decision for the entire
Games/Browser Hub.** Every per-game box score is fetched with
`game_id`; the EndpointSpec (`_workflows.py:541-642`) declares
`game_id` as a free-form `str`; the actual format basketball-reference
uses is the load-bearing detail.

### 3.1 What basketball-reference uses

Empirically (confirmed by the existing test fixture at
`raw/boxscore_four_factors/202606100NYK.html`, the
`raw/team_box_scores/2017_01_01/201701010ATL.html` fixture used by
`tests/test_box_score_per_game_endpoints.py:28`, and the
`BoxScoreGameInfoRow.game_date` + `home_team` schema fields
which the parser populates from the URL): the game_id format is

```
{YYYYMMDD}0{HOMETEAM_ABBR}
```

where the literal `0` is a separator, `YYYYMMDD` is the calendar date
in Eastern time (the date of the game, not the date it was
played-from-in-the-fixture), and `{HOMETEAM_ABBR}` is the
basketball-reference team abbreviation of the **home** team (e.g.
`ATL` for Atlanta Hawks, `NYK` for New York Knicks, `BOS` for Boston
Celtics).

**Worked example:** `201701010ATL` resolves to
`/boxscores/201701010ATL.html`, which is the box score for the
game hosted by the Atlanta Hawks on 2017-01-01. The
`BoxScoreGameInfoRow` schema (populated by the parser from
scorebox + prose footers) is expected to carry
`game_date=2017-01-01` and `home_team=Team.ATLANTA_HAWKS` for
that fixture (the test asserts this exactly in
`tests/test_box_score_per_game_endpoints.py:67-69`).

The literal `0` is not optional: it is a basketball-reference
quirk that disambiguates games on the same date (rare on
regular-season dates, common on playoff dates when two games are
played on the same day).

### 3.2 What this means for the API design

**The HTTP route should accept `game_id` as a single path
parameter, NOT decompose it into `{date}/{away}/{home}` in the
URL.** The reason is that the `game_id` is the canonical
basketball-reference handle for a game, and decomposing it
forces the caller to know the home-team abbreviation up-front
(which they do not, until they have looked up the day's
scoreboard via the daily-leaders or play-by-play endpoints).

The natural route shape is therefore:

```
GET /api/games/{game_id}/{dataset}
```

where `{game_id}` matches the basketball-reference format
verbatim (`201701010ATL`, `202606100NYK`, …). This keeps the
HTTP layer a thin pass-through to the BR URL: the route
handler builds the call as
`endpoint_name="{dataset}", game_id="{game_id}"` and the
existing BR URL formatter (`_workflows.py`'s path template
`/boxscores/{game_id}.html`) does the rest.

**Reject the alternative** of a route like
`/api/games/{date}/{away_abbr}/{home_abbr}/{dataset}`. It looks
RESTful on paper but it (a) requires the caller to know both
abbreviations up-front, (b) silently disagrees with the
`/boxscores/{game_id}.html` URL when the BR game_id format ever
changes, and (c) does not work for the all-star game or
exhibition games where there is no home team. The single
`game_id` path parameter is simpler and is the right
abstraction.

### 3.3 The game-finding flow

**The chicken-and-egg problem:** to view a box score, the user
needs a `game_id`. To get a `game_id`, they need to know which
games happened on a date. The daily-leaders endpoints already
solve this:

- `GET /api/games/box-scores?date=2024-03-15&dataset=team`
  returns `TeamBoxScoreRow` rows for every game on that date.
- Each team row carries the home/away team abbreviations in the
  `team` / `opponent` fields, which the client combines into
  the `game_id` (`{date}0{home_abbr}`) before navigating to a
  specific game's box score.

The play-by-play endpoint has the same chicken-and-egg
already solved internally: its workflow fans out to
`/boxscores/?day={day}&month={month}&year={year}` first, then
resolves the game from the home-team pick. The HTTP surface
for the play-by-play route is `?date=...&home_team=...` for
the same reason.

`season_schedule` (the league-wide schedule for a season) can
also serve as a game directory for client-side "browse the
whole season" UX, but it is not on the critical path for the
date-picker → game-list flow — that flow is driven by the
daily-leaders call.

### 3.4 Proposed game-identifier format for the HTTP route

```
GET /api/games/{game_id}/{dataset}
  game_id  := {YYYYMMDD}0{HOMETEAM_ABBR}    # verbatim BR game_id
  dataset  := box-score-player-basic
            | box-score-player-advanced
            | box-score-line-score
            | box-score-player-quarter-splits
            | box-score-team-four-factors
            | box-score-game-info
            (six fixed values, see §5 for why this is a closed set)
```

The `period` sub-param for `box-score-player-quarter-splits` is
a query parameter on the same route:

```
GET /api/games/{game_id}/box-score-player-quarter-splits?period=q1
  period  := q1 | q2 | h1 | q3 | q4 | h2 | (any free-form string the
            parser accepts; the BR server returns 404 for unknown
            periods which the error pipeline maps to 404)
```

This is the route shape the service layer should build toward
(see §6).

## 4. HTTP route design

The proposed routes look fundamentally different from the Player
Hub and Team Hub routes. There is no entity search, no entity
summary, no entity catalog — the "catalog" concept does not apply
in the same way. The dates / game-ids in the URL ARE the selector.

### 4.1 Per-game box scores (6 routes)

```http
GET /api/games/{game_id}/box-score-player-basic
GET /api/games/{game_id}/box-score-player-advanced
GET /api/games/{game_id}/box-score-line-score
GET /api/games/{game_id}/box-score-team-four-factors
GET /api/games/{game_id}/box-score-game-info
GET /api/games/{game_id}/box-score-player-quarter-splits?period=q1
```

(`period` is required for the last route; the other five ignore
it. Validation: a `period` value on a route that does not accept
it is silently ignored — or, preferably, rejected with `400
bad_request` for clarity. Decision needed in §9.)

### 4.2 Daily leaders (2 routes)

```http
GET /api/games/box-scores?date=2024-03-15&dataset=player
GET /api/games/box-scores?date=2024-03-15&dataset=team
```

The `dataset` query parameter disambiguates the two daily
endpoints. An alternative is two separate routes
(`/api/games/daily-player-leaders?date=...` and
`/api/games/daily-team-leaders?date=...`) but the
`?dataset=…` form keeps the URL shorter and matches the
entity-hub export-route pattern. Decision needed in §9.

### 4.3 Play-by-play (1 route)

```http
GET /api/games/play-by-play?date=2024-03-15&home_team=BOS
```

`home_team` is a `Team` enum value (the same enum the
play-by-play workflow's `ENUM_PARAM_COERCION` feature consumes
today).

### 4.4 League season tables (3 routes, RECOMMEND MOVING TO LEAGUE HUB)

```http
# Recommended location: /api/league/seasons/{year}/{dataset}
GET /api/league/seasons/{year}/schedule              # season_schedule
GET /api/league/seasons/{year}/player-totals         # players_season_totals
GET /api/league/seasons/{year}/player-totals-advanced # players_advanced_season_totals
```

These three routes do not belong under `/api/games/...` — they
are league-wide, season-scoped, and have no per-game content.
See §9 for the full recommendation.

### 4.5 Status / catalog route

```http
GET /api/endpoints/games-hub
```

Returns the static catalog payload (the six box-score datasets
as a closed set, the two daily-leader datasets, the one PBP
endpoint, and the cross-reference to the three League Hub
endpoints if they were moved). Implemented by
`courtside_data.server.games_catalog.games_hub_catalog()` once
the lane lands.

## 5. Catalog design (or why catalog doesn't apply)

The Team Hub catalog (`courtside_data/server/team_catalog.py`)
groups 13 datasets into 5 tabs; the catalog is a static
`TEAM_DATASETS` tuple plus a static `TEAM_TABS` tuple. The
catalog is meaningful because there are 13 datasets to choose
from, with different scopes and different UI affordances.

### 5.1 Why the catalog concept does not map cleanly

The GAMES domain has 4 different scopes with 4 different URL
shapes. A single "Games Hub catalog" that lists all of them
side-by-side would be confusing:

- The 6 box-score datasets are a **closed set** — every game
  exposes the same 6. There is no "which box-score datasets
  exist for this game?" question to ask.
- The 2 daily-leader datasets are a **closed pair** — `team`
  is always the team-level view of the same data that `player`
  is the player-level view of.
- The 1 play-by-play dataset is a **singleton**.
- The 3 season-scoped datasets (recommended to move) are
  **league-wide** — they have nothing to do with a "Games"
  Hub at all.

### 5.2 Proposed alternative

A `BOX_SCORE_DATASETS` constant (closed set of 6) drives the
box-score viewer's six tabs. A `DAILY_LEADERS_DATASETS`
constant (closed pair of 2) drives the daily-leaders viewer's
tab pair. A `PBP_DATASET` constant (singleton) is referenced
once in the play-by-play route. The 3 season-scoped datasets
move to a future `league_catalog.py` module.

```python
# courtside_data/server/games_catalog.py (when the lane lands)
BOX_SCORE_DATASETS: tuple[BoxScoreDataset, ...] = (
    BoxScoreDataset(id="box-score-player-basic",         label="Player Basic",         ...),
    BoxScoreDataset(id="box-score-player-advanced",      label="Player Advanced",      ...),
    BoxScoreDataset(id="box-score-player-quarter-splits", label="Quarter Splits",       ...),
    BoxScoreDataset(id="box-score-line-score",           label="Line Score",           ...),
    BoxScoreDataset(id="box-score-team-four-factors",    label="Team Four Factors",    ...),
    BoxScoreDataset(id="box-score-game-info",            label="Game Info",            ...),
)

DAILY_LEADERS_DATASETS: tuple[DailyDataset, ...] = (
    DailyDataset(id="player", endpoint_name="player_box_scores", ...),
    DailyDataset(id="team",   endpoint_name="team_box_scores",   ...),
)

PBP_DATASET = PBPDataset(endpoint_name="play_by_play", ...)
```

The `season_schedule` + `players_season_totals` +
`players_advanced_season_totals` endpoints move to a future
`league_catalog.py`; see §9.

## 6. Service design

The games service is a thin wrapper around the existing
`CourtsideClient` (or `CourtsideData` façade) methods in
`courtside_data/client/games.py`. The class is intentionally
different from `PlayerHubService` and `TeamHubService`: it has
no `summary()`, no `search()`, and no `csv()` method (the
existing Player-Hub–style methods do not have obvious games
analogues).

### 6.1 Proposed `GamesHubService` shape

```python
class GamesHubService:
    def daily_box_scores(self, date: date, dataset: Literal["player", "team"]) -> list[dict]:
        """Per-player or per-team box-score rows for every game on `date`."""

    def box_score(self, game_id: str, dataset: str) -> dict:
        """One box-score dataset for one game. The 6 box-score dataset ids
        form a closed set; the service validates against BOX_SCORE_DATASETS."""

    def play_by_play(self, date: date, home_team: Team) -> list[dict]:
        """Play-by-play event stream for the game hosted by `home_team` on `date`."""
```

### 6.2 Workflow runner implications

Every per-game box score is `kind=EndpointKind.WORKFLOW` and
all six share the same BR URL (`/boxscores/{game_id}.html`).
The workflow runner fetches **one** HTML page per game and
**six** different parser views target different table ids on
that same page. The service is therefore naturally a "fetch
once, parse six times" model — though the HTTP layer should
still expose six routes (one per dataset) so the client can
lazy-load individual datasets on demand. A future optimization
could be a `?include=all` query parameter that triggers a
single backend fetch and returns all six datasets, but that is
out of scope for the initial lane.

`box_score_player_quarter_splits` is the one box-score
endpoint with a `period` sub-param. The `period` value
selects which of the six `box-<ABBR>-<period>-basic` tables
the parser targets on the per-game page (see
`schemas/boxscores.py:266-272` for the full table-id list).
The HTTP route accepts `period` as a query parameter; the
service passes it through to the workflow's
`ENUM_PARAM_COERCION` step.

### 6.3 Workflow endpoints in the HTTP layer

Workflow endpoints have a `WORKFLOW_DIAGNOSTICS` feature flag
that emits parser stats alongside the rows. The HTTP layer
should preserve this in the `EndpointRowsResponse` envelope
(see `courtside_data/server/models.py:24-30` for the
existing shape used by Player and Team Hub). Decision needed
in §9: do we expose `parser_stats` as a top-level response
field, or only via the existing `?debug=true` toggle? Player
Hub and Team Hub already do this; consistency wins.

## 7. UI feature design

The `features/games-browser/` package (a future addition —
no UI code exists for this domain today) should be a
**date-driven** UI, not an entity-driven UI. The flow is:

### 7.1 Components

1. **Date picker** — the primary navigation. A simple
   `<input type="date">` that drives the
   `/api/games/box-scores?date=…&dataset=team` call.
2. **Game list** — a small table of "games on the selected
   date" populated from the daily-leaders response. Each row
   is one game (away @ home, score if final). Clicking a row
   navigates to the box-score viewer for that game.
3. **Box-score viewer** — a six-tab viewer (Player Basic,
   Player Advanced, Quarter Splits, Line Score, Four
   Factors, Game Info) for one selected game. The
   quarter-splits tab also has a period picker (Q1 / Q2 /
   H1 / Q3 / Q4 / H2).
4. **Play-by-play viewer** — a date + home-team picker plus
   an event stream (period / time / description / score)
   for the selected game.

### 7.2 Route structure (Next.js–style example)

```
/games?date=2024-03-15                  # game list for that date
/games/{game_id}                        # box-score viewer (defaults to first tab)
/games/{game_id}/{dataset}              # box-score viewer pinned to a tab
/games/{game_id}/play-by-play?date=…    # play-by-play viewer
```

### 7.3 The chicken-and-egg, resolved

The game list comes "for free" from the daily-leaders call —
`/api/games/box-scores?date=2024-03-15&dataset=team` returns
one `TeamBoxScoreRow` per team per game, which the client
groups by `(home_team, away_team)` to form a game list. No
new endpoint is needed; the daily-leaders call IS the
game-directory call. The `season_schedule` endpoint
(recommended to move to League Hub) is an alternative
season-wide game directory but is not on the critical path
for the date-picker flow.

## 8. Fixture capture plan

### 8.1 Per-endpoint fixture strategy

| Endpoint group | Sample param set | URL | Fixture file |
|---|---|---|---|
| `box_score_*` (6) | `game_id="201701010ATL"` | `/boxscores/201701010ATL.html` | `raw/{endpoint_name}/201701010ATL.html` |
| `player_box_scores` | `day=15, month=3, year=2024` | `/friv/dailyleaders.cgi?day=15&month=3&year=2024` | `raw/player_box_scores/2024-03-15.html` |
| `team_box_scores` | `day=15, month=3, year=2024` | `/boxscores/?day=15&month=3&year=2024` | `raw/team_box_scores/2024-03-15.html` (one file, the workflow fans out) |
| `play_by_play` | `day=15, month=3, year=2024, home_team=BOS` | `/boxscores/pbp/202403150BOS.html` | `raw/play_by_play/2024-03-15-BOS.html` |
| `season_schedule` | `season_end_year=2024` | `/leagues/NBA_2024_games.html` | `raw/season_schedule/2024.html` |
| `players_season_totals` | `season_end_year=2024, include_combined_values=False` | `/leagues/NBA_2024_totals.html` | `raw/players_season_totals/2024_false.html` |
| `players_advanced_season_totals` | `season_end_year=2024, include_combined_values=True` | `/leagues/NBA_2024_advanced.html` | `raw/players_advanced_season_totals/2024_true.html` |

### 8.2 Existing fixture assets that can be reused

- `raw/boxscore_four_factors/202606100NYK.html` —
  pre-existing fixture, covers the
  `box_score_team_four_factors` endpoint with
  `game_id="202606100NYK"`. Sibling directories
  `boxscore_plus_minus/` and `boxscore_shot_chart/` are
  for OTHER endpoints (the Plus-Minus and Shot Chart
  endpoints in the all-star or shooting subdomains) and
  are NOT direct fixtures for the per-game box-score
  workflows; their naming convention (`boxscore_*` vs
  the `box_score_*` EndpointSpec names) is a known
  inconsistency that the lane should address (decide
  whether to rename directories or keep them as-is).
- `raw/team_box_scores/2017_01_01/201701010ATL.html` —
  the daily team box-scores fixture, contains a per-day
  scoreboard that the per-game box-score parser can also
  consume. (The
  `tests/test_box_score_per_game_endpoints.py:28` test
  reads this exact path and feeds it to the
  `parse_box_score_player_basic_with_stats` parser.)
- `raw/player_box_scores/` and
  `raw/team_box_scores/` directories — already
  pre-populated for the date-scoped endpoints (the
  existing player-hub / team-hub manifest covers them).
- `raw/season_schedule/`, `raw/players_season_totals/`,
  `raw/players_advanced_season_totals/` — already
  pre-populated for the season-scoped endpoints.

### 8.3 Capture ordering

1. Capture one game's six box-score pages first (one
   real game, e.g. `201701010ATL` — 2017-01-01 Hawks vs
   Spurs, which has dense data and the inactive-player
   edge cases the test suite already covers).
2. Capture one daily-leaders date (a date with ≥4 games
   for variety).
3. Capture one play-by-play game (a different game from
   step 1 to avoid a one-game fixture universe).
4. Capture one season of the season-scoped endpoints
   (these are already pre-populated — verify the
   existing fixtures cover the `?include_combined_values`
   toggle for both `true` and `false`).

## 9. Design decisions needed

### 9.1 Game-identifier scheme (the #1 blocker)

**Decision:** Use the single `game_id` path parameter
(`/api/games/{game_id}/{dataset}`) and accept the
basketball-reference `game_id` format verbatim
(`{YYYYMMDD}0{HOMETEAM_ABBR}`). Rationale in §3.2.

**Alternatives rejected:**

- `/api/games/{date}/{away}/{home}/{dataset}` — forces the
  caller to know both abbreviations up-front; disagrees
  with the BR URL when format changes; does not work for
  the all-star game.
- A new "game-search" endpoint that returns game_ids
  given `(date, away, home)` — duplicates what
  `team_box_scores` already returns; adds a new round-trip
  on the hot path.

### 9.2 League Hub boundary (RECOMMEND MOVE)

**Decision:** Move `season_schedule`,
`players_season_totals`, and
`players_advanced_season_totals` to a future
`courtside_data/server/league_catalog.py` module and serve
them from `/api/league/seasons/{year}/{dataset}`. Rationale:

- All three are `scope=SEASON` and have no per-game or
  per-date content. They share URL structure with the
  existing League Hub endpoints
  (`/leagues/NBA_{season_end_year}_*.html`).
- Two of the three (`players_season_totals`,
  `players_advanced_season_totals`) live in the
  `player_totals` schema module alongside the league
  season tables; moving them to League Hub matches the
  schema grouping.
- `season_schedule` is a league-wide directory of all
  games in a season — semantically a "league navigation"
  surface, not a "games browser" surface. The recommended
  downstream use is "pick a season, browse the
  season-wide schedule, drill into a game" — that is a
  League Hub flow, not a Games Hub flow.

**Consequence:** the Games Hub lane ships 9 endpoints
(box scores + daily leaders + play-by-play) and the
League Hub lane picks up the 3 season-scoped endpoints
plus the existing 11 League endpoints. Total
reachable-endpoint count after both lanes land: 47 / 61
(Player 11 + Team 13 + League 14 = 38, plus Games 9 =
47).

### 9.3 Daily-scores endpoint

**Decision:** **No new endpoint.** The existing
`player_box_scores` and `team_box_scores` endpoints
(§2.2) already return all games for a date, and the
client can derive the game list from the team-level
response (one `TeamBoxScoreRow` per team per game;
client groups by home+away). This is the
"chicken-and-egg resolved" pattern in §3.3 and §7.3.

**Alternative rejected:** a new
`GET /api/games/dates/{date}/scores` endpoint that
returns one row per game (home/away/score/status). Adds
maintenance burden (a new row model, a new EndpointSpec,
a new fixture) and duplicates data the daily leaders
endpoints already return.

### 9.4 Box-score tab vs separate endpoints

**Decision:** Expose 6 separate routes
(`/api/games/{game_id}/{dataset}` for each of the 6
datasets). The client fetches them lazily (one per tab
activation) but they are first-class routes because
(a) the EndpointSpec declares them as 6 separate
workflows, (b) tests need to exercise each
independently, and (c) it gives the client explicit
control over the parse cost for the heavy datasets
(e.g. `box_score_player_quarter_splits` with all 6
periods in one call would mean 6 separate workflow
runs).

**Alternative rejected:** a single
`GET /api/games/{game_id}` route that returns all 6
datasets. Saves a round-trip but ties the box-score
viewer to "fetch all 6 always", which is wrong for the
"only show me Player Basic" UX.

### 9.5 `period` validation

**Decision:** Reject an unknown `period` value with
`400 bad_request` (the existing
`InvalidSearch`/`InvalidPlayer` error pipeline already
maps cleanly to 400). The
`box_score_player_quarter_splits` route requires
`period`; the other 5 box-score routes reject
`period` as an unknown query parameter (or silently
ignore it; preference for "reject" so the client does
not silently drop a typo).

### 9.6 Daily-leaders `dataset` discriminator

**Decision:** Single route
`GET /api/games/box-scores?date=…&dataset=player|team`
with the `dataset` query param. Matches the Player
Hub / Team Hub export-route pattern.

## 10. Implementation checklist + priority

### 10.1 Recommended order

This is the **hardest** of the six endpoint domains. The
recommended implementation order across all domains is:

1. ✅ Player Hub (complete)
2. ✅ Team Hub (scaffolded — needs search fix + fixture
   HTML; see `docs/architecture/team-hub.md` §5)
3. **League Hub** (11→14 endpoints if the 3 GAMES
   season-scoped endpoints move; straightforward
   season-scoped pattern, mostly a copy of the Team Hub
   pattern with no entity in the URL)
4. **Playoffs Hub** (6 endpoints, similar season-scoped
   pattern + 3 `STATIC`-scoped friv endpoints)
5. **Draft/Awards/Leaders Hub** (5 endpoints, mix of
   `SEASON` + `STATIC` scope)
6. **Games/Browser Hub** (this doc — 9 endpoints if the
   3 season-scoped ones moved to League Hub; 12 if all
   stay here; the hardest lane by a wide margin)

### 10.2 Pre-flight checklist before starting the lane

- [ ] **Move the 3 season-scoped GAMES endpoints to
  League Hub** (or, alternatively, accept that this
  domain keeps them). §9.2 has the rationale.
- [ ] **Capture the box-score fixture universe** (§8).
  One real game, six HTML pages, four file
  directories. Use `201701010ATL` if reusing the
  existing test fixture; capture a second game for
  variety.
- [ ] **Add `BOX_SCORE_ENDPOINTS`, `DAILY_ENDPOINTS`,
  `PBP_ENDPOINTS` whitelists** in
  `courtside_data/server/fixtures.py` mirroring
  `TEAM_ENDPOINTS`. Add `_box_score_map`,
  `_daily_leaders_map`, `_pdp_map` helpers mirroring
  `_player_only_map`.
- [ ] **Create `courtside_data/server/games_service.py`**
  with `GamesHubService` (§6.1).
- [ ] **Create `courtside_data/server/games_models.py`**
  with `BoxScoreViewer`, `DailyLeadersResponse`,
  `PlayByPlayResponse`, `GameSummary` Pydantic models.
- [ ] **Fill in `courtside_data/server/games_catalog.py`**
  with `BOX_SCORE_DATASETS`, `DAILY_LEADERS_DATASETS`,
  `PBP_DATASET`, and `games_hub_catalog()`.
- [ ] **Add the 9 new routes to
  `courtside_data/server/app.py`** (§4).
- [ ] **Add the `features/games-browser/` UI** (§7).
- [ ] **Add a `tests/server/test_games_hub_api.py`**
  smoke test mirroring
  `tests/server/test_player_hub_api.py`.

### 10.3 Success criteria

- All 9 (or 12, if the 3 season-scoped endpoints stay)
  GAMES endpoints return valid rows in both live and
  fixture transport modes.
- The 6 box-score routes share one catalog entry per
  game (the `BOX_SCORE_DATASETS` constant).
- The daily-leaders route returns one
  `TeamBoxScoreRow` per team per game for the selected
  date; the client can derive the game list from the
  response.
- The play-by-play route returns one `PlayByPlayRow`
  per event for the selected game.
- The 3 season-scoped endpoints are served from the
  League Hub (or from a new Games Hub route if the move
  is rejected) with the same row shape the
  `players_season_totals` and
  `players_advanced_season_totals` workflow tests
  already assert.
