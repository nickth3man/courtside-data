"""Offline fixture manifest for the ``courtside-data`` test suite.

The manifest owns the public ``(endpoint, params) -> {url: file_or_error}``
catalogue consumed by the offline transport. Private helper modules do the
fixture discovery and URL construction; this module keeps the stable import
surface used by tests.
"""

from __future__ import annotations

from courtside_data.endpoints import ENDPOINTS

from tests._fixture_manifest_common import BASE_URL, PROJECT_ROOT, RAW_ROOT, Case
from tests._fixture_manifest_errors import build_error_cases
from tests._fixture_manifest_resolvers import is_multi_request_fixture_endpoint, resolve_endpoint
from tests.fixture_transport import FixtureValue


def _build_all_cases() -> tuple[list[Case], list[str]]:
    """Walk every endpoint in ``ENDPOINTS`` and emit zero or more cases."""
    cases: list[Case] = []
    unresolved: list[str] = []
    for name, endpoint in sorted(ENDPOINTS.items()):
        endpoint_cases, reason = resolve_endpoint(name, endpoint)
        if endpoint_cases is None:
            unresolved.append(f"{name} ({reason})")
            continue
        cases.extend(endpoint_cases)
    cases.sort(key=lambda c: c.id)
    return cases, unresolved


_ALL_CASES_RAW, _UNRESOLVED = _build_all_cases()
_ERROR_CASES = build_error_cases()

_MULTI_REQUEST_NAMES: frozenset[str] = frozenset(
    {case.endpoint_name for case in _ALL_CASES_RAW if is_multi_request_fixture_endpoint(ENDPOINTS[case.endpoint_name])}
)


ALL_CASES: list[Case] = list(_ALL_CASES_RAW)
"""Every successfully-resolved endpoint/fixture case, sorted by id."""


ERROR_CASES: list[Case] = _ERROR_CASES
"""Cases that serve a synthetic 404 and exercise domain error paths."""


MULTI_REQUEST_ENDPOINTS: frozenset[str] = _MULTI_REQUEST_NAMES
"""Custom endpoints needing a multi-URL map."""


GENERIC_CASES: list[Case] = [case for case in ALL_CASES if case.endpoint_name not in MULTI_REQUEST_ENDPOINTS]
"""``ALL_CASES`` minus the multi-request custom endpoints."""


MULTI_REQUEST_CASES: list[Case] = [case for case in ALL_CASES if case.endpoint_name in MULTI_REQUEST_ENDPOINTS]
"""Every resolved multi-fetch custom endpoint case."""


TIER1_EXCLUDED_CASE_IDS: frozenset[str] = frozenset()

TIER1_CASES: list[Case] = [case for case in GENERIC_CASES if case.id not in TIER1_EXCLUDED_CASE_IDS]
"""``GENERIC_CASES`` minus known parser/schema gaps."""


UNRESOLVED_ENDPOINTS: list[str] = sorted(_UNRESOLVED)
"""Endpoint names with no or insufficient fixtures."""


def transport_map(endpoint_name: str, **params: object) -> dict[str, FixtureValue]:
    """Return the url_to_file dict for the case matching ``endpoint_name`` and params."""
    for case in ALL_CASES:
        if case.endpoint_name != endpoint_name:
            continue
        if case.params == params:
            return case.url_to_file

    if endpoint_name.startswith("error-"):
        for case in ERROR_CASES:
            if case.endpoint_name == endpoint_name:
                return case.url_to_file

    same_endpoint = [case for case in ALL_CASES if case.endpoint_name == endpoint_name]
    raise KeyError(
        f"No manifest case for endpoint={endpoint_name!r} params={params!r}. "
        f"Available cases for this endpoint: {[case.params for case in same_endpoint] or 'NONE'}"
    )


def case_for(endpoint_name: str, **params: object) -> Case | None:
    """Return the matching :class:`Case` or ``None`` if no case matches."""
    for case in ALL_CASES:
        if case.endpoint_name == endpoint_name and case.params == params:
            return case
    if endpoint_name.startswith("error-"):
        for case in ERROR_CASES:
            if case.endpoint_name == endpoint_name:
                return case
    return None


__all__ = [
    "ALL_CASES",
    "BASE_URL",
    "ERROR_CASES",
    "GENERIC_CASES",
    "MULTI_REQUEST_CASES",
    "MULTI_REQUEST_ENDPOINTS",
    "PROJECT_ROOT",
    "RAW_ROOT",
    "TIER1_CASES",
    "TIER1_EXCLUDED_CASE_IDS",
    "UNRESOLVED_ENDPOINTS",
    "Case",
    "case_for",
    "transport_map",
]
