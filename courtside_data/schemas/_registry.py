from __future__ import annotations

from types import GenericAlias
from typing import TYPE_CHECKING

from pydantic import TypeAdapter

if TYPE_CHECKING:
    from courtside_data.schemas._base import BRRow


ROW_ADAPTERS: dict[str, TypeAdapter[list[BRRow]]] = {}


def register(name: str, model: type[BRRow]) -> None:
    """Register a ``BRRow`` subclass as the row schema for an endpoint.

    The resulting ``TypeAdapter[list[model]]`` is stored in ``ROW_ADAPTERS``
    under ``name`` and can be used by the generic table pipeline to validate
    and coerce rows. Raises ``ValueError`` if ``name`` is already registered.
    """
    if name in ROW_ADAPTERS:
        raise ValueError(f"Schema already registered for endpoint: {name!r}")
    list_model = GenericAlias(list, (model,))
    adapter: TypeAdapter[list[BRRow]] = TypeAdapter(list_model)
    ROW_ADAPTERS[name] = adapter
