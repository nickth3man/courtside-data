"""Unit tests for the playoff row schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import Position, Team
from courtside_data.output.columns import (
    PLAYOFF_BRACKET_COLUMN_NAMES,
    PLAYOFF_PER_GAME_COLUMN_NAMES,
    PLAYOFF_TOTALS_COLUMN_NAMES,
)
from courtside_data.schemas.playoffs import (
    PlayoffBracketRow,
    PlayoffPerGameRow,
    PlayoffTotalsRow,
)

# ---------------------------------------------------------------------------
# Per-game / totals — mirror the league per-game/totals layout
# ---------------------------------------------------------------------------


def _full_playoff_per_game_row() -> dict[str, str]:
    return {
        "name_display": "Jayson Tatum",
        "pos": "SF",
        "age": "25",
        "team_name_abbr": "BOS",
        "games": "20",
        "games_started": "20",
        "mp_per_g": "40.1",
        "fg_per_g": "9.9",
        "fga_per_g": "21.4",
        "fg_pct": ".463",
        "fg3_per_g": "3.4",
        "fg3a_per_g": "8.2",
        "fg3_pct": ".415",
        "fg2_per_g": "6.5",
        "fg2a_per_g": "13.2",
        "fg2_pct": ".492",
        "efg_pct": ".542",
        "ft_per_g": "5.8",
        "fta_per_g": "6.9",
        "ft_pct": ".841",
        "orb_per_g": "1.0",
        "drb_per_g": "7.9",
        "trb_per_g": "8.9",
        "ast_per_g": "5.1",
        "stl_per_g": "1.2",
        "blk_per_g": "0.5",
        "tov_per_g": "2.8",
        "pf_per_g": "2.2",
        "pts_per_g": "29.0",
    }


class TestPlayoffPerGameRow:
    def test_happy_path(self):
        row = PlayoffPerGameRow.model_validate(_full_playoff_per_game_row())
        assert row.name_display == "Jayson Tatum"
        assert row.positions == [Position.SMALL_FORWARD]
        assert row.team == Team.BOSTON_CELTICS
        assert row.points_per_game == pytest.approx(29.0)
        assert row.three_point_field_goal_percentage == pytest.approx(0.415)

    def test_empty_optional_cells_become_none(self):
        raw = _full_playoff_per_game_row()
        raw["team_name_abbr"] = ""
        raw["games_started"] = ""
        raw["ft_pct"] = ""
        row = PlayoffPerGameRow.model_validate(raw)
        assert row.team is None
        assert row.games_started is None
        assert row.free_throw_percentage is None

    def test_missing_required_data_stat_raises(self):
        raw = _full_playoff_per_game_row()
        del raw["name_display"]
        with pytest.raises(ValidationError):
            PlayoffPerGameRow.model_validate(raw)

    def test_field_count_matches_column_constant(self):
        assert len(PlayoffPerGameRow.model_fields) == len(PLAYOFF_PER_GAME_COLUMN_NAMES)


def _full_playoff_totals_row() -> dict[str, str]:
    return {
        "name_display": "Jayson Tatum",
        "pos": "SF",
        "age": "25",
        "team_name_abbr": "BOS",
        "games": "20",
        "games_started": "20",
        "mp": "802",
        "fg": "198",
        "fga": "428",
        "fg_pct": ".463",
        "fg3": "68",
        "fg3a": "164",
        "fg3_pct": ".415",
        "fg2": "130",
        "fg2a": "264",
        "fg2_pct": ".492",
        "efg_pct": ".542",
        "ft": "116",
        "fta": "138",
        "ft_pct": ".841",
        "orb": "20",
        "drb": "158",
        "trb": "178",
        "ast": "102",
        "stl": "24",
        "blk": "10",
        "tov": "56",
        "pf": "44",
        "pts": "580",
    }


class TestPlayoffTotalsRow:
    def test_happy_path(self):
        row = PlayoffTotalsRow.model_validate(_full_playoff_totals_row())
        assert row.name_display == "Jayson Tatum"
        assert row.made_field_goals == 198
        assert row.points == 580
        assert row.effective_field_goal_percentage == pytest.approx(0.542)
        assert row.two_point_field_goal_percentage == pytest.approx(0.492)

    def test_empty_optional_cells_become_none(self):
        raw = {
            "name_display": "Jayson Tatum",
            "pos": "SF",
            "age": "25",
            "team_name_abbr": "BOS",
        }
        row = PlayoffTotalsRow.model_validate(raw)
        assert row.games_played is None
        assert row.points is None
        assert row.field_goal_percentage is None

    def test_missing_required_data_stat_raises(self):
        raw = _full_playoff_totals_row()
        del raw["name_display"]
        with pytest.raises(ValidationError):
            PlayoffTotalsRow.model_validate(raw)

    def test_field_count_matches_column_constant(self):
        assert len(PlayoffTotalsRow.model_fields) == len(PLAYOFF_TOTALS_COLUMN_NAMES)


# ---------------------------------------------------------------------------
# Bracket
# ---------------------------------------------------------------------------


class TestPlayoffBracketRow:
    def test_happy_path(self):
        row = PlayoffBracketRow.model_validate(
            {
                "series": "NBA Finals",
                "team": "Boston Celtics",
                "result": "Won NBA Championship",
            }
        )
        assert row.series == "NBA Finals"
        assert row.team == "Boston Celtics"
        assert row.result == "Won NBA Championship"

    def test_accepts_header_fallback_keys(self):
        # The use_header_fallback path emits normalized header text as the
        # row keys; the model should accept the same shape either way.
        row = PlayoffBracketRow.model_validate(
            {
                "series": "Eastern Conference Finals",
                "team": "Miami Heat",
                "result": "Lost Conference Finals",
            }
        )
        assert row.series == "Eastern Conference Finals"
        assert row.team == "Miami Heat"
        assert row.result == "Lost Conference Finals"

    def test_missing_required_series_raises(self):
        with pytest.raises(ValidationError):
            PlayoffBracketRow.model_validate({"team": "Boston Celtics", "result": "Won"})

    def test_field_count_matches_column_constant(self):
        assert len(PlayoffBracketRow.model_fields) == len(PLAYOFF_BRACKET_COLUMN_NAMES)
