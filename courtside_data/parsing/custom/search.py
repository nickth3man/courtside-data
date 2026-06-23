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

from collections import Counter
from typing import TYPE_CHECKING, Any

from parsel import Selector

from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.parsing import rows

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = ["search"]


def _merge_search_stats(aggregate: dict[str, Any], page_stats: dict[str, Any]) -> None:
    aggregate["candidate_count"] = aggregate.get("candidate_count", 0) + page_stats.get("candidate_count", 0)
    aggregate["matched_result_count"] = aggregate.get("matched_result_count", 0) + page_stats.get(
        "matched_result_count", 0
    )
    ignored = aggregate.setdefault("ignored_result_reason_counts", Counter())
    for reason, count in (page_stats.get("ignored_result_reason_counts") or {}).items():
        ignored[reason] += count


def search(facade: FetchFacade, term: str) -> dict[str, list[dict[str, Any]]]:
    """Return the ``{"players": [...]}`` search-result dict for ``term``."""
    response = facade.get(url=facade.url("/search/search.fcgi"), params={"search": term})

    response.raise_for_status()

    player_results: list[dict[str, Any]] = []
    aggregate_stats: dict[str, Any] = {
        "query": term,
        "candidate_count": 0,
        "matched_result_count": 0,
        "ignored_result_reason_counts": Counter(),
        "result_source": "unknown",
    }
    source_sections = ["div#searches div#players"]

    if str(response.url).startswith(facade.url("/search/search.fcgi")):
        aggregate_stats["result_source"] = "search_index"
        selector = Selector(text=response.text)
        page_rows, page_stats = rows.parse_search_rows_with_stats(selector)
        player_results.extend(page_rows)
        _merge_search_stats(aggregate_stats, page_stats)

        seen_pagination_urls: set[str] = set()
        pagination_url = rows.parse_search_pagination_url(selector)
        while pagination_url is not None:
            if pagination_url in seen_pagination_urls:
                break
            seen_pagination_urls.add(pagination_url)

            response = facade.get(url=f"{facade.BASE_URL}/search/{pagination_url}")

            response.raise_for_status()

            selector = Selector(text=response.text)
            page_rows, page_stats = rows.parse_search_rows_with_stats(selector)
            player_results.extend(page_rows)
            _merge_search_stats(aggregate_stats, page_stats)
            pagination_url = rows.parse_search_pagination_url(selector)

    elif str(response.url).startswith(f"{facade.BASE_URL}/players"):
        aggregate_stats["result_source"] = "player_redirect"
        source_sections = ["h1[itemprop=name]", "table#per_game"]
        selector = Selector(text=response.text)
        player_results.extend(rows.parse_player_direct_search_results(selector, str(response.url)))
        aggregate_stats["candidate_count"] = 1
        aggregate_stats["matched_result_count"] = len(player_results)

    aggregate_stats["result_count"] = len(player_results)
    ignored = aggregate_stats["ignored_result_reason_counts"]
    trace = current_debug_trace()
    if trace is not None:
        emit_parser_diagnostics(
            trace,
            parser_name="search",
            rows=player_results,
            source_sections=source_sections,
            ignored_event_count=sum(ignored.values()) if ignored else None,
            ignored_event_reason_counts=dict(ignored) if ignored else None,
            custom_diagnostics={
                "query": term,
                "result_count": len(player_results),
                "candidate_count": aggregate_stats.get("candidate_count"),
                "matched_result_count": aggregate_stats.get("matched_result_count"),
                "ignored_result_reason_counts": dict(ignored) if ignored else {},
                "result_source": aggregate_stats.get("result_source"),
            },
        )
    return {"players": player_results}
