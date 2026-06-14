#!/usr/bin/env python3
"""Download a raw HTML corpus from basketball-reference.com.

This script populates ``./raw/`` with representative full-HTML examples for
every endpoint declared in ``courtside_data.endpoints`` AND for every in-scope
page family listed in the BREF inventory CSV
(``docs/bref_new_page_families.csv``). It uses the project's own
``HTTPService`` so it inherits rate limiting, retry, jail detection, and TLS
impersonation. Run it with conservative settings and never in parallel.

CSV page families are written to ``raw/{page_family}/sample.html`` with the same
directory layout and duplicate-skip logic as ENDPOINTS examples. Because their
table ids are unknown up front, they are fetched with ``table_ids=()`` — so
every URL downloads regardless of how many tables it contains; the tables that
ARE present are discovered (visible + comment-wrapped) and recorded in the
sidecar under ``discovered_table_ids``.

Examples
--------
    # 10-request pilot (recommended before any full run)
    python -m scripts.raw_download --pilot

    # Full corpus download (ENDPOINTS + CSV page families)
    python -m scripts.raw_download

    # Resume from an interrupted run (already-present files are skipped)
    python -m scripts.raw_download

    # Only fetch the CSV page families
    python -m scripts.raw_download --csv-only

    # ENDPOINTS corpus only (skip CSV page families)
    python -m scripts.raw_download --no-csv

Environment variables
---------------------
BASKETBALL_REF_RATE_LIMIT_INTERVAL
    Seconds between requests (default 6.0 for ENDPOINTS rows).
BASKETBALL_REF_RATE_LIMIT_JITTER
    Extra random seconds up to this value (default 2.0).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import logging
import os
import re
import sys
import time
import zlib
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote_plus, urlsplit

import httpx
from lxml import html

# Make repo root importable regardless of cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from courtside_data.endpoints import ENDPOINTS, TableEndpoint  # noqa: E402
from courtside_data.errors import RateLimitJailed  # noqa: E402
from courtside_data.http_service import HTTPService, build_client  # noqa: E402

logger = logging.getLogger("raw_download")

DEFAULT_OUTPUT_ROOT = Path("raw")
DEFAULT_RATE_LIMIT_INTERVAL = 6.0
DEFAULT_RATE_LIMIT_JITTER = 2.0
DEFAULT_CACHE = True  # hishel SyncCacheTransport handles gzip decompression
MIN_BODY_BYTES = 1024
BASE_URL = "https://www.basketball-reference.com"
BLOCKED_MARKERS = (
    b"Rate Limited Request",
    b"Bot/Scraping/Crawler Traffic",
    b"Too Many Requests",
)
TOOL_NAME = "courtside-data:5.0.0a1"
DEFAULT_CSV_PATH = Path("docs/bref_new_page_families.csv")
BREF_BASE_URL = "https://www.basketball-reference.com/"
# P1_duplicate CSV rows that are still in scope (need table-id discovery).
_SCOPED_P1_DUPLICATE_FAMILIES = frozenset({"season_awards_voting", "friv_upcoming_milestones"})


class RawDownloadError(RuntimeError):
    """Raised when the download cannot continue safely."""


@dataclass(frozen=True)
class FetchTask:
    """One URL to fetch and where to store it."""

    url: str
    relative_path: Path
    table_ids: tuple[str, ...] = ()
    allowed_statuses: tuple[int, ...] = (200,)


@dataclass(frozen=True)
class ResponseSnapshot:
    """Observability snapshot captured when validation fails."""

    url: str
    final_url: str
    status_code: int
    content_encoding: str | None
    content_type: str | None
    body_bytes: int
    is_gzip: bool
    title: str | None
    first_kilobyte_preview: str


@dataclass(frozen=True)
class RawExample:
    """A single example for an endpoint; may require several HTML files."""

    endpoint: str
    example_id: str
    params: dict[str, Any]
    tasks: tuple[FetchTask, ...]


@dataclass
class FetchResult:
    task: FetchTask
    output_path: Path
    metadata_path: Path
    status_code: int
    byte_count: int
    sha256: str
    wallclock_ms: int
    attempts: int = 1
    retry_after_seen: int | None = None
    skipped: bool = False
    discovered_table_ids: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Catalog builders
# ---------------------------------------------------------------------------


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


def _endpoint_path(endpoint_name: str, **params: Any) -> str:
    endpoint = ENDPOINTS[endpoint_name]
    return endpoint.path.format(**params)


def _player_path(player_identifier: str, suffix: str = "") -> str:
    first = player_identifier[0]
    if suffix:
        return f"/players/{first}/{player_identifier}/{suffix}"
    return f"/players/{first}/{player_identifier}.html"


def _generic_example(
    endpoint_name: str,
    example_id: str,
    params: dict[str, Any],
    table_ids: tuple[str, ...] | None = None,
    allowed_statuses: tuple[int, ...] = (200,),
) -> RawExample:
    endpoint = ENDPOINTS[endpoint_name]
    path = endpoint.path.format(**params)
    # All corpus pages are HTML; always emit the documented .html extension
    # regardless of the URL path ending (avoids dropping it for paths that end
    # in a year digit, a query string, or an unrecognised extension like .fcgi).
    file_name = f"{example_id}.html"
    # Transaction-list endpoints have no table id; the parser uses <ul> lists.
    resolved_table_ids = (
        ()
        if endpoint.transaction_list_fallback
        else (_endpoint_table_ids(endpoint, params) if table_ids is None else table_ids)
    )
    return RawExample(
        endpoint=endpoint_name,
        example_id=example_id,
        params=params,
        tasks=(
            FetchTask(
                url=_url(path),
                relative_path=Path(endpoint_name) / file_name,
                table_ids=resolved_table_ids,
                allowed_statuses=allowed_statuses,
            ),
        ),
    )


def _endpoint_table_ids(endpoint: TableEndpoint, params: dict[str, Any]) -> tuple[str, ...]:
    ids: list[str] = []
    if endpoint.table_id is not None:
        ids.append(endpoint.table_id.format(**params))
    if endpoint.commented_table_id is not None:
        ids.append(endpoint.commented_table_id.format(**params))
    for fallback_id in endpoint.fallback_table_ids:
        ids.append(fallback_id.format(**params))
    return tuple(ids)


def _static_example(endpoint_name: str, example_id: str = "default") -> RawExample:
    endpoint = ENDPOINTS[endpoint_name]
    return _generic_example(endpoint_name, example_id, {}, _endpoint_table_ids(endpoint, {}))


# ---------------------------------------------------------------------------
# Full catalog: 2 examples per endpoint
# ---------------------------------------------------------------------------


def _build_season_schedule_example(season: int) -> RawExample:
    """Build a season_schedule example by discovering month pages dynamically.

    Fetches the main schedule page and extracts month links so only
    months that actually exist are included.  This avoids 404s for
    seasons with truncated calendars (e.g. 1980 has no June, 2012
    lockout has no October/November).
    """
    url = f"{BASE_URL}/leagues/NBA_{season}_games.html"
    client = build_client(cache=True)
    try:
        response = client.get(url)
        response.raise_for_status()
        document = html.fromstring(_decompress_if_needed(response.content))

        tasks: list[FetchTask] = [
            FetchTask(
                url=url,
                relative_path=Path("season_schedule") / str(season) / "index.html",
                table_ids=("schedule",),
            )
        ]

        for link in document.cssselect('div#content div.filter div:not([class*="current"]) a'):
            href = link.attrib.get("href", "")
            if "games-" in href:
                month_name = href.split("games-")[-1].removesuffix(".html")
                tasks.append(
                    FetchTask(
                        url=f"{BASE_URL}{href}",
                        relative_path=Path("season_schedule") / str(season) / f"{month_name}.html",
                        table_ids=("schedule",),
                    )
                )

        return RawExample(
            endpoint="season_schedule",
            example_id=str(season),
            params={"season_end_year": season},
            tasks=tuple(tasks),
        )
    finally:
        client.close()


def _build_team_box_scores_example(year: int, month: int, day: int) -> RawExample:
    """Build a team_box_scores example by discovering that day's games dynamically.

    ``team_box_scores`` reads the daily index and fetches *every* gamelink it
    lists, so the corpus must contain the index plus one page per game played
    that day — otherwise a mocked run would request an un-mocked URL.
    """
    example_id = f"{year}_{month:02d}_{day:02d}"
    index_url = f"{BASE_URL}/boxscores/?day={day}&month={month}&year={year}"
    client = build_client(cache=True)
    try:
        response = client.get(index_url)
        response.raise_for_status()
        document = html.fromstring(_decompress_if_needed(response.content))
        tasks: list[FetchTask] = [
            FetchTask(
                url=index_url,
                relative_path=Path("team_box_scores") / example_id / "index.html",
                table_ids=(),
            )
        ]
        for link in document.cssselect("td.gamelink a"):
            href = link.attrib.get("href", "")
            game_id = href.rstrip("/").rsplit("/", 1)[-1].removesuffix(".html")
            if game_id:
                tasks.append(
                    FetchTask(
                        url=f"{BASE_URL}/boxscores/{game_id}.html",
                        relative_path=Path("team_box_scores") / example_id / f"{game_id}.html",
                        table_ids=(),
                    )
                )
        return RawExample(
            endpoint="team_box_scores",
            example_id=example_id,
            params={"day": day, "month": month, "year": year},
            tasks=tuple(tasks),
        )
    finally:
        client.close()


def _build_integration_test_examples() -> list[RawExample]:
    """Examples the integration test-suite asserts on that the curated catalog omits.

    Added so ``tests/integration/client`` can read fixtures straight from the
    committed ``raw/`` corpus. Seasons/games already present in the curated
    catalog are intentionally excluded here (re-fetching them would be a no-op
    skip). A handful of these (search ``ja`` pagination, the 2018-01-01 game
    set) are content/time-coupled and their assertions are re-baselined after
    download.
    """
    examples: list[RawExample] = []

    # players_season_totals — every asserted season except 2018 (already curated).
    for year in (*range(2001, 2018), 2019):
        examples.append(
            _generic_example("players_season_totals", str(year), {"season_end_year": year}, ("totals_stats",))
        )

    # players_advanced_season_totals — asserted seasons except 2019 (curated).
    for year, combined in ((2001, False), (2016, True), (2017, True), (2018, False)):
        examples.append(
            _generic_example(
                "players_advanced_season_totals",
                f"{year}_{str(combined).lower()}",
                {"season_end_year": year, "include_combined_values": combined},
                ("advanced",),
            )
        )

    # standings — asserted seasons (none overlap the curated 2010/2021/2024 set).
    for year in (2000, 2001, 2002, 2005, 2019, 2020):
        examples.append(
            _generic_example(
                "standings", str(year), {"season_end_year": year}, ("divs_standings_E", "divs_standings_W")
            )
        )

    # season_schedule 2001 (2018 already curated; 2026 stays a synthetic not-found fixture).
    examples.append(_build_season_schedule_example(2001))

    # player daily box scores — 2001-01-01 (client test) plus the dates the
    # legacy parser tests assert on (2017-12-12 is already curated).
    daily_box_score_dates = [
        ("2001_01_01", 1, 1, 2001),
        ("2003_11_03", 3, 11, 2003),
        ("2006_11_01", 1, 11, 2006),
        ("2015_12_18", 18, 12, 2015),
        ("2017_01_29", 29, 1, 2017),
    ]
    for example_id, day, month, year in daily_box_score_dates:
        examples.append(
            _generic_example("player_box_scores", example_id, {"day": day, "month": month, "year": year}, ("stats",))
        )

    # play-by-play — the integration suite only reads the pbp game page (it stubs
    # the daily index inline), so fetch the pbp page alone. TOR_2003 is curated.
    pbp_games = [
        ("ATL_1999_11_16", "199911160ATL"),
        ("MIL_2018_10_27", "201810270MIL"),
        ("DEN_2019_01_01", "201901010DEN"),
        ("SAC_2019_01_01", "201901010SAC"),
        ("GSW_2018_10_16", "201810160GSW"),
    ]
    for example_id, game_id in pbp_games:
        examples.append(
            RawExample(
                endpoint="play_by_play",
                example_id=example_id,
                params={"game_id": game_id},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/boxscores/pbp/{game_id}.html",
                        relative_path=Path("play_by_play") / example_id / f"{game_id}.html",
                        table_ids=("pbp",),
                    ),
                ),
            )
        )

    # team box scores — 2018-01-01 (index + every game that day, discovered live).
    examples.append(_build_team_box_scores_example(2018, 1, 1))

    # player gamelogs (regular + playoff). Reg/playoff share the gamelog URL, so
    # duplicate (player, season) pairs are served from cache on the second fetch.
    gamelogs = [
        ("regular_season_player_box_scores", "brownja01", 2015, "player_game_log_reg"),
        ("regular_season_player_box_scores", "bradlav01", 2019, "player_game_log_reg"),
        ("regular_season_player_box_scores", "westbru01", 2020, "player_game_log_reg"),
        ("playoff_player_box_scores", "westbru01", 2019, "player_game_log_post"),
        ("playoff_player_box_scores", "westbru01", 2020, "player_game_log_post"),
        ("playoff_player_box_scores", "antetgi01", 2020, "player_game_log_post"),
    ]
    for endpoint_name, player_id, year, table_id in gamelogs:
        examples.append(
            _generic_example(
                endpoint_name,
                f"{player_id}_{year}",
                {"player_identifier": player_id, "season_end_year": year, "include_inactive_games": False},
                (table_id,),
            )
        )
    # Invalid-player gamelog (404/500) for the error-path test.
    examples.append(
        RawExample(
            endpoint="regular_season_player_box_scores",
            example_id="foobar_2020",
            params={"player_identifier": "foobar", "season_end_year": 2020},
            tasks=(
                FetchTask(
                    url=f"{BASE_URL}/players/f/foobar/gamelog/2020",
                    relative_path=Path("regular_season_player_box_scores") / "foobar_2020.html",
                    table_ids=(),
                    allowed_statuses=(200, 404, 500),
                ),
            ),
        )
    )

    # Search — single-match terms (may redirect to a player page), a no-result
    # term, and the "ja" pagination pages 2-8 (pages 0-1 are curated).
    search_terms = [
        ("kobe_bryant", "kobe bryant"),
        ("alonzo_mourning", "Alonzo Mourning"),
        ("dominique_wilkins", "Dominique Wilkins"),
        ("rick_barry", "Rick Barry"),
        ("jaebaebae", "jaebaebae"),
    ]
    for example_id, term in search_terms:
        examples.append(
            RawExample(
                endpoint="search",
                example_id=example_id,
                params={"term": term},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/search/search.fcgi?search={quote_plus(term)}",
                        relative_path=Path("search") / f"{example_id}.html",
                        table_ids=(),
                        allowed_statuses=(200,),
                    ),
                ),
            )
        )
    for offset in (200, 300, 400, 500, 600, 700, 800):
        examples.append(
            RawExample(
                endpoint="search",
                example_id=f"ja_page_{offset // 100}",
                params={"term": "ja", "offset": offset},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/search/search.fcgi?search=ja&i=players&offset={offset}",
                        relative_path=Path("search") / f"ja_page_{offset // 100}.html",
                        table_ids=(),
                    ),
                ),
            )
        )

    return examples


def build_catalog() -> tuple[RawExample, ...]:
    """Return the curated raw-HTML example catalog."""
    examples: list[RawExample] = []

    # ── League-wide season tables ──
    examples.extend(
        [
            _generic_example("league_per_game_stats", "2024", {"season_end_year": 2024}),
            _generic_example("league_per_game_stats", "2010", {"season_end_year": 2010}),
            _generic_example("league_per_36_minutes", "2024", {"season_end_year": 2024}),
            _generic_example("league_per_36_minutes", "2015", {"season_end_year": 2015}),
            _generic_example("league_totals", "2024", {"season_end_year": 2024}),
            _generic_example("league_totals", "2012", {"season_end_year": 2012}),
            _generic_example("league_per_100_possessions", "2024", {"season_end_year": 2024}),
            _generic_example("league_per_100_possessions", "2016", {"season_end_year": 2016}),
            _generic_example("league_shooting", "2024", {"season_end_year": 2024}),
            _generic_example("league_shooting", "2018", {"season_end_year": 2018}),
            _generic_example("league_transactions", "2024", {"season_end_year": 2024}),
            _generic_example("league_transactions", "2020", {"season_end_year": 2020}),
            _generic_example("rookie_stats", "2024", {"season_end_year": 2024}),
            _generic_example("rookie_stats", "2019", {"season_end_year": 2019}),
        ]
    )

    # Standings requires the bespoke parser page.
    examples.extend(
        [
            _generic_example("standings", "2024", {"season_end_year": 2024}, ("divs_standings_E", "divs_standings_W")),
            _generic_example("standings", "2010", {"season_end_year": 2010}, ("divs_standings_E", "divs_standings_W")),
        ]
    )

    # Standings by date: one example spans both conferences.
    for season in (2024, 2018):
        tasks = []
        for conference in ("eastern_conference", "western_conference"):
            params = {"season_end_year": season, "conference": conference}
            path = ENDPOINTS["standings_by_date"].path.format(**params)
            tasks.append(
                FetchTask(
                    url=_url(path),
                    relative_path=Path("standings_by_date") / f"{season}_{conference}.html",
                    table_ids=("standings_by_date",),
                )
            )
        examples.append(
            RawExample(
                endpoint="standings_by_date",
                example_id=str(season),
                params={"season_end_year": season},
                tasks=tuple(tasks),
            )
        )

    examples.extend(
        [
            _generic_example("attendance", "2024", {"season_end_year": 2024}, ("advanced-team",)),
            _generic_example("attendance", "2016", {"season_end_year": 2016}, ("advanced-team",)),
        ]
    )

    # ── Playoffs ──
    examples.extend(
        [
            _generic_example("playoff_per_game", "2024", {"season_end_year": 2024}, ("per_game_stats_post",)),
            _generic_example("playoff_per_game", "2019", {"season_end_year": 2019}, ("per_game_stats_post",)),
            _generic_example("playoff_totals", "2024", {"season_end_year": 2024}, ("totals_stats_post",)),
            _generic_example("playoff_totals", "2018", {"season_end_year": 2018}, ("totals_stats_post",)),
            _generic_example("playoff_bracket", "2024", {"season_end_year": 2024}, ("all_playoffs",)),
            _generic_example("playoff_bracket", "2015", {"season_end_year": 2015}, ("all_playoffs",)),
        ]
    )

    # ── Draft, awards, leaders ──
    examples.extend(
        [
            _generic_example("draft_picks", "2024", {"season_end_year": 2024}, ("stats",)),
            _generic_example("draft_picks", "2010", {"season_end_year": 2010}, ("stats",)),
            _generic_example("season_awards", "2024", {"season_end_year": 2024}, ("mvp",)),
            _generic_example("season_awards", "2015", {"season_end_year": 2015}, ("mvp",)),
            _static_example("season_leaders", "default"),
            _static_example("career_leaders", "default"),
        ]
    )

    # ── Player pages ──
    player_pages = [
        ("player_career_stats", "jamesle01", "curryst01", ("per_game_stats",)),
        ("player_playoff_series", "jamesle01", "duncati01", ("playoffs_series",)),
        ("player_adjusted_shooting", "jamesle01", "birdla01", ("adj_shooting",)),
        ("player_play_by_play", "jamesle01", "paulch01", ("pbp_stats",)),
        ("player_game_highs", "jamesle01", "jordami01", ("highs-reg-season",)),
        ("player_all_star", "jamesle01", "bryanko01", ("all_star",)),
        ("player_similarity_scores", "jamesle01", "abdulka01", ("sims-career",)),
        ("player_salaries", "jamesle01", "duranke01", ("all_salaries",)),
    ]
    for endpoint_name, player_a, player_b, table_ids in player_pages:
        examples.extend(
            [
                _generic_example(endpoint_name, player_a, {"player_identifier": player_a}, table_ids),
                _generic_example(endpoint_name, player_b, {"player_identifier": player_b}, table_ids),
            ]
        )

    # Player deep pages (robots.txt disallowed)
    examples.extend(
        [
            _generic_example(
                "player_splits",
                "jamesle01_2024",
                {"player_identifier": "jamesle01", "season_end_year": 2024},
                ("splits",),
            ),
            _generic_example(
                "player_splits",
                "curryst01_2023",
                {"player_identifier": "curryst01", "season_end_year": 2023},
                ("splits",),
            ),
            _generic_example(
                "player_on_off",
                "jamesle01_2024",
                {"player_identifier": "jamesle01", "season_end_year": 2024},
                ("on-off",),
            ),
            _generic_example(
                "player_on_off",
                "jokicni01_2024",
                {"player_identifier": "jokicni01", "season_end_year": 2024},
                ("on-off",),
            ),
            _generic_example(
                "player_shot_charts",
                "jamesle01_2024",
                {"player_identifier": "jamesle01", "season_end_year": 2024},
                ("shooting",),
            ),
            _generic_example(
                "player_shot_charts",
                "curryst01_2024",
                {"player_identifier": "curryst01", "season_end_year": 2024},
                ("shooting",),
            ),
        ]
    )

    # ── Team pages ──
    team_params = [
        ("team_roster", "BOS_2024", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("roster",)),
        ("team_roster", "LAL_2023", {"team_abbreviation": "LAL", "season_end_year": 2023}, ("roster",)),
        ("team_injury_report", "default", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("injuries",)),
        (
            "team_and_opponent",
            "BOS_2024",
            {"team_abbreviation": "BOS", "season_end_year": 2024},
            ("team_and_opponent",),
        ),
        (
            "team_and_opponent",
            "GSW_2023",
            {"team_abbreviation": "GSW", "season_end_year": 2023},
            ("team_and_opponent",),
        ),
        ("team_misc_four_factors", "BOS_2024", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("team_misc",)),
        ("team_misc_four_factors", "MIA_2023", {"team_abbreviation": "MIA", "season_end_year": 2023}, ("team_misc",)),
        (
            "team_opponent_stats",
            "BOS_2024",
            {"team_abbreviation": "BOS", "season_end_year": 2024},
            ("team_and_opponent",),
        ),
        (
            "team_opponent_stats",
            "DEN_2024",
            {"team_abbreviation": "DEN", "season_end_year": 2024},
            ("team_and_opponent",),
        ),
        ("team_schedule", "BOS_2024", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("games",)),
        ("team_schedule", "LAL_2023", {"team_abbreviation": "LAL", "season_end_year": 2023}, ("games",)),
        ("team_transactions", "BOS_2024", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("transactions",)),
        ("team_transactions", "DAL_2024", {"team_abbreviation": "DAL", "season_end_year": 2024}, ("transactions",)),
        ("team_splits", "BOS_2024", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("team_splits",)),
        ("team_splits", "GSW_2023", {"team_abbreviation": "GSW", "season_end_year": 2023}, ("team_splits",)),
        ("team_contracts", "BOS", {"team_abbreviation": "BOS"}, ("contracts",)),
        ("team_contracts", "LAL", {"team_abbreviation": "LAL"}, ("contracts",)),
        ("team_lineups", "BOS_2024", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("lineups_5-man_",)),
        ("team_lineups", "DEN_2024", {"team_abbreviation": "DEN", "season_end_year": 2024}, ("lineups_5-man_",)),
        (
            "team_starting_lineups",
            "BOS_2024",
            {"team_abbreviation": "BOS", "season_end_year": 2024},
            ("starting_lineups_po0",),
        ),
        (
            "team_starting_lineups",
            "PHO_2024",
            {"team_abbreviation": "PHO", "season_end_year": 2024},
            ("starting_lineups_po0",),
        ),
        ("team_on_off", "BOS_2024", {"team_abbreviation": "BOS", "season_end_year": 2024}, ("on_off",)),
        ("team_on_off", "MIL_2023", {"team_abbreviation": "MIL", "season_end_year": 2023}, ("on_off",)),
        ("franchise_history", "BOS", {"team_abbreviation": "BOS"}, ("BOS",)),
        ("franchise_history", "LAL", {"team_abbreviation": "LAL"}, ("LAL",)),
    ]
    for endpoint_name, example_id, params, table_ids in team_params:
        examples.append(_generic_example(endpoint_name, example_id, params, table_ids))

    # ── Bespoke / custom endpoints ──

    # Player daily box scores
    examples.extend(
        [
            _generic_example(
                "player_box_scores",
                "2018_01_01",
                {"day": 1, "month": 1, "year": 2018},
                ("stats",),
            ),
            _generic_example(
                "player_box_scores",
                "2017_12_12",
                {"day": 12, "month": 12, "year": 2017},
                ("stats",),
            ),
        ]
    )

    # Team box scores: daily index + individual game pages.
    team_box_score_dates = [
        ("2017_01_01", 2017, 1, 1, ["201701010ATL"]),
        ("2001_01_01", 2001, 1, 1, ["200101010MIN", "200101010POR"]),
    ]
    for example_id, year, month, day, game_ids in team_box_score_dates:
        tasks = [
            FetchTask(
                url=f"{BASE_URL}/boxscores/?day={day}&month={month}&year={year}",
                relative_path=Path("team_box_scores") / example_id / "index.html",
                table_ids=(),
            )
        ]
        for game_id in game_ids:
            tasks.append(
                FetchTask(
                    url=f"{BASE_URL}/boxscores/{game_id}.html",
                    relative_path=Path("team_box_scores") / example_id / f"{game_id}.html",
                    table_ids=(),
                )
            )
        examples.append(
            RawExample(
                endpoint="team_box_scores",
                example_id=example_id,
                params={"day": day, "month": month, "year": year},
                tasks=tuple(tasks),
            )
        )

    # Play by play: daily index + pbp page.
    pbp_games = [
        ("ATL_2017_01_01", "ATL", 2017, 1, 1, "201701010ATL"),
        ("TOR_2003_10_29", "TOR", 2003, 10, 29, "200310290TOR"),
    ]
    for example_id, home_team, year, month, day, game_id in pbp_games:
        tasks = [
            FetchTask(
                url=f"{BASE_URL}/boxscores/?day={day}&month={month}&year={year}",
                relative_path=Path("play_by_play") / example_id / "index.html",
                table_ids=(),
            ),
            FetchTask(
                url=f"{BASE_URL}/boxscores/pbp/{game_id}.html",
                relative_path=Path("play_by_play") / example_id / f"{game_id}.html",
                table_ids=("pbp",),
            ),
        ]
        examples.append(
            RawExample(
                endpoint="play_by_play",
                example_id=example_id,
                params={"home_team": home_team, "day": day, "month": month, "year": year},
                tasks=tuple(tasks),
            )
        )

    # Player gamelogs (regular season and playoffs)
    examples.extend(
        [
            _generic_example(
                "regular_season_player_box_scores",
                "westbru01_2019",
                {"player_identifier": "westbru01", "season_end_year": 2019, "include_inactive_games": False},
                ("player_game_log_reg",),
            ),
            _generic_example(
                "regular_season_player_box_scores",
                "antetgi01_2020",
                {"player_identifier": "antetgi01", "season_end_year": 2020, "include_inactive_games": False},
                ("player_game_log_reg",),
            ),
            _generic_example(
                "playoff_player_box_scores",
                "jamesle01_2023",
                {"player_identifier": "jamesle01", "season_end_year": 2023, "include_inactive_games": False},
                ("player_game_log_post",),
            ),
            _generic_example(
                "playoff_player_box_scores",
                "curryst01_2023",
                {"player_identifier": "curryst01", "season_end_year": 2023, "include_inactive_games": False},
                ("player_game_log_post",),
            ),
        ]
    )

    # Season schedule: main page + monthly pages (discovered dynamically).
    # Includes anomaly seasons: 1999 (lockout, Feb start), 2020 (COVID bubble,
    # Mar suspension / Jul-Oct resume), 2021 (compressed Dec start, play-in era).
    for season in (2024, 2018, 1980, 2000, 2012, 1999, 2020, 2021):
        examples.append(_build_season_schedule_example(season))

    # Players season totals
    examples.extend(
        [
            _generic_example("players_season_totals", "2024", {"season_end_year": 2024}, ("totals_stats",)),
            _generic_example("players_season_totals", "2018", {"season_end_year": 2018}, ("totals_stats",)),
        ]
    )

    # Players advanced season totals
    examples.extend(
        [
            _generic_example(
                "players_advanced_season_totals",
                "2024_false",
                {"season_end_year": 2024, "include_combined_values": False},
                ("advanced",),
            ),
            _generic_example(
                "players_advanced_season_totals",
                "2019_true",
                {"season_end_year": 2019, "include_combined_values": True},
                ("advanced",),
            ),
        ]
    )

    # Search: one redirect, one results page, one no-results, one pagination.
    examples.extend(
        [
            _generic_example("search", "kobe", {"term": "kobe"}, ()),
            _generic_example("search", "Alonz", {"term": "Alonz"}, ()),
            _generic_example("search", "no_results", {"term": "qqqqqqqqqqq"}, ()),
        ]
    )

    # Search pagination: fetch first two pages of "ja" query.
    for page, offset in (("ja_page_0", 0), ("ja_page_1", 100)):
        examples.append(
            RawExample(
                endpoint="search",
                example_id=page,
                params={"term": "ja", "offset": offset},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/search/search.fcgi?search=ja&i=players&offset={offset}",
                        relative_path=Path("search") / f"{page}.html",
                        table_ids=(),
                    ),
                ),
            )
        )

    # ── Era/stat-boundary league pages (P1) ──
    era_league_endpoints = [
        # endpoint, example_id, params, table_ids
        ("league_per_game_stats", "1955", {"season_end_year": 1955}, ("per_game_stats",)),
        ("league_per_game_stats", "1973", {"season_end_year": 1973}, ("per_game_stats",)),
        ("league_per_game_stats", "1974", {"season_end_year": 1974}, ("per_game_stats",)),
        ("league_per_game_stats", "1979", {"season_end_year": 1979}, ("per_game_stats",)),
        ("league_per_game_stats", "1980", {"season_end_year": 1980}, ("per_game_stats",)),
        ("league_totals", "1973", {"season_end_year": 1973}, ("totals_stats",)),
        ("league_totals", "1974", {"season_end_year": 1974}, ("totals_stats",)),
        ("league_totals", "1978", {"season_end_year": 1978}, ("totals_stats",)),
        ("league_totals", "1980", {"season_end_year": 1980}, ("totals_stats",)),
        ("league_per_100_possessions", "1973", {"season_end_year": 1973}, ("per_poss",), (200, 404)),
        ("league_per_100_possessions", "1974", {"season_end_year": 1974}, ("per_poss",)),
        ("league_shooting", "2013", {"season_end_year": 2013}, ("shooting",)),
        ("league_shooting", "2014", {"season_end_year": 2014}, ("shooting",)),
        ("league_shooting", "2025", {"season_end_year": 2025}, ("shooting",)),
        ("players_season_totals", "1974", {"season_end_year": 1974}, ("totals_stats",)),
        ("players_season_totals", "1975", {"season_end_year": 1975}, ("totals_stats",)),
        ("players_season_totals", "1980", {"season_end_year": 1980}, ("totals_stats",)),
        ("players_season_totals", "1990", {"season_end_year": 1990}, ("totals_stats",)),
        (
            "players_advanced_season_totals",
            "1974",
            {"season_end_year": 1974, "include_combined_values": False},
            ("advanced",),
        ),
        (
            "players_advanced_season_totals",
            "1977",
            {"season_end_year": 1977, "include_combined_values": False},
            ("advanced",),
        ),
        (
            "players_advanced_season_totals",
            "1978",
            {"season_end_year": 1978, "include_combined_values": False},
            ("advanced",),
        ),
        (
            "players_advanced_season_totals",
            "1985",
            {"season_end_year": 1985, "include_combined_values": False},
            ("advanced",),
        ),
        (
            "players_advanced_season_totals",
            "1990",
            {"season_end_year": 1990, "include_combined_values": False},
            ("advanced",),
        ),
        ("standings", "1974", {"season_end_year": 1974}, ("divs_standings_E", "divs_standings_W")),
        ("standings", "1980", {"season_end_year": 1980}, ("divs_standings_E", "divs_standings_W")),
        ("playoff_per_game", "1980", {"season_end_year": 1980}, ("per_game_stats_post",)),
        ("playoff_totals", "1974", {"season_end_year": 1974}, ("totals_stats_post",)),
        ("playoff_bracket", "1974", {"season_end_year": 1974}, ("all_playoffs",)),
        ("draft_picks", "1965", {"season_end_year": 1965}, ("stats",)),
        ("draft_picks", "1984", {"season_end_year": 1984}, ("stats",)),
        ("season_awards", "1974", {"season_end_year": 1974}, ()),
        ("rookie_stats", "1980", {"season_end_year": 1980}, ("rookies",)),
    ]
    for entry in era_league_endpoints:
        endpoint_name, example_id, params, table_ids, *rest = entry
        allowed_statuses = rest[0] if rest else (200,)
        examples.append(
            _generic_example(endpoint_name, example_id, params, table_ids, allowed_statuses=allowed_statuses)
        )

    # ── Era-spanning player career pages (P1/P2) ──
    era_player_pages = [
        ("player_career_stats", "chambwi01", ("per_game_stats",)),
        ("player_career_stats", "russebi01", ("per_game_stats",)),
        ("player_career_stats", "abdulka01", ("per_game_stats",)),
        ("player_career_stats", "birdla01", ("per_game_stats",)),
        ("player_playoff_series", "chambwi01", ("playoffs_series",)),
        ("player_adjusted_shooting", "jordami01", ("adj_shooting",)),
        ("player_play_by_play", "jordami01", ("pbp_stats",)),
        ("player_game_highs", "birdla01", ("highs-reg-season",)),
        ("player_all_star", "chambwi01", ("all_star",)),
        ("player_similarity_scores", "chambwi01", ("sims-career",)),
        ("player_salaries", "jordami01", ("all_salaries",)),
    ]
    for endpoint_name, player_id, table_ids in era_player_pages:
        examples.append(_generic_example(endpoint_name, player_id, {"player_identifier": player_id}, table_ids))

    # ── Era boundary player deep pages (P1) ──
    examples.extend(
        [
            _generic_example(
                "player_splits",
                "birdla01_1980",
                {"player_identifier": "birdla01", "season_end_year": 1980},
                ("splits",),
            ),
            _generic_example(
                "player_on_off",
                "jordami01_1997",
                {"player_identifier": "jordami01", "season_end_year": 1997},
                ("on-off",),
            ),
            _generic_example(
                "player_shot_charts",
                "jordami01_1997",
                {"player_identifier": "jordami01", "season_end_year": 1997},
                ("shooting",),
            ),
        ]
    )

    # ── Era/edge-case team pages (P1/P2) ──
    era_team_params = [
        ("team_roster", "BOS_1974", {"team_abbreviation": "BOS", "season_end_year": 1974}, ("roster",)),
        ("team_roster", "BOS_1980", {"team_abbreviation": "BOS", "season_end_year": 1980}, ("roster",)),
        ("team_schedule", "SEA_2008", {"team_abbreviation": "SEA", "season_end_year": 2008}, ("games",)),
        (
            "team_and_opponent",
            "BOS_1974",
            {"team_abbreviation": "BOS", "season_end_year": 1974},
            ("team_and_opponent",),
        ),
        ("team_misc_four_factors", "BOS_1974", {"team_abbreviation": "BOS", "season_end_year": 1974}, ("team_misc",)),
        ("team_splits", "BOS_1980", {"team_abbreviation": "BOS", "season_end_year": 1980}, ("team_splits",)),
        ("team_on_off", "CHI_1997", {"team_abbreviation": "CHI", "season_end_year": 1997}, ("on_off",)),
        ("team_lineups", "CHI_1997", {"team_abbreviation": "CHI", "season_end_year": 1997}, ("lineups_5-man_",)),
        ("franchise_history", "OKC", {"team_abbreviation": "OKC"}, ("OKC",)),
        ("franchise_history", "WAS", {"team_abbreviation": "WAS"}, ("WAS",)),
        ("franchise_history", "SAC", {"team_abbreviation": "SAC"}, ("SAC",)),
    ]
    for endpoint_name, example_id, params, table_ids in era_team_params:
        examples.append(_generic_example(endpoint_name, example_id, params, table_ids))

    # ── Empty-state / error-case fixtures (P0/P2) ──
    examples.extend(
        [
            # No-game date for team box scores
            RawExample(
                endpoint="team_box_scores",
                example_id="2024_07_04_no_games",
                params={"day": 4, "month": 7, "year": 2024},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/boxscores/?day=4&month=7&year=2024",
                        relative_path=Path("team_box_scores") / "2024_07_04" / "index.html",
                        table_ids=(),
                        allowed_statuses=(200,),
                    ),
                ),
            ),
            # Offseason injury report (static URL; reusing same global page is fine)
            RawExample(
                endpoint="team_injury_report",
                example_id="offseason",
                params={"team_abbreviation": "BOS", "season_end_year": 2024},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/friv/injuries.fcgi",
                        relative_path=Path("team_injury_report") / "offseason.html",
                        table_ids=("injuries",),
                    ),
                ),
            ),
            # 404 player page
            RawExample(
                endpoint="player_career_stats",
                example_id="invalid_404",
                params={"player_identifier": "xyzabc01"},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/players/x/xyzabc01.html",
                        relative_path=Path("errors") / "invalid_player_404.html",
                        table_ids=(),
                        allowed_statuses=(404,),
                    ),
                ),
            ),
            # 404 team page
            RawExample(
                endpoint="team_roster",
                example_id="invalid_team_404",
                params={"team_abbreviation": "XYZ", "season_end_year": 2024},
                tasks=(
                    FetchTask(
                        url=f"{BASE_URL}/teams/XYZ/2024.html",
                        relative_path=Path("errors") / "invalid_team_404.html",
                        table_ids=(),
                        allowed_statuses=(404,),
                    ),
                ),
            ),
        ]
    )

    # ── Play-by-play: first PBP season + multi-OT modern game (P1) ──
    pbp_era_games = [
        ("TOR_1996_11_01", "TOR", 1996, 11, 1, "199611010TOR"),
    ]
    for example_id, home_team, year, month, day, game_id in pbp_era_games:
        tasks = [
            FetchTask(
                url=f"{BASE_URL}/boxscores/?day={day}&month={month}&year={year}",
                relative_path=Path("play_by_play") / example_id / "index.html",
                table_ids=(),
            ),
            FetchTask(
                url=f"{BASE_URL}/boxscores/pbp/{game_id}.html",
                relative_path=Path("play_by_play") / example_id / f"{game_id}.html",
                table_ids=("pbp",),
            ),
        ]
        examples.append(
            RawExample(
                endpoint="play_by_play",
                example_id=example_id,
                params={"home_team": home_team, "day": day, "month": month, "year": year},
                tasks=tuple(tasks),
            )
        )

    # ── Custom player endpoints: additional active/inactive and empty-state cases (P0/P1) ──
    examples.extend(
        [
            _generic_example(
                "regular_season_player_box_scores",
                "jokicni01_2024",
                {"player_identifier": "jokicni01", "season_end_year": 2024, "include_inactive_games": True},
                ("player_game_log_reg",),
            ),
            _generic_example(
                "playoff_player_box_scores",
                "doncilu01_2024",
                {"player_identifier": "doncilu01", "season_end_year": 2024, "include_inactive_games": False},
                ("player_game_log_post",),
            ),
        ]
    )

    # ── Era/edge-case gaps identified by PDCA cycle 1 (P1) ──
    # Stat-availability boundaries not previously exercised:
    examples.append(
        # First public season of the shooting-detail table (1996-97).
        _generic_example("league_shooting", "1997", {"season_end_year": 1997}, ("shooting",))
    )
    examples.append(
        # Play-in-era standings seeding labels.
        _generic_example("standings", "2021", {"season_end_year": 2021}, ("divs_standings_E", "divs_standings_W"))
    )

    # Franchise relocation / rename / expansion edge cases. The Team enum already
    # recognises every historical abbreviation below; these exercise abbreviation
    # resolution, rename boundaries, and split franchise histories.
    franchise_relocation_params = [
        # NJN -> BRK rename (2012-13)
        ("team_roster", "BRK_2013", {"team_abbreviation": "BRK", "season_end_year": 2013}, ("roster",)),
        (
            "team_and_opponent",
            "BRK_2013",
            {"team_abbreviation": "BRK", "season_end_year": 2013},
            ("team_and_opponent",),
        ),
        # Vancouver expansion + VAN -> MEM move (2001-02)
        ("team_roster", "VAN_1996", {"team_abbreviation": "VAN", "season_end_year": 1996}, ("roster",)),
        ("team_roster", "MEM_2002", {"team_abbreviation": "MEM", "season_end_year": 2002}, ("roster",)),
        # New Orleans abbreviation drift: NOH -> NOK (OKC temp.) -> NOH -> NOP
        ("team_roster", "NOH_2003", {"team_abbreviation": "NOH", "season_end_year": 2003}, ("roster",)),
        ("team_roster", "NOK_2006", {"team_abbreviation": "NOK", "season_end_year": 2006}, ("roster",)),
        ("team_roster", "NOP_2014", {"team_abbreviation": "NOP", "season_end_year": 2014}, ("roster",)),
        # Charlotte: Bobcats expansion (CHA), original Hornets (CHH), modern reclaim (CHO)
        ("team_roster", "CHA_2005", {"team_abbreviation": "CHA", "season_end_year": 2005}, ("roster",)),
        ("team_roster", "CHH_1989", {"team_abbreviation": "CHH", "season_end_year": 1989}, ("roster",)),
        ("team_roster", "CHO_2015", {"team_abbreviation": "CHO", "season_end_year": 2015}, ("roster",)),
        # Washington Bullets (WSB) -> Wizards (WAS) rename boundary
        ("team_roster", "WSB_1997", {"team_abbreviation": "WSB", "season_end_year": 1997}, ("roster",)),
        ("team_roster", "WAS_1998", {"team_abbreviation": "WAS", "season_end_year": 1998}, ("roster",)),
        # Kansas City Kings (KCK) -> Sacramento (SAC) move (1985-86)
        ("team_roster", "KCK_1984", {"team_abbreviation": "KCK", "season_end_year": 1984}, ("roster",)),
        ("team_roster", "SAC_1986", {"team_abbreviation": "SAC", "season_end_year": 1986}, ("roster",)),
    ]
    for endpoint_name, example_id, params, table_ids in franchise_relocation_params:
        examples.append(_generic_example(endpoint_name, example_id, params, table_ids))

    # League-wide player play-by-play stats page — new page family
    # (/leagues/NBA_{YEAR}_play-by-play.html) not yet backed by an endpoint.
    # table_ids=() downloads regardless of table count; endpoint TBD later.
    for pbp_year in (1997, 2024):
        examples.append(
            RawExample(
                endpoint="league_play_by_play",
                example_id=str(pbp_year),
                params={"season_end_year": pbp_year},
                tasks=(
                    FetchTask(
                        url=_url(f"/leagues/NBA_{pbp_year}_play-by-play.html"),
                        relative_path=Path("league_play_by_play") / f"{pbp_year}.html",
                        table_ids=(),
                    ),
                ),
            )
        )

    # Examples the integration test-suite asserts on (beyond the curated set).
    examples.extend(_build_integration_test_examples())

    return tuple(examples)


# ---------------------------------------------------------------------------
# CSV page-family catalog (BREF new page families)
# ---------------------------------------------------------------------------


def _example_id_from_url(sample_url: str) -> str:
    """Derive a descriptive ``example_id`` from a CSV ``sample_url``.

    Mirrors the older ENDPOINTS convention of naming files by their identifying
    parameter (``BOS_2024``, ``jamesle01``) rather than a generic placeholder.
    Rule: last URL path segment (extension stripped) + sorted query params
    folded in after ``__``; sanitized to be filename-safe. Examples:
      ``/coaches/mazzujo99c.html``                            -> ``mazzujo99c``
      ``/boxscores/202606100NYK.html#all_four_factors``       -> ``202606100NYK``
      ``/leagues/NBA_2026_rookies.html``                      -> ``NBA_2026_rookies``
      ``/friv/birthdays.fcgi?month=12&day=30``                -> ``birthdays__day-30_month-12``
    """
    parts = urlsplit(sample_url)
    segments = [s for s in parts.path.split("/") if s]
    if segments:
        last = segments[-1]
        for ext in (".html", ".htm", ".fcgi", ".cgi"):
            if last.endswith(ext):
                last = last[: -len(ext)]
                break
        segments[-1] = last
    slug = segments[-1] if segments else "index"
    if parts.query:
        params = sorted(parse_qsl(parts.query))  # deterministic order by key
        qs = "_".join(f"{k}-{v}" for k, v in params)
        slug = f"{slug}__{qs}"
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", slug)
    slug = re.sub(r"_+", "_", slug).strip("._")
    return slug or "index"


def _build_csv_catalog(csv_path: Path) -> list[RawExample]:
    """Load in-scope page families from the BREF inventory CSV.

    A CSV row is in scope IFF:
      1. ``robots_status == "allowed"``
      2. ``tier == "P2_new"`` OR (``tier == "P1_duplicate"`` AND
         ``page_family`` in :data:`_SCOPED_P1_DUPLICATE_FAMILIES`)
      3. ``sample_url`` starts with the basketball-reference.com base URL.

    Each in-scope row becomes one :class:`RawExample` writing to
    ``raw/{page_family}/sample.html`` with ``table_ids=()`` (unknown up front)
    and ``allowed_statuses=(200, 404)``. Because ``table_ids`` is empty,
    :func:`validate_html` never rejects a page for missing tables — every URL
    downloads regardless of table count; discovered tables are recorded in the
    sidecar instead.
    """
    examples: list[RawExample] = []
    if not csv_path.exists():
        logger.warning("CSV catalog not found: %s", csv_path)
        return examples

    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row_num, row in enumerate(reader, start=1):
            page_family = row.get("page_family", "").strip()
            category = row.get("category", "").strip()
            tier = row.get("tier", "").strip()
            robots_status = row.get("robots_status", "").strip()
            sample_url = row.get("sample_url", "").strip()

            if robots_status != "allowed":
                logger.debug(
                    "CSV row %d (%s): robots_status=%s, excluded",
                    row_num + 1,
                    page_family,
                    robots_status,
                )
                continue
            if tier == "P2_new":
                pass
            elif tier == "P1_duplicate" and page_family in _SCOPED_P1_DUPLICATE_FAMILIES:
                pass
            else:
                logger.debug(
                    "CSV row %d (%s): tier=%s, excluded",
                    row_num + 1,
                    page_family,
                    tier,
                )
                continue
            if not sample_url.startswith(BREF_BASE_URL):
                logger.debug(
                    "CSV row %d (%s): sample_url off-domain, excluded",
                    row_num + 1,
                    page_family,
                )
                continue

            example_id = _example_id_from_url(sample_url)
            examples.append(
                RawExample(
                    endpoint=page_family,
                    example_id=example_id,
                    params={
                        "category": category,
                        "tier": tier,
                        "librarian_row": row.get("librarian_row", "").strip(),
                        "url": sample_url,
                    },
                    tasks=(
                        FetchTask(
                            url=sample_url,
                            relative_path=Path(page_family) / f"{example_id}.html",
                            table_ids=(),
                            allowed_statuses=(200, 404),
                        ),
                    ),
                )
            )

    logger.info("Loaded %d in-scope CSV page families from %s", len(examples), csv_path)
    return examples


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _decompress_if_needed(content: bytes) -> bytes:
    """Defensively decompress gzip responses.

    ``HTTPService(cache=False)`` with the curl-cffi transport can return raw
    gzip bytes even though ``Content-Encoding: gzip`` is present. hishel's
    ``SyncCacheTransport`` normally handles decompression, so we default to
    ``cache=True`` and use this helper as a fallback for any compressed body.
    """
    if content[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(content)
        except Exception:
            pass
    try:
        return zlib.decompress(content)
    except Exception:
        return content


def _extract_title(document: html.HtmlElement) -> str | None:
    try:
        title_nodes = document.xpath("//title/text()")
        if title_nodes:
            return str(title_nodes[0]).strip()
    except Exception:
        pass
    return None


def _looks_like_br_page(document: html.HtmlElement) -> bool:
    title = _extract_title(document) or ""
    return "Basketball-Reference" in title or "Basketball Stats and History" in title


def _discover_table_ids(
    html_bytes: bytes,
    document: html.HtmlElement,
) -> tuple[list[str], list[str], list[str]]:
    """Extract every ``<table id="...">`` — visible and comment-wrapped.

    Basketball-Reference hides many tables inside HTML comments
    (``<!-- <table id="X"> ... -->``). Returns ``(visible, commented, union)``,
    each a sorted, deduplicated list. Used to record what tables a page actually
    contains without requiring them upfront (so every URL downloads regardless
    of table count).
    """
    visible_ids = [str(i) for i in document.xpath("//table[@id]/@id")]
    text = html_bytes.decode("utf-8", errors="ignore")
    commented_ids: list[str] = []
    for comment_body in re.findall(r"<!--(.*?)-->", text, flags=re.DOTALL):
        commented_ids += re.findall(r"""<table[^>]*\sid=["']([^"']+)["']""", comment_body)
    visible = sorted(set(visible_ids))
    commented = sorted(set(commented_ids))
    union = sorted(set(visible_ids) | set(commented_ids))
    return visible, commented, union


def _snapshot_response(
    html_bytes: bytes,
    response: httpx.Response,
) -> ResponseSnapshot:
    document: html.HtmlElement | None = None
    try:
        document = html.fromstring(html_bytes)
    except Exception:
        pass

    return ResponseSnapshot(
        url=str(response.request.url),
        final_url=str(response.url),
        status_code=response.status_code,
        content_encoding=response.headers.get("content-encoding"),
        content_type=response.headers.get("content-type"),
        body_bytes=len(html_bytes),
        is_gzip=html_bytes[:2] == b"\x1f\x8b",
        title=_extract_title(document) if document is not None else None,
        first_kilobyte_preview=html_bytes[:1024].decode("utf-8", errors="replace"),
    )


def validate_html(
    html_bytes: bytes,
    task: FetchTask,
) -> None:
    """Validate a downloaded HTML body. Raises RawDownloadError on failure."""
    if len(html_bytes) < MIN_BODY_BYTES:
        raise RawDownloadError(f"Body too small ({len(html_bytes)} bytes) for {task.url}; likely a block page")

    for marker in BLOCKED_MARKERS:
        if marker in html_bytes:
            raise RawDownloadError(f"Blocked-page marker {marker!r} found for {task.url}")

    try:
        document = html.fromstring(html_bytes)
    except Exception as exc:
        raise RawDownloadError(f"Could not parse HTML for {task.url}") from exc

    if not document.xpath("//html"):
        raise RawDownloadError(f"Missing <html> root for {task.url}")

    if not _looks_like_br_page(document):
        title = _extract_title(document)
        raise RawDownloadError(f"Page title does not look like Basketball-Reference for {task.url} (title={title!r})")

    for table_id in task.table_ids:
        if document.xpath(f'//table[@id="{table_id}"]'):
            return
        html_text = html_bytes.decode("utf-8", errors="ignore")
        if f'id="{table_id}"' in html_text or f"id='{table_id}'" in html_text:
            return
        raise RawDownloadError(f"Expected table id {table_id!r} not found for {task.url}")


# ---------------------------------------------------------------------------
# Download orchestration
# ---------------------------------------------------------------------------


@dataclass
class DownloadStats:
    fetched: int = 0
    skipped: int = 0
    failed: int = 0
    total_bytes: int = 0
    wallclock_seconds: float = 0.0


def _save_failure_snapshot(
    output_root: Path,
    task: FetchTask,
    response: httpx.Response,
    html_bytes: bytes,
    error_message: str,
) -> Path:
    """Persist a raw response plus metadata when validation fails."""
    failure_dir = output_root / "_failures"
    failure_dir.mkdir(parents=True, exist_ok=True)
    safe_name = task.relative_path.as_posix().replace("/", "__")
    failure_path = failure_dir / f"{safe_name}.failed.html"
    failure_meta_path = failure_path.with_suffix(".meta.json")

    snapshot = _snapshot_response(html_bytes, response)
    failure_path.write_bytes(html_bytes)
    failure_meta_path.write_text(
        json.dumps(
            {
                "url": snapshot.url,
                "final_url": snapshot.final_url,
                "status_code": snapshot.status_code,
                "content_encoding": snapshot.content_encoding,
                "content_type": snapshot.content_type,
                "body_bytes": snapshot.body_bytes,
                "is_gzip": snapshot.is_gzip,
                "title": snapshot.title,
                "first_kilobyte_preview": snapshot.first_kilobyte_preview,
                "error": error_message,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return failure_path


def _fetch_one(
    service: HTTPService,
    task: FetchTask,
    output_root: Path,
    force: bool,
) -> FetchResult:
    """Fetch and save one URL, or skip if already present."""
    output_path = output_root / task.relative_path
    metadata_path = output_path.with_suffix(output_path.suffix + ".meta.json")

    if not force and output_path.exists() and metadata_path.exists():
        try:
            meta = json.loads(metadata_path.read_text(encoding="utf-8"))
            return FetchResult(
                task=task,
                output_path=output_path,
                metadata_path=metadata_path,
                status_code=meta.get("status_code", 0),
                byte_count=meta.get("byte_count", 0),
                sha256=meta.get("sha256", ""),
                wallclock_ms=0,
                skipped=True,
                discovered_table_ids=meta.get("discovered_table_ids", []),
            )
        except (OSError, ValueError):
            pass  # malformed sidecar; refetch

    output_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    try:
        response = service._get(url=task.url)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in task.allowed_statuses:
            response = exc.response
        else:
            raise
    if response.status_code not in task.allowed_statuses:
        response.raise_for_status()
    raw_bytes = response.content
    html_bytes = _decompress_if_needed(raw_bytes)
    wallclock_ms = int((time.perf_counter() - start) * 1000)

    logger.debug(
        "Response metadata for %s: status=%d content-encoding=%s content-type=%s "
        "raw_bytes=%d decompressed_bytes=%d is_gzip=%s",
        task.url,
        response.status_code,
        response.headers.get("content-encoding"),
        response.headers.get("content-type"),
        len(raw_bytes),
        len(html_bytes),
        raw_bytes[:2] == b"\x1f\x8b",
    )

    # Discovery state (populated only for HTTP 200 pages).
    discovered_visible: list[str] = []
    discovered_commented: list[str] = []
    discovered_table_ids: list[str] = []

    # Skip HTML validation for allowed non-200 statuses (e.g. 404 fixtures)
    if response.status_code == 200:
        try:
            validate_html(html_bytes, task)
        except RawDownloadError as exc:
            failure_path = _save_failure_snapshot(output_root, task, response, html_bytes, str(exc))
            logger.warning("Saved failure snapshot to %s", failure_path)
            raise
        # Record every <table id> present (visible + comment-wrapped). This is
        # non-blocking: a page with zero tables still downloads successfully.
        try:
            document = html.fromstring(html_bytes)
        except Exception:  # noqa: BLE001
            document = None
        if document is not None:
            discovered_visible, discovered_commented, discovered_table_ids = _discover_table_ids(html_bytes, document)
            logger.debug(
                "Discovered %d table id(s) for %s: visible=%s commented=%s",
                len(discovered_table_ids),
                task.url,
                discovered_visible,
                discovered_commented,
            )

    output_path.write_bytes(html_bytes)
    digest = hashlib.sha256(html_bytes).hexdigest()
    metadata = {
        "url": task.url,
        "final_url": str(response.url),
        "downloaded_at": datetime.now(UTC).isoformat(),
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "content_encoding": response.headers.get("content-encoding", ""),
        "raw_byte_count": len(raw_bytes),
        "byte_count": len(html_bytes),
        "sha256": digest,
        "tool": TOOL_NAME,
        "allowed_statuses": task.allowed_statuses,
        "table_ids": task.table_ids,
        "wallclock_ms": wallclock_ms,
        "discovered_visible_table_ids": discovered_visible,
        "discovered_commented_table_ids": discovered_commented,
        "discovered_table_ids": discovered_table_ids,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    return FetchResult(
        task=task,
        output_path=output_path,
        metadata_path=metadata_path,
        status_code=response.status_code,
        byte_count=len(html_bytes),
        sha256=digest,
        wallclock_ms=wallclock_ms,
        discovered_table_ids=discovered_table_ids,
    )


def _endpoint_display_name(example: RawExample) -> str:
    return f"{example.endpoint}/{example.example_id}"


def download_corpus(
    examples: Sequence[RawExample],
    output_root: Path,
    *,
    force: bool,
    max_requests: int | None,
    pilot: bool,
) -> tuple[list[FetchResult], list[tuple[str, Exception]], DownloadStats]:
    """Download the full catalog sequentially."""
    stats = DownloadStats()
    results: list[FetchResult] = []
    failures: list[tuple[str, Exception]] = []

    tasks_to_run: list[tuple[RawExample, FetchTask]] = []
    for example in examples:
        for task in example.tasks:
            tasks_to_run.append((example, task))

    if pilot:
        tasks_to_run = tasks_to_run[:10]

    if max_requests is not None and len(tasks_to_run) > max_requests:
        raise RawDownloadError(f"Would make {len(tasks_to_run)} requests but --max-requests is {max_requests}")

    rate_limit_interval = float(os.environ.get("BASKETBALL_REF_RATE_LIMIT_INTERVAL", DEFAULT_RATE_LIMIT_INTERVAL))
    rate_limit_jitter = float(os.environ.get("BASKETBALL_REF_RATE_LIMIT_JITTER", DEFAULT_RATE_LIMIT_JITTER))

    service = HTTPService(
        cache=DEFAULT_CACHE,
        rate_limit_interval=rate_limit_interval,
        rate_limit_jitter=rate_limit_jitter,
    )

    total = len(tasks_to_run)
    logger.info("Starting download of %d URL(s) under %s", total, output_root)
    logger.info("Rate limit: %.1fs base + %.1fs jitter", rate_limit_interval, rate_limit_jitter)

    start_all = time.perf_counter()
    for index, (example, task) in enumerate(tasks_to_run, start=1):
        label = f"{_endpoint_display_name(example)} -> {task.relative_path}"
        try:
            result = _fetch_one(service, task, output_root, force=force)
            if result.skipped:
                logger.info(
                    "[%d/%d] SKIP %s (%d tables: %s)",
                    index,
                    total,
                    label,
                    len(result.discovered_table_ids),
                    ",".join(result.discovered_table_ids) or "(none)",
                )
                stats.skipped += 1
            else:
                logger.info(
                    "[%d/%d] OK %s (%d bytes, %d ms, %d tables: %s)",
                    index,
                    total,
                    label,
                    result.byte_count,
                    result.wallclock_ms,
                    len(result.discovered_table_ids),
                    ",".join(result.discovered_table_ids) or "(none)",
                )
                stats.fetched += 1
                stats.total_bytes += result.byte_count
            results.append(result)
        except (httpx.HTTPStatusError, RateLimitJailed, RawDownloadError) as exc:
            logger.error("[%d/%d] FAIL %s: %s", index, total, label, exc)
            stats.failed += 1
            failures.append((label, exc))
            if isinstance(exc, RateLimitJailed):
                logger.error("Rate-limit jail detected; aborting run to avoid escalation.")
                break
        except Exception as exc:  # noqa: BLE001
            logger.exception("[%d/%d] ERROR %s: %s", index, total, label, exc)
            stats.failed += 1
            failures.append((label, exc))

    stats.wallclock_seconds = time.perf_counter() - start_all
    return results, failures, stats


# ---------------------------------------------------------------------------
# Manifest and reporting
# ---------------------------------------------------------------------------


def write_manifest(
    output_root: Path,
    examples: Sequence[RawExample],
    stats: DownloadStats,
) -> None:
    """Write a corpus-level manifest from on-disk sidecars."""
    fixtures: list[dict[str, Any]] = []
    endpoint_counts: dict[str, int] = {}

    for meta_path in sorted(output_root.rglob("*.meta.json")):
        rel_meta = meta_path.relative_to(output_root)
        if rel_meta.parts[0] == "_failures":
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        fixture_path = rel_meta.with_suffix("").with_suffix("")  # strips .meta.json
        endpoint = fixture_path.parts[0]
        endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        fixtures.append(
            {
                "path": str(fixture_path).replace("\\", "/"),
                "url": meta.get("url"),
                "sha256": meta.get("sha256"),
                "byte_count": meta.get("byte_count"),
                "status_code": meta.get("status_code"),
            }
        )

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "tool": TOOL_NAME,
        "corpus_root": str(output_root),
        "stats": {
            "total_fixtures": len(fixtures),
            "endpoints_covered": len(endpoint_counts),
            "fetched": stats.fetched,
            "skipped": stats.skipped,
            "failed": stats.failed,
            "total_bytes": stats.total_bytes,
            "wallclock_seconds": round(stats.wallclock_seconds, 2),
            "effective_rps": round(len(fixtures) / stats.wallclock_seconds, 3) if stats.wallclock_seconds else 0.0,
        },
        "endpoint_counts": endpoint_counts,
        "fixtures": fixtures,
    }

    manifest_path = output_root / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=False), encoding="utf-8")
    logger.info("Wrote manifest: %s", manifest_path)


def print_summary(
    examples: Sequence[RawExample],
    stats: DownloadStats,
    failures: list[tuple[str, Exception]],
) -> None:
    total_endpoints = len({example.endpoint for example in examples})
    print("\n" + "=" * 70)
    print("RAW DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"Endpoints in catalog: {total_endpoints}")
    print(f"Total tasks:          {stats.fetched + stats.skipped + stats.failed}")
    print(f"Fetched:              {stats.fetched}")
    print(f"Skipped (present):    {stats.skipped}")
    print(f"Failed:               {stats.failed}")
    print(f"Total bytes:          {stats.total_bytes:,}")
    print(f"Wall-clock seconds:   {stats.wallclock_seconds:.1f}")
    if stats.wallclock_seconds > 0:
        print(f"Effective req/sec:    {(stats.fetched + stats.skipped) / stats.wallclock_seconds:.3f}")
    if failures:
        print("\nFailures:")
        for label, exc in failures:
            print(f"  - {label}: {exc}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download raw Basketball-Reference HTML for every endpoint.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory to store the raw HTML corpus",
    )
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Run a 10-request pilot only",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Refetch files even if they already exist",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=None,
        help="Abort if the run would exceed this many requests",
    )
    parser.add_argument(
        "--endpoint",
        action="append",
        default=[],
        help="Only download examples for this endpoint or CSV page-family (can repeat)",
    )
    parser.add_argument(
        "--csv",
        default=str(DEFAULT_CSV_PATH),
        help="Path to the BREF page-family inventory CSV (default: %(default)s)",
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Exclude CSV page-family examples (ENDPOINTS corpus only)",
    )
    parser.add_argument(
        "--csv-only",
        action="store_true",
        help="Fetch only CSV page-family examples (skip ENDPOINTS corpus)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console log level",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    # Build the merged catalog: ENDPOINTS corpus + CSV page families.
    if args.csv_only:
        examples: list[RawExample] = _build_csv_catalog(Path(args.csv))
    elif args.no_csv:
        examples = list(build_catalog())
    else:
        examples = list(build_catalog()) + _build_csv_catalog(Path(args.csv))

    if args.endpoint:
        selected = set(args.endpoint)
        examples = [example for example in examples if example.endpoint in selected]
        if not examples:
            logger.warning("No examples matched --endpoint filter: %s", sorted(selected))

    try:
        results, failures, stats = download_corpus(
            examples=examples,
            output_root=output_root,
            force=args.force,
            max_requests=args.max_requests,
            pilot=args.pilot,
        )
    except RawDownloadError as exc:
        logger.error("Download aborted: %s", exc)
        return 1

    write_manifest(output_root, examples, stats)
    print_summary(examples, stats, failures)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
