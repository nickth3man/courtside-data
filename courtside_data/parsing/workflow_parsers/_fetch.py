"""Public fetch surface for workflow parser helpers.

The :class:`FetchFacade` is the ONLY surface workflow parser helpers are
allowed to use to talk to :class:`~courtside_data.http.HTTPService`.
Reaching into ``http._url`` / ``http._get_selector`` / ``http._get``
directly (or reading ``HTTPService.BASE_URL`` from the transport class) is a
layering violation: those names are private to the transport and bespoke
handlers should depend on the facade so the transport can evolve
independently.

Why a facade rather than just calling :class:`HTTPService` directly?
``HTTPService._url`` is a ``@classmethod`` (no ``self``), while
``_get_selector`` and ``_get`` need a live instance — so a thin wrapper
normalizes the call shape. The facade also pins ``BASE_URL`` for the
search-redirect branch, which historically read
``HTTPService.BASE_URL`` off the class.

This module also keeps the bespoke path free of an unconditional import of
:mod:`courtside_data.http`: every domain module below imports
:class:`FetchFacade` from here, so the transport boundary lives in one
place.
"""

from __future__ import annotations

from typing import Any

import httpx
from parsel import Selector

from courtside_data.http import HTTPService

__all__ = ["FetchFacade"]


class FetchFacade:
    """Public wrapper around an :class:`HTTPService` for bespoke handlers.

    Exposes the three primitives bespoke handlers need (``url``,
    ``get_selector``, ``get``) plus the transport's ``BASE_URL``. The
    underlying ``HTTPService`` is held as a private attribute and is never
    exposed — handlers should never need to call any other transport
    method.
    """

    BASE_URL: str = HTTPService.BASE_URL

    def __init__(self, http: HTTPService) -> None:
        self._http = http

    def url(self, path: str = "") -> str:
        """Return the absolute URL for a Basketball Reference path.

        Thin pass-through to :meth:`HTTPService._url` — leading slash is
        optional, and an empty ``path`` returns :attr:`BASE_URL`.
        """
        return self._http._url(path)

    def get_selector(self, url: str) -> Selector:
        """Fetch a page and return a parsel ``Selector`` (cached per instance)."""
        return self._http._get_selector(url=url)

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Fetch a raw ``httpx.Response`` — used by handlers that need the
        status code or follow-redirect control (search, daily leaders).
        """
        return self._http._get(url=url, **kwargs)
