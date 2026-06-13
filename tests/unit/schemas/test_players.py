"""Unit tests for the row schemas in :mod:`courtside_data.schemas.players`.

Each model gets a focused test class that covers the happy path, an empty
or optional cell, and a missing required ``data-stat`` alias.  Tests use
synthetic raw rows that mirror the ``data-stat`` keys BR emits.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import League, Position, Team
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
        assert row.team == Team.LOS_ANGELES_LAKERS
        assert row.league == League.NATIONAL_BASKETBALL_ASSOCIATION
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
        row = PlayerPlayoffSeriesRow.model_validate(_career_row(games="5", games_started="5"))
        assert row.season == "2023-24"
        assert row.games_played == 5
        assert row.team == Team.LOS_ANGELES_LAKERS

    def test_missing_required_team_raises(self):
        raw = _career_row()
        raw.pop("team_name_abbr")
        with pytest.raises(ValidationError):
            PlayerPlayoffSeriesRow.model_validate(raw)


class TestPlayerAllStarRow:
    def test_happy_path(self):
        # All-Star rows lack the two-point columns but the per-game mixin
        # accepts them as optional and leaves them None.
        row = PlayerAllStarRow.model_validate(_career_row(fg2_per_g="", fg2a_per_g="", fg2_pct="", efg_pct=""))
        assert row.season == "2023-24"
        assert row.team == Team.LOS_ANGELES_LAKERS
        assert row.made_two_point_field_goals_per_game is None
        assert row.attempted_two_point_field_goals_per_game is None
        assert row.two_point_field_goal_percentage is None
        assert row.effective_field_goal_percentage is None

    def test_missing_required_league_raises(self):
        raw = _career_row()
        raw.pop("league_id")
        with pytest.raises(ValidationError):
            PlayerAllStarRow.model_validate(raw)


class TestPlayerAdjustedShootingRow:
    def test_happy_path(self):
        row = PlayerAdjustedShootingRow.model_validate(
            {
                "season": "2023-24",
                "age": "39",
                "team_name_abbr": "LAL",
                "league_id": "NBA",
                "pos": "SF",
                "g": "71",
                "mp": "2506",
                "fg_pct": ".502",
                "fg3_pct": ".410",
                "ft_pct": ".750",
                "ts_pct": ".580",
                "fg_per_36_min": "10.0",
                "fga_per_36_min": "20.0",
                "adjusted_fg_pct": ".510",
                "adjusted_fg3_pct": ".420",
                "adjusted_ft_pct": ".760",
            }
        )
        assert row.games_played == 71
        assert row.minutes_played == 2506
        assert row.true_shooting_percentage == pytest.approx(0.580)
        assert row.field_goals_per_36_minutes == pytest.approx(10.0)
        assert row.adjusted_field_goal_percentage == pytest.approx(0.510)

    def test_empty_pct_cells_parse_to_none(self):
        row = PlayerAdjustedShootingRow.model_validate(
            {
                "season": "2023-24",
                "team_name_abbr": "LAL",
                "league_id": "NBA",
                "g": "0",
                "mp": "0",
                "fg_pct": "",
                "fg3_pct": "",
                "ft_pct": "",
            }
        )
        assert row.field_goal_percentage is None
        assert row.three_point_field_goal_percentage is None
        assert row.free_throw_percentage is None
        assert row.true_shooting_percentage is None

    def test_missing_required_season_raises(self):
        raw = {
            "team_name_abbr": "LAL",
            "league_id": "NBA",
            "g": "71",
            "mp": "2506",
        }
        with pytest.raises(ValidationError):
            PlayerAdjustedShootingRow.model_validate(raw)


class TestPlayerPlayByPlayStatsRow:
    def test_happy_path(self):
        row = PlayerPlayByPlayStatsRow.model_validate(
            {
                "season": "2023-24",
                "age": "39",
                "team_name_abbr": "LAL",
                "league_id": "NBA",
                "pos": "SF",
                "g": "71",
                "mp": "2506",
                "pct_fg_2pt": ".710",
                "pct_fg_3pt": ".290",
                "pct_ast_2pt": ".420",
                "pct_ast_3pt": ".650",
                "pct_dunks": ".080",
                "pct_corner_3s": ".120",
                "pct_heaves": ".001",
            }
        )
        assert row.season == "2023-24"
        assert row.games_played == 71
        assert row.percentage_of_two_point_field_goals == pytest.approx(0.710)
        assert row.percentage_heaves == pytest.approx(0.001)

    def test_empty_pct_cells_parse_to_none(self):
        row = PlayerPlayByPlayStatsRow.model_validate(
            {
                "season": "2023-24",
                "team_name_abbr": "LAL",
                "league_id": "NBA",
                "g": "0",
                "mp": "0",
                "pct_fg_2pt": "",
                "pct_heaves": "",
            }
        )
        assert row.percentage_of_two_point_field_goals is None
        assert row.percentage_heaves is None

    def test_missing_required_team_raises(self):
        raw = {
            "season": "2023-24",
            "league_id": "NBA",
            "g": "71",
            "mp": "2506",
        }
        with pytest.raises(ValidationError):
            PlayerPlayByPlayStatsRow.model_validate(raw)


class TestPlayerGameHighsRow:
    def test_happy_path(self):
        row = PlayerGameHighsRow.model_validate(
            {
                "stat": "Points",
                "value": "48",
                "date": "2024-01-15",
                "opponent": "Los Angeles Lakers",
            }
        )
        assert row.stat == "Points"
        assert row.value == 48
        assert row.date.isoformat() == "2024-01-15"
        assert row.opponent == Team.LOS_ANGELES_LAKERS

    def test_missing_required_value_raises(self):
        with pytest.raises(ValidationError):
            PlayerGameHighsRow.model_validate(
                {
                    "stat": "Points",
                    "date": "2024-01-15",
                    "opponent": "Los Angeles Lakers",
                }
            )


class TestPlayerSimilarityScoresRow:
    def test_happy_path(self):
        row = PlayerSimilarityScoresRow.model_validate(
            {
                "rank": "1",
                "player": "Kareem Abdul-Jabbar",
                "similarity_score": "98.5",
            }
        )
        assert row.rank == 1
        assert row.player == "Kareem Abdul-Jabbar"
        assert row.similarity_score == pytest.approx(98.5)

    def test_missing_required_player_raises(self):
        with pytest.raises(ValidationError):
            PlayerSimilarityScoresRow.model_validate({"rank": "1", "similarity_score": "98.5"})


class TestPlayerSalariesRow:
    def test_happy_path(self):
        row = PlayerSalariesRow.model_validate(
            {
                "season": "2023-24",
                "team_id": "LAL",
                "salary": "$47,607,350",
            }
        )
        assert row.season == "2023-24"
        assert row.team == Team.LOS_ANGELES_LAKERS
        assert row.salary == 47607350

    def test_team_name_abbr_alias_fallback(self):
        # The historical column list names the team column ``team_id`` but
        # some older fixtures surface it as ``team_name_abbr``.
        row = PlayerSalariesRow.model_validate(
            {
                "season": "2023-24",
                "team_name_abbr": "LAL",
                "salary": "$47,607,350",
            }
        )
        assert row.team == Team.LOS_ANGELES_LAKERS

    def test_empty_salary_parses_to_none(self):
        row = PlayerSalariesRow.model_validate(
            {
                "season": "2023-24",
                "team_id": "LAL",
                "salary": "",
            }
        )
        assert row.salary is None

    def test_missing_required_season_raises(self):
        with pytest.raises(ValidationError):
            PlayerSalariesRow.model_validate({"team_id": "LAL", "salary": "$1"})


class TestPlayerShotChartsRow:
    def test_happy_path(self):
        row = PlayerShotChartsRow.model_validate(
            {
                "shot_type": "Dunk",
                "made": "120",
                "attempted": "125",
                "fg_pct": ".960",
            }
        )
        assert row.shot_type == "Dunk"
        assert row.made == 120
        assert row.attempted == 125
        assert row.field_goal_percentage == pytest.approx(0.96)

    def test_optional_shot_count_cells_parse_to_none(self):
        row = PlayerShotChartsRow.model_validate({"shot_type": "Heave", "made": "", "attempted": "", "fg_pct": ""})
        assert row.made is None
        assert row.attempted is None
        assert row.field_goal_percentage is None

    def test_missing_required_shot_type_raises(self):
        with pytest.raises(ValidationError):
            PlayerShotChartsRow.model_validate({"made": "10", "attempted": "20", "fg_pct": ".500"})


class TestPlayerSplitsRow:
    def test_happy_path(self):
        row = PlayerSplitsRow.model_validate(
            {
                "split_type": "Location",
                "value": "Home",
                "g": "35",
                "mp": "1235",
                "fg": "350",
                "fga": "680",
                "fg_pct": ".515",
                "fg3": "80",
                "fg3a": "180",
                "fg3_pct": ".444",
                "ft": "120",
                "fta": "160",
                "ft_pct": ".750",
                "orb": "25",
                "drb": "190",
                "trb": "215",
                "ast": "300",
                "stl": "45",
                "blk": "18",
                "tov": "100",
                "pf": "40",
                "pts": "900",
            }
        )
        assert row.split_type == "Location"
        assert row.value == "Home"
        assert row.games_played == 35
        assert row.points == 900
        assert row.field_goal_percentage == pytest.approx(0.515)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = PlayerSplitsRow.model_validate({"split_type": "Location", "value": "Home"})
        assert row.games_played is None
        assert row.points is None
        assert row.field_goal_percentage is None

    def test_missing_required_split_type_raises(self):
        with pytest.raises(ValidationError):
            PlayerSplitsRow.model_validate({"value": "Home", "g": "35", "pts": "900"})


class TestPlayerOnOffRow:
    def test_happy_path(self):
        row = PlayerOnOffRow.model_validate(
            {
                "situation": "On Court",
                "g": "71",
                "mp": "2506",
                "fg": "696",
                "fga": "1392",
                "fg_pct": ".502",
                "fg3": "149",
                "fg3a": "362",
                "fg3_pct": ".410",
                "ft": "241",
                "fta": "320",
                "ft_pct": ".750",
                "orb": "57",
                "drb": "391",
                "trb": "448",
                "ast": "589",
                "stl": "92",
                "blk": "36",
                "tov": "206",
                "pf": "78",
                "pts": "1782",
            }
        )
        assert row.situation == "On Court"
        assert row.games_played == 71
        assert row.points == 1782
        assert row.three_point_field_goal_percentage == pytest.approx(0.410)

    def test_optional_stat_block_cells_parse_to_none(self):
        row = PlayerOnOffRow.model_validate({"situation": "On"})
        assert row.games_played is None
        assert row.points is None

    def test_missing_required_situation_raises(self):
        with pytest.raises(ValidationError):
            PlayerOnOffRow.model_validate({"g": "71", "pts": "1782"})


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
        "fg3": "149",
        "fg3a": "362",
        "ft": "241",
        "fta": "320",
        "orb": "57",
        "drb": "391",
        "ast": "589",
        "stl": "92",
        "blk": "36",
        "tov": "206",
        "pf": "78",
        "pts": "1782",
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
        assert row.points == 1782
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
                fg3="",
                fg3a="",
                ft="",
                fta="",
                orb="",
                drb="",
                ast="",
                stl="",
                blk="",
                tov="",
                pf="",
                pts="0",
            )
        )
        assert row.age is None
        assert row.games_started is None
        assert row.minutes_played is None
        assert row.points == 0
        assert row.made_field_goals == 0
        assert row.attempted_field_goals is None
        assert row.assists is None

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
                "mp": "0",
            }
        )
        assert row.age is None
        assert row.positions == []
        assert row.games_played == 0
        assert row.minutes_played == 0
        assert row.player_efficiency_rating is None
        assert row.true_shooting_percentage is None
        assert row.value_over_replacement_player is None
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
