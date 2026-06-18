"""Extraction-layer siblings: table primitive, cell helpers, row parsers,
and the generic/custom endpoint dispatchers.

These modules cluster the pure HTML/value parsing and table extraction that
sit between :mod:`courtside_data.http_service` and the per-domain client
functions. They are internal — not re-exported by the top-level
:mod:`courtside_data` facade — but their public symbols are listed here for
discoverability.
"""

from courtside_data.parsing.cells import (
    cell_text,
    division_value,
    extract_pattern_from_href,
    is_combined_team,
    pattern_from_gameslist_spans,
    pattern_to_games_played,
    period_number,
    period_type,
    remaining_locations_from_text,
    remaining_seconds,
    remaining_text_from_gameslist,
    require_slug,
    resource_identifier,
    score_outcome,
    search_result_name,
    slug_from_metadata,
    standings_team_value,
    team_abbreviation_from_name,
    team_name_from_abbreviation,
)
from courtside_data.parsing.custom import (
    CustomEndpointHandler,
    dispatch_custom_endpoint,
)
from courtside_data.parsing.generic import (
    GenericEndpointHandler,
    find_table,
    find_table_by_id,
    xpath_literal,
)
from courtside_data.parsing.rows import (
    parse_friv_playoff_outcomes_row,
    parse_play_by_play_rows,
    parse_player_direct_search_results,
    parse_playoff_bracket,
    parse_search_pagination_url,
    parse_search_rows,
    parse_standings,
    parse_team_box_score,
    raw_rows_from_table,
    resolve_pbp_game_url_path,
)
from courtside_data.parsing.tables import (
    GenericTable,
    GenericTableRow,
    extract_commented_table,
    parse_transaction_list,
)

__all__ = [
    "CustomEndpointHandler",
    "GenericEndpointHandler",
    "GenericTable",
    "GenericTableRow",
    "cell_text",
    "dispatch_custom_endpoint",
    "division_value",
    "extract_commented_table",
    "extract_pattern_from_href",
    "find_table",
    "find_table_by_id",
    "is_combined_team",
    "parse_friv_playoff_outcomes_row",
    "parse_play_by_play_rows",
    "parse_player_direct_search_results",
    "parse_playoff_bracket",
    "parse_search_pagination_url",
    "parse_search_rows",
    "parse_standings",
    "parse_team_box_score",
    "parse_transaction_list",
    "pattern_from_gameslist_spans",
    "pattern_to_games_played",
    "period_number",
    "period_type",
    "raw_rows_from_table",
    "remaining_locations_from_text",
    "remaining_seconds",
    "remaining_text_from_gameslist",
    "require_slug",
    "resolve_pbp_game_url_path",
    "resource_identifier",
    "score_outcome",
    "search_result_name",
    "slug_from_metadata",
    "standings_team_value",
    "team_abbreviation_from_name",
    "team_name_from_abbreviation",
    "xpath_literal",
]
