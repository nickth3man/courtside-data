from unittest import TestCase

from tests.e2e.live_policy import (
    LIVE_TEST_ENVIRONMENT_VARIABLE,
    LiveRateLimitExceeded,
    LiveRequestLimitExceeded,
    LiveRequestPolicy,
    live_tests_enabled,
)


class TestLiveTestsEnabled(TestCase):
    def test_returns_true_only_when_environment_variable_is_one(self):
        self.assertTrue(live_tests_enabled({LIVE_TEST_ENVIRONMENT_VARIABLE: "1"}))
        self.assertFalse(live_tests_enabled({LIVE_TEST_ENVIRONMENT_VARIABLE: "true"}))
        self.assertFalse(live_tests_enabled({}))


class TestLiveRequestPolicy(TestCase):
    def test_stops_after_maximum_request_count(self):
        policy = LiveRequestPolicy(max_requests=2, min_delay_seconds=0)
        response = _Response(status_code=200)

        self.assertIs(response, policy.request(lambda **_: response, url="https://example.com/1"))
        self.assertIs(response, policy.request(lambda **_: response, url="https://example.com/2"))

        with self.assertRaises(LiveRequestLimitExceeded):
            policy.request(lambda **_: response, url="https://example.com/3")

    def test_delays_between_requests(self):
        # Third clock value is the post-sleep re-read for request 2.
        clock = _Clock([10, 11, 25])
        sleeps = []
        policy = LiveRequestPolicy(
            max_requests=2,
            min_delay_seconds=15,
            clock=clock,
            sleep=sleeps.append,
        )
        response = _Response(status_code=200)

        policy.request(lambda **_: response, url="https://example.com/1")
        policy.request(lambda **_: response, url="https://example.com/2")

        self.assertEqual([14], sleeps)

    def test_delay_is_measured_from_when_previous_request_fired(self):
        # Request 2 sleeps until t=25, so request 3 (attempted at t=26, only
        # one second after request 2 actually fired) must wait again rather
        # than measuring its delay from request 2's pre-sleep timestamp.
        clock = _Clock([10, 11, 25, 26, 40])
        sleeps = []
        policy = LiveRequestPolicy(
            max_requests=3,
            min_delay_seconds=15,
            clock=clock,
            sleep=sleeps.append,
        )
        response = _Response(status_code=200)

        policy.request(lambda **_: response, url="https://example.com/1")
        policy.request(lambda **_: response, url="https://example.com/2")
        policy.request(lambda **_: response, url="https://example.com/3")

        self.assertEqual([14, 14], sleeps)

    def test_stops_immediately_on_rate_limit_response(self):
        policy = LiveRequestPolicy(max_requests=2, min_delay_seconds=0)

        with self.assertRaises(LiveRateLimitExceeded):
            policy.request(
                lambda **_: _Response(status_code=429, headers={"Retry-After": "3600"}),
                url="https://example.com/rate-limited",
            )

        with self.assertRaises(LiveRateLimitExceeded):
            policy.request(lambda **_: _Response(status_code=200), url="https://example.com/after-429")

    def test_stops_immediately_on_raised_rate_limit_error(self):
        # HTTPService._get raise_for_status()es inside its retry loop, so a
        # 429 reaches the policy as an exception carrying a response, never
        # as a returned response.
        policy = LiveRequestPolicy(max_requests=2, min_delay_seconds=0)

        def raise_status_error(**_):
            raise _StatusError(_Response(status_code=429, headers={"Retry-After": "3600"}))

        with self.assertRaises(LiveRateLimitExceeded):
            policy.request(raise_status_error, url="https://example.com/rate-limited")

        with self.assertRaises(LiveRateLimitExceeded):
            policy.request(lambda **_: _Response(status_code=200), url="https://example.com/after-429")

    def test_reraises_non_rate_limit_errors_without_tripping_kill_switch(self):
        policy = LiveRequestPolicy(max_requests=2, min_delay_seconds=0)

        def raise_status_error(**_):
            raise _StatusError(_Response(status_code=404))

        with self.assertRaises(_StatusError):
            policy.request(raise_status_error, url="https://example.com/missing")

        response = _Response(status_code=200)
        self.assertIs(response, policy.request(lambda **_: response, url="https://example.com/after-404"))


class _Clock:
    def __init__(self, values):
        self._values = list(values)

    def __call__(self):
        return self._values.pop(0)


class _Response:
    def __init__(self, status_code, headers=None):
        self.status_code = status_code
        self.headers = headers or {}


class _StatusError(Exception):
    def __init__(self, response):
        self.response = response
        super().__init__(f"status {response.status_code}")
