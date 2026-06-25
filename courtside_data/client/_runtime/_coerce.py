"""Typed-param coercion for workflow endpoints.

Workflow endpoints (``endpoint.kind is EndpointKind.WORKFLOW``) are dispatched
through the workflow executor, which delegates to the bespoke
:class:`~courtside_data.parsing.custom.CustomEndpointHandler` methods. The
probe path passes raw abbreviations (``"ATL"``); the typed-client path passes
:class:`~courtside_data.data.Team` enums. :func:`_coerce_params` unifies
both by walking the cached method annotations and running
:func:`courtside_data.schemas._fields._team_field` on any param whose
annotation is :class:`Team` and whose value is a raw string. Other params
are passed through untouched (the dispatch path already handles
``int``/``str`` idempotently). A fresh dict is returned so the caller's
dict is never mutated.

:func:`_params_hints` is an ``@lru_cache(maxsize=128)`` over
``inspect.signature`` + ``get_type_hints(..., include_extras=True)`` for
each workflow-endpoint method, so the introspection work happens once per
endpoint and stays off the hot path. It returns ``None`` for generic-table
endpoints so the dispatch path is free of Pydantic overhead.

:data:`_TeamParam` is the ``Annotated[Team, BeforeValidator(_team_field)]``
alias that downstream Pydantic models reuse for ``Team`` fields. It is
defined here because it shares the same runtime validator as
:func:`_coerce_params`.
"""

from __future__ import annotations

import inspect
from functools import lru_cache
from typing import Annotated, Any, get_type_hints

from pydantic import BeforeValidator

from courtside_data.data import Team
from courtside_data.endpoints import ENDPOINTS, EndpointKind
from courtside_data.parsing.custom import CustomEndpointHandler
from courtside_data.schemas._fields import _team_field

__all__ = [
    "_TeamParam",
    "_coerce_params",
    "_params_hints",
]

# Annotate ``Team`` parameters so Pydantic coerces raw abbreviations
# (``"ATL"``) into the :class:`Team` enum before dispatch. Pydantic's default
# enum coercion matches ``.value`` (``"ATLANTA HAWKS"``), not the abbreviation
# the registry probe passes, so the runtime validator reuses the abbreviation
# table from the schemas package.
_TeamParam = Annotated[Team, BeforeValidator(_team_field)]


@lru_cache(maxsize=128)
def _params_hints(endpoint_name: str) -> dict[str, Any] | None:
    """Return the cached ``{param_name: annotation}`` for one workflow endpoint.

    Returns ``None`` for generic-table endpoints so the dispatch path
    stays free of Pydantic overhead. Per-endpoint hints are computed once
    and reused for every call; the ``@lru_cache`` decorator keeps the
    ``inspect``/``get_type_hints`` work off the hot path.
    """
    endpoint = ENDPOINTS[endpoint_name]
    if endpoint.kind is not EndpointKind.WORKFLOW:
        return None
    method = getattr(CustomEndpointHandler, endpoint_name, None)
    if method is None:
        return None
    try:
        sig = inspect.signature(method)
        hints = get_type_hints(method, include_extras=True)
    except (TypeError, ValueError, NameError):
        # Some methods may have unresolvable forward references; skip coercion
        # rather than break the dispatch path.
        return None
    fields: dict[str, Any] = {}
    for pname, param in sig.parameters.items():
        if pname == "self":
            continue
        ann = hints.get(pname, param.annotation)
        if ann is inspect.Parameter.empty:
            continue
        fields[pname] = ann
    return fields or None


def _coerce_params(endpoint_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Coerce raw string params into typed values for workflow endpoint methods.

    The probe path passes raw abbreviations (``"ATL"``) to the runner; the
    typed client path passes :class:`Team` enums. This helper unifies both
    paths by walking the cached method annotations and running ``_team_field``
    on any param whose annotation is :class:`Team` and whose value is a raw
    string. Other params are passed through untouched (the dispatch path
    already handles ``int``/``str`` idempotently). A fresh dict is returned
    so the caller's dict is never mutated.
    """
    hints = _params_hints(endpoint_name)
    if hints is None:
        return params
    coerced: dict[str, Any] = {}
    for key, value in params.items():
        if hints.get(key) is Team and isinstance(value, str):
            try:
                coerced[key] = _team_field(value)
            except ValueError as exc:
                raise ValueError(f"Invalid param {key!r} for endpoint {endpoint_name!r}: {exc}") from exc
        else:
            coerced[key] = value
    return coerced
