"""Data-quality evaluation helpers for the live endpoint probe."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from courtside_data.client._pipelines.drop_reasons import (
    DROP_REASON_HISTORICAL_TEAM_NAME,
    DROP_REASON_INVALID_VALUE,
    DROP_REASON_UNKNOWN,
    EXPECTED_DROP_REASONS,
    UNRESOLVED_DROP_REASONS,
    summarize_drop_counts,
)

DATA_QUALITY_CLEAN = "clean"
DATA_QUALITY_WARNINGS = "warnings"
DATA_QUALITY_LOSSY = "lossy"
DATA_QUALITY_FAILED = "failed"

DROP_RATE_WARNING_THRESHOLD = 0.10


def evaluate_data_quality(
    *,
    ok: bool,
    dropped_row_count: int | None,
    dropped_row_reason_counts: Mapping[str, int] | None,
    ignored_row_reason_counts: Mapping[str, int] | None = None,
    parser_ignored_row_reason_counts: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Compute probe-facing data-quality fields from row-drop diagnostics."""
    if not ok:
        return {
            "data_quality_status": DATA_QUALITY_FAILED,
            "data_quality_warnings_json": [],
            "drop_rate": None,
            "drop_rate_warning": False,
            "expected_drop_count": None,
            "unexpected_drop_count": None,
        }

    dropped_reasons = dict(dropped_row_reason_counts or {})
    ignored = dict(ignored_row_reason_counts or {})
    parser_ignored = dict(parser_ignored_row_reason_counts or {})

    # Parser-level ignored rows are expected and do not count as unexpected loss.
    for reason, _count in parser_ignored.items():
        if reason in EXPECTED_DROP_REASONS or reason.startswith("missing_"):
            continue

    drop_summary = summarize_drop_counts(dropped_reasons)
    expected = drop_summary["expected_drop_count"] + sum(
        count for reason, count in ignored.items() if reason in EXPECTED_DROP_REASONS or reason.startswith("missing_")
    )
    unexpected = drop_summary["unexpected_drop_count"]
    total_baseline = (dropped_row_count or 0) + (
        drop_summary["expected_drop_count"] + drop_summary["unexpected_drop_count"]
    )
    drop_rate = round(unexpected / total_baseline, 4) if total_baseline else 0.0

    warnings: list[str] = []
    if unexpected:
        unresolved = [reason for reason in dropped_reasons if reason in UNRESOLVED_DROP_REASONS]
        if unresolved:
            warnings.append(f"unresolved_drop_reasons={sorted(unresolved)}")
        if DROP_REASON_HISTORICAL_TEAM_NAME in dropped_reasons:
            warnings.append("historical_team_rows_still_dropped")
        if drop_rate >= DROP_RATE_WARNING_THRESHOLD:
            warnings.append(f"high_drop_rate={drop_rate}")

    if not dropped_row_count and not ignored and not parser_ignored:
        status = DATA_QUALITY_CLEAN
    elif unexpected or any(reason in UNRESOLVED_DROP_REASONS for reason in dropped_reasons):
        status = DATA_QUALITY_LOSSY if unexpected else DATA_QUALITY_WARNINGS
        if DROP_REASON_INVALID_VALUE in dropped_reasons or DROP_REASON_UNKNOWN in dropped_reasons:
            status = DATA_QUALITY_LOSSY
    elif dropped_reasons or ignored or parser_ignored:
        status = DATA_QUALITY_WARNINGS
    else:
        status = DATA_QUALITY_CLEAN

    return {
        "data_quality_status": status,
        "data_quality_warnings_json": warnings,
        "drop_rate": drop_rate if total_baseline else 0.0,
        "drop_rate_warning": drop_rate >= DROP_RATE_WARNING_THRESHOLD,
        "expected_drop_count": expected,
        "unexpected_drop_count": unexpected,
    }
