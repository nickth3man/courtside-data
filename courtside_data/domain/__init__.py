"""Domain layer for courtside-data.

This package hosts the core domain types — enums, lookup tables, and the
legacy container classes — extracted from the historical
:mod:`courtside_data.data` module. The split is purely organizational for
Phase 1 of the refactor: the contents here are byte-equivalent to the
previous module surface, and :mod:`courtside_data.data` now exists only as
a thin backward-compatible shim that re-exports these names.
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
