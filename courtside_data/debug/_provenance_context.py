"""Provenance context management.

Owns the per-trace :class:`ProvenanceContext` storage and the helpers
that fetch / create contexts for an active :class:`DebugTrace`.
"""

from __future__ import annotations

from weakref import WeakKeyDictionary

from courtside_data.debug._provenance_types import ProvenanceContext
from courtside_data.debug.trace import DebugTrace

_TRACE_CONTEXTS: WeakKeyDictionary[DebugTrace, ProvenanceContext] = WeakKeyDictionary()
_SAMPLE_LIMIT = 5


def trace_context(trace: DebugTrace) -> ProvenanceContext:
    context = _TRACE_CONTEXTS.get(trace)
    if context is None:
        context = ProvenanceContext()
        _TRACE_CONTEXTS[trace] = context
    return context


def get_trace_context(trace: DebugTrace | None) -> ProvenanceContext | None:
    if trace is None:
        return None
    return _TRACE_CONTEXTS.get(trace)
