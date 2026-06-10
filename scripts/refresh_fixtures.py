#!/usr/bin/env python3
import argparse
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests
from lxml import html

DEFAULT_OUTPUT_ROOT = Path("staged_fixtures")
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_DELAY_SECONDS = 8
DEFAULT_MAX_REQUESTS = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class FixtureRefreshError(RuntimeError):
    pass


@dataclass(frozen=True)
class Fixture:
    key: str
    url: str
    path: Path
    checks: tuple
    allowed_statuses: tuple = (200,)


@dataclass(frozen=True)
class RefreshResult:
    fixture: Fixture
    output_path: Path
    metadata_path: Path
    request_count: int
    byte_count: int
    sha256: str


def refresh_fixture(fixture, output_root, get=requests.get, sleep=time.sleep):
    headers = {"User-Agent": USER_AGENT}
    response = get(url=fixture.url, timeout=DEFAULT_TIMEOUT_SECONDS, headers=headers)
    validate_response(response=response, fixture=fixture)
    html_bytes = response.content

    for check in fixture.checks:
        check(html_bytes)

    output_path = output_root / fixture.path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(html_bytes)

    digest = sha256(html_bytes)
    metadata_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    metadata_path.write_text(
        json.dumps(
            {
                "url": fixture.url,
                "downloaded_at": datetime.now(UTC).isoformat(),
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "sha256": digest,
                "byte_count": len(html_bytes),
                "tool": "requests",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf8",
    )
    sleep(0)
    return RefreshResult(
        fixture=fixture,
        output_path=output_path,
        metadata_path=metadata_path,
        request_count=1,
        byte_count=len(html_bytes),
        sha256=digest,
    )


def validate_response(response, fixture):
    if response.status_code in {403, 429}:
        raise FixtureRefreshError(f"Stopping fixture refresh: {response.status_code} received for {fixture.url}")

    if response.status_code not in fixture.allowed_statuses:
        raise FixtureRefreshError(
            "Expected HTTP status one of {expected} for {url}, got {status_code}".format(
                expected=", ".join(str(status) for status in fixture.allowed_statuses),
                url=fixture.url,
                status_code=response.status_code,
            )
        )

    if not response.url.startswith("https://www.basketball-reference.com/"):
        raise FixtureRefreshError(f"Unexpected response URL for {fixture.url}: {response.url}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise FixtureRefreshError(f"Expected text/html for {fixture.url}, got {content_type}")

    blocked_markers = (
        b"Rate Limited Request",
        b"Bot/Scraping/Crawler Traffic",
        b"Too Many Requests",
    )
    if any(marker in response.content for marker in blocked_markers):
        raise FixtureRefreshError(f"Blocked or rate-limited content detected for {fixture.url}")


def verify_html_fixture(html_bytes):
    try:
        document = html.fromstring(html_bytes)
    except Exception as error:
        raise FixtureRefreshError("Downloaded HTML could not be parsed by lxml") from error

    if not document.xpath("//html"):
        raise FixtureRefreshError("Downloaded content does not look like an HTML document")


def verify_box_score_fixture(html_bytes):
    document = html.fromstring(html_bytes)
    basic_tables = document.xpath('//table[contains(@id, "-game-basic")]')
    if len(basic_tables) < 2:
        raise FixtureRefreshError("Box score fixture must contain at least two game-basic tables")

    totals = document.xpath('//table[contains(@id, "-game-basic")]//tfoot/tr')
    if len(totals) < 2:
        raise FixtureRefreshError("Box score fixture must contain team totals in game-basic table footers")


def verify_table_exists(*table_ids):
    def verify(html_bytes):
        document = html.fromstring(html_bytes)
        for table_id in table_ids:
            if document.xpath(f'//table[@id="{table_id}"]'):
                return
        html_text = html_bytes.decode("utf-8", errors="ignore")
        for table_id in table_ids:
            if f'id="{table_id}"' in html_text:
                return
            if f"id='{table_id}'" in html_text:
                return
        raise FixtureRefreshError("Expected table with id one of {ids} was not found".format(ids=", ".join(table_ids)))

    return verify


def verify_xpath_exists(xpath, description):
    def verify(html_bytes):
        document = html.fromstring(html_bytes)
        if document.xpath(xpath):
            return
        raise FixtureRefreshError(f"Expected {description} was not found")

    return verify


def verify_search_fixture(html_bytes):
    document = html.fromstring(html_bytes)
    if document.xpath('//div[contains(@class, "search-item")]'):
        return
    if document.xpath('//h1[contains(., "Search Results") or contains(., "Search")]'):
        return
    if document.xpath('//form[contains(@action, "search.fcgi")]'):
        return
    raise FixtureRefreshError("Search fixture must contain search results or the search form")


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def _checks_for_fixture_key(key):
    if key.startswith("boxscore_index_"):
        return (verify_html_fixture,)
    if key.startswith("boxscore_"):
        return (verify_html_fixture, verify_box_score_fixture)
    if key.startswith("player_advanced_season_totals_"):
        return (verify_html_fixture, verify_table_exists("advanced"))
    if key.startswith("players_season_totals_"):
        return (verify_html_fixture, verify_table_exists("totals", "totals_stats"))
    if key.startswith("play_by_play_"):
        return (verify_html_fixture, verify_table_exists("pbp"))
    if key.startswith("player_box_scores_daily_"):
        return (verify_html_fixture, verify_table_exists("stats"))
    if key.startswith("player_box_scores_gamelog_"):
        return (verify_html_fixture, verify_table_exists("player_game_log_reg", "pgl_basic"))
    if key.startswith("season_schedule_") and key not in {"season_schedule_not_found", "season_schedule_upcoming"}:
        return (verify_html_fixture, verify_table_exists("schedule"))
    if key.startswith("search_"):
        return (verify_html_fixture, verify_search_fixture)
    return (verify_html_fixture,)


_RAW_FIXTURES = {
    "boxscore_201701010ATL": Fixture(
        key="boxscore_201701010ATL",
        url="https://www.basketball-reference.com/boxscores/201701010ATL.html",
        path=Path("tests/integration/files/boxscores/2017/1/201701010ATL.html"),
        checks=(),
    ),
    "player_advanced_season_totals_2019": Fixture(
        key="player_advanced_season_totals_2019",
        url="https://www.basketball-reference.com/leagues/NBA_2019_advanced.html",
        path=Path("tests/integration/files/player_advanced_season_totals/2019.html"),
        checks=(),
    ),
    "players_season_totals_2018": Fixture(
        key="players_season_totals_2018",
        url="https://www.basketball-reference.com/leagues/NBA_2018_totals.html",
        path=Path("tests/integration/files/players_season_totals/2018.html"),
        checks=(),
    ),
    "play_by_play_201901010SAC": Fixture(
        key="play_by_play_201901010SAC",
        url="https://www.basketball-reference.com/boxscores/pbp/201901010SAC.html",
        path=Path("tests/integration/files/play_by_play/201901010SAC.html"),
        checks=(),
    ),
    "player_box_scores_daily_2018_1_1": Fixture(
        key="player_box_scores_daily_2018_1_1",
        url="https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=1&year=2018",
        path=Path("tests/integration/files/player_box_scores/2018/1/1.html"),
        checks=(),
    ),
    "player_box_scores_gamelog_2019_westbru01": Fixture(
        key="player_box_scores_gamelog_2019_westbru01",
        url="https://www.basketball-reference.com/players/w/westbru01/gamelog/2019",
        path=Path("tests/integration/files/player_box_scores/2019/westbru01.html"),
        checks=(),
    ),
    "player_box_scores_empty_2020_foobar": Fixture(
        key="player_box_scores_empty_2020_foobar",
        url="https://www.basketball-reference.com/players/",
        path=Path("tests/integration/files/player_box_scores/2020/foobar.html"),
        checks=(),
    ),
    "season_schedule_2018": Fixture(
        key="season_schedule_2018",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games.html",
        path=Path("tests/integration/files/schedule/2018/2018.html"),
        checks=(),
    ),
    "season_schedule_2018_october": Fixture(
        key="season_schedule_2018_october",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-october.html",
        path=Path("tests/integration/files/schedule/2018/october.html"),
        checks=(),
    ),
    "season_schedule_not_found": Fixture(
        key="season_schedule_not_found",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-blabla.html",
        path=Path("tests/integration/files/schedule/not-found.html"),
        checks=(),
        allowed_statuses=(404,),
    ),
    "season_schedule_upcoming": Fixture(
        key="season_schedule_upcoming",
        url="https://www.basketball-reference.com/boxscores/",
        path=Path("tests/integration/files/schedule/upcoming-games.html"),
        checks=(),
    ),
    "search_kobe": Fixture(
        key="search_kobe",
        url="https://www.basketball-reference.com/search/search.fcgi?search=kobe",
        path=Path("tests/integration/files/search/kobe.html"),
        checks=(),
    ),
    "search_ja_offset_0": Fixture(
        key="search_ja_offset_0",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=0",
        path=Path("tests/integration/files/search/ja/0.html"),
        checks=(),
    ),
    "search_ja_offset_1": Fixture(
        key="search_ja_offset_1",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=100",
        path=Path("tests/integration/files/search/ja/1.html"),
        checks=(),
    ),
    "search_ja_offset_2": Fixture(
        key="search_ja_offset_2",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=200",
        path=Path("tests/integration/files/search/ja/2.html"),
        checks=(),
    ),
    "search_ja_offset_3": Fixture(
        key="search_ja_offset_3",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=300",
        path=Path("tests/integration/files/search/ja/3.html"),
        checks=(),
    ),
    "search_ja_offset_4": Fixture(
        key="search_ja_offset_4",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=400",
        path=Path("tests/integration/files/search/ja/4.html"),
        checks=(),
    ),
    "search_ja_offset_5": Fixture(
        key="search_ja_offset_5",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=500",
        path=Path("tests/integration/files/search/ja/5.html"),
        checks=(),
    ),
    "search_ja_offset_6": Fixture(
        key="search_ja_offset_6",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=600",
        path=Path("tests/integration/files/search/ja/6.html"),
        checks=(),
    ),
    "search_ja_offset_7": Fixture(
        key="search_ja_offset_7",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=700",
        path=Path("tests/integration/files/search/ja/7.html"),
        checks=(),
    ),
    "search_ja_offset_8": Fixture(
        key="search_ja_offset_8",
        url="https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=800",
        path=Path("tests/integration/files/search/ja/8.html"),
        checks=(),
    ),
    # --- Phase 2: multi-era play-by-play ---
    "play_by_play_199911160ATL": Fixture(
        key="play_by_play_199911160ATL",
        url="https://www.basketball-reference.com/boxscores/pbp/199911160ATL.html",
        path=Path("tests/integration/files/play_by_play/199911160ATL.html"),
        checks=(),
    ),
    "play_by_play_200310290TOR": Fixture(
        key="play_by_play_200310290TOR",
        url="https://www.basketball-reference.com/boxscores/pbp/200310290TOR.html",
        path=Path("tests/integration/files/play_by_play/200310290TOR.html"),
        checks=(),
    ),
    "play_by_play_201810160GSW": Fixture(
        key="play_by_play_201810160GSW",
        url="https://www.basketball-reference.com/boxscores/pbp/201810160GSW.html",
        path=Path("tests/integration/files/play_by_play/201810160GSW.html"),
        checks=(),
    ),
    "play_by_play_201810270MIL": Fixture(
        key="play_by_play_201810270MIL",
        url="https://www.basketball-reference.com/boxscores/pbp/201810270MIL.html",
        path=Path("tests/integration/files/play_by_play/201810270MIL.html"),
        checks=(),
    ),
    "play_by_play_201810290MIL": Fixture(
        key="play_by_play_201810290MIL",
        url="https://www.basketball-reference.com/boxscores/pbp/201810290MIL.html",
        path=Path("tests/integration/files/play_by_play/201810290MIL.html"),
        checks=(),
    ),
    "play_by_play_201901010DEN": Fixture(
        key="play_by_play_201901010DEN",
        url="https://www.basketball-reference.com/boxscores/pbp/201901010DEN.html",
        path=Path("tests/integration/files/play_by_play/201901010DEN.html"),
        checks=(),
    ),
    # --- Phase 2: player advanced season totals ---
    "player_advanced_season_totals_2001": Fixture(
        key="player_advanced_season_totals_2001",
        url="https://www.basketball-reference.com/leagues/NBA_2001_advanced.html",
        path=Path("tests/integration/files/player_advanced_season_totals/2001.html"),
        checks=(),
    ),
    "player_advanced_season_totals_2016": Fixture(
        key="player_advanced_season_totals_2016",
        url="https://www.basketball-reference.com/leagues/NBA_2016_advanced.html",
        path=Path("tests/integration/files/player_advanced_season_totals/2016.html"),
        checks=(),
    ),
    "player_advanced_season_totals_2017": Fixture(
        key="player_advanced_season_totals_2017",
        url="https://www.basketball-reference.com/leagues/NBA_2017_advanced.html",
        path=Path("tests/integration/files/player_advanced_season_totals/2017.html"),
        checks=(),
    ),
    "player_advanced_season_totals_2018": Fixture(
        key="player_advanced_season_totals_2018",
        url="https://www.basketball-reference.com/leagues/NBA_2018_advanced.html",
        path=Path("tests/integration/files/player_advanced_season_totals/2018.html"),
        checks=(),
    ),
    # --- Phase 2: daily player box scores ---
    "player_box_scores_daily_2001_1_1": Fixture(
        key="player_box_scores_daily_2001_1_1",
        url="https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=1&year=2001",
        path=Path("tests/integration/files/player_box_scores/2001/1/1.html"),
        checks=(),
    ),
    "player_box_scores_daily_2003_11_3": Fixture(
        key="player_box_scores_daily_2003_11_3",
        url="https://www.basketball-reference.com/friv/dailyleaders.cgi?month=11&day=3&year=2003",
        path=Path("tests/integration/files/player_box_scores/2003/11/3.html"),
        checks=(),
    ),
    "player_box_scores_daily_2006_11_1": Fixture(
        key="player_box_scores_daily_2006_11_1",
        url="https://www.basketball-reference.com/friv/dailyleaders.cgi?month=11&day=1&year=2006",
        path=Path("tests/integration/files/player_box_scores/2006/11/1.html"),
        checks=(),
    ),
    "player_box_scores_daily_2015_12_18": Fixture(
        key="player_box_scores_daily_2015_12_18",
        url="https://www.basketball-reference.com/friv/dailyleaders.cgi?month=12&day=18&year=2015",
        path=Path("tests/integration/files/player_box_scores/2015/12/18.html"),
        checks=(),
    ),
    "player_box_scores_daily_2017_1_29": Fixture(
        key="player_box_scores_daily_2017_1_29",
        url="https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=29&year=2017",
        path=Path("tests/integration/files/player_box_scores/2017/1/29.html"),
        checks=(),
    ),
    "player_box_scores_daily_2017_12_12": Fixture(
        key="player_box_scores_daily_2017_12_12",
        url="https://www.basketball-reference.com/friv/dailyleaders.cgi?month=12&day=12&year=2017",
        path=Path("tests/integration/files/player_box_scores/2017/12/12.html"),
        checks=(),
    ),
    # --- Phase 2: player gamelog (multi-era) ---
    "player_box_scores_gamelog_2015_brownja01": Fixture(
        key="player_box_scores_gamelog_2015_brownja01",
        url="https://www.basketball-reference.com/players/b/brownja01/gamelog/2015",
        path=Path("tests/integration/files/player_box_scores/2015/brownja01.html"),
        checks=(),
    ),
    "player_box_scores_gamelog_2019_bradlav01": Fixture(
        key="player_box_scores_gamelog_2019_bradlav01",
        url="https://www.basketball-reference.com/players/b/bradlav01/gamelog/2019",
        path=Path("tests/integration/files/player_box_scores/2019/bradlav01.html"),
        checks=(),
    ),
    "player_box_scores_gamelog_2020_antetgi01": Fixture(
        key="player_box_scores_gamelog_2020_antetgi01",
        url="https://www.basketball-reference.com/players/a/antetgi01/gamelog/2020",
        path=Path("tests/integration/files/player_box_scores/2020/antetgi01.html"),
        checks=(),
    ),
    "player_box_scores_gamelog_2020_westbru01": Fixture(
        key="player_box_scores_gamelog_2020_westbru01",
        url="https://www.basketball-reference.com/players/w/westbru01/gamelog/2020",
        path=Path("tests/integration/files/player_box_scores/2020/westbru01.html"),
        checks=(),
    ),
    # --- Phase 2: players season totals (2001-2024, minus 2018 already registered) ---
    "players_season_totals_2001": Fixture(
        key="players_season_totals_2001",
        url="https://www.basketball-reference.com/leagues/NBA_2001_totals.html",
        path=Path("tests/integration/files/players_season_totals/2001.html"),
        checks=(),
    ),
    "players_season_totals_2002": Fixture(
        key="players_season_totals_2002",
        url="https://www.basketball-reference.com/leagues/NBA_2002_totals.html",
        path=Path("tests/integration/files/players_season_totals/2002.html"),
        checks=(),
    ),
    "players_season_totals_2003": Fixture(
        key="players_season_totals_2003",
        url="https://www.basketball-reference.com/leagues/NBA_2003_totals.html",
        path=Path("tests/integration/files/players_season_totals/2003.html"),
        checks=(),
    ),
    "players_season_totals_2004": Fixture(
        key="players_season_totals_2004",
        url="https://www.basketball-reference.com/leagues/NBA_2004_totals.html",
        path=Path("tests/integration/files/players_season_totals/2004.html"),
        checks=(),
    ),
    "players_season_totals_2005": Fixture(
        key="players_season_totals_2005",
        url="https://www.basketball-reference.com/leagues/NBA_2005_totals.html",
        path=Path("tests/integration/files/players_season_totals/2005.html"),
        checks=(),
    ),
    "players_season_totals_2006": Fixture(
        key="players_season_totals_2006",
        url="https://www.basketball-reference.com/leagues/NBA_2006_totals.html",
        path=Path("tests/integration/files/players_season_totals/2006.html"),
        checks=(),
    ),
    "players_season_totals_2007": Fixture(
        key="players_season_totals_2007",
        url="https://www.basketball-reference.com/leagues/NBA_2007_totals.html",
        path=Path("tests/integration/files/players_season_totals/2007.html"),
        checks=(),
    ),
    "players_season_totals_2008": Fixture(
        key="players_season_totals_2008",
        url="https://www.basketball-reference.com/leagues/NBA_2008_totals.html",
        path=Path("tests/integration/files/players_season_totals/2008.html"),
        checks=(),
    ),
    "players_season_totals_2009": Fixture(
        key="players_season_totals_2009",
        url="https://www.basketball-reference.com/leagues/NBA_2009_totals.html",
        path=Path("tests/integration/files/players_season_totals/2009.html"),
        checks=(),
    ),
    "players_season_totals_2010": Fixture(
        key="players_season_totals_2010",
        url="https://www.basketball-reference.com/leagues/NBA_2010_totals.html",
        path=Path("tests/integration/files/players_season_totals/2010.html"),
        checks=(),
    ),
    "players_season_totals_2011": Fixture(
        key="players_season_totals_2011",
        url="https://www.basketball-reference.com/leagues/NBA_2011_totals.html",
        path=Path("tests/integration/files/players_season_totals/2011.html"),
        checks=(),
    ),
    "players_season_totals_2012": Fixture(
        key="players_season_totals_2012",
        url="https://www.basketball-reference.com/leagues/NBA_2012_totals.html",
        path=Path("tests/integration/files/players_season_totals/2012.html"),
        checks=(),
    ),
    "players_season_totals_2013": Fixture(
        key="players_season_totals_2013",
        url="https://www.basketball-reference.com/leagues/NBA_2013_totals.html",
        path=Path("tests/integration/files/players_season_totals/2013.html"),
        checks=(),
    ),
    "players_season_totals_2014": Fixture(
        key="players_season_totals_2014",
        url="https://www.basketball-reference.com/leagues/NBA_2014_totals.html",
        path=Path("tests/integration/files/players_season_totals/2014.html"),
        checks=(),
    ),
    "players_season_totals_2015": Fixture(
        key="players_season_totals_2015",
        url="https://www.basketball-reference.com/leagues/NBA_2015_totals.html",
        path=Path("tests/integration/files/players_season_totals/2015.html"),
        checks=(),
    ),
    "players_season_totals_2016": Fixture(
        key="players_season_totals_2016",
        url="https://www.basketball-reference.com/leagues/NBA_2016_totals.html",
        path=Path("tests/integration/files/players_season_totals/2016.html"),
        checks=(),
    ),
    "players_season_totals_2017": Fixture(
        key="players_season_totals_2017",
        url="https://www.basketball-reference.com/leagues/NBA_2017_totals.html",
        path=Path("tests/integration/files/players_season_totals/2017.html"),
        checks=(),
    ),
    "players_season_totals_2019": Fixture(
        key="players_season_totals_2019",
        url="https://www.basketball-reference.com/leagues/NBA_2019_totals.html",
        path=Path("tests/integration/files/players_season_totals/2019.html"),
        checks=(),
    ),
    "players_season_totals_2020": Fixture(
        key="players_season_totals_2020",
        url="https://www.basketball-reference.com/leagues/NBA_2020_totals.html",
        path=Path("tests/integration/files/players_season_totals/2020.html"),
        checks=(),
    ),
    "players_season_totals_2021": Fixture(
        key="players_season_totals_2021",
        url="https://www.basketball-reference.com/leagues/NBA_2021_totals.html",
        path=Path("tests/integration/files/players_season_totals/2021.html"),
        checks=(),
    ),
    "players_season_totals_2022": Fixture(
        key="players_season_totals_2022",
        url="https://www.basketball-reference.com/leagues/NBA_2022_totals.html",
        path=Path("tests/integration/files/players_season_totals/2022.html"),
        checks=(),
    ),
    "players_season_totals_2023": Fixture(
        key="players_season_totals_2023",
        url="https://www.basketball-reference.com/leagues/NBA_2023_totals.html",
        path=Path("tests/integration/files/players_season_totals/2023.html"),
        checks=(),
    ),
    "players_season_totals_2024": Fixture(
        key="players_season_totals_2024",
        url="https://www.basketball-reference.com/leagues/NBA_2024_totals.html",
        path=Path("tests/integration/files/players_season_totals/2024.html"),
        checks=(),
    ),
    # --- Phase 2: season schedule (multi-era annual) ---
    "season_schedule_2000": Fixture(
        key="season_schedule_2000",
        url="https://www.basketball-reference.com/leagues/NBA_2000_games.html",
        path=Path("tests/integration/files/schedule/2000/2000.html"),
        checks=(),
    ),
    "season_schedule_2001": Fixture(
        key="season_schedule_2001",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games.html",
        path=Path("tests/integration/files/schedule/2001/2001.html"),
        checks=(),
    ),
    "season_schedule_2002": Fixture(
        key="season_schedule_2002",
        url="https://www.basketball-reference.com/leagues/NBA_2002_games.html",
        path=Path("tests/integration/files/schedule/2002/2002.html"),
        checks=(),
    ),
    "season_schedule_2005": Fixture(
        key="season_schedule_2005",
        url="https://www.basketball-reference.com/leagues/NBA_2005_games.html",
        path=Path("tests/integration/files/schedule/2005/2005.html"),
        checks=(),
    ),
    "season_schedule_2019": Fixture(
        key="season_schedule_2019",
        url="https://www.basketball-reference.com/leagues/NBA_2019_games.html",
        path=Path("tests/integration/files/schedule/2019/2019.html"),
        checks=(),
    ),
    "season_schedule_2020": Fixture(
        key="season_schedule_2020",
        url="https://www.basketball-reference.com/leagues/NBA_2020_games.html",
        path=Path("tests/integration/files/schedule/2020/2020.html"),
        checks=(),
    ),
    # --- Phase 2: season schedule 2001 monthly ---
    "season_schedule_2001_october": Fixture(
        key="season_schedule_2001_october",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-october.html",
        path=Path("tests/integration/files/schedule/2001/october.html"),
        checks=(),
    ),
    "season_schedule_2001_november": Fixture(
        key="season_schedule_2001_november",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-november.html",
        path=Path("tests/integration/files/schedule/2001/november.html"),
        checks=(),
    ),
    "season_schedule_2001_december": Fixture(
        key="season_schedule_2001_december",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-december.html",
        path=Path("tests/integration/files/schedule/2001/december.html"),
        checks=(),
    ),
    "season_schedule_2001_january": Fixture(
        key="season_schedule_2001_january",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-january.html",
        path=Path("tests/integration/files/schedule/2001/january.html"),
        checks=(),
    ),
    "season_schedule_2001_february": Fixture(
        key="season_schedule_2001_february",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-february.html",
        path=Path("tests/integration/files/schedule/2001/february.html"),
        checks=(),
    ),
    "season_schedule_2001_march": Fixture(
        key="season_schedule_2001_march",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-march.html",
        path=Path("tests/integration/files/schedule/2001/march.html"),
        checks=(),
    ),
    "season_schedule_2001_april": Fixture(
        key="season_schedule_2001_april",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-april.html",
        path=Path("tests/integration/files/schedule/2001/april.html"),
        checks=(),
    ),
    "season_schedule_2001_may": Fixture(
        key="season_schedule_2001_may",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-may.html",
        path=Path("tests/integration/files/schedule/2001/may.html"),
        checks=(),
    ),
    "season_schedule_2001_june": Fixture(
        key="season_schedule_2001_june",
        url="https://www.basketball-reference.com/leagues/NBA_2001_games-june.html",
        path=Path("tests/integration/files/schedule/2001/june.html"),
        checks=(),
    ),
    # --- Phase 2: season schedule 2018 remaining monthly ---
    "season_schedule_2018_november": Fixture(
        key="season_schedule_2018_november",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-november.html",
        path=Path("tests/integration/files/schedule/2018/november.html"),
        checks=(),
    ),
    "season_schedule_2018_december": Fixture(
        key="season_schedule_2018_december",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-december.html",
        path=Path("tests/integration/files/schedule/2018/december.html"),
        checks=(),
    ),
    "season_schedule_2018_january": Fixture(
        key="season_schedule_2018_january",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-january.html",
        path=Path("tests/integration/files/schedule/2018/january.html"),
        checks=(),
    ),
    "season_schedule_2018_february": Fixture(
        key="season_schedule_2018_february",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-february.html",
        path=Path("tests/integration/files/schedule/2018/february.html"),
        checks=(),
    ),
    "season_schedule_2018_march": Fixture(
        key="season_schedule_2018_march",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-march.html",
        path=Path("tests/integration/files/schedule/2018/march.html"),
        checks=(),
    ),
    "season_schedule_2018_april": Fixture(
        key="season_schedule_2018_april",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-april.html",
        path=Path("tests/integration/files/schedule/2018/april.html"),
        checks=(),
    ),
    "season_schedule_2018_may": Fixture(
        key="season_schedule_2018_may",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-may.html",
        path=Path("tests/integration/files/schedule/2018/may.html"),
        checks=(),
    ),
    "season_schedule_2018_june": Fixture(
        key="season_schedule_2018_june",
        url="https://www.basketball-reference.com/leagues/NBA_2018_games-june.html",
        path=Path("tests/integration/files/schedule/2018/june.html"),
        checks=(),
    ),
    # --- Phase 2: team box score index pages (day listings) ---
    "boxscore_index_20010101": Fixture(
        key="boxscore_index_20010101",
        url="https://www.basketball-reference.com/boxscores/?day=1&month=1&year=2001",
        path=Path("tests/integration/files/boxscores/2001/1/1/index.html"),
        checks=(),
    ),
    "boxscore_index_20170101": Fixture(
        key="boxscore_index_20170101",
        url="https://www.basketball-reference.com/boxscores/?day=1&month=1&year=2017",
        path=Path("tests/integration/files/boxscores/2017/1/1.html"),
        checks=(),
    ),
    "boxscore_index_20180101": Fixture(
        key="boxscore_index_20180101",
        url="https://www.basketball-reference.com/boxscores/?day=1&month=1&year=2018",
        path=Path("tests/integration/files/boxscores/2018/1/1/index.html"),
        checks=(),
    ),
    # --- Phase 2: team box score individual game pages ---
    "boxscore_200101010MIN": Fixture(
        key="boxscore_200101010MIN",
        url="https://www.basketball-reference.com/boxscores/200101010MIN.html",
        path=Path("tests/integration/files/boxscores/2001/1/1/200101010MIN.html"),
        checks=(),
    ),
    "boxscore_200101010POR": Fixture(
        key="boxscore_200101010POR",
        url="https://www.basketball-reference.com/boxscores/200101010POR.html",
        path=Path("tests/integration/files/boxscores/2001/1/1/200101010POR.html"),
        checks=(),
    ),
    "boxscore_201801010BRK": Fixture(
        key="boxscore_201801010BRK",
        url="https://www.basketball-reference.com/boxscores/201801010BRK.html",
        path=Path("tests/integration/files/boxscores/2018/1/1/201801010BRK.html"),
        checks=(),
    ),
    "boxscore_201801010CHI": Fixture(
        key="boxscore_201801010CHI",
        url="https://www.basketball-reference.com/boxscores/201801010CHI.html",
        path=Path("tests/integration/files/boxscores/2018/1/1/201801010CHI.html"),
        checks=(),
    ),
    "boxscore_201801010MIN": Fixture(
        key="boxscore_201801010MIN",
        url="https://www.basketball-reference.com/boxscores/201801010MIN.html",
        path=Path("tests/integration/files/boxscores/2018/1/1/201801010MIN.html"),
        checks=(),
    ),
    "boxscore_201801010TOR": Fixture(
        key="boxscore_201801010TOR",
        url="https://www.basketball-reference.com/boxscores/201801010TOR.html",
        path=Path("tests/integration/files/boxscores/2018/1/1/201801010TOR.html"),
        checks=(),
    ),
    # --- Phase 2: search fixtures (non-ja) ---
    "search_alonz": Fixture(
        key="search_alonz",
        url="https://www.basketball-reference.com/search/search.fcgi?search=Alonz",
        path=Path("tests/integration/files/search/Alonz.html"),
        checks=(),
    ),
    "search_alonzo_mourning": Fixture(
        key="search_alonzo_mourning",
        url="https://www.basketball-reference.com/search/search.fcgi?search=Alonzo+Mourning",
        path=Path("tests/integration/files/search/Alonzo Mourning.html"),
        checks=(),
    ),
    "search_dominique_wilkins": Fixture(
        key="search_dominique_wilkins",
        url="https://www.basketball-reference.com/search/search.fcgi?search=Dominique+Wilkins",
        path=Path("tests/integration/files/search/Dominique Wilkins.html"),
        checks=(),
    ),
    "search_rick_barry": Fixture(
        key="search_rick_barry",
        url="https://www.basketball-reference.com/search/search.fcgi?search=Rick+Barry",
        path=Path("tests/integration/files/search/Rick Barry.html"),
        checks=(),
    ),
    "search_jaebaebae": Fixture(
        key="search_jaebaebae",
        url="https://www.basketball-reference.com/search/search.fcgi?search=jaebaebae",
        path=Path("tests/integration/files/search/jaebaebae.html"),
        checks=(),
    ),
    "search_kobe_bryant": Fixture(
        key="search_kobe_bryant",
        url="https://www.basketball-reference.com/search/search.fcgi?search=kobe+bryant",
        path=Path("tests/integration/files/search/kobe bryant.html"),
        checks=(),
    ),
    # --- Phase 3: WNBA season totals ---
    "wnba_players_season_totals_2024": Fixture(
        key="wnba_players_season_totals_2024",
        url="https://www.basketball-reference.com/wnba/years/2024_totals.html",
        path=Path("tests/integration/files/wnba/players_season_totals/2024.html"),
        checks=(),
    ),
    "wnba_players_season_totals_2023": Fixture(
        key="wnba_players_season_totals_2023",
        url="https://www.basketball-reference.com/wnba/years/2023_totals.html",
        path=Path("tests/integration/files/wnba/players_season_totals/2023.html"),
        checks=(),
    ),
    "wnba_players_season_totals_2019": Fixture(
        key="wnba_players_season_totals_2019",
        url="https://www.basketball-reference.com/wnba/years/2019_totals.html",
        path=Path("tests/integration/files/wnba/players_season_totals/2019.html"),
        checks=(),
    ),
    # --- Phase 3: WNBA schedule ---
    "wnba_season_schedule_2024": Fixture(
        key="wnba_season_schedule_2024",
        url="https://www.basketball-reference.com/wnba/years/2024_games.html",
        path=Path("tests/integration/files/wnba/schedule/2024.html"),
        checks=(),
    ),
    "wnba_season_schedule_2023": Fixture(
        key="wnba_season_schedule_2023",
        url="https://www.basketball-reference.com/wnba/years/2023_games.html",
        path=Path("tests/integration/files/wnba/schedule/2023.html"),
        checks=(),
    ),
    # --- Phase 3: WNBA player gamelog ---
    "wnba_player_gamelog_2024_wilsoa01w": Fixture(
        key="wnba_player_gamelog_2024_wilsoa01w",
        url="https://www.basketball-reference.com/wnba/players/w/wilsoa01w/gamelog/2024",
        path=Path("tests/integration/files/wnba/player_box_scores/2024/wilsoa01w.html"),
        checks=(),
    ),
    # --- Phase 3: WNBA boxscore (2024 Finals Game 1 - NYL home) ---
    "wnba_boxscore_202410130NYL": Fixture(
        key="wnba_boxscore_202410130NYL",
        url="https://www.basketball-reference.com/wnba/boxscores/202410130NYL.html",
        path=Path("tests/integration/files/wnba/boxscores/202410130NYL.html"),
        checks=(),
    ),
    # --- Phase 3: NBA draft pages ---
    "nba_draft_2024": Fixture(
        key="nba_draft_2024",
        url="https://www.basketball-reference.com/draft/NBA_2024.html",
        path=Path("tests/integration/files/draft/NBA_2024.html"),
        checks=(),
    ),
    "nba_draft_2001": Fixture(
        key="nba_draft_2001",
        url="https://www.basketball-reference.com/draft/NBA_2001.html",
        path=Path("tests/integration/files/draft/NBA_2001.html"),
        checks=(),
    ),
    # --- Phase 3: ABA historical season totals ---
    "aba_players_season_totals_1972": Fixture(
        key="aba_players_season_totals_1972",
        url="https://www.basketball-reference.com/leagues/ABA_1972_totals.html",
        path=Path("tests/integration/files/aba/players_season_totals/1972.html"),
        checks=(),
    ),
}


FIXTURES = {
    key: Fixture(
        key=fixture.key,
        url=fixture.url,
        path=fixture.path,
        checks=_checks_for_fixture_key(key),
        allowed_statuses=fixture.allowed_statuses,
    )
    for key, fixture in _RAW_FIXTURES.items()
}


# ---------------------------------------------------------------------------
# Drift detection – maps fixture keys → pytest node IDs.
# Only keys with known snapshot (filecmp-based) tests are included.
# Phase 3 keys (wnba_*, aba_*, nba_draft_*) have no matching tests → skipped.
# ---------------------------------------------------------------------------
FIXTURE_KEY_TO_TEST = {
    # players_season_totals: 2001 … 2018 (1976-through-2000 have no snapshot tests)
    **{
        f"players_season_totals_{year}": (
            "tests/integration/client/test_players_season_totals.py"
            f"::Test{year}PlayerSeasonJSONTotals::test_{year}_json_output"
        )
        for year in range(2001, 2019)
    },
    # season_schedule: only 2001 and 2018 have snapshot tests
    "season_schedule_2001": (
        "tests/integration/client/test_season_schedule.py::Test2001SeasonScheduleCsvOutput::test_output"
    ),
    "season_schedule_2018": (
        "tests/integration/client/test_season_schedule.py::Test2018SeasonScheduleCsvOutput::test_output"
    ),
    # player_advanced_season_totals
    "player_advanced_season_totals_2001": (
        "tests/integration/client/test_players_advanced_season_totals.py"
        "::Test2001PlayerAdvancedSeasonTotalsJSONOutput"
        "::test_players_advanced_season_totals_json"
    ),
    "player_advanced_season_totals_2016": (
        "tests/integration/client/test_players_advanced_season_totals.py"
        "::Test2016PlayerAdvancedSeasonTotalsJSONOutput"
        "::test_players_advanced_season_totals_json"
    ),
    "player_advanced_season_totals_2017": (
        "tests/integration/client/test_players_advanced_season_totals.py"
        "::Test2017PlayerAdvancedSeasonTotalsJSONOutput"
        "::test_players_advanced_season_totals_json"
    ),
    "player_advanced_season_totals_2018": (
        "tests/integration/client/test_players_advanced_season_totals.py"
        "::Test2018PlayerAdvancedSeasonTotalsJSONOutput"
        "::test_players_advanced_season_totals_json"
    ),
    "player_advanced_season_totals_2019": (
        "tests/integration/client/test_players_advanced_season_totals.py"
        "::Test2019PlayerAdvancedSeasonTotalsJSONOutput"
        "::test_players_advanced_season_totals_json"
    ),
    # player_box_scores_daily
    "player_box_scores_daily_2001_1_1": (
        "tests/integration/client/test_player_box_scores.py::Test20010101::test_json_output"
    ),
}


def _expected_output_path_for_fixture_key(key):
    """Return the *expected* output path (relative to repo root) for a fixture key, or None."""
    m = re.match(r"^players_season_totals_(\d{4})$", key)
    if m:
        return Path(f"tests/integration/client/output/expected/players_season_totals/{m.group(1)}.json")

    m = re.match(r"^season_schedule_(\d{4})$", key)
    if m:
        return Path(f"tests/integration/client/output/expected/season_schedule/{m.group(1)}.csv")

    m = re.match(r"^player_advanced_season_totals_(\d{4})$", key)
    if m:
        return Path(f"tests/integration/client/output/expected/player_advanced_season_totals/{m.group(1)}.json")

    m = re.match(r"^player_box_scores_daily_(\d{4})_(\d+)_(\d+)$", key)
    if m:
        return Path(
            f"tests/integration/client/output/expected/player_box_scores/{m.group(1)}/{m.group(2)}/{m.group(3)}.json"
        )

    return None


def promote_to_final_destination(output_root, fixture, copyfile=shutil.copyfile):
    """Copy a staged fixture to its final destination in tests/integration/files/.

    Returns True on success, False if the staged file doesn't exist.
    """
    staged_path = output_root / fixture.path
    if not staged_path.exists():
        print(
            f"WARNING: staged fixture {staged_path} does not exist, skipping promotion",
            file=sys.stderr,
        )
        return False
    fixture.path.parent.mkdir(parents=True, exist_ok=True)
    copyfile(str(staged_path), str(fixture.path))
    return True


def check_expected_drift(fixture, output_root, run_pytest=subprocess.run):
    """Detect drift between generated and expected output for *fixture*.

    Returns a warning string if drift is detected, *None* otherwise.
    """
    node_id = FIXTURE_KEY_TO_TEST.get(fixture.key)
    if node_id is None:
        return None

    expected_path = _expected_output_path_for_fixture_key(fixture.key)
    if expected_path is None or not expected_path.exists():
        return None  # nothing to compare against yet

    try:
        result = run_pytest(
            [sys.executable, "-m", "pytest", "-q", "--no-header", "--tb=line", node_id],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return f"[drift] {fixture.key}: pytest timed out after 60s"

    if result.returncode != 0:
        return f"[drift] {fixture.key}: {node_id} failed (run scripts/regenerate_expected.py)"

    return None


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Safely stage refreshed Basketball-Reference HTML fixtures.")
    parser.add_argument("keys", nargs="*", help="Fixture keys to refresh")
    parser.add_argument("--keys", dest="keys_csv", help="Comma-separated fixture keys to refresh")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Staging root for refreshed fixtures")
    parser.add_argument("--max-requests", type=int, default=DEFAULT_MAX_REQUESTS, help="Maximum live requests per run")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY_SECONDS, help="Base delay between requests")
    parser.add_argument("--list", action="store_true", help="List available fixture keys")
    parser.add_argument("--skip-drift-check", action="store_true", help="Skip post-refresh drift detection")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.list:
        for key, fixture in sorted(FIXTURES.items()):
            print(f"{key}: {fixture.url} -> {fixture.path}")
        return 0

    keys = list(args.keys)
    if args.keys_csv:
        keys.extend(key.strip() for key in args.keys_csv.split(",") if key.strip())
    if not keys:
        raise FixtureRefreshError("Specify at least one fixture key, or use --list to inspect available keys")
    unknown_keys = sorted(key for key in keys if key not in FIXTURES)
    if unknown_keys:
        raise FixtureRefreshError("Unknown fixture keys: {keys}".format(keys=", ".join(unknown_keys)))
    if len(keys) > args.max_requests:
        raise FixtureRefreshError(f"Requested {len(keys)} fixtures but max requests is {args.max_requests}")

    output_root = Path(args.output_root)
    skip_drift = args.skip_drift_check
    drift_warnings = []

    for index, key in enumerate(keys):
        result = refresh_fixture(fixture=FIXTURES[key], output_root=output_root)
        print(f"Staged {key}: {result.output_path} ({result.byte_count} bytes, sha256={result.sha256})")

        if not skip_drift:
            promoted = promote_to_final_destination(output_root=output_root, fixture=FIXTURES[key])
            if promoted:
                warning = check_expected_drift(fixture=FIXTURES[key], output_root=output_root)
                if warning:
                    print(warning, file=sys.stderr)
                    drift_warnings.append(warning)

        if index < len(keys) - 1:
            time.sleep(args.delay + random.uniform(0, 2))

    n_total = len(keys)
    n_drift = len(drift_warnings)
    summary = f"Refreshed {n_total} fixtures."
    if drift_warnings:
        summary = f"{summary} {n_drift} warning(s): drift={n_drift}"
    else:
        summary = f"{summary} No drift detected."
    print(summary)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FixtureRefreshError as error:
        print(error)
        raise SystemExit(1) from error
