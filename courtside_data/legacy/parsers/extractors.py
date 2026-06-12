"""Mid-level extractors: parse formatted strings into structured values."""

from __future__ import annotations

import re
from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo

from courtside_data.data import Outcome, PeriodType
from courtside_data.legacy.parsers.mappers import OutcomeAbbreviationParser

PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT: str = "%Y-%m-%d"
PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX: str = "(?P<outcome_abbreviation>W|L),"
SEARCH_RESULT_NAME_REGEX: str = "(?P<name>^[^\\(]+)"


def _match_group(pattern: str, text: str, group_name: str, description: str) -> str:
    """Extract a named regex group from text, raising ValueError when unmatched."""
    match = re.search(pattern, text)
    if match is None:
        raise ValueError(f"Could not parse {description} from: {text}")
    return match.group(group_name)


class PlayerBoxScoreOutcomeParser:
    def __init__(
        self,
        outcome_abbreviation_parser: OutcomeAbbreviationParser,
        formatted_outcome_regex: str = PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX,
        outcome_abbreviation_regex_group_name: str = "outcome_abbreviation",
    ) -> None:
        self.outcome_abbreviation_parser = outcome_abbreviation_parser
        self.formatted_outcome_regex = formatted_outcome_regex
        self.outcome_abbreviation_regex_group_name = outcome_abbreviation_regex_group_name

    def parse_outcome_abbreviation(self, formatted_outcome: str) -> str:
        return _match_group(
            self.formatted_outcome_regex,
            formatted_outcome,
            self.outcome_abbreviation_regex_group_name,
            description="outcome",
        )

    def parse_outcome(self, formatted_outcome: str) -> Outcome:
        return self.outcome_abbreviation_parser.from_abbreviation(
            abbreviation=self.parse_outcome_abbreviation(formatted_outcome=formatted_outcome)
        )


class SecondsPlayedParser:
    def parse(self, formatted_playing_time: str) -> int:
        if formatted_playing_time == "":
            return 0

        # It seems like basketball reference formats everything in MM:SS
        # even when the playing time is greater than 59 minutes, 59 seconds.
        #
        # Because of this, we can't use strptime / %M as valid values are 0-59.
        # So have to parse time by splitting on ":" and assuming that
        # the first part is the minute part and the second part is the seconds part
        time_parts = formatted_playing_time.split(":")
        if len(time_parts) != 2:
            raise ValueError(f"Invalid playing time format: {formatted_playing_time}")
        minutes_played = time_parts[0]
        seconds_played = time_parts[1]
        return 60 * int(minutes_played) + int(seconds_played)


class PeriodDetailsParser:
    def __init__(self, regulation_periods_count: int) -> None:
        self.regulation_periods_count = regulation_periods_count

    def is_overtime(self, period_count: int) -> bool:
        return period_count > self.regulation_periods_count

    def parse_period_number(self, period_count: int) -> int:
        if self.is_overtime(period_count=period_count):
            return period_count - self.regulation_periods_count

        return period_count

    def parse_period_type(self, period_count: int) -> PeriodType:
        if self.is_overtime(period_count=period_count):
            return PeriodType.OVERTIME

        return PeriodType.QUARTER


class PeriodTimestampParser:
    def __init__(self, timestamp_format: str) -> None:
        self.timestamp_format = timestamp_format

    def to_seconds(self, timestamp: str) -> float:
        dt = datetime.strptime(timestamp, self.timestamp_format)
        return float((dt.minute * 60) + dt.second + (dt.microsecond / 1000000))


class ScoresParser:
    def __init__(
        self,
        scores_regex: str,
        away_team_score_group_name: str = "away_team_score",
        home_team_score_group_name: str = "home_team_score",
    ) -> None:
        self.scores_regex = scores_regex
        self.away_team_score_group_name = away_team_score_group_name
        self.home_team_score_group_name = home_team_score_group_name

    def parse_away_team_score(self, formatted_scores: str) -> int:
        return int(_match_group(self.scores_regex, formatted_scores, self.away_team_score_group_name, "scores"))

    def parse_home_team_score(self, formatted_scores: str) -> int:
        return int(_match_group(self.scores_regex, formatted_scores, self.home_team_score_group_name, "scores"))


class ScheduledStartTimeParser:
    def __init__(self, time_zone: tzinfo = UTC) -> None:
        self.time_zone = time_zone

    def parse_start_time(self, formatted_date: str, formatted_time_of_day: str | None) -> datetime:
        if formatted_time_of_day is None or formatted_time_of_day in ["", " "]:
            start_time = datetime.strptime(formatted_date, "%a, %b %d, %Y")
        else:
            # Starting in 2018, the start times had a "p" or "a" appended to the end
            # Between 2001 and 2017, the start times had a "pm" or "am"
            #
            # https://www.basketball-reference.com/leagues/NBA_2018_games.html
            # vs.
            # https://www.basketball-reference.com/leagues/NBA_2001_games.html
            is_prior_format = formatted_time_of_day[-2:] in ("am", "pm")
            if is_prior_format:
                combined_formatted_time = f"{formatted_date} {formatted_time_of_day}"
                start_time = datetime.strptime(combined_formatted_time, "%a, %b %d, %Y %I:%M %p")
            else:
                # Newer format has only "p" or "a"; add an "m" so strptime's %p can parse it
                combined_formatted_time = f"{formatted_date} {formatted_time_of_day}m"
                start_time = datetime.strptime(combined_formatted_time, "%a, %b %d, %Y %I:%M%p")

        # All basketball reference times seem to be in Eastern
        localized_start_time = start_time.replace(tzinfo=ZoneInfo("US/Eastern"))
        return localized_start_time.astimezone(self.time_zone)


class SearchResultNameParser:
    def __init__(
        self,
        search_result_name_regex: str = SEARCH_RESULT_NAME_REGEX,
        result_name_regex_group_name: str = "name",
    ) -> None:
        self.search_result_name_regex = search_result_name_regex
        self.result_name_regex_group_name = result_name_regex_group_name

    def parse(self, search_result_name: str) -> str:
        return _match_group(
            self.search_result_name_regex,
            search_result_name,
            self.result_name_regex_group_name,
            description="search result name",
        ).strip()


class ResourceLocationParser:
    def __init__(
        self,
        resource_location_regex: str,
        resource_type_regex_group_name: str = "resource_type",
        resource_identifier_regex_group_name: str = "resource_identifier",
    ) -> None:
        self.resource_location_regex = resource_location_regex
        self.resource_type_regex_group_name = resource_type_regex_group_name
        self.resource_identifier_regex_group_name = resource_identifier_regex_group_name

    def parse_resource_type(self, resource_location: str) -> str:
        return _match_group(
            self.resource_location_regex,
            resource_location,
            self.resource_type_regex_group_name,
            description="resource location",
        )

    def parse_resource_identifier(self, resource_location: str) -> str:
        return _match_group(
            self.resource_location_regex,
            resource_location,
            self.resource_identifier_regex_group_name,
            description="resource location",
        )
