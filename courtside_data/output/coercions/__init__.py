"""Column coercion registry and inference."""

from __future__ import annotations

from courtside_data.output.coercions.inference import _infer_coercion
from courtside_data.output.coercions.registry import _COLUMN_TYPE_MAP, _COUNT_STAT_PATTERNS

__all__ = ["_COLUMN_TYPE_MAP", "_infer_coercion"]

# Re-export the private pattern tuple for backward compat (used by _infer_coercion internally).
_COUNT_STAT_PATTERNS  # noqa: B018
