"""Type coercion layer for basketball-reference scraper output.

Generic endpoints return all values as raw strings from HTML. This module
converts them to proper Python types (int, float) using a column-name registry
plus heuristic fallback rules.

Legacy endpoints already produce typed values, so coercion is idempotent for
them: values already matching the target type pass through unchanged.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from courtside_data.output import _coercions
from courtside_data.output._column_type_map import _COLUMN_TYPE_MAP, _infer_coercion

coerce_float = _coercions.coerce_float
coerce_float_or_none = _coercions.coerce_float_or_none
coerce_int = _coercions.coerce_int
coerce_int_or_clock = _coercions.coerce_int_or_clock
coerce_int_or_none = _coercions.coerce_int_or_none


def get_coercion(column_name: str) -> Callable[[Any], Any]:
    """Return the coercion function for a given column name.

    Checks the explicit registry first, then falls back to heuristic inference.
    """
    if column_name in _COLUMN_TYPE_MAP:
        return _COLUMN_TYPE_MAP[column_name]
    return _infer_coercion(column_name)


def coerce_row(row: dict[str, Any]) -> dict[str, Any]:
    """Apply type coercion to every value in a row dict."""
    return {key: get_coercion(key)(value) for key, value in row.items()}


def coerce_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply type coercion to a list of row dicts.

    Uses a per-call column-to-function cache so that ``get_coercion`` is
    invoked only once per unique column key across the whole batch.
    """
    cache: dict[str, Callable[[Any], Any]] = {}
    result: list[dict[str, Any]] = []
    for row in rows:
        coerced: dict[str, Any] = {}
        for key, value in row.items():
            fn = cache.get(key)
            if fn is None:
                fn = get_coercion(key)
                cache[key] = fn
            coerced[key] = fn(value)
        result.append(coerced)
    return result


def coerce_data(data: Any) -> Any:
    """Apply type coercion to endpoint output data.

    Handles both list[dict] and dict[str, list[dict]] shapes.
    """
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            return coerce_rows(data)
    elif isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                result[key] = coerce_rows(value)
            else:
                result[key] = value
        return result
    return data
