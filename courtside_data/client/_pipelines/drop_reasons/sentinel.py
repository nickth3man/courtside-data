"""Sentinel row detection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from courtside_data.client._pipelines.drop_reasons.constants import (
    _SENTINEL_ROW_VALUES,
)
from courtside_data.client._pipelines.drop_reasons.helpers import normalized_cell_value


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
