from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import PeriodType, Team
from courtside_data.schemas.playbyplay import PlayByPlayRow


class TestPlayByPlayRow:
    def test_happy_path(self):
        row = PlayByPlayRow.model_validate(
            {
                "period": 1,
                "period_type": PeriodType.QUARTER,
                "remaining_seconds_in_period": 720.0,
                "relevant_team": Team.BOSTON_CELTICS,
                "away_team": Team.BOSTON_CELTICS,
                "home_team": Team.LOS_ANGELES_LAKERS,
                "away_score": 112,
                "home_score": 108,
                "description": "J. Tatum makes 2-pt shot",
            }
        )
        assert row.period == 1
        assert row.period_type == PeriodType.QUARTER
        assert row.remaining_seconds_in_period == pytest.approx(720.0)
        assert row.relevant_team == Team.BOSTON_CELTICS
        assert row.away_score == 112
        assert row.home_score == 108

    def test_period_type_from_string_and_raw_score_string(self):
        row = PlayByPlayRow.model_validate(
            {
                "period": 5,
                "period_type": "OVERTIME",
                "remaining_seconds_in_period": 300.0,
                "relevant_team": "BOS",
                "away_team": "BOS",
                "home_team": "LAL",
                "away_score": "112-108",
                "home_score": "112-108",
                "description": "Tip-off",
            }
        )
        assert row.period_type == PeriodType.OVERTIME
        assert row.relevant_team == Team.BOSTON_CELTICS
        assert row.away_score == 112
        assert row.home_score == 108

    def test_empty_score_parses_to_none(self):
        row = PlayByPlayRow.model_validate(
            {
                "period": 1,
                "period_type": PeriodType.QUARTER,
                "remaining_seconds_in_period": 720.0,
                "relevant_team": Team.BOSTON_CELTICS,
                "away_team": Team.BOSTON_CELTICS,
                "home_team": Team.LOS_ANGELES_LAKERS,
                "away_score": "",
                "home_score": "\xa0",
                "description": "J. Tatum misses free throw",
            }
        )
        assert row.away_score is None
        assert row.home_score is None

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            PlayByPlayRow.model_validate(
                {
                    "period_type": PeriodType.QUARTER,
                    "remaining_seconds_in_period": 720.0,
                    "relevant_team": Team.BOSTON_CELTICS,
                    "away_team": Team.BOSTON_CELTICS,
                    "home_team": Team.LOS_ANGELES_LAKERS,
                    "description": "J. Tatum misses free throw",
                }
            )
