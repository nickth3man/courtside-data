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
