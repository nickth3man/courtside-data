"""Unit tests for the row schemas in :mod:`courtside_data.schemas.schedule`.

The schedule rows merge ``date_game`` and ``game_start_time`` into a single
``start_time`` ``BRDatetime`` field via a ``model_validator``; tests exercise
the merged validator, the empty-start-time path, and the alias fallbacks for
``away_team``/``home_team``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from courtside_data.data import Outcome, Team
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
    def test_happy_path_using_g_and_visitor_aliases(self):
        raw = {
            "g": "1",
            "date_game": "Tue, Oct 30, 2018",
            "game_start_time": "7:30p",
            "visitor_team_name": "Boston Celtics",
            "visitor_pts": "112",
            "home_team_name": "Los Angeles Lakers",
            "home_pts": "108",
            "game_result": "W",
            "overtimes": "",
            "wins": "1",
            "losses": "0",
            "streak": "W 1",
        }
        row = TeamScheduleRow.model_validate(raw)
        assert row.game_number == 1
        assert row.date == date(2018, 10, 30)
        assert row.start_time == _expected_start_time("Tue, Oct 30, 2018", "7:30p")
        assert row.away_team == Team.BOSTON_CELTICS
        assert row.away_team_score == 112
        assert row.home_team == Team.LOS_ANGELES_LAKERS
        assert row.home_team_score == 108
        assert row.result == Outcome.WIN
        assert row.overtimes == ""
        assert row.wins == 1
        assert row.losses == 0
        assert row.streak == "W 1"

    def test_alternative_aliases_away_team_name_and_team_name(self):
        # Some BR pages expose the team schedule with ``away_team_name`` for
        # the visitor and ``team_name`` for the home squad.
        raw = {
            "game_number": "1",
            "date_game": "Tue, Oct 30, 2018",
            "game_start_time": "7:30p",
            "away_team_name": "Boston Celtics",
            "away_team_score": "112",
            "team_name": "Los Angeles Lakers",
            "home_team_score": "108",
            "result": "L",
            "wins": "1",
            "losses": "0",
            "streak": "W 1",
        }
        row = TeamScheduleRow.model_validate(raw)
        assert row.away_team == Team.BOSTON_CELTICS
        assert row.home_team == Team.LOS_ANGELES_LAKERS
        assert row.result == Outcome.LOSS

    def test_opp_name_alias(self):
        # ``opp_name`` is the data-stat on the franchise-team schedule pages.
        raw = {
            "game_number": "1",
            "date_game": "Tue, Oct 30, 2018",
            "game_start_time": "7:30p",
            "opp_name": "Boston Celtics",
            "opp_pts": "112",
            "team_name": "Los Angeles Lakers",
            "tm_pts": "108",
            "result": "L",
            "wins": "1",
            "losses": "0",
            "streak": "W 1",
        }
        row = TeamScheduleRow.model_validate(raw)
        assert row.away_team == Team.BOSTON_CELTICS
        assert row.away_team_score == 112
        assert row.home_team == Team.LOS_ANGELES_LAKERS
        assert row.home_team_score == 108

    def test_optional_score_and_overtime_cells_parse_to_none(self):
        # Future games on a team schedule leave the score columns empty.
        raw = {
            "g": "1",
            "date_game": "Tue, Oct 30, 2018",
            "game_start_time": "7:30p",
            "visitor_team_name": "Boston Celtics",
            "visitor_pts": "",
            "home_team_name": "Los Angeles Lakers",
            "home_pts": "",
            "game_result": "W",
            "overtimes": "",
            "wins": "0",
            "losses": "0",
            "streak": "",
        }
        row = TeamScheduleRow.model_validate(raw)
        assert row.away_team_score is None
        assert row.home_team_score is None
        assert row.overtimes == ""

    def test_missing_required_game_number_raises(self):
        with pytest.raises(ValidationError):
            TeamScheduleRow.model_validate(
                {
                    "date_game": "Tue, Oct 30, 2018",
                    "game_start_time": "7:30p",
                    "visitor_team_name": "Boston Celtics",
                    "visitor_pts": "112",
                    "home_team_name": "Los Angeles Lakers",
                    "home_pts": "108",
                    "game_result": "W",
                    "overtimes": "",
                    "wins": "1",
                    "losses": "0",
                    "streak": "W 1",
                }
            )


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
