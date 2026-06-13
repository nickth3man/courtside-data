from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from pydantic import TypeAdapter, ValidationError

from courtside_data.data import Conference, Division, League, Location, Outcome, Position, Team
from courtside_data.schemas._fields import (
    BRDate,
    BRDatetime,
    BRFloat,
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    BRSalary,
    ConferenceField,
    DivisionField,
    LeagueField,
    LocationField,
    OutcomeField,
    PositionsField,
    SecondsPlayed,
    TeamField,
    TeamNameField,
)


class TestBRInt:
    def test_accepts_int(self):
        assert TypeAdapter(BRInt).validate_python(42) == 42

    def test_accepts_int_string(self):
        assert TypeAdapter(BRInt).validate_python("42") == 42

    def test_accepts_comma_separated_int_string(self):
        assert TypeAdapter(BRInt).validate_python("610,329") == 610329

    def test_rejects_empty_string(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRInt).validate_python("")

    def test_rejects_non_breaking_space(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRInt).validate_python("\xa0")

    def test_rejects_garbage(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRInt).validate_python("abc")


class TestBRIntOrNone:
    def test_empty_string_is_none(self):
        assert TypeAdapter(BRIntOrNone).validate_python("") is None

    def test_non_breaking_space_is_none(self):
        assert TypeAdapter(BRIntOrNone).validate_python("\xa0") is None

    def test_valid_int_parses(self):
        assert TypeAdapter(BRIntOrNone).validate_python("42") == 42

    def test_comma_separated_int_parses(self):
        assert TypeAdapter(BRIntOrNone).validate_python("610,329") == 610329

    def test_garbage_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRIntOrNone).validate_python("abc")


class TestBRFloat:
    def test_accepts_float_string(self):
        assert TypeAdapter(BRFloat).validate_python("0.456") == pytest.approx(0.456)

    def test_rejects_empty_string(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRFloat).validate_python("")

    def test_rejects_garbage(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRFloat).validate_python("abc")


class TestBRFloatOrNone:
    def test_empty_string_is_none(self):
        assert TypeAdapter(BRFloatOrNone).validate_python("") is None

    def test_valid_float_parses(self):
        assert TypeAdapter(BRFloatOrNone).validate_python("0.456") == pytest.approx(0.456)


class TestSecondsPlayed:
    def test_empty_string_is_zero(self):
        assert TypeAdapter(SecondsPlayed).validate_python("") == 0

    def test_zero_seconds(self):
        assert TypeAdapter(SecondsPlayed).validate_python("0:01") == 1

    def test_59_seconds(self):
        assert TypeAdapter(SecondsPlayed).validate_python("0:59") == 59

    def test_one_minute(self):
        assert TypeAdapter(SecondsPlayed).validate_python("1:00") == 60

    def test_one_minute_one_second(self):
        assert TypeAdapter(SecondsPlayed).validate_python("1:01") == 61

    def test_59_minutes_59_seconds(self):
        assert TypeAdapter(SecondsPlayed).validate_python("59:59") == 3599

    def test_60_minutes(self):
        assert TypeAdapter(SecondsPlayed).validate_python("60:00") == 3600

    def test_60_minutes_and_1_second(self):
        assert TypeAdapter(SecondsPlayed).validate_python("60:01") == 3601

    def test_garbage_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(SecondsPlayed).validate_python("abc")

    def test_too_many_parts_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(SecondsPlayed).validate_python("1:2:3")


class TestTeamField:
    def test_abbreviation_maps_to_team(self):
        assert TypeAdapter(TeamField).validate_python("BOS") == Team.BOSTON_CELTICS

    def test_unknown_abbreviation_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(TeamField).validate_python("XYZ")


class TestTeamNameField:
    def test_full_name_maps_to_team(self):
        assert TypeAdapter(TeamNameField).validate_python("Boston Celtics") == Team.BOSTON_CELTICS

    def test_unknown_name_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(TeamNameField).validate_python("Springfield Isotopes")


class TestLocationField:
    def test_away_symbol(self):
        assert TypeAdapter(LocationField).validate_python("@") == Location.AWAY

    def test_home_symbol(self):
        assert TypeAdapter(LocationField).validate_python("") == Location.HOME

    def test_unknown_location_symbol_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(LocationField).validate_python("jaebaebae")


class TestOutcomeField:
    def test_parse_win(self):
        assert TypeAdapter(OutcomeField).validate_python("W") == Outcome.WIN

    def test_parse_loss(self):
        assert TypeAdapter(OutcomeField).validate_python("L") == Outcome.LOSS

    def test_parse_win_with_margin(self):
        assert TypeAdapter(OutcomeField).validate_python("W (+10)") == Outcome.WIN

    def test_parse_loss_with_margin(self):
        assert TypeAdapter(OutcomeField).validate_python("L (-5)") == Outcome.LOSS

    def test_unknown_outcome_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(OutcomeField).validate_python("jaebaebae")


class TestPositionsField:
    def test_single_position(self):
        assert TypeAdapter(PositionsField).validate_python("PG") == [Position.POINT_GUARD]

    def test_multiple_positions(self):
        assert TypeAdapter(PositionsField).validate_python("PG-SG") == [
            Position.POINT_GUARD,
            Position.SHOOTING_GUARD,
        ]

    def test_empty_string_is_empty_list(self):
        assert TypeAdapter(PositionsField).validate_python("") == []

    def test_position_list_is_idempotent(self):
        assert TypeAdapter(PositionsField).validate_python([Position.POINT_GUARD]) == [Position.POINT_GUARD]

    def test_unknown_position_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(PositionsField).validate_python("XX")


class TestDivisionField:
    def test_short_name(self):
        assert TypeAdapter(DivisionField).validate_python("ATLANTIC") == Division.ATLANTIC

    def test_full_name(self):
        assert TypeAdapter(DivisionField).validate_python("Atlantic Division") == Division.ATLANTIC

    def test_unknown_division_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(DivisionField).validate_python("Mars Division")


class TestConferenceField:
    def test_short_name(self):
        assert TypeAdapter(ConferenceField).validate_python("EASTERN") == Conference.EASTERN

    def test_full_name(self):
        assert TypeAdapter(ConferenceField).validate_python("Eastern Conference") == Conference.EASTERN

    def test_unknown_conference_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(ConferenceField).validate_python("Martian Conference")


class TestLeagueField:
    def test_nba(self):
        assert TypeAdapter(LeagueField).validate_python("NBA") == League.NATIONAL_BASKETBALL_ASSOCIATION

    def test_aba(self):
        assert TypeAdapter(LeagueField).validate_python("ABA") == League.AMERICAN_BASKETBALL_ASSOCIATION

    def test_baa(self):
        assert TypeAdapter(LeagueField).validate_python("BAA") == League.BASKETBALL_ASSOCIATION_OF_AMERICA

    def test_unknown_league_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(LeagueField).validate_python("jaebaebae")


class TestBRDate:
    def test_parses_br_date(self):
        assert TypeAdapter(BRDate).validate_python("Tue, Oct 17, 2017") == date(2017, 10, 17)

    def test_parses_iso_date(self):
        assert TypeAdapter(BRDate).validate_python("2017-10-17") == date(2017, 10, 17)

    def test_garbage_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRDate).validate_python("not a date")


class TestBRDatetime:
    def _expected(self, hour: int, minute: int) -> datetime:
        return datetime(2017, 10, 17, hour, minute).replace(tzinfo=ZoneInfo("US/Eastern")).astimezone(UTC)

    def test_current_pm_formatting(self):
        parsed = TypeAdapter(BRDatetime).validate_python(("Tue, Oct 17, 2017", "8:01p"))
        expected = self._expected(20, 1)
        assert abs(parsed - expected) < timedelta(seconds=1)

    def test_current_am_formatting(self):
        parsed = TypeAdapter(BRDatetime).validate_python(("Tue, Oct 17, 2017", "8:01a"))
        expected = self._expected(8, 1)
        assert abs(parsed - expected) < timedelta(seconds=1)

    def test_previous_pm_formatting(self):
        parsed = TypeAdapter(BRDatetime).validate_python(("Tue, Oct 17, 2017", "7:30 pm"))
        expected = self._expected(19, 30)
        assert abs(parsed - expected) < timedelta(seconds=1)

    def test_previous_am_formatting(self):
        parsed = TypeAdapter(BRDatetime).validate_python(("Tue, Oct 17, 2017", "7:30 am"))
        expected = self._expected(7, 30)
        assert abs(parsed - expected) < timedelta(seconds=1)

    def test_date_only_defaults_to_midnight(self):
        parsed = TypeAdapter(BRDatetime).validate_python("Tue, Oct 17, 2017")
        expected = self._expected(0, 0)
        assert abs(parsed - expected) < timedelta(seconds=1)

    def test_garbage_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRDatetime).validate_python("not a datetime")


class TestBRPercentage:
    def test_decimal_form(self):
        assert TypeAdapter(BRPercentage).validate_python("0.456") == pytest.approx(0.456)

    def test_percentage_form(self):
        assert TypeAdapter(BRPercentage).validate_python("45.6%") == pytest.approx(0.456)

    def test_empty_is_none(self):
        assert TypeAdapter(BRPercentage).validate_python("") is None

    def test_garbage_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRPercentage).validate_python("abc")


class TestBRSalary:
    def test_parses_salary(self):
        assert TypeAdapter(BRSalary).validate_python("$1,234,567") == 1234567

    def test_empty_is_none(self):
        assert TypeAdapter(BRSalary).validate_python("") is None

    def test_garbage_raises(self):
        with pytest.raises(ValidationError):
            TypeAdapter(BRSalary).validate_python("abc")


class TestSchemaDriftError:
    def test_extracts_missing_field(self):
        from courtside_data.errors import SchemaDriftError

        err = SchemaDriftError(
            endpoint_name="league_per_game",
            url="/leagues/NBA_2024_per_game.html",
            pydantic_errors=[
                {
                    "type": "missing",
                    "loc": ("points_per_game",),
                    "msg": "Field required",
                    "input": {"fg_per_g": "7.5"},
                }
            ],
        )
        assert err.endpoint_name == "league_per_game"
        assert err.url == "/leagues/NBA_2024_per_game.html"
        assert "points_per_game" in str(err)
        assert "league_per_game" in str(err)
