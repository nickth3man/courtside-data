"""Core trace event collection."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any, ClassVar

from courtside_data.debug._jsonish import _index_artifact, _jsonish, _prepare_artifact
from courtside_data.debug._runtime import _runtime_context, _severity_for_status
from courtside_data.debug.config import DebugConfig


class DebugTraceCore:
    """Core debug trace — event recording, artifacts, metrics, and lifecycle.

    This class is intended to be used as a base class in a mixin chain::

        class DebugTrace(DebugTraceCore, SpansMixin, ...):
            pass
    """

    capabilities: ClassVar[list[str]] = [
        "bounded_events",
        "bounded_artifacts",
        "redaction",
        "artifact_index",
        "exception_events",
        "json_export",
        "jsonl_event_export",
        "metrics",
        "row_diagnostics",
        "runtime_context",
        "span_events",
        "span_index",
    ]

    def __init__(
        self,
        *,
        endpoint: str,
        params: dict[str, Any],
        config: DebugConfig | None = None,
        trace_id: str | None = None,
        clock: Callable[[], float] | None = None,
        wall_clock_ns: Callable[[], int] | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self.config = config or DebugConfig()
        self.trace_id = trace_id or str(uuid.uuid4())
        self.endpoint = endpoint
        self.params = _jsonish(params, config=self.config)
        self._clock = clock or time.perf_counter
        self._wall_clock_ns = wall_clock_ns or time.time_ns
        self._id_factory = id_factory or (lambda: uuid.uuid4().hex)
        self._started = self._clock()
        self._started_unix_ns = self._wall_clock_ns()
        self._sequence = 0
        self._span_stack: list[str] = []
        self.events: list[dict[str, Any]] = []
        self.artifacts: dict[str, Any] = {}
        self.artifact_index: dict[str, dict[str, Any]] = {}
        self.metrics: dict[str, Any] = {}
        self.runtime: dict[str, Any] = _runtime_context(self.config)
        self.dropped_events = 0
        self.status: dict[str, Any] = {"code": "ok", "error_type": None, "error_message": None}
        if self.runtime:
            self.record("debug", "runtime_context_captured", **self.runtime)

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def started_unix_ns(self) -> int:
        """Wall-clock start time of this trace, in nanoseconds since the epoch."""
        return self._started_unix_ns

    # ------------------------------------------------------------------
    # Event recording
    # ------------------------------------------------------------------

    def record(
        self,
        stage: str,
        event: str,
        *,
        status: str = "ok",
        span_id: str | None = None,
        parent_span_id: str | None = None,
        **attributes: Any,
    ) -> None:
        """Record one structured event."""
        if self.config.max_events is not None and len(self.events) >= self.config.max_events:
            self.dropped_events += 1
            return

        self._sequence += 1
        active_parent = self._span_stack[-1] if self._span_stack else None
        resolved_parent = parent_span_id if parent_span_id is not None else active_parent
        self.events.append(
            {
                "sequence": self._sequence,
                "time_unix_ns": self._wall_clock_ns(),
                "elapsed_ms": self._elapsed_ms(),
                "stage": stage,
                "event": event,
                "status": status,
                "severity_text": _severity_for_status(status)[0],
                "severity_number": _severity_for_status(status)[1],
                "span_id": span_id,
                "parent_span_id": resolved_parent,
                "attributes": _jsonish(attributes, config=self.config),
            }
        )

    # ------------------------------------------------------------------
    # Artifacts
    # ------------------------------------------------------------------

    def artifact(self, name: str, value: Any) -> None:
        """Capture or replace a named artifact."""
        if not self.config.include_artifacts:
            _index_artifact(self.artifact_index, name, value, stored=False, truncated=False)
            self.record("debug", "artifact_skipped", name=name, reason="include_artifacts_false")
            return
        stored, metadata = _prepare_artifact(value, config=self.config)
        self.artifacts[name] = stored
        self.artifact_index[name] = metadata
        self.record("debug", "artifact_captured", name=name, **metadata)

    def append_artifact(self, name: str, value: Any) -> None:
        """Append one value to a list artifact."""
        if not self.config.include_artifacts:
            _index_artifact(self.artifact_index, name, value, stored=False, truncated=False)
            self.record("debug", "artifact_skipped", name=name, reason="include_artifacts_false")
            return

        values = self.artifacts.setdefault(name, [])
        if not isinstance(values, list):
            values = [values]
            self.artifacts[name] = values
        values.append(_jsonish(value, config=self.config))
        stored, metadata = _prepare_artifact(values, config=self.config)
        self.artifacts[name] = stored
        self.artifact_index[name] = metadata
        self.record("debug", "artifact_appended", name=name, count=metadata.get("stored_count"), **metadata)

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def metric(self, name: str, value: Any) -> None:
        """Store a scalar or small structured metric."""
        self.metrics[name] = _jsonish(value, config=self.config)
        self.record("debug", "metric_recorded", name=name, value=value)

    def increment(self, name: str, amount: int | float = 1) -> None:
        """Increment a numeric metric."""
        previous = self.metrics.get(name, 0)
        if not isinstance(previous, int | float):
            previous = 0
        self.metrics[name] = previous + amount
        self.record("debug", "metric_incremented", name=name, value=self.metrics[name], amount=amount)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def find(self, *, stage: str | None = None, event: str | None = None) -> list[dict[str, Any]]:
        """Return events matching *stage* and/or *event*."""
        return [
            item
            for item in self.events
            if (stage is None or item["stage"] == stage) and (event is None or item["event"] == event)
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _elapsed_ms(self) -> float:
        return round((self._clock() - self._started) * 1000, 3)
