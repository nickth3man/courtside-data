from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from unittest import TestCase


from courtside_data.parsers import ScheduledStartTimeParser


class TestScheduledStartTimeParser(TestCase):
    def test_correctly_parses_time_for_current_pm_formatting(self):
        parsed_start_time = ScheduledStartTimeParser().parse_start_time(
            formatted_date="Tue, Oct 17, 2017",
            formatted_time_of_day="8:01p"
        )
        expected_datetime = datetime(year=2017, month=10, day=17, hour=20, minute=1).replace(tzinfo=ZoneInfo("US/Eastern")).astimezone(timezone.utc)

        self.assertTrue(abs(parsed_start_time - expected_datetime) < timedelta(seconds=1))

    def test_correctly_parses_time_for_current_am_formatting(self):
        parsed_start_time = ScheduledStartTimeParser().parse_start_time(
            formatted_date="Tue, Oct 17, 2017",
            formatted_time_of_day="8:01a"
        )
        expected_datetime = datetime(year=2017, month=10, day=17, hour=8, minute=1).replace(tzinfo=ZoneInfo("US/Eastern")).astimezone(timezone.utc)

        self.assertTrue(abs(parsed_start_time - expected_datetime) < timedelta(seconds=1))

    def test_correctly_parses_time_for_previous_pm_formatting(self):
        parsed_start_time = ScheduledStartTimeParser().parse_start_time(
            formatted_date="Tue, Oct 17, 2017",
            formatted_time_of_day="7:30 pm"
        )
        expected_datetime = datetime(year=2017, month=10, day=17, hour=19, minute=30).replace(tzinfo=ZoneInfo("US/Eastern")).astimezone(timezone.utc)

        self.assertTrue(abs(parsed_start_time - expected_datetime) < timedelta(seconds=1))

    def test_correctly_parses_time_for_previous_am_formatting(self):
        parsed_start_time = ScheduledStartTimeParser().parse_start_time(
            formatted_date="Tue, Oct 17, 2017",
            formatted_time_of_day="7:30 am"
        )
        expected_datetime = datetime(year=2017, month=10, day=17, hour=7, minute=30).replace(tzinfo=ZoneInfo("US/Eastern")).astimezone(timezone.utc)

        self.assertTrue(abs(parsed_start_time - expected_datetime) < timedelta(seconds=1))
