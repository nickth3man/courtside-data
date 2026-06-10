from __future__ import annotations

from typing import Any, overload


@overload
def str_to_int(value: Any) -> int: ...
@overload
def str_to_int(value: Any, default: None) -> int | None: ...
@overload
def str_to_int(value: Any, default: int) -> int: ...
def str_to_int(value: Any, default: int | None = 0) -> int | None:
    stripped_value = str(value).strip()
    try:
        return int(stripped_value)
    except ValueError:
        return default


@overload
def str_to_float(value: Any) -> float: ...
@overload
def str_to_float(value: Any, default: None) -> float | None: ...
@overload
def str_to_float(value: Any, default: float) -> float: ...
def str_to_float(value: Any, default: float | None = 0.0) -> float | None:
    stripped_value = str(value).strip()
    try:
        return float(stripped_value)
    except ValueError:
        return default
