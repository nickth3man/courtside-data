"""Legacy domain classes retained for backward compatibility.

These pre-Pydantic, attr-less container classes are exposed under
``courtside_data.data`` for historical callers. New code should prefer the
typed schemas in :mod:`courtside_data.schemas`.

Moved verbatim from :mod:`courtside_data.data` during the Phase 1 domain
extraction refactor.
"""


class TeamTotal:
    def __init__(self, team_abbreviation, totals):
        self.team_abbreviation = team_abbreviation
        self.totals = totals

    @property
    def minutes_played(self):
        return self.totals.minutes_played

    @property
    def made_field_goals(self):
        return self.totals.made_field_goals

    @property
    def attempted_field_goals(self):
        return self.totals.attempted_field_goals

    @property
    def made_three_point_field_goals(self):
        return self.totals.made_three_point_field_goals

    @property
    def attempted_three_point_field_goals(self):
        return self.totals.attempted_three_point_field_goals

    @property
    def made_free_throws(self):
        return self.totals.made_free_throws

    @property
    def attempted_free_throws(self):
        return self.totals.attempted_free_throws

    @property
    def offensive_rebounds(self):
        return self.totals.offensive_rebounds

    @property
    def defensive_rebounds(self):
        return self.totals.defensive_rebounds

    @property
    def assists(self):
        return self.totals.assists

    @property
    def steals(self):
        return self.totals.steals

    @property
    def blocks(self):
        return self.totals.blocks

    @property
    def turnovers(self):
        return self.totals.turnovers

    @property
    def personal_fouls(self):
        return self.totals.personal_fouls

    @property
    def points(self):
        return self.totals.points


class PlayerData:
    def __init__(self, name, resource_location, league_abbreviations):
        self.name = name
        self.resource_location = resource_location
        self.league_abbreviations = set(league_abbreviations)
