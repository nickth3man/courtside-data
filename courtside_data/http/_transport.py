"""HTTP client construction and the curl-cffi transport shim.

Phase 2A of the courtside-data refactor extracts the transport pieces
from :mod:`courtside_data.http_service`:

* :class:`_SafeCurlTransport` — workarounds for hishel 1.x + curl-cffi.
* :func:`build_client` — the rate-limit-aware ``httpx.Client`` factory.

The :class:`~courtside_data.http_service.HTTPService` consumer still
lives in :mod:`courtside_data.http_service` and will switch to calling
this module in Phase 2C. Until then both surfaces exist in parallel.
"""

from __future__ import annotations

from typing import Any

import httpx
from curl_cffi.const import CurlOpt  # type: ignore[import-untyped]
from hishel.httpx import SyncCacheTransport

from courtside_data import config
from courtside_data.http._constants import _DEFAULT_HEADERS, _DEFAULT_TIMEOUT


class _SafeCurlTransport(httpx.BaseTransport):
    """Wraps :class:`httpx_curl_cffi.CurlTransport` with two workarounds for
    correct caching behavior with hishel:

    1. **Timeout extension**: A hishel 1.x regression drops the ``timeout``
       extension when revalidating cached responses, causing
       ``CurlTransport._create_request_params`` to fail with an
       ``AssertionError``. The ``handle_request`` method ensures every
       request has a ``timeout`` extension before handing off to the real
       transport.

    2. **Content decoding**: ``curl-cffi`` decompresses gzip responses by
       default but leaves the ``Content-Encoding: gzip`` header in place.
       When hishel stores/retrieves the response, ``httpx`` sees the header
       and tries to decompress already-plaintext content, raising
       ``httpx.DecodingError``. Passing
       ``curl_options={CurlOpt.HTTP_CONTENT_DECODING: 0}`` tells libcurl
       not to decode content, so ``httpx`` handles decompression
       consistently.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        from httpx_curl_cffi import CurlTransport  # type: ignore[import-untyped]

        curl_options = kwargs.pop("curl_options", {})
        curl_options = {CurlOpt.HTTP_CONTENT_DECODING: 0, **curl_options}
        self._impl = CurlTransport(*args, curl_options=curl_options, **kwargs)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if "timeout" not in request.extensions:
            request.extensions["timeout"] = {
                "connect": _DEFAULT_TIMEOUT.connect,
                "read": _DEFAULT_TIMEOUT.read,
                "write": _DEFAULT_TIMEOUT.write,
                "pool": _DEFAULT_TIMEOUT.pool,
            }
        return self._impl.handle_request(request)

    def close(self) -> None:
        self._impl.close()


def build_client(
    cache: bool = False,
    timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
    headers: dict[str, str] | None = None,
    impersonate: str | None = None,
) -> httpx.Client:
    """Build the httpx client used by HTTPService.

    With cache=True, responses are cached per RFC 9111 via hishel's
    SQLite-backed storage. Headers default to browser-like values that
    reduce bot-flagging; pass ``headers`` to override or extend.

    TLS impersonation is enabled by default via the ``httpx-curl-cffi``
    package, using the Chrome target named by the ``BASKETBALL_REF_IMPERSONATE``
    env var when set, otherwise ``"chrome131"``. The default was rolled
    forward from ``"chrome124"`` (early 2024) to keep the JA3/JA4
    fingerprint aligned with a current stable Chrome release. Set
    ``impersonate=None`` to use standard httpx TLS instead.
    """
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    transport: httpx.BaseTransport = httpx.HTTPTransport()

    if impersonate is None:
        impersonate = config.impersonate()
    if impersonate is not None:
        transport = _SafeCurlTransport(impersonate=impersonate)

    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(transport=transport, follow_redirects=True, timeout=timeout, headers=merged)
