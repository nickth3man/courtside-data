from __future__ import annotations

import re
from datetime import UTC, datetime, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

from courtside_data.data import Conference, Division, League, Location, Outcome, PeriodType, Position, Team
from courtside_data.utilities import str_to_float, str_to_int

PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT: str = "%Y-%m-%d"
PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX: str = "(?P<outcome_abbreviation>W|L),"
SEARCH_RESULT_NAME_REGEX: str = "(?P<name>^[^\\(]+)"


class TeamAbbreviationParser:
    def __init__(self, abbreviations_to_teams: dict[str, Team]) -> None:
        self.abbreviations_to_teams = abbreviations_to_teams

    def from_abbreviation(self, abbreviation: str) -> Team | None:
        return self.abbreviations_to_teams.get(abbreviation)


class PositionAbbreviationParser:
    def __init__(self, abbreviations_to_positions: dict[str, Position]) -> None:
        self.abbreviations_to_positions = abbreviations_to_positions

    def from_abbreviation(self, abbreviation: str) -> Position | None:
        return self.abbreviations_to_positions.get(abbreviation)

    def from_abbreviations(self, abbreviations: str) -> list[Position]:
        parsed_positions = list(
            map(lambda position_abbreviation: self.from_abbreviation(position_abbreviation), abbreviations.split("-"))
        )
        return [position for position in parsed_positions if position is not None]


class LocationAbbreviationParser:
    def __init__(self, abbreviations_to_locations: dict[str, Location]) -> None:
        self.abbreviations_to_locations = abbreviations_to_locations

    def from_abbreviation(self, abbreviation: str) -> Location:
        location = self.abbreviations_to_locations.get(abbreviation)
        if location is None:
            raise ValueError(f"Unknown symbol: {abbreviation}")

        return location


class OutcomeAbbreviationParser:
    def __init__(self, abbreviations_to_outcomes: dict[str, Outcome]) -> None:
        self.abbreviations_to_outcomes = abbreviations_to_outcomes

    def from_abbreviation(self, abbreviation: str) -> Outcome:
        outcome = self.abbreviations_to_outcomes.get(abbreviation)
        if outcome is None:
            raise ValueError(f"Unknown symbol: {abbreviation}")

        return outcome


class LeagueAbbreviationParser:
    def __init__(self, abbreviations_to_league: dict[str, League]) -> None:
        self.abbreviations_to_league = abbreviations_to_league

    def from_abbreviation(self, abbreviation: str) -> League:
        league = self.abbreviations_to_league.get(abbreviation)
        if league is None:
            raise ValueError(f"Unknown league abbreviation: {abbreviation}")

        return league

    def from_abbreviations(self, abbreviations: str | None) -> list[League]:
        if abbreviations is None:
            return []

        return [
            self.from_abbreviation(abbreviation=league_abbreviation) for league_abbreviation in abbreviations.split("/")
        ]


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

    def search_formatted_outcome(self, formatted_outcome: str) -> re.Match[str] | None:
        return re.search(self.formatted_outcome_regex, formatted_outcome)

    def parse_outcome_abbreviation(self, formatted_outcome: str) -> str:
        match = self.search_formatted_outcome(formatted_outcome=formatted_outcome)
        if match is None:
            raise ValueError(f"Could not parse outcome from: {formatted_outcome}")
        return match.group(self.outcome_abbreviation_regex_group_name)

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

    def parse_scores(self, formatted_scores: str) -> re.Match[str] | None:
        return re.search(self.scores_regex, formatted_scores)

    def parse_away_team_score(self, formatted_scores: str) -> int:
        match = self.parse_scores(formatted_scores=formatted_scores)
        if match is None:
            raise ValueError(f"Could not parse scores from: {formatted_scores}")
        return int(match.group(self.away_team_score_group_name))

    def parse_home_team_score(self, formatted_scores: str) -> int:
        match = self.parse_scores(formatted_scores=formatted_scores)
        if match is None:
            raise ValueError(f"Could not parse scores from: {formatted_scores}")
        return int(match.group(self.home_team_score_group_name))


class TeamNameParser:
    def __init__(self, team_names_to_teams: dict[str, Team]) -> None:
        self.team_names_to_teams = team_names_to_teams

    def parse_team_name(self, team_name: str) -> Team:
        result = self.team_names_to_teams.get(team_name.strip().upper())
        if result is None:
            raise ValueError(f"Unknown team name: {team_name}")
        return result


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
        match = re.search(self.search_result_name_regex, search_result_name)
        if match is None:
            raise ValueError(f"Could not parse search result name from: {search_result_name}")
        return match.group(self.result_name_regex_group_name).strip()


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

    def search(self, resource_location: str) -> re.Match[str] | None:
        return re.search(self.resource_location_regex, resource_location)

    def parse_resource_type(self, resource_location: str) -> str:
        match = self.search(resource_location=resource_location)
        if match is None:
            raise ValueError(f"Could not parse resource location from: {resource_location}")
        return match.group(self.resource_type_regex_group_name)

    def parse_resource_identifier(self, resource_location: str) -> str:
        match = self.search(resource_location=resource_location)
        if match is None:
            raise ValueError(f"Could not parse resource location from: {resource_location}")
        return match.group(self.resource_identifier_regex_group_name)


class TeamStandingsParser:
    def __init__(self, teams: type[Team]) -> None:
        self.teams = teams

    def parse_team(self, formatted_name: str) -> Team | None:
        for team in self.teams:
            if formatted_name.upper().startswith(team.value):
                return team

        return None


class DivisionNameParser:
    def __init__(self, divisions: type[Division]) -> None:
        self.divisions = divisions

    def parse_division(self, formatted_name: str) -> Division | None:
        for division in self.divisions:
            if formatted_name.upper() == f"{division.value} DIVISION":
                return division

        return None


class ScheduledGamesParser:
    def __init__(self, start_time_parser: ScheduledStartTimeParser, team_name_parser: TeamNameParser) -> None:
        self.start_time_parser = start_time_parser
        self.team_name_parser = team_name_parser

    def parse_games(self, games: list[Any]) -> list[dict[str, Any]]:
        return [
            {
                "start_time": self.start_time_parser.parse_start_time(
                    formatted_date=game.start_date,
                    formatted_time_of_day=game.start_time_of_day,
                ),
                "away_team": self.team_name_parser.parse_team_name(team_name=game.away_team_name),
                "home_team": self.team_name_parser.parse_team_name(team_name=game.home_team_name),
                "away_team_score": str_to_int(value=game.away_team_score, default=None),
                "home_team_score": str_to_int(value=game.home_team_score, default=None),
            }
            for game in games
        ]


class PlayerAdvancedSeasonTotalsParser:
    def __init__(
        self,
        position_abbreviation_parser: PositionAbbreviationParser,
        team_abbreviation_parser: TeamAbbreviationParser,
    ) -> None:
        self.position_abbreviation_parser = position_abbreviation_parser
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, totals: list[Any]) -> list[dict[str, Any]]:
        return [
            {
                "slug": str(total.slug),
                "name": str(total.name).rstrip("*"),
                "positions": self.position_abbreviation_parser.from_abbreviations(total.position_abbreviations),
                "age": str_to_int(total.age, default=None),
                "team": self.team_abbreviation_parser.from_abbreviation(total.team_abbreviation),
                "games_played": str_to_int(total.games_played),
                "minutes_played": str_to_int(total.minutes_played),
                "player_efficiency_rating": str_to_float(total.player_efficiency_rating),
                "true_shooting_percentage": str_to_float(total.true_shooting_percentage),
                "three_point_attempt_rate": str_to_float(total.three_point_attempt_rate),
                "free_throw_attempt_rate": str_to_float(total.free_throw_attempt_rate),
                "offensive_rebound_percentage": str_to_float(total.offensive_rebound_percentage),
                "defensive_rebound_percentage": str_to_float(total.defensive_rebound_percentage),
                "total_rebound_percentage": str_to_float(total.total_rebound_percentage),
                "assist_percentage": str_to_float(total.assist_percentage),
                "steal_percentage": str_to_float(total.steal_percentage),
                "block_percentage": str_to_float(total.block_percentage),
                "turnover_percentage": str_to_float(total.turnover_percentage),
                "usage_percentage": str_to_float(total.usage_percentage),
                "offensive_win_shares": str_to_float(total.offensive_win_shares),
                "defensive_win_shares": str_to_float(total.defensive_win_shares),
                "win_shares": str_to_float(total.win_shares),
                "win_shares_per_48_minutes": str_to_float(total.win_shares_per_48_minutes),
                "offensive_box_plus_minus": str_to_float(total.offensive_plus_minus),
                "defensive_box_plus_minus": str_to_float(total.defensive_plus_minus),
                "box_plus_minus": str_to_float(total.plus_minus),
                "value_over_replacement_player": str_to_float(total.value_over_replacement_player),
                "is_combined_totals": total.is_combined_totals,
            }
            for total in totals
        ]


class PlayerSeasonTotalsParser:
    def __init__(
        self,
        position_abbreviation_parser: PositionAbbreviationParser,
        team_abbreviation_parser: TeamAbbreviationParser,
    ) -> None:
        self.position_abbreviation_parser = position_abbreviation_parser
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, totals: list[Any]) -> list[dict[str, Any]]:
        return [
            {
                "slug": str(total.slug),
                "name": str(total.name).rstrip("*"),
                "positions": self.position_abbreviation_parser.from_abbreviations(total.position_abbreviations),
                "age": str_to_int(total.age, default=None),
                "team": self.team_abbreviation_parser.from_abbreviation(total.team_abbreviation),
                "games_played": str_to_int(total.games_played),
                "games_started": str_to_int(total.games_started),
                "minutes_played": str_to_int(total.minutes_played),
                "made_field_goals": str_to_int(total.made_field_goals),
                "attempted_field_goals": str_to_int(total.attempted_field_goals),
                "made_three_point_field_goals": str_to_int(total.made_three_point_field_goals),
                "attempted_three_point_field_goals": str_to_int(total.attempted_three_point_field_goals),
                "made_free_throws": str_to_int(total.made_free_throws),
                "attempted_free_throws": str_to_int(total.attempted_free_throws),
                "offensive_rebounds": str_to_int(total.offensive_rebounds),
                "defensive_rebounds": str_to_int(total.defensive_rebounds),
                "assists": str_to_int(total.assists),
                "steals": str_to_int(total.steals),
                "blocks": str_to_int(total.blocks),
                "turnovers": str_to_int(total.turnovers),
                "personal_fouls": str_to_int(total.personal_fouls),
                "points": str_to_int(total.points),
            }
            for total in totals
        ]


class TeamTotalsParser:
    def __init__(self, team_abbreviation_parser: TeamAbbreviationParser) -> None:
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, first_team_totals: Any, second_team_totals: Any) -> list[dict[str, Any]]:
        return [
            self.parse_totals(
                team_totals=first_team_totals,
                opposing_team_totals=second_team_totals,
            ),
            self.parse_totals(
                team_totals=second_team_totals,
                opposing_team_totals=first_team_totals,
            ),
        ]

    def parse_totals(self, team_totals: Any, opposing_team_totals: Any) -> dict[str, Any]:
        current_team = self.team_abbreviation_parser.from_abbreviation(team_totals.team_abbreviation)

        if str_to_int(team_totals.points) > str_to_int(opposing_team_totals.points):
            outcome = Outcome.WIN
        elif str_to_int(team_totals.points) < str_to_int(opposing_team_totals.points):
            outcome = Outcome.LOSS
        else:
            outcome = None

        return {
            "team": current_team,
            "outcome": outcome,
            "minutes_played": str_to_int(team_totals.minutes_played),
            "made_field_goals": str_to_int(team_totals.made_field_goals),
            "attempted_field_goals": str_to_int(team_totals.attempted_field_goals),
            "made_three_point_field_goals": str_to_int(team_totals.made_three_point_field_goals),
            "attempted_three_point_field_goals": str_to_int(team_totals.attempted_three_point_field_goals),
            "made_free_throws": str_to_int(team_totals.made_free_throws),
            "attempted_free_throws": str_to_int(team_totals.attempted_free_throws),
            "offensive_rebounds": str_to_int(team_totals.offensive_rebounds),
            "defensive_rebounds": str_to_int(team_totals.defensive_rebounds),
            "assists": str_to_int(team_totals.assists),
            "steals": str_to_int(team_totals.steals),
            "blocks": str_to_int(team_totals.blocks),
            "turnovers": str_to_int(team_totals.turnovers),
            "personal_fouls": str_to_int(team_totals.personal_fouls),
            "points": str_to_int(team_totals.points),
        }


class PlayerBoxScoresParser:
    def __init__(
        self,
        team_abbreviation_parser: TeamAbbreviationParser,
        location_abbreviation_parser: LocationAbbreviationParser,
        outcome_abbreviation_parser: OutcomeAbbreviationParser,
        seconds_played_parser: SecondsPlayedParser,
    ) -> None:
        self.team_abbreviation_parser = team_abbreviation_parser
        self.location_abbreviation_parser = location_abbreviation_parser
        self.outcome_abbreviation_parser = outcome_abbreviation_parser
        self.seconds_played_parser = seconds_played_parser

    def parse(self, box_scores: list[Any]) -> list[dict[str, Any]]:
        return [
            {
                "slug": str(box_score.slug),
                "name": str(box_score.name).rstrip("*"),
                "team": self.team_abbreviation_parser.from_abbreviation(box_score.team_abbreviation),
                "location": self.location_abbreviation_parser.from_abbreviation(
                    box_score.location_abbreviation.strip()
                ),
                "opponent": self.team_abbreviation_parser.from_abbreviation(box_score.opponent_abbreviation),
                "outcome": self.outcome_abbreviation_parser.from_abbreviation(box_score.outcome),
                "seconds_played": self.seconds_played_parser.parse(box_score.playing_time),
                "made_field_goals": str_to_int(box_score.made_field_goals),
                "attempted_field_goals": str_to_int(box_score.attempted_field_goals),
                "made_three_point_field_goals": str_to_int(box_score.made_three_point_field_goals),
                "attempted_three_point_field_goals": str_to_int(box_score.attempted_three_point_field_goals),
                "made_free_throws": str_to_int(box_score.made_free_throws),
                "attempted_free_throws": str_to_int(box_score.attempted_free_throws),
                "offensive_rebounds": str_to_int(box_score.offensive_rebounds),
                "defensive_rebounds": str_to_int(box_score.defensive_rebounds),
                "assists": str_to_int(box_score.assists),
                "steals": str_to_int(box_score.steals),
                "blocks": str_to_int(box_score.blocks),
                "turnovers": str_to_int(box_score.turnovers),
                "personal_fouls": str_to_int(box_score.personal_fouls),
                "plus_minus": str_to_float(box_score.plus_minus),
                "game_score": str_to_float(box_score.game_score),
            }
            for box_score in box_scores
        ]


class PlayerSeasonBoxScoresParser:
    def __init__(
        self,
        team_abbreviation_parser: TeamAbbreviationParser,
        location_abbreviation_parser: LocationAbbreviationParser,
        outcome_parser: PlayerBoxScoreOutcomeParser,
        seconds_played_parser: SecondsPlayedParser,
    ) -> None:
        self.team_abbreviation_parser = team_abbreviation_parser
        self.location_abbreviation_parser = location_abbreviation_parser
        self.outcome_parser = outcome_parser
        self.seconds_played_parser = seconds_played_parser

    def parse(self, box_scores: list[Any], include_inactive_games: bool = False) -> list[dict[str, Any]]:
        active_fields = {
            "seconds_played": lambda bs: self.seconds_played_parser.parse(bs.playing_time),
            "made_field_goals": lambda bs: str_to_int(bs.made_field_goals),
            "attempted_field_goals": lambda bs: str_to_int(bs.attempted_field_goals),
            "made_three_point_field_goals": lambda bs: str_to_int(bs.made_three_point_field_goals),
            "attempted_three_point_field_goals": lambda bs: str_to_int(bs.attempted_three_point_field_goals),
            "made_free_throws": lambda bs: str_to_int(bs.made_free_throws),
            "attempted_free_throws": lambda bs: str_to_int(bs.attempted_free_throws),
            "offensive_rebounds": lambda bs: str_to_int(bs.offensive_rebounds),
            "defensive_rebounds": lambda bs: str_to_int(bs.defensive_rebounds),
            "assists": lambda bs: str_to_int(bs.assists),
            "steals": lambda bs: str_to_int(bs.steals),
            "blocks": lambda bs: str_to_int(bs.blocks),
            "turnovers": lambda bs: str_to_int(bs.turnovers),
            "personal_fouls": lambda bs: str_to_int(bs.personal_fouls),
            "points_scored": lambda bs: str_to_int(bs.points_scored),
            "game_score": lambda bs: str_to_float(bs.game_score),
            "plus_minus": lambda bs: str_to_int(bs.plus_minus),
        }
        results = []
        for box_score in box_scores:
            common = {
                "date": datetime.strptime(str(box_score.date), "%Y-%m-%d").date(),
                "team": self.team_abbreviation_parser.from_abbreviation(box_score.team_abbreviation),
                "location": self.location_abbreviation_parser.from_abbreviation(
                    box_score.location_abbreviation.strip()
                ),
                "opponent": self.team_abbreviation_parser.from_abbreviation(box_score.opponent_abbreviation),
                "outcome": self.outcome_parser.parse_outcome(formatted_outcome=box_score.outcome),
            }
            if box_score.is_active:
                results.append(
                    {
                        **common,
                        "active": True,
                        **{key: extractor(box_score) for key, extractor in active_fields.items()},
                    }
                )
            elif include_inactive_games:
                results.append(
                    {
                        **common,
                        "active": False,
                        **{key: None for key in active_fields},
                    }
                )

        return results


class PlayByPlaysParser:
    def __init__(
        self,
        period_details_parser: PeriodDetailsParser,
        period_timestamp_parser: PeriodTimestampParser,
        scores_parser: ScoresParser,
    ) -> None:
        self.period_details_parser = period_details_parser
        self.period_timestamp_parser = period_timestamp_parser
        self.scores_parser = scores_parser

    def parse(self, play_by_plays: list[Any], away_team: Team, home_team: Team) -> list[dict[str, Any]]:
        current_period = 0
        result = []
        for play_by_play in play_by_plays:
            if play_by_play.is_start_of_period:
                current_period += 1
            elif play_by_play.has_play_by_play_data:
                result.append(
                    self.format_data(
                        current_period=current_period,
                        play_by_play=play_by_play,
                        away_team=away_team,
                        home_team=home_team,
                    )
                )
        return result

    def format_data(self, current_period: int, play_by_play: Any, away_team: Team, home_team: Team) -> dict[str, Any]:
        return {
            "period": self.period_details_parser.parse_period_number(period_count=current_period),
            "period_type": self.period_details_parser.parse_period_type(period_count=current_period),
            "remaining_seconds_in_period": self.period_timestamp_parser.to_seconds(timestamp=play_by_play.timestamp),
            "relevant_team": away_team if play_by_play.is_away_team_play else home_team,
            "away_team": away_team,
            "home_team": home_team,
            "away_score": self.scores_parser.parse_away_team_score(formatted_scores=play_by_play.formatted_scores),
            "home_score": self.scores_parser.parse_home_team_score(formatted_scores=play_by_play.formatted_scores),
            "description": play_by_play.away_team_play_description
            if play_by_play.is_away_team_play
            else play_by_play.home_team_play_description,
        }


class SearchResultsParser:
    def __init__(
        self,
        search_result_name_parser: SearchResultNameParser,
        search_result_location_parser: ResourceLocationParser,
        league_abbreviation_parser: LeagueAbbreviationParser,
    ) -> None:
        self.search_result_name_parser = search_result_name_parser
        self.search_result_location_parser = search_result_location_parser
        self.league_abbreviation_parser = league_abbreviation_parser

    def parse(self, nba_aba_baa_players: list[Any]) -> dict[str, list[dict[str, Any]]]:
        return {
            "players": [
                {
                    "name": self.search_result_name_parser.parse(search_result_name=result.resource_name),
                    "identifier": self.search_result_location_parser.parse_resource_identifier(
                        resource_location=result.resource_location
                    ),
                    "leagues": set(
                        self.league_abbreviation_parser.from_abbreviations(abbreviations=result.league_abbreviations)
                    ),
                }
                for result in nba_aba_baa_players
            ]
        }


class PlayerDataParser:
    def __init__(
        self,
        search_result_location_parser: ResourceLocationParser,
        league_abbreviation_parser: LeagueAbbreviationParser,
    ) -> None:
        self.search_result_location_parser = search_result_location_parser
        self.league_abbreviation_parser = league_abbreviation_parser

    def parse(self, player: Any) -> dict[str, Any]:
        return {
            "name": player.name,
            "identifier": self.search_result_location_parser.parse_resource_identifier(
                resource_location=player.resource_location
            ),
            "leagues": set(
                self.league_abbreviation_parser.from_abbreviation(abbreviation=abbreviation)
                for abbreviation in player.league_abbreviations
            ),
        }


class ConferenceDivisionStandingsParser:
    def __init__(
        self,
        division_name_parser: DivisionNameParser,
        team_standings_parser: TeamStandingsParser,
        divisions_to_conferences: dict[Division, Conference],
    ) -> None:
        self.division_name_parser = division_name_parser
        self.team_standings_parser = team_standings_parser
        self.divisions_to_conferences = divisions_to_conferences

    def parse(self, division_standings: list[Any]) -> list[dict[str, Any]]:
        current_division = None
        results = []
        for standing in division_standings:
            if standing.is_division_name_row:
                current_division = self.division_name_parser.parse_division(formatted_name=standing.division_name)
            else:
                results.append(
                    {
                        "team": self.team_standings_parser.parse_team(formatted_name=standing.team_name),
                        "wins": str_to_int(standing.wins),
                        "losses": str_to_int(standing.losses),
                        "division": current_division,
                        "conference": (
                            self.divisions_to_conferences.get(current_division)
                            if current_division is not None
                            else None
                        ),
                    }
                )
        return results
