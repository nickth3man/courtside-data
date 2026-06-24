"""Workflow execution compatibility tests."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.data import Team
from courtside_data.parsing.workflows import CallCustomHandlerStep, WorkflowExecutionContext


def test_workflow_endpoint_dispatches_through_compatibility_step(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_execute(self: CallCustomHandlerStep, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        calls.append((context.endpoint_name, dict(context.params)))
        context.scratch["rows"] = []
        return []

    monkeypatch.setattr(CallCustomHandlerStep, "execute", fake_execute)

    result = _run_endpoint(
        "play_by_play",
        {"home_team": Team.ATLANTA_HAWKS, "day": 1, "month": 1, "year": 2024},
    )

    assert result == []
    assert calls == [
        (
            "play_by_play",
            {"home_team": Team.ATLANTA_HAWKS, "day": 1, "month": 1, "year": 2024},
        )
    ]
