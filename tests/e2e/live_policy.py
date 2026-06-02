import os
import time


LIVE_TEST_ENVIRONMENT_VARIABLE = "RUN_LIVE_BASKETBALL_REFERENCE_TESTS"


class LiveRequestLimitExceeded(RuntimeError):
    pass


class LiveRateLimitExceeded(RuntimeError):
    pass


def live_tests_enabled(environ=None):
    if environ is None:
        environ = os.environ

    return environ.get(LIVE_TEST_ENVIRONMENT_VARIABLE) == "1"


class LiveRequestPolicy:
    def __init__(self, max_requests=3, min_delay_seconds=15, clock=None, sleep=None):
        self.max_requests = max_requests
        self.min_delay_seconds = min_delay_seconds
        self.clock = clock or time.monotonic
        self.sleep = sleep or time.sleep
        self._request_count = 0
        self._last_request_started_at = None
        self._rate_limited = False

    def request(self, get, url, **kwargs):
        self._before_request(url=url)
        response = get(url=url, **kwargs)
        self._after_response(url=url, response=response)
        return response

    def _before_request(self, url):
        if self._rate_limited:
            raise LiveRateLimitExceeded("Live e2e requests stopped after a 429 response")

        if self._request_count >= self.max_requests:
            raise LiveRequestLimitExceeded(
                "Live e2e request cap exceeded: {max_requests}. Last attempted URL: {url}".format(
                    max_requests=self.max_requests,
                    url=url,
                )
            )

        now = self.clock()
        if self._last_request_started_at is not None:
            elapsed = now - self._last_request_started_at
            remaining_delay = self.min_delay_seconds - elapsed
            if remaining_delay > 0:
                self.sleep(remaining_delay)

        self._request_count += 1
        self._last_request_started_at = now

    def _after_response(self, url, response):
        if response.status_code != 429:
            return

        self._rate_limited = True
        retry_after = response.headers.get("Retry-After")
        raise LiveRateLimitExceeded(
            "Basketball-Reference returned 429 for {url}. Retry-After: {retry_after}. "
            "Stop live e2e tests and allow a cooldown before retrying.".format(
                url=url,
                retry_after=retry_after or "not provided",
            )
        )
