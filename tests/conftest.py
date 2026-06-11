import os

import pytest
import pytest_socket


@pytest.fixture(autouse=True, scope="session")
def disable_rate_limiting():
    """Disable Basketball-Reference rate limiting for all non-e2e tests.

    HTTPService.__init__() reads BASKETBALL_REF_RATE_LIMIT_INTERVAL and
    BASKETBALL_REF_RATE_LIMIT_JITTER from the environment. Setting them to 0
    eliminates all time.sleep() calls during tests.
    """
    os.environ["BASKETBALL_REF_RATE_LIMIT_INTERVAL"] = "0"
    os.environ["BASKETBALL_REF_RATE_LIMIT_JITTER"] = "0"
    yield


def pytest_runtest_setup(item):
    """Block all network access in non-e2e tests.

    E2e tests can use @pytest.mark.enable_socket to opt back in.
    """
    if item.get_closest_marker("enable_socket"):
        return
    pytest_socket.disable_socket()
