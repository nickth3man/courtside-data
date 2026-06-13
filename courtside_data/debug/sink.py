"""On-disk destination for debug trace envelopes.

When an endpoint runs with ``debug=True`` the runner writes the full
``{"data": ..., "debug": ...}`` envelope to one JSON file per call. The
destination defaults to ``./logs`` (relative to the current working
directory) and can be overridden with the ``COURTSIDE_DEBUG_LOG_DIR``
environment variable. Writing is best-effort: a filesystem failure warns
but never breaks the underlying data fetch.
"""

from __future__ import annotations

import os
import warnings
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from courtside_data.debug.trace import DebugTrace

DEFAULT_LOG_DIR = "logs"
LOG_DIR_ENV_VAR = "COURTSIDE_DEBUG_LOG_DIR"


def resolve_log_dir() -> Path:
    """Return the directory debug traces are written to (``./logs`` by default)."""
    configured = os.environ.get(LOG_DIR_ENV_VAR)
    return Path(configured) if configured else Path(DEFAULT_LOG_DIR)


def _safe_segment(value: str) -> str:
    """Reduce an arbitrary string to a filename-safe segment."""
    cleaned = "".join(char if char.isalnum() or char in "-_" else "-" for char in value)
    return cleaned.strip("-_") or "trace"


def debug_log_path(trace: DebugTrace) -> Path:
    """Build the per-call log path: ``<log dir>/<timestamp>_<endpoint>_<id>.json``."""
    endpoint = _safe_segment(trace.endpoint)
    short_id = trace.trace_id.replace("-", "")[:8] or "00000000"
    try:
        stamp = datetime.fromtimestamp(trace.started_unix_ns / 1e9).strftime("%Y%m%d_%H%M%S")
    except (OSError, OverflowError, TypeError, ValueError):
        stamp = "unknown"
    return resolve_log_dir() / f"{stamp}_{endpoint}_{short_id}.json"


def prepare_log_dir(path: Path) -> bool:
    """Ensure ``path``'s parent directory exists. Returns ``False`` (and warns) on failure."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        warnings.warn(f"Could not create debug log directory {path.parent}: {error}", stacklevel=2)
        return False
    return True
