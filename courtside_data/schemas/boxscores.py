"""Row schemas for box-score Basketball-Reference endpoints.

Box-score tables use ``data-stat="mp"`` to carry an "MM:SS" playing-time
string.  :class:`SecondsPlayed` ports that into a total-seconds ``int`` so
consumers can compare or aggregate without re-parsing the original string.

Workflow parser steps inject the player ``slug`` (extracted from the
``data-append-csv`` cell attribute, not a ``data-stat``) for the per-day
leaders endpoint.
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
    CSV column contract already uses ``points`` here, so no rename).
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
    attribute, injected by the workflow parser) and a full name, plus
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
    attribute; the workflow parser injects a boolean and this model treats
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


register("regular_season_player_box_scores", RegularSeasonPlayerBoxScoreRow)


class PlayoffPlayerBoxScoreRow(_PlayerSeasonBoxScoreRow):
    """Row from a player's playoff game log (``player_game_log_post``)."""


register("playoff_player_box_scores", PlayoffPlayerBoxScoreRow)


# ── Team box scores (per-day, assembled from individual game totals) ────


class TeamBoxScoreRow(BRRow, _BoxScoreTeamCountingStats, _BoxScorePctStats):
    """Row from a daily team box-score listing.

    A workflow parser assembles these rows from individual game footer rows.

    The team-level ``mp`` cell holds a bare integer (the total team
    minutes summed across players), exposed as :attr:`minutes_played` to
    match the CSV column contract.
    """

    team: TeamNameField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    outcome: OutcomeField | None = Field(default=None, validation_alias="outcome")
    player: StrOrNone = Field(default=None, validation_alias="player")
    game_score: BRFloatOrNone = Field(default=None, validation_alias="game_score")
    plus_minus: BRIntOrNone = Field(default=None, validation_alias="plus_minus")


register("team_box_scores", TeamBoxScoreRow)


# ── Per-game box-score readers (SCAFFOLD — PDCA Cycle 1) ─────────────────
#
# Data models for the tables/sections present on a per-game Basketball
# Reference box-score page (``/boxscores/YYYYMMDD0XXX.html``) that the
# existing ``player_box_scores`` (daily leaders) and ``team_box_scores``
# (team totals) endpoints do NOT capture:
#
#   • per-player Advanced stats     → ``box-<ABBR>-game-advanced`` tbody
#   • per-team Four Factors         → four-factors table
#   • per-team Line Score           → ``line_score`` table (quarter scoring)
#   • per-player per-quarter splits → ``box-<ABBR>-game-basic`` (Q1/Q2/H1/Q3/Q4/H2)
#   • game-level metadata           → officials / attendance / arena / inactive (prose)
#   • per-player basic + status     → ``box-<ABBR>-game-basic`` tbody (starter/DNP)
#
# SCAFFOLD STATE — forward-declared data models only:
# These classes are intentionally NOT passed to ``register()`` yet. Two CI
# canaries enforce that schemas and endpoints land together as complete,
# fixture-backed units:
#   1. ``test_row_adapters_registry_populated`` pins ``len(ROW_ADAPTERS) == 55``;
#   2. ``test_manifest_meets_coverage_target`` requires ≥95% of registered
#      endpoints to have offline fixtures (which need the parser).
# So each reader is promoted as one atomic unit in PDCA Cycle 2+: ``register()``
# + an ``EndpointSpec`` in ``WORKFLOW_ENDPOINTS`` + a ``WorkflowSpec`` +
# executor binding + parser + offline fixture, bumping the registry count and
# coverage together.
#
# The ``validation_alias`` values below are the standard Basketball Reference
# ``data-stat`` keys and are provisional until each reader's Cycle 2 parser
# verifies them against live HTML. The matching CSV column contracts live in
# ``courtside_data/output/columns/boxscores.py`` (also forward-declared).


class _BoxScoreAdvancedStats:
    """Advanced rate/rating columns from a per-game ``-game-advanced`` table.

    Every ``data-stat`` is provisional (TODO Cycle 2: verify against live HTML).
    """

    true_shooting_percentage: BRFloatOrNone = Field(default=None, validation_alias="ts_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
    three_point_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="fg3a_per_fga_pct")
    free_throw_rate: BRFloatOrNone = Field(default=None, validation_alias="fta_per_fga_pct")
    offensive_rebound_percentage: BRFloatOrNone = Field(default=None, validation_alias="orb_pct")
    defensive_rebound_percentage: BRFloatOrNone = Field(default=None, validation_alias="drb_pct")
    total_rebound_percentage: BRFloatOrNone = Field(default=None, validation_alias="trb_pct")
    assist_percentage: BRFloatOrNone = Field(default=None, validation_alias="ast_pct")
    steal_percentage: BRFloatOrNone = Field(default=None, validation_alias="stl_pct")
    block_percentage: BRFloatOrNone = Field(default=None, validation_alias="blk_pct")
    turnover_percentage: BRFloatOrNone = Field(default=None, validation_alias="tov_pct")
    usage_percentage: BRFloatOrNone = Field(default=None, validation_alias="usg_pct")
    offensive_rating: BRFloatOrNone = Field(default=None, validation_alias="off_rtg")
    defensive_rating: BRFloatOrNone = Field(default=None, validation_alias="def_rtg")
    box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="bpm")


class BoxScorePlayerAdvancedRow(BRRow, _BoxScoreAdvancedStats):
    """Per-player advanced stat line from one game's ``-game-advanced`` table.

    SCAFFOLD: identity (``slug``/``name``/``team``) is injected by the Cycle 2
    parser from row metadata (``data-append-csv`` + the ``box-<ABBR>`` table id).
    """

    slug: StrOrNone = Field(default=None, validation_alias="slug")
    name: StrOrNone = Field(default=None, validation_alias="player")
    team: TeamField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    opponent: TeamField = Field(validation_alias=AliasChoices("opp_name_abbr", "opp_id"))
    seconds_played: SecondsPlayedOrNone = Field(default=None, validation_alias="mp")
    plus_minus: BRIntOrNone = Field(default=None, validation_alias="plus_minus")


class BoxScoreTeamFourFactorsRow(BRRow):
    """One row per team from the per-game Four Factors table. SCAFFOLD.

    Columns: Pace, eFG%, TOV%, ORB%, FT/FGA, ORtg.
    """

    team: TeamNameField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    pace: BRFloatOrNone = Field(default=None, validation_alias="pace")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
    turnover_percentage: BRFloatOrNone = Field(default=None, validation_alias="tov_pct")
    offensive_rebound_percentage: BRFloatOrNone = Field(default=None, validation_alias="orb_pct")
    free_throw_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="ft_rate")
    offensive_rating: BRFloatOrNone = Field(default=None, validation_alias="off_rtg")


class BoxScoreLineScoreRow(BRRow):
    """One row per team from the per-game Line Score table. SCAFFOLD.

    Quarter-by-quarter scoring (Q1-Q4 + final total). Overtime periods are
    variable on Basketball Reference and are TODO for Cycle 2.
    """

    team: TeamNameField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    first_quarter_points: BRIntOrNone = Field(default=None, validation_alias="1")
    second_quarter_points: BRIntOrNone = Field(default=None, validation_alias="2")
    third_quarter_points: BRIntOrNone = Field(default=None, validation_alias="3")
    fourth_quarter_points: BRIntOrNone = Field(default=None, validation_alias="4")
    total_points: BRIntOrNone = Field(default=None, validation_alias="T")


class BoxScorePlayerQuarterSplitRow(BRRow, _BoxScoreCountingStats, _BoxScorePctStats):
    """Per-player basic stat line scoped to one quarter/half period. SCAFFOLD.

    The ``period`` call param (``q1``/``q2``/``h1``/``q3``/``q4``/``h2``)
    selects which per-quarter ``box-<ABBR>-game-basic`` variant the Cycle 2
    parser targets on the per-game page.
    """

    slug: StrOrNone = Field(default=None, validation_alias="slug")
    name: StrOrNone = Field(default=None, validation_alias="player")
    team: TeamField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    opponent: TeamField = Field(validation_alias=AliasChoices("opp_name_abbr", "opp_id"))


class BoxScoreGameInfoRow(BRRow):
    """Game-level metadata row. SCAFFOLD.

    Assembled from prose footers (officials / attendance / arena / inactive
    lists) rather than a ``<table>``; the Cycle 2 parser injects these keys.
    """

    game_date: BRDate = Field(validation_alias="game_date")
    home_team: TeamField = Field(validation_alias="home_team")
    away_team: TeamField = Field(validation_alias="away_team")
    home_team_score: BRIntOrNone = Field(default=None, validation_alias="home_team_score")
    away_team_score: BRIntOrNone = Field(default=None, validation_alias="away_team_score")
    arena: StrOrNone = Field(default=None, validation_alias="arena")
    attendance: BRIntOrNone = Field(default=None, validation_alias="attendance")
    duration: StrOrNone = Field(default=None, validation_alias="duration")
    tip_off: StrOrNone = Field(default=None, validation_alias="tip_off")
    officials: list[str] = Field(default_factory=list, validation_alias="officials")
    inactive_home: list[str] = Field(default_factory=list, validation_alias="inactive_home")
    inactive_away: list[str] = Field(default_factory=list, validation_alias="inactive_away")


class BoxScorePlayerBasicRow(BRRow, _BoxScoreCountingStats, _BoxScorePctStats):
    """Per-player basic line sourced from the per-game ``-game-basic`` table.

    Carries starter/reserve status and the Did-Not-Play / Did-Not-Dress
    distinction that the daily-leaders ``player_box_scores`` endpoint omits.
    SCAFFOLD.
    """

    slug: StrOrNone = Field(default=None, validation_alias="slug")
    name: StrOrNone = Field(default=None, validation_alias="player")
    team: TeamField = Field(validation_alias=AliasChoices("team_name_abbr", "team_id"))
    opponent: TeamField = Field(validation_alias=AliasChoices("opp_name_abbr", "opp_id"))
    location: LocationField = Field(validation_alias="game_location")
    outcome: OutcomeField = Field(validation_alias="game_result")
    is_starter: bool = Field(default=False, validation_alias="is_starter")
    status: StrOrNone = Field(default=None, validation_alias="status")
    plus_minus: BRIntOrNone = Field(default=None, validation_alias="plus_minus")
