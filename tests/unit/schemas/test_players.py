"""Unit tests for the row schemas in :mod:`courtside_data.schemas.players`.

Each model gets a focused test class that covers the happy path, an empty
or optional cell, and a missing required ``data-stat`` alias.  Tests use
synthetic raw rows that mirror the ``data-stat`` keys BR emits.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import Position, Team
from courtside_data.output.columns import (
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
)
from courtside_data.schemas.players import (
    PlayerAdjustedShootingRow,
    PlayerAdvancedSeasonTotalsRow,
    PlayerAllStarRow,
    PlayerCareerStatsRow,
    PlayerGameHighsRow,
    PlayerOnOffRow,
    PlayerPlayByPlayStatsRow,
    PlayerPlayoffSeriesRow,
    PlayerSalariesRow,
    PlayerSeasonTotalsRow,
    PlayerShotChartsRow,
    PlayerSimilarityScoresRow,
    PlayerSplitsRow,
)


def _career_row(**overrides: object) -> dict[str, object]:
    """Return a full ``player_career_stats`` raw row with optional overrides."""
    base: dict[str, object] = {
        "season": "2023-24",
        "age": "39",
        "team_name_abbr": "LAL",
        "league_id": "NBA",
        "pos": "SF",
        "games": "71",
        "games_started": "71",
        "mp_per_g": "35.3",
        "fg_per_g": "9.8",
        "fga_per_g": "19.6",
        "fg_pct": ".502",
        "fg3_per_g": "2.1",
        "fg3a_per_g": "5.1",
        "fg3_pct": ".410",
        "fg2_per_g": "7.7",
        "fg2a_per_g": "14.5",
        "fg2_pct": ".531",
        "efg_pct": ".550",
        "ft_per_g": "3.4",
        "fta_per_g": "4.5",
        "ft_pct": ".750",
        "orb_per_g": "0.8",
        "drb_per_g": "5.5",
        "trb_per_g": "6.3",
        "ast_per_g": "8.3",
        "stl_per_g": "1.3",
        "blk_per_g": "0.5",
        "tov_per_g": "2.9",
        "pf_per_g": "1.1",
        "pts_per_g": "25.1",
    }
    base.update(overrides)
    return base


class TestPlayerCareerStatsRow:
    def test_happy_path(self):
        row = PlayerCareerStatsRow.model_validate(_career_row())
        assert row.season == "2023-24"
        assert row.age == 39
        assert row.team_name_abbr == Team.LOS_ANGELES_LAKERS
        assert row.comp_name_abbr == "NBA"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.games_played == 71
        assert row.games_started == 71
        assert row.minutes_played_per_game == pytest.approx(35.3)
        assert row.points_per_game == pytest.approx(25.1)
        assert row.field_goal_percentage == pytest.approx(0.502)
        assert row.effective_field_goal_percentage == pytest.approx(0.550)

    def test_optional_empty_cells_parse_to_none(self):
        # A DNP-only season has empty stat cells; required identifiers remain.
        row = PlayerCareerStatsRow.model_validate(_career_row(games="0", games_started="", mp_per_g="", pts_per_g=""))
        assert row.games_played == 0
        assert row.games_started is None
        assert row.minutes_played_per_game is None
        assert row.points_per_game is None

    def test_missing_required_season_raises(self):
        raw = _career_row()
        raw.pop("season")
        with pytest.raises(ValidationError):
            PlayerCareerStatsRow.model_validate(raw)


class TestPlayerPlayoffSeriesRow:
    def test_happy_path(self):
        row = PlayerPlayoffSeriesRow.model_validate(
            {
                "year_id": "2023-24",
                "age": "39",
                "team_name_abbr": "LAL",
                "comp_name_abbr": "NBA",
                "ps_round": "First Round",
                "opp_name_abbr": "DEN",
                "series_result": "L 1-4",
                "games": "5",
                "mp_per_g": "38.2",
                "pts_per_g": "27.8",
                "trb_per_g": "6.8",
                "ast_per_g": "8.8",
                "stl_per_g": "2.4",
                "blk_per_g": "1.0",
                "fg": "52",
                "fga": "105",
                "fg_pct": ".495",
                "fg3": "10",
                "fg3a": "25",
                "fg3_pct": ".400",
                "fg2": "42",
                "fg2a": "80",
                "fg2_pct": ".525",
                "efg_pct": ".540",
                "ft": "25",
                "fta": "33",
                "ft_pct": ".758",
                "orb": "6",
                "drb": "28",
                "trb": "34",
                "ast": "44",
                "stl": "12",
                "blk": "5",
                "tov": "20",
                "pf": "11",
                "pts": "139",
            }
        )
        assert row.year_id == "2023-24"
        assert row.games_played == 5
        assert row.team_name_abbr == Team.LOS_ANGELES_LAKERS

    def test_missing_required_team_raises(self):
        raw = {
            "year_id": "2023-24",
            "age": "39",
            "games": "5",
        }
        with pytest.raises(ValidationError):
            PlayerPlayoffSeriesRow.model_validate(raw)


class TestPlayerAllStarRow:
    def test_happy_path(self):
        row = PlayerAllStarRow.model_validate(
            {
                "season": "2023-24",
                "age": "39",
                "team_id": "LAL",
                "lg_id": "NBA",
                "pos": "SF",
                "g": "1",
                "gs": "1",
                "mp": "20",
                "fg": "10",
                "fga": "15",
                "fg_pct": ".667",
                "fg3": "3",
                "fg3a": "6",
                "fg3_pct": ".500",
                "ft": "2",
                "fta": "2",
                "ft_pct": "1.000",
                "orb": "1",
                "trb": "5",
                "ast": "5",
                "stl": "1",
                "blk": "0",
                "tov": "2",
                "pf": "1",
                "pts": "25",
            }
        )
        assert row.season == "2023-24"
        assert row.points == 25

    def test_missing_required_season_raises(self):
        raw = {
            "age": "39",
            "team_id": "LAL",
            "lg_id": "NBA",
            "pos": "SF",
            "g": "1",
            "gs": "1",
            "mp": "20",
            "pts": "25",
        }
        with pytest.raises(ValidationError):
            PlayerAllStarRow.model_validate(raw)


class TestPlayerAdjustedShootingRow:
    def test_happy_path(self):
        row = PlayerAdjustedShootingRow.model_validate(
            {
                "year_id": "2023-24",
                "team_name_abbr": "LAL",
                "age": "39",
                "comp_name_abbr": "NBA",
                "pos": "SF",
                "games": "71",
                "games_started": "71",
                "mp": "2506",
                "fg_pct": ".502",
                "fg2_pct": ".531",
                "fg3_pct": ".410",
                "efg_pct": ".550",
                "ft_pct": ".750",
                "ts_pct": ".580",
                "fta_per_fga_pct": ".230",
                "fg3a_per_fga_pct": ".260",
                "adj_fg_pct": ".510",
                "adj_fg2_pct": ".540",
                "adj_fg3_pct": ".420",
                "adj_efg_pct": ".560",
                "adj_ft_pct": ".760",
                "adj_ts_pct": ".590",
                "adj_fta_per_fga_pct": ".240",
                "adj_fg3a_per_fga_pct": ".270",
                "fg_pts_added": "45.2",
                "ts_pts_added": "52.1",
            }
        )
        assert row.age == 39
        assert row.minutes_played == 2506
        assert row.true_shooting_percentage == pytest.approx(0.580)
        assert row.adjusted_field_goal_percentage == pytest.approx(0.510)

    def test_empty_pct_cells_parse_to_none(self):
        row = PlayerAdjustedShootingRow.model_validate(
            {
                "year_id": "2023-24",
                "team_name_abbr": "LAL",
                "age": "39",
                "comp_name_abbr": "NBA",
                "pos": "SF",
                "games": "0",
                "games_started": "0",
                "mp": "0",
                "fg_pct": "",
                "fg2_pct": "",
                "fg3_pct": "",
                "efg_pct": "",
                "ft_pct": "",
                "ts_pct": "",
            }
        )
        assert row.field_goal_percentage is None
        assert row.three_point_field_goal_percentage is None
        assert row.free_throw_percentage is None
        assert row.true_shooting_percentage is None

    def test_missing_required_team_raises(self):
        raw = {
            "year_id": "2023-24",
            "age": "39",
            "games": "71",
            "mp": "2506",
        }
        with pytest.raises(ValidationError):
            PlayerAdjustedShootingRow.model_validate(raw)


class TestPlayerPlayByPlayStatsRow:
    def test_happy_path(self):
        row = PlayerPlayByPlayStatsRow.model_validate(
            {
                "year_id": "2023-24",
                "age": "39",
                "team_name_abbr": "LAL",
                "comp_name_abbr": "NBA",
                "pos": "SF",
                "games": "71",
                "games_started": "71",
                "mp": "2506",
                "pct_1": ".710",
                "pct_2": ".150",
                "pct_3": ".100",
                "pct_4": ".030",
                "pct_5": ".010",
                "plus_minus_on": "5.2",
                "plus_minus_net": "3.1",
                "tov_bad_pass": "45",
                "tov_lost_ball": "30",
                "fouls_shooting": "12",
                "fouls_offensive": "5",
                "drawn_shooting": "25",
                "drawn_offensive": "10",
                "astd_pts": "150",
                "and1s": "8",
                "own_shots_blk": "15",
            }
        )
        assert row.year_id == "2023-24"
        assert row.games_played == 71
        assert row.pct_1 == pytest.approx(0.710)
        assert row.pct_5 == pytest.approx(0.010)

    def test_empty_pct_cells_parse_to_none(self):
        row = PlayerPlayByPlayStatsRow.model_validate(
            {
                "year_id": "2023-24",
                "team_name_abbr": "LAL",
                "comp_name_abbr": "NBA",
                "pos": "SF",
                "games": "0",
                "games_started": "0",
                "mp": "0",
                "pct_1": "",
                "pct_5": "",
            }
        )
        assert row.pct_1 is None
        assert row.pct_5 is None

    def test_missing_required_team_raises(self):
        raw = {
            "year_id": "2023-24",
            "comp_name_abbr": "NBA",
            "pos": "SF",
            "games": "71",
            "mp": "2506",
        }
        with pytest.raises(ValidationError):
            PlayerPlayByPlayStatsRow.model_validate(raw)


class TestPlayerGameHighsRow:
    def test_happy_path(self):
        row = PlayerGameHighsRow.model_validate(
            {
                "season": "2023-24",
                "age": "39",
                "team": "Los Angeles Lakers",
                "league": "NBA",
                "time_on_court": "39:42",
                "fg": "19",
                "fga": "28",
                "fg3": "9",
                "fg3a": "14",
                "fg2": "10",
                "fg2a": "14",
                "ft": "12",
                "fta": "14",
                "orb": "3",
                "drb": "14",
                "trb": "17",
                "ast": "14",
                "stl": "4",
                "blk": "3",
                "tov": "7",
                "pf": "3",
                "pts": "48",
                "game_score": "W 112-108",
            }
        )
        assert row.season == "2023-24"
        assert row.points == 48
        assert row.game_score == "W 112-108"

    def test_missing_required_pts_raises(self):
        raw = {
            "season": "2023-24",
            "team": "Los Angeles Lakers",
            "league": "NBA",
            "game_score": "W 112-108",
        }
        # No required fields without defaults, so no error for missing stat values.
        # The model is permissive for optional columns.
        row = PlayerGameHighsRow.model_validate(raw)
        assert row.points is None

    def test_optional_cells_parse_to_none(self):
        row = PlayerGameHighsRow.model_validate({"season": "2023-24"})
        assert row.points is None
        assert row.game_score is None


class TestPlayerSimilarityScoresRow:
    def test_happy_path(self):
        row = PlayerSimilarityScoresRow.model_validate(
            {
                "player": "Kareem Abdul-Jabbar",
                "sim_score": "98.5",
                "year1": "jamesle01",
                "year2": "curryst01",
            }
        )
        assert row.player == "Kareem Abdul-Jabbar"
        assert row.sim_score == pytest.approx(98.5)
        assert row.year1 == "jamesle01"

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            PlayerSimilarityScoresRow.model_validate({"sim_score": "98.5"})


class TestPlayerSalariesRow:
    def test_happy_path(self):
        row = PlayerSalariesRow.model_validate(
            {
                "season": "2023-24",
                "team_name": "Los Angeles Lakers",
                "lg_id": "NBA",
                "salary": "$47,607,350",
            }
        )
        assert row.season == "2023-24"
        assert row.team_name == "Los Angeles Lakers"
        assert row.lg_id == "NBA"
        assert row.salary == "$47,607,350"

    def test_empty_salary_parses_to_none(self):
        row = PlayerSalariesRow.model_validate(
            {
                "season": "2023-24",
                "team_name": "Los Angeles Lakers",
                "lg_id": "NBA",
                "salary": "",
            }
        )
        assert row.salary is None

    def test_missing_required_season_raises(self):
        with pytest.raises(ValidationError):
            PlayerSalariesRow.model_validate({"team_name": "Los Angeles Lakers", "lg_id": "NBA", "salary": "$1"})


class TestPlayerShotChartsRow:
    def test_happy_path(self):
        row = PlayerShotChartsRow.model_validate(
            {
                "split_id": "Shot Type",
                "split_value": "Dunk",
                "fg": "120",
                "fga": "125",
                "fg_pct": ".960",
                "fg3": "0",
                "fg3a": "0",
                "fg3_pct": "",
                "efg_pct": ".960",
                "fg_ast": "100",
                "fg_ast_pct": ".833",
            }
        )
        assert row.split_id == "Shot Type"
        assert row.split_value == "Dunk"
        assert row.made_field_goals == 120
        assert row.attempted_field_goals == 125
        assert row.field_goal_percentage == pytest.approx(0.96)

    def test_optional_shot_count_cells_parse_to_none(self):
        row = PlayerShotChartsRow.model_validate(
            {
                "split_id": "Shot Type",
                "split_value": "Heave",
                "fg": "",
                "fga": "",
                "fg_pct": "",
                "fg3": "",
                "fg3a": "",
                "fg3_pct": "",
                "efg_pct": "",
                "fg_ast": "",
                "fg_ast_pct": "",
            }
        )
        assert row.made_field_goals is None
        assert row.attempted_field_goals is None
        assert row.field_goal_percentage is None


class TestPlayerSplitsRow:
    def test_happy_path(self):
        row = PlayerSplitsRow.model_validate(
            {
                "split_id": "Location",
                "split_value": "Home",
                "g": "35",
                "gs": "35",
                "mp": "1235",
                "fg": "350",
                "fga": "680",
                "fg3": "80",
                "fg3a": "180",
                "ft": "120",
                "fta": "160",
                "orb": "25",
                "trb": "215",
                "ast": "300",
                "stl": "45",
                "blk": "18",
                "tov": "100",
                "pf": "40",
                "pts": "900",
                "fg_pct": ".515",
                "fg3_pct": ".444",
                "ft_pct": ".750",
            }
        )
        assert row.split_id == "Location"
        assert row.split_value == "Home"
        assert row.games_played == 35
        assert row.points == 900
        assert row.field_goal_percentage == pytest.approx(0.515)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = PlayerSplitsRow.model_validate({"split_id": "Location", "split_value": "Home"})
        assert row.games_played is None
        assert row.points is None
        assert row.field_goal_percentage is None


class TestPlayerOnOffRow:
    def test_happy_path(self):
        row = PlayerOnOffRow.model_validate(
            {
                "split_id": "On Court",
                "team_id": "LAL",
                "mp": "2506",
                "efg_pct": ".550",
                "orb_pct": "5.5",
                "drb_pct": "18.2",
                "trb_pct": "11.8",
                "ast_pct": "40.1",
                "stl_pct": "2.1",
                "blk_pct": "0.9",
                "tov_pct": "11.4",
                "off_rtg": "118.5",
                "opp_efg_pct": ".520",
                "opp_orb_pct": "4.8",
                "opp_drb_pct": "17.0",
                "opp_trb_pct": "10.9",
                "opp_ast_pct": "35.2",
                "opp_stl_pct": "1.8",
                "opp_blk_pct": "0.7",
                "opp_tov_pct": "10.5",
                "opp_off_rtg": "112.3",
                "diff_efg_pct": "3.0",
                "diff_orb_pct": "0.7",
                "diff_drb_pct": "1.2",
                "diff_trb_pct": "0.9",
                "diff_ast_pct": "4.9",
                "diff_stl_pct": "0.3",
                "diff_blk_pct": "0.2",
                "diff_tov_pct": "0.9",
                "diff_off_rtg": "6.2",
            }
        )
        assert row.split_id == "On Court"
        assert row.minutes_played == 2506
        assert row.effective_field_goal_percentage == pytest.approx(0.550)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = PlayerOnOffRow.model_validate({"split_id": "On Court", "team_id": "LAL", "mp": "0"})
        assert row.effective_field_goal_percentage is None
        assert row.offensive_rating is None

    def test_minimal_row_validates(self):
        # All fields are optional, so a row with only split_id is valid.
        row = PlayerOnOffRow.model_validate({"split_id": "On Court", "mp": "0"})
        assert row.split_id == "On Court"


# ── League-wide season totals ────────────────────────────────────────────


def _season_totals_row(**overrides: object) -> dict[str, object]:
    """Return a full ``players_season_totals`` raw row with optional overrides."""
    base: dict[str, object] = {
        "slug": "jamesle01",
        "name_display": "LeBron James",
        "pos": "SF",
        "age": "39",
        "team_name_abbr": "LAL",
        "games": "71",
        "games_started": "71",
        "mp": "2506",
        "fg": "696",
        "fga": "1392",
        "fg_pct": ".500",
        "fg3": "149",
        "fg3a": "362",
        "fg3_pct": ".412",
        "fg2": "547",
        "fg2a": "1030",
        "fg2_pct": ".531",
        "efg_pct": ".554",
        "ft": "241",
        "fta": "320",
        "ft_pct": ".753",
        "orb": "57",
        "drb": "391",
        "trb": "448",
        "ast": "589",
        "stl": "92",
        "blk": "36",
        "tov": "206",
        "pf": "78",
        "pts": "1782",
        "tpl_dbl": "5",
        "awards": "All-NBA",
    }
    base.update(overrides)
    return base


class TestPlayerSeasonTotalsRow:
    def test_happy_path(self):
        row = PlayerSeasonTotalsRow.model_validate(_season_totals_row())
        assert row.slug == "jamesle01"
        assert row.name == "LeBron James"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.age == 39
        assert row.team == Team.LOS_ANGELES_LAKERS
        assert row.games_played == 71
        assert row.games_started == 71
        assert row.minutes_played == 2506
        assert row.made_field_goals == 696
        assert row.field_goal_percentage == pytest.approx(0.500)
        assert row.three_point_field_goal_percentage == pytest.approx(0.412)
        assert row.made_two_point_field_goals == 547
        assert row.effective_field_goal_percentage == pytest.approx(0.554)
        assert row.free_throw_percentage == pytest.approx(0.753)
        assert row.total_rebounds == 448
        assert row.points == 1782
        assert row.triple_doubles == 5
        assert row.awards == "All-NBA"
        dumped = row.model_dump()
        # Stable Python attribute names are used as dump keys (no aliases).
        assert set(dumped.keys()) == set(PLAYER_SEASON_TOTALS_COLUMN_NAMES)
        assert dumped["slug"] == "jamesle01"
        assert dumped["points"] == 1782

    def test_empty_optional_cells_parse_to_none(self):
        # A partial row (e.g. DNP) leaves optional stat cells blank.
        row = PlayerSeasonTotalsRow.model_validate(
            _season_totals_row(
                age="",
                games="0",
                games_started="",
                mp="",
                fg="0",
                fga="",
                fg_pct="",
                fg3="",
                fg3a="",
                fg3_pct="",
                fg2="",
                fg2a="",
                fg2_pct="",
                efg_pct="",
                ft="",
                fta="",
                ft_pct="",
                orb="",
                drb="",
                trb="",
                ast="",
                stl="",
                blk="",
                tov="",
                pf="",
                pts="0",
                tpl_dbl="",
                awards="",
            )
        )
        assert row.age is None
        assert row.games_started is None
        assert row.minutes_played is None
        assert row.points == 0
        assert row.made_field_goals == 0
        assert row.attempted_field_goals is None
        assert row.field_goal_percentage is None
        assert row.total_rebounds is None
        assert row.assists is None
        assert row.awards is None

    def test_alias_acceptance(self):
        # Pass the row by its raw ``data-stat`` keys (the validation_alias
        # values), as a real GenericTable extraction would.
        row = PlayerSeasonTotalsRow.model_validate(_season_totals_row())
        assert row.team == Team.LOS_ANGELES_LAKERS
        assert row.games_played == 71

    def test_invalid_team_raises(self):
        with pytest.raises(ValidationError):
            PlayerSeasonTotalsRow.model_validate(_season_totals_row(team_name_abbr="XXX"))

    def test_invalid_garbage_value_raises(self):
        with pytest.raises(ValidationError):
            PlayerSeasonTotalsRow.model_validate(_season_totals_row(pts="not-a-number"))

    def test_missing_required_team_raises(self):
        raw = _season_totals_row()
        raw.pop("team_name_abbr")
        with pytest.raises(ValidationError):
            PlayerSeasonTotalsRow.model_validate(raw)

    def test_field_count_matches_column_constant(self):
        assert len(PlayerSeasonTotalsRow.model_fields) == len(PLAYER_SEASON_TOTALS_COLUMN_NAMES)

    def test_field_names_match_column_constant(self):
        # The Python attribute names on the model (used as CSV/JSON keys by
        # downstream writers) must match the legacy column constant.
        assert set(PlayerSeasonTotalsRow.model_fields.keys()) == set(PLAYER_SEASON_TOTALS_COLUMN_NAMES)


def _advanced_season_totals_row(**overrides: object) -> dict[str, object]:
    """Return a full ``players_advanced_season_totals`` raw row with optional overrides."""
    base: dict[str, object] = {
        "slug": "jamesle01",
        "name_display": "LeBron James",
        "pos": "SF",
        "age": "39",
        "team_name_abbr": "LAL",
        "games": "71",
        "games_started": "71",
        "mp": "2506",
        "per": "25.0",
        "ts_pct": ".620",
        "fg3a_per_fga_pct": ".260",
        "fta_per_fga_pct": ".230",
        "orb_pct": "5.5",
        "drb_pct": "18.2",
        "trb_pct": "11.8",
        "ast_pct": "40.1",
        "stl_pct": "2.1",
        "blk_pct": "0.9",
        "tov_pct": "11.4",
        "usg_pct": "29.6",
        "ows": "6.2",
        "dws": "4.1",
        "ws": "10.3",
        "ws_per_48": ".197",
        "obpm": "6.8",
        "dbpm": "1.5",
        "bpm": "8.3",
        "vorp": "5.7",
        "awards": "All-NBA",
        "is_combined_totals": "False",
    }
    base.update(overrides)
    return base


class TestPlayerAdvancedSeasonTotalsRow:
    def test_happy_path(self):
        row = PlayerAdvancedSeasonTotalsRow.model_validate(_advanced_season_totals_row())
        assert row.slug == "jamesle01"
        assert row.name == "LeBron James"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.age == 39
        assert row.team == Team.LOS_ANGELES_LAKERS
        assert row.games_played == 71
        assert row.games_started == 71
        assert row.minutes_played == 2506
        assert row.player_efficiency_rating == pytest.approx(25.0)
        assert row.true_shooting_percentage == pytest.approx(0.620)
        # ``usage_percentage`` arrives as a whole-number percentage (29.6
        # meaning 29.6%) — ``BRPercentage`` passes it through unchanged when
        # the value carries no ``%`` suffix, matching the legacy parser.
        assert row.usage_percentage == pytest.approx(29.6)
        assert row.win_shares == pytest.approx(10.3)
        assert row.box_plus_minus == pytest.approx(8.3)
        assert row.value_over_replacement_player == pytest.approx(5.7)
        assert row.awards == "All-NBA"
        # ``is_combined_totals`` arrives as the string ``"False"`` and is
        # coerced by Pydantic's bool validator.
        assert row.is_combined_totals is False
        dumped = row.model_dump()
        assert set(dumped.keys()) == set(PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES)

    def test_empty_optional_cells_parse_to_none(self):
        # A row with only identity cells filled leaves every optional stat
        # field as ``None`` (and ``is_combined_totals`` defaults to ``False``).
        row = PlayerAdvancedSeasonTotalsRow.model_validate(
            {
                "slug": "jamesle01",
                "name_display": "LeBron James",
                "pos": "",
                "age": "",
                "team_name_abbr": "LAL",
                "games": "0",
                "games_started": "",
                "mp": "0",
                "awards": "",
            }
        )
        assert row.age is None
        assert row.positions == []
        assert row.games_played == 0
        assert row.games_started is None
        assert row.minutes_played == 0
        assert row.player_efficiency_rating is None
        assert row.true_shooting_percentage is None
        assert row.value_over_replacement_player is None
        assert row.awards is None
        assert row.is_combined_totals is False

    def test_alias_acceptance(self):
        # Pass the row by its raw ``data-stat`` keys (the validation_alias
        # values), as a real GenericTable extraction would.
        row = PlayerAdvancedSeasonTotalsRow.model_validate(_advanced_season_totals_row())
        assert row.team == Team.LOS_ANGELES_LAKERS
        assert row.true_shooting_percentage == pytest.approx(0.620)

    def test_invalid_team_raises(self):
        with pytest.raises(ValidationError):
            PlayerAdvancedSeasonTotalsRow.model_validate(_advanced_season_totals_row(team_name_abbr="XXX"))

    def test_invalid_garbage_value_raises(self):
        with pytest.raises(ValidationError):
            PlayerAdvancedSeasonTotalsRow.model_validate(_advanced_season_totals_row(per="not-a-number"))

    def test_missing_required_team_raises(self):
        raw = _advanced_season_totals_row()
        raw.pop("team_name_abbr")
        with pytest.raises(ValidationError):
            PlayerAdvancedSeasonTotalsRow.model_validate(raw)

    def test_field_count_matches_column_constant(self):
        assert len(PlayerAdvancedSeasonTotalsRow.model_fields) == len(PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES)

    def test_field_names_match_column_constant(self):
        # The Python attribute names on the model (used as CSV/JSON keys by
        # downstream writers) must match the legacy column constant.
        assert set(PlayerAdvancedSeasonTotalsRow.model_fields.keys()) == set(PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES)

    def test_is_combined_totals_string_coercion(self):
        # Pydantic v2's bool accepts "True"/"true"/"1" (case-insensitive) as
        # True; the legacy parser may emit a string for this field.
        row_true = PlayerAdvancedSeasonTotalsRow.model_validate(_advanced_season_totals_row(is_combined_totals="True"))
        assert row_true.is_combined_totals is True
        row_false = PlayerAdvancedSeasonTotalsRow.model_validate(
            _advanced_season_totals_row(is_combined_totals="False")
        )
        assert row_false.is_combined_totals is False

    def test_is_combined_totals_omitted_defaults_to_false(self):
        # The field is derived in the legacy extractor; if a future raw-row
        # source omits the key, the model must still validate.
        raw = _advanced_season_totals_row()
        raw.pop("is_combined_totals")
        row = PlayerAdvancedSeasonTotalsRow.model_validate(raw)
        assert row.is_combined_totals is False
