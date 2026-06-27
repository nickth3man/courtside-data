"""Typed-param coercion for workflow endpoints.

Workflow endpoints (``endpoint.kind is EndpointKind.WORKFLOW``) route through
the executable workflow engine. The live probe passes raw abbreviations
(``"ATL"``), while the typed client path may pass :class:`~courtside_data.domain.Team`
enums. :func:`_coerce_params` unifies those call paths from registry metadata:
only endpoints marked with :attr:`EndpointFeature.ENUM_PARAM_COERCION` are
checked, and only explicitly-listed params are coerced.

:data:`_TeamParam` is the ``Annotated[Team, BeforeValidator(_team_field)]``
alias that downstream Pydantic models reuse for ``Team`` fields. It is
defined here because it shares the same runtime validator as
:func:`_coerce_params`.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BeforeValidator

from courtside_data.domain import Team
from courtside_data.endpoints import ENDPOINTS, EndpointFeature, EndpointKind
from courtside_data.schemas._fields import _team_field

__all__ = [
    "_TeamParam",
    "_coerce_params",
]

# Annotate ``Team`` parameters so Pydantic coerces raw abbreviations
# (``"ATL"``) into the :class:`Team` enum before dispatch. Pydantic's default
# enum coercion matches ``.value`` (``"ATLANTA HAWKS"``), not the abbreviation
# the registry probe passes, so the runtime validator reuses the abbreviation
# table from the schemas package.
_TeamParam = Annotated[Team, BeforeValidator(_team_field)]

_WORKFLOW_ENUM_PARAM_COERCERS: dict[str, Callable[[Any], Any]] = {
    "home_team": _team_field,
}


def _coerce_params(endpoint_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Coerce raw string params into typed values for workflow endpoint methods.

    The probe path passes raw abbreviations (``"ATL"``) to the runner; the
    typed client path passes :class:`Team` enums. This helper unifies both
    paths from endpoint metadata. Other
    params are passed through untouched. A fresh dict is returned only when
    coercion is enabled so the caller's dict is never mutated.
    """
    endpoint = ENDPOINTS[endpoint_name]
    if (
        endpoint.kind is not EndpointKind.WORKFLOW
        or endpoint.metadata is None
        or EndpointFeature.ENUM_PARAM_COERCION not in endpoint.metadata.features
    ):
        return params
    coerced: dict[str, Any] = {}
    for key, value in params.items():
        coercer = _WORKFLOW_ENUM_PARAM_COERCERS.get(key)
        if coercer is not None and isinstance(value, str):
            try:
                coerced[key] = coercer(value)
            except ValueError as exc:
                raise ValueError(f"Invalid param {key!r} for endpoint {endpoint_name!r}: {exc}") from exc
        else:
            coerced[key] = value
    return coerced
