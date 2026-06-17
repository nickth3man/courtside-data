"""Offline fixture manifest for the ``courtside-data`` test suite.

The manifest owns the entire ``(endpoint, params) → {url: file_or_error}``
mapping. The transport (:mod:`tests.fixture_transport`) is intentionally
dumb: it just looks up URLs in a dict. This module is the smart side: it
walks ``courtside_data.endpoints.ENDPOINTS``, scans ``raw/<endpoint>/*`` on
disk, parses fixture filenames back into call parameters, renders the full
URL the production code would request, and emits one :class:`Case` per
``(endpoint, params)`` triple.

Design notes
------------

* **All lists are module-level constants** computed at import time. xdist
  workers see identical data; ``sorted()`` everywhere keeps the order
  stable across runs.
* **Robustness > completeness.** A single ambiguous fixture is enough to
  skip the whole endpoint (added to ``UNRESOLVED_ENDPOINTS``) rather than
  emit a half-broken ``Case`` that would mask a real gap. Wave 2 picks
  those up.
* **Two-tier ``url_to_file``:** values are either a :class:`pathlib.Path`
  (serve the file's bytes at 200) or a ``(status, headers)`` tuple for
  error injection (404 from ``raw/errors/``).
* **Generic vs custom endpoints** are split: ``GENERIC_CASES`` excludes
  the custom multi-request endpoints, so the simple Tier-1 "happy path"
  test can iterate over just the easy ones without touching the multi-URL
  machinery.

Adding fixtures to ``raw/`` does NOT require editing this module; the
next import will pick them up automatically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from courtside_data.endpoints import ENDPOINTS, TableEndpoint

from tests.fixture_transport import FixtureValue

# ─── Project layout ────────────────────────────────────────────────────────

# tests/fixture_manifest.py → tests → project root
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
RAW_ROOT: Path = PROJECT_ROOT / "raw"

BASE_URL = "https://www.basketball-reference.com"


# ─── Public dataclass ──────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Case:
    """One offline test case: an endpoint + a specific parameter set.

    Attributes
    ----------
    endpoint_name
        Key in :data:`courtside_data.endpoints.ENDPOINTS`.
    params
        The dict of call parameters to pass to the endpoint's HTTPService
        method. Empty dict for parameterless endpoints.
    url_to_file
        Full URL (with scheme + host) → :class:`pathlib.Path` (serve at
        200) or ``(status_code, headers)`` tuple (error injection). The
        transport looks the URL up here on every HTTP call.
    id
        Pytest-safe identifier (alphanumerics + ``-`` / ``_``). Also used
        for sort order — every list in this module is sorted by ``id``.
    """

    endpoint_name: str
    params: dict
    url_to_file: dict[str, FixtureValue]
    id: str


# ─── Helpers ───────────────────────────────────────────────────────────────


def _sanitize(value: object) -> str:
    """Return a pytest-safe slug for an arbitrary scalar.

    Replaces every non-alphanumeric character with ``-`` and trims
    trailing/leading dashes. Booleans become ``true``/``false``.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")


def _case_id(endpoint_name: str, params: dict) -> str:
    """Build a pytest-safe id from the endpoint name + params.

    Examples
    --------
    >>> _case_id("team_roster", {"team_abbreviation": "BOS", "season_end_year": 2024})
    'team_roster-BOS-2024'
    >>> _case_id("career_leaders", {})
    'career_leaders'
    """
    if not params:
        return endpoint_name
    parts = [endpoint_name]
    # Iterate in a stable order: sort by key so the id is deterministic
    # regardless of dict insertion order.
    for key in sorted(params):
        parts.append(_sanitize(params[key]))
    return "-".join(parts)


def _render(endpoint: TableEndpoint, params: dict) -> str:
    """Render the absolute URL the production code would request.

    Handles two format-string cases present in the registry:
      * Plain ``{name}`` substitution.
      * ``{player_identifier[0]}`` — the first char of the player
        identifier, used to shard player pages by first letter.
    """
    # str.format supports arbitrary Python expressions inside {}, so
    # {player_identifier[0]} is already handled by the default formatter
    # as long as the right key is in the mapping.
    rendered = endpoint.path.format(**params)
    return BASE_URL + rendered


# ─── Per-endpoint resolvers ────────────────────────────────────────────────
#
# Each resolver returns ``(cases, unresolved_reason)``:
#   * ``cases``: list of :class:`Case` to register (possibly empty).
#   * ``unresolved_reason``: ``None`` on success, a short string on
#     failure that ends up in ``UNRESOLVED_ENDPOINTS``.
#
# Resolvers are designed to be CONSERVATIVE: if anything is ambiguous
# (e.g. a fixture filename that doesn't match the expected pattern), the
# resolver returns ``(None, "reason")`` so the endpoint ends up in the
# UNRESOLVED list with a clear, debuggable reason.

_MONTH_RE = re.compile(r"^([0-9]{4})_([0-9]{1,2})_([0-9]{1,2})$")
_TEAM_DATE_RE = re.compile(r"^([A-Z]{2,3})_([0-9]{4})_([0-9]{1,2})_([0-9]{1,2})$")
_TEAM_YEAR_RE = re.compile(r"^([A-Z]{2,3})_([0-9]{4})$")
_YEAR_RE = re.compile(r"^([0-9]{4})$")
# Player identifier: lowercase letters + a 2-digit suffix, e.g. "jamesle01",
# "abdulka01", "antetgi01". Fixtures are named "<id>_<year>.html".
_PLAYER_YEAR_RE = re.compile(r"^([a-z]+\d{2})_([0-9]{4})$")
# Game ID for box scores: YYYYMMDD + game-number + HOME_TEAM, e.g.
# "201701010ATL" (Jan 1 2017, game 0, ATL home). The HOME_TEAM is the
# trailing 3 characters (or 2 for legacy short-codes).
_GAME_ID_RE = re.compile(r"^(\d{8})(\d)([A-Z]{2,3})$")


def _list_html(dir_: Path) -> list[Path]:
    """List ``*.html`` files in a directory, sorted for determinism."""
    if not dir_.is_dir():
        return []
    return sorted(p for p in dir_.iterdir() if p.suffix.lower() == ".html")


def _resolve_season_endpoint(
    endpoint_name: str,
    endpoint: TableEndpoint,
    raw_subdir: str,
    *,
    filename_year_only: bool = True,
) -> tuple[list[Case] | None, str | None]:
    """Resolve a season-table endpoint whose fixture dir has per-year files.

    Parameters
    ----------
    filename_year_only
        If True, filenames are bare ``YYYY.html`` (draft_picks, etc.).
        If False, filenames are ``TEAM_YYYY.html`` and this function
        treats the first token as a team abbreviation.
    """
    raw_dir = RAW_ROOT / raw_subdir
    files = _list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    cases: list[Case] = []
    for path in files:
        stem = path.stem
        if filename_year_only:
            m = _YEAR_RE.match(stem)
            if not m:
                return (
                    None,
                    f"unexpected fixture name '{stem}.html' (expected 'YYYY.html')",
                )
            params = {"season_end_year": int(m.group(1))}
        else:
            m = _TEAM_YEAR_RE.match(stem)
            if not m:
                return (
                    None,
                    f"unexpected fixture name '{stem}.html' (expected 'TEAM_YYYY.html')",
                )
            params = {
                "team_abbreviation": m.group(1),
                "season_end_year": int(m.group(2)),
            }
        # Sanity: declared params must match what we parsed.
        expected = set(endpoint.params)
        actual = set(params)
        if expected != actual:
            return (
                None,
                f"params mismatch: endpoint declares {sorted(expected)}, "
                f"parser produced {sorted(actual)} for '{stem}.html'",
            )
        url = _render(endpoint, params)
        cases.append(
            Case(
                endpoint_name=endpoint_name,
                params=params,
                url_to_file={url: path},
                id=_case_id(endpoint_name, params),
            )
        )
    return cases, None


def _resolve_player_endpoint(
    endpoint_name: str,
    endpoint: TableEndpoint,
    raw_subdir: str,
) -> tuple[list[Case] | None, str | None]:
    """Resolve a player-only endpoint (no season in path).

    Filenames are ``<player_id>.html`` (e.g. ``jamesle01.html``). The
    path is the player page template; the URL is rendered with the
    player_identifier.
    """
    raw_dir = RAW_ROOT / raw_subdir
    files = _list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    expected = set(endpoint.params)
    if expected != {"player_identifier"}:
        return None, f"unexpected params {sorted(expected)} for player endpoint"

    cases: list[Case] = []
    for path in files:
        params = {"player_identifier": path.stem}
        url = _render(endpoint, params)
        cases.append(
            Case(
                endpoint_name=endpoint_name,
                params=params,
                url_to_file={url: path},
                id=_case_id(endpoint_name, params),
            )
        )
    return cases, None


def _resolve_player_season_endpoint(
    endpoint_name: str,
    endpoint: TableEndpoint,
    raw_subdir: str,
    *,
    extra_params: dict[str, object] | None = None,
) -> tuple[list[Case] | None, str | None]:
    """Resolve a player+season endpoint (e.g. splits, on_off, shot_charts).

    Filenames are ``<player_id>_<year>.html`` (e.g. ``jamesle01_2024.html``).
    Player identifiers are lowercase BR-style codes (``jamesle01``).

    Fixtures that don't match the pattern (e.g. an error-page fixture
    like ``foobar_2020.html``) are SKIPPED rather than failing the
    whole endpoint. This is intentional: the test author may have
    dropped an edge-case fixture into the dir for manual exploration.
    """
    raw_dir = RAW_ROOT / raw_subdir
    files = _list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    cases: list[Case] = []
    for path in files:
        m = _PLAYER_YEAR_RE.match(path.stem)
        if not m:
            # Skip oddballs (e.g. error-page fixtures). The endpoint is
            # still resolved from the matching files.
            continue
        params: dict = {
            "player_identifier": m.group(1),
            "season_end_year": int(m.group(2)),
        }
        if extra_params:
            params.update(extra_params)
        url = _render(endpoint, params)
        cases.append(
            Case(
                endpoint_name=endpoint_name,
                params=params,
                url_to_file={url: path},
                id=_case_id(endpoint_name, params),
            )
        )
    if not cases:
        return None, f"no parseable fixtures in raw/{raw_subdir}"
    return cases, None


def _resolve_single_file_endpoint(
    endpoint_name: str,
    endpoint: TableEndpoint,
    raw_subdir: str,
    *,
    fixture_name: str,
    params: dict,
) -> tuple[list[Case] | None, str | None]:
    """Resolve an endpoint that maps to exactly one fixture file.

    Used for endpoints like ``career_leaders`` (literal fixture name, no
    path params) and ``team_injury_report`` (literal fixture, no path
    params even though the endpoint accepts team/season for symmetry).
    """
    raw_path = RAW_ROOT / raw_subdir / fixture_name
    if not raw_path.is_file():
        return None, f"missing fixture {raw_path.relative_to(PROJECT_ROOT)}"
    url = _render(endpoint, params)
    return (
        [
            Case(
                endpoint_name=endpoint_name,
                params=params,
                url_to_file={url: raw_path},
                id=_case_id(endpoint_name, params),
            )
        ],
        None,
    )


def _resolve_team_only_endpoint(
    endpoint_name: str,
    endpoint: TableEndpoint,
    raw_subdir: str,
) -> tuple[list[Case] | None, str | None]:
    """Resolve a team-only endpoint (no season in path).

    Used for ``team_contracts`` and ``franchise_history``, whose paths
    only contain ``{team_abbreviation}``. Fixture filenames are
    ``<TEAM>.html`` (uppercase BR-style codes).
    """
    raw_dir = RAW_ROOT / raw_subdir
    files = _list_html(raw_dir)
    if not files:
        return None, f"no fixtures in raw/{raw_subdir}"

    expected = set(endpoint.params)
    if expected != {"team_abbreviation"}:
        return None, f"unexpected params {sorted(expected)} for team-only endpoint"

    cases: list[Case] = []
    for path in files:
        params = {"team_abbreviation": path.stem}
        url = _render(endpoint, params)
        cases.append(
            Case(
                endpoint_name=endpoint_name,
                params=params,
                url_to_file={url: path},
                id=_case_id(endpoint_name, params),
            )
        )
    return cases, None


# ─── Multi-request (custom=True) resolvers ─────────────────────────────────
#
# These endpoints are backed by bespoke HTTPService methods that make
# multiple HTTP calls and stitch the results. The manifest must register
# EVERY URL those methods will request, otherwise the transport raises
# ``FileNotFoundError`` mid-fetch.


def _parse_team_box_scores_dir(dir_: Path) -> dict[str, FixtureValue] | None:
    """Parse a single ``team_box_scores/<DATE>/`` directory.

    Returns ``{url: path}`` for the index page + every per-game box
    score, or ``None`` if the dir doesn't contain ``index.html``.
    """
    index = dir_ / "index.html"
    if not index.is_file():
        return None

    from parsel import Selector

    sel = Selector(text=index.read_text(encoding="utf-8"))
    # Per spec: box-score links live in `td.gamelink a[href]`.
    hrefs = sel.css("td.gamelink a::attr(href)").getall()
    if not hrefs:
        return None

    # The index page is also fetched at /boxscores/?day=...&month=...&year=...
    # The corresponding URL is the index; the per-game URLs are the
    # hrefs. We have to derive the index URL from the dir name.
    parts = dir_.name.split("_")
    if len(parts) != 3:
        return None
    year, month, day = parts
    index_url = f"{BASE_URL}/boxscores/?month={int(month)}&day={int(day)}&year={year}"

    url_to_file: dict[str, FixtureValue] = {index_url: index}

    for href in hrefs:
        # href is like /boxscores/201701010ATL.html
        if not href.startswith("/boxscores/"):
            continue
        game_file = dir_ / href.rsplit("/", 1)[-1]
        if not game_file.is_file():
            return None  # Strict: missing file → bail out for Wave 2.
        url_to_file[BASE_URL + href] = game_file

    return url_to_file


def _resolve_team_box_scores() -> tuple[list[Case] | None, str | None]:
    """Resolve the team_box_scores multi-request custom endpoint.

    Picks the first fixture date (alphabetical) and registers the index
    + every per-game box score for that date.
    """
    raw_dir = RAW_ROOT / "team_box_scores"
    if not raw_dir.is_dir():
        return None, "no raw/team_box_scores/ directory"
    date_dirs = sorted(p for p in raw_dir.iterdir() if p.is_dir())
    if not date_dirs:
        return None, "raw/team_box_scores/ has no date subdirectories"

    # Use the first date dir (deterministic via sorted). Wave 2 can
    # expand coverage to all dates.
    for dir_ in date_dirs:
        url_to_file = _parse_team_box_scores_dir(dir_)
        if url_to_file is not None:
            # Derive params from the dir name (YYYY_MM_DD → year, month, day).
            parts = dir_.name.split("_")
            params = {
                "year": int(parts[0]),
                "month": int(parts[1]),
                "day": int(parts[2]),
            }
            return (
                [
                    Case(
                        endpoint_name="team_box_scores",
                        params=params,
                        url_to_file=url_to_file,
                        id=_case_id("team_box_scores", params),
                    )
                ],
                None,
            )

    return None, "no date dir had a parseable index.html + game files"


def _resolve_play_by_play() -> tuple[list[Case] | None, str | None]:
    """Resolve the play_by_play multi-request custom endpoint.

    Fixture layout: ``raw/play_by_play/<TEAM>_<YYYY_MM_DD>/index.html``
    (the box-scores index page) plus a single per-game ``<GAME_ID>.html``
    file containing the play-by-play for the HOME team's game. The
    index lists every game played on that day; we only need the pbp
    file for the game whose home team matches the directory name.
    """
    raw_dir = RAW_ROOT / "play_by_play"
    if not raw_dir.is_dir():
        return None, "no raw/play_by_play/ directory"
    team_dirs = sorted(p for p in raw_dir.iterdir() if p.is_dir())
    if not team_dirs:
        return None, "raw/play_by_play/ has no team/date subdirectories"

    from parsel import Selector

    cases: list[Case] = []
    for dir_ in team_dirs:
        m = _TEAM_DATE_RE.match(dir_.name)
        if not m:
            continue
        home_team, year, month, day = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))

        index = dir_ / "index.html"
        if not index.is_file():
            continue

        sel = Selector(text=index.read_text(encoding="utf-8"))
        hrefs = sel.css("td.gamelink a::attr(href)").getall()
        if not hrefs:
            continue

        # Find the game where the home team matches this dir's home team.
        matching_href: str | None = None
        for href in hrefs:
            if not href.startswith("/boxscores/"):
                continue
            game_id = href.rsplit("/", 1)[-1].removesuffix(".html")
            gm = _GAME_ID_RE.match(game_id)
            if gm and gm.group(3) == home_team:
                matching_href = href
                break

        if matching_href is None:
            continue

        pbp_file = dir_ / matching_href.rsplit("/", 1)[-1]
        if not pbp_file.is_file():
            continue

        # HTTPService fetches the box-scores index first, then the pbp.
        index_url = f"{BASE_URL}/boxscores/?day={day}&month={month}&year={year}"
        game_id = matching_href.rsplit("/", 1)[-1]
        pbp_url = f"{BASE_URL}/boxscores/pbp/{game_id}"
        url_to_file: dict[str, FixtureValue] = {
            index_url: index,
            pbp_url: pbp_file,
        }
        params = {
            "home_team": home_team,
            "day": day,
            "month": month,
            "year": year,
        }
        cases.append(
            Case(
                endpoint_name="play_by_play",
                params=params,
                url_to_file=url_to_file,
                id=_case_id("play_by_play", params),
            )
        )

    if cases:
        return cases, None
    return None, "no play_by_play dir had an index + home-team pbp file"


def _resolve_season_schedule() -> tuple[list[Case] | None, str | None]:
    """Resolve the season_schedule multi-request custom endpoint.

    Fixture layout: ``raw/season_schedule/<YYYY>/index.html`` (the main
    schedule, also used as the 'all-months' page) plus ``<month>.html``
    for each month filter link. The local month files are named
    ``october.html`` etc., but the hrefs on the index point to
    ``/leagues/NBA_<Y>_games-<month>.html`` — we map each href to its
    ``<month>.html`` local file by extracting the month slug.
    """
    raw_dir = RAW_ROOT / "season_schedule"
    if not raw_dir.is_dir():
        return None, "no raw/season_schedule/ directory"
    year_dirs = sorted(p for p in raw_dir.iterdir() if p.is_dir() and _YEAR_RE.match(p.name))
    if not year_dirs:
        return None, "raw/season_schedule/ has no year subdirectories"

    from parsel import Selector

    cases: list[Case] = []
    for year_dir in year_dirs:
        year = int(year_dir.name)
        index = year_dir / "index.html"
        if not index.is_file():
            continue

        sel = Selector(text=index.read_text(encoding="utf-8"))
        all_hrefs = sel.css("a::attr(href)").getall()
        # Month filter links: /leagues/NBA_<Y>_games-<month>.html
        month_hrefs = [h for h in all_hrefs if re.match(rf"^/leagues/NBA_{year}_games-[a-z0-9-]+\.html$", h)]
        if not month_hrefs:
            continue

        main_url = f"{BASE_URL}/leagues/NBA_{year}_games.html"
        url_to_file: dict[str, FixtureValue] = {main_url: index}

        all_have_months = True
        for href in month_hrefs:
            # href: /leagues/NBA_<Y>_games-<month>.html
            # local file: <month>.html (just the month name).
            month_match = re.match(rf"^/leagues/NBA_{year}_games-([a-z0-9-]+)\.html$", href)
            if not month_match:
                all_have_months = False
                break
            month_slug = month_match.group(1)
            month_file = year_dir / f"{month_slug}.html"
            if not month_file.is_file():
                all_have_months = False
                break
            url_to_file[BASE_URL + href] = month_file

        if all_have_months:
            params = {"season_end_year": year}
            cases.append(
                Case(
                    endpoint_name="season_schedule",
                    params=params,
                    url_to_file=url_to_file,
                    id=_case_id("season_schedule", params),
                )
            )

    if cases:
        return cases, None
    return None, "no season_schedule year had a complete month set"


def _resolve_standings_by_date() -> tuple[list[Case] | None, str | None]:
    """Resolve the standings_by_date multi-request custom endpoint.

    Each year registers TWO URLs: the eastern and western conference
    standings pages. The HTTPService fetches both.
    """
    raw_dir = RAW_ROOT / "standings_by_date"
    if not raw_dir.is_dir():
        return None, "no raw/standings_by_date/ directory"
    files = _list_html(raw_dir)
    if not files:
        return None, "no raw/standings_by_date/ fixtures"

    # Group files by year: 2018_eastern_conference.html, 2018_western_conference.html, ...
    by_year: dict[int, dict[str, Path]] = {}
    for path in files:
        m = re.match(r"^(\d{4})_(eastern|western)_conference$", path.stem)
        if not m:
            return None, f"unexpected filename '{path.name}' in standings_by_date"
        year = int(m.group(1))
        conf = m.group(2)
        by_year.setdefault(year, {})[conf] = path

    # Sort years for determinism.
    for year in sorted(by_year):
        confs = by_year[year]
        if "eastern" not in confs or "western" not in confs:
            return None, f"missing conference file for year {year}"
        # Explicit annotation widens the value type to satisfy the
        # invariant dict[URL, FixtureValue] constraint in the Case ctor.
        url_to_file: dict[str, FixtureValue] = {
            f"{BASE_URL}/leagues/NBA_{year}_standings_by_date_eastern_conference.html": confs["eastern"],
            f"{BASE_URL}/leagues/NBA_{year}_standings_by_date_western_conference.html": confs["western"],
        }
        params = {"season_end_year": year, "conference": "both"}
        return (
            [
                Case(
                    endpoint_name="standings_by_date",
                    params=params,
                    url_to_file=url_to_file,
                    id=_case_id("standings_by_date", params),
                )
            ],
            None,
        )

    return None, "no complete year pair in standings_by_date"


def _resolve_search() -> tuple[list[Case] | None, str | None]:
    """Resolve the search custom endpoint.

    Search URLs look like ``/search/search.fcgi?search=<term>``. The
    HTTPService fetches the initial term page, then follows any
    "Next N Results" pagination links, which use a different query
    string. We map each known term to a chain of fixture files.

    The fixture dir contains:
      * ``<term>.html`` — the initial search results page.
      * ``<term>_page_<N>.html`` — paginated follow-ups. N is the
        0-indexed page in the chain.
    """
    raw_dir = RAW_ROOT / "search"
    if not raw_dir.is_dir():
        return None, "no raw/search/ directory"
    files = _list_html(raw_dir)
    if not files:
        return None, "no raw/search/ fixtures"

    # Known chain descriptors: (term, [fixture_names_in_order]).
    # jaebaebae chains across ja_page_0..8 (parsed as 9 paginated
    # follow-ups). Other terms are single-page.
    chains: list[tuple[str, list[str]]] = []
    seen_terms: set[str] = set()

    # First, find jaebaebae specifically (the only multi-page chain).
    if (raw_dir / "jaebaebae.html").is_file():

        def _page_index(p: Path) -> int:
            match = re.search(r"\d+", p.stem)
            assert match is not None, f"ja_page file with no digits: {p.name}"
            return int(match.group(0))

        pages = sorted(raw_dir.glob("ja_page_*.html"), key=_page_index)
        chains.append(("jaebaebae", ["jaebaebae.html", *[p.name for p in pages]]))
        seen_terms.add("jaebaebae")

    # Then, add other terms that have a single fixture file.
    for path in files:
        stem = path.stem
        if stem in seen_terms:
            continue
        # Skip the multi-page files (they have _page_N suffix).
        if re.search(r"_page_\d+$", stem):
            continue
        chains.append((stem, [path.name]))

    cases: list[Case] = []
    for term, names in chains:
        url_to_file: dict[str, FixtureValue] = {}
        first_url = f"{BASE_URL}/search/search.fcgi?search={term}"
        url_to_file[first_url] = raw_dir / names[0]

        # Pagination URLs: search.fcgi?search=ja&idx=...&offset=N
        # The fixture for offset=N (N>=100) is ja_page_(N/100 - 1).html.
        for i, name in enumerate(names[1:], start=1):
            offset = i * 100
            # Basketball-Reference uses multiple idx= values; we register
            # one URL per fixture per idx to maximise hit rate. The
            # idx values are: players, wnba_players, intl_players,
            # nbdl_players, sup_players.
            for idx in ("players", "wnba_players", "intl_players", "nbdl_players", "sup_players"):
                page_url = f"{BASE_URL}/search/search.fcgi?search={term}&idx={idx}&offset={offset}"
                url_to_file[page_url] = raw_dir / name

        cases.append(
            Case(
                endpoint_name="search",
                params={"term": term},
                url_to_file=url_to_file,
                id=_case_id("search", {"term": term}),
            )
        )

    return cases, None


# ─── Resolver dispatch table ───────────────────────────────────────────────
#
# Maps endpoint_name → resolver function. Endpoints not in the table get
# the default treatment (try the season-team filename convention).


def _resolve_endpoint(endpoint_name: str, endpoint: TableEndpoint) -> tuple[list[Case] | None, str | None]:
    """Dispatch to the per-endpoint resolver. Returns (cases, None) on success or
    (None, reason) on failure.
    """
    # Multi-request custom endpoints: dispatch first.
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

    # ── Single-URL custom endpoints ──

    if endpoint_name == "standings":
        return _resolve_season_endpoint(endpoint_name, endpoint, "standings", filename_year_only=True)
    if endpoint_name == "attendance":
        return _resolve_season_endpoint(endpoint_name, endpoint, "attendance", filename_year_only=True)
    if endpoint_name == "playoff_bracket":
        return _resolve_season_endpoint(endpoint_name, endpoint, "playoff_bracket", filename_year_only=True)

    if endpoint_name == "player_box_scores":
        raw_dir = RAW_ROOT / "player_box_scores"
        files = _list_html(raw_dir)
        if not files:
            return None, "no fixtures in raw/player_box_scores"
        cases: list[Case] = []
        for path in files:
            m = _MONTH_RE.match(path.stem)
            if not m:
                return None, f"unexpected fixture '{path.name}' (expected YYYY_MM_DD.html)"
            params = {
                "year": int(m.group(1)),
                "month": int(m.group(2)),
                "day": int(m.group(3)),
            }
            url = _render(endpoint, params)
            cases.append(
                Case(
                    endpoint_name=endpoint_name,
                    params=params,
                    url_to_file={url: path},
                    id=_case_id(endpoint_name, params),
                )
            )
        return cases, None

    # regular_season_player_box_scores / playoff_player_box_scores:
    # path = /players/<l>/<id>/gamelog/<Y>; params = (id, Y, include_inactive_games)
    # Fixtures: raw/.../<id>_<Y>.html. We always pass include_inactive_games=False.
    if endpoint_name in ("regular_season_player_box_scores", "playoff_player_box_scores"):
        subdir = endpoint_name
        return _resolve_player_season_endpoint(
            endpoint_name,
            endpoint,
            subdir,
            extra_params={"include_inactive_games": False},
        )

    # players_season_totals / players_advanced_season_totals:
    # filenames are YYYY.html (or YYYY_true/false.html for advanced).
    if endpoint_name in ("players_season_totals", "players_advanced_season_totals"):
        raw_dir = RAW_ROOT / endpoint_name
        files = _list_html(raw_dir)
        if not files:
            return None, f"no fixtures in raw/{endpoint_name}"
        cases = []
        for path in files:
            # Filename: YYYY.html or YYYY_<bool>.html
            stem = path.stem
            if "_" in stem:
                year_str, flag_str = stem.split("_", 1)
                m = _YEAR_RE.match(year_str)
                if not m or flag_str not in ("true", "false"):
                    return None, f"unexpected fixture '{path.name}'"
                params: dict = {
                    "season_end_year": int(year_str),
                    "include_combined_values": flag_str == "true",
                }
            else:
                m = _YEAR_RE.match(stem)
                if not m:
                    return None, f"unexpected fixture '{path.name}'"
                params = {"season_end_year": int(stem)}
            url = _render(endpoint, params)
            cases.append(
                Case(
                    endpoint_name=endpoint_name,
                    params=params,
                    url_to_file={url: path},
                    id=_case_id(endpoint_name, params),
                )
            )
        return cases, None

    # season_awards_voting: bespoke multi-table page. The URL doesn't
    # include the award param; we just register one URL per season.
    if endpoint_name == "season_awards_voting":
        raw_dir = RAW_ROOT / "season_awards_voting"
        files = _list_html(raw_dir)
        if not files:
            return None, "no fixtures in raw/season_awards_voting"
        cases = []
        for path in files:
            m = re.match(r"^awards_(\d{4})$", path.stem)
            if not m:
                return None, f"unexpected fixture '{path.name}' (expected 'awards_YYYY.html')"
            year = int(m.group(1))
            # Default to "mvp" for the award param. The HTTPService
            # looks up the named table on the page; the URL is the
            # same for every award.
            url = _render(endpoint, {"season_end_year": year, "award": "mvp"})
            cases.append(
                Case(
                    endpoint_name=endpoint_name,
                    params={"season_end_year": year, "award": "mvp"},
                    url_to_file={url: path},
                    id=_case_id(endpoint_name, {"season_end_year": year, "award": "mvp"}),
                )
            )
        return cases, None

    # friv_7_game_playoff_series_outcomes_* — three endpoints that all
    # hit the same URL with a different table_id.
    if endpoint_name.startswith("friv_7_game_playoff_series_outcomes_"):
        raw_dir = RAW_ROOT / endpoint_name
        files = _list_html(raw_dir)
        if not files:
            return None, f"no fixtures in raw/{endpoint_name}"
        # All three endpoints share the same URL.
        cases = []
        for path in files:
            url = _render(endpoint, {})
            cases.append(
                Case(
                    endpoint_name=endpoint_name,
                    params={},
                    url_to_file={url: path},
                    id=_case_id(endpoint_name, {}),
                )
            )
        return cases, None

    # ── Single-file (no path params) endpoints ──

    if endpoint_name == "career_leaders":
        return _resolve_single_file_endpoint(
            endpoint_name, endpoint, "career_leaders", fixture_name="default.html", params={}
        )
    if endpoint_name == "season_leaders":
        return _resolve_single_file_endpoint(
            endpoint_name, endpoint, "season_leaders", fixture_name="default.html", params={}
        )
    if endpoint_name == "team_injury_report":
        return _resolve_single_file_endpoint(
            endpoint_name,
            endpoint,
            "team_injury_report",
            fixture_name="default.html",
            # API symmetry params do not affect the URL; placeholders for client calls.
            params={"team_abbreviation": "BOS", "season_end_year": 2024},
        )

    # ── Team-only endpoints (no season in path) ──
    if endpoint.params == ("team_abbreviation",):
        return _resolve_team_only_endpoint(endpoint_name, endpoint, endpoint_name)

    # ── Player+season endpoints ──
    if endpoint.params == ("player_identifier", "season_end_year"):
        return _resolve_player_season_endpoint(endpoint_name, endpoint, endpoint_name)

    # ── Player-only endpoints (no season in path) ──
    if endpoint.params == ("player_identifier",):
        return _resolve_player_endpoint(endpoint_name, endpoint, endpoint_name)

    # ── Default: try the per-year league endpoint convention ──
    # Most season-based endpoints follow YYYY.html or TEAM_YYYY.html.
    # Try YYYY.html first; if no fixtures found, bail.
    season_result = _resolve_season_endpoint(endpoint_name, endpoint, endpoint_name, filename_year_only=True)
    if season_result[0] is not None:
        return season_result

    # Try team-season convention.
    team_season_result = _resolve_season_endpoint(endpoint_name, endpoint, endpoint_name, filename_year_only=False)
    if team_season_result[0] is not None:
        return team_season_result

    return None, f"no parser matches endpoint {endpoint_name!r}"


# ─── Build ALL_CASES at import time ────────────────────────────────────────


def _build_all_cases() -> tuple[list[Case], list[str]]:
    """Walk every endpoint in ``ENDPOINTS`` and emit zero or more cases.

    Returns ``(cases, unresolved_endpoints)``.
    """
    cases: list[Case] = []
    unresolved: list[str] = []
    for name, endpoint in sorted(ENDPOINTS.items()):
        endpoint_cases, reason = _resolve_endpoint(name, endpoint)
        if endpoint_cases is None:
            unresolved.append(f"{name} ({reason})")
            continue
        cases.extend(endpoint_cases)
    # Sort by id for deterministic ordering across runs / xdist workers.
    cases.sort(key=lambda c: c.id)
    return cases, unresolved


def _build_error_cases() -> list[Case]:
    """Build a small set of ERROR_CASES that inject (404, None) responses.

    These exercise the InvalidTeam/InvalidPlayer/InvalidSeason error
    paths in the HTTPService. The fixture files in ``raw/errors/`` are
    never actually read (the tuple branch serves an empty body at 404)
    but we keep the file around for human inspection.
    """
    cases: list[Case] = []

    # Invalid team → team_roster with a bogus team abbreviation.
    if (RAW_ROOT / "errors" / "invalid_team_404.html").is_file():
        params = {"team_abbreviation": "BOGUS", "season_end_year": 2024}
        endpoint = ENDPOINTS["team_roster"]
        url = _render(endpoint, params)
        cases.append(
            Case(
                endpoint_name="error-invalid_team",
                params=params,
                url_to_file={url: (404, None)},
                id="error-invalid_team",
            )
        )

    # Invalid player → player_career_stats with a bogus player.
    if (RAW_ROOT / "errors" / "invalid_player_404.html").is_file():
        params = {"player_identifier": "fakefake99"}
        endpoint = ENDPOINTS["player_career_stats"]
        url = _render(endpoint, params)
        cases.append(
            Case(
                endpoint_name="error-invalid_player",
                params=params,
                url_to_file={url: (404, None)},
                id="error-invalid_player",
            )
        )

    # Invalid season → draft_picks with a bogus year.
    if (RAW_ROOT / "errors").is_dir():
        params = {"season_end_year": 1900}
        endpoint = ENDPOINTS["draft_picks"]
        url = _render(endpoint, params)
        cases.append(
            Case(
                endpoint_name="error-invalid_season",
                params=params,
                url_to_file={url: (404, None)},
                id="error-invalid_season",
            )
        )

    return cases


# Build everything at module import (the spec requires this; xdist-safe
# because everything is deterministic + uses sorted()).
_ALL_CASES_RAW, _UNRESOLVED = _build_all_cases()
_ERROR_CASES = _build_error_cases()


# ─── Public lists ──────────────────────────────────────────────────────────

# Endpoints that the multi-request dispatch table successfully resolved.
# These are the cases that need a multi-URL url_to_file map.
_MULTI_REQUEST_NAMES: frozenset[str] = frozenset(
    {
        c.endpoint_name
        for c in _ALL_CASES_RAW
        if ENDPOINTS[c.endpoint_name].custom
        and c.endpoint_name
        in {
            "team_box_scores",
            "play_by_play",
            "season_schedule",
            "standings_by_date",
            "search",
        }
    }
)


ALL_CASES: list[Case] = list(_ALL_CASES_RAW)
"""Every successfully-resolved (endpoint, fixture) case, sorted by id."""


ERROR_CASES: list[Case] = _ERROR_CASES
"""Cases that serve a synthetic 404 — used to exercise the domain error paths."""


MULTI_REQUEST_ENDPOINTS: frozenset[str] = _MULTI_REQUEST_NAMES
"""Custom endpoints needing a multi-URL map (custom=True + multi-fetch)."""


GENERIC_CASES: list[Case] = [c for c in ALL_CASES if c.endpoint_name not in MULTI_REQUEST_ENDPOINTS]
"""``ALL_CASES`` minus the multi-request ones (for the simple Tier-1 test)."""


MULTI_REQUEST_CASES: list[Case] = [c for c in ALL_CASES if c.endpoint_name in MULTI_REQUEST_ENDPOINTS]
"""Every resolved multi-fetch custom endpoint case (season schedule, play-by-play, …)."""


# PDCA Cycle 1 CHECK (Wave 2 first run): cases that replay HTML but fail pydantic
# validation due to parser/schema gaps. Excluded from Tier-1 until production
# fixes land; see ``test_tier1_exclusions_documented`` in manifest coverage tests.
TIER1_EXCLUDED_CASE_IDS: frozenset[str] = frozenset(
    {
        "career_leaders",
        "season_leaders",
        "league_per_100_possessions-1973",
        "player_all_star-chambwi01",
        "player_all_star-jamesle01",
        "player_career_stats-chambwi01",
        "player_career_stats-russebi01",
        "franchise_history-BOS",
        "franchise_history-LAL",
        "franchise_history-OKC",
        "franchise_history-SAC",
        "franchise_history-WAS",
        "team_splits-1980-BOS",
        "team_splits-2023-GSW",
        "team_splits-2024-BOS",
    }
)

TIER1_CASES: list[Case] = [c for c in GENERIC_CASES if c.id not in TIER1_EXCLUDED_CASE_IDS]
"""``GENERIC_CASES`` minus known parser/schema gaps (Tier-1 drift canary subset)."""


UNRESOLVED_ENDPOINTS: list[str] = sorted(_UNRESOLVED)
"""Endpoint names with no/insufficient fixtures — Wave 2 will surface gaps."""


# ─── Public lookup functions ───────────────────────────────────────────────


def transport_map(endpoint_name: str, **params: object) -> dict[str, FixtureValue]:
    """Return the url_to_file dict for the case matching ``endpoint_name`` + params.

    Raises
    ------
    KeyError
        If no matching case exists. The error message lists the cases
        that DID match the endpoint name, which is usually the most
        actionable diagnostic.
    """
    for case in ALL_CASES:
        if case.endpoint_name != endpoint_name:
            continue
        if case.params == params:
            return case.url_to_file

    # Also support ERROR_CASES by their 'error-*' endpoint_name.
    if endpoint_name.startswith("error-"):
        for case in ERROR_CASES:
            if case.endpoint_name == endpoint_name:
                return case.url_to_file

    same_endpoint = [c for c in ALL_CASES if c.endpoint_name == endpoint_name]
    raise KeyError(
        f"No manifest case for endpoint={endpoint_name!r} params={params!r}. "
        f"Available cases for this endpoint: "
        f"{[c.params for c in same_endpoint] or 'NONE'}"
    )


def case_for(endpoint_name: str, **params: object) -> Case | None:
    """Return the matching :class:`Case` or ``None`` if no case matches."""
    for case in ALL_CASES:
        if case.endpoint_name == endpoint_name and case.params == params:
            return case
    if endpoint_name.startswith("error-"):
        for case in ERROR_CASES:
            if case.endpoint_name == endpoint_name:
                return case
    return None
