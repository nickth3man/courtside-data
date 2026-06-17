"""Row schemas for team-scoped Basketball-Reference endpoints."""

from __future__ import annotations

from pydantic import AliasChoices, Field

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    PositionsField,
    SecondsPlayedOrNone,
    StrOrNone,
)


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
    team_name: StrOrNone = Field(default=None, validation_alias="team_name")
    date_update: StrOrNone = Field(default=None, validation_alias="date_update")
    note: StrOrNone = Field(default=None, validation_alias="note")


register("team_injury_report", TeamInjuryReportRow)


class TeamAndOpponentRow(BRRow):
    """Row from a team's ``#team_and_opponent`` table.

    Contains both the team's own totals and the opponent's aggregated totals.
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


register("team_and_opponent", TeamAndOpponentRow)


class TeamMiscFourFactorsRow(BRRow):
    """Row from a team's ``#team_misc`` four-factors table."""

    player: StrOrNone = Field(default=None, validation_alias="player")
    wins: BRIntOrNone = Field(default=None, validation_alias="wins")
    losses: BRIntOrNone = Field(default=None, validation_alias="losses")
    wins_pyth: BRFloatOrNone = Field(default=None, validation_alias="wins_pyth")
    losses_pyth: BRFloatOrNone = Field(default=None, validation_alias="losses_pyth")
    mov: BRFloatOrNone = Field(default=None, validation_alias="mov")
    sos: BRFloatOrNone = Field(default=None, validation_alias="sos")
    srs: BRFloatOrNone = Field(default=None, validation_alias="srs")
    off_rtg: BRFloatOrNone = Field(default=None, validation_alias="off_rtg")
    def_rtg: BRFloatOrNone = Field(default=None, validation_alias="def_rtg")
    pace: BRFloatOrNone = Field(default=None, validation_alias="pace")
    fta_per_fga_pct: BRFloatOrNone = Field(default=None, validation_alias="fta_per_fga_pct")
    fg3a_per_fga_pct: BRFloatOrNone = Field(default=None, validation_alias="fg3a_per_fga_pct")
    efg_pct: BRFloatOrNone = Field(default=None, validation_alias="efg_pct")
    tov_pct: BRFloatOrNone = Field(default=None, validation_alias="tov_pct")
    orb_pct: BRFloatOrNone = Field(default=None, validation_alias="orb_pct")
    ft_rate: BRFloatOrNone = Field(default=None, validation_alias="ft_rate")
    opp_efg_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_efg_pct")
    opp_tov_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_tov_pct")
    drb_pct: BRFloatOrNone = Field(default=None, validation_alias="drb_pct")
    opp_ft_rate: BRFloatOrNone = Field(default=None, validation_alias="opp_ft_rate")
    arena_name: StrOrNone = Field(default=None, validation_alias="arena_name")
    attendance: BRIntOrNone = Field(default=None, validation_alias="attendance")


register("team_misc_four_factors", TeamMiscFourFactorsRow)


class TeamOpponentStatsRow(BRRow):
    """Subset of ``#team_and_opponent`` exposing only the opponent totals contract."""

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
    from_team_abbreviations: list[str] = Field(default_factory=list, validation_alias="from_team_abbreviations")
    to_team_abbreviations: list[str] = Field(default_factory=list, validation_alias="to_team_abbreviations")
    linked_resources: list[dict[str, str]] = Field(default_factory=list, validation_alias="linked_resources")


register("team_transactions", TeamTransactionsRow)


class TeamSplitsRow(BRRow):
    """Row from a team's ``#team_splits`` table."""

    split_id: StrOrNone = Field(default=None, validation_alias="split_id")
    split_value: StrOrNone = Field(default=None, validation_alias="split_value")
    g: BRIntOrNone = Field(default=None, validation_alias="g")
    wins: BRIntOrNone = Field(default=None, validation_alias="wins")
    losses: BRIntOrNone = Field(default=None, validation_alias="losses")
    fg: BRFloatOrNone = Field(default=None, validation_alias="fg")
    fga: BRFloatOrNone = Field(default=None, validation_alias="fga")
    fg3: BRFloatOrNone = Field(default=None, validation_alias="fg3")
    fg3a: BRFloatOrNone = Field(default=None, validation_alias="fg3a")
    ft: BRFloatOrNone = Field(default=None, validation_alias="ft")
    fta: BRFloatOrNone = Field(default=None, validation_alias="fta")
    orb: BRFloatOrNone = Field(default=None, validation_alias="orb")
    trb: BRFloatOrNone = Field(default=None, validation_alias="trb")
    ast: BRFloatOrNone = Field(default=None, validation_alias="ast")
    stl: BRFloatOrNone = Field(default=None, validation_alias="stl")
    blk: BRFloatOrNone = Field(default=None, validation_alias="blk")
    tov: BRFloatOrNone = Field(default=None, validation_alias="tov")
    pf: BRFloatOrNone = Field(default=None, validation_alias="pf")
    pts: BRFloatOrNone = Field(default=None, validation_alias="pts")
    fg_pct: BRPercentage = Field(default=None, validation_alias="fg_pct")
    fg3_pct: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    efg_pct: BRPercentage = Field(default=None, validation_alias="efg_pct")
    ft_pct: BRPercentage = Field(default=None, validation_alias="ft_pct")
    ts_pct: BRPercentage = Field(default=None, validation_alias="ts_pct")
    opp_fg: BRFloatOrNone = Field(default=None, validation_alias="opp_fg")
    opp_fga: BRFloatOrNone = Field(default=None, validation_alias="opp_fga")
    opp_fg3: BRFloatOrNone = Field(default=None, validation_alias="opp_fg3")
    opp_fg3a: BRFloatOrNone = Field(default=None, validation_alias="opp_fg3a")
    opp_ft: BRFloatOrNone = Field(default=None, validation_alias="opp_ft")
    opp_fta: BRFloatOrNone = Field(default=None, validation_alias="opp_fta")
    opp_orb: BRFloatOrNone = Field(default=None, validation_alias="opp_orb")
    opp_trb: BRFloatOrNone = Field(default=None, validation_alias="opp_trb")
    opp_ast: BRFloatOrNone = Field(default=None, validation_alias="opp_ast")
    opp_stl: BRFloatOrNone = Field(default=None, validation_alias="opp_stl")
    opp_blk: BRFloatOrNone = Field(default=None, validation_alias="opp_blk")
    opp_tov: BRFloatOrNone = Field(default=None, validation_alias="opp_tov")
    opp_pf: BRFloatOrNone = Field(default=None, validation_alias="opp_pf")
    opp_pts: BRFloatOrNone = Field(default=None, validation_alias="opp_pts")
    opp_fg_pct: BRPercentage = Field(default=None, validation_alias="opp_fg_pct")
    opp_fg3_pct: BRPercentage = Field(default=None, validation_alias="opp_fg3_pct")
    opp_efg_pct: BRPercentage = Field(default=None, validation_alias="opp_efg_pct")
    opp_ft_pct: BRPercentage = Field(default=None, validation_alias="opp_ft_pct")
    opp_ts_pct: BRPercentage = Field(default=None, validation_alias="opp_ts_pct")


register("team_splits", TeamSplitsRow)


class TeamContractsRow(BRRow):
    """Row from a team's contracts table (``table#contracts``).

    The raw HTML exposes per-year salaries as ``y1`` through ``y6``
    plus age, guaranteed remainder, and player name.
    """

    player: str = Field(validation_alias="player")
    age_today: StrOrNone = Field(default=None, validation_alias="age_today")
    y1: StrOrNone = Field(default=None, validation_alias="y1")
    y2: StrOrNone = Field(default=None, validation_alias="y2")
    y3: StrOrNone = Field(default=None, validation_alias="y3")
    y4: StrOrNone = Field(default=None, validation_alias="y4")
    y5: StrOrNone = Field(default=None, validation_alias="y5")
    y6: StrOrNone = Field(default=None, validation_alias="y6")
    remain_gtd: StrOrNone = Field(default=None, validation_alias="remain_gtd")


register("team_contracts", TeamContractsRow)


class TeamLineupsRow(BRRow):
    """Row from a team's ``#lineups_5-man_`` table."""

    lineup: StrOrNone = Field(default=None, validation_alias="lineup")
    mp: SecondsPlayedOrNone = Field(default=None, validation_alias="mp")
    diff_pts: BRFloatOrNone = Field(default=None, validation_alias="diff_pts")
    diff_fg: BRFloatOrNone = Field(default=None, validation_alias="diff_fg")
    diff_fga: BRFloatOrNone = Field(default=None, validation_alias="diff_fga")
    diff_fg_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_fg_pct")
    diff_fg3: BRFloatOrNone = Field(default=None, validation_alias="diff_fg3")
    diff_fg3a: BRFloatOrNone = Field(default=None, validation_alias="diff_fg3a")
    diff_fg3_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_fg3_pct")
    diff_efg_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_efg_pct")
    diff_ft: BRFloatOrNone = Field(default=None, validation_alias="diff_ft")
    diff_fta: BRFloatOrNone = Field(default=None, validation_alias="diff_fta")
    diff_ft_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_ft_pct")
    diff_orb: BRFloatOrNone = Field(default=None, validation_alias="diff_orb")
    diff_orb_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_orb_pct")
    diff_drb: BRFloatOrNone = Field(default=None, validation_alias="diff_drb")
    diff_drb_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_drb_pct")
    diff_trb: BRFloatOrNone = Field(default=None, validation_alias="diff_trb")
    diff_trb_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_trb_pct")
    diff_ast: BRFloatOrNone = Field(default=None, validation_alias="diff_ast")
    diff_stl: BRFloatOrNone = Field(default=None, validation_alias="diff_stl")
    diff_blk: BRFloatOrNone = Field(default=None, validation_alias="diff_blk")
    diff_tov: BRFloatOrNone = Field(default=None, validation_alias="diff_tov")
    diff_pf: BRFloatOrNone = Field(default=None, validation_alias="diff_pf")


register("team_lineups", TeamLineupsRow)


class TeamStartingLineupsRow(BRRow):
    """Row from a team's ``#starting_lineups_po0`` table."""

    g: BRIntOrNone = Field(default=None, validation_alias="g")
    date_game: StrOrNone = Field(default=None, validation_alias="date_game")
    game_start_time: StrOrNone = Field(default=None, validation_alias="game_start_time")
    network: StrOrNone = Field(default=None, validation_alias="network")
    box_score_text: StrOrNone = Field(default=None, validation_alias="box_score_text")
    game_location: StrOrNone = Field(default=None, validation_alias="game_location")
    opp_name: StrOrNone = Field(default=None, validation_alias="opp_name")
    game_result: StrOrNone = Field(default=None, validation_alias="game_result")
    overtimes: StrOrNone = Field(default=None, validation_alias="overtimes")
    pts: BRIntOrNone = Field(default=None, validation_alias="pts")
    opp_pts: BRIntOrNone = Field(default=None, validation_alias="opp_pts")
    wins: BRIntOrNone = Field(default=None, validation_alias="wins")
    losses: BRIntOrNone = Field(default=None, validation_alias="losses")
    game_starters: StrOrNone = Field(default=None, validation_alias="game_starters")


register("team_starting_lineups", TeamStartingLineupsRow)


class TeamOnOffRow(BRRow):
    """Row from a team's ``#on_off`` table."""

    player: StrOrNone = Field(default=None, validation_alias="player")
    split_id: StrOrNone = Field(default=None, validation_alias="split_id")
    mp: BRIntOrNone = Field(default=None, validation_alias="mp")
    efg_pct: BRFloatOrNone = Field(default=None, validation_alias="efg_pct")
    orb_pct: BRFloatOrNone = Field(default=None, validation_alias="orb_pct")
    drb_pct: BRFloatOrNone = Field(default=None, validation_alias="drb_pct")
    trb_pct: BRFloatOrNone = Field(default=None, validation_alias="trb_pct")
    ast_pct: BRFloatOrNone = Field(default=None, validation_alias="ast_pct")
    stl_pct: BRFloatOrNone = Field(default=None, validation_alias="stl_pct")
    blk_pct: BRFloatOrNone = Field(default=None, validation_alias="blk_pct")
    tov_pct: BRFloatOrNone = Field(default=None, validation_alias="tov_pct")
    pace: BRFloatOrNone = Field(default=None, validation_alias="pace")
    off_rtg: BRFloatOrNone = Field(default=None, validation_alias="off_rtg")
    opp_efg_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_efg_pct")
    opp_orb_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_orb_pct")
    opp_drb_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_drb_pct")
    opp_trb_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_trb_pct")
    opp_ast_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_ast_pct")
    opp_stl_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_stl_pct")
    opp_blk_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_blk_pct")
    opp_tov_pct: BRFloatOrNone = Field(default=None, validation_alias="opp_tov_pct")
    opp_pace: BRFloatOrNone = Field(default=None, validation_alias="opp_pace")
    opp_off_rtg: BRFloatOrNone = Field(default=None, validation_alias="opp_off_rtg")
    diff_efg_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_efg_pct")
    diff_orb_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_orb_pct")
    diff_drb_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_drb_pct")
    diff_trb_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_trb_pct")
    diff_ast_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_ast_pct")
    diff_stl_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_stl_pct")
    diff_blk_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_blk_pct")
    diff_tov_pct: BRFloatOrNone = Field(default=None, validation_alias="diff_tov_pct")
    diff_pace: BRFloatOrNone = Field(default=None, validation_alias="diff_pace")
    diff_off_rtg: BRFloatOrNone = Field(default=None, validation_alias="diff_off_rtg")


register("team_on_off", TeamOnOffRow)


class FranchiseHistoryRow(BRRow):
    """Row from a franchise history table (``table#{team_abbreviation}``)."""

    season: StrOrNone = Field(default=None, validation_alias="season")
    lg_id: StrOrNone = Field(default=None, validation_alias="lg_id")
    team_name: StrOrNone = Field(
        default=None,
        validation_alias=AliasChoices("team_name", "team_abbreviation", "team_name_abbr"),
    )
    wins: BRInt = Field(validation_alias="wins")
    losses: BRInt = Field(validation_alias="losses")
    win_loss_pct: BRFloatOrNone = Field(default=None, validation_alias="win_loss_pct")
    rank_team: StrOrNone = Field(default=None, validation_alias="rank_team")
    srs: BRFloatOrNone = Field(default=None, validation_alias="srs")
    pace: BRFloatOrNone = Field(default=None, validation_alias="pace")
    pace_rel: BRFloatOrNone = Field(default=None, validation_alias="pace_rel")
    off_rtg: BRFloatOrNone = Field(default=None, validation_alias="off_rtg")
    off_rtg_rel: BRFloatOrNone = Field(default=None, validation_alias="off_rtg_rel")
    def_rtg: BRFloatOrNone = Field(default=None, validation_alias="def_rtg")
    def_rtg_rel: BRFloatOrNone = Field(default=None, validation_alias="def_rtg_rel")
    rank_team_playoffs: StrOrNone = Field(default=None, validation_alias="rank_team_playoffs")
    coaches: StrOrNone = Field(default=None, validation_alias="coaches")
    top_ws: StrOrNone = Field(default=None, validation_alias="top_ws")


register("franchise_history", FranchiseHistoryRow)
