"""Bounded row/value previews and output-shape inference for probe reports.

Produces deterministic, size-limited previews of result rows so the report JSON
stays small, plus helpers that describe the shape of an endpoint's output.
"""

from __future__ import annotations

from typing import Any

_PREVIEW_MAX_KEYS = 8
_PREVIEW_MAX_STR_LEN = 80
_PREVIEW_MAX_NESTED_DEPTH = 2


def _row_count(data: Any) -> int | None:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            return len(data["data"])
        return len(data)
    return None


def _truncate_preview_value(value: Any, *, depth: int = 0) -> tuple[Any, bool]:
    """Return a bounded preview fragment and whether truncation occurred."""
    truncated = False
    if isinstance(value, str):
        if len(value) > _PREVIEW_MAX_STR_LEN:
            return f"{value[:_PREVIEW_MAX_STR_LEN]}...", True
        return value, False
    if depth >= _PREVIEW_MAX_NESTED_DEPTH:
        if isinstance(value, (dict, list, tuple)):
            return "...", True
        return value, False
    if isinstance(value, dict):
        preview: dict[str, Any] = {}
        for index, (key, nested) in enumerate(sorted(value.items())):
            if index >= _PREVIEW_MAX_KEYS:
                truncated = True
                break
            nested_preview, nested_truncated = _truncate_preview_value(nested, depth=depth + 1)
            preview[str(key)] = nested_preview
            truncated = truncated or nested_truncated
        return preview, truncated
    if isinstance(value, list):
        items: list[Any] = []
        for index, item in enumerate(value):
            if index >= _PREVIEW_MAX_KEYS:
                truncated = True
                break
            nested_preview, nested_truncated = _truncate_preview_value(item, depth=depth + 1)
            items.append(nested_preview)
            truncated = truncated or nested_truncated
        return items, truncated
    return value, False


def _preview_result(row: Any) -> tuple[Any, bool, int | None, int | None]:
    """Build a deterministic first-row preview with truncation metadata."""
    if not isinstance(row, dict):
        return row, False, None, None
    total_field_count = len(row)
    preview: dict[str, Any] = {}
    truncated = total_field_count > _PREVIEW_MAX_KEYS
    for index, (key, value) in enumerate(sorted(row.items())):
        if index >= _PREVIEW_MAX_KEYS:
            break
        preview_value, value_truncated = _truncate_preview_value(value)
        preview[str(key)] = preview_value
        truncated = truncated or value_truncated
    return preview, truncated, len(preview), total_field_count


def _field_names_from_row(row: Any) -> list[str]:
    if isinstance(row, dict):
        return sorted(row)
    if hasattr(row, "model_dump"):
        dumped = row.model_dump()
        if isinstance(dumped, dict):
            return sorted(dumped)
    return []


def _infer_output_type(data: Any, model_name: str | None) -> str | None:
    if data is None:
        return None
    if isinstance(data, list):
        return f"list[{model_name}]" if model_name else "list"
    if isinstance(data, dict):
        return "dict"
    return type(data).__name__
