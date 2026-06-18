"""High-level row parsers for Basketball Reference tables.

Each function takes a parsel ``Selector`` (typically a table or row) and
returns a list of plain ``dict`` rows. They compose the low-level helpers
in :mod:`courtside_data.parsing.cells` and the generic table extractor in
:mod:`courtside_data.parsing.tables`.
"""

from __future__ import annotations

import re
from typing import Any

from parsel import Selector

from courtside_data.data import DIVISIONS_TO_CONFERENCES, Division
from courtside_data.debug import current_debug_trace
from courtside_data.parsing.cells import (
    cell_text,
    division_value,
    extract_pattern_from_href,
    pattern_from_gameslist_spans,
    pattern_to_games_played,
    period_number,
    period_type,
    remaining_locations_from_text,
    remaining_seconds,
    remaining_text_from_gameslist,
    resource_identifier,
    score_outcome,
    search_result_name,
    standings_team_value,
    team_name_from_abbreviation,
)
from courtside_data.parsing.tables import GenericTable


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


def raw_rows_from_table(
    table_selector: Selector,
    *,
    use_header_fallback: bool = False,
) -> list[tuple[dict[str, Any], dict[str, dict[str, str]]]]:
    table = GenericTable(table_selector, use_header_fallback=use_header_fallback)
    rows = [(row.to_dict(), row.metadata) for row in table.rows]
    trace = current_debug_trace()
    if trace is not None:
        trace.record(
            "parse",
            "raw_rows_from_table",
            row_count=len(rows),
            use_header_fallback=use_header_fallback,
            column_names=list(rows[0][0].keys()) if rows else [],
        )
        trace.append_artifact(
            "raw_table_extracts",
            {
                "rows": [row for row, _ in rows],
                "row_metadata": [
                    {"row_index": index, "metadata": metadata} for index, (_, metadata) in enumerate(rows)
                ],
            },
        )
    return rows


def parse_standings(selector: Selector) -> list[dict[str, Any]]:
    standings: list[dict[str, Any]] = []
    for table_id in ("divs_standings_E", "divs_standings_W"):
        current_division: Division | None = None
        table = selector.css(f"table#{table_id}")
        if not table:
            continue
        for row in table[0].css("tbody tr"):
            classes = row.attrib.get("class", "").split()
            if "thead" in classes:
                div_val = division_value(cell_text(row.css("th")))
                current_division = Division(div_val) if div_val is not None else None
                continue
            team = cell_text(row.css('[data-stat="team_name"]'))
            if not team:
                continue
            standings.append(
                {
                    "team": standings_team_value(team),
                    "wins": cell_text(row.css('[data-stat="wins"]')),
                    "losses": cell_text(row.css('[data-stat="losses"]')),
                    "division": current_division.value if current_division is not None else None,
                    "conference": (
                        DIVISIONS_TO_CONFERENCES[current_division].value if current_division is not None else None
                    ),
                }
            )
    return standings


def resolve_pbp_game_url_path(boxscores_selector: Selector, abbr: str) -> str | None:
    for path in [link.attrib["href"] for link in boxscores_selector.css("td.gamelink a")]:
        if path.endswith((f"0{abbr}.html", f"1{abbr}.html")):
            return path
    return None


def parse_play_by_play_rows(selector: Selector, away_team: str, home_team_abbreviation: str) -> list[dict[str, Any]]:
    current_period = 0
    rows: list[dict[str, Any]] = []
    for row in selector.css("table#pbp tr"):
        cells = row.css("td, th")
        if not cells:
            continue
        timestamp_cell = cells[0]
        if timestamp_cell.attrib.get("colspan") == "6":
            current_period += 1
            continue
        if len(cells) < 2 or cells[1].attrib.get("colspan") == "5" or timestamp_cell.attrib.get("aria-label") == "Time":
            continue

        timestamp = cell_text(timestamp_cell)
        away_description = cell_text(cells[1]) if len(cells) == 6 else ""
        home_description = cell_text(cells[5]) if len(cells) == 6 else ""
        scores = cell_text(cells[3]) if len(cells) == 6 else ""
        is_away_play = away_description != ""
        rows.append(
            {
                "period": period_number(current_period),
                "period_type": period_type(current_period),
                "remaining_seconds_in_period": remaining_seconds(timestamp),
                "relevant_team": away_team if is_away_play else home_team_abbreviation,
                "away_team": away_team,
                "home_team": home_team_abbreviation,
                "away_score": scores,
                "home_score": scores,
                "description": away_description if is_away_play else home_description,
            }
        )
    return rows


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


def parse_team_box_score(selector: Selector) -> list[dict[str, Any]]:
    combined_team_totals: list[dict[str, Any]] = []
    for table in selector.css('table.stats_table[id$="-game-basic"]'):
        table_id = table.attrib.get("id", "")
        if not table_id.startswith("box-"):
            continue
        team_abbreviation = table_id.removeprefix("box-").removesuffix("-game-basic")
        footer = table.css("tfoot")
        if not footer:
            continue
        rows = raw_rows_from_table(footer[0])
        if not rows:
            continue
        row = rows[0][0]
        row["team_name_abbr"] = team_name_from_abbreviation(team_abbreviation)
        combined_team_totals.append(row)

    if len(combined_team_totals) < 2:
        raise ValueError(f"Expected 2 team totals in box score page, got {len(combined_team_totals)}")

    first_team_totals, second_team_totals = combined_team_totals[:2]
    first_team_totals["outcome"] = score_outcome(first_team_totals["pts"], second_team_totals["pts"])
    second_team_totals["outcome"] = score_outcome(second_team_totals["pts"], first_team_totals["pts"])
    return [first_team_totals, second_team_totals]


def parse_search_rows(selector: Selector) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in selector.css("div#searches div#players div.search-item"):
        link = result.css("div.search-item-name a")
        if not link:
            continue
        rows.append(
            {
                "name": search_result_name(cell_text(link[0])),
                "identifier": resource_identifier(link[0].attrib.get("href")),
                "leagues": cell_text(result.css("div.search-item-league")),
            }
        )
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
