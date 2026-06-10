"""Low-level mappers: translate Basketball Reference strings to domain enums."""

from __future__ import annotations

from courtside_data.data import Division, League, Location, Outcome, Position, Team


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
        parsed_positions = [self.from_abbreviation(abbreviation) for abbreviation in abbreviations.split("-")]
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


class TeamNameParser:
    def __init__(self, team_names_to_teams: dict[str, Team]) -> None:
        self.team_names_to_teams = team_names_to_teams

    def parse_team_name(self, team_name: str) -> Team:
        result = self.team_names_to_teams.get(team_name.strip().upper())
        if result is None:
            raise ValueError(f"Unknown team name: {team_name}")
        return result


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
