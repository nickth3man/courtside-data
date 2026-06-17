"""Pure HTML/value parsing helpers extracted from :mod:`courtside_data.http_service`.

These functions have no dependency on :class:`HTTPService` state (no ``self``/
``cls``); they take a parsel ``Selector`` or plain values and return parsed data.
They are kept here so the HTTP layer stays focused on requests, caching, rate
limiting, and trace recording. ``HTTPService`` exposes them as ``@staticmethod``
shims for backward compatibility with existing call sites.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qs, urlparse

from parsel import Selector

from courtside_data.data import (
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
    Division,
    Team,
)
from courtside_data.errors import MissingPlayerSlug

_BR_WIN_COLOR = "#080"
_BR_LOSS_COLOR = "#f00"


def cell_text(selector: Any) -> str:
    text = (
        " ".join(value.strip() for value in selector.css("::text").getall() if value.strip()).replace("*", "").strip()
    )
    return re.sub(r"\s+([),.;:])", r"\1", text)


def slug_from_metadata(metadata: dict[str, dict[str, str]], stat_name: str) -> str:
    return metadata.get(stat_name, {}).get("data-append-csv", "")


def require_slug(endpoint_name: str, row: dict[str, Any], row_index: int) -> None:
    if row.get("slug"):
        return
    player = row.get("name_display") or row.get("player") or row.get("name") or "<unknown>"
    raise MissingPlayerSlug(endpoint_name=endpoint_name, row_index=row_index, player=str(player))


def is_combined_team(row: dict[str, Any]) -> bool:
    return str(row.get("team_name_abbr", "")).endswith("TM")


def team_abbreviation_from_name(team_name: str) -> str:
    team = TEAM_NAME_TO_TEAM[team_name.strip().upper()]
    return TEAM_TO_TEAM_ABBREVIATION[team]


def team_name_from_abbreviation(team_abbreviation: str) -> str:
    return TEAM_ABBREVIATIONS_TO_TEAM[team_abbreviation].value.title()


def score_outcome(points: str, opponent_points: str) -> str | None:
    team_points = int(points)
    opposing_points = int(opponent_points)
    if team_points > opposing_points:
        return "W"
    if team_points < opposing_points:
        return "L"
    return None


def period_number(period_count: int) -> int:
    return period_count if period_count <= 4 else period_count - 4


def period_type(period_count: int) -> str:
    return "QUARTER" if period_count <= 4 else "OVERTIME"


def remaining_seconds(timestamp: str) -> float:
    minutes, seconds = timestamp.split(":", maxsplit=1)
    return (int(minutes) * 60) + float(seconds)


def standings_team_value(formatted_name: str) -> str:
    cleaned = formatted_name.upper().strip()
    for team in Team:
        if cleaned.startswith(team.value):
            return team.value
    return cleaned


def division_value(formatted_name: str) -> str | None:
    cleaned = formatted_name.upper().strip()
    for division in Division:
        if cleaned == f"{division.value} DIVISION":
            return division.value
    return None


def resource_identifier(resource_location: str | None) -> str:
    if not resource_location:
        return ""
    return resource_location.rstrip("/").rsplit("/", maxsplit=1)[-1].removesuffix(".html")


def search_result_name(resource_name: str | None) -> str:
    if resource_name is None:
        return ""
    return resource_name.split("(", maxsplit=1)[0].strip()


def extract_pattern_from_href(href: str) -> str:
    if not href:
        return ""
    return parse_qs(urlparse(href).query).get("pattern", [""])[0]


def pattern_to_games_played(pattern: str) -> list[dict[str, Any]]:
    games: list[dict[str, Any]] = []
    index = 0
    game_number = 1
    while index < len(pattern):
        location_char = pattern[index]
        if location_char not in ("H", "A"):
            break
        index += 1
        if index >= len(pattern) or pattern[index] not in ("0", "1"):
            break
        result = "win" if pattern[index] == "1" else "loss"
        index += 1
        location = "home" if location_char == "H" else "away"
        games.append({"game": game_number, "location": location, "result": result})
        game_number += 1
    return games


def remaining_locations_from_text(text: str) -> list[str]:
    locations: list[str] = []
    for char in text.replace(" ", ""):
        if char == "H":
            locations.append("home")
        elif char == "A":
            locations.append("away")
    return locations


def pattern_from_gameslist_spans(gameslist_cell: Selector) -> str | None:
    parts: list[str] = []
    seen_slash = False
    for span in gameslist_cell.css("span"):
        text = (span.css("::text").get() or "").strip()
        if text == "/":
            seen_slash = True
            continue
        if seen_slash or text not in ("H", "A"):
            continue
        style = span.attrib.get("style", "")
        if _BR_WIN_COLOR in style:
            parts.append(f"{text}1")
        elif _BR_LOSS_COLOR in style:
            parts.append(f"{text}0")
        else:
            parts.append(text)
    if not parts:
        return None
    return "".join(parts)


def remaining_text_from_gameslist(gameslist_cell: Selector) -> str:
    raw = "".join(gameslist_cell.css("::text").getall())
    if "/" not in raw:
        return ""
    return raw.split("/", 1)[1].strip().replace(" ", "")


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
