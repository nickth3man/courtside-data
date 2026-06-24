"""Search-results row parsers (player search list and direct player lookup)."""

from __future__ import annotations

from typing import Any

from parsel import Selector

from courtside_data.parsing.cells import (
    cell_text,
    resource_identifier,
    search_result_name,
)


def parse_search_rows_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ignored_result_reason_counts: dict[str, int] = {}
    candidate_count = len(selector.css("div#searches div#players div.search-item"))
    rows: list[dict[str, Any]] = []
    for result in selector.css("div#searches div#players div.search-item"):
        link = result.css("div.search-item-name a")
        if not link:
            ignored_result_reason_counts["missing_link"] = ignored_result_reason_counts.get("missing_link", 0) + 1
            continue
        rows.append(
            {
                "name": search_result_name(cell_text(link[0])),
                "identifier": resource_identifier(link[0].attrib.get("href")),
                "leagues": cell_text(result.css("div.search-item-league")),
            }
        )
    stats = {
        "candidate_count": candidate_count,
        "matched_result_count": len(rows),
        "ignored_result_reason_counts": ignored_result_reason_counts,
    }
    return rows, stats


def parse_search_rows(selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_search_rows_with_stats(selector)
    return rows


def parse_search_pagination_url(selector: Selector) -> str | None:
    links = selector.css("div#searches div#players div.search-pagination a")
    if not links:
        return None
    if len(links) == 1:
        if cell_text(links[0]) == "Previous 100 Results":
            return None
        return links[0].attrib["href"]
    return links[1].attrib["href"]


def parse_player_direct_search_results(selector: Selector, url: str) -> list[dict[str, Any]]:
    league_abbreviations = {
        cell_text(league)
        for league in selector.css('table#per_game tbody tr td[data-stat="lg_id"]')
        if cell_text(league)
    }
    return [
        {
            "name": cell_text(selector.css('h1[itemprop="name"]')),
            "identifier": resource_identifier(url),
            "leagues": league_abbreviations,
        }
    ]
