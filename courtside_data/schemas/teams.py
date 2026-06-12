"""Row schemas for team-scoped Basketball-Reference endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, Field, model_validator

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRDate,
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    BRSalary,
    PositionsField,
)


class _GBasedTotalStats:
    """Counting stats whose raw ``data-stat`` key for games is ``g``."""

    games_played: BRIntOrNone = Field(default=None, validation_alias="g")
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


class _PercentageStats:
    """Shooting percentage columns that use BR's ``_pct`` data-stat keys."""

    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")


class TeamRosterRow(BRRow):
    """Row from a team's season roster table (``table#roster``)."""

    player: str = Field(validation_alias="player")
    number: str = Field(validation_alias="number")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    height: str = Field(validation_alias="height")
    weight: BRInt = Field(validation_alias="weight")
    birth_date: str = Field(validation_alias="birth_date")
    flag: str = Field(validation_alias="flag")
    years_experience: str = Field(validation_alias="years_experience")
    college: str | None = Field(default=None, validation_alias="college")


register("team_roster", TeamRosterRow)


class TeamInjuryReportRow(BRRow):
    """Row from the league-wide injury table (``table#injuries``)."""

    player: str = Field(validation_alias="player")
    date: BRDate = Field(validation_alias="date")
    description: str = Field(validation_alias="description")


register("team_injury_report", TeamInjuryReportRow)


class TeamAndOpponentRow(BRRow, _GBasedTotalStats, _PercentageStats):
    """Row from a team's ``#team_and_opponent`` table.

    Contains both the team's own totals and the opponent's aggregated totals.
    """

    stat_type: str = Field(validation_alias=AliasChoices("stat_type", "team_name_abbr"))


register("team_and_opponent", TeamAndOpponentRow)


class TeamMiscFourFactorsRow(BRRow):
    """Row from a team's ``#team_misc`` four-factors table."""

    stat_type: str = Field(validation_alias="stat_type")
    pace: BRFloatOrNone = Field(default=None, validation_alias="pace")
    effective_field_goal_percentage: BRFloatOrNone = Field(default=None, validation_alias="efg_pct")
    turnover_percentage: BRFloatOrNone = Field(default=None, validation_alias="tov_pct")
    offensive_rebound_percentage: BRFloatOrNone = Field(default=None, validation_alias="orb_pct")
    free_throw_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="ft_rate")
    opponent_effective_field_goal_percentage: BRFloatOrNone = Field(default=None, validation_alias="opp_efg_pct")
    opponent_turnover_percentage: BRFloatOrNone = Field(default=None, validation_alias="opp_tov_pct")
    defensive_rebound_percentage: BRFloatOrNone = Field(default=None, validation_alias="drb_pct")
    opponent_free_throw_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="opp_ft_rate")


register("team_misc_four_factors", TeamMiscFourFactorsRow)


class TeamOpponentStatsRow(BRRow, _GBasedTotalStats, _PercentageStats):
    """Subset of ``#team_and_opponent`` exposing only the opponent totals contract."""

    stat_type: str = Field(validation_alias=AliasChoices("stat_type", "team_name_abbr"))


register("team_opponent_stats", TeamOpponentStatsRow)


class TeamTransactionsRow(BRRow):
    """Row from a team's transaction-list page.

    Transaction-list pages are ``<ul>``-based rather than tabular; the raw dict
    shape comes from :func:`courtside_data.tables.parse_transaction_list`.
    Dates are full-month strings (e.g. "October 16, 2018") so they are kept as
    strings to avoid lossy parsing.
    """

    date: str = Field(validation_alias="date")
    transaction: str = Field(validation_alias="transaction")


register("team_transactions", TeamTransactionsRow)


class TeamSplitsRow(BRRow, _GBasedTotalStats, _PercentageStats):
    """Row from a team's ``#team_splits`` table."""

    split_type: str = Field(validation_alias="split_type")
    value: str = Field(validation_alias="value")


register("team_splits", TeamSplitsRow)


class TeamContractsRow(BRRow):
    """Row from a team's contracts table (``table#contracts``).

    The raw HTML exposes per-year salaries as ``y1`` through ``y6``;
    ``salary`` maps to the first year and ``years_remaining`` is derived from
    the count of non-empty yearly columns.
    """

    player: str = Field(validation_alias="player")
    salary: BRSalary = Field(validation_alias=AliasChoices("y1", "salary"))
    years_remaining: BRIntOrNone = Field(default=None, validation_alias="years_remaining")

    @model_validator(mode="before")
    @classmethod
    def _derive_years_remaining(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        current = data.get("years_remaining")
        if current in {None, "", "\xa0"}:
            count = sum(1 for i in range(1, 7) if str(data.get(f"y{i}", "")).strip() not in {"", "\xa0"})
            data["years_remaining"] = str(count) if count else ""
        return data


register("team_contracts", TeamContractsRow)


class TeamLineupsRow(BRRow, _GBasedTotalStats, _PercentageStats):
    """Row from a team's ``#lineups_5-man_`` table."""

    lineup: str = Field(validation_alias="lineup")


register("team_lineups", TeamLineupsRow)


class TeamStartingLineupsRow(BRRow, _GBasedTotalStats, _PercentageStats):
    """Row from a team's ``#starting_lineups_po0`` table."""

    player: str = Field(validation_alias="player")


register("team_starting_lineups", TeamStartingLineupsRow)


class TeamOnOffRow(BRRow, _GBasedTotalStats, _PercentageStats):
    """Row from a team's ``#on_off`` table."""

    situation: str = Field(validation_alias="situation")


register("team_on_off", TeamOnOffRow)


class FranchiseHistoryRow(BRRow):
    """Row from a franchise history table (``table#{team_abbreviation}``)."""

    season: str = Field(validation_alias="season")
    team_abbreviation: str = Field(validation_alias=AliasChoices("team_abbreviation", "team_name_abbr", "team_name"))
    wins: BRInt = Field(validation_alias="wins")
    losses: BRInt = Field(validation_alias="losses")
    playoffs: str | None = Field(default=None, validation_alias=AliasChoices("playoffs", "playoffs_text"))


register("franchise_history", FranchiseHistoryRow)
