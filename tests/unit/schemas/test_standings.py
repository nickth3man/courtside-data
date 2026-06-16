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
                "conference": "Eastern Conference",
                "date": "2024-10-25",
                "1st": "BOS (2-0)",
                "2nd": "MIL (1-0)",
            }
        )
        assert row.conference == Conference.EASTERN
        assert row.date == "2024-10-25"
        assert row.first == "BOS (2-0)"
        assert row.second == "MIL (1-0)"

    def test_empty_optional_cells_become_none(self):
        row = StandingsByDateRow.model_validate(
            {
                "conference": "Eastern Conference",
                "date": "2024-10-25",
                "1st": "",
                "2nd": "",
            }
        )
        assert row.first is None
        assert row.second is None

    def test_missing_required_data_stat_raises(self):
        with pytest.raises(ValidationError):
            StandingsByDateRow.model_validate(
                {
                    "1st": "BOS (2-0)",
                }
            )
