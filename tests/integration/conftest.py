"""
Pytest configuration for integration tests.

Auto-patches time.sleep so HTTPService's rate limiter is a no-op when
requests are mocked. The session-level conftest in tests/conftest.py sets
BASKETBALL_REF_RATE_LIMIT_INTERVAL=0 and _JITTER=0, which should disable
sleeps, but some tests construct HTTPService instances before the env vars
take effect or in subprocesses. This belt-and-suspenders fixture ensures
the integration suite stays fast in all cases.
"""
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _patch_rate_limiter():
    """Patch time.sleep to a no-op so rate-limit waits don't slow tests.

    All client-level integration tests use requests_mock to mock HTTP, but
    `HTTPService._apply_rate_limiting` still calls time.sleep before every
    request. This fixture patches sleep across every test in this directory
    tree, keeping the suite fast.
    """
    with patch("time.sleep"):
        yield
