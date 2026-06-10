class InvalidDate(Exception):
    def __init__(self, day, month, year):
        message = "Date with year set to {year}, month set to {month}, and day set to {day} is invalid"\
            .format(
                year=year,
                month=month,
                day=day,
            )
        super().__init__(message)


class InvalidSeason(Exception):
    def __init__(self, season_end_year):
        message = "Season end year of {season_end_year} is invalid".format(season_end_year=season_end_year)
        super().__init__(message)


class InvalidPlayerAndSeason(Exception):
    def __init__(self, player_identifier, season_end_year):
        message = "Player with identifier \"{player_identifier}\" in season ending in {season_end_year} is invalid" \
            .format(player_identifier=player_identifier, season_end_year=season_end_year)
        super().__init__(message)


class InvalidSearch(Exception):
    def __init__(self, term):
        message = "Search term \"{term}\" returned no results".format(term=term)
        super().__init__(message)


class InvalidPlayer(Exception):
    def __init__(self, player_identifier):
        self.player_identifier = player_identifier
        message = "Invalid player: {player_identifier}".format(player_identifier=player_identifier)
        super().__init__(message)


class InvalidTeam(Exception):
    def __init__(self, team_abbreviation):
        self.team_abbreviation = team_abbreviation
        message = "Invalid team: {team_abbreviation}".format(team_abbreviation=team_abbreviation)
        super().__init__(message)
