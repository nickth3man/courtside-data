"""Backward-compatibility shim for column coercion registry.

.. deprecated::
    This module exists solely for backward compatibility.
    New code should import directly from
    ``courtside_data.output.coercions``.
    This shim will be removed in a future major version.
"""

from __future__ import annotations

from courtside_data.output.coercions import _COLUMN_TYPE_MAP, _infer_coercion

__all__ = ["_COLUMN_TYPE_MAP", "_infer_coercion"]
