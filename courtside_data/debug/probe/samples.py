"""Endpoint grouping and sample-parameter selection for the probe.

Builds the per-endpoint parameter set used to drive one live call each, layering
explicit live-audit overrides on top of the fixture-manifest base set.
"""

from __future__ import annotations

from tests.fixture_manifest import ALL_CASES

from courtside_data.debug.live_probe_cases import (
    LIVE_AUDIT_SOURCE,
    get_live_audit_sample,
)
from courtside_data.debug.probe.models import SampleParamsInfo
from courtside_data.endpoints import ENDPOINTS
from courtside_data.endpoints._custom import CUSTOM_ENDPOINTS
from courtside_data.endpoints._draft_awards_leaders import DRAFT_AWARDS_LEADERS_ENDPOINTS
from courtside_data.endpoints._league import LEAGUE_ENDPOINTS
from courtside_data.endpoints._players import PLAYER_ENDPOINTS
from courtside_data.endpoints._playoffs import PLAYOFF_ENDPOINTS
from courtside_data.endpoints._teams import TEAM_ENDPOINTS


def _endpoint_group_map() -> dict[str, str]:
    groups: dict[str, str] = {}
    for group_name, mapping in (
        ("league", LEAGUE_ENDPOINTS),
        ("playoffs", PLAYOFF_ENDPOINTS),
        ("draft_awards_leaders", DRAFT_AWARDS_LEADERS_ENDPOINTS),
        ("players", PLAYER_ENDPOINTS),
        ("teams", TEAM_ENDPOINTS),
        ("custom", CUSTOM_ENDPOINTS),
    ):
        for endpoint_name in mapping:
            groups[endpoint_name] = group_name
    return groups


_ENDPOINT_GROUPS = _endpoint_group_map()


def _sample_params_per_endpoint() -> dict[str, SampleParamsInfo]:
    """Build sample params for the live probe.

    Base set comes from the first sorted case in ``tests.fixture_manifest.ALL_CASES``
    (for backward compatibility and to cover every registered endpoint).

    Live-audit overrides (recent dense seasons) are applied on top for
    selected endpoints so that probe reports reflect modern tables instead
    of old historical fixtures that produce many expected nulls/drops.
    """
    params_by_endpoint: dict[str, SampleParamsInfo] = {}
    for case in sorted(ALL_CASES, key=lambda item: item.id):
        if case.endpoint_name not in params_by_endpoint:
            params_by_endpoint[case.endpoint_name] = SampleParamsInfo(
                params=dict(case.params),
                case_id=case.id,
                source="fixture_manifest",
            )
    for name, endpoint in ENDPOINTS.items():
        if name not in params_by_endpoint and not endpoint.params:
            params_by_endpoint[name] = SampleParamsInfo(params={}, case_id=None, source="empty_default")

    # Overlay explicit live-audit samples (preferred for the probe).
    # These do not affect ALL_CASES or any offline regression tests.
    for name in ENDPOINTS:
        live = get_live_audit_sample(name)
        if live is not None:
            params_by_endpoint[name] = SampleParamsInfo(
                params=dict(live),
                case_id=f"live_audit:{name}",
                source=LIVE_AUDIT_SOURCE,
            )

    return params_by_endpoint
