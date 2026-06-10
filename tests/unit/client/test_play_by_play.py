from unittest import TestCase, mock

import httpx

from courtside_data.client import play_by_play
from courtside_data.data import Team
from courtside_data.errors import InvalidDate
from courtside_data.http_service import HTTPService
from tests.http_mock import http_status_error


class TestPlayByPlay(TestCase):
    @mock.patch.object(HTTPService, "play_by_play")
    def test_raises_invalid_date_for_404_response(self, mocked_play_by_play):
        mocked_play_by_play.side_effect = http_status_error(404)
        self.assertRaises(InvalidDate, play_by_play, home_team=Team.MILWAUKEE_BUCKS, day=1, month=1, year=2018)

    @mock.patch.object(HTTPService, "play_by_play")
    def test_raises_non_404_http_error(self, mocked_play_by_play):
        mocked_play_by_play.side_effect = http_status_error(500)
        self.assertRaises(
            httpx.HTTPStatusError, play_by_play, home_team=Team.MILWAUKEE_BUCKS, day=1, month=1, year=2018
        )
