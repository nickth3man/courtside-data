"""Domain layer for courtside-data.

This package hosts the core domain types — enums, lookup tables, and the
canonical definitions used by endpoint parameters, parsed values, and
output formatting.
"""

from courtside_data.domain.enums import (
    Conference,
    Division,
    League,
    Location,
    Outcome,
    OutputType,
    OutputWriteOption,
    PeriodType,
    Position,
    Team,
)
from courtside_data.domain.lookups import (
    DIVISIONS_TO_CONFERENCES,
    LEAGUE_ABBREVIATIONS_TO_LEAGUE,
    LOCATION_ABBREVIATIONS_TO_LOCATION,
    OUTCOME_ABBREVIATIONS_TO_OUTCOME,
    POSITION_ABBREVIATIONS_TO_POSITION,
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
)

__all__ = [
    "DIVISIONS_TO_CONFERENCES",
    "LEAGUE_ABBREVIATIONS_TO_LEAGUE",
    "LOCATION_ABBREVIATIONS_TO_LOCATION",
    "OUTCOME_ABBREVIATIONS_TO_OUTCOME",
    "POSITION_ABBREVIATIONS_TO_POSITION",
    "TEAM_ABBREVIATIONS_TO_TEAM",
    "TEAM_NAME_TO_TEAM",
    "TEAM_TO_TEAM_ABBREVIATION",
    "Conference",
    "Division",
    "League",
    "Location",
    "Outcome",
    "OutputType",
    "OutputWriteOption",
    "PeriodType",
    "Position",
    "Team",
]
