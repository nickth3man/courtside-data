"""HTTP layer: rate-limited, retried requests plus per-endpoint fetch methods.

Legacy endpoints (standings, box scores, schedule, play-by-play, season
totals, search) have bespoke methods using dedicated page classes from
``courtside_data.html``. Generic endpoints are declared in
``courtside_data.endpoints`` and served by :meth:`HTTPService.fetch_table`,
which the generated client functions call directly.
"""

from __future__ import annotations

import os
import random
import re
import threading
import time
from collections.abc import Callable
from datetime import UTC
from typing import Any, ClassVar

import httpx
import stamina
from hishel.httpx import SyncCacheTransport
from lxml import html
from parsel import Selector

from courtside_data.data import TEAM_TO_TEAM_ABBREVIATION, PlayerData, Team, TeamTotal
from courtside_data.endpoints import ENDPOINTS, TableEndpoint
from courtside_data.errors import InvalidDate, InvalidPlayerAndSeason
from courtside_data.html import (
    BoxScoresPage,
    DailyBoxScoresPage,
    DailyLeadersPage,
    GenericTable,
    PlayByPlayPage,
    PlayerAdvancedSeasonTotalsTable,
    PlayerPage,
    PlayerSeasonBoxScoresPage,
    PlayerSeasonTotalTable,
    SchedulePage,
    SearchPage,
    StandingsPage,
    extract_commented_table,
)

_DEFAULT_RATE_LIMIT_INTERVAL = 3.5
_DEFAULT_RATE_LIMIT_JITTER = 1.2
_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
_RETRY_ATTEMPTS = 3
# Basketball-Reference can send Retry-After values of an hour or more when a
# session is jailed. stamina uses a hook-returned float verbatim (wait_max
# does not apply to it), so cap it to keep a single request from sleeping
# for the full jail duration.
_MAX_RETRY_AFTER_WAIT = 60.0


def _parse_retry_after(value: str) -> float:
    """Parse Retry-After header value, returning seconds to wait.

    Handles both integer seconds and HTTP-date formats per RFC 9110.
    """
    try:
        return float(value)
    except ValueError:
        pass
    # HTTP-date format: parse RFC 2822 date
    import email.utils as eutils
    from datetime import datetime

    parsed = eutils.parsedate_tz(value)
    if parsed is not None:
        retry_time = datetime(*parsed[:6], tzinfo=UTC)
        now = datetime.now(UTC)
        wait = (retry_time - now).total_seconds()
        return max(wait, 1.0)
    return 5.0


def _should_retry(exc: Exception) -> bool | float:
    """Custom stamina retry predicate.

    Returns True to retry with default backoff, a float to retry after
    that many seconds (honors Retry-After), or False to abort.
    """
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in (429, 502, 503, 504):
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after is not None:
                return min(_parse_retry_after(retry_after), _MAX_RETRY_AFTER_WAIT)
            return True
        # Do NOT retry other 4xx (400, 401, 403, 404, etc.)
        return False
    return False


def build_client(cache: bool = False, timeout: httpx.Timeout = _DEFAULT_TIMEOUT) -> httpx.Client:
    """Build the httpx client used by HTTPService.

    With cache=True, responses are cached per RFC 9111 via hishel's
    SQLite-backed storage.
    """
    transport: httpx.BaseTransport = httpx.HTTPTransport()
    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(transport=transport, follow_redirects=True, timeout=timeout)


class HTTPService:
    BASE_URL = "https://www.basketball-reference.com"
    _last_request_time: ClassVar[float] = float("-inf")
    _rate_limit_lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(
        self,
        parser: Any,
        rate_limit_interval: float | None = None,
        rate_limit_jitter: float | None = None,
        session: httpx.Client | None = None,
        time_func: Callable[[], float] | None = None,
        sleep: Callable[[float], None] | None = None,
        random_func: Callable[[float, float], float] | None = None,
        timeout: httpx.Timeout | None = None,
        cache: bool = False,
    ) -> None:
        self.parser = parser
        # Constructor param > env var > default
        if rate_limit_interval is not None:
            self._rate_limit_interval = rate_limit_interval
        else:
            self._rate_limit_interval = float(
                os.environ.get("BASKETBALL_REF_RATE_LIMIT_INTERVAL", _DEFAULT_RATE_LIMIT_INTERVAL)
            )

        if rate_limit_jitter is not None:
            self._rate_limit_jitter = rate_limit_jitter
        else:
            self._rate_limit_jitter = float(
                os.environ.get("BASKETBALL_REF_RATE_LIMIT_JITTER", _DEFAULT_RATE_LIMIT_JITTER)
            )

        self._timeout = timeout if timeout is not None else _DEFAULT_TIMEOUT
        self._session = session if session is not None else build_client(cache=cache, timeout=self._timeout)

        # Injectable dependencies for testing
        self._time = time_func if time_func is not None else time.monotonic
        self._sleep = sleep if sleep is not None else time.sleep
        self._random = random_func if random_func is not None else random.uniform

    def _apply_rate_limiting(self) -> None:
        current_time = self._time()
        with self._rate_limit_lock:
            time_since_last = current_time - self.__class__._last_request_time
            if self._rate_limit_interval > 0 and time_since_last < self._rate_limit_interval:
                jitter = self._random(0.0, self._rate_limit_jitter)
                self._sleep((self._rate_limit_interval - time_since_last) + jitter)
            self.__class__._last_request_time = self._time()

    def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        self._apply_rate_limiting()
        response = None
        for attempt in stamina.retry_context(
            on=_should_retry,
            attempts=_RETRY_ATTEMPTS,
            wait_initial=1.0,
            wait_max=10.0,
            wait_jitter=0.5,
        ):
            with attempt:
                response = self._session.get(url=url, **kwargs)
                response.raise_for_status()
        assert response is not None  # retry_context either yields a response or raises
        return response

    def _get_selector(self, url: str) -> Selector:
        """Fetch a page (no redirects) and wrap the body in a parsel Selector."""
        response = self._get(url=url, follow_redirects=False)
        response.raise_for_status()
        return Selector(text=response.text)

    def _get_html(self, url: str, **kwargs: Any) -> html.HtmlElement:
        """Fetch a page, raise on HTTP errors, and parse the body with lxml."""
        response = self._get(url=url, **kwargs)
        response.raise_for_status()
        return html.fromstring(response.content)

    @staticmethod
    def _clean_text(values: list[str]) -> str:
        return re.sub(r"\s+", " ", " ".join(values)).strip()

    @classmethod
    def _parse_transaction_list(cls, selector: Selector) -> list[dict[str, Any]]:
        transactions = []
        for day in selector.css("ul.page_index > li"):
            date = cls._clean_text(day.xpath("./span//text()").getall())
            for transaction in day.xpath("./p[normalize-space()]"):
                linked_resources = []
                from_team_abbreviations = []
                to_team_abbreviations = []
                for link in transaction.css("a"):
                    from_team = link.attrib.get("data-attr-from")
                    to_team = link.attrib.get("data-attr-to")
                    if from_team:
                        from_team_abbreviations.append(from_team)
                    if to_team:
                        to_team_abbreviations.append(to_team)
                    linked_resources.append(
                        {
                            "text": cls._clean_text(link.css("::text").getall()),
                            "href": link.attrib.get("href", ""),
                            "from_team_abbreviation": from_team or "",
                            "to_team_abbreviation": to_team or "",
                        }
                    )

                transactions.append(
                    {
                        "date": date,
                        "transaction": cls._clean_text(transaction.css("::text").getall()),
                        "from_team_abbreviations": from_team_abbreviations,
                        "to_team_abbreviations": to_team_abbreviations,
                        "linked_resources": linked_resources,
                    }
                )
        return transactions

    # ── Generic endpoint plumbing ───────────────────────────────────────

    def fetch_table(self, endpoint: TableEndpoint, **params: Any) -> list[dict[str, Any]]:
        """Fetch and parse a generic table endpoint described by ``endpoint``.

        Resolution order: CSS ``table#<table_id>``, then a comment-wrapped
        table with ``commented_table_id``, then the transaction-list fallback,
        then an empty list.
        """
        if endpoint.custom:
            raise ValueError("Endpoint requires its bespoke HTTPService method, not fetch_table()")
        selector = self._get_selector(url=f"{HTTPService.BASE_URL}{endpoint.path.format(**params)}")

        table_selector: Selector | None = None
        if endpoint.table_id is not None:
            found = selector.css(f"table#{endpoint.table_id.format(**params)}")
            if found:
                table_selector = found[0]
        if table_selector is None and endpoint.commented_table_id is not None:
            table_selector = extract_commented_table(selector, endpoint.commented_table_id)

        if table_selector is None:
            if endpoint.transaction_list_fallback:
                return self._parse_transaction_list(selector)
            return []

        table = GenericTable(table_selector, use_header_fallback=endpoint.use_header_fallback)
        rows = self.parser.parse_generic_table(table)
        if endpoint.projection is not None:
            rows = [{key: row.get(key, "") for key in endpoint.projection} for row in rows]
        return rows

    # ── Legacy endpoints (dedicated page classes and parser chains) ─────

    def standings(self, season_end_year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}.html"

        page = StandingsPage(html=self._get_html(url=url, follow_redirects=False))
        return self.parser.parse_division_standings(
            standings=page.division_standings.eastern_conference_table.rows
        ) + self.parser.parse_division_standings(standings=page.division_standings.western_conference_table.rows)

    def player_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/friv/dailyleaders.cgi?month={month}&day={day}&year={year}"

        response = self._get(url=url, follow_redirects=False)

        response.raise_for_status()

        if response.status_code == httpx.codes.OK:
            page = DailyLeadersPage(html=html.fromstring(response.content))
            if not page.daily_leaders:
                raise InvalidDate(day=day, month=month, year=year)
            return self.parser.parse_player_box_scores(box_scores=page.daily_leaders)

        raise InvalidDate(day=day, month=month, year=year)

    def _player_season_box_scores_page(self, player_identifier: str, season_end_year: int) -> PlayerSeasonBoxScoresPage:
        # Makes assumption that basketball reference pattern of breaking out player pathing using first character of
        # surname can be derived from the fact that basketball reference also has a pattern of player identifiers
        # starting with first few characters of player's surname
        url = f"{HTTPService.BASE_URL}/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}"

        return PlayerSeasonBoxScoresPage(html=self._get_html(url=url, follow_redirects=False))

    def regular_season_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        page = self._player_season_box_scores_page(player_identifier, season_end_year)
        if page.regular_season_box_scores_table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self.parser.parse_player_season_box_scores(
            box_scores=page.regular_season_box_scores_table.rows, include_inactive_games=include_inactive_games
        )

    def playoff_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        page = self._player_season_box_scores_page(player_identifier, season_end_year)
        if page.playoff_box_scores_table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self.parser.parse_player_season_box_scores(
            box_scores=page.playoff_box_scores_table.rows, include_inactive_games=include_inactive_games
        )

    def play_by_play(self, home_team: Team, day: int, month: int, year: int) -> list[dict[str, Any]]:
        # Look up the actual game URL from the daily boxscores page
        # instead of hardcoding the game index (handles doubleheaders).
        boxscores_page = DailyBoxScoresPage(
            html=self._get_html(
                url=f"{HTTPService.BASE_URL}/boxscores/",
                params={"day": day, "month": month, "year": year},
            )
        )
        abbr = TEAM_TO_TEAM_ABBREVIATION[home_team]
        game_url_path = None
        for path in boxscores_page.game_url_paths:
            if path.endswith(f"0{abbr}.html") or path.endswith(f"1{abbr}.html"):
                game_url_path = path
                break
        if game_url_path is None:
            raise InvalidDate(day=day, month=month, year=year)
        url = f"{HTTPService.BASE_URL}/boxscores/pbp/{game_url_path.split('/')[-1]}"
        page = PlayByPlayPage(html=self._get_html(url=url))

        return self.parser.parse_play_by_plays(
            play_by_plays=page.play_by_play_table.rows,
            away_team_name=page.away_team_name,
            home_team_name=page.home_team_name,
        )

    def players_advanced_season_totals(
        self, season_end_year: int, include_combined_values: bool = False
    ) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}_advanced.html"

        table = PlayerAdvancedSeasonTotalsTable(html=self._get_html(url=url))
        return self.parser.parse_player_advanced_season_totals(totals=table.get_rows(include_combined_values))

    def players_season_totals(self, season_end_year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}_totals.html"

        table = PlayerSeasonTotalTable(html=self._get_html(url=url))
        return self.parser.parse_player_season_totals(totals=table.rows)

    def schedule_for_month(self, url: str) -> list[dict[str, Any]]:
        page = SchedulePage(html=self._get_html(url=url))
        return self.parser.parse_scheduled_games(games=page.rows)

    def season_schedule(self, season_end_year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}_games.html"

        page = SchedulePage(html=self._get_html(url=url))
        season_schedule_values = self.parser.parse_scheduled_games(games=page.rows)

        for month_url_path in page.other_months_schedule_urls:
            url = f"{HTTPService.BASE_URL}{month_url_path}"
            monthly_schedule = self.schedule_for_month(url=url)
            season_schedule_values.extend(monthly_schedule)

        return season_schedule_values

    def team_box_score(self, game_url_path: str) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/{game_url_path.lstrip('/')}"

        page = BoxScoresPage(self._get_html(url=url))
        combined_team_totals = [
            TeamTotal(team_abbreviation=table.team_abbreviation, totals=table.team_totals)
            for table in page.basic_statistics_tables
        ]

        if len(combined_team_totals) < 2:
            raise ValueError(f"Expected 2 team totals in box score page, got {len(combined_team_totals)}")
        return self.parser.parse_team_totals(
            first_team_totals=combined_team_totals[0],
            second_team_totals=combined_team_totals[1],
        )

    def team_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/boxscores/"

        page = DailyBoxScoresPage(html=self._get_html(url=url, params={"day": day, "month": month, "year": year}))

        if not page.game_url_paths:
            raise InvalidDate(day=day, month=month, year=year)

        return [
            box_score
            for game_url_path in page.game_url_paths
            for box_score in self.team_box_score(game_url_path=game_url_path)
        ]

    def search(self, term: str) -> dict[str, list[dict[str, Any]]]:
        response = self._get(url=f"{HTTPService.BASE_URL}/search/search.fcgi", params={"search": term})

        response.raise_for_status()

        player_results: list[dict[str, Any]] = []

        if str(response.url).startswith(f"{HTTPService.BASE_URL}/search/search.fcgi"):
            page = SearchPage(html=html.fromstring(response.content))
            parsed_results = self.parser.parse_player_search_results(nba_aba_baa_players=page.nba_aba_baa_players)
            player_results += parsed_results["players"]

            # Guard against pagination loops where the next-page URL doesn't
            # advance (e.g., when a page points back to itself). Without this,
            # a malformed or stale "Next" link can cause an infinite loop.
            seen_pagination_urls: set[str] = set()
            while page.nba_aba_baa_players_pagination_url is not None:
                pagination_url = page.nba_aba_baa_players_pagination_url
                if pagination_url in seen_pagination_urls:
                    break
                seen_pagination_urls.add(pagination_url)

                response = self._get(url=f"{HTTPService.BASE_URL}/search/{pagination_url}")

                response.raise_for_status()

                page = SearchPage(html=html.fromstring(response.content))

                parsed_results = self.parser.parse_player_search_results(nba_aba_baa_players=page.nba_aba_baa_players)
                player_results += parsed_results["players"]

        elif str(response.url).startswith(f"{HTTPService.BASE_URL}/players"):
            player_page = PlayerPage(html=html.fromstring(response.content))
            if player_page.totals_table is None:
                league_abbreviations: set[str] = set()
            else:
                league_abbreviations = {
                    row.league_abbreviation
                    for row in player_page.totals_table.rows
                    if row.league_abbreviation is not None
                }
            data = PlayerData(
                name=player_page.name,
                resource_location=str(response.url),
                league_abbreviations=league_abbreviations,
            )
            player_results += [self.parser.parse_player_data(player=data)]

        return {"players": player_results}

    # ── Generic endpoints with bespoke behavior ─────────────────────────

    def standings_by_date(self, season_end_year: int) -> list[dict[str, Any]]:
        endpoint = ENDPOINTS["standings_by_date"]
        standings: list[dict[str, Any]] = []
        for conference in ["eastern_conference", "western_conference"]:
            url = (
                f"{HTTPService.BASE_URL}{endpoint.path.format(season_end_year=season_end_year, conference=conference)}"
            )
            selector = self._get_selector(url=url)
            table_selector = selector.css(f"table#{endpoint.table_id}")
            if table_selector:
                table = GenericTable(table_selector[0])
                standings.extend(self.parser.parse_generic_table(table))
        return standings
