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

import threading
from collections.abc import Callable, Sequence
from contextvars import ContextVar
from typing import Any, cast

import httpx
from pydantic import ValidationError

from courtside_data.data import OutputType, OutputWriteOption
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import SchemaDriftError
from courtside_data.http_service import HTTPService
from courtside_data.output.field_types import coerce_data
from courtside_data.output.fields import BasketballReferenceJSONEncoder, format_value
from courtside_data.output.service import OutputService
from courtside_data.output.type_validator import validate_rows
from courtside_data.output.writers import CSVWriter, FileOptions, JSONWriter, OutputOptions
from courtside_data.schemas import ROW_ADAPTERS

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


def _extract_rows(values: Any) -> list[dict[str, Any]] | None:
    """Pull the row list out of endpoint output (list[dict] or dict[str, list[dict]])."""
    if isinstance(values, list) and values and isinstance(values[0], dict):
        return values
    if isinstance(values, dict):
        for v in values.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return None


def _extract_raw_rows(values: Any) -> list[dict[str, Any]]:
    """Pull raw rows out of row-model endpoint output, preserving empty results."""
    if isinstance(values, list):
        if all(isinstance(row, dict) for row in values):
            return values
        return []
    if isinstance(values, dict):
        for v in values.values():
            if isinstance(v, list) and all(isinstance(row, dict) for row in v):
                return v
    return []


def _detect_csv_columns(rows: list[dict[str, Any]]) -> Sequence[str]:
    """Auto-detect CSV column names from row keys, stripping all-empty columns.

    Only used when an endpoint doesn't declare explicit column names; declared
    columns keep their contract even when empty.
    """
    column_names = list(rows[0].keys())
    non_empty = [k for k in column_names if any(row.get(k) not in (None, "", set(), []) for row in rows)]
    return non_empty or column_names


def _endpoint_url_context(endpoint: Any, params: dict[str, Any] | None) -> str:
    if endpoint is None:
        return "<unknown>"
    path = getattr(endpoint, "path", "<unknown>")
    if params:
        try:
            path = path.format(**params)
        except (IndexError, KeyError, TypeError, ValueError):
            pass
    if isinstance(path, str) and path.startswith("/"):
        return f"https://www.basketball-reference.com{path}"
    return str(path)


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
) -> Any:
    values = _call_with_error_mapping(service_call, error_mappings)

    # Row-model endpoints validate the raw Basketball-Reference rows directly.
    # That intentionally bypasses the legacy coerce_data/validate_rows path.
    row_model = getattr(endpoint, "row_model", None)
    if row_model is not None:
        raw_rows = _extract_raw_rows(values)
        if raw:
            return raw_rows

        adapter = ROW_ADAPTERS.get(endpoint_name)
        if adapter is None:
            raise RuntimeError(
                f"Endpoint {endpoint_name!r} declares row_model {row_model.__name__!r} but no adapter is registered."
            )
        try:
            values = adapter.validate_python(raw_rows)
        except ValidationError as exc:
            raise SchemaDriftError(
                endpoint_name=endpoint_name or "<unknown>",
                url=_endpoint_url_context(endpoint, endpoint_params),
                # exc.errors() yields Pydantic ErrorDetails TypedDicts;
                # SchemaDriftError is typed list[dict] (plan-mandated signature),
                # and the values are dicts at runtime, so cast the type.
                pydantic_errors=cast("list[dict[str, Any]]", exc.errors()),
            ) from exc

        if output_type in (OutputType.CSV, OutputType.DATAFRAME):
            csv_column_names = tuple(row_model.model_fields)

        options = OutputOptions.of(
            file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
            output_type=output_type,
            json_options=json_options,
            csv_options={"column_names": csv_column_names},
        )
        output_service = OutputService(
            json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
            csv_writer=CSVWriter(value_formatter=format_value),
        )
        return output_service.output(data=values, options=options)

    # Coerce raw string values to proper Python types (idempotent for endpoints
    # whose parser chains already produce typed values)
    values = coerce_data(values)

    if output_type in (OutputType.CSV, OutputType.DATAFRAME) and csv_column_names is None:
        rows = _extract_rows(values)
        if rows is not None:
            csv_column_names = _detect_csv_columns(rows)

    if validate_output and isinstance(values, list) and values and isinstance(values[0], dict):
        report = validate_rows(values, expected_columns=csv_column_names)
        if not report.ok:
            raise ValueError(str(report))

    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": csv_column_names},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def _run_endpoint(
    name: str,
    params: dict[str, Any],
    *,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Execute the registry-described endpoint ``name`` with bound call params.

    The :data:`ENDPOINTS` entry supplies the metadata (service dispatch, CSV
    columns, error mapping); the caller supplies an explicit, typed signature.
    """
    endpoint = ENDPOINTS[name]

    def service_call() -> Any:
        service = _resolve_service()
        if endpoint.custom:
            return getattr(service, name)(**params)
        return service.fetch_table(endpoint, **params)

    return _execute(
        service_call=service_call,
        csv_column_names=endpoint.csv_columns,
        error_mappings=endpoint.error_mappings(params),
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        endpoint=endpoint,
        endpoint_name=name,
        endpoint_params=params,
        raw=raw,
    )
