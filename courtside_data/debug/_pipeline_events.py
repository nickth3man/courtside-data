"""Compact debug events emitted by the parse/validation pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from courtside_data.debug.trace import DebugTrace

__all__ = [
    "emit_parser_diagnostics",
    "record_custom_parser_parsed",
    "record_parsed_rows_summary",
    "record_rows_filtered",
    "record_sentinel_rows",
    "record_validation_failed",
    "record_validation_passed",
    "validation_error_paths",
]


def validation_error_paths(errors: Sequence[Mapping[str, Any]], *, limit: int = 25) -> list[str]:
    """Extract dotted field paths from pydantic error dicts."""
    paths: list[str] = []
    for error in errors:
        location = error.get("loc")
        if isinstance(location, (list, tuple)):
            paths.append(".".join(str(part) for part in location))
        elif location is not None:
            paths.append(str(location))
        if len(paths) >= limit:
            break
    return paths


def record_parsed_rows_summary(
    trace: DebugTrace,
    *,
    parser_name: str,
    rows: Sequence[Mapping[str, Any]],
) -> None:
    """Record post-parse row/field counts before validation."""
    parsed_fields = sorted(rows[0]) if rows else []
    trace.record(
        "parse",
        "parsed_rows_summary",
        parser_name=parser_name,
        parsed_row_count=len(rows),
        parsed_field_count=len(parsed_fields),
        parsed_fields=[str(name) for name in parsed_fields],
    )


def record_custom_parser_parsed(
    trace: DebugTrace,
    *,
    parser_name: str,
    source_sections: Sequence[str],
    parsed_row_count: int | None = None,
    parsed_event_count: int | None = None,
    ignored_event_count: int | None = None,
    ignored_event_reason_counts: Mapping[str, int] | None = None,
    ignored_row_reason_counts: Mapping[str, int] | None = None,
    custom_diagnostics: Mapping[str, Any] | None = None,
    period_count: int | None = None,
    score_event_count: int | None = None,
    substitution_event_count: int | None = None,
) -> None:
    """Record parser-specific diagnostics for non-table custom endpoints."""
    attributes: dict[str, Any] = {
        "parser_name": parser_name,
        "source_sections": [str(section) for section in source_sections],
    }
    if parsed_row_count is not None:
        attributes["parsed_row_count"] = parsed_row_count
    if parsed_event_count is not None:
        attributes["parsed_event_count"] = parsed_event_count
    if ignored_event_count is not None:
        attributes["ignored_event_count"] = ignored_event_count
    if ignored_event_reason_counts:
        attributes["ignored_event_reason_counts"] = dict(ignored_event_reason_counts)
    if ignored_row_reason_counts:
        attributes["ignored_row_reason_counts"] = dict(ignored_row_reason_counts)
    if custom_diagnostics:
        attributes["custom_diagnostics"] = dict(custom_diagnostics)
    if period_count is not None:
        attributes["period_count"] = period_count
    if score_event_count is not None:
        attributes["score_event_count"] = score_event_count
    if substitution_event_count is not None:
        attributes["substitution_event_count"] = substitution_event_count
    trace.record("parse", f"{parser_name}_parsed", **attributes)


def emit_parser_diagnostics(
    trace: DebugTrace,
    *,
    parser_name: str,
    rows: Sequence[Mapping[str, Any]],
    source_sections: Sequence[str],
    parsed_event_count: int | None = None,
    ignored_event_count: int | None = None,
    ignored_event_reason_counts: Mapping[str, int] | None = None,
    ignored_row_reason_counts: Mapping[str, int] | None = None,
    custom_diagnostics: Mapping[str, Any] | None = None,
    **extra_attributes: Any,
) -> None:
    """Record parsed-row summary plus parser-specific diagnostics in one call."""
    record_parsed_rows_summary(trace, parser_name=parser_name, rows=rows)
    record_custom_parser_parsed(
        trace,
        parser_name=parser_name,
        source_sections=source_sections,
        parsed_row_count=len(rows),
        parsed_event_count=parsed_event_count if parsed_event_count is not None else len(rows),
        ignored_event_count=ignored_event_count,
        ignored_event_reason_counts=ignored_event_reason_counts,
        ignored_row_reason_counts=ignored_row_reason_counts,
        custom_diagnostics=custom_diagnostics,
        **extra_attributes,
    )


def record_sentinel_rows(
    trace: DebugTrace,
    *,
    sentinel_row_count: int,
    sentinel_row_types: Mapping[str, int],
) -> None:
    """Record sentinel-like rows retained in validated output (diagnostics only)."""
    if sentinel_row_count <= 0:
        return
    trace.record(
        "validation",
        "sentinel_rows_observed",
        sentinel_row_count=sentinel_row_count,
        sentinel_row_types=dict(sentinel_row_types),
    )


def record_rows_filtered(
    trace: DebugTrace,
    *,
    dropped_row_reason_counts: Mapping[str, int],
) -> None:
    """Record aggregated row-drop reasons from validation/filtering."""
    if not dropped_row_reason_counts:
        return
    trace.record(
        "validation",
        "rows_filtered",
        dropped_row_count=sum(dropped_row_reason_counts.values()),
        dropped_row_reason_counts=dict(dropped_row_reason_counts),
    )


def record_validation_passed(
    trace: DebugTrace,
    *,
    row_model: str,
    validated_row_count: int,
) -> None:
    trace.record(
        "validation",
        "pydantic_validation_complete",
        validation_status="passed",
        row_model=row_model,
        validated_row_count=validated_row_count,
        row_count=validated_row_count,
        validation_error_count=0,
        validation_error_paths=[],
        adapter_registered=True,
    )


def record_validation_failed(
    trace: DebugTrace,
    *,
    row_model: str,
    errors: Sequence[Mapping[str, Any]],
) -> None:
    paths = validation_error_paths(errors)
    trace.record(
        "validation",
        "pydantic_validation_failed",
        validation_status="failed",
        row_model=row_model,
        validation_error_count=len(errors),
        validation_error_paths=paths,
        errors=list(errors),
    )
