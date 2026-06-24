"""Standings row parsers for the Eastern and Western conference tables."""

from __future__ import annotations

from typing import Any

from parsel import Selector

from courtside_data.data import DIVISIONS_TO_CONFERENCES, Division
from courtside_data.parsing.cells import (
    cell_text,
    division_value,
    standings_team_value,
)


def parse_standings_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    standings: list[dict[str, Any]] = []
    ignored_row_reason_counts: dict[str, int] = {}
    standings_section_count = 0
    conferences: set[Any] = set()
    divisions: set[Any] = set()

    def ignore(reason: str) -> None:
        ignored_row_reason_counts[reason] = ignored_row_reason_counts.get(reason, 0) + 1

    for table_id in ("divs_standings_E", "divs_standings_W"):
        table = selector.css(f"table#{table_id}")
        if not table:
            ignore("missing_table")
            continue
        standings_section_count += 1
        current_division: Division | None = None
        for row in table[0].css("tbody tr"):
            classes = row.attrib.get("class", "").split()
            if "thead" in classes:
                div_val = division_value(cell_text(row.css("th")))
                current_division = Division(div_val) if div_val is not None else None
                if current_division is not None:
                    divisions.add(current_division)
                    conferences.add(DIVISIONS_TO_CONFERENCES[current_division])
                else:
                    ignore("division_header")
                continue
            team = cell_text(row.css('[data-stat="team_name"]'))
            if not team:
                ignore("missing_team")
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

    stats = {
        "standings_section_count": standings_section_count,
        "conference_count": len(conferences),
        "division_count": len(divisions),
        "team_count": len(standings),
        "ignored_row_reason_counts": ignored_row_reason_counts,
    }
    return standings, stats


def parse_standings(selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_standings_with_stats(selector)
    return rows
