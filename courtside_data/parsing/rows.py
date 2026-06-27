"""Domain-specific row parsers (re-export facade)."""

from courtside_data.parsing._rows_boxscores import (
    parse_box_score_game_info,
    parse_box_score_game_info_with_stats,
    parse_box_score_line_score,
    parse_box_score_line_score_with_stats,
    parse_box_score_player_advanced,
    parse_box_score_player_advanced_with_stats,
    parse_box_score_player_basic,
    parse_box_score_player_basic_with_stats,
    parse_box_score_player_quarter_splits,
    parse_box_score_player_quarter_splits_with_stats,
    parse_box_score_team_four_factors,
    parse_box_score_team_four_factors_with_stats,
    parse_player_box_scores_from_table,
    parse_player_box_scores_from_table_with_stats,
    parse_team_box_score,
    parse_team_box_score_with_stats,
)
from courtside_data.parsing._rows_common import raw_rows_from_table
from courtside_data.parsing._rows_play_by_play import (
    parse_play_by_play_rows,
    parse_play_by_play_rows_with_stats,
    resolve_pbp_game_url_path,
)
from courtside_data.parsing._rows_playoffs import (
    parse_friv_playoff_outcomes_row,
    parse_playoff_bracket,
)
from courtside_data.parsing._rows_search import (
    parse_player_direct_search_results,
    parse_search_pagination_url,
    parse_search_rows,
    parse_search_rows_with_stats,
)
from courtside_data.parsing._rows_standings import parse_standings, parse_standings_with_stats

__all__ = [
    "parse_box_score_game_info",
    "parse_box_score_game_info_with_stats",
    "parse_box_score_line_score",
    "parse_box_score_line_score_with_stats",
    "parse_box_score_player_advanced",
    "parse_box_score_player_advanced_with_stats",
    "parse_box_score_player_basic",
    "parse_box_score_player_basic_with_stats",
    "parse_box_score_player_quarter_splits",
    "parse_box_score_player_quarter_splits_with_stats",
    "parse_box_score_team_four_factors",
    "parse_box_score_team_four_factors_with_stats",
    "parse_friv_playoff_outcomes_row",
    "parse_play_by_play_rows",
    "parse_play_by_play_rows_with_stats",
    "parse_player_box_scores_from_table",
    "parse_player_box_scores_from_table_with_stats",
    "parse_player_direct_search_results",
    "parse_playoff_bracket",
    "parse_search_pagination_url",
    "parse_search_rows",
    "parse_search_rows_with_stats",
    "parse_standings",
    "parse_standings_with_stats",
    "parse_team_box_score",
    "parse_team_box_score_with_stats",
    "raw_rows_from_table",
    "resolve_pbp_game_url_path",
]
