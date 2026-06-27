"""Output formatting and debug-envelope wrapping.

Three collaborators live here:

- :func:`_make_output_service` — one-line factory that returns an
  :class:`~courtside_data.output.service.OutputService` wired with the
  default :class:`JSONWriter` and :class:`CSVWriter`. Centralised so
  every code path writes JSON/CSV the same way.

- :func:`_format_output` — strategy-pattern dispatch: builds
  :class:`OutputOptions` from the caller's ``output_type``,
  ``output_file_path``, ``output_write_option``, ``json_options``, and
  ``csv_column_names``, then hands the data to
  :meth:`OutputService.output`. When ``output_type is None`` the Python
  data structure is returned unchanged.

- :func:`_output_debug_result` — the ``debug=True`` wrapper. It flushes
  the trace envelope to disk via :func:`_flush_trace` (idempotent — a
  surrounding ``finally`` may also flush if the call later raises, but
  only one write happens) and returns the same envelope through the
  output service so the caller gets ``{"data": ..., "debug": ...}`` back
  on stdout / in the output file.

:mod:`courtside_data.client._runtime._flush` lazy-imports
:func:`_make_output_service` at call time to break the
``_output`` ↔ ``_flush`` circular import.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from courtside_data.client._runtime._flush import _flush_trace
from courtside_data.debug import DebugTrace
from courtside_data.domain import OutputType, OutputWriteOption
from courtside_data.output.fields import format_value
from courtside_data.output.service import OutputService
from courtside_data.output.writers import CSVWriter, FileOptions, JSONWriter, OutputOptions

__all__ = [
    "_format_output",
    "_make_output_service",
    "_output_debug_result",
]


def _make_output_service() -> OutputService:
    return OutputService(
        json_writer=JSONWriter(),
        csv_writer=CSVWriter(value_formatter=format_value),
    )


def _format_output(
    data: Any,
    *,
    output_type: OutputType | None,
    output_file_path: str | None,
    output_write_option: OutputWriteOption | None,
    json_options: dict[str, Any] | None,
    csv_column_names: Sequence[str] | None,
) -> Any:
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": csv_column_names},
    )
    return _make_output_service().output(data=data, options=options)


def _output_debug_result(
    data: Any,
    trace: DebugTrace,
    output_type: OutputType | None,
    output_file_path: str | None,
    output_write_option: OutputWriteOption | None,
    json_options: dict[str, Any] | None,
) -> Any:
    # Persist the envelope to disk (idempotent: a surrounding ``finally`` may
    # also flush if the call later raises, but only one write happens).
    _flush_trace(
        trace,
        data,
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )
    envelope = {"data": data, "debug": trace.to_dict()}
    return _make_output_service().output(
        data=envelope,
        options=OutputOptions.of(
            file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
            output_type=output_type,
            json_options=json_options,
            csv_options={"column_names": None},
        ),
    )
