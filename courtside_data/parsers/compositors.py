"""Domain compositors: combine mappers and extractors into complete records."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from courtside_data.data import Conference, Division, Outcome, Team
from courtside_data.parsers.extractors import (
    PeriodDetailsParser,
    PeriodTimestampParser,
    PlayerBoxScoreOutcomeParser,
    ResourceLocationParser,
    ScheduledStartTimeParser,
    ScoresParser,
    SearchResultNameParser,
    SecondsPlayedParser,
)
from courtside_data.parsers.mappers import (
    DivisionNameParser,
    LeagueAbbreviationParser,
    LocationAbbreviationParser,
    OutcomeAbbreviationParser,
    PositionAbbreviationParser,
    TeamAbbreviationParser,
    TeamNameParser,
    TeamStandingsParser,
)
from courtside_data.utilities import str_to_float, str_to_int


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
