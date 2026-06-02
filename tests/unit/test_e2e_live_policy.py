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
        clock = _Clock([10, 11])
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

    def test_stops_immediately_on_rate_limit_response(self):
        policy = LiveRequestPolicy(max_requests=2, min_delay_seconds=0)

        with self.assertRaises(LiveRateLimitExceeded):
            policy.request(
                lambda **_: _Response(status_code=429, headers={"Retry-After": "3600"}),
                url="https://example.com/rate-limited",
            )

        with self.assertRaises(LiveRateLimitExceeded):
            policy.request(lambda **_: _Response(status_code=200), url="https://example.com/after-429")


class _Clock:
    def __init__(self, values):
        self._values = list(values)

    def __call__(self):
        return self._values.pop(0)


class _Response:
    def __init__(self, status_code, headers=None):
        self.status_code = status_code
        self.headers = headers or {}
