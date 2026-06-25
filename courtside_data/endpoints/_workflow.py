"""Workflow descriptors consumed by the executable workflow engine.

``EndpointKind.WORKFLOW`` registrations declare a ``WorkflowSpec`` whose step
ids are executed, in order, by ``courtside_data.parsing.workflows``. The
descriptor stays lightweight; concrete step implementations live in the
workflow executor's native handler map.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """One named step in a workflow endpoint."""

    id: str
    kind: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parser_id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowSpec:
    """Ordered executable shape for a workflow endpoint."""

    steps: tuple[WorkflowStep, ...]
    result: str = "rows"
