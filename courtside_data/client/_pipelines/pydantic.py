"""Pydantic row-model validation pipeline.

Used by :func:`courtside_data.client._runner._execute` when the endpoint
declares a ``row_model``. Wraps each raw row through the Pydantic adapter,
drops BREF sentinel/header rows, and surfaces :class:`SchemaDriftError`
when no row in a non-empty table validates.

Output formatting is the runner's responsibility: this module returns
``(data, csv_column_names)`` and never touches the output service.
"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from pydantic import ValidationError

from courtside_data.data import OutputType
from courtside_data.debug import DebugTrace
from courtside_data.errors import SchemaDriftError
from courtside_data.schemas import ROW_ADAPTERS

if TYPE_CHECKING:
    from pydantic_core import InitErrorDetails

_SENTINEL_ROW_VALUES = {
    "did not dress",
    "did not play",
    "inactive",
    "not with team",
    "player suspended",
    "suspended",
    "traded",
    "forfeited",
}


_HEADER_ROW_VALUES = {
    "2p",
    "2p%",
    "2pa",
    "3p",
    "3p%",
    "3pa",
    "age",
    "ast",
    "blk",
    "date",
    "drb",
    "efg%",
    "fg",
    "fg%",
    "fga",
    "ft",
    "ft%",
    "fta",
    "g",
    "gs",
    "lg",
    "mp",
    "opp",
    "orb",
    "pf",
    "player",
    "pos",
    "pts",
    "rk",
    "season",
    "stl",
    "team",
    "tov",
    "trb",
    "w/l",
}


def _normalized_cell_value(value: Any) -> str:
    return " ".join(str(value).strip().lower().replace("\xa0", " ").split())


def _is_skippable_bref_row(row: dict[str, Any]) -> bool:
    values = {_normalized_cell_value(value) for value in row.values() if value not in (None, "")}
    if any(any(marker in value for marker in _SENTINEL_ROW_VALUES) for value in values):
        return True
    # Some BREF tables repeat header rows or section rows that survive table
    # extraction because they use data-stat attributes like normal cells.
    if bool(values) and all(_normalized_cell_value(key) in values for key in row):
        return True
    return bool(values) and all(value in _HEADER_ROW_VALUES for value in values)


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


def _validate_row_model_rows(row_model: Any, raw_rows: list[dict[str, Any]]) -> list[Any]:
    """Validate rows one at a time, dropping invalid BREF sentinel/header rows.

    Basketball-Reference can interleave non-data rows with otherwise valid
    table rows. Keep the validated rows instead of failing the whole table, but
    still surface schema drift when no row in a non-empty table validates.
    """
    values: list[Any] = []
    drift_errors: list[dict[str, Any]] = []
    for index, row in enumerate(raw_rows):
        try:
            values.append(row_model.model_validate(row))
        except ValidationError as exc:
            if _is_skippable_bref_row(row):
                continue
            for error in exc.errors():
                enriched = dict(error)
                enriched["row_index"] = index
                drift_errors.append(enriched)
    if drift_errors and not values:
        raise ValidationError.from_exception_data(row_model.__name__, cast("list[InitErrorDetails]", drift_errors))
    return values


def _endpoint_url_context(endpoint: Any, params: dict[str, Any] | None) -> str:
    if endpoint is None:
        return "<unknown>"
    path = getattr(endpoint, "path", "<unknown>")
    if params:
        with contextlib.suppress(IndexError, KeyError, TypeError, ValueError):
            path = path.format(**params)
    if isinstance(path, str) and path.startswith("/"):
        return f"https://www.basketball-reference.com{path}"
    return str(path)


def validate_rows_pydantic(
    values: Any,
    *,
    row_model: Any,
    endpoint: Any,
    endpoint_name: str | None,
    endpoint_params: dict[str, Any] | None,
    csv_column_names: Sequence[str] | None,
    output_type: OutputType | None,
    raw: bool,
    trace: DebugTrace | None,
) -> tuple[Any, Sequence[str] | None]:
    """Validate ``values`` against ``row_model`` and return ``(data, csv_column_names)``.

    When ``raw=True``, the data is the unvalidated rows and the caller is
    responsible for the output envelope. When ``raw=False``, the data is
    the list of validated Pydantic instances, and ``SchemaDriftError`` is
    raised if no row in a non-empty table validates.
    """
    raw_rows = _extract_raw_rows(values)
    if trace is not None:
        trace.record(
            "runner",
            "row_model_pipeline_start",
            row_model=row_model.__name__,
            raw_row_count=len(raw_rows),
            raw_requested=raw,
        )
        trace.observe_rows("raw_rows", raw_rows, expected_columns=csv_column_names)
    if raw:
        return raw_rows, csv_column_names

    if ROW_ADAPTERS.get(endpoint_name) is None:
        raise RuntimeError(
            f"Endpoint {endpoint_name!r} declares row_model {row_model.__name__!r} but no adapter is registered."
        )
    try:
        if trace is not None:
            with trace.span("pydantic_validation", stage="validation", row_model=row_model.__name__):
                validated = _validate_row_model_rows(row_model, raw_rows)
        else:
            validated = _validate_row_model_rows(row_model, raw_rows)
        if trace is not None:
            trace.record(
                "validation",
                "pydantic_validation_complete",
                adapter_registered=True,
                row_model=row_model.__name__,
                row_count=len(validated),
            )
    except ValidationError as exc:
        if trace is not None:
            trace.record(
                "validation",
                "pydantic_validation_failed",
                row_model=row_model.__name__,
                errors=exc.errors(),
            )
            trace.record_exception(exc, stage="validation")
        raise SchemaDriftError(
            endpoint_name=endpoint_name or "<unknown>",
            url=_endpoint_url_context(endpoint, endpoint_params),
            pydantic_errors=cast("list[dict[str, Any]]", exc.errors()),
        ) from exc

    if output_type in (OutputType.CSV, OutputType.DATAFRAME):
        csv_column_names = tuple(row_model.model_fields)
    if trace is not None:
        trace.artifact("validated_rows", validated)
        trace.observe_rows("validated_rows", validated, expected_columns=tuple(row_model.model_fields))

    return validated, csv_column_names
