"""Shared CSV column primitives reused across multiple endpoint contracts.

``SHARED_COLUMN_NAMES`` is the base of both ``BOX_SCORE_COLUMN_NAMES`` and
``PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES`` in
:mod:`courtside_data.output.columns.boxscores`, so it lives here as the
single source of truth.
"""

SHARED_COLUMN_NAMES = [
    "team",
    "location",
    "opponent",
    "outcome",
    "seconds_played",
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
    "game_score",
]
