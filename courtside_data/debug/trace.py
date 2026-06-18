"""Trace collection primitives used by courtside-data debug mode."""

from __future__ import annotations

import hashlib
import math
import os
import platform
import socket
import time
import traceback
import uuid
from collections.abc import Callable, Iterable, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from importlib import metadata
from typing import Any, ClassVar

import orjson

from courtside_data.debug.config import DebugConfig

_current_trace: ContextVar[DebugTrace | None] = ContextVar("courtside_data_debug_trace", default=None)


class DebugTrace:
    """Collect structured, bounded, AI-readable debugging data for one endpoint call."""

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

    @property
    def started_unix_ns(self) -> int:
        """Wall-clock start time of this trace, in nanoseconds since the epoch."""
        return self._started_unix_ns

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

    def artifact(self, name: str, value: Any) -> None:
        """Capture or replace a named artifact."""
        if not self.config.include_artifacts:
            self._index_artifact(name, value, stored=False, truncated=False)
            self.record("debug", "artifact_skipped", name=name, reason="include_artifacts_false")
            return
        stored, metadata = self._prepare_artifact(value)
        self.artifacts[name] = stored
        self.artifact_index[name] = metadata
        self.record("debug", "artifact_captured", name=name, **metadata)

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

    def append_artifact(self, name: str, value: Any) -> None:
        """Append one value to a list artifact."""
        if not self.config.include_artifacts:
            self._index_artifact(name, value, stored=False, truncated=False)
            self.record("debug", "artifact_skipped", name=name, reason="include_artifacts_false")
            return

        values = self.artifacts.setdefault(name, [])
        if not isinstance(values, list):
            values = [values]
            self.artifacts[name] = values
        values.append(_jsonish(value, config=self.config))
        stored, metadata = self._prepare_artifact(values)
        self.artifacts[name] = stored
        self.artifact_index[name] = metadata
        self.record("debug", "artifact_appended", name=name, count=metadata.get("stored_count"), **metadata)

    @contextmanager
    def span(self, name: str, *, stage: str = "span", **attributes: Any):
        """Record start/end/error events for a nested operation."""
        parent_span_id = self._span_stack[-1] if self._span_stack else None
        span_id = f"span_{self._id_factory()}"
        self.record(stage, "span_start", span_id=span_id, parent_span_id=parent_span_id, name=name, **attributes)
        self._span_stack.append(span_id)
        started = self._clock()
        try:
            yield span_id
        except BaseException as exc:
            self.record_exception(exc, stage=stage, span_id=span_id, escaped=True)
            self.record(
                stage,
                "span_end",
                status="error",
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                duration_ms=round((self._clock() - started) * 1000, 3),
            )
            raise
        else:
            self.record(
                stage,
                "span_end",
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                duration_ms=round((self._clock() - started) * 1000, 3),
            )
        finally:
            if self._span_stack and self._span_stack[-1] == span_id:
                self._span_stack.pop()

    @contextmanager
    def profile(self, name: str = "profile", **attributes: Any):
        """Optionally profile the wrapped block with pyinstrument.

        When ``self.config.profile`` is False (the default) this is a
        zero-overhead pass-through: it does not import ``pyinstrument`` and
        yields immediately.

        When ``self.config.profile`` is True it lazily imports
        ``pyinstrument.Profiler``, starts it at ``self.config.profile_interval``,
        yields, and on exit renders both the text and HTML profile reports
        and stores them as debug artifacts (``<name>_text`` and ``<name>_html``).
        The wrapped block is also recorded as a span so the profile window
        shows up in the trace event log.
        """
        if not self.config.profile:
            yield
            return
        # Lazy import: keep the debug package cheap to import when profiling is off.
        # pyinstrument is intentionally a dev dependency; profiling is opt-in.
        from pyinstrument import Profiler  # deptry: ignore[DEP004]

        profiler = Profiler(interval=self.config.profile_interval)
        with self.span(name, stage="profile", **attributes):
            profiler.start()
            try:
                yield
            finally:
                profiler.stop()
                self.artifact(f"{name}_text", profiler.output_text())
                self.artifact(f"{name}_html", profiler.output_html())

    def record_exception(
        self,
        exception: BaseException,
        *,
        stage: str = "exception",
        span_id: str | None = None,
        escaped: bool = False,
        **attributes: Any,
    ) -> None:
        """Record exception details using OpenTelemetry-style attribute names."""
        self.status = {
            "code": "error",
            "error_type": type(exception).__name__,
            "error_message": str(exception),
        }
        exception_attributes: dict[str, Any] = {
            "exception.type": type(exception).__name__,
            "exception.message": str(exception),
            "exception.escaped": escaped,
            **attributes,
        }
        if self.config.include_stacktraces:
            exception_attributes["exception.stacktrace"] = "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__)
            )
        self.record(stage, "exception", status="error", span_id=span_id, **exception_attributes)

    def observe_rows(
        self,
        name: str,
        rows: Any,
        *,
        expected_columns: Iterable[str] | None = None,
    ) -> None:
        """Capture row-shape, column, nullness, and type diagnostics."""
        if not self.config.include_row_diagnostics:
            return
        row_list = _rows_as_dicts(rows)
        diagnostics = _row_diagnostics(
            row_list,
            expected_columns=tuple(expected_columns) if expected_columns is not None else None,
            max_examples=self.config.max_column_examples,
        )
        self.artifact(f"{name}_diagnostics", diagnostics)
        self.record(
            "diagnostics",
            "rows_observed",
            name=name,
            row_count=diagnostics["row_count"],
            column_count=len(diagnostics["columns"]),
            missing_expected_columns=diagnostics["missing_expected_columns"],
            extra_columns=diagnostics["extra_columns"],
        )

    def sanitize_headers(self, headers: Mapping[str, Any]) -> dict[str, Any]:
        """Return lower-cased, redacted response headers allowed by DebugConfig."""
        result = {}
        for key, value in headers.items():
            normalized = str(key).lower()
            if normalized in self.config.safe_response_headers:
                result[normalized] = _jsonish(value, config=self.config, key=normalized)
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 3,
            "capabilities": list(self.capabilities),
            "trace_id": self.trace_id,
            "endpoint": self.endpoint,
            "params": self.params,
            "started_unix_ns": self._started_unix_ns,
            "duration_ms": self._elapsed_ms(),
            "status": self.status,
            "runtime": self.runtime,
            "limits": _jsonish(asdict(self.config), config=self.config),
            "metrics": self.metrics,
            "stage_counts": self.stage_counts(),
            "dropped_events": self.dropped_events,
            "spans": self.spans(),
            "events": self.events,
            "artifact_index": self.artifact_index,
            "artifacts": self.artifacts,
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        options = orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS
        if indent:
            options |= orjson.OPT_INDENT_2
        return orjson.dumps(self.to_dict(), option=options).decode("utf-8")

    def events_jsonl(self) -> str:
        if not self.events:
            return ""
        options = orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS
        return b"\n".join(orjson.dumps(event, option=options) for event in self.events).decode("utf-8")

    def stage_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for event in self.events:
            stage = str(event["stage"])
            counts[stage] = counts.get(stage, 0) + 1
        return counts

    def spans(self) -> list[dict[str, Any]]:
        """Return a compact span index derived from span_start/span_end events."""
        spans: dict[str, dict[str, Any]] = {}
        for event in self.events:
            span_id = event.get("span_id")
            if not span_id:
                continue
            attributes = event.get("attributes", {})
            if event["event"] == "span_start":
                spans[span_id] = {
                    "span_id": span_id,
                    "parent_span_id": event.get("parent_span_id"),
                    "name": attributes.get("name"),
                    "stage": event["stage"],
                    "status": event["status"],
                    "start_sequence": event["sequence"],
                    "end_sequence": None,
                    "start_time_unix_ns": event["time_unix_ns"],
                    "end_time_unix_ns": None,
                    "start_elapsed_ms": event["elapsed_ms"],
                    "end_elapsed_ms": None,
                    "duration_ms": None,
                    "attributes": {key: value for key, value in attributes.items() if key != "name"},
                    "error_type": None,
                    "error_message": None,
                }
                continue
            span = spans.setdefault(
                span_id,
                {
                    "span_id": span_id,
                    "parent_span_id": event.get("parent_span_id"),
                    "name": None,
                    "stage": event["stage"],
                    "status": event["status"],
                    "start_sequence": None,
                    "end_sequence": None,
                    "start_time_unix_ns": None,
                    "end_time_unix_ns": None,
                    "start_elapsed_ms": None,
                    "end_elapsed_ms": None,
                    "duration_ms": None,
                    "attributes": {},
                    "error_type": None,
                    "error_message": None,
                },
            )
            if event["event"] == "span_end":
                span["status"] = event["status"]
                span["end_sequence"] = event["sequence"]
                span["end_time_unix_ns"] = event["time_unix_ns"]
                span["end_elapsed_ms"] = event["elapsed_ms"]
                span["duration_ms"] = attributes.get("duration_ms")
            elif event["event"] == "exception":
                span["status"] = "error"
                span["error_type"] = attributes.get("exception.type")
                span["error_message"] = attributes.get("exception.message")
        return sorted(spans.values(), key=lambda span: span["start_sequence"] or 0)

    def find(self, *, stage: str | None = None, event: str | None = None) -> list[dict[str, Any]]:
        return [
            item
            for item in self.events
            if (stage is None or item["stage"] == stage) and (event is None or item["event"] == event)
        ]

    def _elapsed_ms(self) -> float:
        return round((self._clock() - self._started) * 1000, 3)

    def _prepare_artifact(self, value: Any) -> tuple[Any, dict[str, Any]]:
        json_value = _jsonish(value, config=self.config)
        sampled, truncated, original_count = _sample_artifact(json_value, self.config)
        metadata = self._artifact_metadata(sampled, original_count=original_count, truncated=truncated, stored=True)
        return sampled, metadata

    def _index_artifact(self, name: str, value: Any, *, stored: bool, truncated: bool) -> None:
        self.artifact_index[name] = self._artifact_metadata(
            value,
            original_count=_count_items(value),
            truncated=truncated,
            stored=stored,
        )

    def _artifact_metadata(
        self,
        value: Any,
        *,
        original_count: int | None,
        truncated: bool,
        stored: bool,
    ) -> dict[str, Any]:
        encoded = orjson.dumps(value, option=orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS, default=str)
        metadata = {
            "type": type(value).__name__,
            "stored": stored,
            "truncated": truncated,
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "stored_count": _count_items(value),
            "original_count": original_count,
            "byte_length": len(encoded),
        }
        if isinstance(value, list) and value and isinstance(value[0], dict):
            metadata["row_keys"] = sorted(value[0])
        if isinstance(value, dict):
            metadata["keys"] = sorted(value)
        return metadata


def current_debug_trace() -> DebugTrace | None:
    return _current_trace.get()


@contextmanager
def debug_trace_context(trace: DebugTrace | None):
    token = _current_trace.set(trace)
    try:
        yield
    finally:
        _current_trace.reset(token)


def _jsonish(value: Any, *, config: DebugConfig, key: str | None = None, depth: int = 0) -> Any:
    if key is not None and _should_redact(key, config.redact_keys):
        return "<redacted>"
    if config.max_depth is not None and depth >= config.max_depth:
        return "<max-depth-exceeded>"
    if hasattr(value, "model_dump"):
        return _jsonish(value.model_dump(mode="json"), config=config, depth=depth + 1)
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonish(asdict(value), config=config, depth=depth + 1)
    if isinstance(value, Mapping):
        return {
            str(item_key): _jsonish(item_value, config=config, key=str(item_key), depth=depth + 1)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [_jsonish(item, config=config, depth=depth + 1) for item in value]
    if isinstance(value, tuple):
        return [_jsonish(item, config=config, depth=depth + 1) for item in value]
    if isinstance(value, set):
        return sorted(_jsonish(item, config=config, depth=depth + 1) for item in value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, str) and config.max_string_length is not None and len(value) > config.max_string_length:
        return f"{value[: config.max_string_length]}...<truncated {len(value) - config.max_string_length} chars>"
    if isinstance(value, bytes):
        return f"<bytes len={len(value)} sha256={hashlib.sha256(value).hexdigest()}>"
    try:
        orjson.dumps(value)
    except (TypeError, orjson.JSONEncodeError):
        return repr(value)
    return value


def _runtime_context(config: DebugConfig) -> dict[str, Any]:
    if not config.include_runtime:
        return {}
    try:
        package_version = metadata.version("courtside-data")
    except metadata.PackageNotFoundError:
        package_version = None
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "package_version": package_version,
        "service.name": "courtside-data",
        "service.version": package_version,
        "telemetry.sdk.name": "courtside_data.debug",
        "telemetry.sdk.language": "python",
        "telemetry.sdk.version": package_version,
        "instrumentation_scope.name": "courtside_data.debug",
        "instrumentation_scope.version": package_version,
        "process.pid": os.getpid(),
        "process.runtime.name": platform.python_implementation(),
        "process.runtime.version": platform.python_version(),
        "host.name": socket.gethostname(),
    }


def _rows_as_dicts(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, list):
        values = rows
    elif isinstance(rows, dict):
        values = next((value for value in rows.values() if isinstance(value, list)), [])
    else:
        return []
    result = []
    for row in values:
        if hasattr(row, "model_dump"):
            result.append(row.model_dump(mode="json"))
        elif isinstance(row, Mapping):
            result.append(dict(row))
    return result


def _row_diagnostics(
    rows: list[dict[str, Any]],
    *,
    expected_columns: tuple[str, ...] | None,
    max_examples: int,
) -> dict[str, Any]:
    columns = sorted({key for row in rows for key in row})
    expected = list(expected_columns or [])
    missing_expected = [column for column in expected if column not in columns]
    extra = [column for column in columns if expected_columns is not None and column not in expected_columns]
    by_column: dict[str, Any] = {}
    for column in columns:
        present_count = 0
        empty_count = 0
        type_counts: dict[str, int] = {}
        examples = []
        for row in rows:
            if column not in row:
                continue
            present_count += 1
            value = row.get(column)
            if value in (None, "", [], {}, set()):
                empty_count += 1
            type_name = type(value).__name__
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            if len(examples) < max_examples and value not in (None, "", [], {}, set()):
                examples.append(value)
        by_column[column] = {
            "present_count": present_count,
            "missing_count": len(rows) - present_count,
            "empty_count": empty_count,
            "type_counts": type_counts,
            "examples": examples,
        }
    return {
        "row_count": len(rows),
        "columns": columns,
        "expected_columns": expected,
        "missing_expected_columns": missing_expected,
        "extra_columns": extra,
        "by_column": by_column,
    }


def _should_redact(key: str, redact_keys: Iterable[str]) -> bool:
    normalized = key.lower().replace("_", "-")
    return any(redact_key.lower().replace("_", "-") in normalized for redact_key in redact_keys)


def _severity_for_status(status: str) -> tuple[str, int]:
    if status == "error":
        return "ERROR", 17
    if status == "cancelled":
        return "WARN", 13
    return "INFO", 9


def _sample_artifact(value: Any, config: DebugConfig) -> tuple[Any, bool, int | None]:
    max_items = config.max_artifact_items
    if max_items is None:
        return value, False, _count_items(value)
    if isinstance(value, list) and len(value) > max_items:
        if config.artifact_sample == "tail":
            return value[-max_items:], True, len(value)
        if config.artifact_sample == "head_tail" and max_items > 2:
            head_count = max_items // 2
            tail_count = max_items - head_count - 1
            sampled = [
                *value[:head_count],
                {"__debug_truncation__": len(value) - max_items},
                *value[-tail_count:],
            ]
            return sampled, True, len(value)
        return value[:max_items], True, len(value)
    if isinstance(value, dict) and len(value) > max_items:
        items = list(value.items())
        if config.artifact_sample == "tail":
            sampled_items = items[-max_items:]
        elif config.artifact_sample == "head_tail" and max_items > 2:
            head_count = max_items // 2
            tail_count = max_items - head_count - 1
            sampled_items = [
                *items[:head_count],
                ("__debug_truncation__", len(items) - max_items),
                *items[-tail_count:],
            ]
        else:
            sampled_items = items[:max_items]
        return dict(sampled_items), True, len(value)
    return value, False, _count_items(value)


def _count_items(value: Any) -> int | None:
    if isinstance(value, list | tuple | set | dict):
        return len(value)
    return None
