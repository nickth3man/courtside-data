"""Workflow endpoint execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from courtside_data.parsing.workflows._context import WorkflowExecutionContext
from courtside_data.parsing.workflows._steps import CallCustomHandlerStep

if TYPE_CHECKING:
    from courtside_data.endpoints import TableEndpoint
    from courtside_data.http_service import HTTPService


@dataclass(frozen=True, slots=True)
class WorkflowEndpointHandler:
    """Execute a registry-described workflow endpoint."""

    http: HTTPService

    def execute(self, endpoint_name: str, endpoint: TableEndpoint, params: dict[str, Any]) -> Any:
        """Run the workflow endpoint through its executable compatibility step."""
        if endpoint.workflow is None:
            raise ValueError(f"Endpoint {endpoint_name!r} does not declare a workflow spec.")
        context = WorkflowExecutionContext.from_http(
            self.http,
            endpoint_name=endpoint_name,
            endpoint=endpoint,
            params=params,
        )
        return CallCustomHandlerStep().execute(context)


def execute_workflow(http: HTTPService, endpoint_name: str, endpoint: TableEndpoint, params: dict[str, Any]) -> Any:
    """Execute one workflow endpoint with bound call params."""
    return WorkflowEndpointHandler(http).execute(endpoint_name, endpoint, params)
