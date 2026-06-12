"""Pydantic v2 row schemas for Basketball-Reference endpoints.

This package is intentionally small at the top level. Domain modules add
per-endpoint row models and call ``register`` at import time; consumers import
``BRRow``, ``ROW_ADAPTERS``, and ``register`` from here.

Importing the domain submodules here is the side effect that populates
``ROW_ADAPTERS``. Each module calls :func:`register` exactly once per
endpoint, and registration is idempotent against the module's import order.
"""

# ``register`` must be available in this package's namespace before the
# domain submodules are imported — they call ``from courtside_data.schemas
# import register`` at module load time. Importing the registry first also
# initialises ``ROW_ADAPTERS`` (an empty dict) so submodules can rely on it.
from courtside_data.schemas._registry import ROW_ADAPTERS, register  # noqa: I001

# Domain modules — each calls ``register(name, Model)`` at import time,
# populating ROW_ADAPTERS with one TypeAdapter[list[Model]] per endpoint.
from courtside_data.schemas import (
    boxscores,
    draft,
    league,
    playbyplay,
    players,
    playoffs,
    schedule,
    search,
    standings,
    teams,
)
from courtside_data.schemas._base import BRRow

__all__ = [
    "BRRow",
    "ROW_ADAPTERS",
    "register",
    "boxscores",
    "draft",
    "league",
    "playbyplay",
    "players",
    "playoffs",
    "schedule",
    "search",
    "standings",
    "teams",
]
