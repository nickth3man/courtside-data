"""Pure-function retry helpers used by :class:`HTTPService`.

Owns the retry predicates extracted from
:mod:`courtside_data.http_service`:

* :func:`_parse_retry_after` — parse a ``Retry-After`` header value per
  RFC 9110 (integer seconds and HTTP-date forms).
* :func:`_should_retry` — stamina retry predicate that decides whether
  to retry, what to wait, or to bail out as jailed.

The cap on a single ``Retry-After`` sleep is read via
:func:`courtside_data.config.max_retry_after_wait` on every call, so
changes to the ``BASKETBALL_REF_MAX_RETRY_AFTER`` env var after import
are honored immediately.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from courtside_data import config
from courtside_data.http._constants import _JAIL_THRESHOLD_SECONDS

logger = logging.getLogger(__name__)


def _parse_retry_after(value: str) -> float:
    """Parse Retry-After header value, returning seconds to wait.

    Handles both integer seconds and HTTP-date formats per RFC 9110.
    """
    try:
        return float(value)
    except ValueError:
        pass
    # HTTP-date format: parse RFC 2822 date
    import email.utils as eutils

    parsed = eutils.parsedate_tz(value)
    if parsed is not None:
        retry_time = datetime(*parsed[:6], tzinfo=UTC)
        now = datetime.now(UTC)
        wait = (retry_time - now).total_seconds()
        return max(wait, 1.0)
    return 5.0


def _should_retry(exc: Exception) -> bool | float:
    """Custom stamina retry predicate.

    Returns True to retry with default backoff, a float to retry after
    that many seconds (honors Retry-After, capped at the configured
    ``max_retry_after_wait()``), or False to abort. If the Retry-After
    value exceeds the jail threshold (5 minutes), returns False to skip
    retries — the caller handles jail detection.

    The cap is read via :func:`courtside_data.config.max_retry_after_wait`
    on every invocation, so changes to the ``BASKETBALL_REF_MAX_RETRY_AFTER``
    env var after import are honored immediately.
    """
    if isinstance(exc, httpx.TransportError):
        logger.debug("Retrying after transport error: %s", exc)
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in (429, 502, 503, 504):
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after is not None:
                parsed = _parse_retry_after(retry_after)
                if parsed > _JAIL_THRESHOLD_SECONDS:
                    logger.warning("Retry-After of %.0fs exceeds jail threshold; not retrying", parsed)
                    return False  # We're jailed — don't burn retries
                wait = min(parsed, config.max_retry_after_wait())
                logger.debug("HTTP %d with Retry-After %s; retrying in %.1fs", code, retry_after, wait)
                return wait
            logger.debug("HTTP %d; retrying with default backoff", code)
            return True
        # Do NOT retry other 4xx (400, 401, 403, 404, etc.)
        return False
    return False
