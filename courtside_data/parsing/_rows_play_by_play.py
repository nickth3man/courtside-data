"""Play-by-play row parsers for the ``#pbp`` table on box-score pages."""

from __future__ import annotations

from typing import Any

from parsel import Selector

from courtside_data.parsing.cells import (
    cell_text,
    period_number,
    period_type,
    remaining_seconds,
)


def resolve_pbp_game_url_path(boxscores_selector: Selector, abbr: str) -> str | None:
    for path in [link.attrib["href"] for link in boxscores_selector.css("td.gamelink a")]:
        if path.endswith((f"0{abbr}.html", f"1{abbr}.html")):
            return path
    return None


def parse_play_by_play_rows_with_stats(
    selector: Selector,
    away_team: str,
    home_team_abbreviation: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    current_period = 0
    rows: list[dict[str, Any]] = []
    ignored_reasons: dict[str, int] = {}
    score_event_count = 0
    substitution_event_count = 0

    def ignore(reason: str) -> None:
        ignored_reasons[reason] = ignored_reasons.get(reason, 0) + 1

    for row in selector.css("table#pbp tr"):
        cells = row.css("td, th")
        if not cells:
            ignore("blank_row")
            continue
        timestamp_cell = cells[0]
        if timestamp_cell.attrib.get("colspan") == "6":
            current_period += 1
            ignore("period_header")
            continue
        if len(cells) < 2 or cells[1].attrib.get("colspan") == "5" or timestamp_cell.attrib.get("aria-label") == "Time":
            ignore("parser_excluded")
            continue

        timestamp = cell_text(timestamp_cell)
        away_description = cell_text(cells[1]) if len(cells) == 6 else ""
        home_description = cell_text(cells[5]) if len(cells) == 6 else ""
        scores = cell_text(cells[3]) if len(cells) == 6 else ""
        is_away_play = away_description != ""
        description = away_description if is_away_play else home_description
        if scores:
            score_event_count += 1
        lowered_description = description.lower()
        if " enters " in lowered_description or " enters for " in lowered_description:
            substitution_event_count += 1
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
                "description": description,
            }
        )

    stats = {
        "parsed_event_count": len(rows),
        "ignored_event_count": sum(ignored_reasons.values()),
        "ignored_event_reason_counts": ignored_reasons,
        "period_count": current_period,
        "score_event_count": score_event_count,
        "substitution_event_count": substitution_event_count,
    }
    return rows, stats


def parse_play_by_play_rows(selector: Selector, away_team: str, home_team_abbreviation: str) -> list[dict[str, Any]]:
    rows, _ = parse_play_by_play_rows_with_stats(selector, away_team, home_team_abbreviation)
    return rows
