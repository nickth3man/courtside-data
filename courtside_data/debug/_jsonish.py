"""JSON-safe value conversion, artifact sampling, and row diagnostics."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

import orjson

from courtside_data.debug._runtime import _should_redact
from courtside_data.debug.config import DebugConfig

# ---------------------------------------------------------------------------
# Public helpers (used by multiple mixins and by external modules)
# ---------------------------------------------------------------------------


def _jsonish(value: Any, *, config: DebugConfig, key: str | None = None, depth: int = 0) -> Any:
    """Recursively convert *value* to a JSON-safe structure.

    Handles Pydantic models, dataclasses, mappings, collections, enums,
    dates, non-finite floats, bytes, and strings exceeding
    ``config.max_string_length``.  Deeply-nested structures are truncated
    at ``config.max_depth``.
    """
    if key is not None and _should_redact(key, config.redact_keys):
        return "<redacted>"
    if config.max_depth is not None and depth >= config.max_depth:
        return "<max-depth-exceeded>"
    if hasattr(value, "model_dump"):
        return _jsonish(value.model_dump(mode="json"), config=config, depth=depth + 1)
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonish(asdict(value), config=config, depth=depth + 1)
    if isinstance(value, Mapping):
        return {
            str(item_key): _jsonish(item_value, config=config, key=str(item_key), depth=depth + 1)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [_jsonish(item, config=config, depth=depth + 1) for item in value]
    if isinstance(value, tuple):
        return [_jsonish(item, config=config, depth=depth + 1) for item in value]
    if isinstance(value, set):
        return sorted(_jsonish(item, config=config, depth=depth + 1) for item in value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, str) and config.max_string_length is not None and len(value) > config.max_string_length:
        return f"{value[: config.max_string_length]}...<truncated {len(value) - config.max_string_length} chars>"
    if isinstance(value, bytes):
        return f"<bytes len={len(value)} sha256={hashlib.sha256(value).hexdigest()}>"
    try:
        orjson.dumps(value)
    except (TypeError, orjson.JSONEncodeError):
        return repr(value)
    return value


def _is_empty(value: Any) -> bool:
    """Return ``True`` for ``None``, empty string, or empty collection."""
    return value in (None, "", [], {}, set())


def _count_items(value: Any) -> int | None:
    """Return ``len(value)`` for collection types, ``None`` for scalars."""
    if isinstance(value, list | tuple | set | dict):
        return len(value)
    return None


# ---------------------------------------------------------------------------
# Artifact sampling
# ---------------------------------------------------------------------------


def _sample_artifact(value: Any, config: DebugConfig) -> tuple[Any, bool, int | None]:
    """Apply size-bounds to *value* per *config*.

    Returns ``(sampled, truncated, original_count)``.
    """
    max_items = config.max_artifact_items
    if max_items is None:
        return value, False, _count_items(value)
    if isinstance(value, list) and len(value) > max_items:
        if config.artifact_sample == "tail":
            return value[-max_items:], True, len(value)
        if config.artifact_sample == "head_tail" and max_items > 2:
            head_count = max_items // 2
            tail_count = max_items - head_count - 1
            sampled = [
                *value[:head_count],
                {"__debug_truncation__": len(value) - max_items},
                *value[-tail_count:],
            ]
            return sampled, True, len(value)
        return value[:max_items], True, len(value)
    if isinstance(value, dict) and len(value) > max_items:
        items = list(value.items())
        if config.artifact_sample == "tail":
            sampled_items = items[-max_items:]
        elif config.artifact_sample == "head_tail" and max_items > 2:
            head_count = max_items // 2
            tail_count = max_items - head_count - 1
            sampled_items = [
                *items[:head_count],
                ("__debug_truncation__", len(items) - max_items),
                *items[-tail_count:],
            ]
        else:
            sampled_items = items[:max_items]
        return dict(sampled_items), True, len(value)
    return value, False, _count_items(value)


# ---------------------------------------------------------------------------
# Artifact metadata
# ---------------------------------------------------------------------------


def _artifact_metadata(
    value: Any,
    *,
    original_count: int | None,
    truncated: bool,
    stored: bool,
) -> dict[str, Any]:
    """Build an artifact-index entry for *value*."""
    encoded = orjson.dumps(value, option=orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS, default=str)
    metadata: dict[str, Any] = {
        "type": type(value).__name__,
        "stored": stored,
        "truncated": truncated,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "stored_count": _count_items(value),
        "original_count": original_count,
        "byte_length": len(encoded),
    }
    if isinstance(value, list) and value and isinstance(value[0], dict):
        metadata["row_keys"] = sorted(value[0])
    if isinstance(value, dict):
        metadata["keys"] = sorted(value)
    return metadata


def _prepare_artifact(value: Any, config: DebugConfig) -> tuple[Any, dict[str, Any]]:
    """JSON-ify *value*, sample it, and return ``(stored_value, metadata)``."""
    item_count = _count_items(value)
    if config.detail_level == "summary" and isinstance(value, (list, dict)) and item_count and item_count > 5:
        json_value = {"__truncated__": {"original_count": item_count, "reason": "detail_level_summary"}}
        metadata = _artifact_metadata(json_value, original_count=item_count, truncated=True, stored=True)
        return json_value, metadata

    json_value = _jsonish(value, config=config)
    max_rows = config.max_row_sample if config.max_row_sample is not None else config.max_artifact_items
    if max_rows is not None and isinstance(json_value, list) and len(json_value) > max_rows:
        sampled, truncated, original_count = _sample_artifact(json_value, config)
    else:
        sampled, truncated, original_count = _sample_artifact(json_value, config)

    if config.max_artifact_bytes is not None:
        encoded = orjson.dumps(sampled, option=orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS, default=str)
        if len(encoded) > config.max_artifact_bytes:
            sampled = {
                "__truncated__": {
                    "original_count": original_count,
                    "stored_count": _count_items(sampled),
                    "byte_length": len(encoded),
                    "max_artifact_bytes": config.max_artifact_bytes,
                    "reason": "artifact_byte_cap",
                }
            }
            truncated = True

    metadata = _artifact_metadata(sampled, original_count=original_count, truncated=truncated, stored=True)
    return sampled, metadata


def _index_artifact(
    artifact_index: dict[str, Any],
    name: str,
    value: Any,
    *,
    stored: bool,
    truncated: bool,
) -> None:
    """Write an artifact-index entry for an unstored or skipped artifact."""
    artifact_index[name] = _artifact_metadata(
        value,
        original_count=_count_items(value),
        truncated=truncated,
        stored=stored,
    )


# ---------------------------------------------------------------------------
# Row helpers
# ---------------------------------------------------------------------------


def _rows_as_dicts(rows: Any) -> list[dict[str, Any]]:
    """Normalise *rows* to ``list[dict]`` (supports Pydantic models)."""
    if isinstance(rows, list):
        values = rows
    elif isinstance(rows, dict):
        values = next((value for value in rows.values() if isinstance(value, list)), [])
    else:
        return []
    result: list[dict[str, Any]] = []
    for row in values:
        if hasattr(row, "model_dump"):
            result.append(row.model_dump(mode="json"))
        elif isinstance(row, Mapping):
            result.append(dict(row))
    return result


def _row_diagnostics(
    rows: list[dict[str, Any]],
    *,
    expected_columns: tuple[str, ...] | None,
    max_examples: int,
) -> dict[str, Any]:
    """Build a column-level diagnostic report for *rows*."""
    columns = sorted({key for row in rows for key in row})
    expected = list(expected_columns or [])
    missing_expected = [column for column in expected if column not in columns]
    extra = [column for column in columns if expected_columns is not None and column not in expected_columns]
    by_column: dict[str, Any] = {}
    for column in columns:
        present_count = 0
        empty_count = 0
        type_counts: dict[str, int] = {}
        examples: list[Any] = []
        for row in rows:
            if column not in row:
                continue
            present_count += 1
            value = row.get(column)
            if _is_empty(value):
                empty_count += 1
            type_name = type(value).__name__
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            if len(examples) < max_examples and not _is_empty(value):
                examples.append(value)
        by_column[column] = {
            "present_count": present_count,
            "missing_count": len(rows) - present_count,
            "empty_count": empty_count,
            "type_counts": type_counts,
            "examples": examples,
        }
    return {
        "row_count": len(rows),
        "columns": columns,
        "expected_columns": expected,
        "missing_expected_columns": missing_expected,
        "extra_columns": extra,
        "by_column": by_column,
    }
