"""CSV column contracts for box-score Basketball-Reference endpoints."""

from courtside_data.output.columns._common import SHARED_COLUMN_NAMES

BOX_SCORE_COLUMN_NAMES = ["slug", "name", *SHARED_COLUMN_NAMES, "plus_minus"]

PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES = ["active", "date", "points_scored", "plus_minus", *SHARED_COLUMN_NAMES]

TEAM_BOX_SCORES_COLUMN_NAMES = [
    "team",
    "minutes_played",
    "made_field_goals",
    "attempted_field_goals",
    "made_three_point_field_goals",
    "attempted_three_point_field_goals",
    "made_free_throws",
    "attempted_free_throws",
    "offensive_rebounds",
    "defensive_rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "personal_fouls",
    "points",
    "outcome",
]
