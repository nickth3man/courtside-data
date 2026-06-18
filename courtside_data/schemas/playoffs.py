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

from typing import Literal

from pydantic import BaseModel, Field

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._blocks import IdentityBlock, PerGameRateStatsBlock, TotalStatsBlock
from courtside_data.schemas._fields import (
    BRIntOrNone,
    BRPercentage,
    PositionsField,
    StrOrNone,
)
from courtside_data.schemas.league import TeamOrAggregateFieldOrNone


class PlayoffPerGameStats(IdentityBlock, PerGameRateStatsBlock):
    """Per-game stat block for playoff/player aggregate tables."""

    name_display: str = Field(validation_alias="name_display")


class PlayoffTotalStats(TotalStatsBlock):
    """Totals stat block for playoff/player aggregate tables."""


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


class PlayedGame(BaseModel):
    """One completed game in a seven-game playoff series path."""

    game: int
    location: Literal["home", "away"]
    result: Literal["win", "loss"]


class SevenGamePlayoffSeriesOutcomesRow(BRRow):
    """Row from one outcome matrix on ``/friv/7-game-playoff-series-outcomes-22111.html``.

    The page repeats the same three-column table for teams that are down, tied,
    or up in a seven-game playoff series. ``record`` is the current series
    score, ``gameslist`` is Basketball-Reference's home/away pattern label, and
    ``wl`` is the historical series outcome record for that state.

    Structured fields derive from the W-L link ``pattern`` query parameter
    (canonical) and from colored ``gameslist`` spans (cross-check).
    """

    record: str = Field(validation_alias="record")
    gameslist: str = Field(validation_alias="gameslist")
    wl: str = Field(validation_alias="wl")
    aggregate: bool = False
    pattern: str = ""
    pattern_from_spans: str | None = None
    patterns_agree: bool | None = None
    games_played: list[PlayedGame] = Field(default_factory=list)
    games_remaining: list[Literal["home", "away"]] = Field(default_factory=list)
    gameslist_display: str = ""


register("friv_7_game_playoff_series_outcomes_team_is_down", SevenGamePlayoffSeriesOutcomesRow)
register("friv_7_game_playoff_series_outcomes_team_is_tied", SevenGamePlayoffSeriesOutcomesRow)
register("friv_7_game_playoff_series_outcomes_team_is_up", SevenGamePlayoffSeriesOutcomesRow)
