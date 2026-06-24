"""Executable workflow step implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from courtside_data.parsing.custom import dispatch_custom_endpoint

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext


@dataclass(frozen=True, slots=True)
class CallCustomHandlerStep:
    """Compatibility step that delegates to the legacy bespoke dispatcher."""

    def execute(self, context: WorkflowExecutionContext) -> Any:
        """Call ``dispatch_custom_endpoint`` and store the result in scratch."""
        result = dispatch_custom_endpoint(
            context.fetch._http,
            context.endpoint_name,
            **dict(context.params),
        )
        result_key = context.endpoint.workflow.result if context.endpoint.workflow is not None else "rows"
        context.scratch[result_key] = result
        return result


LegacyCustomHandlerStep = CallCustomHandlerStep
