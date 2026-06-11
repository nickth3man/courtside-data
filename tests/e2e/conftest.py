import httpx
import pytest

from courtside_data import http_service
from courtside_data.http_service import HTTPService
from tests.e2e.live_policy import LiveRequestPolicy, live_tests_enabled


def pytest_configure(config):
    if not live_tests_enabled():
        return

    original_get = HTTPService._get
    policy = LiveRequestPolicy()

    def guarded_get(self, url, **kwargs):
        return policy.request(lambda **request_kwargs: original_get(self, **request_kwargs), url=url, **kwargs)

    setattr(HTTPService, "_get", guarded_get)  # noqa: B010 — keep the patch visible to ty as a dynamic assignment

    # Never retry a 429 during live runs. Basketball-Reference jails sessions
    # that exceed its rate limit, so when it says back off, stop immediately
    # instead of letting stamina re-request while jailed.
    original_should_retry = http_service._should_retry

    def live_should_retry(exc: Exception) -> bool | float:
        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
            return False
        return original_should_retry(exc)

    http_service._should_retry = live_should_retry  # ty: ignore[invalid-assignment] — intentional live-mode patch


@pytest.fixture(autouse=True)
def skip_unless_live_tests_enabled():
    if not live_tests_enabled():
        pytest.skip("Set RUN_LIVE_BASKETBALL_REFERENCE_TESTS=1 to run live Basketball-Reference e2e tests")
