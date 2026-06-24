"""Shared primitive helpers for the drop-reason classifiers.

These small, dependency-free utility functions live in their own module to
break the otherwise-circular import between :mod:`row` and
:mod:`schedule` (``row`` imports ``_schedule_drop_reason`` from
``schedule``, and ``schedule`` needs ``normalized_cell_value`` and
``_field_text`` from ``row``). Extracting them here keeps both modules
import-clean while preserving identical behavior.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def normalized_cell_value(value: Any) -> str:
    return " ".join(str(value).strip().lower().replace("\xa0", " ").split())


def _field_text(row: Mapping[str, Any], *names: str) -> str | None:
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return str(value).strip()
    return None
