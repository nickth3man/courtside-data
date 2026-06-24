"""Playoff row parsers (Friv series-outcomes table and bracket pages)."""

from __future__ import annotations

import re
from typing import Any

from parsel import Selector

from courtside_data.parsing.cells import (
    cell_text,
    extract_pattern_from_href,
    pattern_from_gameslist_spans,
    pattern_to_games_played,
    remaining_locations_from_text,
    remaining_text_from_gameslist,
)


def parse_friv_playoff_outcomes_row(row: Selector) -> dict[str, Any]:
    record = cell_text(row.css('[data-stat="record"]'))
    gameslist_cell = row.css('[data-stat="gameslist"]')
    wl_cell = row.css('[data-stat="wl"]')
    gameslist_display = cell_text(gameslist_cell) if gameslist_cell else ""
    wl = cell_text(wl_cell) if wl_cell else ""
    href = wl_cell.css("a::attr(href)").get() if wl_cell else ""
    pattern = extract_pattern_from_href(href or "")
    aggregate = gameslist_display.strip().casefold() == "all series"

    if aggregate:
        return {
            "record": record,
            "gameslist": gameslist_display,
            "wl": wl,
            "aggregate": True,
            "pattern": pattern,
            "pattern_from_spans": None,
            "patterns_agree": None,
            "games_played": [],
            "games_remaining": [],
            "gameslist_display": gameslist_display,
        }

    gameslist_node = gameslist_cell[0]
    pattern_from_spans = pattern_from_gameslist_spans(gameslist_node)
    remaining_text = remaining_text_from_gameslist(gameslist_node)
    canonical_pattern = pattern or pattern_from_spans or ""
    games_played = pattern_to_games_played(canonical_pattern)
    games_remaining = remaining_locations_from_text(remaining_text)
    patterns_agree = None if pattern_from_spans is None or not pattern else pattern == pattern_from_spans

    return {
        "record": record,
        "gameslist": gameslist_display,
        "wl": wl,
        "aggregate": False,
        "pattern": pattern,
        "pattern_from_spans": pattern_from_spans,
        "patterns_agree": patterns_agree,
        "games_played": games_played,
        "games_remaining": games_remaining,
        "gameslist_display": gameslist_display,
    }


def parse_playoff_bracket(table_selector: Selector) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in table_selector.xpath("./tbody/tr"):
        classes = row.attrib.get("class", "").split()
        if "thead" in classes or "toggleable" in classes or row.css("table"):
            continue
        cells = row.xpath("./td|./th")
        if len(cells) != 3:
            continue

        series = cell_text(cells[0])
        matchup = re.sub(r"\s+", " ", cell_text(cells[1])).strip()
        if not series or not matchup:
            continue

        team, separator, result = matchup.partition(" over ")
        rows.append(
            {
                "series": series,
                "team": team.strip(),
                "result": f"over {result.strip()}" if separator else matchup,
            }
        )
    return rows
