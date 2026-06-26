"""Primitive coercion functions used by the output layer."""

from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Any


def _make_coercion(name: str, target: Callable[[str], Any], empty_value: Any) -> Callable[[Any], Any]:
    """Build a string-coercion function."""

    def coerce(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        stripped = value.strip()
        if not stripped or stripped == "\xa0":
            return empty_value
        try:
            return target(stripped)
        except ValueError:
            warnings.warn(
                f"Failed to coerce {stripped!r} via {getattr(target, '__name__', repr(target))}, leaving as string",
                UserWarning,
                stacklevel=2,
            )
            return value

    coerce.__name__ = name
    coerce.__qualname__ = name
    return coerce


coerce_int = _make_coercion("coerce_int", int, 0)
coerce_float = _make_coercion("coerce_float", float, 0.0)
coerce_int_or_none = _make_coercion("coerce_int_or_none", int, None)
coerce_float_or_none = _make_coercion("coerce_float_or_none", float, None)


def coerce_years_experience(value: Any) -> Any:
    """Coerce years_experience: int for veterans, None for BR rookie marker 'R'."""
    if isinstance(value, str) and value.strip().upper() == "R":
        return None
    return coerce_int_or_none(value)


def coerce_salary(value: Any) -> Any:
    """Coerce Basketball-Reference salary strings to whole-dollar integers."""
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped or stripped == "\xa0":
        return None
    return coerce_int_or_none(stripped.replace("$", "").replace(",", "").replace(" ", ""))


def coerce_int_or_clock(value: Any) -> Any:
    """Coerce numeric minutes while preserving Basketball-Reference clock strings."""

    if isinstance(value, str) and ":" in value.strip():
        return value
    return coerce_int(value)


coerce_int_or_clock.__name__ = "coerce_int_or_clock"


def _pass_through(value: Any) -> Any:
    """Identity coercion for free-text and already-typed columns."""
    return value
