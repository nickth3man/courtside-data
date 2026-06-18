"""Module-level constants for the ``courtside_data.http`` package.

Phase 2A of the courtside-data refactor extracts these from
:mod:`courtside_data.http_service` so they can be shared by the new
``_transport`` and ``_retry`` helpers without pulling in the entire
:class:`~courtside_data.http_service.HTTPService` class. Behavior,
defaults, and string values are preserved exactly — the live
:class:`~courtside_data.http_service.HTTPService` consumer still
imports from this package's re-exports in
:mod:`courtside_data.http_service` until Phase 2C wires the new layout.
"""

from __future__ import annotations

import httpx

from courtside_data import config

BASE_URL = "https://www.basketball-reference.com"

_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
_RETRY_ATTEMPTS = 3

# Pages like the 7-game playoff series outcomes matrix host multiple tables
# that are exposed as separate endpoints. Cache parsed selectors per URL so
# fetching several tables from the same page only makes one HTTP request and
# only parses the HTML once. The cache is per-instance and bounded to avoid
# unbounded growth for long-lived clients.
_SELECTOR_CACHE_SIZE = 16
# 10 minutes — selectors for time-sensitive pages (e.g. box scores) should
# not be reused indefinitely. TTLCache evicts on age *and* size.
_SELECTOR_CACHE_TTL = 600.0
# Basketball-Reference can send Retry-After values of an hour or more when a
# session is jailed. stamina uses a hook-returned float verbatim (wait_max
# does not apply to it), so cap it to keep a single request from sleeping
# for the full jail duration.
#
# This import-time read is preserved for backward compatibility (tests
# import ``_MAX_RETRY_AFTER_WAIT``); the live, call-time value used by
# :func:`courtside_data.http._retry._should_retry` is read via
# :func:`courtside_data.config.max_retry_after_wait`.
_MAX_RETRY_AFTER_WAIT = config.max_retry_after_wait()

# If Retry-After exceeds this threshold, the session is considered jailed
# and further retries are suppressed to avoid wasting requests.
_JAIL_THRESHOLD_SECONDS = 300.0  # 5 minutes

# Env var that controls where the on-disk jail-state blob lives. Set to
# an empty string to disable persistence (the test suite does this to
# stay hermetic). Re-exported from :mod:`courtside_data.config` for tests
# and for backward compatibility with the previous module-level constant.
_JAIL_STATE_PATH_ENV = config.BASKETBALL_REF_JAIL_STATE_PATH_ENV

# Browser-like headers proven to avoid bot-flagging.
# Tells Cloudflare this looks like a real browser navigation event.
_DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}
