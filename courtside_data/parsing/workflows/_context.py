"""Runtime state passed between executable workflow steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from courtside_data.parsing.workflow_parsers._fetch import FetchFacade

if TYPE_CHECKING:
    from collections.abc import Mapping

    from courtside_data.endpoints import EndpointSpec
    from courtside_data.http import HTTPService


@dataclass(frozen=True, slots=True)
class WorkflowExecutionContext:
    """Per-call workflow runtime state, separate from endpoint metadata."""

    endpoint_name: str
    endpoint: EndpointSpec
    params: Mapping[str, Any]
    fetch: FetchFacade
    scratch: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_http(
        cls,
        http: HTTPService,
        *,
        endpoint_name: str,
        endpoint: EndpointSpec,
        params: dict[str, Any],
    ) -> WorkflowExecutionContext:
        """Build a workflow context from the transport and bound endpoint params."""
        return cls(
            endpoint_name=endpoint_name,
            endpoint=endpoint,
            params=MappingProxyType(dict(params)),
            fetch=FetchFacade(http),
        )
