"""Backwards-compatibility shim for the HTTP transport.

Phase 2C of the courtside-data refactor moves the implementation into
:mod:`courtside_data.http._service` and the rate-limit singleton into
:mod:`courtside_data.http._rate_limit`. This module re-exports the
public (and previously private) names that lived here so existing
imports keep working:

* :class:`HTTPService` — the rate-limited, retried, selector-cached
  HTTP client.
* :func:`build_client` — the rate-limit-aware ``httpx.Client`` factory.
* :class:`_SafeCurlTransport` — the curl-cffi transport shim used by
  :func:`build_client`.
* Module-level constants: ``_DEFAULT_TIMEOUT``, ``_RETRY_ATTEMPTS``,
  ``_SELECTOR_CACHE_SIZE``, ``_SELECTOR_CACHE_TTL``, ``_DEFAULT_HEADERS``,
  ``_MAX_RETRY_AFTER_WAIT``, ``_JAIL_THRESHOLD_SECONDS``,
  ``_JAIL_STATE_PATH_ENV``.
* Pure-function retry helpers: :func:`_parse_retry_after` and
  :func:`_should_retry`.
* Persistence helpers: :func:`_read_persisted_jail`,
  :func:`_persist_jail`, and the thin :func:`_jail_state_path` wrapper
  around :func:`courtside_data.config.jail_state_path`.

Process-wide pacing state (``_last_request_time``, ``_jailed_until``,
``_jail_state_loaded``, ``_rate_limit_lock``) lives in
:mod:`courtside_data.http._rate_limit` and is exposed on
:class:`HTTPService` via the :class:`_ClassStateMeta` metaclass
forwarder, so existing test resets
(``HTTPService._last_request_time = float('-inf')``) keep working
without code changes.

The shim is intended to be removed in a future major release once the
new module path is the public surface.
"""

from __future__ import annotations

from courtside_data import config
from courtside_data.http import _constants, _rate_limit, _retry, _service
from courtside_data.http._service import HTTPService
from courtside_data.http._transport import _SafeCurlTransport, build_client

# Re-export the module-level constants. Defined as module attributes
# (not bare imports) so they appear as ``http_service._DEFAULT_TIMEOUT``
# etc. on the legacy module — matching the previous layout.
_DEFAULT_TIMEOUT = _constants._DEFAULT_TIMEOUT
_RETRY_ATTEMPTS = _constants._RETRY_ATTEMPTS
_SELECTOR_CACHE_SIZE = _constants._SELECTOR_CACHE_SIZE
_SELECTOR_CACHE_TTL = _constants._SELECTOR_CACHE_TTL
_MAX_RETRY_AFTER_WAIT = _constants._MAX_RETRY_AFTER_WAIT
_JAIL_THRESHOLD_SECONDS = _constants._JAIL_THRESHOLD_SECONDS
_JAIL_STATE_PATH_ENV = _constants._JAIL_STATE_PATH_ENV
_DEFAULT_HEADERS = _constants._DEFAULT_HEADERS

# Re-export the pure-function retry helpers.
_parse_retry_after = _retry._parse_retry_after
_should_retry = _retry._should_retry

# Re-export the persistence helpers. ``_persist_jail`` and
# ``_read_persisted_jail`` now live in :mod:`courtside_data.http._rate_limit`.
_persist_jail = _rate_limit._persist_jail
_read_persisted_jail = _rate_limit._read_persisted_jail


def _jail_state_path():
    """Return the persisted jail-state path, or ``None`` if persistence is disabled.

    Thin wrapper around :func:`courtside_data.config.jail_state_path`
    preserved for callers that historically imported ``_jail_state_path``
    from :mod:`courtside_data.http_service`.
    """
    return config.jail_state_path()


# Re-export the service module's ``BASE_URL`` for callers that
# historically imported it as ``http_service.BASE_URL`` (or read it off
# the class via ``HTTPService.BASE_URL``).
BASE_URL = _service.BASE_URL


__all__ = [
    "BASE_URL",
    "_DEFAULT_HEADERS",
    "_DEFAULT_TIMEOUT",
    "_JAIL_STATE_PATH_ENV",
    "_JAIL_THRESHOLD_SECONDS",
    "_MAX_RETRY_AFTER_WAIT",
    "_RETRY_ATTEMPTS",
    "_SELECTOR_CACHE_SIZE",
    "_SELECTOR_CACHE_TTL",
    "HTTPService",
    "_SafeCurlTransport",
    "_jail_state_path",
    "_parse_retry_after",
    "_persist_jail",
    "_read_persisted_jail",
    "_should_retry",
    "build_client",
]
