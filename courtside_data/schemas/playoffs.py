"""Row schemas for playoff-scoped Basketball-Reference endpoints.

Covers the playoff per-game and totals stat tables (structurally identical to
the league per-game and totals layouts) plus the playoff bracket results.
The bracket endpoint uses ``use_header_fallback=True`` because the ``all_playoffs``
table is a manually-laid-out bracket whose data cells often lack ``data-stat``
attributes; :class:`PlayoffBracketRow` therefore uses the normalized header text
the fallback layer produces (``series``, ``team``, ``result``) as its
``validation_alias`` keys.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator, Field

from courtside_data.data import Team
from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
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
# Local field vocabulary
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


class PlayoffPerGameStats:
    """Per-game stat block for playoff/player aggregate tables."""

    name_display: str = Field(validation_alias="name_display")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team: TeamOrAggregateFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
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


class PlayoffTotalStats:
    """Totals stat block for playoff/player aggregate tables."""

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
# Playoff per-game / totals
# ---------------------------------------------------------------------------


class PlayoffPerGameRow(BRRow, PlayoffPerGameStats):
    """Row from a playoff per-game table (``/leagues/NBA_{year}_per_game.html``).

    Structurally identical to the league per-game table, so the
    :data:`PerGameStats` mixin covers every stat column. The ``team`` field is
    re-declared as :data:`TeamFieldOrNone` so the model tolerates empty
    ``team_name_abbr`` cells (mid-series trades, multi-team playoff stints).
    ``name_display`` is the only truly required column — without it the row
    is unidentifiable.
    """

    awards: StrOrNone = Field(default=None, validation_alias="awards")


register("playoff_per_game", PlayoffPerGameRow)


class PlayoffTotalsRow(BRRow, PlayoffTotalStats):
    """Row from a playoff totals table (``/leagues/NBA_{year}_totals.html``).

    Mirrors :class:`courtside_data.schemas.league.LeagueTotalsRow`: the
    :data:`TotalStats` mixin covers the counting stat block, and the
    two-point split, shooting percentages, position, and age columns are
    re-declared explicitly because the BR table emits them as their own
    columns rather than derived fields.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamOrAggregateFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    made_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2")
    attempted_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2a")
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
    triple_doubles: BRIntOrNone = Field(default=None, validation_alias="tpl_dbl")
    awards: StrOrNone = Field(default=None, validation_alias="awards")


register("playoff_totals", PlayoffTotalsRow)


# ---------------------------------------------------------------------------
# Playoff bracket
# ---------------------------------------------------------------------------


class PlayoffBracketRow(BRRow):
    """Row from a playoff bracket results table (``/playoffs/NBA_{year}.html``).

    The ``all_playoffs`` table is a manually-laid-out bracket whose cells
    often lack ``data-stat`` attributes. The generic-table fetcher falls back
    to the normalized header text in that case, producing rows keyed by
    ``series`` / ``team`` / ``result`` (the header text "Series", "Team",
    "Result" normalized to lowercase snake case). All three columns are kept
    as ``str`` to remain agnostic to playoff-specific team names and free-form
    result strings such as "Won NBA Championship".
    """

    series: str = Field(validation_alias="series")
    team: str = Field(validation_alias="team")
    result: str = Field(validation_alias="result")


register("playoff_bracket", PlayoffBracketRow)


# ---------------------------------------------------------------------------
# Seven-game playoff series outcome matrices
# ---------------------------------------------------------------------------


class SevenGamePlayoffSeriesOutcomesRow(BRRow):
    """Row from one outcome matrix on ``/friv/7-game-playoff-series-outcomes-22111.html``.

    The page repeats the same three-column table for teams that are down, tied,
    or up in a seven-game playoff series. ``record`` is the current series
    score, ``gameslist`` is Basketball-Reference's home/away pattern label, and
    ``wl`` is the historical series outcome record for that state.
    """

    record: str = Field(validation_alias="record")
    gameslist: str = Field(validation_alias="gameslist")
    wl: str = Field(validation_alias="wl")


register("friv_7_game_playoff_series_outcomes_team_is_down", SevenGamePlayoffSeriesOutcomesRow)
register("friv_7_game_playoff_series_outcomes_team_is_tied", SevenGamePlayoffSeriesOutcomesRow)
register("friv_7_game_playoff_series_outcomes_team_is_up", SevenGamePlayoffSeriesOutcomesRow)
