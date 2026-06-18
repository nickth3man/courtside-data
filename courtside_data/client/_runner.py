"""Template method shared by every endpoint function.

The per-endpoint *metadata* — URL path, table location, CSV columns, and
HTTP-status-to-domain-error mapping — lives in the
:data:`courtside_data.endpoints.ENDPOINTS` registry. The category modules
(``league``, ``players``, ``teams``, …) hold the explicit, typed function
definitions; each body is a thin call into :func:`_run_endpoint`.

:func:`_run_endpoint` resolves an
:class:`~courtside_data.http_service.HTTPService` through
:func:`courtside_data.client._runtime._locator._resolve_service`: a
``CourtsideClient`` method call binds its own service for the duration of
the call (via :data:`_service_override`, re-exported below), and
everything else shares one lazily-created process-wide service so HTTP
connections, the response cache, and the parser graph are reused across
calls.

The plumbing steps are split across :mod:`courtside_data.client._runtime`:

- :mod:`~courtside_data.client._runtime._locator` — service singleton
  + per-call override
- :mod:`~courtside_data.client._runtime._coerce` — typed-param
  coercion for custom endpoints
- :mod:`~courtside_data.client._runtime._output` — output
  formatting and debug-envelope wrapping
- :mod:`~courtside_data.client._runtime._flush` — best-effort,
  idempotent debug-trace flush
- :mod:`~courtside_data.client._runtime._execute` — service call →
  validation → output template
"""

from __future__ import annotations

import sys
from typing import Any

from courtside_data.client._runtime._coerce import _coerce_params
from courtside_data.client._runtime._execute import _execute
from courtside_data.client._runtime._flush import _flush_trace
from courtside_data.client._runtime._locator import _resolve_service, _service_override
from courtside_data.data import OutputType, OutputWriteOption
from courtside_data.debug import DebugTrace, debug_trace_context
from courtside_data.endpoints import ENDPOINTS
from courtside_data.parsing.custom import dispatch_custom_endpoint
from courtside_data.parsing.generic import GenericEndpointHandler

# Re-exported for ``CourtsideClient`` (``courtside_data.client.courtside_client``
# uses ``_runner._service_override.set(self._service)`` as its injection seam
# so the user's HTTPService rides on top of every nested helper for the
# duration of one method call). Other modules and tests should prefer the
# canonical path: ``courtside_data.client._runtime._locator._service_override``.
__all__ = ["_run_endpoint", "_service_override"]


def _run_endpoint(
    name: str,
    params: dict[str, Any],
    *,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Execute the registry-described endpoint ``name`` with bound call params.

    The :data:`ENDPOINTS` entry supplies the metadata (service dispatch, CSV
    columns, error mapping); the caller supplies an explicit, typed signature.
    """
    endpoint = ENDPOINTS[name]
    # Coerce raw string params (``"ATL"``) into typed values for custom
    # endpoints so the probe path and the typed-client path dispatch the
    # same way. Generic (non-custom) endpoints are unaffected; ``str``/``int``
    # URL params are idempotent.
    coerced_params = _coerce_params(name, params) if endpoint.custom else params
    trace = DebugTrace(endpoint=name, params=coerced_params) if debug else None
    if trace is not None:
        trace.record(
            "endpoint",
            "run_endpoint_start",
            endpoint=name,
            params=coerced_params,
            custom=endpoint.custom,
            path_template=endpoint.path,
            table_id=endpoint.table_id,
            commented_table_id=endpoint.commented_table_id,
            row_model=getattr(endpoint.row_model, "__name__", None),
            csv_columns=list(endpoint.csv_columns) if endpoint.csv_columns is not None else None,
        )

    def service_call() -> Any:
        service = _resolve_service()
        if endpoint.custom:
            if trace is not None:
                trace.record("endpoint", "custom_service_dispatch", method=name)
            return dispatch_custom_endpoint(service, name, **coerced_params)
        if trace is not None:
            trace.record("endpoint", "generic_service_dispatch", method="fetch_table")
        return GenericEndpointHandler(service).fetch_table(endpoint, **coerced_params)

    with debug_trace_context(trace):
        try:
            return _execute(
                service_call=service_call,
                csv_column_names=endpoint.csv_columns,
                error_mappings=endpoint.error_mappings(coerced_params),
                output_type=output_type,
                output_file_path=output_file_path,
                output_write_option=output_write_option,
                json_options=json_options,
                endpoint=endpoint,
                endpoint_name=name,
                endpoint_params=coerced_params,
                raw=raw,
                debug=debug,
                trace=trace,
            )
        finally:
            # Guarantee the trace envelope is persisted to disk on every
            # code path: when the call succeeds, ``_output_debug_result``
            # already flushed (idempotent no-op). When the call raises —
            # e.g. ``SchemaDriftError`` — the in-memory trace (with the
            # ``validation/pydantic_validation_failed`` event and any
            # ``exc.errors()`` payload) is flushed here as a last resort
            # so the failure is recoverable from ``./logs``. The raised
            # exception is preserved by Python's normal ``finally`` re-raise.
            if trace is not None:
                exc_info = sys.exc_info()
                if exc_info[1] is not None:
                    trace.record_exception(exc_info[1], stage="runner")
                _flush_trace(
                    trace,
                    data=None,
                    output_type=output_type,
                    output_file_path=output_file_path,
                    output_write_option=output_write_option,
                    json_options=json_options,
                )
