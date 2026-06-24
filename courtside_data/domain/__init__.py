"""Domain layer for courtside-data.

This package hosts the core domain types — enums, lookup tables, and the
container classes (:class:`TeamTotal`, :class:`PlayerData`). The contents
are the canonical definitions; :mod:`courtside_data.data` is a thin
re-export module that preserves the older ``courtside_data.data`` import
path for these names.
"""

from courtside_data.domain._legacy import PlayerData, TeamTotal
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
    LOCATION_ABBREVIATIONS_TO_POSITION,
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
    "LOCATION_ABBREVIATIONS_TO_POSITION",
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
    "PlayerData",
    "Position",
    "Team",
    "TeamTotal",
]
