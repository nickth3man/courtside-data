import os
from unittest import TestCase, mock

import httpx

from courtside_data.errors import InvalidDate, InvalidPlayer, InvalidTeam, RateLimitJailed
from courtside_data.http_service import _MAX_RETRY_AFTER_WAIT, HTTPService, _should_retry


class TestHTTPService(TestCase):
    def test_player_box_scores_raises_invalid_date_for_300_response(self):
        response = mock.Mock(status_code=httpx.codes.MULTIPLE_CHOICES)
        session = mock.MagicMock()
        session.get.return_value = response
        self.assertRaisesRegex(
            InvalidDate,
            "Date with year set to 2018, month set to 1, and day set to 1 is invalid",
            HTTPService(parser=mock.MagicMock(), session=session, rate_limit_interval=0).player_box_scores,
            day=1,
            month=1,
            year=2018,
        )


class TestHTTPServiceBackwardCompatibility(TestCase):
    """Ensure existing HTTPService(parser) construction remains valid."""

    def test_constructor_with_parser_only(self):
        parser = mock.MagicMock()
        service = HTTPService(parser=parser, impersonate=None)
        self.assertIs(service.parser, parser)

    def test_session_created_by_default(self):
        service = HTTPService(parser=mock.MagicMock(), impersonate=None)
        self.assertIsNotNone(service._session)


class TestHTTPServiceSessionReuse(TestCase):
    """Verify _get uses the provided/injected session."""

    def test_default_session_is_httpx_client(self):
        service = HTTPService(parser=mock.MagicMock(), impersonate=None)
        self.assertIsInstance(service._session, httpx.Client)

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
        service._get(url="https://example.com", follow_redirects=False, params={"key": "val"})

        mock_session.get.assert_called_once_with(
            url="https://example.com",
            follow_redirects=False,
            params={"key": "val"},
        )


class TestHTTPServiceRateLimiting(TestCase):
    """Verify rate limiting behavior with injected time/sleep."""

    def setUp(self):
        # Reset class-level rate limiting state between tests
        HTTPService._last_request_time = float("-inf")

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
        # Simulate time progression: first call at 0.0, second at 1.0 (less than 6.0s interval)
        # _apply_rate_limiting calls _time() twice, _get() pacing reset calls it once more (3 per call)
        mock_time = mock.MagicMock(side_effect=[0.0, 0.0, 0.0, 1.0, 1.0, 1.0])

        service = HTTPService(
            parser=mock.MagicMock(),
            session=mock_session,
            rate_limit_interval=6.0,
            rate_limit_jitter=0.0,
            sleep=mock_sleep,
            time_func=mock_time,
        )
        service._get(url="https://example.com")
        service._get(url="https://example.com")

        # Should sleep for 6.0 - 1.0 = 5.0 seconds (interval - elapsed)
        mock_sleep.assert_called_once()
        sleep_arg = mock_sleep.call_args[0][0]
        self.assertAlmostEqual(sleep_arg, 5.0, places=1)

    def test_interval_zero_disables_sleep(self):
        mock_session = mock.MagicMock()
        mock_session.get.return_value = mock.Mock()
        mock_sleep = mock.MagicMock()
        # _apply_rate_limiting calls _time() twice, _get() pacing reset calls it once more (3 per call)
        mock_time = mock.MagicMock(side_effect=[0.0, 0.0, 0.0, 0.5, 0.5, 0.5])

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
        # _apply_rate_limiting calls _time() twice, _get() pacing reset calls it once more (3 per call)
        mock_time = mock.MagicMock(side_effect=[0.0, 0.0, 0.0, 1.0, 1.0, 1.0])

        service = HTTPService(
            parser=mock.MagicMock(),
            session=mock_session,
            rate_limit_interval=6.0,
            rate_limit_jitter=1.0,
            sleep=mock_sleep,
            time_func=mock_time,
            random_func=mock_random,
        )
        service._get(url="https://example.com")
        service._get(url="https://example.com")

        mock_sleep.assert_called_once()
        sleep_arg = mock_sleep.call_args[0][0]
        # Should be (6.0 - 1.0) + 0.5 = 5.5
        self.assertAlmostEqual(sleep_arg, 5.5, places=1)


class TestHTTPServiceEnvVarFallback(TestCase):
    """Verify environment variable fallback for rate limiting configuration."""

    def test_env_var_fallback_for_interval(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_INTERVAL": "5.0"}):
            service = HTTPService(parser=mock.MagicMock(), impersonate=None)
            self.assertEqual(service._rate_limit_interval, 5.0)

    def test_env_var_fallback_for_jitter(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_JITTER": "2.0"}):
            service = HTTPService(parser=mock.MagicMock(), impersonate=None)
            self.assertEqual(service._rate_limit_jitter, 2.0)

    def test_constructor_args_override_env_vars(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_INTERVAL": "5.0"}):
            service = HTTPService(parser=mock.MagicMock(), rate_limit_interval=2.0, impersonate=None)
            self.assertEqual(service._rate_limit_interval, 2.0)

    def test_constructor_jitter_override_env_vars(self):
        with mock.patch.dict(os.environ, {"BASKETBALL_REF_RATE_LIMIT_JITTER": "2.0"}):
            service = HTTPService(parser=mock.MagicMock(), rate_limit_jitter=0.5, impersonate=None)
            self.assertEqual(service._rate_limit_jitter, 0.5)

    def test_default_interval_when_no_env_or_constructor(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            service = HTTPService(parser=mock.MagicMock(), impersonate=None)
            self.assertEqual(service._rate_limit_interval, 6.0)

    def test_default_jitter_when_no_env_or_constructor(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            service = HTTPService(parser=mock.MagicMock(), impersonate=None)
            self.assertEqual(service._rate_limit_jitter, 1.0)


class TestShouldRetryRetryAfterCap(TestCase):
    """The honored Retry-After wait must be capped: stamina uses a
    hook-returned float verbatim, so an uncapped hour-plus Retry-After from a
    jailed session would make a single request sleep that entire time."""

    @staticmethod
    def _status_error(status_code, headers=None):
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(status_code, headers=headers, request=request)
        return httpx.HTTPStatusError("error", request=request, response=response)

    def test_small_retry_after_is_honored(self):
        wait = _should_retry(self._status_error(429, headers={"Retry-After": "5"}))
        self.assertEqual(wait, 5.0)

    def test_huge_retry_after_returns_false(self):
        """3600s exceeds jail threshold (300s), so returns False (don't retry)."""
        wait = _should_retry(self._status_error(429, headers={"Retry-After": "3600"}))
        self.assertIs(wait, False)

    def test_429_without_retry_after_retries_with_default_backoff(self):
        self.assertIs(_should_retry(self._status_error(429)), True)

    def test_client_errors_are_not_retried(self):
        self.assertIs(_should_retry(self._status_error(404)), False)

    def test_jail_threshold_boundary_exactly_300_returns_capped_not_false(self):
        """300s exactly is NOT above threshold, so returns capped value."""
        wait = _should_retry(self._status_error(429, headers={"Retry-After": "300"}))
        self.assertEqual(wait, _MAX_RETRY_AFTER_WAIT)

    def test_jail_threshold_above_300_returns_false(self):
        """301s is above threshold, returns False (don't retry)."""
        wait = _should_retry(self._status_error(429, headers={"Retry-After": "301"}))
        self.assertIs(wait, False)

    def test_retry_after_60_seconds_still_honored(self):
        wait = _should_retry(self._status_error(429, headers={"Retry-After": "60"}))
        self.assertEqual(wait, 60.0)


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


class TestHTTPServiceDefaultHeaders(TestCase):
    """Default browser-like headers (Phase 1A)."""

    def test_default_session_has_user_agent(self):
        service = HTTPService(parser=mock.MagicMock(), impersonate=None)
        headers = service._session.headers
        self.assertIn("User-Agent", headers)
        self.assertIn("Chrome/124.0.0.0", headers["User-Agent"])

    def test_default_session_has_sec_fetch_headers(self):
        service = HTTPService(parser=mock.MagicMock(), impersonate=None)
        headers = service._session.headers
        self.assertEqual(headers.get("Sec-Fetch-Dest"), "document")
        self.assertEqual(headers.get("Sec-Fetch-Mode"), "navigate")

    def test_custom_headers_override_defaults(self):
        service = HTTPService(
            parser=mock.MagicMock(),
            headers={"User-Agent": "MyCustomAgent/1.0"},
            impersonate=None,
        )
        self.assertEqual(service._session.headers["User-Agent"], "MyCustomAgent/1.0")


class TestRateLimitJailed(TestCase):
    """RateLimitJailed exception behavior."""

    def test_message_includes_retry_after_seconds(self):
        exc = RateLimitJailed(retry_after=600.0)
        self.assertIn("600s", str(exc))

    def test_message_includes_minutes(self):
        exc = RateLimitJailed(retry_after=600.0)
        self.assertIn("10.0 minutes", str(exc))

    def test_stores_retry_after(self):
        exc = RateLimitJailed(retry_after=3600.0)
        self.assertEqual(exc.retry_after, 3600.0)

    def test_is_exception(self):
        exc = RateLimitJailed(retry_after=300.0)
        self.assertIsInstance(exc, Exception)


class TestHTTPServiceCircuitBreaker(TestCase):
    """Circuit breaker (_jailed_until ClassVar) behavior (Phase 2B)."""

    def setUp(self):
        HTTPService._last_request_time = float("-inf")
        HTTPService._jailed_until = 0.0

    def test_jailed_requests_raise_immediately(self):
        """After setting _jailed_until to future, _apply_rate_limiting raises RateLimitJailed."""
        mock_time = mock.MagicMock(return_value=100.0)
        service = HTTPService(parser=mock.MagicMock(), time_func=mock_time, rate_limit_interval=0, impersonate=None)
        HTTPService._jailed_until = 200.0  # Future timestamp
        with self.assertRaises(RateLimitJailed) as ctx:
            service._apply_rate_limiting()
        self.assertAlmostEqual(ctx.exception.retry_after, 100.0)  # 200 - 100

    def test_jail_expires_after_duration(self):
        """After _jailed_until passes, requests proceed normally."""
        mock_session = mock.MagicMock()
        mock_session.get.return_value = mock.Mock()
        mock_time = mock.MagicMock(return_value=200.0)
        service = HTTPService(
            parser=mock.MagicMock(),
            session=mock_session,
            time_func=mock_time,
            rate_limit_interval=0,
        )
        HTTPService._jailed_until = 100.0  # Past timestamp
        # Should NOT raise — jail has expired
        service._get(url="https://example.com")
        mock_session.get.assert_called_once()

    def test_jail_is_shared_across_instances(self):
        """ClassVar _jailed_until is shared across all HTTPService instances."""
        mock_time = mock.MagicMock(return_value=100.0)
        HTTPService._jailed_until = 200.0
        service1 = HTTPService(parser=mock.MagicMock(), time_func=mock_time, rate_limit_interval=0, impersonate=None)
        service2 = HTTPService(parser=mock.MagicMock(), time_func=mock_time, rate_limit_interval=0, impersonate=None)
        with self.assertRaises(RateLimitJailed):
            service1._apply_rate_limiting()
        with self.assertRaises(RateLimitJailed):
            service2._apply_rate_limiting()
