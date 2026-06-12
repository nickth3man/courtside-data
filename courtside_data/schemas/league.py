"""Row schemas for league-wide Basketball-Reference endpoints.

Covers the per-game, per-36-minutes, per-100-possessions, totals, and shooting
player tables, the rookie stats table, league-wide transactions, and arena
attendance. Every field's ``validation_alias`` is the raw ``data-stat`` key the
table emits, so the schema drift detection in the runner fires whenever BR
renames a column.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator, Field

from courtside_data.data import Team
from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow, PerGameStats, TotalStats
from courtside_data.schemas._fields import (
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    PositionsField,
    TeamField,
    _is_empty,
    _team_field,
)

# ---------------------------------------------------------------------------
# Local field vocabulary
# ---------------------------------------------------------------------------


def _team_field_or_none(value: object) -> Team | None:
    """``TeamField`` that maps empty / non-breaking-space cells to ``None``."""
    if _is_empty(value):
        return None
    return _team_field(value)


TeamFieldOrNone = Annotated[Team | None, BeforeValidator(_team_field_or_none)]


# ---------------------------------------------------------------------------
# Per-game / totals stat blocks (mp_per_g, mp, and counting stats)
# ---------------------------------------------------------------------------


class LeaguePerGameStatsRow(BRRow, PerGameStats):
    """Row from a league per-game table (``/leagues/NBA_{year}_per_game.html``).

    The per-game layout (counting stats normalised to per-game values plus an
    effective field-goal percentage) is reused verbatim by the
    :data:`PerGameStats` mixin, so this row only needs to override the
    ``team`` field to tolerate empty ``team_name_abbr`` cells (mid-season
    trades, multi-team stints). ``name_display`` is the one truly required
    column — without it the row is unidentifiable.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamFieldOrNone = Field(default=None, validation_alias="team_name_abbr")


register("league_per_game_stats", LeaguePerGameStatsRow)


class LeagueTotalsRow(BRRow, TotalStats):
    """Row from a league totals table (``/leagues/NBA_{year}_totals.html``).

    The :data:`TotalStats` mixin covers the counting stat block; the player
    info, two-point split, and shooting percentages are added here because
    the BR totals table emits them as separate columns rather than derived
    fields.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    made_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2")
    attempted_two_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg2a")
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")


register("league_totals", LeagueTotalsRow)


class RookieStatsRow(BRRow, PerGameStats):
    """Row from a league rookies table (``/leagues/NBA_{year}_rookies.html``).

    The rookies table is structurally identical to the per-game table, so we
    reuse the :data:`PerGameStats` mixin and apply the same ``team``
    override.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamFieldOrNone = Field(default=None, validation_alias="team_name_abbr")


register("rookie_stats", RookieStatsRow)


# ---------------------------------------------------------------------------
# Per-36 / per-100 / shooting (distinct stat blocks; defined explicitly)
# ---------------------------------------------------------------------------


class LeaguePer36MinutesRow(BRRow):
    """Row from a league per-36-minutes table.

    The per-36 layout does not include effective field-goal percentage and
    uses ``*_per_36_min`` aliases rather than the per-game ``*_per_g`` names,
    so this row redeclares the stat block explicitly.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    made_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fg_per_36_min")
    attempted_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fga_per_36_min")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    made_three_point_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fg3_per_36_min")
    attempted_three_point_field_goals_per_36_min: BRFloatOrNone = Field(
        default=None, validation_alias="fg3a_per_36_min"
    )
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    made_two_point_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fg2_per_36_min")
    attempted_two_point_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fg2a_per_36_min")
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    made_free_throws_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="ft_per_36_min")
    attempted_free_throws_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fta_per_36_min")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    offensive_rebounds_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="orb_per_36_min")
    defensive_rebounds_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="drb_per_36_min")
    total_rebounds_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="trb_per_36_min")
    assists_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="ast_per_36_min")
    steals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="stl_per_36_min")
    blocks_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="blk_per_36_min")
    turnovers_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="tov_per_36_min")
    personal_fouls_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="pf_per_36_min")
    points_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="pts_per_36_min")


register("league_per_36_minutes", LeaguePer36MinutesRow)


class LeaguePer100PossessionsRow(BRRow):
    """Row from a league per-100-possessions table.

    The per-100 layout does not include effective field-goal percentage and
    uses ``*_per_100_poss`` aliases for the rate columns.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    made_field_goals_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="fg_per_100_poss")
    attempted_field_goals_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="fga_per_100_poss")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    made_three_point_field_goals_per_100_possessions: BRFloatOrNone = Field(
        default=None, validation_alias="fg3_per_100_poss"
    )
    attempted_three_point_field_goals_per_100_possessions: BRFloatOrNone = Field(
        default=None, validation_alias="fg3a_per_100_poss"
    )
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    made_two_point_field_goals_per_100_possessions: BRFloatOrNone = Field(
        default=None, validation_alias="fg2_per_100_poss"
    )
    attempted_two_point_field_goals_per_100_possessions: BRFloatOrNone = Field(
        default=None, validation_alias="fg2a_per_100_poss"
    )
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    made_free_throws_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="ft_per_100_poss")
    attempted_free_throws_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="fta_per_100_poss")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    offensive_rebounds_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="orb_per_100_poss")
    defensive_rebounds_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="drb_per_100_poss")
    total_rebounds_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="trb_per_100_poss")
    assists_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="ast_per_100_poss")
    steals_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="stl_per_100_poss")
    blocks_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="blk_per_100_poss")
    turnovers_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="tov_per_100_poss")
    personal_fouls_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="pf_per_100_poss")
    points_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="pts_per_100_poss")


register("league_per_100_possessions", LeaguePer100PossessionsRow)


class LeagueShootingRow(BRRow):
    """Row from a league shooting table (``/leagues/NBA_{year}_shooting.html``).

    The shooting table exposes shot-distance buckets
    (``fg_pct_from_0_3_ft`` ... ``pct_fga_from_3p``), a corner-3 pair, and a
    ``heaves`` pair. Every column shares its BR data-stat key with the field
    name.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    field_goal_percentage_from_zero_to_three_feet: BRPercentage = Field(
        default=None, validation_alias="fg_pct_from_0_3_ft"
    )
    field_goal_percentage_from_three_to_ten_feet: BRPercentage = Field(
        default=None, validation_alias="fg_pct_from_3_10_ft"
    )
    field_goal_percentage_from_ten_to_sixteen_feet: BRPercentage = Field(
        default=None, validation_alias="fg_pct_from_10_16_ft"
    )
    field_goal_percentage_from_sixteen_to_three_point: BRPercentage = Field(
        default=None, validation_alias="fg_pct_from_16_3p"
    )
    field_goal_percentage_from_three_point: BRPercentage = Field(default=None, validation_alias="fg_pct_from_3p")
    percentage_of_field_goal_attempts_from_zero_to_three_feet: BRPercentage = Field(
        default=None, validation_alias="pct_fga_from_0_3_ft"
    )
    percentage_of_field_goal_attempts_from_three_to_ten_feet: BRPercentage = Field(
        default=None, validation_alias="pct_fga_from_3_10_ft"
    )
    percentage_of_field_goal_attempts_from_ten_to_sixteen_feet: BRPercentage = Field(
        default=None, validation_alias="pct_fga_from_10_16_ft"
    )
    percentage_of_field_goal_attempts_from_sixteen_to_three_point: BRPercentage = Field(
        default=None, validation_alias="pct_fga_from_16_3p"
    )
    percentage_of_field_goal_attempts_from_three_point: BRPercentage = Field(
        default=None, validation_alias="pct_fga_from_3p"
    )
    field_goal_percentage_from_two_point: BRPercentage = Field(default=None, validation_alias="fg_pct_from_2p")
    field_goal_percentage_from_zero_to_three_feet_assisted: BRPercentage = Field(
        default=None, validation_alias="fg_pct_from_0_3_ft_2"
    )
    field_goal_percentage_from_corner_three: BRPercentage = Field(default=None, validation_alias="fg_pct_from_corner_3")
    percentage_of_field_goal_attempts_from_corner_three: BRPercentage = Field(
        default=None, validation_alias="pct_fga_from_corner_3"
    )
    number_of_shots_heaved: BRIntOrNone = Field(default=None, validation_alias="num_shots_heaved")
    percentage_of_shots_heaved: BRPercentage = Field(default=None, validation_alias="pct_shots_heaved")


register("league_shooting", LeagueShootingRow)


# ---------------------------------------------------------------------------
# Transactions / attendance
# ---------------------------------------------------------------------------


class LeagueTransactionRow(BRRow):
    """Row from a league transactions page.

    The endpoint declares ``transaction_list_fallback=True``, so the Wave-3
    fetcher produces rows from :func:`courtside_data.tables.parse_transaction_list`
    with the stable keys ``date`` and ``transaction``. The optional
    ``from_team_abbreviations`` / ``to_team_abbreviations`` / ``linked_resources``
    keys are accepted for forward compatibility but are not part of the legacy
    CSV column contract.
    """

    date: str = Field(validation_alias="date")
    transaction: str = Field(validation_alias="transaction")
    from_team_abbreviations: list[str] = Field(default_factory=list, validation_alias="from_team_abbreviations")
    to_team_abbreviations: list[str] = Field(default_factory=list, validation_alias="to_team_abbreviations")
    linked_resources: list[dict[str, str]] = Field(default_factory=list, validation_alias="linked_resources")


register("league_transactions", LeagueTransactionRow)


class AttendanceRow(BRRow):
    """Row from the league attendance table (``table#advanced-team``).

    The endpoint's ``projection`` keeps only ``team``, ``arena_name``,
    ``attendance``, and ``attendance_per_g`` from the underlying
    ``#advanced-team`` table, so the row is keyed off those four columns.
    The historical ``ATTENDANCE_COLUMN_NAMES`` CSV contract (with separate
    home/away game and attendance columns) does not match the BR data and is
    intentionally not modelled here.
    """

    team: TeamField = Field(validation_alias="team")
    arena_name: str = Field(validation_alias="arena_name")
    attendance: BRIntOrNone = Field(default=None, validation_alias="attendance")
    attendance_per_game: BRIntOrNone = Field(default=None, validation_alias="attendance_per_g")


register("attendance", AttendanceRow)


# ---------------------------------------------------------------------------
# Awards + leaders (irregular table shapes; minimal column contract)
# ---------------------------------------------------------------------------


class SeasonAwardsRow(BRRow):
    """Row from a season awards table (``/awards/awards_{year}.html``).

    The MVP table exposes at minimum the award name and the player who
    won (or is being voted on). Both fields are required — a row without
    a player is meaningless, and the award name disambiguates the row
    when several awards share a page.
    """

    award: str = Field(validation_alias="award")
    player: str = Field(validation_alias="player")


register("season_awards", SeasonAwardsRow)


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
    active leader category.
    """

    rank: BRInt = Field(validation_alias="rank")
    player: str = Field(validation_alias="player")
    value: str = Field(validation_alias="value")


register("career_leaders", CareerLeadersRow)
