"""Row-level drop reason classification."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from courtside_data.client._pipelines.drop_reasons.constants import (
    _AGGREGATE_ROW_MARKERS,
    _AGGREGATE_TEAM_ABBREVIATIONS,
    _COMBINED_TEAM_SUFFIX,
    _HEADER_ROW_VALUES,
    _SENTINEL_ROW_VALUES,
    DROP_REASON_AGGREGATE_ROW,
    DROP_REASON_BLANK_ROW,
    DROP_REASON_COMBINED_TEAM,
    DROP_REASON_REPEATED_HEADER,
    DROP_REASON_UNSUPPORTED_SENTINEL_VALUE,
    EXPECTED_DROP_REASONS,
    UNRESOLVED_DROP_REASONS,
)
from courtside_data.client._pipelines.drop_reasons.helpers import (
    _field_text,
    normalized_cell_value,
)
from courtside_data.client._pipelines.drop_reasons.schedule import (
    _schedule_drop_reason,
)


def _row_values(row: Mapping[str, Any]) -> set[str]:
    return {normalized_cell_value(value) for value in row.values() if value not in (None, "")}


def _is_aggregate_row(row: Mapping[str, Any]) -> bool:
    team_abbr = _field_text(row, "team_name_abbr", "team_id", "team")
    if team_abbr is not None and team_abbr.upper() in _AGGREGATE_TEAM_ABBREVIATIONS:
        return True
    values = _row_values(row)
    if values & _AGGREGATE_ROW_MARKERS:
        return True
    name = normalized_cell_value(_field_text(row, "name_display", "player") or "")
    return name in _AGGREGATE_ROW_MARKERS


def _is_combined_team_row(row: Mapping[str, Any]) -> bool:
    team_abbr = _field_text(row, "team_name_abbr", "team_id")
    return team_abbr is not None and team_abbr.upper().endswith(_COMBINED_TEAM_SUFFIX)


def row_drop_reason(row: dict[str, Any]) -> str | None:
    """Return a parser-level drop reason when the row is clearly non-data."""
    values = _row_values(row)
    if not values:
        return DROP_REASON_BLANK_ROW

    schedule_reason = _schedule_drop_reason(row)
    if schedule_reason is not None:
        return schedule_reason

    if any(any(marker in value for marker in _SENTINEL_ROW_VALUES) for value in values):
        return DROP_REASON_UNSUPPORTED_SENTINEL_VALUE

    if _is_combined_team_row(row):
        return DROP_REASON_COMBINED_TEAM

    if _is_aggregate_row(row):
        return DROP_REASON_AGGREGATE_ROW

    if bool(values) and all(normalized_cell_value(key) in values for key in row):
        return DROP_REASON_REPEATED_HEADER
    if bool(values) and all(value in _HEADER_ROW_VALUES for value in values):
        return DROP_REASON_REPEATED_HEADER

    return None


def summarize_drop_counts(dropped_reasons: Mapping[str, int]) -> dict[str, Any]:
    """Split drop counts into expected vs unexpected buckets for probe reporting."""
    expected = 0
    unexpected = 0
    for reason, count in dropped_reasons.items():
        if reason in EXPECTED_DROP_REASONS:
            expected += count
        elif reason in UNRESOLVED_DROP_REASONS or reason not in EXPECTED_DROP_REASONS:
            unexpected += count
    total = expected + unexpected
    drop_rate = round(unexpected / total, 4) if total else 0.0
    return {
        "expected_drop_count": expected,
        "unexpected_drop_count": unexpected,
        "drop_rate": drop_rate,
    }
