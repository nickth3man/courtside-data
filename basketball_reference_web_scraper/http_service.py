import os
import random
import re
import time

import requests
from lxml import html
from parsel import Selector

from basketball_reference_web_scraper.html import GenericTable, extract_commented_table

from basketball_reference_web_scraper.data import TEAM_TO_TEAM_ABBREVIATION, TeamTotal, PlayerData
from basketball_reference_web_scraper.errors import InvalidDate, InvalidPlayer, InvalidPlayerAndSeason, InvalidTeam
from basketball_reference_web_scraper.html import DailyLeadersPage, PlayerSeasonBoxScoresPage, PlayerSeasonTotalTable, \
    PlayerAdvancedSeasonTotalsTable, PlayByPlayPage, SchedulePage, BoxScoresPage, DailyBoxScoresPage, SearchPage, \
    PlayerPage, StandingsPage

_DEFAULT_RATE_LIMIT_INTERVAL = 3.5
_DEFAULT_RATE_LIMIT_JITTER = 1.2


class HTTPService:
    BASE_URL = 'https://www.basketball-reference.com'

    def __init__(
        self,
        parser,
        rate_limit_interval=None,
        rate_limit_jitter=None,
        session=None,
        time_func=None,
        sleep=None,
        random_func=None,
    ):
        self.parser = parser
        # Constructor param > env var > default
        if rate_limit_interval is not None:
            self._rate_limit_interval = rate_limit_interval
        else:
            self._rate_limit_interval = float(
                os.environ.get('BASKETBALL_REF_RATE_LIMIT_INTERVAL', _DEFAULT_RATE_LIMIT_INTERVAL)
            )

        if rate_limit_jitter is not None:
            self._rate_limit_jitter = rate_limit_jitter
        else:
            self._rate_limit_jitter = float(
                os.environ.get('BASKETBALL_REF_RATE_LIMIT_JITTER', _DEFAULT_RATE_LIMIT_JITTER)
            )

        self._session = session if session is not None else requests.Session()
        self._last_request_time = float('-inf')

        # Injectable dependencies for testing
        self._time = time_func if time_func is not None else time.time
        self._sleep = sleep if sleep is not None else time.sleep
        self._random = random_func if random_func is not None else random.uniform

    def _apply_rate_limiting(self):
        current_time = self._time()
        time_since_last = current_time - self._last_request_time

        if self._rate_limit_interval > 0 and time_since_last < self._rate_limit_interval:
            jitter = self._random(0.0, self._rate_limit_jitter)
            self._sleep((self._rate_limit_interval - time_since_last) + jitter)

        self._last_request_time = current_time

    def _get(self, url, **kwargs):
        self._apply_rate_limiting()
        return self._session.get(url=url, **kwargs)

    @staticmethod
    def _clean_text(values):
        return re.sub(r'\s+', ' ', ' '.join(values)).strip()

    @classmethod
    def _parse_transaction_list(cls, selector):
        transactions = []
        for day in selector.css('ul.page_index > li'):
            date = cls._clean_text(day.xpath('./span//text()').getall())
            for transaction in day.xpath('./p[normalize-space()]'):
                linked_resources = []
                from_team_abbreviations = []
                to_team_abbreviations = []
                for link in transaction.css('a'):
                    from_team = link.attrib.get('data-attr-from')
                    to_team = link.attrib.get('data-attr-to')
                    if from_team:
                        from_team_abbreviations.append(from_team)
                    if to_team:
                        to_team_abbreviations.append(to_team)
                    linked_resources.append({
                        'text': cls._clean_text(link.css('::text').getall()),
                        'href': link.attrib.get('href', ''),
                        'from_team_abbreviation': from_team or '',
                        'to_team_abbreviation': to_team or '',
                    })

                transactions.append({
                    'date': date,
                    'transaction': cls._clean_text(transaction.css('::text').getall()),
                    'from_team_abbreviations': from_team_abbreviations,
                    'to_team_abbreviations': to_team_abbreviations,
                    'linked_resources': linked_resources,
                })
        return transactions

    def standings(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )

        response = self._get(url=url, allow_redirects=False)

        response.raise_for_status()

        page = StandingsPage(html=html.fromstring(response.content))
        return self.parser.parse_division_standings(standings=page.division_standings.eastern_conference_table.rows) + \
               self.parser.parse_division_standings(standings=page.division_standings.western_conference_table.rows)

    def player_box_scores(self, day, month, year):
        url = '{BASE_URL}/friv/dailyleaders.cgi?month={month}&day={day}&year={year}'.format(
            BASE_URL=HTTPService.BASE_URL,
            day=day,
            month=month,
            year=year
        )

        response = self._get(url=url, allow_redirects=False)

        response.raise_for_status()

        if response.status_code == requests.codes.ok:
            page = DailyLeadersPage(html=html.fromstring(response.content))
            if not page.daily_leaders:
                raise InvalidDate(day=day, month=month, year=year)
            return self.parser.parse_player_box_scores(box_scores=page.daily_leaders)

        raise InvalidDate(day=day, month=month, year=year)

    def regular_season_player_box_scores(self, player_identifier, season_end_year, include_inactive_games=False):
        # Makes assumption that basketball reference pattern of breaking out player pathing using first character of
        # surname can be derived from the fact that basketball reference also has a pattern of player identifiers
        # starting with first few characters of player's surname
        url = '{BASE_URL}/players/{player_surname_starting_character}/{player_identifier}/gamelog/{season_end_year}' \
            .format(
            BASE_URL=HTTPService.BASE_URL,
            player_surname_starting_character=player_identifier[0],
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )

        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        page = PlayerSeasonBoxScoresPage(html=html.fromstring(response.content))
        if page.regular_season_box_scores_table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self.parser.parse_player_season_box_scores(box_scores=page.regular_season_box_scores_table.rows, include_inactive_games=include_inactive_games)

    def playoff_player_box_scores(self, player_identifier, season_end_year, include_inactive_games=False):
        # Makes assumption that basketball reference pattern of breaking out player pathing using first character of
        # surname can be derived from the fact that basketball reference also has a pattern of player identifiers
        # starting with first few characters of player's surname
        url = '{BASE_URL}/players/{player_surname_starting_character}/{player_identifier}/gamelog/{season_end_year}' \
            .format(
            BASE_URL=HTTPService.BASE_URL,
            player_surname_starting_character=player_identifier[0],
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )

        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        page = PlayerSeasonBoxScoresPage(html=html.fromstring(response.content))
        if page.playoff_box_scores_table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self.parser.parse_player_season_box_scores(box_scores=page.playoff_box_scores_table.rows, include_inactive_games=include_inactive_games)

    def play_by_play(self, home_team, day, month, year):
        add_0_if_needed = lambda s: "0" + s if len(s) == 1 else s

        # the hard-coded `0` in the url assumes we always take the first match of the given date and team.
        url = "{BASE_URL}/boxscores/pbp/{year}{month}{day}0{team_abbr}.html".format(
            BASE_URL=HTTPService.BASE_URL, year=year, month=add_0_if_needed(str(month)), day=add_0_if_needed(str(day)),
            team_abbr=TEAM_TO_TEAM_ABBREVIATION[home_team]
        )
        response = self._get(url=url)
        response.raise_for_status()

        page = PlayByPlayPage(html=html.fromstring(response.content))

        return self.parser.parse_play_by_plays(
            play_by_plays=page.play_by_play_table.rows,
            away_team_name=page.away_team_name,
            home_team_name=page.home_team_name,
        )

    def players_advanced_season_totals(self, season_end_year, include_combined_values=False):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_advanced.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )

        response = self._get(url=url)

        response.raise_for_status()

        table = PlayerAdvancedSeasonTotalsTable(html=html.fromstring(response.content))
        return self.parser.parse_player_advanced_season_totals_parser(totals=table.get_rows(include_combined_values))

    def players_season_totals(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_totals.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )

        response = self._get(url=url)

        response.raise_for_status()

        table = PlayerSeasonTotalTable(html=html.fromstring(response.content))
        return self.parser.parse_player_season_totals(totals=table.rows)

    def schedule_for_month(self, url):
        response = self._get(url=url)

        response.raise_for_status()

        page = SchedulePage(html=html.fromstring(html=response.content))
        return self.parser.parse_scheduled_games(games=page.rows)

    def season_schedule(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_games.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year
        )

        response = self._get(url=url)

        response.raise_for_status()

        page = SchedulePage(html=html.fromstring(html=response.content))
        season_schedule_values = self.parser.parse_scheduled_games(games=page.rows)

        for month_url_path in page.other_months_schedule_urls:
            url = '{BASE_URL}{month_url_path}'.format(BASE_URL=HTTPService.BASE_URL, month_url_path=month_url_path)
            monthly_schedule = self.schedule_for_month(url=url)
            season_schedule_values.extend(monthly_schedule)

        return season_schedule_values

    def team_box_score(self, game_url_path):
        url = "{BASE_URL}/{game_url_path}".format(BASE_URL=HTTPService.BASE_URL, game_url_path=game_url_path)

        response = self._get(url=url)

        response.raise_for_status()

        page = BoxScoresPage(html.fromstring(response.content))
        combined_team_totals = [
            TeamTotal(team_abbreviation=table.team_abbreviation, totals=table.team_totals)
            for table in page.basic_statistics_tables
        ]

        return self.parser.parse_team_totals(
            first_team_totals=combined_team_totals[0],
            second_team_totals=combined_team_totals[1],
        )

    def team_box_scores(self, day, month, year):
        url = "{BASE_URL}/boxscores/".format(BASE_URL=HTTPService.BASE_URL)

        response = self._get(url=url, params={"day": day, "month": month, "year": year})

        response.raise_for_status()

        page = DailyBoxScoresPage(html=html.fromstring(response.content))

        if not page.game_url_paths:
            raise InvalidDate(day=day, month=month, year=year)

        return [
            box_score
            for game_url_path in page.game_url_paths
            for box_score in self.team_box_score(game_url_path=game_url_path)
        ]

    def search(self, term):
        response = self._get(
            url="{BASE_URL}/search/search.fcgi".format(BASE_URL=HTTPService.BASE_URL),
            params={"search": term}
        )

        response.raise_for_status()

        player_results = []

        if response.url.startswith("{BASE_URL}/search/search.fcgi".format(BASE_URL=HTTPService.BASE_URL)):
            page = SearchPage(html=html.fromstring(response.content))
            parsed_results = self.parser.parse_player_search_results(nba_aba_baa_players=page.nba_aba_baa_players)
            player_results += parsed_results["players"]

            while page.nba_aba_baa_players_pagination_url is not None:
                response = self._get(
                    url="{BASE_URL}/search/{pagination_url}".format(
                        BASE_URL=HTTPService.BASE_URL,
                        pagination_url=page.nba_aba_baa_players_pagination_url
                    )
                )

                response.raise_for_status()

                page = SearchPage(html=html.fromstring(response.content))

                parsed_results = self.parser.parse_player_search_results(nba_aba_baa_players=page.nba_aba_baa_players)
                player_results += parsed_results["players"]

        elif response.url.startswith("{BASE_URL}/players".format(BASE_URL=HTTPService.BASE_URL)):
            page = PlayerPage(html=html.fromstring(response.content))
            if page.totals_table is None:
                player_results += [self.parser.parse_player_data(player=PlayerData(
                    name=page.name,
                    resource_location=response.url,
                    league_abbreviations=set(),
                ))]
            else:
                data = PlayerData(
                    name=page.name,
                    resource_location=response.url,
                    league_abbreviations=set([
                        row.league_abbreviation
                        for row in page.totals_table.rows
                        if row.league_abbreviation is not None
                    ])
                )
                player_results += [self.parser.parse_player_data(player=data)]

        return {
            "players": player_results
        }

    def league_per_game_stats(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_per_game.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#per_game_stats')
        if not table_selector:
            return []

        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def league_per_36_minutes(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_per_minute.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#per_minute_stats')
        if not table_selector:
            return []

        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def league_totals(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_totals.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#totals_stats')
        if not table_selector:
            return []

        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def rookie_stats(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_rookies.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#rookies')
        if not table_selector:
            return []

        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def standings_by_date(self, season_end_year):
        standings = []
        for conference in ['eastern_conference', 'western_conference']:
            url = '{BASE_URL}/leagues/NBA_{season_end_year}_standings_by_date_{conference}.html'.format(
                BASE_URL=HTTPService.BASE_URL,
                season_end_year=season_end_year,
                conference=conference,
            )
            response = self._get(url=url, allow_redirects=False)
            response.raise_for_status()

            selector = Selector(text=response.text)
            table_selector = selector.css('table#standings_by_date')
            if table_selector:
                table = GenericTable(table_selector[0])
                standings.extend(self.parser.parse_generic_table(table))
        return standings

    def attendance(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#advanced-team')
        if not table_selector:
            return []

        table = GenericTable(table_selector[0])
        return [
            {
                'team': row.get('team', ''),
                'arena_name': row.get('arena_name', ''),
                'attendance': row.get('attendance', ''),
                'attendance_per_g': row.get('attendance_per_g', ''),
            }
            for row in table.rows
        ]

    def league_transactions(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_transactions.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#transactions')
        if not table_selector:
            return self._parse_transaction_list(selector)

        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def league_per_100_possessions(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_per_poss.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#per_poss')
        if not table_selector:
            return []

        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def league_shooting(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_shooting.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#shooting')
        if not table_selector:
            return []

        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def playoff_per_game(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_per_game.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#per_game_stats_post')
        if not table_selector:
            table_selector = extract_commented_table(selector, 'per_game_stats_post')
            if table_selector is None:
                return []
            table = GenericTable(table_selector)
        else:
            table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def playoff_totals(self, season_end_year):
        url = '{BASE_URL}/leagues/NBA_{season_end_year}_totals.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        selector = Selector(text=response.text)
        table_selector = selector.css('table#totals_stats_post')
        if not table_selector:
            table_selector = extract_commented_table(selector, 'totals_stats_post')
            if table_selector is None:
                return []
            table = GenericTable(table_selector)
        else:
            table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_schedule(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}_games.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#games')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_transactions(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}_transactions.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#transactions')
        if not table_selector:
            return self._parse_transaction_list(selector)

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def draft_picks(self, season_end_year):
        url = '{BASE_URL}/draft/NBA_{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#stats')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def season_leaders(self):
        url = '{BASE_URL}/leaders/per_season.html'.format(BASE_URL=HTTPService.BASE_URL)
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#stats_TOT')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0], use_header_fallback=True)
        return self.parser.parse_generic_table(table)

    def career_leaders(self):
        url = '{BASE_URL}/leaders/'.format(BASE_URL=HTTPService.BASE_URL)
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#leaders_index')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0], use_header_fallback=True)
        return self.parser.parse_generic_table(table)

    def playoff_bracket(self, season_end_year):
        url = '{BASE_URL}/playoffs/NBA_{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#all_playoffs')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0], use_header_fallback=True)
        return self.parser.parse_generic_table(table)

    def season_awards(self, season_end_year):
        url = '{BASE_URL}/awards/awards_{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#mvp')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def player_career_stats(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#per_game_stats')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def player_playoff_series(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'playoffs_series')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def player_splits(self, player_identifier, season_end_year):
        url = '{BASE_URL}/players/{initial}/{player_identifier}/splits/{season_end_year}'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#splits')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def player_on_off(self, player_identifier, season_end_year):
        url = '{BASE_URL}/players/{initial}/{player_identifier}/on-off/{season_end_year}'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#on-off')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def player_shot_charts(self, player_identifier, season_end_year):
        url = '{BASE_URL}/players/{initial}/{player_identifier}/shooting/{season_end_year}'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )
        # basketball-reference redirects .html for shooting pages, so no .html suffix
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#shooting')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def player_adjusted_shooting(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'adj_shooting')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def player_play_by_play(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'pbp_stats')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def player_game_highs(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'highs-reg-season')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def player_all_star(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'all_star')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def player_similarity_scores(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'sims-career')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def player_salaries(self, player_identifier):
        url = '{BASE_URL}/players/{initial}/{player_identifier}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            initial=player_identifier[0],
            player_identifier=player_identifier,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'all_salaries')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def team_roster(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#roster')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_injury_report(self, team_abbreviation=None, season_end_year=None):
        url = '{BASE_URL}/friv/injuries.fcgi'.format(
            BASE_URL=HTTPService.BASE_URL,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#injuries')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_and_opponent(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'team_and_opponent')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def team_misc_four_factors(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'team_misc')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def team_splits(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}/splits/'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#team_splits')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_contracts(self, team_abbreviation):
        url = '{BASE_URL}/contracts/{team_abbreviation}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#contracts')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_lineups(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}/lineups/'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'lineups_5-man_')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def team_starting_lineups(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}_start.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#starting_lineups_po0')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_on_off(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}/on-off/'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css('table#on_off')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)

    def team_opponent_stats(self, team_abbreviation, season_end_year):
        url = '{BASE_URL}/teams/{team_abbreviation}/{season_end_year}.html'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = extract_commented_table(selector, 'team_and_opponent')
        if table_selector is None:
            return []

        table = GenericTable(table_selector)
        return self.parser.parse_generic_table(table)

    def franchise_history(self, team_abbreviation):
        url = '{BASE_URL}/teams/{team_abbreviation}/'.format(
            BASE_URL=HTTPService.BASE_URL,
            team_abbreviation=team_abbreviation,
        )
        response = self._get(url=url, allow_redirects=False)
        response.raise_for_status()

        from parsel import Selector
        selector = Selector(text=response.text)
        table_selector = selector.css(f'table#{team_abbreviation}')
        if not table_selector:
            return []

        from basketball_reference_web_scraper.html import GenericTable
        table = GenericTable(table_selector[0])
        return self.parser.parse_generic_table(table)
