"""CLI entry point for the optional Player Hub API server."""

from __future__ import annotations

import os
from pathlib import Path

from courtside_data.server.models import TransportMode


def serve(
    *,
    transport: TransportMode,
    host: str,
    port: int,
    raw_root: str | None = None,
    reload: bool = False,
) -> int:
    """Run the FastAPI server through Uvicorn."""

    try:
        import uvicorn
    except ImportError as error:  # pragma: no cover - depends on optional extra
        raise RuntimeError("Install courtside-data with the 'server' extra to use `courtside-data serve`.") from error

    os.environ["COURTSIDE_SERVER_TRANSPORT"] = transport
    if raw_root is not None:
        os.environ["COURTSIDE_DATA_FIXTURE_ROOT"] = str(Path(raw_root).resolve())
    uvicorn.run(
        "courtside_data.server.app:app",
        host=host,
        port=port,
        reload=reload,
        factory=False,
    )
    return 0
