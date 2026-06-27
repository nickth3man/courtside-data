"""The :func:`_execute` template: service call → validation → output.

The runner's per-endpoint pipeline is composed of two pieces:

- :func:`_call_with_error_mapping` — invokes the ``service_call`` closure
  built by :func:`courtside_data.client._runner._run_endpoint` and
  translates mapped HTTP status codes to domain errors
  (``InvalidSeason``/``InvalidTeam``/``InvalidPlayer``/``InvalidDate``/
  ``InvalidSearch``/``InvalidPlayerAndSeason``). :class:`RateLimitJailed`
  (raised by :class:`HTTPService` on jail detection) is a domain
  exception that propagates naturally — it is not caught here because
  it is not an :class:`httpx.HTTPStatusError`.

- :func:`_execute` — the template method. It (1) wires the service call
  through :func:`_call_with_error_mapping` inside a debug-trace span
  (when one is active), (2) validates rows through the declared
  Pydantic row-model pipeline, and (3) hands the
  validated data to :func:`_output_debug_result`
  (when ``debug=True``) or :func:`_format_output` (otherwise).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import httpx

from courtside_data.client._pipelines.pydantic import validate_rows_pydantic
from courtside_data.client._runtime._output import _format_output, _output_debug_result
from courtside_data.debug import DebugTrace
from courtside_data.domain import OutputType, OutputWriteOption

__all__ = [
    "_call_with_error_mapping",
    "_execute",
]


def _call_with_error_mapping(
    service_call: Callable[[], Any],
    error_mappings: dict[int, Callable[[], Exception]] | None,
) -> Any:
    """Invoke the service call, translating mapped HTTP status codes to domain errors.

    RateLimitJailed (raised by HTTPService on jail detection) is a domain
    exception that propagates naturally — it is not caught here because it
    is not an httpx.HTTPStatusError.
    """
    try:
        return service_call()
    except httpx.HTTPStatusError as http_error:
        if error_mappings:
            factory = error_mappings.get(http_error.response.status_code)
            if factory:
                raise factory() from http_error
        raise


def _execute(
    service_call: Callable[[], Any],
    csv_column_names: Sequence[str] | None = None,
    error_mappings: dict[int, Callable[[], Exception]] | None = None,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    validate_output: bool = True,
    *,
    endpoint: Any = None,
    endpoint_name: str | None = None,
    endpoint_params: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
    trace: DebugTrace | None = None,
) -> Any:
    if debug and output_type in (OutputType.CSV, OutputType.DATAFRAME):
        raise ValueError("debug=True is only supported with Python-returned data or OutputType.JSON.")

    if trace is not None:
        trace.metric("debug.enabled", True)
        trace.record(
            "runner",
            "execute_start",
            output_type=output_type.name if output_type is not None else None,
            output_file_path=output_file_path,
            validate_output=validate_output,
            raw=raw,
        )

    if trace is not None:
        with trace.span("service_call", stage="runner"):
            values = _call_with_error_mapping(service_call, error_mappings)
    else:
        values = _call_with_error_mapping(service_call, error_mappings)
    if trace is not None:
        trace.record("runner", "service_call_complete", value_type=type(values).__name__)
        trace.artifact("service_values", values)
        trace.observe_rows("service_values", values, expected_columns=csv_column_names)

    row_model = getattr(endpoint, "row_model", None)
    if row_model is None:
        raise RuntimeError(f"Endpoint {endpoint_name!r} does not declare a row_model.")
    data, csv_column_names = validate_rows_pydantic(
        values,
        row_model=row_model,
        endpoint=endpoint,
        endpoint_name=endpoint_name,
        endpoint_params=endpoint_params,
        csv_column_names=csv_column_names,
        output_type=output_type,
        raw=raw,
        trace=trace,
    )

    if debug and trace is not None:
        return _output_debug_result(
            data,
            trace,
            output_type,
            output_file_path,
            output_write_option,
            json_options,
        )

    return _format_output(
        data,
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        csv_column_names=csv_column_names,
    )
