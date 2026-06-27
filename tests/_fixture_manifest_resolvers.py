"""Fixture resolvers used by :mod:`tests.fixture_manifest`."""

from __future__ import annotations

import re
from pathlib import Path

from courtside_data.endpoints import EndpointFeature, EndpointSpec, RequestShape

from tests._fixture_manifest_common import (
    BASE_URL,
    GAME_ID_RE,
    MONTH_RE,
    PLAYER_YEAR_RE,
    PROJECT_ROOT,
    RAW_ROOT,
    TEAM_DATE_RE,
    TEAM_YEAR_RE,
    YEAR_RE,
    Case,
    ResolveResult,
    list_html,
    make_case,
    render_url,
)
from tests.fixture_transport import FixtureValue


def is_multi_request_fixture_endpoint(endpoint: EndpointSpec) -> bool:
    """Return whether an endpoint's fixture case needs a multi-URL map."""
    if endpoint.metadata is None:
        return False
    return (
        endpoint.metadata.request_shape is RequestShape.MULTI_REQUEST
        or EndpointFeature.FANOUT_LINKS in endpoint.metadata.features
    )


def resolve_endpoint(endpoint_name: str, endpoint: EndpointSpec) -> ResolveResult:
    """Dispatch an endpoint to the resolver matching its fixture layout."""
    if is_multi_request_fixture_endpoint(endpoint):
        return _resolve_multi_request_endpoint(endpoint_name)

    if endpoint_name in ("standings", "attendance", "playoff_bracket"):
        return _resolve_season_endpoint(endpoint_name, endpoint, endpoint_name, filename_year_only=True)

    if endpoint_name == "player_box_scores":
        return _resolve_player_box_scores(endpoint_name, endpoint)

    if endpoint_name in ("box_score_player_basic", "box_score_game_info"):
        return _resolve_box_score_game_endpoint(endpoint_name, endpoint)

    if endpoint_name in ("regular_season_player_box_scores", "playoff_player_box_scores"):
        return _resolve_player_season_endpoint(
            endpoint_name,
            endpoint,
            endpoint_name,
            extra_params={"include_inactive_games": False},
        )

    if endpoint_name in ("players_season_totals", "players_advanced_season_totals"):
        return _resolve_players_season_totals(endpoint_name, endpoint)

    if endpoint_name == "season_awards_voting":
        return _resolve_season_awards_voting(endpoint_name, endpoint)

    if endpoint_name.startswith("friv_7_game_playoff_series_outcomes_"):
        return _resolve_friv_outcomes(endpoint_name, endpoint)

    if endpoint_name == "career_leaders":
        return _resolve_single_file_endpoint(
            endpoint_name,
            endpoint,
            "leaders_record_boards",
            fixture_name="pts_career.html",
            params={},
        )
    if endpoint_name == "season_leaders":
        return _resolve_single_file_endpoint(
            endpoint_name,
            endpoint,
            "season_leaders",
            fixture_name="default.html",
            params={},
        )
    if endpoint_name == "team_injury_report":
        return _resolve_single_file_endpoint(
            endpoint_name,
            endpoint,
            "team_injury_report",
            fixture_name="default.html",
            params={"team_abbreviation": "BOS", "season_end_year": 2024},
        )

    if endpoint.params == ("team_abbreviation",):
        return _resolve_team_only_endpoint(endpoint_name, endpoint, endpoint_name)
    if endpoint.params == ("player_identifier", "season_end_year"):
        return _resolve_player_season_endpoint(endpoint_name, endpoint, endpoint_name)
    if endpoint.params == ("player_identifier",):
        return _resolve_player_endpoint(endpoint_name, endpoint, endpoint_name)

    season_result = _resolve_season_endpoint(endpoint_name, endpoint, endpoint_name, filename_year_only=True)
    if season_result[0] is not None:
        return season_result

    team_season_result = _resolve_season_endpoint(endpoint_name, endpoint, endpoint_name, filename_year_only=False)
    if team_season_result[0] is not None:
        return team_season_result

    return None, f"no parser matches endpoint {endpoint_name!r}"


def _resolve_multi_request_endpoint(endpoint_name: str) -> ResolveResult:
    if endpoint_name == "team_box_scores":
        return _resolve_team_box_scores()
    if endpoint_name == "play_by_play":
        return _resolve_play_by_play()
    if endpoint_name == "season_schedule":
        return _resolve_season_schedule()
    if endpoint_name == "standings_by_date":
        return _resolve_standings_by_date()
    if endpoint_name == "search":
        return _resolve_search()
    return None, f"no multi-request resolver matches endpoint {endpoint_name!r}"


def _resolve_season_endpoint(
    endpoint_name: str,
    endpoint: EndpointSpec,
    raw_subdir: str,
    *,
    filename_year_only: bool = True,
) -> ResolveResult:
    raw_dir = RAW_ROOT / raw_subdir
    files = list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    cases: list[Case] = []
    for path in files:
        stem = path.stem
        if filename_year_only:
            match = YEAR_RE.match(stem)
            if not match:
                return None, f"unexpected fixture name '{stem}.html' (expected 'YYYY.html')"
            year = int(match.group(1))
            params = {"season_end_year": year}
        else:
            match = TEAM_YEAR_RE.match(stem)
            if not match:
                return None, f"unexpected fixture name '{stem}.html' (expected 'TEAM_YYYY.html')"
            year = int(match.group(2))
            params = {"team_abbreviation": match.group(1), "season_end_year": year}

        if endpoint.min_year is not None and year < endpoint.min_year:
            continue
        if endpoint.max_year is not None and year > endpoint.max_year:
            continue

        expected = set(endpoint.params)
        actual = set(params)
        if expected != actual:
            return (
                None,
                f"params mismatch: endpoint declares {sorted(expected)}, "
                f"parser produced {sorted(actual)} for '{stem}.html'",
            )

        cases.append(make_case(endpoint_name, params, {render_url(endpoint, params): path}))

    return cases, None


def _resolve_player_endpoint(endpoint_name: str, endpoint: EndpointSpec, raw_subdir: str) -> ResolveResult:
    raw_dir = RAW_ROOT / raw_subdir
    files = list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    expected = set(endpoint.params)
    if expected != {"player_identifier"}:
        return None, f"unexpected params {sorted(expected)} for player endpoint"

    cases = [
        make_case(
            endpoint_name,
            {"player_identifier": path.stem},
            {render_url(endpoint, {"player_identifier": path.stem}): path},
        )
        for path in files
    ]
    return cases, None


def _resolve_player_season_endpoint(
    endpoint_name: str,
    endpoint: EndpointSpec,
    raw_subdir: str,
    *,
    extra_params: dict[str, object] | None = None,
) -> ResolveResult:
    raw_dir = RAW_ROOT / raw_subdir
    files = list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    cases: list[Case] = []
    for path in files:
        match = PLAYER_YEAR_RE.match(path.stem)
        if not match:
            continue
        params: dict = {
            "player_identifier": match.group(1),
            "season_end_year": int(match.group(2)),
        }
        if extra_params:
            params.update(extra_params)
        cases.append(make_case(endpoint_name, params, {render_url(endpoint, params): path}))

    if not cases:
        return None, f"no parseable fixtures in raw/{raw_subdir}"
    return cases, None


def _resolve_single_file_endpoint(
    endpoint_name: str,
    endpoint: EndpointSpec,
    raw_subdir: str,
    *,
    fixture_name: str,
    params: dict,
) -> ResolveResult:
    raw_path = RAW_ROOT / raw_subdir / fixture_name
    if not raw_path.is_file():
        return None, f"missing fixture {raw_path.relative_to(PROJECT_ROOT)}"
    return [make_case(endpoint_name, params, {render_url(endpoint, params): raw_path})], None


def _resolve_team_only_endpoint(endpoint_name: str, endpoint: EndpointSpec, raw_subdir: str) -> ResolveResult:
    raw_dir = RAW_ROOT / raw_subdir
    files = list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    expected = set(endpoint.params)
    if expected != {"team_abbreviation"}:
        return None, f"unexpected params {sorted(expected)} for team-only endpoint"

    cases = [
        make_case(
            endpoint_name,
            {"team_abbreviation": path.stem},
            {render_url(endpoint, {"team_abbreviation": path.stem}): path},
        )
        for path in files
    ]
    return cases, None


def _resolve_player_box_scores(endpoint_name: str, endpoint: EndpointSpec) -> ResolveResult:
    raw_dir = RAW_ROOT / "player_box_scores"
    files = list_html(raw_dir)
    if not files:
        return None, "no fixtures in raw/player_box_scores"

    cases: list[Case] = []
    for path in files:
        match = MONTH_RE.match(path.stem)
        if not match:
            return None, f"unexpected fixture '{path.name}' (expected YYYY_MM_DD.html)"
        params = {"year": int(match.group(1)), "month": int(match.group(2)), "day": int(match.group(3))}
        cases.append(make_case(endpoint_name, params, {render_url(endpoint, params): path}))
    return cases, None


def _resolve_box_score_game_endpoint(endpoint_name: str, endpoint: EndpointSpec) -> ResolveResult:
    raw_dir = RAW_ROOT / "team_box_scores"
    if not raw_dir.is_dir():
        return None, "no raw/team_box_scores/ directory"

    preferred = raw_dir / "2017_01_01" / "201701010ATL.html"
    files = [preferred] if preferred.is_file() else []
    if not files:
        files = sorted(
            path for path in raw_dir.glob("*/*.html") if path.name != "index.html" and GAME_ID_RE.match(path.stem)
        )
    if not files:
        return None, "no per-game box-score fixtures in raw/team_box_scores"

    game_id = files[0].stem
    params = {"game_id": game_id}
    return [make_case(endpoint_name, params, {render_url(endpoint, params): files[0]})], None


def _resolve_players_season_totals(endpoint_name: str, endpoint: EndpointSpec) -> ResolveResult:
    raw_dir = RAW_ROOT / endpoint_name
    files = list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{endpoint_name}"

    cases: list[Case] = []
    for path in files:
        stem = path.stem
        if "_" in stem:
            year_str, flag_str = stem.split("_", 1)
            match = YEAR_RE.match(year_str)
            if not match or flag_str not in ("true", "false"):
                return None, f"unexpected fixture '{path.name}'"
            params: dict = {
                "season_end_year": int(year_str),
                "include_combined_values": flag_str == "true",
            }
        else:
            match = YEAR_RE.match(stem)
            if not match:
                return None, f"unexpected fixture '{path.name}'"
            params = {"season_end_year": int(stem)}
            if "include_combined_values" in endpoint.params:
                params["include_combined_values"] = False
        cases.append(make_case(endpoint_name, params, {render_url(endpoint, params): path}))
    return cases, None


def _resolve_season_awards_voting(endpoint_name: str, endpoint: EndpointSpec) -> ResolveResult:
    raw_dir = RAW_ROOT / "season_awards_voting"
    files = list_html(raw_dir)
    if not files:
        return None, "no fixtures in raw/season_awards_voting"

    cases: list[Case] = []
    for path in files:
        match = re.match(r"^awards_(\d{4})$", path.stem)
        if not match:
            return None, f"unexpected fixture '{path.name}' (expected 'awards_YYYY.html')"
        params = {"season_end_year": int(match.group(1)), "award": "mvp"}
        cases.append(make_case(endpoint_name, params, {render_url(endpoint, params): path}))
    return cases, None


def _resolve_friv_outcomes(endpoint_name: str, endpoint: EndpointSpec) -> ResolveResult:
    raw_dir = RAW_ROOT / endpoint_name
    files = list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{endpoint_name}"
    return [make_case(endpoint_name, {}, {render_url(endpoint, {}): path}) for path in files], None


def _parse_team_box_scores_dir(dir_: Path) -> dict[str, FixtureValue] | None:
    index = dir_ / "index.html"
    if not index.is_file():
        return None

    from parsel import Selector

    selector = Selector(text=index.read_text(encoding="utf-8"))
    hrefs = selector.css("td.gamelink a::attr(href)").getall()
    if not hrefs:
        return None

    parts = dir_.name.split("_")
    if len(parts) != 3:
        return None
    year, month, day = parts
    index_url = f"{BASE_URL}/boxscores/?month={int(month)}&day={int(day)}&year={year}"
    url_to_file: dict[str, FixtureValue] = {index_url: index}

    for href in hrefs:
        if not href.startswith("/boxscores/"):
            continue
        game_file = dir_ / href.rsplit("/", 1)[-1]
        if not game_file.is_file():
            return None
        url_to_file[BASE_URL + href] = game_file

    return url_to_file


def _resolve_team_box_scores() -> ResolveResult:
    raw_dir = RAW_ROOT / "team_box_scores"
    if not raw_dir.is_dir():
        return None, "no raw/team_box_scores/ directory"
    date_dirs = sorted(path for path in raw_dir.iterdir() if path.is_dir())
    if not date_dirs:
        return None, "raw/team_box_scores/ has no date subdirectories"

    for dir_ in date_dirs:
        url_to_file = _parse_team_box_scores_dir(dir_)
        if url_to_file is None:
            continue
        parts = dir_.name.split("_")
        params = {"year": int(parts[0]), "month": int(parts[1]), "day": int(parts[2])}
        return [make_case("team_box_scores", params, url_to_file)], None

    return None, "no date dir had a parseable index.html + game files"


def _resolve_play_by_play() -> ResolveResult:
    raw_dir = RAW_ROOT / "play_by_play"
    if not raw_dir.is_dir():
        return None, "no raw/play_by_play/ directory"
    team_dirs = sorted(path for path in raw_dir.iterdir() if path.is_dir())
    if not team_dirs:
        return None, "raw/play_by_play/ has no team/date subdirectories"

    from parsel import Selector

    cases: list[Case] = []
    for dir_ in team_dirs:
        match = TEAM_DATE_RE.match(dir_.name)
        if not match:
            continue
        home_team, year, month, day = match.group(1), int(match.group(2)), int(match.group(3)), int(match.group(4))

        index = dir_ / "index.html"
        if not index.is_file():
            continue

        selector = Selector(text=index.read_text(encoding="utf-8"))
        matching_href = _matching_home_team_href(selector.css("td.gamelink a::attr(href)").getall(), home_team)
        if matching_href is None:
            continue

        pbp_file = dir_ / matching_href.rsplit("/", 1)[-1]
        if not pbp_file.is_file():
            continue

        index_url = f"{BASE_URL}/boxscores/?day={day}&month={month}&year={year}"
        game_id = matching_href.rsplit("/", 1)[-1]
        pbp_url = f"{BASE_URL}/boxscores/pbp/{game_id}"
        params = {"home_team": home_team, "day": day, "month": month, "year": year}
        cases.append(make_case("play_by_play", params, {index_url: index, pbp_url: pbp_file}))

    if cases:
        return cases, None
    return None, "no play_by_play dir had an index + home-team pbp file"


def _matching_home_team_href(hrefs: list[str], home_team: str) -> str | None:
    for href in hrefs:
        if not href.startswith("/boxscores/"):
            continue
        game_id = href.rsplit("/", 1)[-1].removesuffix(".html")
        match = GAME_ID_RE.match(game_id)
        if match and match.group(3) == home_team:
            return href
    return None


def _resolve_season_schedule() -> ResolveResult:
    raw_dir = RAW_ROOT / "season_schedule"
    if not raw_dir.is_dir():
        return None, "no raw/season_schedule/ directory"
    year_dirs = sorted(path for path in raw_dir.iterdir() if path.is_dir() and YEAR_RE.match(path.name))
    if not year_dirs:
        return None, "raw/season_schedule/ has no year subdirectories"

    from parsel import Selector

    cases: list[Case] = []
    for year_dir in year_dirs:
        year = int(year_dir.name)
        index = year_dir / "index.html"
        if not index.is_file():
            continue

        selector = Selector(text=index.read_text(encoding="utf-8"))
        all_hrefs = selector.css("a::attr(href)").getall()
        month_hrefs = [href for href in all_hrefs if re.match(rf"^/leagues/NBA_{year}_games-[a-z0-9-]+\.html$", href)]
        if not month_hrefs:
            continue

        main_url = f"{BASE_URL}/leagues/NBA_{year}_games.html"
        url_to_file: dict[str, FixtureValue] = {main_url: index}
        if _add_schedule_months(year_dir, year, month_hrefs, url_to_file):
            params = {"season_end_year": year}
            cases.append(make_case("season_schedule", params, url_to_file))

    if cases:
        return cases, None
    return None, "no season_schedule year had a complete month set"


def _add_schedule_months(
    year_dir: Path,
    year: int,
    month_hrefs: list[str],
    url_to_file: dict[str, FixtureValue],
) -> bool:
    for href in month_hrefs:
        month_match = re.match(rf"^/leagues/NBA_{year}_games-([a-z0-9-]+)\.html$", href)
        if not month_match:
            return False
        month_file = year_dir / f"{month_match.group(1)}.html"
        if not month_file.is_file():
            return False
        url_to_file[BASE_URL + href] = month_file
    return True


def _resolve_standings_by_date() -> ResolveResult:
    raw_dir = RAW_ROOT / "standings_by_date"
    if not raw_dir.is_dir():
        return None, "no raw/standings_by_date/ directory"
    files = list_html(raw_dir)
    if not files:
        return None, "no raw/standings_by_date/ fixtures"

    by_year: dict[int, dict[str, Path]] = {}
    for path in files:
        match = re.match(r"^(\d{4})_(eastern|western)_conference$", path.stem)
        if not match:
            return None, f"unexpected filename '{path.name}' in standings_by_date"
        by_year.setdefault(int(match.group(1)), {})[match.group(2)] = path

    for year in sorted(by_year):
        conferences = by_year[year]
        if "eastern" not in conferences or "western" not in conferences:
            return None, f"missing conference file for year {year}"
        url_to_file: dict[str, FixtureValue] = {
            f"{BASE_URL}/leagues/NBA_{year}_standings_by_date_eastern_conference.html": conferences["eastern"],
            f"{BASE_URL}/leagues/NBA_{year}_standings_by_date_western_conference.html": conferences["western"],
        }
        params = {"season_end_year": year}
        return [make_case("standings_by_date", params, url_to_file)], None

    return None, "no complete year pair in standings_by_date"


def _resolve_search() -> ResolveResult:
    raw_dir = RAW_ROOT / "search"
    if not raw_dir.is_dir():
        return None, "no raw/search/ directory"
    files = list_html(raw_dir)
    if not files:
        return None, "no raw/search/ fixtures"

    cases: list[Case] = []
    for term, names in _search_fixture_chains(raw_dir, files):
        url_to_file: dict[str, FixtureValue] = {f"{BASE_URL}/search/search.fcgi?search={term}": raw_dir / names[0]}
        for i, name in enumerate(names[1:], start=1):
            offset = i * 100
            for idx in ("players", "wnba_players", "intl_players", "nbdl_players", "sup_players"):
                page_url = f"{BASE_URL}/search/search.fcgi?search={term}&idx={idx}&offset={offset}"
                url_to_file[page_url] = raw_dir / name
        cases.append(make_case("search", {"term": term}, url_to_file))

    return cases, None


def _search_fixture_chains(raw_dir: Path, files: list[Path]) -> list[tuple[str, list[str]]]:
    chains: list[tuple[str, list[str]]] = []
    seen_terms: set[str] = set()

    if (raw_dir / "jaebaebae.html").is_file():

        def _page_index(path: Path) -> int:
            match = re.search(r"\d+", path.stem)
            assert match is not None, f"ja_page file with no digits: {path.name}"
            return int(match.group(0))

        pages = sorted(raw_dir.glob("ja_page_*.html"), key=_page_index)
        chains.append(("jaebaebae", ["jaebaebae.html", *[path.name for path in pages]]))
        seen_terms.add("jaebaebae")

    for path in files:
        stem = path.stem
        if stem in seen_terms or re.search(r"_page_\d+$", stem):
            continue
        chains.append((stem, [path.name]))

    return chains
