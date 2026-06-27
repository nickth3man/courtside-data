"""Service locator: shared :class:`HTTPService` singleton + per-call override.

Two pieces of state live here:

- :data:`_shared_service` / :data:`_shared_service_lock` — a single,
  lazily-created process-wide :class:`~courtside_data.http.HTTPService`.
  The first module-level call creates it under a ``threading.Lock``;
  every subsequent call reuses the same session, response cache, and
  parser graph. Rate-limit pacing is enforced globally inside that service
  so the singleton is also the single rate-limit window for the process.

- :data:`_service_override` — a :class:`~contextvars.ContextVar` set by a
  :class:`~courtside_data.client.courtside_client.CourtsideClient` for the
  duration of one method call. ``_resolve_service`` consults the override
  first, so nested helpers transparently use the client's own session
  instead of the shared one. The ``ContextVar`` makes the override safe
  across threads and async tasks. :class:`CourtsideClient` resets the
  token in a ``finally`` block.

  The symbol is re-exported from :mod:`courtside_data.client._runner` so
  external callers can keep using ``_runner._service_override`` as the
  public injection seam.
"""

from __future__ import annotations

import threading
from contextvars import ContextVar

from courtside_data.http import HTTPService

__all__ = [
    "_default_service",
    "_resolve_service",
    "_service_override",
    "_shared_service",
    "_shared_service_lock",
]

_shared_service_lock = threading.Lock()
_shared_service: HTTPService | None = None
# Set by CourtsideClient for the duration of a method call so nested helpers
# use the client's own session instead of the shared one.
_service_override: ContextVar[HTTPService | None] = ContextVar("courtside_data_service_override", default=None)


def _default_service() -> HTTPService:
    """Return the process-wide shared service, creating it on first use."""
    global _shared_service
    with _shared_service_lock:
        if _shared_service is None:
            _shared_service = HTTPService()
        return _shared_service


def _resolve_service() -> HTTPService:
    override = _service_override.get()
    return override if override is not None else _default_service()
