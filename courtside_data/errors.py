class InvalidDate(Exception):
    def __init__(self, day, month, year):
        message = f"Date with year set to {year}, month set to {month}, and day set to {day} is invalid"
        super().__init__(message)


class InvalidSeason(Exception):
    def __init__(self, season_end_year):
        message = f"Season end year of {season_end_year} is invalid"
        super().__init__(message)


class InvalidPlayerAndSeason(Exception):
    def __init__(self, player_identifier, season_end_year):
        message = f'Player with identifier "{player_identifier}" in season ending in {season_end_year} is invalid'
        super().__init__(message)


class InvalidSearch(Exception):
    def __init__(self, term):
        message = f'Search term "{term}" returned no results'
        super().__init__(message)


class InvalidPlayer(Exception):
    def __init__(self, player_identifier):
        self.player_identifier = player_identifier
        message = f"Invalid player: {player_identifier}"
        super().__init__(message)


class InvalidTeam(Exception):
    def __init__(self, team_abbreviation):
        self.team_abbreviation = team_abbreviation
        message = f"Invalid team: {team_abbreviation}"
        super().__init__(message)
