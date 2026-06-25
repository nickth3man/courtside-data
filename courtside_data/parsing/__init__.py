"""Convenience facade for parsing helpers.

The concrete parsing modules import each other during startup, and the debug
provenance layer imports ``courtside_data.parsing._table_shared`` very early.
Keep this package facade lazy so those direct imports do not pull in the
generic-table or workflow-compatibility dispatchers while provenance is still
initialising.
"""

from __future__ import annotations

from importlib import import_module

_LAZY_EXPORTS = {
    "CustomEndpointHandler": ("courtside_data.parsing.custom", "CustomEndpointHandler"),
    "GenericEndpointHandler": ("courtside_data.parsing.generic", "GenericEndpointHandler"),
    "GenericTable": ("courtside_data.parsing.tables", "GenericTable"),
    "GenericTableRow": ("courtside_data.parsing.tables", "GenericTableRow"),
    "cell_text": ("courtside_data.parsing.cells", "cell_text"),
    "dispatch_custom_endpoint": ("courtside_data.parsing.custom", "dispatch_custom_endpoint"),
    "division_value": ("courtside_data.parsing.cells", "division_value"),
    "extract_commented_table": ("courtside_data.parsing.tables", "extract_commented_table"),
    "extract_pattern_from_href": ("courtside_data.parsing.cells", "extract_pattern_from_href"),
    "find_table": ("courtside_data.parsing.generic", "find_table"),
    "find_table_by_id": ("courtside_data.parsing.generic", "find_table_by_id"),
    "is_combined_team": ("courtside_data.parsing.cells", "is_combined_team"),
    "parse_friv_playoff_outcomes_row": ("courtside_data.parsing.rows", "parse_friv_playoff_outcomes_row"),
    "parse_play_by_play_rows": ("courtside_data.parsing.rows", "parse_play_by_play_rows"),
    "parse_player_direct_search_results": ("courtside_data.parsing.rows", "parse_player_direct_search_results"),
    "parse_playoff_bracket": ("courtside_data.parsing.rows", "parse_playoff_bracket"),
    "parse_search_pagination_url": ("courtside_data.parsing.rows", "parse_search_pagination_url"),
    "parse_search_rows": ("courtside_data.parsing.rows", "parse_search_rows"),
    "parse_standings": ("courtside_data.parsing.rows", "parse_standings"),
    "parse_team_box_score": ("courtside_data.parsing.rows", "parse_team_box_score"),
    "parse_transaction_list": ("courtside_data.parsing.tables", "parse_transaction_list"),
    "pattern_from_gameslist_spans": ("courtside_data.parsing.cells", "pattern_from_gameslist_spans"),
    "pattern_to_games_played": ("courtside_data.parsing.cells", "pattern_to_games_played"),
    "period_number": ("courtside_data.parsing.cells", "period_number"),
    "period_type": ("courtside_data.parsing.cells", "period_type"),
    "raw_rows_from_table": ("courtside_data.parsing.rows", "raw_rows_from_table"),
    "remaining_locations_from_text": ("courtside_data.parsing.cells", "remaining_locations_from_text"),
    "remaining_seconds": ("courtside_data.parsing.cells", "remaining_seconds"),
    "remaining_text_from_gameslist": ("courtside_data.parsing.cells", "remaining_text_from_gameslist"),
    "require_slug": ("courtside_data.parsing.cells", "require_slug"),
    "resolve_pbp_game_url_path": ("courtside_data.parsing.rows", "resolve_pbp_game_url_path"),
    "resource_identifier": ("courtside_data.parsing.cells", "resource_identifier"),
    "score_outcome": ("courtside_data.parsing.cells", "score_outcome"),
    "search_result_name": ("courtside_data.parsing.cells", "search_result_name"),
    "slug_from_metadata": ("courtside_data.parsing.cells", "slug_from_metadata"),
    "standings_team_value": ("courtside_data.parsing.cells", "standings_team_value"),
    "team_abbreviation_from_name": ("courtside_data.parsing.cells", "team_abbreviation_from_name"),
    "team_name_from_abbreviation": ("courtside_data.parsing.cells", "team_name_from_abbreviation"),
    "xpath_literal": ("courtside_data.parsing.generic", "xpath_literal"),
}

__all__ = list(_LAZY_EXPORTS)


def __getattr__(name: str) -> object:
    """Load facade exports on first access."""
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = _LAZY_EXPORTS[name]
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value
