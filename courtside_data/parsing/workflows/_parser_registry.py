"""Stable parser ids used by executable workflow steps."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from parsel import Selector

from courtside_data.parsing import rows
from courtside_data.parsing.custom._common import (
    _player_season_box_score_rows_with_stats,
    _player_totals_rows_with_stats,
)

SelectorParser = Callable[..., list[dict[str, Any]] | tuple[list[dict[str, Any]], dict[str, Any]]]


def parse_player_game_log_table(
    table: Selector,
    *,
    include_inactive_games: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Parse one player game-log table and return rows plus stats."""
    return _player_season_box_score_rows_with_stats(table, include_inactive_games=include_inactive_games)


def parse_player_totals_page(
    selector: Selector,
    *,
    table_id: str,
    include_combined: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Parse one league-wide player totals page and return rows plus stats."""
    return _player_totals_rows_with_stats(selector, table_id, include_combined=include_combined)


def parse_awards_voting_table(table: Selector) -> list[dict[str, Any]]:
    """Parse raw award voting rows from one selected table."""
    return [row for row, _ in rows.raw_rows_from_table(table)]


def parse_playoff_bracket_table(table: Selector) -> list[dict[str, Any]]:
    """Parse playoff bracket rows from the selected bracket table."""
    return rows.parse_playoff_bracket(table)


def parse_friv_playoff_outcomes_table(table: Selector) -> list[dict[str, Any]]:
    """Parse one Friv seven-game playoff outcomes table."""
    return [rows.parse_friv_playoff_outcomes_row(row) for row in table.css("tbody tr:not(.thead)") if row.css("td")]


PARSER_REGISTRY: dict[str, SelectorParser] = {
    "awards_voting_table": parse_awards_voting_table,
    "friv_playoff_outcomes_table": parse_friv_playoff_outcomes_table,
    "player_game_log_table": parse_player_game_log_table,
    "player_totals_page": parse_player_totals_page,
    "playoff_bracket_table": parse_playoff_bracket_table,
}
