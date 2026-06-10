from unittest import TestCase
from unittest.mock import MagicMock, patch

import httpx

from tests.http_mock import http_status_error

from courtside_data.client import regular_season_player_box_scores
from courtside_data.errors import InvalidPlayerAndSeason
from courtside_data.http_service import HTTPService


class TestPlayerRegularSeasonBoxScores(TestCase):
    @patch.object(HTTPService, "regular_season_player_box_scores")
    def test_raises_exception_for_500_response(self, mocked_regular_season_player_box_scores):
        mocked_regular_season_player_box_scores.side_effect = http_status_error(500)
        self.assertRaises(InvalidPlayerAndSeason, regular_season_player_box_scores, 'Mock Player', 2000)

    @patch.object(HTTPService, "regular_season_player_box_scores")
    def test_raises_exception_for_404_response(self, mocked_regular_season_player_box_scores):
        mocked_regular_season_player_box_scores.side_effect = http_status_error(404)
        self.assertRaises(InvalidPlayerAndSeason, regular_season_player_box_scores, 'Mock Player', 2000)

    @patch.object(HTTPService, "regular_season_player_box_scores")
    def test_raises_non_500_http_error(self, mocked_regular_season_player_box_scores):
        mocked_regular_season_player_box_scores.side_effect = http_status_error(400)
        self.assertRaises(httpx.HTTPStatusError, regular_season_player_box_scores, 'Mock Player', 2000)
