"""Type validation for basketball-reference scraper output.

Validates that scraped data rows have the expected Python types after coercion.
Handles columns that can be None (e.g., empty cells for age, combined-totals rows).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from courtside_data.output.field_types import get_coercion

_CLOCK_RE = re.compile(r"^\d+:\d{2}$")

# ─── Expected type extraction ─────────────────────────────────────────


def _get_target_type(column_name: str) -> type | tuple[type, ...] | None:
    """Infer the expected Python type for a column from its coercion function.

    We use a naming convention: functions named coerce_<type> target <type>.
    The coercion function's __name__ tells us what it produces.
    """
    fn = get_coercion(column_name)
    name = getattr(fn, "__name__", "")

    # coerce_int, coerce_float, coerce_int_or_none, coerce_float_or_none
    if name in {"coerce_int", "coerce_int_or_clock"}:
        return int
    if name == "coerce_float":
        return (int, float)  # int is acceptable for float columns
    if name == "coerce_int_or_none":
        return (int, type(None))
    if name == "coerce_float_or_none":
        return (int, float, type(None))
    # lambda v: v or other pass-through — no type expectation (legacy
    # endpoints may return typed values like Team enums)
    return None


# ─── Validation ────────────────────────────────────────────────────────


class ValidationError:
    """A single type-mismatch issue."""

    def __init__(self, row_index: int, column: str, expected: str, actual: str, value: Any):
        self.row_index = row_index
        self.column = column
        self.expected = expected
        self.actual = actual
        self.value = value

    def __str__(self) -> str:
        return f"row[{self.row_index}].{self.column}: expected {self.expected}, got {self.actual} ({self.value!r})"


class ValidationReport:
    """Report from a validation run."""

    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        self.error_count = len(errors)

    @property
    def is_ok(self) -> bool:
        return self.error_count == 0

    def summary(self) -> str:
        if self.is_ok:
            return "Validation passed — no type mismatches."
        return f"Validation found {self.error_count} type error(s)."

    def __str__(self) -> str:
        lines = [self.summary()]
        for error in self.errors:
            lines.append(f"  {error}")
        return "\n".join(lines)


def validate_rows(
    rows: Sequence[dict[str, Any]],
    expected_columns: Sequence[str] | None = None,
    strict: bool = False,
) -> ValidationReport:
    """Validate that all rows have expected types for their columns.

    Args:
        rows: List of row dicts (should be coerced already).
        expected_columns: If provided, only validate these columns.
        strict: If True, raise ValueError on first error (for fail-fast).

    Returns:
        ValidationReport with any type mismatches found.
    """
    errors: list[ValidationError] = []

    for i, row in enumerate(rows):
        columns_to_check = expected_columns or list(row.keys())
        for column in columns_to_check:
            value = row.get(column)
            target_type = _get_target_type(column)

            if target_type is None:
                continue  # no type expectation

            # None is acceptable for any nullable target type
            if value is None:
                if type(None) in (target_type if isinstance(target_type, tuple) else (target_type,)):
                    continue
                # For strict int/float, None is also acceptable (empty cells)
                if target_type in (int, float, (int, float)):
                    continue

            if not isinstance(value, target_type):
                if column == "mp" and isinstance(value, str) and _CLOCK_RE.fullmatch(value.strip()):
                    continue
                expected_name = _type_name(target_type)
                actual_name = type(value).__name__
                error = ValidationError(i, column, expected_name, actual_name, value)
                if strict:
                    raise ValueError(str(error))
                errors.append(error)

    return ValidationReport(errors)


def _type_name(t: type | tuple[type, ...]) -> str:
    """Human-readable type name."""
    if isinstance(t, tuple):
        return " | ".join(ty.__name__ for ty in t)
    return t.__name__
