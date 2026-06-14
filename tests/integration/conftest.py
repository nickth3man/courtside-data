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


@pytest.fixture(autouse=True)
def _clear_http_service_selector_cache():
    """Clear the shared HTTPService selector cache between tests.

    The shared service is a process-level singleton, and its selector cache
    is meant to avoid re-fetching the same static page within a single
    session. In tests, mocks may return different bodies for the same URL,
    so we reset the cache before every integration test to keep tests
    independent.
    """
    from courtside_data.client import _runner

    service = _runner._shared_service
    if service is not None:
        service._selector_cache.clear()
    yield
