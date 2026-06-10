from unittest import TestCase
from unittest.mock import patch, MagicMock

from requests import HTTPError, codes

from courtside_data.client import season_schedule
from courtside_data.errors import InvalidSeason
from courtside_data.http_service import HTTPService


class TestSeasonSchedule(TestCase):
    @patch.object(HTTPService, "season_schedule")
    def test_not_found_raises_invalid_season(self, mocked_season_schedule):
        mocked_season_schedule.side_effect = HTTPError(response=MagicMock(status_code=codes.not_found))
        self.assertRaisesRegex(
            InvalidSeason,
            "Season end year of jaebaebae is invalid",
            season_schedule,
            season_end_year="jaebaebae")

    @patch.object(HTTPService, "season_schedule")
    def test_other_http_error_is_raised(self, mocked_season_schedule):
        mocked_season_schedule.side_effect = HTTPError(response=MagicMock(status_code=codes.internal_server_error))
        self.assertRaises(HTTPError, season_schedule, season_end_year=2018)
