"""Span, profile, and exception recording mixin."""

from __future__ import annotations

import traceback
from contextlib import contextmanager
from typing import Any


class SpansMixin:
    """Mixin that adds span tracking, profiling, and exception recording.

    Requires ``DebugTraceCore`` (or equivalent) to be in the MRO so that
    ``self.record()``, ``self._clock``, ``self._id_factory``,
    ``self._span_stack``, ``self.config``, and ``self.artifact`` are
    available.
    """

    # ------------------------------------------------------------------
    # Span tracking
    # ------------------------------------------------------------------

    @contextmanager
    def span(self, name: str, *, stage: str = "span", **attributes: Any):
        """Record start/end/error events for a nested operation.

        Yields the generated ``span_id`` so callers can pass it to
        ``record()`` or ``record_exception()``.
        """
        parent_span_id = self._span_stack[-1] if self._span_stack else None  # ty: ignore
        span_id = f"span_{self._id_factory()}"  # ty: ignore
        self.record(stage, "span_start", span_id=span_id, parent_span_id=parent_span_id, name=name, **attributes)  # ty: ignore
        self._span_stack.append(span_id)  # ty: ignore
        started = self._clock()  # ty: ignore
        try:
            yield span_id
        except BaseException as exc:
            self.record_exception(exc, stage=stage, span_id=span_id, escaped=True)
            self.record(  # ty: ignore
                stage,
                "span_end",
                status="error",
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                duration_ms=round((self._clock() - started) * 1000, 3),  # ty: ignore
            )
            raise
        else:
            self.record(  # ty: ignore
                stage,
                "span_end",
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                duration_ms=round((self._clock() - started) * 1000, 3),  # ty: ignore
            )
        finally:
            if self._span_stack and self._span_stack[-1] == span_id:  # ty: ignore
                self._span_stack.pop()  # ty: ignore

    # ------------------------------------------------------------------
    # Profiling
    # ------------------------------------------------------------------

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
        if not self.config.profile:  # ty: ignore
            yield
            return
        # Lazy import: keep the debug package cheap to import when profiling is off.
        # pyinstrument is intentionally a dev dependency; profiling is opt-in.
        from pyinstrument import Profiler  # deptry: ignore[DEP004]

        profiler = Profiler(interval=self.config.profile_interval)  # ty: ignore
        with self.span(name, stage="profile", **attributes):
            profiler.start()
            try:
                yield
            finally:
                profiler.stop()
                self.artifact(f"{name}_text", profiler.output_text())  # ty: ignore
                self.artifact(f"{name}_html", profiler.output_html())  # ty: ignore

    # ------------------------------------------------------------------
    # Exception recording
    # ------------------------------------------------------------------

    def record_exception(
        self,
        exception: BaseException,
        *,
        stage: str = "exception",
        span_id: str | None = None,
        escaped: bool = False,
        **attributes: Any,
    ) -> None:
        """Record exception details using OpenTelemetry-style attribute names.

        The trace status is set to ``{"code": "error", ...}`` and, if
        ``config.include_stacktraces`` is True, a full stacktrace is
        included.
        """
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
        if self.config.include_stacktraces:  # ty: ignore
            exception_attributes["exception.stacktrace"] = "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__)
            )
        self.record(stage, "exception", status="error", span_id=span_id, **exception_attributes)  # ty: ignore

    # ------------------------------------------------------------------
    # Span index
    # ------------------------------------------------------------------

    def spans(self) -> list[dict[str, Any]]:
        """Return a compact span index derived from span_start/span_end events."""
        spans: dict[str, dict[str, Any]] = {}
        for event in self.events:  # ty: ignore
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
