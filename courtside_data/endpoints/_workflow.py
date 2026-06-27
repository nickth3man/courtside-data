"""Workflow descriptors consumed by the executable workflow engine.

``EndpointKind.WORKFLOW`` registrations declare a ``WorkflowSpec`` whose typed
steps are executed, in order, by ``courtside_data.parsing.workflows``. The
descriptor is the ordered workflow contract; concrete Python step objects are
bound to those step ids by the workflow executor's native binding registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from courtside_data._frozen import frozen_slot


class WorkflowStepKind(StrEnum):
    """Closed vocabulary for workflow step categories."""

    BRANCH = "branch"
    DERIVE = "derive"
    DIAGNOSTICS = "diagnostics"
    FANOUT = "fanout"
    FETCH = "fetch"
    MERGE = "merge"
    PARSE = "parse"
    SELECT = "select"
    VALIDATE = "validate"


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkflowStep:
    """One named step in a workflow endpoint."""

    id: str
    kind: WorkflowStepKind
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parser_id: str | None = None


@frozen_slot
class WorkflowSpec:
    """Ordered executable shape for a workflow endpoint."""

    steps: tuple[WorkflowStep, ...]
    result: str = "rows"
