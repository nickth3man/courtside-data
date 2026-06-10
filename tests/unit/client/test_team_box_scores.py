from unittest import TestCase
from unittest.mock import patch, MagicMock

import httpx

import courtside_data.client as client
from courtside_data.errors import InvalidDate
from courtside_data.http_service import HTTPService


class TestTeamBoxScores(TestCase):
    @patch.object(HTTPService, "team_box_scores")
    def test_invalid_date_error_raised_for_unknown_date(self, mocked_http_team_box_scores):
        mocked_http_team_box_scores.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=httpx.codes.NOT_FOUND),
        )
        self.assertRaisesRegex(
            InvalidDate,
            "Date with year set to jae, month set to bae, and day set to bae is invalid",
            client.team_box_scores,
            day="bae",
            month="bae",
            year="jae"
        )
