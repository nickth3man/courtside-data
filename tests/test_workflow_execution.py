"""Workflow execution compatibility tests."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.parsing.workflows import CallCustomHandlerStep, WorkflowExecutionContext


def test_workflow_endpoint_dispatches_through_compatibility_step(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_execute(self: CallCustomHandlerStep, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        calls.append((context.endpoint_name, dict(context.params)))
        context.scratch["rows"] = []
        return []

    monkeypatch.setattr(CallCustomHandlerStep, "execute", fake_execute)

    result = _run_endpoint("team_box_scores", {"day": 1, "month": 1, "year": 2024})

    assert result == []
    assert calls == [("team_box_scores", {"day": 1, "month": 1, "year": 2024})]
