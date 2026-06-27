"""Shared Pydantic mixin blocks for Basketball-Reference row schemas.

Each block groups a logical set of ``data-stat`` columns that appear together
across multiple domain schemas.  Blocks are plain Python mixin classes (not
:class:`BRRow` subclasses) — they declare fields and ``validation_alias`` values
but do **not** carry a ``model_config``.  Rows inherit from both ``BRRow`` and
the needed blocks:

.. code-block:: python

    class LeaguePerGameStatsRow(BRRow, IdentityBlock, PerGameRateStatsBlock):
        awards: StrOrNone = Field(default=None, validation_alias="awards")

The blocks are intentionally **not** ``BaseModel`` subclasses — they are dumb
attribute holders that Pydantic picks up at class-creation time via MRO.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator, Field

from courtside_data.domain import Team
from courtside_data.schemas._fields import (
    BRFloatOrNone,
    BRIntOrNone,
    BRPercentage,
    PositionsField,
    StrOrNone,
    _is_empty,
    _team_field,
)

# ---------------------------------------------------------------------------
# Shared field type aliases
# ---------------------------------------------------------------------------


_AGGREGATE_TEAM_ABBREVIATIONS = frozenset({"TOT", "2TM", "3TM"})


def _team_or_aggregate_field_or_none(value: object) -> Team | str | None:
    """Team abbreviation parser that also accepts BR multi-team aggregate rows."""
    if _is_empty(value):
        return None
    if isinstance(value, Team):
        return value
    s = str(value).strip()
    if s in _AGGREGATE_TEAM_ABBREVIATIONS:
        return s
    return _team_field(value)


TeamOrAggregateFieldOrNone = Annotated[Team | str | None, BeforeValidator(_team_or_aggregate_field_or_none)]


# ---------------------------------------------------------------------------
# Identity block
# ---------------------------------------------------------------------------


class IdentityBlock:
    """Player identity / demographic fields.

    ``name_display`` is optional here (defaults to ``None``) so that rows
    without a ``name_display`` column (e.g. player career per-game tables
    which use ``season`` instead) can inherit the block without a required
    field error.  Rows that need a required ``name_display`` can override::

        name_display: str = Field(validation_alias="name_display")

    ``team`` uses the league-wide aggregate abbreviations (``TOT``, ``2TM``,
    ``3TM``) via :data:`~courtside_data.schemas._blocks.TeamOrAggregateFieldOrNone`;
    rows that need a stricter ``TeamField`` can override the field.
    """

    name_display: str | None = Field(default=None, validation_alias="name_display")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team: TeamOrAggregateFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")


# ---------------------------------------------------------------------------
# Per-game rate stats
# ---------------------------------------------------------------------------


class PerGameRateStatsBlock:
    """Per-game rate stat block (``*_per_g`` columns + percentages).

    Every field uses the ``*_per_g`` ``data-stat`` alias, exactly as emitted
    by the BR per-game tables.  Percentages (``fg_pct``, ``fg3_pct``, etc.)
    are also part of this block because the BR per-game table interleaves them
    between the per-game counts.

    Used by :class:`courtside_data.schemas.league.LeaguePerGameStatsRow`,
    :class:`courtside_data.schemas.playoffs.PlayoffPerGameRow`, and
    :class:`courtside_data.schemas.players.PlayerCareerStatsRow`.
    """

    minutes_played_per_game: BRFloatOrNone = Field(default=None, validation_alias="mp_per_g")
    made_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fg_per_g")
    attempted_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fga_per_g")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    made_three_point_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fg3_per_g")
    attempted_three_point_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fg3a_per_g")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    made_two_point_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fg2_per_g")
    attempted_two_point_field_goals_per_game: BRFloatOrNone = Field(default=None, validation_alias="fg2a_per_g")
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
    made_free_throws_per_game: BRFloatOrNone = Field(default=None, validation_alias="ft_per_g")
    attempted_free_throws_per_game: BRFloatOrNone = Field(default=None, validation_alias="fta_per_g")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    offensive_rebounds_per_game: BRFloatOrNone = Field(default=None, validation_alias="orb_per_g")
    defensive_rebounds_per_game: BRFloatOrNone = Field(default=None, validation_alias="drb_per_g")
    total_rebounds_per_game: BRFloatOrNone = Field(default=None, validation_alias="trb_per_g")
    assists_per_game: BRFloatOrNone = Field(default=None, validation_alias="ast_per_g")
    steals_per_game: BRFloatOrNone = Field(default=None, validation_alias="stl_per_g")
    blocks_per_game: BRFloatOrNone = Field(default=None, validation_alias="blk_per_g")
    turnovers_per_game: BRFloatOrNone = Field(default=None, validation_alias="tov_per_g")
    personal_fouls_per_game: BRFloatOrNone = Field(default=None, validation_alias="pf_per_g")
    points_per_game: BRFloatOrNone = Field(default=None, validation_alias="pts_per_g")


# ---------------------------------------------------------------------------
# Advanced rate / rating stats
# ---------------------------------------------------------------------------


class AdvancedRateStatsBlock:
    """Advanced rate / rating columns (``ts_pct`` … ``bpm``).

    The set of advanced-rate ``data-stat`` columns emitted by Basketball
    Reference's per-game ``-game-advanced`` and per-season advanced tables.
    All rate columns (``ts_pct``, ``efg_pct``, ``orb_pct`` … ``usg_pct``) are
    typed as bare :data:`~courtside_data.schemas._fields.BRFloatOrNone` because
    the per-game advanced table ships them as raw decimal fractions in the
    ``0.0-1.0`` range.  Per-season tables (e.g.
    :class:`courtside_data.schemas.player_totals.PlayerAdvancedSeasonTotalsRow`)
    emit the same aliases as ``0-100`` strings, which the :data:`BRPercentage`
    validator divides by 100 — so they intentionally do **not** inherit this
    block; copy / override the fields with the appropriate type.

    Used by :class:`courtside_data.schemas.boxscores.BoxScorePlayerAdvancedRow`.
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


# ---------------------------------------------------------------------------
# Totals counting stats
# ---------------------------------------------------------------------------


class TotalStatsBlock:
    """Counting-totals stat block (``games`` / ``mp`` / ``fg`` … ``pts``).

    Each field uses the short ``data-stat`` alias that the BR totals table
    emits.  Every field defaults to ``None`` because a player may have zeroes
    in any given counting stat cell.

    Used by :class:`courtside_data.schemas.league.LeagueTotalsRow`,
    :class:`courtside_data.schemas.playoffs.PlayoffTotalsRow`, and several
    player-specific schemas.
    """

    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
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


# ---------------------------------------------------------------------------
# Team-and-opponent block
# ---------------------------------------------------------------------------


class TeamOpponentStatsBlock:
    """Team-and-opponent counting and per-game rate columns (both sides).

    Used by :class:`courtside_data.schemas.teams.TeamAndOpponentRow` and
    :class:`courtside_data.schemas.teams.TeamOpponentStatsRow`.
    """

    player: StrOrNone = Field(default=None, validation_alias="player")
    g: BRIntOrNone = Field(default=None, validation_alias="g")
    mp: BRIntOrNone = Field(default=None, validation_alias="mp")
    fg: BRIntOrNone = Field(default=None, validation_alias="fg")
    fga: BRIntOrNone = Field(default=None, validation_alias="fga")
    fg_pct: BRPercentage = Field(default=None, validation_alias="fg_pct")
    fg3: BRIntOrNone = Field(default=None, validation_alias="fg3")
    fg3a: BRIntOrNone = Field(default=None, validation_alias="fg3a")
    fg3_pct: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    fg2: BRIntOrNone = Field(default=None, validation_alias="fg2")
    fg2a: BRIntOrNone = Field(default=None, validation_alias="fg2a")
    fg2_pct: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    ft: BRIntOrNone = Field(default=None, validation_alias="ft")
    fta: BRIntOrNone = Field(default=None, validation_alias="fta")
    ft_pct: BRPercentage = Field(default=None, validation_alias="ft_pct")
    orb: BRIntOrNone = Field(default=None, validation_alias="orb")
    drb: BRIntOrNone = Field(default=None, validation_alias="drb")
    trb: BRIntOrNone = Field(default=None, validation_alias="trb")
    ast: BRIntOrNone = Field(default=None, validation_alias="ast")
    stl: BRIntOrNone = Field(default=None, validation_alias="stl")
    blk: BRIntOrNone = Field(default=None, validation_alias="blk")
    tov: BRIntOrNone = Field(default=None, validation_alias="tov")
    pf: BRIntOrNone = Field(default=None, validation_alias="pf")
    pts: BRIntOrNone = Field(default=None, validation_alias="pts")
    mp_per_g: BRFloatOrNone = Field(default=None, validation_alias="mp_per_g")
    fg_per_g: BRFloatOrNone = Field(default=None, validation_alias="fg_per_g")
    fga_per_g: BRFloatOrNone = Field(default=None, validation_alias="fga_per_g")
    fg3_per_g: BRFloatOrNone = Field(default=None, validation_alias="fg3_per_g")
    fg3a_per_g: BRFloatOrNone = Field(default=None, validation_alias="fg3a_per_g")
    fg2_per_g: BRFloatOrNone = Field(default=None, validation_alias="fg2_per_g")
    fg2a_per_g: BRFloatOrNone = Field(default=None, validation_alias="fg2a_per_g")
    ft_per_g: BRFloatOrNone = Field(default=None, validation_alias="ft_per_g")
    fta_per_g: BRFloatOrNone = Field(default=None, validation_alias="fta_per_g")
    orb_per_g: BRFloatOrNone = Field(default=None, validation_alias="orb_per_g")
    drb_per_g: BRFloatOrNone = Field(default=None, validation_alias="drb_per_g")
    trb_per_g: BRFloatOrNone = Field(default=None, validation_alias="trb_per_g")
    ast_per_g: BRFloatOrNone = Field(default=None, validation_alias="ast_per_g")
    stl_per_g: BRFloatOrNone = Field(default=None, validation_alias="stl_per_g")
    blk_per_g: BRFloatOrNone = Field(default=None, validation_alias="blk_per_g")
    tov_per_g: BRFloatOrNone = Field(default=None, validation_alias="tov_per_g")
    pf_per_g: BRFloatOrNone = Field(default=None, validation_alias="pf_per_g")
    pts_per_g: BRFloatOrNone = Field(default=None, validation_alias="pts_per_g")
    opp_fg: BRIntOrNone = Field(default=None, validation_alias="opp_fg")
    opp_fga: BRIntOrNone = Field(default=None, validation_alias="opp_fga")
    opp_fg_pct: BRPercentage = Field(default=None, validation_alias="opp_fg_pct")
    opp_fg3: BRIntOrNone = Field(default=None, validation_alias="opp_fg3")
    opp_fg3a: BRIntOrNone = Field(default=None, validation_alias="opp_fg3a")
    opp_fg3_pct: BRPercentage = Field(default=None, validation_alias="opp_fg3_pct")
    opp_fg2: BRIntOrNone = Field(default=None, validation_alias="opp_fg2")
    opp_fg2a: BRIntOrNone = Field(default=None, validation_alias="opp_fg2a")
    opp_fg2_pct: BRPercentage = Field(default=None, validation_alias="opp_fg2_pct")
    opp_ft: BRIntOrNone = Field(default=None, validation_alias="opp_ft")
    opp_fta: BRIntOrNone = Field(default=None, validation_alias="opp_fta")
    opp_ft_pct: BRPercentage = Field(default=None, validation_alias="opp_ft_pct")
    opp_orb: BRIntOrNone = Field(default=None, validation_alias="opp_orb")
    opp_drb: BRIntOrNone = Field(default=None, validation_alias="opp_drb")
    opp_trb: BRIntOrNone = Field(default=None, validation_alias="opp_trb")
    opp_ast: BRIntOrNone = Field(default=None, validation_alias="opp_ast")
    opp_stl: BRIntOrNone = Field(default=None, validation_alias="opp_stl")
    opp_blk: BRIntOrNone = Field(default=None, validation_alias="opp_blk")
    opp_tov: BRIntOrNone = Field(default=None, validation_alias="opp_tov")
    opp_pf: BRIntOrNone = Field(default=None, validation_alias="opp_pf")
    opp_pts: BRIntOrNone = Field(default=None, validation_alias="opp_pts")
    opp_fg_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_fg_per_g")
    opp_fga_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_fga_per_g")
    opp_fg3_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_fg3_per_g")
    opp_fg3a_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_fg3a_per_g")
    opp_fg2_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_fg2_per_g")
    opp_fg2a_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_fg2a_per_g")
    opp_ft_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_ft_per_g")
    opp_fta_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_fta_per_g")
    opp_orb_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_orb_per_g")
    opp_drb_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_drb_per_g")
    opp_trb_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_trb_per_g")
    opp_ast_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_ast_per_g")
    opp_stl_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_stl_per_g")
    opp_blk_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_blk_per_g")
    opp_tov_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_tov_per_g")
    opp_pf_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_pf_per_g")
    opp_pts_per_g: BRFloatOrNone = Field(default=None, validation_alias="opp_pts_per_g")


# ---------------------------------------------------------------------------
# Play-by-play zone percentages
# ---------------------------------------------------------------------------


class PctZoneBlock:
    """Zone-of-the-floor field-goal percentages (``pct_1`` … ``pct_5``).

    The five columns are the percentage of field goals made from each of BR's
    five floor zones (paint, mid-range, three-point, etc.) as exposed on the
    play-by-play derived table (``pbp_stats``). All values are :class:`BRPercentage`
    (a 0.0-1.0 float, ``None`` when the player has no attempts in that zone).

    Used by :class:`courtside_data.schemas.league.LeaguePlayByPlayRow` and
    :class:`courtside_data.schemas.players.PlayerPlayByPlayStatsRow`.
    """

    pct_1: BRPercentage = Field(default=None, validation_alias="pct_1")
    pct_2: BRPercentage = Field(default=None, validation_alias="pct_2")
    pct_3: BRPercentage = Field(default=None, validation_alias="pct_3")
    pct_4: BRPercentage = Field(default=None, validation_alias="pct_4")
    pct_5: BRPercentage = Field(default=None, validation_alias="pct_5")
