"""Unit tests for the standings row schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import Conference, Division, Team
from courtside_data.schemas.standings import StandingsByDateRow, StandingsRow


class TestStandingsRow:
    def test_happy_path(self):
        row = StandingsRow.model_validate(
            {
                "team": Team.BOSTON_CELTICS,
                "wins": 57,
                "losses": 25,
                "division": Division.ATLANTIC,
                "conference": Conference.EASTERN,
            }
        )
        assert row.team == Team.BOSTON_CELTICS
        assert row.wins == 57
        assert row.losses == 25
        assert row.division == Division.ATLANTIC
        assert row.conference == Conference.EASTERN

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            StandingsRow.model_validate(
                {
                    "wins": 57,
                    "losses": 25,
                    "division": Division.ATLANTIC,
                    "conference": Conference.EASTERN,
                }
            )


class TestStandingsByDateRow:
    def test_happy_path(self):
        row = StandingsByDateRow.model_validate(
            {
                "team_name_abbr": "BOS",
                "wins": "30",
                "losses": "10",
                "win_loss_pct": ".750",
                "gb": "0.0",
                "pts_per_g": "118.4",
                "opp_pts_per_g": "112.1",
                "srs": "6.32",
            }
        )
        assert row.team == Team.BOSTON_CELTICS
        assert row.wins == 30
        assert row.losses == 10
        assert row.win_loss_percentage == pytest.approx(0.750)
        assert row.games_back == pytest.approx(0.0)
        assert row.points_per_game == pytest.approx(118.4)
        assert row.opponent_points_per_game == pytest.approx(112.1)
        assert row.simple_rating_system == pytest.approx(6.32)

    def test_empty_optional_cells_become_none(self):
        row = StandingsByDateRow.model_validate(
            {
                "team_name_abbr": "BOS",
                "wins": "30",
                "losses": "10",
                "win_loss_pct": "",
                "gb": "",
                "pts_per_g": "",
                "opp_pts_per_g": "",
                "srs": "",
            }
        )
        assert row.win_loss_percentage is None
        assert row.games_back is None
        assert row.points_per_game is None
        assert row.opponent_points_per_game is None
        assert row.simple_rating_system is None

    def test_missing_required_data_stat_raises(self):
        with pytest.raises(ValidationError):
            StandingsByDateRow.model_validate(
                {
                    "wins": "30",
                    "losses": "10",
                    "win_loss_pct": ".750",
                    "gb": "0.0",
                    "pts_per_g": "118.4",
                    "opp_pts_per_g": "112.1",
                    "srs": "6.32",
                }
            )
