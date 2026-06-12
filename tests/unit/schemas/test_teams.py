"""Unit tests for the row schemas in :mod:`courtside_data.schemas.teams`.

Each model gets a focused test class that covers the happy path, an empty or
optional cell, and a missing required ``data-stat`` alias.
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from courtside_data.data import Position
from courtside_data.schemas.teams import (
    FranchiseHistoryRow,
    TeamAndOpponentRow,
    TeamContractsRow,
    TeamInjuryReportRow,
    TeamLineupsRow,
    TeamMiscFourFactorsRow,
    TeamOnOffRow,
    TeamOpponentStatsRow,
    TeamRosterRow,
    TeamSplitsRow,
    TeamStartingLineupsRow,
    TeamTransactionsRow,
)


class TestTeamRosterRow:
    def test_happy_path(self):
        row = TeamRosterRow.model_validate(
            {
                "player": "LeBron James",
                "number": "23",
                "pos": "SF",
                "height": "6-9",
                "weight": "250",
                "birth_date": "December 30, 1984",
                "flag": "",
                "years_experience": "20",
                "college": "No College",
            }
        )
        assert row.player == "LeBron James"
        assert row.number == "23"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.height == "6-9"
        assert row.weight == 250
        assert row.birth_date == "December 30, 1984"
        assert row.flag == ""
        assert row.years_experience == "20"
        assert row.college == "No College"

    def test_optional_college_parses_to_none(self):
        row = TeamRosterRow.model_validate(
            {
                "player": "LeBron James",
                "number": "23",
                "pos": "PG-SF",
                "height": "6-9",
                "weight": "250",
                "birth_date": "December 30, 1984",
                "flag": "",
                "years_experience": "20",
            }
        )
        assert row.college is None
        assert row.positions == [Position.POINT_GUARD, Position.SMALL_FORWARD]

    def test_missing_required_weight_raises(self):
        with pytest.raises(ValidationError):
            TeamRosterRow.model_validate(
                {
                    "player": "LeBron James",
                    "number": "23",
                    "pos": "SF",
                    "height": "6-9",
                    "birth_date": "December 30, 1984",
                    "flag": "",
                    "years_experience": "20",
                    "college": "No College",
                }
            )


class TestTeamInjuryReportRow:
    def test_happy_path(self):
        row = TeamInjuryReportRow.model_validate(
            {
                "player": "LeBron James",
                "date": "Tue, Oct 30, 2018",
                "description": "Rest",
            }
        )
        assert row.player == "LeBron James"
        assert row.date == date(2018, 10, 30)
        assert row.description == "Rest"

    def test_empty_date_raises(self):
        # Injury rows are only meaningful with a real date; the validator
        # rejects empty strings.
        with pytest.raises(ValidationError):
            TeamInjuryReportRow.model_validate({"player": "LeBron James", "date": "", "description": "Rest"})

    def test_missing_required_description_raises(self):
        with pytest.raises(ValidationError):
            TeamInjuryReportRow.model_validate({"player": "LeBron James", "date": "Tue, Oct 30, 2018"})


class TestTeamAndOpponentRow:
    def test_happy_path(self):
        row = TeamAndOpponentRow.model_validate(
            {
                "stat_type": "Team",
                "g": "82",
                "mp": "19872",
                "fg": "3500",
                "fga": "7500",
                "fg_pct": "0.467",
                "fg3": "1000",
                "fg3a": "2700",
                "fg3_pct": "0.370",
                "ft": "1500",
                "fta": "1900",
                "ft_pct": "0.789",
                "orb": "850",
                "drb": "2700",
                "trb": "3550",
                "ast": "2200",
                "stl": "700",
                "blk": "450",
                "tov": "1200",
                "pf": "1800",
                "pts": "9500",
            }
        )
        assert row.stat_type == "Team"
        assert row.games_played == 82
        assert row.minutes_played == 19872
        assert row.made_field_goals == 3500
        assert row.field_goal_percentage == pytest.approx(0.467)
        assert row.total_rebounds == 3550
        assert row.points == 9500

    def test_optional_stat_block_cells_parse_to_none(self):
        # Only the required ``stat_type`` is present; every other column is
        # optional on the g-based stat block.
        row = TeamAndOpponentRow.model_validate({"stat_type": "Lg"})
        assert row.stat_type == "Lg"
        assert row.games_played is None
        assert row.points is None
        assert row.field_goal_percentage is None

    def test_alias_team_name_abbr_fallback(self):
        # On commented tables BR sometimes uses ``team_name_abbr`` instead of
        # ``stat_type`` for the row label.
        row = TeamAndOpponentRow.model_validate({"team_name_abbr": "LAL", "g": "82", "pts": "9500"})
        assert row.stat_type == "LAL"
        assert row.games_played == 82
        assert row.points == 9500

    def test_missing_required_stat_type_raises(self):
        with pytest.raises(ValidationError):
            TeamAndOpponentRow.model_validate({"g": "82", "pts": "9500"})


class TestTeamMiscFourFactorsRow:
    def test_happy_path(self):
        row = TeamMiscFourFactorsRow.model_validate(
            {
                "stat_type": "Lg",
                "pace": "100.2",
                "efg_pct": "0.532",
                "tov_pct": "0.123",
                "orb_pct": "0.250",
                "ft_rate": "0.250",
                "opp_efg_pct": "0.510",
                "opp_tov_pct": "0.140",
                "drb_pct": "0.750",
                "opp_ft_rate": "0.220",
            }
        )
        assert row.stat_type == "Lg"
        assert row.pace == pytest.approx(100.2)
        assert row.effective_field_goal_percentage == pytest.approx(0.532)
        assert row.turnover_percentage == pytest.approx(0.123)
        assert row.opponent_effective_field_goal_percentage == pytest.approx(0.510)
        assert row.defensive_rebound_percentage == pytest.approx(0.750)

    def test_optional_misc_cells_parse_to_none(self):
        row = TeamMiscFourFactorsRow.model_validate({"stat_type": "Lg"})
        assert row.pace is None
        assert row.turnover_percentage is None

    def test_missing_required_stat_type_raises(self):
        with pytest.raises(ValidationError):
            TeamMiscFourFactorsRow.model_validate({"pace": "100.2"})


class TestTeamOpponentStatsRow:
    """The ``#team_and_opponent`` table exposes a different output contract
    for opponents; this is its own row model with the same data-stat layout.
    """

    def test_happy_path(self):
        row = TeamOpponentStatsRow.model_validate(
            {
                "stat_type": "Opponent",
                "g": "82",
                "mp": "19872",
                "pts": "9000",
                "fg_pct": "0.450",
            }
        )
        assert row.stat_type == "Opponent"
        assert row.games_played == 82
        assert row.points == 9000
        assert row.field_goal_percentage == pytest.approx(0.450)

    def test_optional_cells_parse_to_none(self):
        row = TeamOpponentStatsRow.model_validate({"stat_type": "Opponent"})
        assert row.games_played is None
        assert row.points is None

    def test_missing_required_stat_type_raises(self):
        with pytest.raises(ValidationError):
            TeamOpponentStatsRow.model_validate({"g": "82"})


class TestTeamTransactionsRow:
    def test_happy_path(self):
        row = TeamTransactionsRow.model_validate(
            {
                "date": "October 16, 2018",
                "transaction": "Traded Player X to Team Y for cash.",
            }
        )
        assert row.date == "October 16, 2018"
        assert row.transaction == "Traded Player X to Team Y for cash."

    def test_missing_required_transaction_raises(self):
        with pytest.raises(ValidationError):
            TeamTransactionsRow.model_validate({"date": "October 16, 2018"})


class TestTeamSplitsRow:
    def test_happy_path(self):
        row = TeamSplitsRow.model_validate(
            {
                "split_type": "Value",
                "value": "Home",
                "g": "41",
                "mp": "9920",
                "fg": "1750",
                "fga": "3700",
                "fg_pct": "0.473",
                "fg3": "500",
                "fg3a": "1350",
                "fg3_pct": "0.370",
                "ft": "750",
                "fta": "950",
                "ft_pct": "0.789",
                "orb": "425",
                "drb": "1350",
                "trb": "1775",
                "ast": "1100",
                "stl": "350",
                "blk": "225",
                "tov": "600",
                "pf": "900",
                "pts": "4750",
            }
        )
        assert row.split_type == "Value"
        assert row.value == "Home"
        assert row.games_played == 41
        assert row.points == 4750
        assert row.three_point_field_goal_percentage == pytest.approx(0.370)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamSplitsRow.model_validate({"split_type": "Value", "value": "Home"})
        assert row.games_played is None
        assert row.points is None

    def test_missing_required_split_type_raises(self):
        with pytest.raises(ValidationError):
            TeamSplitsRow.model_validate({"value": "Home", "g": "41"})


class TestTeamContractsRow:
    def test_single_year_contract(self):
        # Pascal Siakam's final contract year: only y1 populated, y2-y6 empty.
        row = TeamContractsRow.model_validate(
            {
                "player": "Pascal Siakam",
                "y1": "$37,893,408",
                "y2": "",
                "y3": "",
                "y4": "",
                "y5": "",
                "y6": "",
            }
        )
        assert row.player == "Pascal Siakam"
        assert row.salary == 37893408
        assert row.years_remaining == 1

    def test_six_year_contract(self):
        # Jaylen Brown's supermax: y1-y6 all populated.
        row = TeamContractsRow.model_validate(
            {
                "player": "Jaylen Brown",
                "y1": "$31,830,357",
                "y2": "$49,700,000",
                "y3": "$53,676,000",
                "y4": "$57,652,000",
                "y5": "$61,628,000",
                "y6": "$65,604,000",
            }
        )
        assert row.player == "Jaylen Brown"
        assert row.salary == 31830357
        assert row.years_remaining == 6

    def test_explicit_years_remaining_overrides_derivation(self):
        # If BR pre-fills a "years_remaining" cell, use it verbatim.
        row = TeamContractsRow.model_validate(
            {
                "player": "Gary Trent Jr.",
                "y1": "$18,560,000",
                "y2": "",
                "y3": "",
                "y4": "",
                "y5": "",
                "y6": "",
                "years_remaining": "1",
            }
        )
        assert row.salary == 18560000
        assert row.years_remaining == 1

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            TeamContractsRow.model_validate({"y1": "$31,830,357", "y2": "$49,700,000"})


class TestTeamLineupsRow:
    def test_happy_path(self):
        row = TeamLineupsRow.model_validate(
            {
                "lineup": "A. Davis - L. James - R. Westbrook - M. Monk - C. Anthony",
                "g": "10",
                "mp": "200",
                "fg": "60",
                "fga": "120",
                "fg_pct": "0.500",
                "fg3": "20",
                "fg3a": "50",
                "fg3_pct": "0.400",
                "ft": "30",
                "fta": "40",
                "ft_pct": "0.750",
                "orb": "15",
                "drb": "50",
                "trb": "65",
                "ast": "40",
                "stl": "12",
                "blk": "8",
                "tov": "20",
                "pf": "25",
                "pts": "170",
            }
        )
        assert row.lineup == "A. Davis - L. James - R. Westbrook - M. Monk - C. Anthony"
        assert row.games_played == 10
        assert row.points == 170

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamLineupsRow.model_validate({"lineup": "A. Davis - L. James - M. Monk - C. Anthony - D. Russell"})
        assert row.games_played is None
        assert row.points is None

    def test_missing_required_lineup_raises(self):
        with pytest.raises(ValidationError):
            TeamLineupsRow.model_validate({"g": "10", "pts": "170"})


class TestTeamStartingLineupsRow:
    def test_happy_path(self):
        row = TeamStartingLineupsRow.model_validate(
            {
                "player": "L. James",
                "g": "82",
                "mp": "2500",
                "fg": "650",
                "fga": "1300",
                "fg_pct": "0.500",
                "pts": "1800",
            }
        )
        assert row.player == "L. James"
        assert row.games_played == 82
        assert row.points == 1800
        assert row.field_goal_percentage == pytest.approx(0.500)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamStartingLineupsRow.model_validate({"player": "L. James"})
        assert row.games_played is None
        assert row.points is None

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            TeamStartingLineupsRow.model_validate({"g": "82", "pts": "1800"})


class TestTeamOnOffRow:
    def test_happy_path(self):
        row = TeamOnOffRow.model_validate(
            {
                "situation": "On",
                "g": "82",
                "mp": "2000",
                "fg": "400",
                "fga": "900",
                "fg_pct": "0.444",
                "pts": "1100",
            }
        )
        assert row.situation == "On"
        assert row.games_played == 82
        assert row.field_goal_percentage == pytest.approx(0.444)
        assert row.points == 1100

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamOnOffRow.model_validate({"situation": "Off"})
        assert row.games_played is None
        assert row.points is None

    def test_missing_required_situation_raises(self):
        with pytest.raises(ValidationError):
            TeamOnOffRow.model_validate({"g": "82", "pts": "1100"})


class TestFranchiseHistoryRow:
    def test_happy_path(self):
        row = FranchiseHistoryRow.model_validate(
            {
                "season": "2020-21",
                "team_abbreviation": "LAL",
                "wins": "42",
                "losses": "30",
                "playoffs": "Won Finals",
            }
        )
        assert row.season == "2020-21"
        assert row.team_abbreviation == "LAL"
        assert row.wins == 42
        assert row.losses == 30
        assert row.playoffs == "Won Finals"

    def test_optional_playoffs_parses_to_none(self):
        # Seasons that missed the playoffs have an empty ``playoffs`` cell.
        row = FranchiseHistoryRow.model_validate(
            {
                "season": "2018-19",
                "team_abbreviation": "LAL",
                "wins": "37",
                "losses": "45",
            }
        )
        assert row.season == "2018-19"
        assert row.wins == 37
        assert row.losses == 45
        assert row.playoffs is None

    def test_team_name_abbr_alias_fallback(self):
        # Some historical seasons expose ``team_name_abbr`` instead of
        # ``team_abbreviation`` for the franchise column.
        row = FranchiseHistoryRow.model_validate(
            {
                "season": "2017-18",
                "team_name_abbr": "BOS",
                "wins": "55",
                "losses": "27",
            }
        )
        assert row.team_abbreviation == "BOS"

    def test_missing_required_wins_raises(self):
        with pytest.raises(ValidationError):
            FranchiseHistoryRow.model_validate(
                {
                    "season": "2020-21",
                    "team_abbreviation": "LAL",
                    "losses": "30",
                }
            )
