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
from courtside_data.endpoints import ENDPOINTS, EndpointSpec


def _endpoint_group_map() -> dict[str, str]:
    # ``endpoint_group`` is a deprecated alias of ``endpoint_domain``
    # (``metadata.domain.value``). It is retained only because the probe CSV
    # and report consumers still read it; new code should use
    # ``endpoint_domain`` / :func:`_endpoint_domain` instead.
    return {
        endpoint_name: endpoint.metadata.domain.value
        for endpoint_name, endpoint in ENDPOINTS.items()
        if endpoint.metadata is not None
    }


_ENDPOINT_GROUPS = _endpoint_group_map()


def _endpoint_domain(endpoint: EndpointSpec | None) -> str | None:
    """Canonical endpoint-domain field (preferred over ``endpoint_group``)."""
    if endpoint is None or endpoint.metadata is None:
        return None
    return endpoint.metadata.domain.value


def _endpoint_kind(endpoint: EndpointSpec | None) -> str | None:
    """Canonical endpoint-kind field (``generic_table`` / ``workflow``)."""
    if endpoint is None or endpoint.metadata is None:
        return None
    return endpoint.metadata.kind.value


def _legacy_endpoint_kind(endpoint: EndpointSpec | None) -> str | None:
    """Return the old implementation label kept for CSV/report compatibility.

    Reads the deprecated :attr:`~courtside_data.endpoints.EndpointSpec.custom`
    compatibility property (``"custom"`` for workflow endpoints, ``"generic"``
    otherwise). Prefer :func:`_endpoint_kind` (``generic_table`` / ``workflow``)
    in new code; this remains so historical probe CSVs keep their column.
    """
    if endpoint is None:
        return None
    return "custom" if endpoint.custom else "generic"


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
