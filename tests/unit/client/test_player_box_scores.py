from unittest import TestCase, mock

import httpx

from tests.http_mock import http_status_error

from courtside_data.client import player_box_scores
from courtside_data.errors import InvalidDate
from courtside_data.http_service import HTTPService


class TestPlayerBoxScores(TestCase):
    @mock.patch.object(HTTPService, 'player_box_scores')
    def test_raises_invalid_date_for_404_response(self, mocked_player_box_scores):
        mocked_player_box_scores.side_effect = http_status_error(404)
        self.assertRaises(InvalidDate, player_box_scores, day=1, month=1, year=2018)

    @mock.patch.object(HTTPService, 'player_box_scores')
    def test_raises_non_404_http_error(self, mocked_player_box_scores):
        mocked_player_box_scores.side_effect = http_status_error(500)
        self.assertRaises(httpx.HTTPStatusError, player_box_scores, day=1, month=1, year=2018)
