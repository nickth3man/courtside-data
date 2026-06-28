"""Search-results row parsers (player search list and direct player lookup)."""

from __future__ import annotations

import re
from typing import Any

from parsel import Selector

from courtside_data.parsing.cells import (
    cell_text,
    resource_identifier,
    search_result_name,
)

# Sub-`div` id -> ``type`` discriminator stamped on every result card.
# See ``ideas/br-search-idx-research-2026-06-28.md`` §1 for the canonical
# 13-index list. Both ``teams`` and ``team_seasons`` collapse to
# ``"team"`` (the enum doesn't distinguish the franchise card from the
# per-season card). Unknown sub-`div` ids fall through to ``"other"``
# (forward-compat: BR may add new indexes in the future).
_SUB_DIV_TO_TYPE: dict[str, str] = {
    "players": "player",
    "wnba_players": "player",
    "intl_players": "player",
    "nbdl_players": "player",
    "nbl_players": "player",
    "sup_players": "player",
    "coaches": "coach",
    "wnba_coaches": "coach",
    "executives": "executive",
    "wnba_executives": "executive",
    "referees": "referee",
    "teams": "team",
    "team_seasons": "team",
}

# ``team_seasons`` card hrefs are ``/teams/{ABBR}/{YEAR}.html`` (e.g.
# ``/teams/NOJ/1975.html``). The team-search service dedupes by
# identifier, so the per-season card MUST carry the team abbreviation
# (not the year) as its identifier — otherwise the dedupe misses it
# and the per-season row leaks through to team-search results, where
# the deep-link ``/teams/{identifier}/summary`` would 404.
# Match the second-to-last path segment, preserving case (BR emits
# uppercase abbreviations; the ``[^/]+`` is intentionally
# case-preserving and tolerant of any future 4-letter franchises).
_TEAM_SEASONS_HREF_RE = re.compile(r"/teams/([^/]+)/")


def _resolve_type(sub_div_id: str | None) -> str:
    """Map a parent sub-`div` id to the entity-type discriminator.

    Returns ``"other"`` for any sub-`div` id not in the known table
    (forward-compat). Returns ``"player"`` for the legacy
    ``div#searches div#players`` selector path that callers (e.g. the
    player-hub search) still use today.
    """
    if sub_div_id is None:
        return "player"
    return _SUB_DIV_TO_TYPE.get(sub_div_id, "other")


def _all_search_items(selector: Selector) -> list[tuple[str, str | None, Any]]:
    """Walk every sub-`div` under ``div#searches`` and yield
    ``(type, sub_div_id, item)``.

    The sub-`div` parent id is the cleanest discriminator signal: every
    ``search-item`` sits inside exactly one sub-`div`, and the sub-`div`
    id is fixed by BR (see librarian research §2 "reliable
    discriminator signal"). We deliberately do not use the href prefix
    — ``/teams/{ABBR}/`` is shared by both ``teams`` and ``team_seasons``
    cards and cannot distinguish them.

    The sub-`div` id is also yielded alongside the resolved type so the
    caller can branch on it (e.g. ``team_seasons`` hrefs need a
    different identifier extraction than ``teams`` hrefs).
    """
    items: list[tuple[str, str | None, Any]] = []
    for sub_div in selector.css("div#searches > div[id]"):
        sub_div_id = sub_div.attrib.get("id")
        type_value = _resolve_type(sub_div_id)
        for result in sub_div.css("div.search-item"):
            items.append((type_value, sub_div_id, result))
    return items


def parse_search_rows_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ignored_result_reason_counts: dict[str, int] = {}
    # Backwards-compat candidate count: the player-hub stats panel
    # only ever reports the player-tab count. The new path walks
    # every sub-`div`, but the stats contract is preserved here for
    # the player-hub consumer.
    candidate_count = len(selector.css("div#searches div#players div.search-item"))
    rows: list[dict[str, Any]] = []
    for type_value, sub_div_id, result in _all_search_items(selector):
        link = result.css("div.search-item-name a")
        if not link:
            ignored_result_reason_counts["missing_link"] = ignored_result_reason_counts.get("missing_link", 0) + 1
            continue
        href = link[0].attrib.get("href")
        # ``team_seasons`` hrefs are ``/teams/{ABBR}/{YEAR}.html``; the
        # default ``resource_identifier`` would return ``{YEAR}`` as
        # the identifier, which makes the team-search dedupe pass
        # useless (each season is a fresh identifier). Branch on the
        # sub-`div` id and pull the team abbreviation out of the href
        # instead, so the per-season card shares its identifier with
        # the franchise card and gets collapsed by the dedupe.
        if sub_div_id == "team_seasons" and href:
            match = _TEAM_SEASONS_HREF_RE.search(href)
            identifier = match.group(1) if match else resource_identifier(href)
        else:
            # ``resource_identifier`` is the URL-tail last segment,
            # with the ``.html`` suffix stripped. Team hrefs are
            # uppercase (``/teams/BOS/``); the ``rsplit`` /
            # ``removesuffix`` chain preserves the original case so
            # the team-hub deep-link ``/teams/{identifier}/summary``
            # doesn't 404 from a mistakenly lowercased BOS.
            identifier = resource_identifier(href)
        rows.append(
            {
                "name": search_result_name(cell_text(link[0])),
                "identifier": identifier,
                "leagues": cell_text(result.css("div.search-item-league")),
                "type": type_value,
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
            "type": "player",
        }
    ]
