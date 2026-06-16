"""An httpx transport that replays saved fixture files for known URLs.

Replaces the network entirely in tests so the real ``HTTPService`` code
paths (parsers, selector cache, validation) run against deterministic
saved HTML. The transport is intentionally DUMB about URL -> file
mapping: the manifest module owns the mapping; this class just replays
it. ``httpx.MockTransport`` is a ``BaseTransport`` subclass; we
subclass ``BaseTransport`` directly for a clean custom transport
(cf. juriscraper's ``AbstractSite._request_url_mock``).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from courtside_data.http_service import HTTPService

# A value in the ``url_to_path`` mapping is one of:
#   - ``pathlib.Path``: serve the file's bytes at status 200
#   - ``tuple[int, dict[str, str] | None]``: ``(status_code, headers)`` for
#     error injection (e.g. 404 / 429)
FixtureValue = Path | tuple[int, dict[str, str] | None]


def _content_type(path: Path) -> str:
    """Map a fixture file extension to an HTTP ``Content-Type`` header value."""
    suffix = path.suffix.lower()
    if suffix == ".html":
        return "text/html; charset=utf-8"
    if suffix == ".json":
        return "application/json"
    if suffix == ".xml":
        return "application/xml"
    return "text/html; charset=utf-8"


def _strip_query(url: str) -> str:
    return url.split("?", 1)[0]


class FixtureTransport(httpx.BaseTransport):
    """A custom httpx transport that serves saved fixture files.

    URL match order in :meth:`handle_request`:
      1. Exact match against dict keys.
      2. Full URL with the query string stripped (so manifest keys can
         omit ``?search=foo`` / ``?day=...&month=...&year=...``).
      3. ``request.url.path`` only (so manifest keys can also be stored
         as bare paths like ``/boxscores/``).

    A missing URL raises ``FileNotFoundError`` whose message lists the
    requested URL and every registered key — deliberately loud so
    typos in the manifest are caught immediately rather than silently
    returning a 404.
    """

    def __init__(self, url_to_path: dict[str, FixtureValue]) -> None:
        self._url_to_path = url_to_path

    def _lookup(self, url: str) -> FixtureValue | None:
        # 1. Exact match.
        if url in self._url_to_path:
            return self._url_to_path[url]
        # 2. URL with the query string stripped.
        stripped = _strip_query(url)
        if stripped != url and stripped in self._url_to_path:
            return self._url_to_path[stripped]
        # 3. Path only (no scheme, host, or query).
        path = httpx.URL(url).path
        if path in self._url_to_path:
            return self._url_to_path[path]
        return None

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        match = self._lookup(url)
        if match is None:
            raise FileNotFoundError(
                f"FixtureTransport: no fixture registered for URL {url!r}.\n"
                f"Available keys ({len(self._url_to_path)}): "
                f"{sorted(self._url_to_path)}"
            )
        # Error-injection branch: tuple = synthetic (status, headers) response.
        if isinstance(match, tuple):
            status_code, headers = match
            return httpx.Response(
                status_code,
                headers=headers or {},
                text="",
                request=request,
            )
        # Happy path: read the file and serve it at 200.
        content = match.read_bytes()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="replace")
        return httpx.Response(
            200,
            headers={"Content-Type": _content_type(match)},
            content=content,
            text=text,
            request=request,
        )

    def close(self) -> None:
        # No resources to release: files are read on demand, no sockets opened.
        return None


def build_client(transport: FixtureTransport, *, follow_redirects: bool = True) -> httpx.Client:
    """Wrap a ``FixtureTransport`` in an ``httpx.Client``.

    ``HTTPService`` accepts the returned client via ``session=``.
    """
    return httpx.Client(transport=transport, follow_redirects=follow_redirects)


def build_service(transport: FixtureTransport) -> HTTPService:
    """Build an ``HTTPService`` whose session uses the transport.

    Rate limiting is disabled at the conftest level (env vars), so no
    pacing needs to be configured here. ``HTTPService`` is imported
    lazily so that importing this module never constructs one.
    """
    from courtside_data.http_service import HTTPService

    return HTTPService(session=build_client(transport), cache=False)
