"""Optional FastAPI server for the Courtside Data UI."""

from __future__ import annotations

__all__ = ["create_app"]


def __getattr__(name: str) -> object:
    if name == "create_app":
        from courtside_data.server.app import create_app

        return create_app
    raise AttributeError(name)
