import os
from unittest import TestCase, mock

from requests import codes

from basketball_reference_web_scraper.errors import InvalidDate, InvalidPlayer, InvalidTeam
from basketball_reference_web_scraper.http_service import HTTPService


class TestHTTPService(TestCase):
    @mock.patch("requests.get")
    def test_player_box_scores_raises_invalid_date_for_300_response(self, mocked_get):
        response = mock.Mock(status_code=codes.multiple_choices)
        mocked_get.return_value = response
        session = mock.MagicMock()
        session.get.return_value = response
        self.assertRaisesRegex(
            InvalidDate,
            "Date with year set to 2018, month set to 1, and day set to 1 is invalid",
            HTTPService(parser=mock.MagicMock(), session=session, rate_limit_interval=0).player_box_scores,
            day=1, month=1, year=2018)


class TestHTTPServiceBackwardCompatibility(TestCase):
    """Ensure existing HTTPService(parser) construction remains valid."""

    def test_constructor_with_parser_only(self):
        parser = mock.MagicMock()
        service = HTTPService(parser=parser)
        self.assertIs(service.parser, parser)

    def test_session_created_by_default(self):
        service = HTTPService(parser=mock.MagicMock())
        self.assertIsNotNone(service._session)


class TestHTTPServiceSessionReuse(TestCase):
    """Verify _get uses the provided/injected session."""

    @mock.patch("requests.Session")
    def test_default_session_is_requests_session(self, MockSession):
        service = HTTPService(parser=mock.MagicMock())
        self.assertIsInstance(service._session, MockSession.return_value.__class__)

    def test_injected_session_is_used(self):
        mock_session = mock.MagicMock()
        mock_response = mock.Mock(status_code=200)
        mock_session.get.return_value = mock_response

        service = HTTPService(parser=mock.MagicMock(), session=mock_session, rate_limit_interval=0)
        result = service._get(url="https://example.com")

        mock_session.get.assert_called_once_with(url="https://example.com")
        self.assertIs(result, mock_response)

    def test_get_passes_kwargs_to_session(self):
        mock_session = mock.MagicMock()
        mock_response = mock.Mock(status_code=200)
        mock_session.get.return_value = mock_response

        service = HTTPService(parser=mock.MagicMock(), session=mock_session, rate_limit_interval=0)
        service._get(url="https://example.com", allow_redirects=False, params={"key": "val"})

        mock_session.get.assert_called_once_with(
            url="https://example.com",
            allow_redirects=False,
            params={"key": "val"},
        )


class TestHTTPServiceRateLimiting(TestCase):
    """Verify rate limiting behavior with injected time/sleep."""

    def test_first_request_does_not_sleep(self):
        mock_session = mock.MagicMock()
        mock_session.get.return_value = mock.Mock()
        mock_sleep = mock.MagicMock()
        mock_time = mock.MagicMock(return_value=100.0)

        service = HTTPService(
            parser=mock.MagicMock(),
            session=mock_session,
            rate_limit_interval=3.5,
            rate_limit_jitter=1.0,
            sleep=mock_sleep,
            time_func=mock_time,
        )
        service._get(url="https://example.com")

        mock_sleep.assert_not_called()

    def test_second_request_sleeps_when_interval_requires(self):
        mock_session = mock.MagicMock()
        mock_session.get.return_value = mock.Mock()
        mock_sleep = mock.MagicMock()
        # Simulate time progression: first call at 0.0, second at 1.0 (less than 3.5s interval)
        mock_time = mock.MagicMock(side_effect=[0.0, 1.0])

        service = HTTPService(
            parser=mock.MagicMock(),
            session=mock_session,
            rate_limit_interval=3.5,
            rate_limit_jitter=0.0,
            sleep=mock_sleep,
            time_func=mock_time,
        )
        service._get(url="https://example.com")
        service._get(url="https://example.com")

        # Should sleep for 3.5 - 1.0 = 2.5 seconds (interval - elapsed)
        mock_sleep.assert_called_once()
        sleep_arg = mock_sleep.call_args[0][0]
        self.assertAlmostEqual(sleep_arg, 2.5, places=1)

    def test_interval_zero_disables_sleep(self):
        mock_session = mock.MagicMock()
        mock_session.get.return_value = mock.Mock()
        mock_sleep = mock.MagicMock()
        mock_time = mock.MagicMock(side_effect=[0.0, 0.5])

        service = HTTPService(
            parser=mock.MagicMock(),
            session=mock_session,
            rate_limit_interval=0,
            rate_limit_jitter=0,
            sleep=mock_sleep,
            time_func=mock_time,
        )
        service._get(url="https://example.com")
        service._get(url="https://example.com")

        mock_sleep.assert_not_called()

    def test_jitter_is_added_to_sleep_time(self):
        mock_session = mock.MagicMock()
        mock_session.get.return_value = mock.Mock()
        mock_sleep = mock.MagicMock()
        mock_random = mock.MagicMock(return_value=0.5)
        # Simulate time: first at 0.0, second at 1.0
        mock_time = mock.MagicMock(side_effect=[0.0, 1.0])

        service = HTTPService(
            parser=mock.MagicMock(),
            session=mock_session,
            rate_limit_interval=3.5,
            rate_limit_jitter=1.0,
            sleep=mock_sleep,
            time_func=mock_time,
            random_func=mock_random,
        )
        service._get(url="https://example.com")
        service._get(url="https://example.com")

        mock_sleep.assert_called_once()
        sleep_arg = mock_sleep.call_args[0][0]
        # Should be (3.5 - 1.0) + 0.5 = 3.0
        self.assertAlmostEqual(sleep_arg, 3.0, places=1)


class TestHTTPServiceEnvVarFallback(TestCase):
    """Verify environment variable fallback for rate limiting configuration."""

    def test_env_var_fallback_for_interval(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_INTERVAL": "5.0"}):
            service = HTTPService(parser=mock.MagicMock())
            self.assertEqual(service._rate_limit_interval, 5.0)

    def test_env_var_fallback_for_jitter(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_JITTER": "2.0"}):
            service = HTTPService(parser=mock.MagicMock())
            self.assertEqual(service._rate_limit_jitter, 2.0)

    def test_constructor_args_override_env_vars(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_INTERVAL": "5.0"}):
            service = HTTPService(parser=mock.MagicMock(), rate_limit_interval=2.0)
            self.assertEqual(service._rate_limit_interval, 2.0)

    def test_constructor_jitter_override_env_vars(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_JITTER": "2.0"}):
            service = HTTPService(parser=mock.MagicMock(), rate_limit_jitter=0.5)
            self.assertEqual(service._rate_limit_jitter, 0.5)

    def test_default_interval_when_no_env_or_constructor(self):
        service = HTTPService(parser=mock.MagicMock())
        self.assertEqual(service._rate_limit_interval, 3.5)

    def test_default_jitter_when_no_env_or_constructor(self):
        service = HTTPService(parser=mock.MagicMock())
        self.assertEqual(service._rate_limit_jitter, 1.2)


class TestInvalidPlayer(TestCase):
    def test_message_format(self):
        exc = InvalidPlayer(player_identifier="jamesle01")
        self.assertEqual(str(exc), "Invalid player: jamesle01")

    def test_stores_player_identifier(self):
        exc = InvalidPlayer(player_identifier="jamesle01")
        self.assertEqual(exc.player_identifier, "jamesle01")

    def test_is_exception(self):
        exc = InvalidPlayer(player_identifier="jamesle01")
        self.assertIsInstance(exc, Exception)


class TestInvalidTeam(TestCase):
    def test_message_format(self):
        exc = InvalidTeam(team_abbreviation="LAL")
        self.assertEqual(str(exc), "Invalid team: LAL")

    def test_stores_team_abbreviation(self):
        exc = InvalidTeam(team_abbreviation="LAL")
        self.assertEqual(exc.team_abbreviation, "LAL")

    def test_is_exception(self):
        exc = InvalidTeam(team_abbreviation="LAL")
        self.assertIsInstance(exc, Exception)
