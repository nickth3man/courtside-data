"""Persistent on-disk cache tier — complements the in-memory ``cachetools`` layer.

The project has two cache tiers:

* **Hot (in-process, sync)** — :class:`cachetools.TTLCache` in
  :mod:`courtside_data.http._service` caches parsed selectors for the
  configured TTL (10 min default). Fast, microsecond, dies with the process.

* **Cold (cross-process, persistent)** — :class:`diskcache.Cache` exposed
  here. SQLite-backed, thread-safe AND process-safe via WAL, survives
  interpreter restarts. Use it for scraped/typed results you want to keep
  across CLI invocations or long-running jobs.

The cold-tier directory honours the existing ``platformdirs`` convention
used for the rate-limit jail state, so it lands in the OS-appropriate
per-user cache location.

Example
-------
>>> from courtside_data.cache import cold_cache
>>> cold_cache.set("team_roster:BOS:2026", roster_bytes, expire=86400)
>>> roster_bytes = cold_cache.get("team_roster:BOS:2026")

Stampede protection is built in via :func:`diskcache.memoize_stampede`.

References
----------
* diskcache: https://github.com/grantjenks/python-diskcache
* cachetools (hot tier): https://github.com/tkem/cachetools
* platformdirs: https://github.com/tox-dev/platformdirs
"""

from __future__ import annotations

from pathlib import Path

import diskcache
from platformdirs import user_cache_dir

_DEFAULT_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
_CACHE_DIR = Path(user_cache_dir("courtside-data", "courtside")) / "br_cache"

#: Module-level singleton. ``diskcache.Cache`` is thread-safe and process-safe
#: (SQLite WAL), so sharing one instance across the process is the intended
#: usage pattern. Tests should construct their own ``diskcache.Cache`` under
#: ``tmp_path`` rather than mutating this singleton.
cold_cache: diskcache.Cache = diskcache.Cache(_CACHE_DIR, ttl=_DEFAULT_TTL_SECONDS)


__all__ = ["_CACHE_DIR", "cold_cache"]
