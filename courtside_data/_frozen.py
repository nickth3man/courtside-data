"""Project-wide decorator aliases for common dataclass configurations.

``frozen_slot`` is the alias for ``@dataclass(frozen=True, slots=True)``, the
dominant dataclass shape across the codebase (workflow steps, endpoint specs,
provenance records, debug models). Centralising it keeps declarations
declarative and trivial to scan.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import dataclass_transform


@dataclass_transform(frozen_default=True, slots_default=True)
def frozen_slot[T](cls: type[T]) -> type[T]:
    """Decorator alias for ``@dataclass(frozen=True, slots=True)``.

    Applies the two flags that ~50 classes in the codebase share. Variants
    needing additional flags (``kw_only=True``, etc.) should keep using
    ``@dataclass(...)`` directly.
    """
    return dataclass(frozen=True, slots=True)(cls)


__all__ = ["frozen_slot"]
