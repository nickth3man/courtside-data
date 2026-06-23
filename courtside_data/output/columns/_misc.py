"""CSV column contracts for endpoints that don't fit a dedicated domain file.

The play-by-play table is structural rather than ``data-stat`` driven, the
schedule table is a small shared layout, and the search results page is a
div-based listing. Each is just a handful of column names, so they are
grouped here instead of in single-purpose modules.
"""

PLAY_BY_PLAY_COLUMN_NAMES = [
    "period",
    "period_type",
    "remaining_seconds_in_period",
    "relevant_team",
    "away_team",
    "home_team",
    "away_score",
    "home_score",
    "description",
]

SCHEDULE_COLUMN_NAMES = [
    "start_time",
    "date_game",
    "game_start_time",
    "away_team",
    "away_team_score",
    "home_team",
    "home_team_score",
    "box_score_text",
    "overtimes",
    "attendance",
    "game_duration",
    "arena_name",
    "game_remarks",
]

SEARCH_RESULTS_COLUMN_NAMES = [
    "name",
    "identifier",
    "leagues",
]
