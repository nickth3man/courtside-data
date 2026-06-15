"""Row schemas for box-score Basketball-Reference endpoints.

Box-score tables use ``data-stat="mp"`` to carry an "MM:SS" playing-time
string.  :class:`SecondsPlayed` ports that into a total-seconds ``int`` so
consumers can compare or aggregate without re-parsing the original string.

The custom fetchers (Wave 3) own the orchestration that injects the
player ``slug`` (extracted from the ``data-append-csv`` cell attribute,
not a ``data-stat``) for the per-day leaders endpoint.
"""

from __future__ import annotations

from pydantic import AliasChoices, Field

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRDate,
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    LocationField,
    OutcomeField,
    SecondsPlayedOrNone,
    StrOrNone,
    TeamField,
    TeamNameField,
)

# ── Private stat-block mixins (box-score shape) ─────────────────────────


class _BoxScoreCountingStats:
    """Counting stats common to player box-score tables.

    Every ``data-stat`` here is shared between the per-day leaders
    table and the per-game game log; the ``mp`` cell on these tables
    is an "MM:SS" string that :class:`SecondsPlayed` converts to
    total seconds.  The team-row variant
    (:class:`_BoxScoreTeamCountingStats` below) overrides ``mp`` to
    accept a bare integer total instead.
    """

    seconds_played: SecondsPlayedOrNone = Field(default=None, validation_alias="mp")
    made_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg")
    attempted_field_goals: BRIntOrNone = Field(default=None, validation_alias="fga")
    made_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3")
    attempted_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3a")
    made_free_throws: BRIntOrNone = Field(default=None, validation_alias="ft")
    attempted_free_throws: BRIntOrNone = Field(default=None, validation_alias="fta")
    offensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="orb")
    defensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="drb")
    total_rebounds: BRIntOrNone = Field(default=None, validation_alias="trb")
    assists: BRIntOrNone = Field(default=None, validation_alias="ast")
    steals: BRIntOrNone = Field(default=None, validation_alias="stl")
    blocks: BRIntOrNone = Field(default=None, validation_alias="blk")
    turnovers: BRIntOrNone = Field(default=None, validation_alias="tov")
    personal_fouls: BRIntOrNone = Field(default=None, validation_alias="pf")
    points: BRIntOrNone = Field(default=None, validation_alias="pts")
    game_score: BRFloatOrNone = Field(default=None, validation_alias="game_score")


class _BoxScoreTeamCountingStats:
    """Counting stats for the team box-score (assembled) variant.

    Differs from :class:`_BoxScoreCountingStats` in two ways: ``mp`` is
    a bare-integer total (not an "MM:SS" string) and ``points`` is the
    canonical Python name (vs. ``points`` in the player shape — the
    legacy column contract already uses ``points`` here, so no rename).
    """

    minutes_played: BRInt = Field(validation_alias="mp")
    made_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg")
    attempted_field_goals: BRIntOrNone = Field(default=None, validation_alias="fga")
    made_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3")
    attempted_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3a")
    made_free_throws: BRIntOrNone = Field(default=None, validation_alias="ft")
    attempted_free_throws: BRIntOrNone = Field(default=None, validation_alias="fta")
    offensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="orb")
    defensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="drb")
    total_rebounds: BRIntOrNone = Field(default=None, validation_alias="trb")
    assists: BRIntOrNone = Field(default=None, validation_alias="ast")
    steals: BRIntOrNone = Field(default=None, validation_alias="stl")
    blocks: BRIntOrNone = Field(default=None, validation_alias="blk")
    turnovers: BRIntOrNone = Field(default=None, validation_alias="tov")
    personal_fouls: BRIntOrNone = Field(default=None, validation_alias="pf")
    points: BRIntOrNone = Field(default=None, validation_alias="pts")


class _BoxScorePctStats:
    """Shooting percentage columns that use BR's ``_pct`` data-stat keys."""

    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    made_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2")
    attempted_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2a")
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")


# ── Per-day leaders (``friv/dailyleaders.cgi``) ──────────────────────────


class PlayerBoxScoreRow(BRRow, _BoxScoreCountingStats, _BoxScorePctStats):
    """Row from a daily-leaders page.

    Includes the player ``slug`` (from the cell's ``data-append-csv``
    attribute, injected by the custom fetcher) and a full name, plus
    team/location/opponent/outcome context and the basic box-score stat
    block. ``plus_minus`` is the per-game plus/minus — distinct from the
    "raw score margin" that appears on the schedule.
    """

    slug: str = Field(validation_alias="slug")
    name: str = Field(validation_alias="player")
    team: TeamField = Field(validation_alias=AliasChoices("team_id", "team_name_abbr"))
    location: LocationField = Field(validation_alias="game_location")
    opponent: TeamField = Field(validation_alias=AliasChoices("opp_id", "opp_name_abbr"))
    outcome: OutcomeField = Field(validation_alias="game_result")
    plus_minus: BRIntOrNone = Field(default=None, validation_alias="plus_minus")


register("player_box_scores", PlayerBoxScoreRow)


# ── Player game logs (regular season + playoffs) ─────────────────────────


class _PlayerSeasonBoxScoreRow(BRRow, _BoxScoreCountingStats, _BoxScorePctStats):
    """Shared base for the per-game regular-season and playoff game logs.

    ``active`` is derived upstream from the ``is_starter`` cell's ``colspan``
    attribute; the custom fetcher injects a boolean and this model treats
    it as the source of truth. ``date_game`` is the historical BR
    ``data-stat``; some fixtures expose it as ``date``.
    """

    active: bool = Field(validation_alias="active")
    date: BRDate = Field(validation_alias=AliasChoices("date_game", "date"))
    player_game_number_career: BRIntOrNone = Field(default=None, validation_alias="player_game_num_career")
    team_game_number_season: BRIntOrNone = Field(default=None, validation_alias="team_game_num_season")
    is_starter: StrOrNone = Field(default=None, validation_alias="is_starter")
    points_scored: BRIntOrNone = Field(default=None, validation_alias=AliasChoices("pts", "points_scored"))
    team: TeamField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    location: LocationField = Field(validation_alias="game_location")
    opponent: TeamField = Field(validation_alias=AliasChoices("opp_name_abbr", "opp_id"))
    outcome: OutcomeField = Field(validation_alias="game_result")
    plus_minus: BRIntOrNone = Field(default=None, validation_alias="plus_minus")


class RegularSeasonPlayerBoxScoreRow(_PlayerSeasonBoxScoreRow):
    """Row from a player's regular-season game log (``player_game_log_reg``)."""

    pass


register("regular_season_player_box_scores", RegularSeasonPlayerBoxScoreRow)


class PlayoffPlayerBoxScoreRow(_PlayerSeasonBoxScoreRow):
    """Row from a player's playoff game log (``player_game_log_post``)."""

    pass


register("playoff_player_box_scores", PlayoffPlayerBoxScoreRow)


# ── Team box scores (per-day, assembled from individual game totals) ────


class TeamBoxScoreRow(BRRow, _BoxScoreTeamCountingStats, _BoxScorePctStats):
    """Row from a daily team box-score listing (assembled by the custom
    fetcher from individual game footer rows).

    The team-level ``mp`` cell holds a bare integer (the total team
    minutes summed across players), exposed as :attr:`minutes_played` to
    match the legacy column contract.
    """

    team: TeamNameField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    outcome: OutcomeField | None = Field(default=None, validation_alias="outcome")
    player: StrOrNone = Field(default=None, validation_alias="player")
    game_score: BRFloatOrNone = Field(default=None, validation_alias="game_score")
    plus_minus: BRIntOrNone = Field(default=None, validation_alias="plus_minus")


register("team_box_scores", TeamBoxScoreRow)
