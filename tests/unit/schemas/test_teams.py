"""Unit tests for the row schemas in :mod:`courtside_data.schemas.teams`.

Each model gets a focused test class that covers the happy path, an empty or
optional cell, and a missing required ``data-stat`` alias.
"""

from __future__ import annotations

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
                "team_name": "Los Angeles Lakers",
                "date_update": "Tue, Oct 30, 2018",
                "note": "Rest",
            }
        )
        assert row.player == "LeBron James"
        assert row.team_name == "Los Angeles Lakers"
        assert row.date_update == "Tue, Oct 30, 2018"
        assert row.note == "Rest"

    def test_optional_cells_become_none(self):
        row = TeamInjuryReportRow.model_validate({"player": "LeBron James"})
        assert row.team_name is None
        assert row.date_update is None
        assert row.note is None

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            TeamInjuryReportRow.model_validate({"date_update": "Tue, Oct 30, 2018", "note": "Rest"})


class TestTeamAndOpponentRow:
    def test_happy_path(self):
        row = TeamAndOpponentRow.model_validate(
            {
                "player": "Team",
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
        assert row.player == "Team"
        assert row.g == 82
        assert row.mp == 19872
        assert row.fg == 3500
        assert row.fg_pct == pytest.approx(0.467)
        assert row.trb == 3550
        assert row.pts == 9500

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamAndOpponentRow.model_validate({})
        assert row.player is None
        assert row.g is None
        assert row.pts is None
        assert row.fg_pct is None

    def test_empty_model_is_valid(self):
        """All fields are optional; an empty dict produces a valid model."""
        row = TeamAndOpponentRow.model_validate({})
        assert row.g is None
        assert row.pts is None


class TestTeamMiscFourFactorsRow:
    def test_happy_path(self):
        row = TeamMiscFourFactorsRow.model_validate(
            {
                "player": "Team",
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
        assert row.player == "Team"
        assert row.pace == pytest.approx(100.2)
        assert row.efg_pct == pytest.approx(0.532)
        assert row.tov_pct == pytest.approx(0.123)
        assert row.opp_efg_pct == pytest.approx(0.510)
        assert row.drb_pct == pytest.approx(0.750)

    def test_optional_misc_cells_parse_to_none(self):
        row = TeamMiscFourFactorsRow.model_validate({})
        assert row.player is None
        assert row.pace is None
        assert row.tov_pct is None

    def test_all_fields_optional_empty_dict_is_valid(self):
        row = TeamMiscFourFactorsRow.model_validate({})
        assert row.wins is None
        assert row.losses is None


class TestTeamOpponentStatsRow:
    """The ``#team_and_opponent`` table exposes a different output contract
    for opponents; this is its own row model with the same data-stat layout.
    """

    def test_happy_path(self):
        row = TeamOpponentStatsRow.model_validate(
            {
                "player": "Opponent",
                "g": "82",
                "mp": "19872",
                "pts": "9000",
                "fg_pct": "0.450",
            }
        )
        assert row.player == "Opponent"
        assert row.g == 82
        assert row.pts == 9000
        assert row.fg_pct == pytest.approx(0.450)

    def test_optional_cells_parse_to_none(self):
        row = TeamOpponentStatsRow.model_validate({})
        assert row.g is None
        assert row.pts is None

    def test_empty_model_is_valid(self):
        """All fields are optional."""
        row = TeamOpponentStatsRow.model_validate({})
        assert row.player is None


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
                "split_id": "Value",
                "split_value": "Home",
                "g": "41",
                "wins": "25",
                "losses": "16",
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
                "trb": "1775",
                "ast": "1100",
                "stl": "350",
                "blk": "225",
                "tov": "600",
                "pf": "900",
                "pts": "4750",
            }
        )
        assert row.split_id == "Value"
        assert row.split_value == "Home"
        assert row.g == 41
        assert row.pts == 4750
        assert row.fg3_pct == pytest.approx(0.370)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamSplitsRow.model_validate({})
        assert row.split_id is None
        assert row.split_value is None
        assert row.g is None
        assert row.pts is None

    def test_all_fields_optional_empty_dict_is_valid(self):
        row = TeamSplitsRow.model_validate({})
        assert row.g is None


class TestTeamContractsRow:
    def test_single_year_contract(self):
        # Pascal Siakam's final contract year: only y1 populated, y2-y6 empty.
        row = TeamContractsRow.model_validate(
            {
                "player": "Pascal Siakam",
                "age_today": "29",
                "y1": "$37,893,408",
                "y2": "",
                "y3": "",
                "y4": "",
                "y5": "",
                "y6": "",
                "remain_gtd": "$37,893,408",
            }
        )
        assert row.player == "Pascal Siakam"
        assert row.age_today == "29"
        assert row.y1 == "$37,893,408"
        assert row.y2 is None
        assert row.y3 is None
        assert row.y4 is None
        assert row.y5 is None
        assert row.y6 is None
        assert row.remain_gtd == "$37,893,408"

    def test_six_year_contract(self):
        # Jaylen Brown's supermax: y1-y6 all populated.
        row = TeamContractsRow.model_validate(
            {
                "player": "Jaylen Brown",
                "age_today": "27",
                "y1": "$31,830,357",
                "y2": "$49,700,000",
                "y3": "$53,676,000",
                "y4": "$57,652,000",
                "y5": "$61,628,000",
                "y6": "$65,604,000",
                "remain_gtd": "$320,090,357",
            }
        )
        assert row.player == "Jaylen Brown"
        assert row.y1 == "$31,830,357"
        assert row.y2 == "$49,700,000"
        assert row.y6 == "$65,604,000"
        assert row.remain_gtd == "$320,090,357"

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            TeamContractsRow.model_validate({"y1": "$31,830,357", "y2": "$49,700,000"})


class TestTeamLineupsRow:
    def test_happy_path(self):
        row = TeamLineupsRow.model_validate(
            {
                "lineup": "A. Davis - L. James - R. Westbrook - M. Monk - C. Anthony",
                "mp": "200:00",
                "diff_pts": "10.5",
                "diff_fg": "5.0",
                "diff_fga": "8.0",
                "diff_fg_pct": "0.025",
                "diff_fg3": "2.0",
                "diff_fg3a": "4.0",
                "diff_fg3_pct": "0.015",
                "diff_efg_pct": "0.030",
                "diff_ft": "3.0",
                "diff_fta": "4.0",
                "diff_ft_pct": "0.010",
                "diff_orb": "1.5",
                "diff_orb_pct": "0.020",
                "diff_drb": "4.0",
                "diff_drb_pct": "0.015",
                "diff_trb": "5.5",
                "diff_trb_pct": "0.018",
                "diff_ast": "3.0",
                "diff_stl": "1.0",
                "diff_blk": "0.5",
                "diff_tov": "-1.0",
                "diff_pf": "-0.5",
            }
        )
        assert row.lineup == "A. Davis - L. James - R. Westbrook - M. Monk - C. Anthony"
        assert row.mp == pytest.approx(12000.0)
        assert row.diff_pts == pytest.approx(10.5)
        assert row.diff_fg_pct == pytest.approx(0.025)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamLineupsRow.model_validate({"lineup": "A. Davis - L. James - M. Monk - C. Anthony - D. Russell"})
        assert row.mp is None
        assert row.diff_pts is None

    def test_empty_model_is_valid(self):
        """All fields are optional; an empty dict produces a valid model."""
        row = TeamLineupsRow.model_validate({})
        assert row.lineup is None
        assert row.mp is None
        assert row.diff_pts is None


class TestTeamStartingLineupsRow:
    def test_happy_path(self):
        row = TeamStartingLineupsRow.model_validate(
            {
                "g": "1",
                "date_game": "Tue, Oct 30, 2018",
                "game_start_time": "7:30p",
                "network": "TNT",
                "box_score_text": "Box Score",
                "game_location": "@",
                "opp_name": "Los Angeles Lakers",
                "game_result": "W",
                "overtimes": "",
                "pts": "112",
                "opp_pts": "108",
                "wins": "1",
                "losses": "0",
                "game_starters": "L. James - A. Davis - ...",
            }
        )
        assert row.g == 1
        assert row.date_game == "Tue, Oct 30, 2018"
        assert row.opp_name == "Los Angeles Lakers"
        assert row.pts == 112
        assert row.opp_pts == 108
        assert row.wins == 1
        assert row.losses == 0
        assert row.game_starters == "L. James - A. Davis - ..."

    def test_optional_cells_parse_to_none(self):
        row = TeamStartingLineupsRow.model_validate({})
        assert row.g is None
        assert row.pts is None
        assert row.game_starters is None

    def test_empty_model_is_valid(self):
        """All fields are optional."""
        row = TeamStartingLineupsRow.model_validate({})
        assert row.wins is None
        assert row.losses is None


class TestTeamOnOffRow:
    def test_happy_path(self):
        row = TeamOnOffRow.model_validate(
            {
                "player": "L. James",
                "split_id": "On",
                "mp": "2000",
                "efg_pct": "0.544",
                "orb_pct": "0.250",
                "drb_pct": "0.750",
                "trb_pct": "0.125",
                "ast_pct": "0.220",
                "stl_pct": "0.015",
                "blk_pct": "0.030",
                "tov_pct": "0.120",
                "pace": "100.5",
                "off_rtg": "115.0",
            }
        )
        assert row.player == "L. James"
        assert row.split_id == "On"
        assert row.mp == 2000
        assert row.efg_pct == pytest.approx(0.544)
        assert row.off_rtg == pytest.approx(115.0)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = TeamOnOffRow.model_validate({})
        assert row.player is None
        assert row.split_id is None
        assert row.mp is None

    def test_empty_model_is_valid(self):
        """All fields are optional."""
        row = TeamOnOffRow.model_validate({})
        assert row.efg_pct is None
        assert row.off_rtg is None


class TestFranchiseHistoryRow:
    def test_happy_path(self):
        row = FranchiseHistoryRow.model_validate(
            {
                "season": "2020-21",
                "lg_id": "NBA",
                "team_name": "LAL",
                "wins": "42",
                "losses": "30",
                "win_loss_pct": "0.583",
                "rank_team": "3",
                "srs": "4.21",
                "pace": "99.6",
                "pace_rel": "0.3",
                "off_rtg": "113.7",
                "off_rtg_rel": "2.8",
                "def_rtg": "108.5",
                "def_rtg_rel": "-2.4",
                "rank_team_playoffs": "1",
                "coaches": "Frank Vogel",
                "top_ws": "LeBron James (9.4)",
            }
        )
        assert row.season == "2020-21"
        assert row.lg_id == "NBA"
        assert row.team_name == "LAL"
        assert row.wins == 42
        assert row.losses == 30
        assert row.win_loss_pct == pytest.approx(0.583)
        assert row.rank_team_playoffs == 1
        assert row.coaches == "Frank Vogel"
        assert row.top_ws == "LeBron James (9.4)"

    def test_optional_cells_parse_to_none(self):
        row = FranchiseHistoryRow.model_validate(
            {
                "season": "2018-19",
                "team_name": "LAL",
                "wins": "37",
                "losses": "45",
            }
        )
        assert row.season == "2018-19"
        assert row.wins == 37
        assert row.losses == 45
        assert row.rank_team_playoffs is None
        assert row.coaches is None

    def test_team_name_abbr_alias_fallback(self):
        # AliasChoices allows ``team_name_abbr`` as an alias for ``team_name``.
        row = FranchiseHistoryRow.model_validate(
            {
                "season": "2017-18",
                "team_name_abbr": "BOS",
                "wins": "55",
                "losses": "27",
            }
        )
        assert row.team_name == "BOS"

    def test_team_abbreviation_alias_fallback(self):
        # AliasChoices also allows ``team_abbreviation`` for ``team_name``.
        row = FranchiseHistoryRow.model_validate(
            {
                "season": "2019-20",
                "team_abbreviation": "MIA",
                "wins": "44",
                "losses": "29",
            }
        )
        assert row.team_name == "MIA"

    def test_missing_required_wins_raises(self):
        with pytest.raises(ValidationError):
            FranchiseHistoryRow.model_validate(
                {
                    "season": "2020-21",
                    "team_name": "LAL",
                    "losses": "30",
                }
            )
