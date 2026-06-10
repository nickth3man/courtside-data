from unittest import TestCase
from unittest.mock import patch

import httpx

from courtside_data.client import players_season_totals
from courtside_data.errors import InvalidSeason
from courtside_data.http_service import HTTPService
from tests.http_mock import http_status_error


class TestPlayerSeasonTotals(TestCase):
    @patch.object(HTTPService, "players_season_totals")
    def test_not_found_raises_invalid_season(self, mocked_players_season_totals):
        end_year = "jaebaebae"
        expected_message = f"Season end year of {end_year} is invalid"
        mocked_players_season_totals.side_effect = http_status_error(404)
        self.assertRaisesRegex(InvalidSeason, expected_message, players_season_totals, season_end_year=end_year)

    @patch.object(HTTPService, "players_season_totals")
    def test_other_http_error_is_raised(self, mocked_players_season_totals):
        mocked_players_season_totals.side_effect = http_status_error(500)
        self.assertRaises(httpx.HTTPStatusError, players_season_totals, season_end_year=2018)
