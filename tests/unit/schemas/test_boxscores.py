"""Unit tests for the row schemas in :mod:`courtside_data.schemas.boxscores`.

Each model gets a focused test class that covers the happy path, an empty
or optional cell, and a missing required ``data-stat`` alias.  Box-score
tests include a "MM:SS" conversion check against the legacy 3607-seconds
expectation.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import Location, Outcome, Team
from courtside_data.schemas.boxscores import (
    PlayerBoxScoreRow,
    PlayoffPlayerBoxScoreRow,
    RegularSeasonPlayerBoxScoreRow,
    TeamBoxScoreRow,
)


class TestPlayerBoxScoreRow:
    def test_happy_path(self):
        # "60:07" is 60 * 60 + 7 = 3607 seconds — LeBron's career-high
        # overtime total. Mirrors the legacy fixture's Paul Millsap row.
        row = PlayerBoxScoreRow.model_validate(
            {
                "slug": "millspa01",
                "player": "Paul Millsap",
                "team_id": "ATL",
                "game_location": "",
                "opp_id": "NYK",
                "game_result": "W",
                "mp": "60:07",
                "fg": "13",
                "fga": "29",
                "fg_pct": ".448",
                "fg3": "3",
                "fg3a": "8",
                "fg3_pct": ".375",
                "ft": "8",
                "fta": "10",
                "ft_pct": ".800",
                "orb": "8",
                "drb": "11",
                "trb": "19",
                "ast": "7",
                "stl": "1",
                "blk": "0",
                "tov": "3",
                "pf": "4",
                "pts": "37",
                "plus_minus": "-1",
                "game_score": "31.3",
            }
        )
        assert row.slug == "millspa01"
        assert row.name == "Paul Millsap"
        assert row.team == Team.ATLANTA_HAWKS
        assert row.location == Location.HOME
        assert row.opponent == Team.NEW_YORK_KNICKS
        assert row.outcome == Outcome.WIN
        assert row.seconds_played == 3607
        assert row.made_field_goals == 13
        assert row.attempted_three_point_field_goals == 8
        assert row.plus_minus == -1
        assert row.game_score == pytest.approx(31.3)

    def test_38_minutes_45_seconds_converts_to_2325(self):
        row = PlayerBoxScoreRow.model_validate(
            {
                "slug": "tester01",
                "player": "Tester",
                "team_id": "BOS",
                "game_location": "@",
                "opp_id": "MIA",
                "game_result": "L",
                "mp": "38:45",
                "fg": "0",
                "fga": "0",
                "fg3": "0",
                "fg3a": "0",
                "ft": "0",
                "fta": "0",
                "orb": "0",
                "drb": "0",
                "trb": "0",
                "ast": "0",
                "stl": "0",
                "blk": "0",
                "tov": "0",
                "pf": "0",
                "pts": "0",
                "plus_minus": "0",
            }
        )
        assert row.seconds_played == 2325
        assert row.location == Location.AWAY
        assert row.outcome == Outcome.LOSS

    def test_optional_plus_minus_and_percentages_parse_to_none(self):
        # The daily-leaders page occasionally omits percentages when
        # attempts are zero; both fields must default to None.
        row = PlayerBoxScoreRow.model_validate(
            {
                "slug": "zeroes01",
                "player": "Zero Attempter",
                "team_id": "BOS",
                "game_location": "",
                "opp_id": "MIA",
                "game_result": "W",
                "mp": "1:00",
                "fg": "0",
                "fga": "0",
                "fg_pct": "",
                "fg3": "0",
                "fg3a": "0",
                "fg3_pct": "",
                "ft": "0",
                "fta": "0",
                "ft_pct": "",
                "orb": "0",
                "drb": "0",
                "trb": "0",
                "ast": "0",
                "stl": "0",
                "blk": "0",
                "tov": "0",
                "pf": "0",
                "pts": "0",
                "plus_minus": "",
            }
        )
        assert row.field_goal_percentage is None
        assert row.three_point_field_goal_percentage is None
        assert row.free_throw_percentage is None
        assert row.plus_minus is None

    def test_missing_required_slug_raises(self):
        raw = {
            "player": "Anonymous",
            "team_id": "BOS",
            "game_location": "",
            "opp_id": "MIA",
            "game_result": "W",
            "mp": "1:00",
            "fg": "0", "fga": "0", "fg3": "0", "fg3a": "0",
            "ft": "0", "fta": "0", "orb": "0", "drb": "0", "trb": "0",
            "ast": "0", "stl": "0", "blk": "0", "tov": "0", "pf": "0", "pts": "0",
        }
        with pytest.raises(ValidationError):
            PlayerBoxScoreRow.model_validate(raw)


class TestRegularSeasonPlayerBoxScoreRow:
    def test_happy_path(self):
        row = RegularSeasonPlayerBoxScoreRow.model_validate(
            {
                "active": "True",
                "date_game": "2018-10-17",
                "pts": "8",
                "plus_minus": "-9",
                "team_name_abbr": "LAC",
                "game_location": "",
                "opp_name_abbr": "DEN",
                "game_result": "L",
                "mp": "27:36",
                "fg": "4",
                "fga": "10",
                "fg_pct": ".400",
                "fg3": "0",
                "fg3a": "2",
                "fg3_pct": ".000",
                "ft": "0",
                "fta": "0",
                "ft_pct": "",
                "orb": "2",
                "drb": "0",
                "trb": "2",
                "ast": "0",
                "stl": "1",
                "blk": "2",
                "tov": "2",
                "pf": "3",
                "game_score": "3.6",
            }
        )
        assert row.active is True
        assert row.date == "2018-10-17"
        assert row.points_scored == 8
        assert row.plus_minus == -9
        assert row.team == Team.LOS_ANGELES_CLIPPERS
        assert row.opponent == Team.DENVER_NUGGETS
        assert row.outcome == Outcome.LOSS
        assert row.seconds_played == 27 * 60 + 36
        assert row.made_field_goals == 4

    def test_inactive_row_active_false(self):
        row = RegularSeasonPlayerBoxScoreRow.model_validate(
            {
                "active": "False",
                "date_game": "2018-10-19",
                "pts": "",
                "plus_minus": "",
                "team_name_abbr": "LAC",
                "game_location": "",
                "opp_name_abbr": "OKC",
                "game_result": "W",
                "mp": "",
                "fg": "", "fga": "", "fg_pct": "",
                "fg3": "", "fg3a": "", "fg3_pct": "",
                "ft": "", "fta": "", "ft_pct": "",
                "orb": "", "drb": "", "trb": "",
                "ast": "", "stl": "", "blk": "", "tov": "", "pf": "",
                "game_score": "",
            }
        )
        assert row.active is False
        assert row.points_scored is None
        assert row.seconds_played == 0
        assert row.made_field_goals is None

    def test_missing_required_date_raises(self):
        raw = {
            "active": "True",
            "pts": "8",
            "plus_minus": "-9",
            "team_name_abbr": "LAC",
            "game_location": "",
            "opp_name_abbr": "DEN",
            "game_result": "L",
            "mp": "27:36",
        }
        with pytest.raises(ValidationError):
            RegularSeasonPlayerBoxScoreRow.model_validate(raw)


class TestPlayoffPlayerBoxScoreRow:
    def test_happy_path(self):
        # Playoff game logs share the exact same shape as regular-season
        # ones; same data-stat names too.  Keep a single happy-path check
        # that exercises the alias-choices path.
        row = PlayoffPlayerBoxScoreRow.model_validate(
            {
                "active": "True",
                "date": "2024-04-20",  # alternate alias
                "points_scored": "30",  # alternate alias
                "plus_minus": "+12",
                "team_id": "BOS",  # alternate alias
                "game_location": "",
                "opp_id": "MIA",  # alternate alias
                "game_result": "W",
                "mp": "36:00",
                "fg": "11", "fga": "20", "fg_pct": ".550",
                "fg3": "3", "fg3a": "7", "fg3_pct": ".429",
                "ft": "5", "fta": "6", "ft_pct": ".833",
                "orb": "1", "drb": "6", "trb": "7",
                "ast": "4", "stl": "2", "blk": "1", "tov": "2", "pf": "2",
                "pts": "30", "game_score": "26.1",
            }
        )
        assert row.active is True
        assert row.date == "2024-04-20"
        assert row.points_scored == 30
        assert row.team == Team.BOSTON_CELTICS
        assert row.opponent == Team.MIAMI_HEAT
        assert row.outcome == Outcome.WIN
        assert row.seconds_played == 36 * 60

    def test_missing_required_active_raises(self):
        raw = {
            "date": "2024-04-20",
            "pts": "30",
            "plus_minus": "+12",
            "team_id": "BOS",
            "game_location": "",
            "opp_id": "MIA",
            "game_result": "W",
            "mp": "36:00",
        }
        with pytest.raises(ValidationError):
            PlayoffPlayerBoxScoreRow.model_validate(raw)


class TestTeamBoxScoreRow:
    def test_happy_path(self):
        # ``mp`` here is a bare integer team total (e.g. 240 = 48 * 5),
        # not an "MM:SS" string — note the contract difference from the
        # per-player box-score rows.
        row = TeamBoxScoreRow.model_validate(
            {
                "team_name_abbr": "Orlando Magic",
                "mp": "240",
                "fg": "35",
                "fga": "96",
                "fg_pct": ".365",
                "fg3": "6",
                "fg3a": "31",
                "fg3_pct": ".194",
                "ft": "19",
                "fta": "25",
                "ft_pct": ".760",
                "orb": "19",
                "drb": "33",
                "trb": "52",
                "ast": "16",
                "stl": "5",
                "blk": "5",
                "tov": "12",
                "pf": "18",
                "pts": "95",
                "outcome": "L",
            }
        )
        assert row.team == Team.ORLANDO_MAGIC
        assert row.minutes_played == 240
        assert row.points == 95
        assert row.outcome == Outcome.LOSS
        assert row.field_goal_percentage == pytest.approx(0.365)

    def test_optional_pct_cells_parse_to_none(self):
        row = TeamBoxScoreRow.model_validate(
            {
                "team_name_abbr": "Boston Celtics",
                "mp": "240",
                "fg": "0",
                "fga": "0",
                "fg_pct": "",
                "fg3": "0",
                "fg3a": "0",
                "fg3_pct": "",
                "ft": "0",
                "fta": "0",
                "ft_pct": "",
                "orb": "0",
                "drb": "0",
                "trb": "0",
                "ast": "0",
                "stl": "0",
                "blk": "0",
                "tov": "0",
                "pf": "0",
                "pts": "0",
            }
        )
        assert row.field_goal_percentage is None
        assert row.outcome is None

    def test_team_id_alias_fallback(self):
        # Older fixtures expose the team column as ``team_id`` instead
        # of ``team_name_abbr``.
        row = TeamBoxScoreRow.model_validate(
            {
                "team_id": "Boston Celtics",
                "mp": "240",
                "fg": "0", "fga": "0", "fg3": "0", "fg3a": "0",
                "ft": "0", "fta": "0", "orb": "0", "drb": "0", "trb": "0",
                "ast": "0", "stl": "0", "blk": "0", "tov": "0", "pf": "0", "pts": "0",
            }
        )
        assert row.team == Team.BOSTON_CELTICS

    def test_missing_required_team_raises(self):
        with pytest.raises(ValidationError):
            TeamBoxScoreRow.model_validate(
                {
                    "mp": "240",
                    "fg": "0", "fga": "0", "fg3": "0", "fg3a": "0",
                    "ft": "0", "fta": "0", "orb": "0", "drb": "0", "trb": "0",
                    "ast": "0", "stl": "0", "blk": "0", "tov": "0", "pf": "0", "pts": "0",
                }
            )

    def test_missing_required_minutes_played_raises(self):
        with pytest.raises(ValidationError):
            TeamBoxScoreRow.model_validate(
                {
                    "team_name_abbr": "Orlando Magic",
                    "fg": "0", "fga": "0", "fg3": "0", "fg3a": "0",
                    "ft": "0", "fta": "0", "orb": "0", "drb": "0", "trb": "0",
                    "ast": "0", "stl": "0", "blk": "0", "tov": "0", "pf": "0", "pts": "0",
                }
            )
