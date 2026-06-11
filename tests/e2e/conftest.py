import pytest

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


@pytest.fixture(autouse=True)
def skip_unless_live_tests_enabled():
    if not live_tests_enabled():
        pytest.skip("Set RUN_LIVE_BASKETBALL_REFERENCE_TESTS=1 to run live Basketball-Reference e2e tests")
