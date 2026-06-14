"""Unit tests for the row schemas in :mod:`courtside_data.schemas.schedule`.

The schedule rows merge ``date_game`` and ``game_start_time`` into a single
``start_time`` ``BRDatetime`` field via a ``model_validator``; tests exercise
the merged validator, the empty-start-time path, and the alias fallbacks for
``away_team``/``home_team``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from courtside_data.data import Team
from courtside_data.schemas.schedule import SeasonScheduleRow, TeamScheduleRow

_EASTERN = ZoneInfo("US/Eastern")


def _expected_start_time(raw_date: str, raw_time: str) -> datetime:
    """Compute the UTC datetime a row should yield for the given BR cells."""
    base = datetime.strptime(raw_date, "%a, %b %d, %Y")
    if not raw_time:
        return base.replace(tzinfo=_EASTERN).astimezone(UTC)
    time_part = raw_time
    if time_part[-2:].lower() in ("am", "pm"):
        parsed = datetime.strptime(f"{raw_date} {time_part}", "%a, %b %d, %Y %I:%M %p")
    else:
        parsed = datetime.strptime(f"{raw_date} {time_part}m", "%a, %b %d, %Y %I:%M%p")
    return parsed.replace(tzinfo=_EASTERN).astimezone(UTC)


class TestTeamScheduleRow:
    def test_happy_path(self):
        raw = {
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
            "game_streak": "W 1",
            "attendance": "18997",
            "game_duration": "2:15",
            "game_remarks": "",
        }
        row = TeamScheduleRow.model_validate(raw)
        assert row.g == 1
        assert row.date_game == "Tue, Oct 30, 2018"
        assert row.game_start_time == "7:30p"
        assert row.network == "TNT"
        assert row.box_score_text == "Box Score"
        assert row.game_location == "@"
        assert row.opp_name == "Los Angeles Lakers"
        assert row.game_result == "W"
        assert row.overtimes is None
        assert row.pts == 112
        assert row.opp_pts == 108
        assert row.wins == 1
        assert row.losses == 0
        assert row.game_streak == "W 1"
        assert row.attendance == 18997
        assert row.game_duration == "2:15"
        assert row.game_remarks is None

    def test_optional_cells_parse_to_none(self):
        row = TeamScheduleRow.model_validate({})
        assert row.g is None
        assert row.date_game is None
        assert row.pts is None
        assert row.opp_pts is None
        assert row.wins is None
        assert row.losses is None
        assert row.attendance is None

    def test_empty_strings_become_none_for_int_fields(self):
        row = TeamScheduleRow.model_validate({"g": "", "pts": "", "opp_pts": "", "attendance": ""})
        assert row.g is None
        assert row.pts is None
        assert row.opp_pts is None
        assert row.attendance is None

    def test_game_result_string_values(self):
        row = TeamScheduleRow.model_validate({"game_result": "W", "opp_name": "Celtics"})
        assert row.game_result == "W"

    def test_game_streak_string_values(self):
        row = TeamScheduleRow.model_validate({"game_streak": "L 3", "opp_name": "Celtics"})
        assert row.game_streak == "L 3"


class TestSeasonScheduleRow:
    def test_happy_path(self):
        raw = {
            "date_game": "Tue, Oct 30, 2018",
            "game_start_time": "7:30p",
            "visitor_team_name": "Boston Celtics",
            "visitor_pts": "112",
            "home_team_name": "Los Angeles Lakers",
            "home_pts": "108",
        }
        row = SeasonScheduleRow.model_validate(raw)
        assert row.start_time == _expected_start_time("Tue, Oct 30, 2018", "7:30p")
        assert row.away_team == Team.BOSTON_CELTICS
        assert row.away_team_score == 112
        assert row.home_team == Team.LOS_ANGELES_LAKERS
        assert row.home_team_score == 108

    def test_empty_start_time_uses_midnight_eastern(self):
        # Upcoming game rows lack a ``game_start_time``; the validator falls
        # back to midnight in the US/Eastern timezone.
        raw = {
            "date_game": "Tue, Apr 1, 2019",
            "game_start_time": "",
            "visitor_team_name": "Miami Heat",
            "visitor_pts": "",
            "home_team_name": "Boston Celtics",
            "home_pts": "",
        }
        row = SeasonScheduleRow.model_validate(raw)
        assert row.start_time == _expected_start_time("Tue, Apr 1, 2019", "")
        assert row.away_team == Team.MIAMI_HEAT
        assert row.away_team_score is None
        assert row.home_team == Team.BOSTON_CELTICS
        assert row.home_team_score is None

    def test_visitor_pts_alias_home_team_name_alias(self):
        # Defensive alias coverage for the ``home_team`` -> ``home_team_name``
        # and ``away_team`` -> ``visitor_team_name`` mapping.
        raw = {
            "date_game": "Tue, Oct 30, 2018",
            "game_start_time": "7:30p",
            "away_team_name": "Boston Celtics",
            "away_team_score": "112",
            "home_team_name": "Los Angeles Lakers",
            "home_team_score": "108",
        }
        row = SeasonScheduleRow.model_validate(raw)
        assert row.away_team == Team.BOSTON_CELTICS
        assert row.home_team == Team.LOS_ANGELES_LAKERS

    def test_missing_required_away_team_raises(self):
        with pytest.raises(ValidationError):
            SeasonScheduleRow.model_validate(
                {
                    "date_game": "Tue, Oct 30, 2018",
                    "game_start_time": "7:30p",
                    "home_team_name": "Los Angeles Lakers",
                    "home_pts": "108",
                }
            )
