"""Box-score row parsers (team totals and daily-leader player rows)."""

from __future__ import annotations

from typing import Any

from parsel import Selector

from courtside_data.parsing._rows_common import raw_rows_from_table
from courtside_data.parsing.cells import (
    require_slug,
    score_outcome,
    slug_from_metadata,
    team_name_from_abbreviation,
)
from courtside_data.parsing.workflow_parsers._diagnostics import (
    IGNORE_EMPTY_TABLE,
    IGNORE_MISSING_FOOTER,
    increment_ignored,
)


def parse_team_box_score_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return team totals for one game page plus parser diagnostics."""
    ignored_row_reason_counts: dict[str, int] = {}
    combined_team_totals: list[dict[str, Any]] = []
    basic_table_count = 0
    advanced_table_count = 0
    empty_table_count = 0

    for table in selector.css('table.stats_table[id^="box-"]'):
        table_id = table.attrib.get("id", "")
        if table_id.endswith("-game-advanced"):
            advanced_table_count += 1
        elif table_id.endswith("-game-basic"):
            basic_table_count += 1

    stat_table_count = basic_table_count + advanced_table_count

    for table in selector.css('table.stats_table[id$="-game-basic"]'):
        table_id = table.attrib.get("id", "")
        if not table_id.startswith("box-"):
            continue
        team_abbreviation = table_id.removeprefix("box-").removesuffix("-game-basic")
        footer = table.css("tfoot")
        if not footer:
            increment_ignored(ignored_row_reason_counts, IGNORE_MISSING_FOOTER)
            continue
        footer_rows = raw_rows_from_table(footer[0])
        if not footer_rows:
            empty_table_count += 1
            increment_ignored(ignored_row_reason_counts, IGNORE_EMPTY_TABLE)
            continue
        row = footer_rows[0][0]
        row["team_name_abbr"] = team_name_from_abbreviation(team_abbreviation)
        combined_team_totals.append(row)

    if len(combined_team_totals) < 2:
        raise ValueError(f"Expected 2 team totals in box score page, got {len(combined_team_totals)}")

    first_team_totals, second_team_totals = combined_team_totals[:2]
    first_team_totals["outcome"] = score_outcome(first_team_totals["pts"], second_team_totals["pts"])
    second_team_totals["outcome"] = score_outcome(second_team_totals["pts"], first_team_totals["pts"])
    parsed_rows = [first_team_totals, second_team_totals]

    stats = {
        "game_count": 1,
        "team_count": len(parsed_rows),
        "stat_table_count": stat_table_count,
        "basic_table_count": basic_table_count,
        "advanced_table_count": advanced_table_count,
        "empty_table_count": empty_table_count,
        "ignored_row_reason_counts": ignored_row_reason_counts,
    }
    return parsed_rows, stats


def parse_team_box_score(selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_team_box_score_with_stats(selector)
    return rows


def parse_player_box_scores_from_table_with_stats(
    table_selector: Selector,
    *,
    endpoint_name: str = "player_box_scores",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return daily-leader player rows and parser diagnostics from ``table#stats``."""
    raw_rows = list(raw_rows_from_table(table_selector))
    parsed_rows: list[dict[str, Any]] = []
    for row_index, (row, metadata) in enumerate(raw_rows):
        row["slug"] = slug_from_metadata(metadata, "player")
        require_slug(endpoint_name, row, row_index)
        parsed_rows.append(row)

    raw_column_count = len(raw_rows[0][0]) if raw_rows else 0
    stats = {
        "player_count": len(parsed_rows),
        "raw_row_count": len(raw_rows),
        "raw_column_count": raw_column_count,
        "stat_table_count": 1,
        "basic_table_count": 1,
        "advanced_table_count": 0,
        "selected_table_id": "stats",
    }
    return parsed_rows, stats


def parse_player_box_scores_from_table(table_selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_player_box_scores_from_table_with_stats(table_selector)
    return rows
