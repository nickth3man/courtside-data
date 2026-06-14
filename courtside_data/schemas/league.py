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
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRFloatOrNone,
    BRInt,
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


class LeaguePerGameStats:
    """Per-game stat block for league/player aggregate tables."""

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


class LeagueTotalStats:
    """Totals stat block for league/player aggregate tables."""

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
# Per-game / totals stat blocks (mp_per_g, mp, and counting stats)
# ---------------------------------------------------------------------------


class LeaguePerGameStatsRow(BRRow, LeaguePerGameStats):
    """Row from a league per-game table (``/leagues/NBA_{year}_per_game.html``).

    The per-game layout (counting stats normalised to per-game values plus an
    effective field-goal percentage) is reused verbatim by the
    :data:`PerGameStats` mixin, so this row only needs to override the
    ``team`` field to tolerate empty ``team_name_abbr`` cells (mid-season
    trades, multi-team stints). ``name_display`` is the one truly required
    column — without it the row is unidentifiable.
    """

    awards: StrOrNone = Field(default=None, validation_alias="awards")


register("league_per_game_stats", LeaguePerGameStatsRow)


class LeagueTotalsRow(BRRow, LeagueTotalStats):
    """Row from a league totals table (``/leagues/NBA_{year}_totals.html``).

    The :data:`TotalStats` mixin covers the counting stat block; the player
    info, two-point split, and shooting percentages are added here because
    the BR totals table emits them as separate columns rather than derived
    fields.
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


register("league_totals", LeagueTotalsRow)


class RookieStatsRow(BRRow, LeaguePerGameStats):
    """Row from a league rookies table (``/leagues/NBA_{year}_rookies.html``).

    The rookies table is structurally identical to the per-game table, so we
    reuse the :data:`PerGameStats` mixin and apply the same ``team``
    override.
    """


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
    team: TeamOrAggregateFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    made_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fg_per_minute_36")
    attempted_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fga_per_minute_36")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    made_three_point_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fg3_per_minute_36")
    attempted_three_point_field_goals_per_36_min: BRFloatOrNone = Field(
        default=None, validation_alias="fg3a_per_minute_36"
    )
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    made_two_point_field_goals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fg2_per_minute_36")
    attempted_two_point_field_goals_per_36_min: BRFloatOrNone = Field(
        default=None, validation_alias="fg2a_per_minute_36"
    )
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
    made_free_throws_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="ft_per_minute_36")
    attempted_free_throws_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="fta_per_minute_36")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    offensive_rebounds_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="orb_per_minute_36")
    defensive_rebounds_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="drb_per_minute_36")
    total_rebounds_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="trb_per_minute_36")
    assists_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="ast_per_minute_36")
    steals_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="stl_per_minute_36")
    blocks_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="blk_per_minute_36")
    turnovers_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="tov_per_minute_36")
    personal_fouls_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="pf_per_minute_36")
    points_per_36_min: BRFloatOrNone = Field(default=None, validation_alias="pts_per_minute_36")
    awards: StrOrNone = Field(default=None, validation_alias="awards")


register("league_per_36_minutes", LeaguePer36MinutesRow)


class LeaguePer100PossessionsRow(BRRow):
    """Row from a league per-100-possessions table.

    The per-100 layout does not include effective field-goal percentage and
    uses ``*_per_100_poss`` aliases for the rate columns.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamOrAggregateFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    made_field_goals_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="fg_per_poss")
    attempted_field_goals_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="fga_per_poss")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    made_three_point_field_goals_per_100_possessions: BRFloatOrNone = Field(
        default=None, validation_alias="fg3_per_poss"
    )
    attempted_three_point_field_goals_per_100_possessions: BRFloatOrNone = Field(
        default=None, validation_alias="fg3a_per_poss"
    )
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    made_two_point_field_goals_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="fg2_per_poss")
    attempted_two_point_field_goals_per_100_possessions: BRFloatOrNone = Field(
        default=None, validation_alias="fg2a_per_poss"
    )
    two_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg2_pct")
    effective_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="efg_pct")
    made_free_throws_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="ft_per_poss")
    attempted_free_throws_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="fta_per_poss")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    offensive_rebounds_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="orb_per_poss")
    defensive_rebounds_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="drb_per_poss")
    total_rebounds_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="trb_per_poss")
    assists_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="ast_per_poss")
    steals_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="stl_per_poss")
    blocks_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="blk_per_poss")
    turnovers_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="tov_per_poss")
    personal_fouls_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="pf_per_poss")
    points_per_100_possessions: BRFloatOrNone = Field(default=None, validation_alias="pts_per_poss")
    offensive_rating: BRFloatOrNone = Field(default=None, validation_alias="off_rtg")
    defensive_rating: BRFloatOrNone = Field(default=None, validation_alias="def_rtg")
    awards: StrOrNone = Field(default=None, validation_alias="awards")


register("league_per_100_possessions", LeaguePer100PossessionsRow)


class LeagueShootingRow(BRRow):
    """Row from a league shooting table (``/leagues/NBA_{year}_shooting.html``).

    Field ``validation_alias`` values are the table's real ``data-stat`` keys:
    the distance buckets ``*_00_03`` / ``*_03_10`` / ``*_10_16`` / ``*_16_xx``,
    the two-point/three-point splits ``*_fg2a`` / ``*_fg3a``, the assisted,
    dunk, corner-three, and heave columns.
    """

    name_display: str = Field(validation_alias="name_display")
    team: TeamOrAggregateFieldOrNone = Field(default=None, validation_alias="team_name_abbr")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    average_shot_distance: BRFloatOrNone = Field(default=None, validation_alias="avg_dist")
    percentage_of_field_goal_attempts_from_two_point_range: BRPercentage = Field(
        default=None, validation_alias="pct_fga_fg2a"
    )
    percentage_of_field_goal_attempts_from_zero_to_three_feet: BRPercentage = Field(
        default=None, validation_alias="pct_fga_00_03"
    )
    percentage_of_field_goal_attempts_from_three_to_ten_feet: BRPercentage = Field(
        default=None, validation_alias="pct_fga_03_10"
    )
    percentage_of_field_goal_attempts_from_ten_to_sixteen_feet: BRPercentage = Field(
        default=None, validation_alias="pct_fga_10_16"
    )
    percentage_of_field_goal_attempts_from_sixteen_feet_to_three_point: BRPercentage = Field(
        default=None, validation_alias="pct_fga_16_xx"
    )
    percentage_of_field_goal_attempts_from_three_point_range: BRPercentage = Field(
        default=None, validation_alias="pct_fga_fg3a"
    )
    field_goal_percentage_from_two_point_range: BRPercentage = Field(default=None, validation_alias="fg_pct_fg2a")
    field_goal_percentage_from_zero_to_three_feet: BRPercentage = Field(default=None, validation_alias="fg_pct_00_03")
    field_goal_percentage_from_three_to_ten_feet: BRPercentage = Field(default=None, validation_alias="fg_pct_03_10")
    field_goal_percentage_from_ten_to_sixteen_feet: BRPercentage = Field(default=None, validation_alias="fg_pct_10_16")
    field_goal_percentage_from_sixteen_feet_to_three_point: BRPercentage = Field(
        default=None, validation_alias="fg_pct_16_xx"
    )
    field_goal_percentage_from_three_point_range: BRPercentage = Field(default=None, validation_alias="fg_pct_fg3a")
    percentage_of_two_point_field_goals_assisted: BRPercentage = Field(default=None, validation_alias="pct_ast_fg2")
    percentage_of_three_point_field_goals_assisted: BRPercentage = Field(default=None, validation_alias="pct_ast_fg3")
    percentage_of_field_goal_attempts_that_are_dunks: BRPercentage = Field(
        default=None, validation_alias="pct_fga_dunk"
    )
    made_dunks: BRIntOrNone = Field(default=None, validation_alias="fg_dunk")
    percentage_of_three_point_attempts_from_corner: BRPercentage = Field(
        default=None, validation_alias="pct_fg3a_corner3"
    )
    field_goal_percentage_on_corner_three_pointers: BRPercentage = Field(
        default=None, validation_alias="fg_pct_corner3"
    )
    attempted_heaves: BRIntOrNone = Field(default=None, validation_alias="fg3a_heave")
    made_heaves: BRIntOrNone = Field(default=None, validation_alias="fg3_heave")
    awards: StrOrNone = Field(default=None, validation_alias="awards")


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

    team: Annotated[Team, BeforeValidator(_team_field)] = Field(validation_alias="team")
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
