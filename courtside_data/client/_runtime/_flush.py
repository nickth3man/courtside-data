r"""Idempotent debug-trace envelope flush to disk.

Mirrors OTel's "SHOULD ignore subsequent calls to End" semantics: a
per-trace flag is held in :data:`_flushed_traces`, a
:class:`weakref.WeakKeyDictionary` keyed on the trace's identity, so the
success-path flush (from :func:`_output_debug_result`) and a surrounding
``finally``-block flush (from :func:`_run_endpoint`) can both run without
double-writing the same envelope. Entries are dropped automatically when
the trace is garbage-collected.

On disk failure the flush :func:`warnings.warn`\ s and continues (matching
:mod:`courtside_data.debug.sink` semantics); ``KeyboardInterrupt`` and
``SystemExit`` are NOT swallowed — only ``Exception`` is caught.

On the failure path, ``data`` is ``None``; the envelope is written as
``{"data": None, "debug": trace.to_dict()}`` so the full trace (including
any ``validation/pydantic_validation_failed`` events with
``exc.errors()``) is recoverable from disk.

:mod:`courtside_data.client._runtime._flush` lazy-imports
:func:`_make_output_service` from :mod:`courtside_data.client._runtime._output`
at call time to break the ``_output`` ↔ ``_flush`` import cycle
(``_output._output_debug_result`` calls back into
:func:`_flush_trace`).
"""

from __future__ import annotations

import warnings
import weakref
from typing import Any

from courtside_data.data import OutputType, OutputWriteOption
from courtside_data.debug import DebugTrace
from courtside_data.debug.sink import debug_log_path, prepare_log_dir
from courtside_data.output.writers import FileOptions, OutputOptions

__all__ = [
    "_flush_trace",
    "_flushed_traces",
]

# Track which traces have already been flushed, so the success path's flush
# and a surrounding ``finally`` flush don't both write the same envelope.
# Keyed by the trace's identity; entries are dropped when the trace is GC'd.
_flushed_traces: weakref.WeakKeyDictionary[DebugTrace, bool] = weakref.WeakKeyDictionary()


def _flush_trace(
    trace: DebugTrace,
    data: Any,
    *,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> None:
    """Best-effort, idempotent write of the debug trace envelope to disk.

    Mirrors OTel's "SHOULD ignore subsequent calls to End" semantics: a
    per-trace flag is held in a module-level :class:`weakref.WeakKeyDictionary`
    so the success path can flush and a surrounding ``finally`` can also
    flush without double-writing. On disk failure the flush warns and
    continues (matching :mod:`courtside_data.debug.sink` semantics);
    ``KeyboardInterrupt`` and ``SystemExit`` are NOT swallowed — only
    ``Exception`` is caught.

    On the failure path, ``data`` is ``None``; the envelope is written as
    ``{"data": None, "debug": trace.to_dict()}`` so the full trace
    (including any ``validation/pydantic_validation_failed`` events with
    ``exc.errors()``) is recoverable from disk.
    """
    # Lazy import to break the _output ↔ _flush import cycle: _output defines
    # _make_output_service and calls back into this function, so this module
    # must not import _output at module-load time.
    from courtside_data.client._runtime._output import _make_output_service

    if _flushed_traces.get(trace):
        return
    try:
        trace.record("debug", "envelope_created", data_type=type(data).__name__)
        trace.observe_rows("result_data", data)
        trace.record(
            "output",
            "debug_output_start",
            output_type=output_type.name if output_type is not None else None,
            output_file_path=output_file_path,
            output_write_option=output_write_option.name if output_write_option is not None else None,
        )
        trace.record("output", "debug_output_ready", envelope_keys=["data", "debug"])
        log_path = debug_log_path(trace)
        trace.record("output", "trace_log", path=str(log_path))
        envelope = {"data": data, "debug": trace.to_dict()}
        if prepare_log_dir(log_path):
            _make_output_service().output(
                data=envelope,
                options=OutputOptions.of(
                    file_options=FileOptions.of(path=str(log_path), mode=OutputWriteOption.WRITE),
                    output_type=OutputType.JSON,
                    json_options=json_options,
                    csv_options={"column_names": None},
                ),
            )
    except Exception as error:  # best-effort disk write, must not raise
        warnings.warn(
            f"Failed to flush debug trace {trace.trace_id} for endpoint {trace.endpoint!r}: {error}",
            stacklevel=2,
        )
        return
    _flushed_traces[trace] = True
