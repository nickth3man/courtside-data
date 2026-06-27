import os
from collections.abc import Callable
from unittest import mock

import pytest
import pytest_socket
import stamina
from courtside_data.client.courtside_client import CourtsideClient
from courtside_data.http import _rate_limit

from tests.fixture_manifest import Case
from tests.fixture_transport import FixtureTransport, build_service


@pytest.fixture(autouse=True, scope="session")
def disable_rate_limiting_and_tls():
    """Disable Basketball-Reference rate limiting and TLS impersonation for tests.

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

    from courtside_data import http

    _original_build_client = http.build_client

    def _test_build_client(**kwargs):
        kwargs["impersonate"] = None
        return _original_build_client(**kwargs)

    with mock.patch.object(http, "build_client", _test_build_client):
        yield


@pytest.fixture(autouse=True, scope="session")
def stamina_testing():
    """Run stamina in test mode for the whole offline test session."""
    stamina.set_testing(True, attempts=3)
    yield
    stamina.set_testing(False)


@pytest.fixture(autouse=True)
def reset_http_rate_limit_state():
    """Clear module-level rate-limit state mutated by rate-limit code paths."""
    yield
    _rate_limit._last_request_time = float("-inf")
    _rate_limit._jailed_until = 0.0
    _rate_limit._jail_state_loaded = False


@pytest.fixture(autouse=True)
def isolate_debug_logs(tmp_path_factory):
    """Keep debug trace logs out of the repo: redirect ./logs to a temp dir.

    Any test that runs an endpoint with ``debug=True`` writes one JSON file per
    call; without this redirect those files would land in the working-directory
    ``logs/`` folder. Tests that assert on the log path set the env var
    themselves, which overrides this default.
    """
    if not os.environ.get("COURTSIDE_DEBUG_LOG_DIR"):
        os.environ["COURTSIDE_DEBUG_LOG_DIR"] = str(tmp_path_factory.mktemp("debug-logs"))


@pytest.fixture
def make_offline_client() -> Callable[[Case], CourtsideClient]:
    """Build a :class:`CourtsideClient` wired to replay ``case.url_to_file``."""

    def _make(case: Case) -> CourtsideClient:
        transport = FixtureTransport(case.url_to_file)
        service = build_service(transport)
        return CourtsideClient(service=service)

    return _make


def pytest_runtest_setup(item):
    """Block all network access in offline tests."""
    pytest_socket.disable_socket()
