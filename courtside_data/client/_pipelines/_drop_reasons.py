"""Row drop and validation-failure reason classification for the pydantic pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

DROP_REASON_BLANK_ROW = "blank_row"
DROP_REASON_REPEATED_HEADER = "repeated_header"
DROP_REASON_PARSER_EXCLUDED = "parser_excluded"
DROP_REASON_MISSING_REQUIRED_FIELD = "missing_required_field"
DROP_REASON_INVALID_VALUE = "invalid_value"
DROP_REASON_SCHEMA_VALIDATION_ERROR = "schema_validation_error"
DROP_REASON_UNKNOWN = "unknown"

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

_INVALID_VALUE_ERROR_TYPES = frozenset(
    {
        "bool_parsing",
        "date_parsing",
        "datetime_parsing",
        "decimal_parsing",
        "enum",
        "float_parsing",
        "int_parsing",
        "string_type",
        "time_parsing",
        "type_error",
        "url_parsing",
        "uuid_parsing",
    }
)


def normalized_cell_value(value: Any) -> str:
    return " ".join(str(value).strip().lower().replace("\xa0", " ").split())


def row_drop_reason(row: dict[str, Any]) -> str | None:
    values = {normalized_cell_value(value) for value in row.values() if value not in (None, "")}
    if not values:
        return DROP_REASON_BLANK_ROW
    if any(any(marker in value for marker in _SENTINEL_ROW_VALUES) for value in values):
        return DROP_REASON_PARSER_EXCLUDED
    if bool(values) and all(normalized_cell_value(key) in values for key in row):
        return DROP_REASON_REPEATED_HEADER
    if bool(values) and all(value in _HEADER_ROW_VALUES for value in values):
        return DROP_REASON_REPEATED_HEADER
    return None


def validation_error_drop_reason(errors: Sequence[Mapping[str, Any]]) -> str:
    """Map pydantic validation errors to a coarse drop-reason category."""
    error_types = {str(error.get("type", "")) for error in errors}
    if "missing" in error_types:
        return DROP_REASON_MISSING_REQUIRED_FIELD
    if any(
        error_type in _INVALID_VALUE_ERROR_TYPES or error_type.startswith(("value_error", "type_error"))
        for error_type in error_types
    ):
        return DROP_REASON_INVALID_VALUE
    return DROP_REASON_SCHEMA_VALIDATION_ERROR


def sentinel_marker(row: Mapping[str, Any]) -> str | None:
    """Return the matched sentinel marker when present in ``row`` values."""
    for value in row.values():
        if value in (None, ""):
            continue
        normalized = normalized_cell_value(value)
        for marker in _SENTINEL_ROW_VALUES:
            if marker in normalized:
                return marker
    return None


def sentinel_row_diagnostics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize sentinel-like rows retained in validated output."""
    sentinel_types: dict[str, int] = {}
    for row in rows:
        marker = sentinel_marker(row)
        if marker is None:
            continue
        sentinel_types[marker] = sentinel_types.get(marker, 0) + 1
    return {
        "sentinel_row_count": sum(sentinel_types.values()),
        "sentinel_row_types": sentinel_types,
    }
