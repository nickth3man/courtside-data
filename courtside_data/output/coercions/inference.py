"""Heuristic coercion inference for columns not in the explicit registry."""

from __future__ import annotations

from collections.abc import Callable

from courtside_data.output._coercions import coerce_float, coerce_int, coerce_int_or_clock
from courtside_data.output.coercions.registry import _COUNT_STAT_PATTERNS


def _infer_coercion(column_name: str) -> Callable:
    """Return a coercion function for a column not in the explicit registry.

    Uses naming heuristics based on basketball-reference data-stat conventions.
    """
    name = column_name.lower()

    # Explicit int patterns
    if name in ("g", "mp"):
        return coerce_int_or_clock if name == "mp" else coerce_int

    # Lineup combination tables expose on/off differentials like ``+7.7``.
    if name.startswith("diff_"):
        return coerce_float

    # Percentage / rate patterns → float
    if (
        name.endswith(("_pct", "_rate", "_percentage", "_per_g", "_vorp", "_bpm", "_ws"))
        or "_per_" in name
        or "win_shares" in name
        or "box_plus_minus" in name
    ):
        return coerce_float

    # Count / integer patterns
    if any(name.startswith(pat) or name.endswith(f"_{pat}") or pat in name for pat in _COUNT_STAT_PATTERNS):
        return coerce_int

    # Default: leave as str
    return lambda v: v
