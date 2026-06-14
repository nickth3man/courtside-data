import filecmp
import json
import os
from datetime import UTC, datetime
from unittest import TestCase

from courtside_data.client import season_schedule
from courtside_data.data import OutputType, Team
from tests import http_mock as requests_mock
from tests.integration.client import raw_fixtures
from tests.integration.client.utilities import SeasonScheduleMocker


@SeasonScheduleMocker(
    schedules_directory=os.path.join(
        os.path.dirname(__file__),
        "../files/schedule",
    ),
    season_end_year=2018,
)
class TestSeasonScheduleInMemoryOutput(TestCase):
    def test_2018_season_schedule_length(self):
        result = season_schedule(season_end_year=2018)
        self.assertEqual(1312, len(result))

    def test_first_game_of_2018_season(self):
        result = season_schedule(season_end_year=2018)
        self.assertEqual(
            result[0],
            {
                "away_team": Team.BOSTON_CELTICS,
                "away_team_score": 99,
                "home_team": Team.CLEVELAND_CAVALIERS,
                "home_team_score": 102,
                "start_time": datetime(2017, 10, 18, 0, 1, tzinfo=UTC),
            },
        )

    def test_last_game_of_2018_season(self):
        result = season_schedule(season_end_year=2018)
        self.assertEqual(
            result[1311],
            {
                "away_team": Team.GOLDEN_STATE_WARRIORS,
                "away_team_score": 108,
                "home_team": Team.CLEVELAND_CAVALIERS,
                "home_team_score": 85,
                "start_time": datetime(2018, 6, 9, 1, 0, tzinfo=UTC),
            },
        )


class TestFutureSeasonSchedule(TestCase):
    def setUp(self):
        self._html = raw_fixtures.read("season_schedule/not_found.html")

    @requests_mock.Mocker()
    def test_future_season_schedule_returns_empty_list(self, m):
        m.get(url="https://www.basketball-reference.com/leagues/NBA_2026_games.html", text=self._html, status_code=200)
        result = season_schedule(season_end_year=2026)
        self.assertEqual([], result)


@SeasonScheduleMocker(
    schedules_directory=os.path.join(
        os.path.dirname(__file__),
        "../files/schedule",
    ),
    season_end_year=2018,
)
class Test2018SeasonScheduleCsvOutput(TestCase):
    def setUp(self):
        self.output_file_path = os.path.join(os.path.dirname(__file__), "./output/generated/season_schedule/2018.csv")
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__), "./output/expected/season_schedule/2018.csv"
        )

    def tearDown(self):
        if not os.environ.get("BR_REGEN"):
            os.remove(self.output_file_path)

    def test_output(self):
        season_schedule(season_end_year=2018, output_type=OutputType.CSV, output_file_path=self.output_file_path)
        self.assertTrue(filecmp.cmp(self.output_file_path, self.expected_output_file_path))


@SeasonScheduleMocker(
    schedules_directory=os.path.join(
        os.path.dirname(__file__),
        "../files/schedule",
    ),
    season_end_year=2018,
)
class Test2018SeasonScheduleJsonOutput(TestCase):
    def setUp(self):
        self.output_file_path = os.path.join(os.path.dirname(__file__), "./output/generated/season_schedule/2018.json")
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__), "./output/expected/season_schedule/2018.json"
        )

    def tearDown(self):
        if not os.environ.get("BR_REGEN"):
            os.remove(self.output_file_path)

    def test_file_output(self):
        season_schedule(season_end_year=2018, output_type=OutputType.JSON, output_file_path=self.output_file_path)
        self.assertTrue(filecmp.cmp(self.output_file_path, self.expected_output_file_path))


@SeasonScheduleMocker(
    schedules_directory=os.path.join(
        os.path.dirname(__file__),
        "../files/schedule",
    ),
    season_end_year=2018,
)
class Test2018SeasonScheduleInMemoryJson(TestCase):
    def setUp(self):
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__), "./output/expected/season_schedule/2018.json"
        )

    def test_in_memory_json(self):
        schedule = season_schedule(season_end_year=2018, output_type=OutputType.JSON)
        with open(self.expected_output_file_path, encoding="utf8") as f:
            self.assertEqual(
                json.load(f),
                json.loads(schedule),
            )


@SeasonScheduleMocker(
    schedules_directory=os.path.join(
        os.path.dirname(__file__),
        "../files/schedule",
    ),
    season_end_year=2001,
)
class Test2001SeasonScheduleCsvOutput(TestCase):
    def setUp(self):
        self.output_file_path = os.path.join(os.path.dirname(__file__), "./output/generated/season_schedule/2001.csv")
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__), "./output/expected/season_schedule/2001.csv"
        )

    def tearDown(self):
        if not os.environ.get("BR_REGEN"):
            os.remove(self.output_file_path)

    def test_output(self):
        season_schedule(season_end_year=2001, output_type=OutputType.CSV, output_file_path=self.output_file_path)
        self.assertTrue(filecmp.cmp(self.output_file_path, self.expected_output_file_path))


@SeasonScheduleMocker(
    schedules_directory=os.path.join(
        os.path.dirname(__file__),
        "../files/schedule",
    ),
    season_end_year=2001,
)
class Test2001SeasonScheduleJsonOutput(TestCase):
    def setUp(self):
        self.output_file_path = os.path.join(os.path.dirname(__file__), "./output/generated/season_schedule/2001.json")
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__), "./output/expected/season_schedule/2001.json"
        )

    def tearDown(self):
        if not os.environ.get("BR_REGEN"):
            os.remove(self.output_file_path)

    def test_file_output(self):
        season_schedule(season_end_year=2001, output_type=OutputType.JSON, output_file_path=self.output_file_path)
        self.assertTrue(filecmp.cmp(self.output_file_path, self.expected_output_file_path))


@SeasonScheduleMocker(
    schedules_directory=os.path.join(
        os.path.dirname(__file__),
        "../files/schedule",
    ),
    season_end_year=2001,
)
class Test2001SeasonScheduleInMemoryJson(TestCase):
    def setUp(self):
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__), "./output/expected/season_schedule/2001.json"
        )

    def test_in_memory_json(self):
        schedule = season_schedule(season_end_year=2001, output_type=OutputType.JSON)
        with open(self.expected_output_file_path, encoding="utf8") as f:
            self.assertEqual(
                json.load(f),
                json.loads(schedule),
            )
