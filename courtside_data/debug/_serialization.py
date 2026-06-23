"""Serialization mixin for to_dict, to_json, and events_jsonl."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import orjson

from courtside_data.debug._jsonish import _jsonish


class SerializationMixin:
    """Mixin that adds dict/JSON/JSONL export.

    Requires ``DebugTraceCore`` and ``SpansMixin`` in the MRO so that
    ``self.capabilities``, ``self.trace_id``, ``self.endpoint``,
    ``self.params``, ``self._started_unix_ns``, ``self._elapsed_ms()``,
    ``self.status``, ``self.runtime``, ``self.config``, ``self.metrics``,
    ``self.dropped_events``, ``self.events``, ``self.artifact_index``,
    ``self.artifacts``, ``self.spans()``, and ``self.stage_counts()``
    are available.
    """

    def to_dict(self) -> dict[str, Any]:
        """Return the full trace as a JSON-serialisable dictionary.

        .. important::

            The envelope shape (``schema_version``, key order, and value
            semantics) is part of the ``schema.json`` contract (version 3).
            Changes here must preserve byte-identical output.
        """
        return {
            "schema_version": 3,
            "capabilities": list(self.capabilities),  # ty: ignore
            "trace_id": self.trace_id,  # ty: ignore
            "endpoint": self.endpoint,  # ty: ignore
            "params": self.params,  # ty: ignore
            "started_unix_ns": self._started_unix_ns,  # ty: ignore
            "duration_ms": self._elapsed_ms(),  # ty: ignore
            "status": self.status,  # ty: ignore
            "runtime": self.runtime,  # ty: ignore
            "limits": _jsonish(asdict(self.config), config=self.config),  # ty: ignore
            "metrics": self._trace_summary_metrics(),
            "stage_counts": self.stage_counts(),
            "dropped_events": self.dropped_events,  # ty: ignore
            "spans": self.spans(),  # ty: ignore
            "events": self.events,  # ty: ignore
            "artifact_index": self.artifact_index,  # ty: ignore
            "artifacts": self.artifacts,  # ty: ignore
        }

    def _trace_summary_metrics(self) -> dict[str, Any]:
        """Merge scalar metrics with trace-size and truncation summaries."""
        metrics = dict(self.metrics)  # ty: ignore
        artifact_index = self.artifact_index  # ty: ignore
        truncated_artifacts = sum(
            1 for meta in artifact_index.values() if isinstance(meta, dict) and meta.get("truncated")
        )
        total_bytes = sum(int(meta.get("byte_length", 0)) for meta in artifact_index.values() if isinstance(meta, dict))
        metrics["trace.artifact_count"] = len(artifact_index)
        metrics["trace.truncated_artifact_count"] = truncated_artifacts
        metrics["trace.artifact_bytes"] = total_bytes
        metrics["trace.detail_level"] = self.config.detail_level  # ty: ignore
        return metrics

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize ``to_dict()`` to a JSON string."""
        options = orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS
        if indent:
            options |= orjson.OPT_INDENT_2
        return orjson.dumps(self.to_dict(), option=options).decode("utf-8")

    def events_jsonl(self) -> str:
        """Return newline-separated JSON for each event (JSON Lines format)."""
        if not self.events:  # ty: ignore
            return ""
        options = orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS
        return b"\n".join(orjson.dumps(event, option=options) for event in self.events).decode("utf-8")  # ty: ignore

    def stage_counts(self) -> dict[str, int]:
        """Return a map of stage-name → event-count for all recorded events."""
        counts: dict[str, int] = {}
        for event in self.events:  # ty: ignore
            stage = str(event["stage"])
            counts[stage] = counts.get(stage, 0) + 1
        return counts
