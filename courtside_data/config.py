"""Centralized environment-variable access for courtside-data.

This module is the **single** surface for every env var the library reads.
All helpers re-read ``os.environ`` on every call so the test suite can
flip configuration via ``monkeypatch.setenv`` without reloading modules.

The functions intentionally return plain primitives (no ``BaseSettings`` /
dataclass framework) so they stay trivial to reason about and to call from
non-runtime contexts (lazy ``build_client`` paths, debug probes, etc.).
"""

from __future__ import annotations

import os
from pathlib import Path

import platformdirs

# ─── Env var names ──────────────────────────────────────────────────────────
#
# Exposed as named constants so tests and documentation can refer to the
# exact string without re-typing it. Callers that read these env vars
# should always go through the helpers below, never ``os.environ.get`` directly.

BASKETBALL_REF_MAX_RETRY_AFTER_ENV = "BASKETBALL_REF_MAX_RETRY_AFTER"
BASKETBALL_REF_JAIL_STATE_PATH_ENV = "BASKETBALL_REF_JAIL_STATE_PATH"
BASKETBALL_REF_IMPERSONATE_ENV = "BASKETBALL_REF_IMPERSONATE"
BASKETBALL_REF_RATE_LIMIT_INTERVAL_ENV = "BASKETBALL_REF_RATE_LIMIT_INTERVAL"
BASKETBALL_REF_RATE_LIMIT_JITTER_ENV = "BASKETBALL_REF_RATE_LIMIT_JITTER"
COURTSIDE_DEBUG_LOG_DIR_ENV = "COURTSIDE_DEBUG_LOG_DIR"
COURTSIDE_DATA_PARSE_BACKEND_ENV = "COURTSIDE_DATA_PARSE_BACKEND"
COURTSIDE_DATA_FAST_PARSE_ENV = "COURTSIDE_DATA_FAST_PARSE"  # compatibility alias for COURTSIDE_DATA_PARSE_BACKEND

# ─── Default values ─────────────────────────────────────────────────────────

# Cap (seconds) on a single Retry-After sleep. Read on every call.
DEFAULT_MAX_RETRY_AFTER_WAIT: float = 60.0

# Default TLS impersonation target for ``httpx-curl-cffi``. Matches the
# rolled-forward Chrome release used by the production transport.
DEFAULT_IMPERSONATE: str = "chrome131"

# Per-request pacing (interval + uniform jitter). Defaults match
# pybaseball's proven-safe rate and keep comfortable headroom under
# Basketball-Reference's rate limit.
DEFAULT_RATE_LIMIT_INTERVAL: float = 6.0  # 10 req/min ceiling
DEFAULT_RATE_LIMIT_JITTER: float = 1.0  # uniform(0, 1.0)

# Default debug-trace destination. Relative to the current working directory.
DEFAULT_DEBUG_LOG_DIR: str = "logs"

# Default HTML-parsing backend. Selectolax (Lexbor) is ~6x faster on
# Basketball-Reference table pages than the lxml+parsel pipeline.
DEFAULT_PARSE_BACKEND: str = "selectolax"

_VALID_PARSE_BACKENDS: frozenset[str] = frozenset({"selectolax", "parsel"})


# ─── Helpers ────────────────────────────────────────────────────────────────


def max_retry_after_wait() -> float:
    """Return the cap (seconds) on a single ``Retry-After`` sleep.

    Reads ``BASKETBALL_REF_MAX_RETRY_AFTER`` on every call. The
    import-time constant ``_MAX_RETRY_AFTER_WAIT`` in
    :mod:`courtside_data.http_service`/`:mod:`courtside_data.http._constants`
    is seeded from this value for backward compatibility.
    """
    return float(os.environ.get(BASKETBALL_REF_MAX_RETRY_AFTER_ENV, str(DEFAULT_MAX_RETRY_AFTER_WAIT)))


def jail_state_path() -> Path | None:
    """Return the persisted rate-limit jail-state path, or ``None`` to disable.

    * Env var unset → default path under
      :func:`platformdirs.user_cache_dir` (``%LOCALAPPDATA%\\courtside\\
      courtside-data\\Cache\\jail.json`` on Windows, ``~/.cache/
      courtside-data/jail.json`` on Linux, ``~/Library/Caches/
      courtside-data/jail.json`` on macOS).
    * Env var set to a non-empty string → that path is used verbatim.
    * Env var set to an empty string → ``None`` (persistence disabled;
      the test suite uses this to stay hermetic).
    """
    value = os.environ.get(BASKETBALL_REF_JAIL_STATE_PATH_ENV)
    if value is None:
        return Path(platformdirs.user_cache_dir("courtside-data", "courtside")) / "jail.json"
    return Path(value) if value else None


def impersonate() -> str:
    """Return the default TLS impersonation target for ``_SafeCurlTransport``."""
    return os.environ.get(BASKETBALL_REF_IMPERSONATE_ENV, DEFAULT_IMPERSONATE)


def rate_limit_interval() -> float:
    """Return the configured per-request pacing interval (seconds)."""
    return float(os.environ.get(BASKETBALL_REF_RATE_LIMIT_INTERVAL_ENV, str(DEFAULT_RATE_LIMIT_INTERVAL)))


def rate_limit_jitter() -> float:
    """Return the configured uniform-jitter width (seconds) for pacing sleeps."""
    return float(os.environ.get(BASKETBALL_REF_RATE_LIMIT_JITTER_ENV, str(DEFAULT_RATE_LIMIT_JITTER)))


def debug_log_dir() -> Path:
    """Return the directory debug-trace envelopes are written to (default ``./logs``)."""
    configured = os.environ.get(COURTSIDE_DEBUG_LOG_DIR_ENV)
    return Path(configured) if configured else Path(DEFAULT_DEBUG_LOG_DIR)


def parse_backend() -> str:
    """Return the active HTML-parsing backend (``'selectolax'`` or ``'parsel'``).

    Resolution order:

    1. ``COURTSIDE_DATA_PARSE_BACKEND`` — case-insensitive, whitespace-stripped.
       Unknown values are ignored.
    2. ``COURTSIDE_DATA_FAST_PARSE`` — compatibility alias. ``"1"`` → ``selectolax``,
       ``"0"`` → ``parsel``. Any other value is ignored.
    3. Default → :data:`DEFAULT_PARSE_BACKEND`.
    """
    backend = os.environ.get(COURTSIDE_DATA_PARSE_BACKEND_ENV, "").strip().lower()
    if backend in _VALID_PARSE_BACKENDS:
        return backend
    legacy = os.environ.get(COURTSIDE_DATA_FAST_PARSE_ENV)
    if legacy == "1":
        return "selectolax"
    if legacy == "0":
        return "parsel"
    return DEFAULT_PARSE_BACKEND
