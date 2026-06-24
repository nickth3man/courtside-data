"""Lightweight workflow descriptors for bespoke endpoint metadata.

These value objects document the current shape of ``EndpointKind.WORKFLOW``
handlers. They are intentionally non-executable: runtime dispatch still lives
in the custom parsing layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """One documented step in a bespoke endpoint workflow."""

    id: str
    kind: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parser_id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowSpec:
    """Documentation-only workflow shape for a bespoke endpoint."""

    steps: tuple[WorkflowStep, ...]
    result: str = "rows"
