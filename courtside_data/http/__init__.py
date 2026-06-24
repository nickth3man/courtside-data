"""Public surface of the ``courtside_data.http`` package.

This package owns the HTTP transport for courtside-data: rate-limited
pacing, persistent circuit-breaker ("jail") state, retry predicates, and
the slim :class:`HTTPService` class that ties them together. The split
across focused private modules:

* :mod:`._constants` — module-level constants (timeouts, headers, cache
  sizing, jail threshold).
* :mod:`._transport` — :func:`build_client` and
  :class:`_SafeCurlTransport`.
* :mod:`._retry` — :func:`_parse_retry_after` and
  :func:`_should_retry`.
* :mod:`._rate_limit` — singleton pacing/jail state and the
  :func:`apply_rate_limiting` primitive.
* :mod:`._service` — the slim :class:`HTTPService` class.

:mod:`courtside_data.http_service` is a thin re-export module that
preserves the older ``courtside_data.http_service`` import path
(``from courtside_data.http_service import HTTPService``) for existing
callers.
"""

from __future__ import annotations

from courtside_data.http._service import HTTPService
from courtside_data.http._transport import build_client

__all__ = ["HTTPService", "build_client"]
