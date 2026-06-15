from datetime import UTC, datetime, timedelta
from unittest import TestCase
from zoneinfo import ZoneInfo

from lxml import html

from courtside_data.data import TEAM_NAME_TO_TEAM, Team
from courtside_data.legacy.html import SchedulePage
from courtside_data.legacy.parsers import ScheduledGamesParser, ScheduledStartTimeParser, TeamNameParser
from tests.integration.client import raw_fixtures


class BaseTest(TestCase):
    _path_from_schedule_directory: str | None = None

    @classmethod
    def setUpClass(cls):
        assert cls._path_from_schedule_directory is not None
        _html = raw_fixtures.schedule_page(cls._path_from_schedule_directory)
        cls._page = SchedulePage(html=html.fromstring(_html))

        super().setUpClass()


class BaseParserTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        assert cls._path_from_schedule_directory is not None
        _html = raw_fixtures.schedule_page(cls._path_from_schedule_directory)
        cls._parsed_results = ScheduledGamesParser(
            start_time_parser=ScheduledStartTimeParser(),
            team_name_parser=TeamNameParser(team_names_to_teams=TEAM_NAME_TO_TEAM),
        ).parse_games(games=SchedulePage(html=html.fromstring(_html)).rows)

        super().setUpClass()


class TestSchedulePage(BaseTest):
    _path_from_schedule_directory = "2001/2001.html"

    def test_expected_urls(self):
        self.assertEqual(
            self._page.other_months_schedule_urls,
            [
                "/leagues/NBA_2001_games-november.html",
                "/leagues/NBA_2001_games-december.html",
                "/leagues/NBA_2001_games-january.html",
                "/leagues/NBA_2001_games-february.html",
                "/leagues/NBA_2001_games-march.html",
                "/leagues/NBA_2001_games-april.html",
                "/leagues/NBA_2001_games-may.html",
                "/leagues/NBA_2001_games-june.html",
            ],
        )


class TestOctober2001Parser(BaseParserTest):
    _path_from_schedule_directory = "2001/2001.html"

    def test_length(self):
        self.assertEqual(len(self._parsed_results), 13)

    def test_first_game(self):
        first_game = self._parsed_results[0]
        expected_datetime = (
            datetime(year=2000, month=10, day=31, hour=19, minute=30)
            .replace(tzinfo=ZoneInfo("US/Eastern"))
            .astimezone(UTC)
        )

        self.assertTrue(abs(first_game["start_time"] - expected_datetime) < timedelta(seconds=1))
        self.assertEqual(first_game["away_team"], Team.CHARLOTTE_HORNETS)
        self.assertEqual(first_game["home_team"], Team.ATLANTA_HAWKS)
        self.assertEqual(first_game["away_team_score"], 106)
        self.assertEqual(first_game["home_team_score"], 82)


class TestOctober2018Parser(BaseParserTest):
    _path_from_schedule_directory = "2018/2018.html"

    def test_length(self):
        self.assertEqual(len(self._parsed_results), 104)


class TestScheduleParserShape(BaseParserTest):
    """Generic contract test for the schedule parser output shape.

    The historical ``TestParsingUpcomingGames`` class depended on a volatile
    ``upcoming-games.html`` snapshot that could not be regenerated. This
    replacement exercises the same parser code path against a stable season
    schedule fixture and asserts the parser's output contract instead of a
    point-in-time snapshot.
    """

    _path_from_schedule_directory = "2018/2018.html"

    def test_each_game_has_required_keys_and_types(self):
        required_keys = {"start_time", "away_team", "home_team", "away_team_score", "home_team_score"}
        for game in self._parsed_results:
            self.assertIsInstance(game, dict)
            self.assertGreaterEqual(game.keys(), required_keys)
            self.assertIsInstance(game["start_time"], datetime)
            self.assertIsNotNone(game["start_time"].tzinfo)
            self.assertIsInstance(game["away_team"], Team)
            self.assertIsInstance(game["home_team"], Team)

    def test_scores_are_consistently_present_or_absent(self):
        """A game either has both scores or neither; partial scores are invalid."""
        for game in self._parsed_results:
            away_score = game["away_team_score"]
            home_score = game["home_team_score"]
            if away_score is None or home_score is None:
                self.assertIsNone(away_score)
                self.assertIsNone(home_score)
            else:
                self.assertIsInstance(away_score, int)
                self.assertIsInstance(home_score, int)
