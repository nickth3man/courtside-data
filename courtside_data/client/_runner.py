"""Execution plumbing shared by every endpoint function.

All endpoint *metadata* — URL path, table location, CSV columns, and
HTTP-status-to-domain-error mapping — lives in the
:data:`courtside_data.endpoints.ENDPOINTS` registry. The category modules
(``league``, ``players``, ``teams``, …) hold the explicit, typed function
definitions; each body is a thin call into :func:`_run_endpoint`.

Every call resolves an :class:`~courtside_data.http_service.HTTPService`
through :func:`_resolve_service`: a ``CourtsideClient`` method call binds its
own service for the duration of the call, and everything else shares one
lazily-created process-wide service so HTTP connections, the response cache,
and the parser graph are reused across calls.
"""

from __future__ import annotations

import inspect
import sys
import threading
import warnings
import weakref
from collections.abc import Callable, Sequence
from contextvars import ContextVar
from functools import lru_cache
from typing import Annotated, Any, get_type_hints

import httpx
from pydantic import BeforeValidator

from courtside_data.client._pipelines.legacy import validate_rows_legacy
from courtside_data.client._pipelines.pydantic import validate_rows_pydantic
from courtside_data.data import OutputType, OutputWriteOption, Team
from courtside_data.debug import DebugTrace, debug_trace_context
from courtside_data.debug.sink import debug_log_path, prepare_log_dir
from courtside_data.endpoints import ENDPOINTS
from courtside_data.http_service import HTTPService
from courtside_data.output.fields import BasketballReferenceJSONEncoder, format_value
from courtside_data.output.service import OutputService
from courtside_data.output.writers import CSVWriter, FileOptions, JSONWriter, OutputOptions
from courtside_data.parsing.custom import CustomEndpointHandler, dispatch_custom_endpoint
from courtside_data.parsing.generic import GenericEndpointHandler
from courtside_data.schemas._fields import _team_field

_shared_service_lock = threading.Lock()
_shared_service: HTTPService | None = None
# Set by CourtsideClient for the duration of a method call so nested helpers
# use the client's own session instead of the shared one.
_service_override: ContextVar[HTTPService | None] = ContextVar("courtside_data_service_override", default=None)


def _default_service() -> HTTPService:
    """Return the process-wide shared service, creating it on first use."""
    global _shared_service
    with _shared_service_lock:
        if _shared_service is None:
            _shared_service = HTTPService()
        return _shared_service


def _resolve_service() -> HTTPService:
    override = _service_override.get()
    return override if override is not None else _default_service()


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


def _make_output_service() -> OutputService:
    return OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
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
    if row_model is not None:
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
    else:
        data, csv_column_names = validate_rows_legacy(
            values,
            csv_column_names=csv_column_names,
            output_type=output_type,
            validate_output=validate_output,
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


# Annotate ``Team`` parameters so Pydantic coerces raw abbreviations
# (``"ATL"``) into the :class:`Team` enum before dispatch. Pydantic's default
# enum coercion matches ``.value`` (``"ATLANTA HAWKS"``), not the abbreviation
# the registry probe passes, so the runtime validator reuses the abbreviation
# table from the schemas package.
_TeamParam = Annotated[Team, BeforeValidator(_team_field)]


@lru_cache(maxsize=128)
def _params_hints(endpoint_name: str) -> dict[str, Any] | None:
    """Return the cached ``{param_name: annotation}`` for one custom endpoint.

    Returns ``None`` for generic (non-custom) endpoints so the dispatch path
    stays free of Pydantic overhead. Per-endpoint hints are computed once
    and reused for every call; the ``@lru_cache`` decorator keeps the
    ``inspect``/``get_type_hints`` work off the hot path.
    """
    endpoint = ENDPOINTS[endpoint_name]
    if not endpoint.custom:
        return None
    method = getattr(CustomEndpointHandler, endpoint_name, None)
    if method is None:
        return None
    try:
        sig = inspect.signature(method)
        hints = get_type_hints(method, include_extras=True)
    except (TypeError, ValueError, NameError):
        # Some methods may have unresolvable forward references; skip coercion
        # rather than break the dispatch path.
        return None
    fields: dict[str, Any] = {}
    for pname, param in sig.parameters.items():
        if pname == "self":
            continue
        ann = hints.get(pname, param.annotation)
        if ann is inspect.Parameter.empty:
            continue
        fields[pname] = ann
    return fields or None


def _coerce_params(endpoint_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Coerce raw string params into typed values for custom endpoint methods.

    The probe path passes raw abbreviations (``"ATL"``) to the runner; the
    typed client path passes :class:`Team` enums. This helper unifies both
    paths by walking the cached method annotations and running ``_team_field``
    on any param whose annotation is :class:`Team` and whose value is a raw
    string. Other params are passed through untouched (the dispatch path
    already handles ``int``/``str`` idempotently). A fresh dict is returned
    so the caller's dict is never mutated.
    """
    hints = _params_hints(endpoint_name)
    if hints is None:
        return params
    coerced: dict[str, Any] = {}
    for key, value in params.items():
        if hints.get(key) is Team and isinstance(value, str):
            try:
                coerced[key] = _team_field(value)
            except ValueError as exc:
                raise ValueError(f"Invalid param {key!r} for endpoint {endpoint_name!r}: {exc}") from exc
        else:
            coerced[key] = value
    return coerced


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
