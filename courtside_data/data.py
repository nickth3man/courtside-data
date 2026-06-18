"""Backward-compatibility shim for :mod:`courtside_data.data`.

Historically this module hosted the project's core domain types — enums
(``Team``, ``Location``, …), abbreviation lookup tables, and a pair of
legacy container classes (``TeamTotal``, ``PlayerData``). Those definitions
now live in :mod:`courtside_data.domain`; this module exists solely to
preserve the existing ``from courtside_data.data import X`` public surface
for downstream callers.

New code should import from :mod:`courtside_data.domain` directly.
"""

from courtside_data.domain import (
    DIVISIONS_TO_CONFERENCES,
    LEAGUE_ABBREVIATIONS_TO_LEAGUE,
    LOCATION_ABBREVIATIONS_TO_LOCATION,
    LOCATION_ABBREVIATIONS_TO_POSITION,
    OUTCOME_ABBREVIATIONS_TO_OUTCOME,
    POSITION_ABBREVIATIONS_TO_POSITION,
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
    Conference,
    Division,
    League,
    Location,
    Outcome,
    OutputType,
    OutputWriteOption,
    PeriodType,
    PlayerData,
    Position,
    Team,
    TeamTotal,
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
