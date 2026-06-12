import os
from unittest import mock

import pytest
import pytest_socket


@pytest.fixture(autouse=True, scope="session")
def disable_rate_limiting_and_tls():
    """Disable Basketball-Reference rate limiting and TLS impersonation for all non-e2e tests.

    Rate limiting: setting the env vars to 0 makes HTTPService.__init__()
    skip all time.sleep() calls during tests.

    TLS impersonation: ``CurlTransport`` from httpx-curl-cffi is incompatible
    with requests_mock/respx used in integration tests (it asserts
    ``"timeout" in req.extensions`` on every request). Patching build_client
    to force ``impersonate=None`` keeps the default behaviour for production
    code (Chrome 124 JA3/JA4 fingerprint) while tests get standard httpx.
    """
    os.environ["BASKETBALL_REF_RATE_LIMIT_INTERVAL"] = "0"
    os.environ["BASKETBALL_REF_RATE_LIMIT_JITTER"] = "0"
    # Keep tests hermetic: never read or write the on-disk jail state
    os.environ["BASKETBALL_REF_JAIL_STATE_PATH"] = ""

    from courtside_data import http_service

    _original_build_client = http_service.build_client

    def _test_build_client(**kwargs):
        kwargs["impersonate"] = None
        return _original_build_client(**kwargs)

    with mock.patch.object(http_service, "build_client", _test_build_client):
        yield


def pytest_runtest_setup(item):
    """Block all network access in non-e2e tests.

    E2e tests can use @pytest.mark.enable_socket to opt back in.
    """
    if item.get_closest_marker("enable_socket"):
        return
    pytest_socket.disable_socket()
