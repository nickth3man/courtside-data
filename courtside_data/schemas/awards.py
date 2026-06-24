"""Row schemas for Basketball-Reference awards and leaders endpoints.

All models remain importable from ``courtside_data.schemas.league`` for
backward compatibility.
"""

from __future__ import annotations

from pydantic import Field

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRAwardRank,
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    PositionsField,
    RankTied,
    StrOrNone,
)

# ---------------------------------------------------------------------------
# Season awards + voting
# ---------------------------------------------------------------------------


class SeasonAwardsRow(BRRow):
    """Row from a season awards table (``/awards/awards_{year}.html``).

    The MVP table exposes voting results: rank, player, age, team, vote
    shares, per-game stats, and advanced metrics. Tied ranks are rendered by
    Basketball Reference as ``"7T"`` / ``"10T"``; ``rank`` carries the
    integer portion while the companion ``rank_tied`` flag preserves the tie
    information that would otherwise be lost.
    """

    rank: BRAwardRank = Field(default=None, validation_alias="rank")
    rank_tied: RankTied = Field(default=False, validation_alias="rank")
    player: str = Field(validation_alias="player")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team_id: StrOrNone = Field(default=None, validation_alias="team_id")
    votes_first: BRIntOrNone = Field(default=None, validation_alias="votes_first")
    points_won: BRIntOrNone = Field(default=None, validation_alias="points_won")
    points_max: BRIntOrNone = Field(default=None, validation_alias="points_max")
    award_share: BRFloatOrNone = Field(default=None, validation_alias="award_share")
    g: BRIntOrNone = Field(default=None, validation_alias="g")
    mp_per_g: BRFloatOrNone = Field(default=None, validation_alias="mp_per_g")
    pts_per_g: BRFloatOrNone = Field(default=None, validation_alias="pts_per_g")
    trb_per_g: BRFloatOrNone = Field(default=None, validation_alias="trb_per_g")
    ast_per_g: BRFloatOrNone = Field(default=None, validation_alias="ast_per_g")
    stl_per_g: BRFloatOrNone = Field(default=None, validation_alias="stl_per_g")
    blk_per_g: BRFloatOrNone = Field(default=None, validation_alias="blk_per_g")
    fg_pct: BRPercentage = Field(default=None, validation_alias="fg_pct")
    fg3_pct: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    ft_pct: BRPercentage = Field(default=None, validation_alias="ft_pct")
    ws: BRFloatOrNone = Field(default=None, validation_alias="ws")
    ws_per_48: BRFloatOrNone = Field(default=None, validation_alias="ws_per_48")


register("season_awards", SeasonAwardsRow)


class SeasonAwardsVotingRow(SeasonAwardsRow):
    """Row from a season award voting table (``/awards/awards_{year}.html``)."""

    wins: BRIntOrNone = Field(default=None, validation_alias="wins")
    losses: BRIntOrNone = Field(default=None, validation_alias="losses")
    win_loss_pct: BRPercentage = Field(default=None, validation_alias="win_loss_pct")
    coach: StrOrNone = Field(default=None, validation_alias="coach")
    tm_id: StrOrNone = Field(default=None, validation_alias="tm_id")
    pos: PositionsField = Field(default_factory=list, validation_alias="pos")
    first_team_votes: BRIntOrNone = Field(default=None, validation_alias="first_team_votes")
    second_team_votes: BRIntOrNone = Field(default=None, validation_alias="second_team_votes")
    third_team_votes: BRIntOrNone = Field(default=None, validation_alias="third_team_votes")
    all_nba_team: StrOrNone = Field(default=None, validation_alias="all_nba_team")
    all_defense_team: StrOrNone = Field(default=None, validation_alias="all_defense_team")
    all_rookie_team: StrOrNone = Field(default=None, validation_alias="all_rookie_team")
    dws: BRFloatOrNone = Field(default=None, validation_alias="dws")
    dbpm: BRFloatOrNone = Field(default=None, validation_alias="dbpm")
    def_rtg: BRFloatOrNone = Field(default=None, validation_alias="def_rtg")


register("season_awards_voting", SeasonAwardsVotingRow)


# ---------------------------------------------------------------------------
# Season leaders + career leaders
# ---------------------------------------------------------------------------


class SeasonLeadersRow(BRRow):
    """Row from the per-season statistical leaders index (``/leaders/per_season.html``).

    The leaders page covers many stat categories (points, rebounds, assists,
    steals, blocks, …) all sharing the same five-column shape. ``rank``,
    ``player``, and ``season`` are required; ``value`` is a free-form stat
    cell that the fallback layer delivers as a string and that downstream
    consumers coerce to ``int``/``float`` based on the active category.
    ``team_id`` is the team abbreviation for the season of the leader's
    record (may be empty for historical pre-ABA / BAA rows).
    """

    rank: BRInt = Field(validation_alias="rank")
    player: str = Field(validation_alias="player")
    value: str = Field(validation_alias="value")
    season: str = Field(validation_alias="season")
    team: str | None = Field(default=None, validation_alias="team_id")


register("season_leaders", SeasonLeadersRow)


class CareerLeadersRow(BRRow):
    """Row from the all-time career leaders index (``/leaders/``).

    A three-column shape (``rank``, ``player``, ``value``). The same
    free-form ``value`` cell appears here as on
    :class:`SeasonLeadersRow`; downstream consumers coerce it based on the
    active leader category. ``rank`` is optional: Basketball Reference
    leaves the rank cell blank for players tied with the previous entry, and
    those rows are real records that must be retained (a blank rank becomes
    ``None`` rather than dropping the row).

    .. todo:: Derive explicit tie information for career leaders. Unlike award
       tables, BR does *not* suffix tied ranks with ``T`` — the tie is
       implicit in the cell being blank while the preceding row carries a
       numbered rank. A future enhancement could surface this via a companion
       field (e.g. ``rank_tied``) derived from row ordering rather than the
       source cell, making the tie explicit without changing the source contract.
    """

    rank: BRIntOrNone = Field(default=None, validation_alias="rank")
    player: str = Field(validation_alias="player")
    value: str = Field(validation_alias="value")


register("career_leaders", CareerLeadersRow)
