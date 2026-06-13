from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from courtside_data.schemas._fields import (
    BRFloatOrNone,
    BRIntOrNone,
    BRPercentage,
    PositionsField,
    SecondsPlayed,
    TeamField,
)


class BRRow(BaseModel):
    """Base model for every Basketball-Reference row schema.

    - ``populate_by_name=True`` lets callers pass values by alias or by the
      stable Python attribute name.
    - ``extra="ignore"`` keeps the model resilient to new data-stat columns BR
      adds without warning.
    - ``str_strip_whitespace=True`` removes incidental padding.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore", str_strip_whitespace=True)

    def __getitem__(self, key: str) -> object:
        return getattr(self, key)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            dumped = self.model_dump(mode="python")
            return all(dumped.get(key) == value for key, value in other.items())
        return super().__eq__(other)


class BasicBoxScoreStats:
    """Counting stats shared by player and team box score tables."""

    seconds_played: SecondsPlayed = 0
    made_field_goals: BRIntOrNone = None
    attempted_field_goals: BRIntOrNone = None
    made_three_point_field_goals: BRIntOrNone = None
    attempted_three_point_field_goals: BRIntOrNone = None
    made_free_throws: BRIntOrNone = None
    attempted_free_throws: BRIntOrNone = None
    offensive_rebounds: BRIntOrNone = None
    defensive_rebounds: BRIntOrNone = None
    assists: BRIntOrNone = None
    steals: BRIntOrNone = None
    blocks: BRIntOrNone = None
    turnovers: BRIntOrNone = None
    personal_fouls: BRIntOrNone = None
    points: BRIntOrNone = None
    plus_minus: BRIntOrNone = None


class TotalStats:
    """Season/career totals-style counting stats (fg, fga, orb, drb, ...)."""

    games_played: BRIntOrNone = Field(validation_alias="games")
    games_started: BRIntOrNone = Field(validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(validation_alias="mp")
    made_field_goals: BRIntOrNone = Field(validation_alias="fg")
    attempted_field_goals: BRIntOrNone = Field(validation_alias="fga")
    made_three_point_field_goals: BRIntOrNone = Field(validation_alias="fg3")
    attempted_three_point_field_goals: BRIntOrNone = Field(validation_alias="fg3a")
    made_free_throws: BRIntOrNone = Field(validation_alias="ft")
    attempted_free_throws: BRIntOrNone = Field(validation_alias="fta")
    offensive_rebounds: BRIntOrNone = Field(validation_alias="orb")
    defensive_rebounds: BRIntOrNone = Field(validation_alias="drb")
    total_rebounds: BRIntOrNone = Field(validation_alias="trb")
    assists: BRIntOrNone = Field(validation_alias="ast")
    steals: BRIntOrNone = Field(validation_alias="stl")
    blocks: BRIntOrNone = Field(validation_alias="blk")
    turnovers: BRIntOrNone = Field(validation_alias="tov")
    personal_fouls: BRIntOrNone = Field(validation_alias="pf")
    points: BRIntOrNone = Field(validation_alias="pts")


class PerGameStats:
    """Per-game stat block matching the ``LEAGUE_PER_GAME_COLUMN_NAMES`` layout.

    Raw ``data-stat`` attributes are used as ``validation_alias`` values; the
    Python attribute names are the stable verbose names used throughout the
    legacy output layer.
    """

    name_display: str | None = Field(default=None, validation_alias="name_display")
    positions: PositionsField = Field(validation_alias="pos")
    age: BRIntOrNone = Field(validation_alias="age")
    team: TeamField | None = Field(default=None, validation_alias="team_name_abbr")
    games_played: BRIntOrNone = Field(validation_alias="games")
    games_started: BRIntOrNone = Field(validation_alias="games_started")
    minutes_played_per_game: BRFloatOrNone = Field(validation_alias="mp_per_g")
    made_field_goals_per_game: BRFloatOrNone = Field(validation_alias="fg_per_g")
    attempted_field_goals_per_game: BRFloatOrNone = Field(validation_alias="fga_per_g")
    field_goal_percentage: BRPercentage = Field(validation_alias="fg_pct")
    made_three_point_field_goals_per_game: BRFloatOrNone = Field(validation_alias="fg3_per_g")
    attempted_three_point_field_goals_per_game: BRFloatOrNone = Field(validation_alias="fg3a_per_g")
    three_point_field_goal_percentage: BRPercentage = Field(validation_alias="fg3_pct")
    made_two_point_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fg2_per_g")
    attempted_two_point_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fg2a_per_g")
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    effective_field_goal_percentage: BRPercentage = Field(validation_alias="efg_pct")
    made_free_throws_per_game: BRFloatOrNone = Field(validation_alias="ft_per_g")
    attempted_free_throws_per_game: BRFloatOrNone = Field(validation_alias="fta_per_g")
    free_throw_percentage: BRPercentage = Field(validation_alias="ft_pct")
    offensive_rebounds_per_game: BRFloatOrNone = Field(validation_alias="orb_per_g")
    defensive_rebounds_per_game: BRFloatOrNone = Field(validation_alias="drb_per_g")
    total_rebounds_per_game: BRFloatOrNone = Field(validation_alias="trb_per_g")
    assists_per_game: BRFloatOrNone = Field(validation_alias="ast_per_g")
    steals_per_game: BRFloatOrNone = Field(validation_alias="stl_per_g")
    blocks_per_game: BRFloatOrNone = Field(validation_alias="blk_per_g")
    turnovers_per_game: BRFloatOrNone = Field(validation_alias="tov_per_g")
    personal_fouls_per_game: BRFloatOrNone = Field(validation_alias="pf_per_g")
    points_per_game: BRFloatOrNone = Field(validation_alias="pts_per_g")
