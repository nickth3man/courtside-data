"""CSV column contracts for box-score Basketball-Reference endpoints."""

BOX_SCORE_STAT_COLUMN_NAMES = [
    "field_goal_percentage",
    "three_point_field_goal_percentage",
    "free_throw_percentage",
    "made_two_point_field_goals",
    "attempted_two_point_field_goals",
    "two_point_field_goal_percentage",
    "effective_field_goal_percentage",
    "seconds_played",
    "made_field_goals",
    "attempted_field_goals",
    "made_three_point_field_goals",
    "attempted_three_point_field_goals",
    "made_free_throws",
    "attempted_free_throws",
    "offensive_rebounds",
    "defensive_rebounds",
    "total_rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "personal_fouls",
    "points",
    "game_score",
]

BOX_SCORE_COLUMN_NAMES = [
    *BOX_SCORE_STAT_COLUMN_NAMES,
    "slug",
    "name",
    "team",
    "location",
    "opponent",
    "outcome",
    "plus_minus",
]

PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES = [
    *BOX_SCORE_STAT_COLUMN_NAMES,
    "active",
    "date",
    "player_game_number_career",
    "team_game_number_season",
    "is_starter",
    "points_scored",
    "team",
    "location",
    "opponent",
    "outcome",
    "plus_minus",
]

TEAM_BOX_SCORES_COLUMN_NAMES = [
    "field_goal_percentage",
    "three_point_field_goal_percentage",
    "free_throw_percentage",
    "made_two_point_field_goals",
    "attempted_two_point_field_goals",
    "two_point_field_goal_percentage",
    "effective_field_goal_percentage",
    "minutes_played",
    "made_field_goals",
    "attempted_field_goals",
    "made_three_point_field_goals",
    "attempted_three_point_field_goals",
    "made_free_throws",
    "attempted_free_throws",
    "offensive_rebounds",
    "defensive_rebounds",
    "total_rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "personal_fouls",
    "points",
    "team",
    "outcome",
    "player",
    "game_score",
    "plus_minus",
]


# ── Per-game box-score readers (SCAFFOLD — PDCA Cycle 1) ─────────────────
# CSV column contracts for the six forward-declared per-game box-score
# readers. These lists are NOT yet wired to any registered endpoint (the
# endpoints are deferred to PDCA Cycle 2 alongside the per-game-page parsers
# and offline fixtures, because the registry-count and coverage canaries
# require schemas, endpoints, parsers, and fixtures to land together).
# See courtside_data/schemas/boxscores.py for the matching row models and
# the full SCAFFOLD note.

BOX_SCORE_PLAYER_ADVANCED_COLUMN_NAMES = [
    "true_shooting_percentage",
    "effective_field_goal_percentage",
    "three_point_attempt_rate",
    "free_throw_rate",
    "offensive_rebound_percentage",
    "defensive_rebound_percentage",
    "total_rebound_percentage",
    "assist_percentage",
    "steal_percentage",
    "block_percentage",
    "turnover_percentage",
    "usage_percentage",
    "offensive_rating",
    "defensive_rating",
    "box_plus_minus",
    "seconds_played",
    "slug",
    "name",
    "team",
    "opponent",
    "plus_minus",
]

BOX_SCORE_TEAM_FOUR_FACTORS_COLUMN_NAMES = [
    "team",
    "pace",
    "effective_field_goal_percentage",
    "turnover_percentage",
    "offensive_rebound_percentage",
    "free_throw_attempt_rate",
    "offensive_rating",
]

BOX_SCORE_LINE_SCORE_COLUMN_NAMES = [
    "team",
    "first_quarter_points",
    "second_quarter_points",
    "third_quarter_points",
    "fourth_quarter_points",
    "total_points",
]

BOX_SCORE_PLAYER_QUARTER_SPLITS_COLUMN_NAMES = [
    *BOX_SCORE_STAT_COLUMN_NAMES,
    "slug",
    "name",
    "team",
    "opponent",
]

BOX_SCORE_GAME_INFO_COLUMN_NAMES = [
    "game_date",
    "home_team",
    "away_team",
    "home_team_score",
    "away_team_score",
    "arena",
    "attendance",
    "duration",
    "tip_off",
    "officials",
    "inactive_home",
    "inactive_away",
]

BOX_SCORE_PLAYER_BASIC_COLUMN_NAMES = [
    *BOX_SCORE_STAT_COLUMN_NAMES,
    "slug",
    "name",
    "team",
    "opponent",
    "location",
    "outcome",
    "is_starter",
    "status",
    "plus_minus",
]
