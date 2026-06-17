"""Bespoke endpoint handlers with multi-step fetch/parse logic."""

from __future__ import annotations

from typing import Any

import httpx
from parsel import Selector

from courtside_data import _parsing
from courtside_data.data import TEAM_TO_TEAM_ABBREVIATION, Team
from courtside_data.debug import current_debug_trace
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import InvalidDate, InvalidPlayerAndSeason
from courtside_data.generic_endpoints import find_table
from courtside_data.http_service import HTTPService
from courtside_data.schemas._fields import _team_field
from courtside_data.tables import GenericTable

_FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_PATH = "/friv/7-game-playoff-series-outcomes-22111.html"


class CustomEndpointHandler:
    """Multi-step endpoint implementations that require bespoke fetch/parse logic."""

    def __init__(self, http: HTTPService) -> None:
        self._http = http

    def _friv_7_game_playoff_series_outcomes(self, table_id: str) -> list[dict[str, Any]]:
        url = self._http._url(_FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_PATH)
        selector = self._http._get_selector(url=url)
        table = find_table(selector, table_id)
        if table is None:
            return []
        rows = [
            _parsing.parse_friv_playoff_outcomes_row(row) for row in table.css("tbody tr:not(.thead)") if row.css("td")
        ]
        trace = current_debug_trace()
        if trace is not None:
            trace.record("parse", "friv_playoff_outcomes_parsed", table_id=table_id, row_count=len(rows))
            trace.artifact("raw_rows", rows)
        return rows

    def friv_7_game_playoff_series_outcomes_team_is_down(self) -> list[dict[str, Any]]:
        """Return the team-is-down matrix from the seven-game series outcomes page."""
        return self._friv_7_game_playoff_series_outcomes("team-is-down")

    def friv_7_game_playoff_series_outcomes_team_is_tied(self) -> list[dict[str, Any]]:
        """Return the team-is-tied matrix from the seven-game series outcomes page."""
        return self._friv_7_game_playoff_series_outcomes("team-is-tied")

    def friv_7_game_playoff_series_outcomes_team_is_up(self) -> list[dict[str, Any]]:
        """Return the team-is-up matrix from the seven-game series outcomes page."""
        return self._friv_7_game_playoff_series_outcomes("team-is-up")

    def season_awards_voting(self, season_end_year: int, award: str) -> list[dict[str, Any]]:
        """Return one award voting table from ``/awards/awards_{year}.html``."""
        table_id = award.strip().lower().replace("-", "_")
        selector = self._http._get_selector(self._http._url(f"/awards/awards_{season_end_year}.html"))
        table = find_table(selector, table_id)
        if table is None:
            return []
        return [row for row, _ in _parsing.raw_rows_from_table(table)]

    def _generic_table_rows(self, selector: Selector, table_id: str) -> list[dict[str, Any]]:
        table_selector = find_table(selector, table_id)
        if table_selector is None:
            return []
        return [row for row, _ in _parsing.raw_rows_from_table(table_selector)]

    def _player_totals_rows(self, selector: Selector, table_id: str, *, include_combined: bool) -> list[dict[str, Any]]:
        table_selector = find_table(selector, table_id)
        if table_selector is None:
            return []

        rows: list[dict[str, Any]] = []
        endpoint_name = "players_advanced_season_totals" if table_id == "advanced" else "players_season_totals"
        for row_index, (row, metadata) in enumerate(_parsing.raw_rows_from_table(table_selector)):
            if not row.get("name_display") or not row.get("team_name_abbr"):
                continue
            if not include_combined and _parsing.is_combined_team(row):
                continue
            row["slug"] = _parsing.slug_from_metadata(metadata, "name_display")
            _parsing.require_slug(endpoint_name, row, row_index)
            if table_id == "advanced":
                row["is_combined_totals"] = _parsing.is_combined_team(row)
            rows.append(row)
        return rows

    def _player_season_box_score_rows(
        self,
        table_selector: Selector,
        *,
        include_inactive_games: bool,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row, metadata in _parsing.raw_rows_from_table(table_selector):
            if not row.get("date") and not row.get("date_game"):
                continue

            active = "colspan" not in metadata.get("is_starter", {})
            if not active and not include_inactive_games:
                continue

            row["active"] = active
            rows.append(row)
        return rows

    def _schedule_rows(self, selector: Selector) -> list[dict[str, Any]]:
        return [
            row
            for row in self._generic_table_rows(selector, "schedule")
            if row.get("visitor_team_name") and row.get("home_team_name")
        ]

    def standings(self, season_end_year: int) -> list[dict[str, Any]]:
        url = self._http._url(f"/leagues/NBA_{season_end_year}.html")
        selector = self._http._get_selector(url=url)
        return _parsing.parse_standings(selector)

    def player_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        url = self._http._url(f"/friv/dailyleaders.cgi?month={month}&day={day}&year={year}")

        response = self._http._get(url=url, follow_redirects=False)

        response.raise_for_status()

        if response.status_code == httpx.codes.OK:
            selector = Selector(text=response.text)
            table = find_table(selector, "stats")
            if table is None:
                raise InvalidDate(day=day, month=month, year=year)
            rows = []
            for row_index, (row, metadata) in enumerate(_parsing.raw_rows_from_table(table)):
                row["slug"] = _parsing.slug_from_metadata(metadata, "player")
                _parsing.require_slug("player_box_scores", row, row_index)
                rows.append(row)
            if not rows:
                raise InvalidDate(day=day, month=month, year=year)
            return rows

        raise InvalidDate(day=day, month=month, year=year)

    def _player_season_box_scores_selector(self, player_identifier: str, season_end_year: int) -> Selector:
        url = self._http._url(f"/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}")
        return self._http._get_selector(url=url)

    def regular_season_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        selector = self._player_season_box_scores_selector(player_identifier, season_end_year)
        table = find_table(selector, "player_game_log_reg")
        if table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self._player_season_box_score_rows(table, include_inactive_games=include_inactive_games)

    def playoff_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        selector = self._player_season_box_scores_selector(player_identifier, season_end_year)
        table = find_table(selector, "player_game_log_post")
        if table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self._player_season_box_score_rows(table, include_inactive_games=include_inactive_games)

    def play_by_play(self, home_team: Team, day: int, month: int, year: int) -> list[dict[str, Any]]:
        if isinstance(home_team, str):
            home_team = _team_field(home_team)
        boxscores_selector = self._http._get_selector(
            url=self._http._url(f"/boxscores/?day={day}&month={month}&year={year}"),
        )
        abbr = TEAM_TO_TEAM_ABBREVIATION[home_team]
        game_url_path = _parsing.resolve_pbp_game_url_path(boxscores_selector, abbr)
        if game_url_path is None:
            raise InvalidDate(day=day, month=month, year=year)
        url = self._http._url(f"/boxscores/pbp/{game_url_path.split('/')[-1]}")
        selector = self._http._get_selector(url=url)
        team_names = [_parsing.cell_text(team_name) for team_name in selector.css("#content div.scorebox strong a")]
        away_team = _parsing.team_abbreviation_from_name(team_names[0])
        home_team_abbreviation = _parsing.team_abbreviation_from_name(team_names[1])
        return _parsing.parse_play_by_play_rows(selector, away_team, home_team_abbreviation)

    def playoff_bracket(self, season_end_year: int) -> list[dict[str, Any]]:
        url = self._http._url(f"/playoffs/NBA_{season_end_year}.html")

        selector = self._http._get_selector(url=url)
        table = find_table(selector, "all_playoffs")
        if table is None:
            return []
        return _parsing.parse_playoff_bracket(table)

    def players_advanced_season_totals(
        self, season_end_year: int, include_combined_values: bool = False
    ) -> list[dict[str, Any]]:
        url = self._http._url(f"/leagues/NBA_{season_end_year}_advanced.html")

        selector = self._http._get_selector(url=url)
        return self._player_totals_rows(selector, "advanced", include_combined=include_combined_values)

    def players_season_totals(self, season_end_year: int) -> list[dict[str, Any]]:
        url = self._http._url(f"/leagues/NBA_{season_end_year}_totals.html")

        selector = self._http._get_selector(url=url)
        return self._player_totals_rows(selector, "totals_stats", include_combined=False)

    def schedule_for_month(self, url: str) -> list[dict[str, Any]]:
        return self._schedule_rows(self._http._get_selector(url=url))

    def season_schedule(self, season_end_year: int) -> list[dict[str, Any]]:
        url = self._http._url(f"/leagues/NBA_{season_end_year}_games.html")

        selector = self._http._get_selector(url=url)
        season_schedule_values = self._schedule_rows(selector)

        for month_url_path in [
            link.attrib["href"] for link in selector.css('div#content div.filter div:not([class*="current"]) a')
        ]:
            url = self._http._url(month_url_path)
            monthly_schedule = self.schedule_for_month(url=url)
            season_schedule_values.extend(monthly_schedule)

        return season_schedule_values

    def team_box_score(self, game_url_path: str) -> list[dict[str, Any]]:
        url = self._http._url(game_url_path)
        selector = self._http._get_selector(url=url)
        return _parsing.parse_team_box_score(selector)

    def team_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        url = self._http._url(f"/boxscores/?day={day}&month={month}&year={year}")

        selector = self._http._get_selector(url=url)
        game_url_paths = [link.attrib["href"] for link in selector.css("td.gamelink a")]
        if not game_url_paths:
            raise InvalidDate(day=day, month=month, year=year)

        return [
            box_score
            for game_url_path in game_url_paths
            for box_score in self.team_box_score(game_url_path=game_url_path)
        ]

    def search(self, term: str) -> dict[str, list[dict[str, Any]]]:
        response = self._http._get(url=self._http._url("/search/search.fcgi"), params={"search": term})

        response.raise_for_status()

        player_results: list[dict[str, Any]] = []

        if str(response.url).startswith(self._http._url("/search/search.fcgi")):
            selector = Selector(text=response.text)
            player_results += _parsing.parse_search_rows(selector)

            seen_pagination_urls: set[str] = set()
            while _parsing.parse_search_pagination_url(selector) is not None:
                pagination_url = _parsing.parse_search_pagination_url(selector)
                assert pagination_url is not None
                if pagination_url in seen_pagination_urls:
                    break
                seen_pagination_urls.add(pagination_url)

                response = self._http._get(url=f"{HTTPService.BASE_URL}/search/{pagination_url}")

                response.raise_for_status()

                selector = Selector(text=response.text)
                player_results += _parsing.parse_search_rows(selector)

        elif str(response.url).startswith(f"{HTTPService.BASE_URL}/players"):
            selector = Selector(text=response.text)
            player_results += _parsing.parse_player_direct_search_results(selector, str(response.url))

        return {"players": player_results}

    def standings_by_date(self, season_end_year: int) -> list[dict[str, Any]]:
        endpoint = ENDPOINTS["standings_by_date"]
        standings: list[dict[str, Any]] = []
        for conference, conference_name in [
            ("eastern_conference", "Eastern"),
            ("western_conference", "Western"),
        ]:
            url = self._http._url(endpoint.path.format(season_end_year=season_end_year, conference=conference))
            selector = self._http._get_selector(url=url)
            table_selector = selector.css(f"table#{endpoint.table_id}")
            if table_selector:
                table = GenericTable(table_selector[0])
                for row in table.rows:
                    standings.append({"conference": conference_name, **row.to_dict()})
        return standings


def dispatch_custom_endpoint(http: HTTPService, name: str, **params: Any) -> Any:
    """Invoke a bespoke endpoint handler by registry name."""
    handler = CustomEndpointHandler(http)
    return getattr(handler, name)(**params)
