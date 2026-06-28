"""Server-safe fixture transport for Player Hub development mode."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from courtside_data.endpoints import ENDPOINTS
from courtside_data.http._constants import BASE_URL

if TYPE_CHECKING:
    from courtside_data.http import HTTPService

FixtureValue = Path | tuple[int, dict[str, str] | None]

PLAYER_ONLY_ENDPOINTS = {
    "player_career_stats",
    "player_playoff_series",
    "player_adjusted_shooting",
    "player_play_by_play",
    "player_game_highs",
    "player_all_star",
    "player_similarity_scores",
    "player_salaries",
}

PLAYER_SEASON_ENDPOINTS = {
    "player_splits",
    "player_on_off",
    "player_shot_charts",
    "regular_season_player_box_scores",
    "playoff_player_box_scores",
}

# Team Hub endpoint whitelists. Mirror the player-hub pair: TEAM_ENDPOINTS
# are reachable via /api/teams/{team_identifier}/{dataset} and
# TEAM_SEASON_ENDPOINTS via /api/teams/{team_identifier}/seasons/{year}/{dataset}.
TEAM_ENDPOINTS = frozenset(
    {
        "team_contracts",
        "franchise_history",
    }
)

TEAM_SEASON_ENDPOINTS = frozenset(
    {
        "team_roster",
        "team_transactions",
        "team_lineups",
        "team_starting_lineups",
        "team_on_off",
        "team_injury_report",
        "team_splits",
        "team_and_opponent",
        "team_opponent_stats",
        "team_misc_four_factors",
        "team_schedule",
    }
)


class MissingFixtureError(FileNotFoundError):
    """Raised when fixture mode cannot satisfy a requested endpoint."""


def default_raw_root() -> Path:
    return Path(__file__).resolve().parents[2] / "raw"


def _content_type(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return "application/json"
    if path.suffix.lower() == ".xml":
        return "application/xml"
    return "text/html; charset=utf-8"


def _strip_query(url: str) -> str:
    return url.split("?", 1)[0]


def _query_key(url: str) -> tuple[str, tuple[tuple[str, str], ...]]:
    parsed = httpx.URL(url)
    return parsed.path, tuple(sorted(parsed.params.multi_items()))


class FixtureTransport(httpx.BaseTransport):
    """Replay raw HTML fixtures for exact Basketball Reference URLs."""

    def __init__(self, url_to_path: dict[str, FixtureValue]) -> None:
        self._url_to_path = url_to_path

    def _lookup(self, url: str) -> FixtureValue | None:
        if url in self._url_to_path:
            return self._url_to_path[url]
        stripped = _strip_query(url)
        if stripped != url and stripped in self._url_to_path:
            return self._url_to_path[stripped]
        path = httpx.URL(url).path
        if path in self._url_to_path:
            return self._url_to_path[path]
        target_key = _query_key(url)
        for key, value in self._url_to_path.items():
            if _query_key(key) == target_key:
                return value
        return None

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        match = self._lookup(url)
        if match is None:
            raise MissingFixtureError(f"No fixture registered for {url!r}. Available keys: {sorted(self._url_to_path)}")
        if isinstance(match, tuple):
            status_code, headers = match
            return httpx.Response(status_code, headers=headers or {}, text="", request=request)

        content = match.read_bytes()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="replace")
        return httpx.Response(
            200,
            headers={"Content-Type": _content_type(match)},
            content=content,
            text=text,
            request=request,
        )

    def close(self) -> None:
        return None


def _render_url(endpoint_name: str, params: dict[str, object]) -> str:
    endpoint = ENDPOINTS[endpoint_name]
    return f"{BASE_URL}{endpoint.path.format(**params)}"


def _player_only_map(endpoint_name: str, raw_root: Path, player_identifier: str) -> dict[str, FixtureValue]:
    path = raw_root / endpoint_name / f"{player_identifier}.html"
    if not path.is_file():
        raise MissingFixtureError(f"Missing fixture file {path}")
    params = {"player_identifier": player_identifier}
    return {_render_url(endpoint_name, params): path}


def _player_season_map(
    endpoint_name: str,
    raw_root: Path,
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
) -> dict[str, FixtureValue]:
    path = raw_root / endpoint_name / f"{player_identifier}_{season_end_year}.html"
    if not path.is_file():
        raise MissingFixtureError(f"Missing fixture file {path}")
    params = {
        "player_identifier": player_identifier,
        "season_end_year": season_end_year,
        "include_inactive_games": include_inactive_games,
    }
    return {_render_url(endpoint_name, params): path}


def _team_only_map(endpoint_name: str, raw_root: Path, team_abbreviation: str) -> dict[str, FixtureValue]:
    path = raw_root / endpoint_name / f"{team_abbreviation}.html"
    if not path.is_file():
        raise MissingFixtureError(f"Missing fixture file {path}")
    params = {"team_abbreviation": team_abbreviation}
    return {_render_url(endpoint_name, params): path}


def _team_season_map(
    endpoint_name: str,
    raw_root: Path,
    team_abbreviation: str,
    season_end_year: int,
) -> dict[str, FixtureValue]:
    if endpoint_name == "team_injury_report":
        for filename in ("default.html", "offseason.html"):
            path = raw_root / endpoint_name / filename
            if path.is_file():
                params = {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year}
                return {_render_url(endpoint_name, params): path}
        raise MissingFixtureError(f"Missing fixture file {raw_root / endpoint_name / 'default.html'}")

    path = raw_root / endpoint_name / f"{team_abbreviation}_{season_end_year}.html"
    if not path.is_file():
        raise MissingFixtureError(f"Missing fixture file {path}")
    params = {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year}
    return {_render_url(endpoint_name, params): path}


def _search_map(raw_root: Path, term: str) -> dict[str, FixtureValue]:
    search_root = raw_root / "search"
    fixture = search_root / f"{term}.html"
    if not fixture.is_file():
        raise MissingFixtureError(f"Missing fixture file {fixture}")

    url_to_path: dict[str, FixtureValue] = {f"{BASE_URL}/search/search.fcgi?search={term}": fixture}
    if term == "jaebaebae":
        pages = sorted(search_root.glob("ja_page_*.html"), key=_search_page_number)
        for index, page in enumerate(pages, start=1):
            offset = index * 100
            for idx in ("players", "wnba_players", "intl_players", "nbdl_players", "sup_players"):
                url_to_path[f"{BASE_URL}/search/search.fcgi?search={term}&idx={idx}&offset={offset}"] = page
    return url_to_path


def _search_page_number(path: Path) -> int:
    match = re.search(r"\d+", path.stem)
    return int(match.group(0)) if match else -1


def fixture_url_map(
    endpoint_name: str,
    params: dict[str, object],
    raw_root: Path | None = None,
) -> dict[str, FixtureValue]:
    root = raw_root or default_raw_root()
    if endpoint_name == "search":
        return _search_map(root, str(params["term"]))
    if endpoint_name in PLAYER_ONLY_ENDPOINTS:
        return _player_only_map(endpoint_name, root, str(params["player_identifier"]))
    if endpoint_name in PLAYER_SEASON_ENDPOINTS:
        return _player_season_map(
            endpoint_name,
            root,
            str(params["player_identifier"]),
            int(str(params["season_end_year"])),
            bool(params.get("include_inactive_games", False)),
        )
    if endpoint_name in TEAM_ENDPOINTS:
        return _team_only_map(endpoint_name, root, str(params["team_abbreviation"]))
    if endpoint_name in TEAM_SEASON_ENDPOINTS:
        return _team_season_map(
            endpoint_name,
            root,
            str(params["team_abbreviation"]),
            int(str(params["season_end_year"])),
        )
    raise MissingFixtureError(f"Endpoint {endpoint_name!r} is not supported in Player Hub fixture mode")


def build_fixture_service(endpoint_name: str, params: dict[str, object], raw_root: Path | None = None) -> HTTPService:
    from courtside_data.http import HTTPService

    transport = FixtureTransport(fixture_url_map(endpoint_name, params, raw_root=raw_root))
    session = httpx.Client(transport=transport, follow_redirects=True)
    return HTTPService(
        session=session,
        cache=False,
        rate_limit_interval=0.0,
        rate_limit_jitter=0.0,
    )


def fixture_seasons_for_player(player_identifier: str, raw_root: Path | None = None) -> dict[str, list[int]]:
    root = raw_root or default_raw_root()
    result: dict[str, list[int]] = {}
    for endpoint_name in sorted(PLAYER_SEASON_ENDPOINTS):
        endpoint_root = root / endpoint_name
        seasons: list[int] = []
        for path in endpoint_root.glob(f"{player_identifier}_*.html"):
            suffix = path.stem.removeprefix(f"{player_identifier}_")
            if suffix.isdigit():
                seasons.append(int(suffix))
            if seasons:
                result[endpoint_name] = sorted(set(seasons), reverse=True)
    return result


def fixture_seasons_for_team(team_abbreviation: str, raw_root: Path | None = None) -> dict[str, list[int]]:
    root = raw_root or default_raw_root()
    result: dict[str, list[int]] = {}
    for endpoint_name in sorted(TEAM_SEASON_ENDPOINTS - {"team_injury_report"}):
        endpoint_root = root / endpoint_name
        seasons: list[int] = []
        for path in endpoint_root.glob(f"{team_abbreviation}_*.html"):
            suffix = path.stem.removeprefix(f"{team_abbreviation}_")
            if suffix.isdigit():
                seasons.append(int(suffix))
        if seasons:
            result[endpoint_name] = sorted(set(seasons), reverse=True)
    return result


# TODO(endpoint-roadmap): Fixture HTML capture needed for 34 additional
# endpoints. This block is documentation-only; it does NOT add any
# whitelists, helpers, or guard branches. The four new lanes below
# mirror the existing TEAM_ENDPOINTS / TEAM_SEASON_ENDPOINTS pattern
# (defined at fixtures.py:41-62) and the existing team TODO above.
#
# Beyond the 13 team endpoints (whitelist + capture plan in the
# # TODO(team-hub): block at fixtures.py:207-336), 34 more endpoints
# have no HTTP route and no fixture HTML. The capture plan is
# documented per-domain:
#   - LEAGUE (11):  docs/architecture/league-hub.md  §7 (planned)
#   - PLAYOFFS (6): docs/architecture/playoffs-hub.md §7 (planned)
#   - DRAFT_AWARDS_LEADERS (5):
#                   docs/architecture/draft-awards-hub.md §7 (planned)
#   - GAMES (12):   docs/architecture/games-browser-hub.md §8
#
# Total fixture HTML files needed across all lanes: ~47
# (13 team + 34 remaining). Each file is a saved basketball-reference
# HTML page; see the per-domain docs for the exact URLs and
# raw/ file paths.
#
# What (per lane): add the per-endpoint whitelist sets, the per-endpoint
#   fixture-map builder helpers, and the dispatch branches in
#   :func:`fixture_url_map` (mirror the four-branch pattern that
#   PLAYER_ONLY_ENDPOINTS / PLAYER_SEASON_ENDPOINTS /
#   TEAM_ENDPOINTS / TEAM_SEASON_ENDPOINTS follow at
#   fixtures.py:197-206 and fixtures.py:331-336).
#
# Per-domain whitelists to add (one set per lane; union of all four
# is the "34 unreachable endpoints" referenced in app.py:368):
#
#   LEAGUE_ENDPOINTS (11 entries, all scope=SEASON with the
#   season_end_year param):
#     league_per_game_stats, league_per_36_minutes, league_totals,
#     league_per_100_possessions, league_shooting, league_play_by_play,
#     league_transactions, rookie_stats, standings, standings_by_date,
#     attendance.
#
#   PLAYOFFS_ENDPOINTS (6 entries; first 3 scope=SEASON, last 3
#   scope=STATIC with no params):
#     playoff_per_game, playoff_totals, playoff_bracket,
#     friv_7_game_playoff_series_outcomes_team_is_down,
#     friv_7_game_playoff_series_outcomes_team_is_tied,
#     friv_7_game_playoff_series_outcomes_team_is_up.
#
#   DRAFT_AWARDS_LEADERS_ENDPOINTS (5 entries; first 3 scope=SEASON,
#     last 2 scope=STATIC):
#     draft_picks, season_awards, season_awards_voting,
#     season_leaders, career_leaders.
#
#   GAMES_ENDPOINTS (12 entries; see games-browser-hub.md §8 for the
#   full per-endpoint capture list):
#     box_score_player_basic, box_score_game_info,
#     box_score_player_advanced, box_score_line_score,
#     box_score_player_quarter_splits, box_score_team_four_factors,
#     player_box_scores, team_box_scores, play_by_play,
#     season_schedule, players_season_totals,
#     players_advanced_season_totals.
#     The 3 GAMES-domain endpoints that are already reachable via the
#     Player Hub (regular_season_player_box_scores,
#     playoff_player_box_scores, search) are NOT in this set -- they
#     are served by /api/players/{id}/seasons/{year}/{dataset} and
#     /api/players/search?term=... today and do not need a games
#     route. See the full inventory at
#     docs/architecture/endpoint-roadmap.md §2.6.
#
# Per-domain fixture-map helpers to add (mirror the player/team
# pattern at fixtures.py:142-181):
#
#   _league_season_map -- season-scoped league endpoint
#     -> one file under raw/{endpoint_name}/{season_end_year}.html
#   _playoff_season_map -- season-scoped playoff endpoint
#     -> one file under raw/{endpoint_name}/{season_end_year}.html
#   _playoff_static_map -- static-scope playoff endpoint
#     -> the 3 friv endpoints share one HTML; raw/
#        friv_7_game_playoff_series_outcomes_team_is_<down|tied|up>/
#        default.html (the same HTML for all 3; the workflow's
#        table_id selects which tbody to parse).
#   _draft_season_map -- season-scoped draft/awards endpoint
#     -> one file under raw/{endpoint_name}/{season_end_year}.html
#   _draft_static_map -- static-scope draft/awards endpoint
#     -> 2 static endpoints; /leaders/per_season.html and
#        /leaders/pts_career.html -- capture under raw/season_leaders/
#        and raw/career_leaders/ respectively.
#   _box_score_map -- per-game box score (GAME scope)
#     -> 6 endpoints share /boxscores/{game_id}.html; capture under
#        raw/{endpoint_name}/{game_id}.html.
#   _daily_leaders_map -- daily box-score leaders (DATE scope)
#     -> 2 endpoints; one file per date under
#        raw/{endpoint_name}/{YYYY-MM-DD}.html (team_box_scores fans
#        out to per-game HTMLs internally, so a single daily HTML is
#        enough).
#   _pdp_map -- play-by-play (DATE_TEAM scope)
#     -> 1 endpoint; raw/play_by_play/{YYYY-MM-DD}-{HOME}.html.
#
# Per-domain dispatch branches to add in :func:`fixture_url_map`
# (insert before the existing team guard at fixtures.py:331-336):
#   - GAMES: dispatch to _box_score_map / _daily_leaders_map /
#     _pdp_map based on the endpoint's scope.
#   - PLAYOFFS: dispatch to _playoff_season_map / _playoff_static_map.
#   - DRAFT_AWARDS_LEADERS: dispatch to _draft_season_map /
#     _draft_static_map.
#   - LEAGUE: dispatch to _league_season_map.
#
# Where: courtside_data/server/fixtures.py (this file), raw/ directory
#   on disk (the project root; see default_raw_root() at fixtures.py:69).
# How: see the existing # TODO(team-hub): block above for the
#   per-endpoint pattern (capture -> whitelist entry -> helper ->
#   dispatch branch). The four new lanes follow the same 4-step
#   recipe. Basketball-Reference rate-limits aggressively; respect the
#   ~8-9 req/min ceiling in HTTPService and avoid bursty captures. Save
#   the HTML "as-is" -- the parser expects raw BR markup.
# Decision needed: see docs/architecture/games-browser-hub.md §9.2
#   (RECOMMEND move the 3 GAMES season-scoped endpoints to League
#   Hub). If the move is rejected, the GAMES_ENDPOINTS set above
#   stays as-is and the League Hub lane picks up only the original
#   11 LEAGUE_ENDPOINTS. If the move is accepted, the 3 endpoints
#   move from GAMES_ENDPOINTS to LEAGUE_ENDPOINTS and the League
#   Hub lane grows from 11 to 14 endpoints.
# Verify: after each lane lands, run the cross-validation check
#   `uv run python -c "from courtside_data.server.fixtures import
#   LEAGUE_ENDPOINTS, PLAYOFFS_ENDPOINTS,
#   DRAFT_AWARDS_LEADERS_ENDPOINTS, GAMES_ENDPOINTS;
#   print(len(LEAGUE_ENDPOINTS) + len(PLAYOFFS_ENDPOINTS) +
#   len(DRAFT_AWARDS_LEADERS_ENDPOINTS) + len(GAMES_ENDPOINTS))"`
#   and confirm the count is 34 (or 31 if the 3 GAMES season-scoped
#   endpoints moved to League Hub). Then run `uv run pytest tests -n
#   auto -q` to confirm the fixture-mode tests pass.
