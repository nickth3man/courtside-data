"""Trace collection primitives used by courtside-data debug mode.

``DebugTrace`` is composed from several mixin classes that each own a
focused responsibility:

* :class:`DebugTraceCore` — event recording, artifacts, metrics, lifetime.
* :class:`SpansMixin` — nested spans, profiling (pyinstrument), exception recording.
* :class:`RowDiagnosticsMixin` — row-shape observation, header sanitisation.
* :class:`SerializationMixin` — ``to_dict()``, ``to_json()``, ``events_jsonl()``.

The module-level helpers ``current_debug_trace()`` and
``debug_trace_context()`` provide context-var-based access to the active
trace for a given endpoint call.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar

from courtside_data.debug._row_diagnostics import RowDiagnosticsMixin
from courtside_data.debug._serialization import SerializationMixin
from courtside_data.debug._spans import SpansMixin
from courtside_data.debug._trace_core import DebugTraceCore


class DebugTrace(DebugTraceCore, SpansMixin, RowDiagnosticsMixin, SerializationMixin):
    """Collect structured, bounded, AI-readable debugging data for one endpoint call.

    This class is a composite of four mixins — see the individual mixin
    docstrings for method-level documentation.
    """


_current_trace: ContextVar[DebugTrace | None] = ContextVar("courtside_data_debug_trace", default=None)


def current_debug_trace() -> DebugTrace | None:
    """Return the active :class:`DebugTrace` for this endpoint call, or ``None``."""
    return _current_trace.get()


@contextmanager
def debug_trace_context(trace: DebugTrace | None):
    """Set *trace* as the active debug trace for the duration of the block."""
    token = _current_trace.set(trace)
    try:
        yield
    finally:
        _current_trace.reset(token)
