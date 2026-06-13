"""Unit tests for the league-wide row schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import Position, Team
from courtside_data.schemas.league import (
    AttendanceRow,
    CareerLeadersRow,
    LeaguePer36MinutesRow,
    LeaguePer100PossessionsRow,
    LeaguePerGameStatsRow,
    LeagueShootingRow,
    LeagueTotalsRow,
    LeagueTransactionRow,
    RookieStatsRow,
    SeasonAwardsRow,
    SeasonLeadersRow,
)

# ---------------------------------------------------------------------------
# Per-game stats / Totals / Rookie stats — use the shared mixin
# ---------------------------------------------------------------------------


def _full_per_game_row() -> dict[str, str]:
    return {
        "name_display": "Jayson Tatum",
        "pos": "SF",
        "age": "25",
        "team_name_abbr": "BOS",
        "games": "74",
        "games_started": "74",
        "mp_per_g": "36.9",
        "fg_per_g": "9.8",
        "fga_per_g": "20.6",
        "fg_pct": ".476",
        "fg3_per_g": "3.2",
        "fg3a_per_g": "7.6",
        "fg3_pct": ".421",
        "fg2_per_g": "6.6",
        "fg2a_per_g": "13.0",
        "fg2_pct": ".508",
        "efg_pct": ".554",
        "ft_per_g": "5.6",
        "fta_per_g": "6.7",
        "ft_pct": ".836",
        "orb_per_g": "1.1",
        "drb_per_g": "7.5",
        "trb_per_g": "8.6",
        "ast_per_g": "4.5",
        "stl_per_g": "1.1",
        "blk_per_g": "0.5",
        "tov_per_g": "2.7",
        "pf_per_g": "2.1",
        "pts_per_g": "28.4",
    }


class TestLeaguePerGameStatsRow:
    def test_happy_path(self):
        row = LeaguePerGameStatsRow.model_validate(_full_per_game_row())
        assert row.name_display == "Jayson Tatum"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.age == 25
        assert row.team == Team.BOSTON_CELTICS
        assert row.games_played == 74
        assert row.points_per_game == pytest.approx(28.4)
        assert row.three_point_field_goal_percentage == pytest.approx(0.421)

    def test_empty_optional_cells_become_none(self):
        raw = _full_per_game_row()
        raw["team_name_abbr"] = ""
        raw["games_started"] = ""
        raw["ft_pct"] = ""
        row = LeaguePerGameStatsRow.model_validate(raw)
        assert row.team is None
        assert row.games_started is None
        assert row.free_throw_percentage is None

    @pytest.mark.parametrize("team_name_abbr", ["TOT", "2TM", "3TM"])
    def test_aggregate_team_rows_are_supported(self, team_name_abbr):
        raw = _full_per_game_row()
        raw["team_name_abbr"] = team_name_abbr
        row = LeaguePerGameStatsRow.model_validate(raw)
        assert row.team == team_name_abbr

    def test_unknown_team_abbreviation_raises(self):
        raw = _full_per_game_row()
        raw["team_name_abbr"] = "XXX"
        with pytest.raises(ValidationError):
            LeaguePerGameStatsRow.model_validate(raw)

    def test_missing_required_data_stat_raises(self):
        raw = _full_per_game_row()
        del raw["name_display"]
        with pytest.raises(ValidationError):
            LeaguePerGameStatsRow.model_validate(raw)

    def test_aliases_remain_data_stat_keys(self):
        assert LeaguePerGameStatsRow.model_fields["name_display"].validation_alias == "name_display"
        assert LeaguePerGameStatsRow.model_fields["team"].validation_alias == "team_name_abbr"


class TestLeagueTotalsRow:
    def test_happy_path(self):
        raw = {
            "name_display": "Joel Embiid",
            "pos": "C",
            "age": "29",
            "team_name_abbr": "PHI",
            "games": "66",
            "games_started": "66",
            "mp": "2304",
            "fg": "558",
            "fga": "1082",
            "fg_pct": ".516",
            "fg3": "69",
            "fg3a": "202",
            "fg3_pct": ".342",
            "fg2": "489",
            "fg2a": "880",
            "fg2_pct": ".556",
            "efg_pct": ".548",
            "ft": "522",
            "fta": "628",
            "ft_pct": ".831",
            "orb": "116",
            "drb": "494",
            "trb": "610",
            "ast": "274",
            "stl": "68",
            "blk": "98",
            "tov": "198",
            "pf": "189",
            "pts": "1707",
        }
        row = LeagueTotalsRow.model_validate(raw)
        assert row.name_display == "Joel Embiid"
        assert row.made_field_goals == 558
        assert row.points == 1707
        assert row.field_goal_percentage == pytest.approx(0.516)

    def test_empty_optional_cells_become_none(self):
        raw = {
            "name_display": "Joel Embiid",
            "pos": "C",
            "age": "29",
            "team_name_abbr": "PHI",
        }
        row = LeagueTotalsRow.model_validate(raw)
        assert row.games_played is None
        assert row.points is None

    @pytest.mark.parametrize("team_name_abbr", ["TOT", "2TM", "3TM"])
    def test_aggregate_team_rows_are_supported(self, team_name_abbr):
        raw = {
            "name_display": "Joel Embiid",
            "pos": "C",
            "age": "29",
            "team_name_abbr": team_name_abbr,
            "pts": "1707",
        }
        row = LeagueTotalsRow.model_validate(raw)
        assert row.team == team_name_abbr

    def test_missing_required_data_stat_raises(self):
        raw = {
            "name_display": "Joel Embiid",
            "pos": "C",
            "age": "29",
            "team_name_abbr": "PHI",
            "pts": "1707",
        }
        del raw["name_display"]
        with pytest.raises(ValidationError):
            LeagueTotalsRow.model_validate(raw)


class TestRookieStatsRow:
    def test_happy_path(self):
        row = RookieStatsRow.model_validate(_full_per_game_row())
        assert row.name_display == "Jayson Tatum"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.team == Team.BOSTON_CELTICS

    def test_empty_optional_cells_become_none(self):
        raw = _full_per_game_row()
        raw["pos"] = ""
        raw["team_name_abbr"] = ""
        row = RookieStatsRow.model_validate(raw)
        assert row.positions == []
        assert row.team is None

    def test_aggregate_team_row_is_supported(self):
        raw = _full_per_game_row()
        raw["team_name_abbr"] = "2TM"
        row = RookieStatsRow.model_validate(raw)
        assert row.team == "2TM"

    def test_missing_required_data_stat_raises(self):
        raw = _full_per_game_row()
        del raw["name_display"]
        with pytest.raises(ValidationError):
            RookieStatsRow.model_validate(raw)


# ---------------------------------------------------------------------------
# Per-36 minutes / Per-100 possessions
# ---------------------------------------------------------------------------


def _full_per_36_row() -> dict[str, str]:
    return {
        "name_display": "Jayson Tatum",
        "pos": "SF",
        "age": "25",
        "team_name_abbr": "BOS",
        "games": "74",
        "games_started": "74",
        "mp": "2728",
        "fg_per_36_min": "9.6",
        "fga_per_36_min": "20.1",
        "fg_pct": ".477",
        "fg3_per_36_min": "3.1",
        "fg3a_per_36_min": "7.4",
        "fg3_pct": ".421",
        "fg2_per_36_min": "6.4",
        "fg2a_per_36_min": "12.7",
        "fg2_pct": ".508",
        "ft_per_36_min": "5.5",
        "fta_per_36_min": "6.5",
        "ft_pct": ".836",
        "orb_per_36_min": "1.1",
        "drb_per_36_min": "7.3",
        "trb_per_36_min": "8.4",
        "ast_per_36_min": "4.4",
        "stl_per_36_min": "1.1",
        "blk_per_36_min": "0.5",
        "tov_per_36_min": "2.6",
        "pf_per_36_min": "2.1",
        "pts_per_36_min": "27.7",
    }


class TestLeaguePer36MinutesRow:
    def test_happy_path(self):
        row = LeaguePer36MinutesRow.model_validate(_full_per_36_row())
        assert row.name_display == "Jayson Tatum"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.minutes_played == 2728
        assert row.made_field_goals_per_36_min == pytest.approx(9.6)
        assert row.points_per_36_min == pytest.approx(27.7)

    def test_empty_optional_cells_become_none(self):
        raw = _full_per_36_row()
        raw["games_started"] = ""
        raw["fg_pct"] = ""
        row = LeaguePer36MinutesRow.model_validate(raw)
        assert row.games_started is None
        assert row.field_goal_percentage is None

    def test_aggregate_team_row_is_supported(self):
        raw = _full_per_36_row()
        raw["team_name_abbr"] = "3TM"
        row = LeaguePer36MinutesRow.model_validate(raw)
        assert row.team == "3TM"

    def test_missing_required_data_stat_raises(self):
        raw = _full_per_36_row()
        del raw["name_display"]
        with pytest.raises(ValidationError):
            LeaguePer36MinutesRow.model_validate(raw)


def _full_per_100_row() -> dict[str, str]:
    return {
        "name_display": "Joel Embiid",
        "pos": "C",
        "age": "29",
        "team_name_abbr": "PHI",
        "games": "66",
        "games_started": "66",
        "mp": "2304",
        "fg_per_100_poss": "13.1",
        "fga_per_100_poss": "25.4",
        "fg_pct": ".516",
        "fg3_per_100_poss": "1.6",
        "fg3a_per_100_poss": "4.7",
        "fg3_pct": ".342",
        "fg2_per_100_poss": "11.5",
        "fg2a_per_100_poss": "20.6",
        "fg2_pct": ".556",
        "ft_per_100_poss": "12.2",
        "fta_per_100_poss": "14.7",
        "ft_pct": ".831",
        "orb_per_100_poss": "2.7",
        "drb_per_100_poss": "11.6",
        "trb_per_100_poss": "14.3",
        "ast_per_100_poss": "6.4",
        "stl_per_100_poss": "1.6",
        "blk_per_100_poss": "2.3",
        "tov_per_100_poss": "4.6",
        "pf_per_100_poss": "4.4",
        "pts_per_100_poss": "40.0",
    }


class TestLeaguePer100PossessionsRow:
    def test_happy_path(self):
        row = LeaguePer100PossessionsRow.model_validate(_full_per_100_row())
        assert row.team == Team.PHILADELPHIA_76ERS
        assert row.made_field_goals_per_100_possessions == pytest.approx(13.1)
        assert row.points_per_100_possessions == pytest.approx(40.0)

    def test_empty_optional_cells_become_none(self):
        raw = _full_per_100_row()
        raw["team_name_abbr"] = ""
        raw["ft_pct"] = ""
        row = LeaguePer100PossessionsRow.model_validate(raw)
        assert row.team is None
        assert row.free_throw_percentage is None

    def test_aggregate_team_row_is_supported(self):
        raw = _full_per_100_row()
        raw["team_name_abbr"] = "TOT"
        row = LeaguePer100PossessionsRow.model_validate(raw)
        assert row.team == "TOT"

    def test_missing_required_data_stat_raises(self):
        raw = _full_per_100_row()
        del raw["name_display"]
        with pytest.raises(ValidationError):
            LeaguePer100PossessionsRow.model_validate(raw)


# ---------------------------------------------------------------------------
# Shooting
# ---------------------------------------------------------------------------


def _full_shooting_row() -> dict[str, str]:
    return {
        "name_display": "Stephen Curry",
        "pos": "PG",
        "age": "35",
        "team_name_abbr": "GSW",
        "games": "56",
        "mp": "1941",
        "fg_pct_from_0_3_ft": ".700",
        "fg_pct_from_3_10_ft": ".476",
        "fg_pct_from_10_16_ft": ".510",
        "fg_pct_from_16_3p": ".420",
        "fg_pct_from_3p": ".427",
        "pct_fga_from_0_3_ft": ".121",
        "pct_fga_from_3_10_ft": ".094",
        "pct_fga_from_10_16_ft": ".083",
        "pct_fga_from_16_3p": ".281",
        "pct_fga_from_3p": ".421",
        "fg_pct_from_2p": ".560",
        "fg_pct_from_0_3_ft_2": ".725",
        "fg_pct_from_corner_3": ".486",
        "pct_fga_from_corner_3": ".119",
        "num_shots_heaved": "1",
        "pct_shots_heaved": ".002",
    }


class TestLeagueShootingRow:
    def test_happy_path(self):
        row = LeagueShootingRow.model_validate(_full_shooting_row())
        assert row.team == Team.GOLDEN_STATE_WARRIORS
        assert row.positions == [Position.POINT_GUARD]
        assert row.number_of_shots_heaved == 1
        assert row.field_goal_percentage_from_corner_three == pytest.approx(0.486)
        assert row.percentage_of_shots_heaved == pytest.approx(0.002)

    def test_empty_optional_cells_become_none(self):
        raw = _full_shooting_row()
        raw["games"] = ""
        raw["fg_pct_from_0_3_ft"] = ""
        row = LeagueShootingRow.model_validate(raw)
        assert row.games_played is None
        assert row.field_goal_percentage_from_zero_to_three_feet is None

    def test_aggregate_team_row_is_supported(self):
        raw = _full_shooting_row()
        raw["team_name_abbr"] = "2TM"
        row = LeagueShootingRow.model_validate(raw)
        assert row.team == "2TM"

    def test_missing_required_data_stat_raises(self):
        raw = _full_shooting_row()
        del raw["name_display"]
        with pytest.raises(ValidationError):
            LeagueShootingRow.model_validate(raw)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------


class TestLeagueTransactionRow:
    def test_happy_path(self):
        row = LeagueTransactionRow.model_validate(
            {
                "date": "October 16, 2018",
                "transaction": "Signed D. Jones to a 1-year contract.",
                "from_team_abbreviations": ["GSW"],
                "to_team_abbreviations": ["GSW"],
                "linked_resources": [
                    {
                        "text": "D. Jones",
                        "href": "/players/j/jonesda01.html",
                        "from_team_abbreviation": "",
                        "to_team_abbreviation": "",
                    },
                ],
            }
        )
        assert row.date == "October 16, 2018"
        assert row.transaction.startswith("Signed")
        assert row.from_team_abbreviations == ["GSW"]
        assert row.to_team_abbreviations == ["GSW"]
        assert row.linked_resources[0]["href"] == "/players/j/jonesda01.html"

    def test_optional_team_fields_default_to_empty_lists(self):
        row = LeagueTransactionRow.model_validate({"date": "July 1, 2020", "transaction": "Waived X. Doe."})
        assert row.date == "July 1, 2020"
        assert row.from_team_abbreviations == []
        assert row.to_team_abbreviations == []
        assert row.linked_resources == []

    def test_missing_required_data_stat_raises(self):
        with pytest.raises(ValidationError):
            LeagueTransactionRow.model_validate({"transaction": "Waived X. Doe."})


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------


class TestAttendanceRow:
    def test_happy_path(self):
        row = AttendanceRow.model_validate(
            {
                "team": "BOS",
                "arena_name": "TD Garden",
                "attendance": "610329",
                "attendance_per_g": "19198",
            }
        )
        assert row.team == Team.BOSTON_CELTICS
        assert row.arena_name == "TD Garden"
        assert row.attendance == 610329
        assert row.attendance_per_game == 19198

    def test_empty_optional_cells_become_none(self):
        row = AttendanceRow.model_validate(
            {"team": "BOS", "arena_name": "TD Garden", "attendance": "", "attendance_per_g": ""}
        )
        assert row.attendance is None
        assert row.attendance_per_game is None

    def test_missing_required_data_stat_raises(self):
        with pytest.raises(ValidationError):
            AttendanceRow.model_validate(
                {"arena_name": "TD Garden", "attendance": "610329", "attendance_per_g": "19198"}
            )


# ---------------------------------------------------------------------------
# Awards + leaders
# ---------------------------------------------------------------------------


class TestSeasonAwardsRow:
    def test_happy_path(self):
        row = SeasonAwardsRow.model_validate({"award": "MVP", "player": "Nikola Jokic"})
        assert row.award == "MVP"
        assert row.player == "Nikola Jokic"

    def test_alias_keys_match_validation_alias(self):
        # The fetcher emits raw dicts keyed by the data-stat names.
        row = SeasonAwardsRow.model_validate({"award": "Defensive Player of the Year", "player": "Jaren Jackson Jr."})
        assert row.award == "Defensive Player of the Year"
        assert row.player == "Jaren Jackson Jr."

    def test_missing_required_award_raises(self):
        with pytest.raises(ValidationError):
            SeasonAwardsRow.model_validate({"player": "Nikola Jokic"})

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            SeasonAwardsRow.model_validate({"award": "MVP"})


class TestSeasonLeadersRow:
    def test_happy_path(self):
        row = SeasonLeadersRow.model_validate(
            {
                "rank": "1",
                "player": "LeBron James",
                "value": "40474",
                "season": "2023-24",
                "team_id": "LAL",
            }
        )
        assert row.rank == 1
        assert row.player == "LeBron James"
        assert row.value == "40474"
        assert row.season == "2023-24"
        assert row.team == "LAL"

    def test_optional_team_id_becomes_none(self):
        row = SeasonLeadersRow.model_validate(
            {
                "rank": "1",
                "player": "Wilt Chamberlain",
                "value": "4029",
                "season": "1961-62",
            }
        )
        assert row.team is None

    def test_missing_required_rank_raises(self):
        with pytest.raises(ValidationError):
            SeasonLeadersRow.model_validate({"player": "LeBron James", "value": "40474", "season": "2023-24"})

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            SeasonLeadersRow.model_validate({"rank": "1", "value": "40474", "season": "2023-24"})

    def test_strict_rank_rejects_garbage(self):
        with pytest.raises(ValidationError):
            SeasonLeadersRow.model_validate(
                {
                    "rank": "abc",
                    "player": "LeBron James",
                    "value": "40474",
                    "season": "2023-24",
                }
            )


class TestCareerLeadersRow:
    def test_happy_path(self):
        row = CareerLeadersRow.model_validate({"rank": "1", "player": "LeBron James", "value": "40474"})
        assert row.rank == 1
        assert row.player == "LeBron James"
        assert row.value == "40474"

    def test_alias_keys_match_validation_alias(self):
        row = CareerLeadersRow.model_validate({"rank": "2", "player": "Kareem Abdul-Jabbar", "value": "38387"})
        assert row.rank == 2
        assert row.player == "Kareem Abdul-Jabbar"
        assert row.value == "38387"

    def test_missing_required_value_raises(self):
        with pytest.raises(ValidationError):
            CareerLeadersRow.model_validate({"rank": "1", "player": "LeBron James"})

    def test_strict_rank_rejects_garbage(self):
        with pytest.raises(ValidationError):
            CareerLeadersRow.model_validate({"rank": "abc", "player": "LeBron James", "value": "40474"})
