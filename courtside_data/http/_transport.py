"""HTTP client construction and the curl-cffi transport adapter.

Owns the transport pieces for the ``courtside_data.http`` package:

* :class:`_SafeCurlTransport` — workarounds for hishel 1.x + curl-cffi.
* :func:`build_client` — the rate-limit-aware ``httpx.Client`` factory.

:class:`HTTPService` (in :mod:`courtside_data.http._service`) consumes
:func:`build_client` via a late-bound indirection through
:mod:`courtside_data.http` so the offline test suite's patch of
``courtside_data.http.build_client`` flows through.
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


def _correlate_headers_with_impersonate(
    impersonate: str | None,
    user_overrides: dict[str, str] | None,
) -> dict[str, str]:
    """Build a correlated header set whose User-Agent matches the TLS fingerprint.

    Defense in depth against anti-bot systems that flag UA↔TLS mismatches:
    ``curl_cffi``'s ``impersonate="chrome131"`` sets a Chrome 131 JA3/JA4
    fingerprint, but the project's static ``_DEFAULT_HEADERS`` (in
    :mod:`courtside_data.http._constants`) carry a Chrome 124 User-Agent.
    ``browserforge`` generates a statistically-correct header set whose
    sec-ch-ua / UA values track the impersonate target.

    Falls back to ``_DEFAULT_HEADERS`` when ``impersonate is None`` or
    ``browserforge`` is not importable (e.g. during offline tests with the
    dependency stripped).

    Caller-supplied ``user_overrides`` always win, mirroring the prior
    ``{**_DEFAULT_HEADERS, **(headers or {})}`` merge semantics.

    References
    ----------
    * browserforge: https://github.com/daijro/browserforge
    * curl_cffi impersonate: https://github.com/lexiforest/curl_cffi
    """
    base = dict(_DEFAULT_HEADERS)
    if impersonate is None:
        return {**base, **(user_overrides or {})}

    try:
        from browserforge.headers import HeaderGenerator
    except ImportError:
        return {**base, **(user_overrides or {})}

    # Map curl_cffi impersonate strings ("chrome131", "chrome124", "safari17_0",
    # "firefox133", …) onto browserforge's coarser browser spec.
    if impersonate.startswith("chrome"):
        browser_spec = ("chrome",)
    elif impersonate.startswith("firefox"):
        browser_spec = ("firefox",)
    elif impersonate.startswith(("safari", "edge", "opera")):
        browser_spec = ("safari",) if impersonate.startswith("safari") else ("chrome",)
    else:
        browser_spec = ("chrome",)

    generator = HeaderGenerator(
        browser=browser_spec,
        os=("windows",),
        device=("desktop",),
        locale=("en-US", "en"),
        http_version=2,
    )
    generated = generator.generate()
    # browserforge returns a case-insensitive Headers mapping; coerce to plain
    # ``dict[str, str]`` and drop any multi-value entries the httpx headers
    # API cannot represent as a flat dict.
    correlated: dict[str, str] = {str(k): str(v) for k, v in generated.items() if isinstance(v, str)}
    return {**base, **correlated, **(user_overrides or {})}


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

    When impersonation is active, ``browserforge`` is used to generate a
    correlated header set (UA + sec-ch-ua-* + Accept-*) matching the
    impersonate target — defeats anti-bot systems that flag UA↔TLS
    mismatches. Caller-supplied ``headers`` still take precedence.
    """
    if impersonate is None:
        impersonate = config.impersonate()
    merged = _correlate_headers_with_impersonate(impersonate, headers)
    transport: httpx.BaseTransport = httpx.HTTPTransport()

    if impersonate is not None:
        transport = _SafeCurlTransport(impersonate=impersonate)

    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(transport=transport, follow_redirects=True, timeout=timeout, headers=merged)
