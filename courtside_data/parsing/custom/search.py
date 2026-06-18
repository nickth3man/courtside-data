"""Search endpoint (``search``).

Basketball Reference's ``/search/search.fcgi?search=…`` endpoint behaves
differently from a normal HTML page: the server either keeps the client
on ``/search/search.fcgi`` (with paginated results, terminated by a
"Next 100" link) or 302s straight to ``/players/<id>.html`` for a unique
match. The handler covers both branches:

* On the index, follow the "Next 100" pagination links (with a
  ``seen_pagination_urls`` cycle guard) and parse each page through
  :func:`rows.parse_search_rows`.
* On a player redirect, parse the redirected page once via
  :func:`rows.parse_player_direct_search_results` and pass the final URL
  so the row can carry the per-game ``lg_id`` cells.

The result is a single-key dict ``{"players": [...]}`` — the runner
looks up the result under the endpoint's declared
``csv_columns``, so the wrapper is structurally stable across the two
branches.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from parsel import Selector

from courtside_data.parsing import rows

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = ["search"]


def search(facade: FetchFacade, term: str) -> dict[str, list[dict[str, Any]]]:
    """Return the ``{"players": [...]}`` search-result dict for ``term``."""
    response = facade.get(url=facade.url("/search/search.fcgi"), params={"search": term})

    response.raise_for_status()

    player_results: list[dict[str, Any]] = []

    if str(response.url).startswith(facade.url("/search/search.fcgi")):
        selector = Selector(text=response.text)
        player_results += rows.parse_search_rows(selector)

        seen_pagination_urls: set[str] = set()
        pagination_url = rows.parse_search_pagination_url(selector)
        while pagination_url is not None:
            if pagination_url in seen_pagination_urls:
                break
            seen_pagination_urls.add(pagination_url)

            response = facade.get(url=f"{facade.BASE_URL}/search/{pagination_url}")

            response.raise_for_status()

            selector = Selector(text=response.text)
            player_results += rows.parse_search_rows(selector)
            pagination_url = rows.parse_search_pagination_url(selector)

    elif str(response.url).startswith(f"{facade.BASE_URL}/players"):
        selector = Selector(text=response.text)
        player_results += rows.parse_player_direct_search_results(selector, str(response.url))

    return {"players": player_results}
