"""Shared fixtures for the offline ``tests/new/`` suite.

Session-scoped ``stamina.set_testing`` and function-scoped ClassVar reset
live here so every module under ``tests/new/`` shares one canonical setup.
Module-level duplicates in the retry/jail unit tests were removed to avoid
the teardown hazard where ``set_testing(False)`` disables stamina for later
modules in the same pytest session.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
import stamina

from courtside_data.client.courtside_client import CourtsideClient
from courtside_data.http_service import HTTPService
from tests.new.fixture_manifest import Case
from tests.new.fixture_transport import FixtureTransport, build_service


@pytest.fixture(autouse=True, scope="session")
def stamina_testing():
    """Run stamina in test mode for the whole ``tests/new/`` session."""
    stamina.set_testing(True, attempts=3)
    yield
    stamina.set_testing(False)


@pytest.fixture(autouse=True)
def reset_http_service_classvars():
    """Clear HTTPService ClassVars mutated by rate-limit code paths after each test."""
    yield
    HTTPService._last_request_time = float("-inf")
    HTTPService._jailed_until = 0.0
    HTTPService._jail_state_loaded = False


@pytest.fixture
def make_offline_client() -> Callable[[Case], CourtsideClient]:
    """Build a :class:`CourtsideClient` wired to replay ``case.url_to_file``."""

    def _make(case: Case) -> CourtsideClient:
        transport = FixtureTransport(case.url_to_file)
        service = build_service(transport)
        return CourtsideClient(service=service)

    return _make
