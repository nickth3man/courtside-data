"""Row schemas for league-wide player season totals endpoints."""

from __future__ import annotations

from pydantic import Field

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._blocks import TeamOrAggregateFieldOrNone
from courtside_data.schemas._fields import (
    BRFloatOrNone,
    BRIntOrNone,
    BRPercentage,
    PositionsField,
    StrOrNone,
    TeamField,
)


class PlayerSeasonTotalsRow(BRRow):
    """Row from the league-wide basic season totals table."""

    slug: str = Field(validation_alias="slug")
    name: str = Field(validation_alias="name_display")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team: TeamField = Field(validation_alias="team_name_abbr")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    made_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg")
    attempted_field_goals: BRIntOrNone = Field(default=None, validation_alias="fga")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    made_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3")
    attempted_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3a")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    made_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2")
    attempted_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2a")
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
    made_free_throws: BRIntOrNone = Field(default=None, validation_alias="ft")
    attempted_free_throws: BRIntOrNone = Field(default=None, validation_alias="fta")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    offensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="orb")
    defensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="drb")
    total_rebounds: BRIntOrNone = Field(default=None, validation_alias="trb")
    assists: BRIntOrNone = Field(default=None, validation_alias="ast")
    steals: BRIntOrNone = Field(default=None, validation_alias="stl")
    blocks: BRIntOrNone = Field(default=None, validation_alias="blk")
    turnovers: BRIntOrNone = Field(default=None, validation_alias="tov")
    personal_fouls: BRIntOrNone = Field(default=None, validation_alias="pf")
    points: BRIntOrNone = Field(default=None, validation_alias="pts")
    triple_doubles: BRIntOrNone = Field(default=None, validation_alias="tpl_dbl")
    awards: StrOrNone = Field(default=None, validation_alias="awards")


register("players_season_totals", PlayerSeasonTotalsRow)


class PlayerAdvancedSeasonTotalsRow(BRRow):
    """Row from the league-wide advanced season totals table."""

    slug: str = Field(validation_alias="slug")
    name: str = Field(validation_alias="name_display")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team: TeamOrAggregateFieldOrNone = Field(validation_alias="team_name_abbr")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    player_efficiency_rating: BRFloatOrNone = Field(default=None, validation_alias="per")
    true_shooting_percentage: BRPercentage = Field(default=None, validation_alias="ts_pct")
    three_point_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="fg3a_per_fga_pct")
    free_throw_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="fta_per_fga_pct")
    offensive_rebound_percentage: BRPercentage = Field(default=None, validation_alias="orb_pct")
    defensive_rebound_percentage: BRPercentage = Field(default=None, validation_alias="drb_pct")
    total_rebound_percentage: BRPercentage = Field(default=None, validation_alias="trb_pct")
    assist_percentage: BRPercentage = Field(default=None, validation_alias="ast_pct")
    steal_percentage: BRPercentage = Field(default=None, validation_alias="stl_pct")
    block_percentage: BRPercentage = Field(default=None, validation_alias="blk_pct")
    turnover_percentage: BRPercentage = Field(default=None, validation_alias="tov_pct")
    usage_percentage: BRPercentage = Field(default=None, validation_alias="usg_pct")
    offensive_win_shares: BRFloatOrNone = Field(default=None, validation_alias="ows")
    defensive_win_shares: BRFloatOrNone = Field(default=None, validation_alias="dws")
    win_shares: BRFloatOrNone = Field(default=None, validation_alias="ws")
    win_shares_per_48_minutes: BRFloatOrNone = Field(default=None, validation_alias="ws_per_48")
    offensive_box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="obpm")
    defensive_box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="dbpm")
    box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="bpm")
    value_over_replacement_player: BRFloatOrNone = Field(default=None, validation_alias="vorp")
    awards: StrOrNone = Field(default=None, validation_alias="awards")
    is_combined_totals: bool = Field(default=False, validation_alias="is_combined_totals")


register("players_advanced_season_totals", PlayerAdvancedSeasonTotalsRow)

# Preserve the historical introspection path while keeping the implementation
# in this focused module.
PlayerSeasonTotalsRow.__module__ = "courtside_data.schemas.players"
PlayerAdvancedSeasonTotalsRow.__module__ = "courtside_data.schemas.players"

__all__ = ["PlayerAdvancedSeasonTotalsRow", "PlayerSeasonTotalsRow"]
