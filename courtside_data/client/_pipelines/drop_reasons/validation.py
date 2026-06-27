"""Validation error drop reason classification."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from courtside_data.client._pipelines.drop_reasons.constants import (
    _AGGREGATE_TEAM_ABBREVIATIONS,
    _DATE_FIELD_NAMES,  # noqa: F401
    _INVALID_VALUE_ERROR_TYPES,
    _PLAYER_FIELD_NAMES,
    _TEAM_FIELD_NAMES,
    DROP_REASON_HISTORICAL_TEAM_NAME,
    DROP_REASON_INVALID_DATE,
    DROP_REASON_INVALID_PLAYER_VALUE,
    DROP_REASON_INVALID_TEAM_VALUE,
    DROP_REASON_INVALID_VALUE,
    DROP_REASON_MISSING_REQUIRED_FIELD,
    DROP_REASON_SCHEMA_VALIDATION_ERROR,
)
from courtside_data.domain import TEAM_NAME_TO_TEAM


def _error_field_names(errors: Sequence[Mapping[str, Any]]) -> set[str]:
    names: set[str] = set()
    for error in errors:
        location = error.get("loc")
        if isinstance(location, (list, tuple)):
            for part in location:
                names.add(str(part))
        elif location is not None:
            names.add(str(location))
    return names


def validation_error_drop_reason(
    errors: Sequence[Mapping[str, Any]],
    *,
    row: Mapping[str, Any] | None = None,
) -> str:
    """Map pydantic validation errors to a precise drop-reason category."""
    error_types = {str(error.get("type", "")) for error in errors}
    field_names = _error_field_names(errors)

    if "missing" in error_types:
        if field_names & _PLAYER_FIELD_NAMES:
            return DROP_REASON_INVALID_PLAYER_VALUE
        return DROP_REASON_MISSING_REQUIRED_FIELD

    if any(error_type in {"date_parsing", "datetime_parsing", "time_parsing"} for error_type in error_types):
        return DROP_REASON_INVALID_DATE

    if field_names & _TEAM_FIELD_NAMES and (
        "enum" in error_types or any(error_type.startswith("value_error") for error_type in error_types)
    ):
        if row is not None:
            for name in _TEAM_FIELD_NAMES:
                raw = row.get(name)
                if raw in (None, ""):
                    continue
                normalized = str(raw).strip().upper()
                if (
                    normalized not in TEAM_NAME_TO_TEAM
                    and normalized not in _AGGREGATE_TEAM_ABBREVIATIONS
                    and any(
                        token in normalized
                        for token in ("BRAVES", "BULLETS", "KINGS", "HORNETS", "SUPERSONICS", "WARRIORS")
                    )
                ):
                    return DROP_REASON_HISTORICAL_TEAM_NAME
        return DROP_REASON_INVALID_TEAM_VALUE

    if field_names & _PLAYER_FIELD_NAMES and (
        "string_type" in error_types or any(error_type.startswith("value_error") for error_type in error_types)
    ):
        return DROP_REASON_INVALID_PLAYER_VALUE

    if any(
        error_type in _INVALID_VALUE_ERROR_TYPES or error_type.startswith(("value_error", "type_error"))
        for error_type in error_types
    ):
        return DROP_REASON_INVALID_VALUE

    return DROP_REASON_SCHEMA_VALIDATION_ERROR
