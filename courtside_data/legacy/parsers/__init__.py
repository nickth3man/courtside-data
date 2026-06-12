"""Parser classes for Basketball Reference data, organized in three tiers.

- :mod:`courtside_data.legacy.parsers.mappers` — low-level mappers translating
  abbreviations and names to domain enums.
- :mod:`courtside_data.legacy.parsers.extractors` — mid-level extractors parsing
  formatted strings into structured values.
- :mod:`courtside_data.legacy.parsers.compositors` — domain compositors combining
  mappers and extractors into complete records.

All names are re-exported here, so ``from courtside_data.legacy.parsers import X``
keeps working regardless of which module defines ``X``.
"""

from courtside_data.legacy.parsers.compositors import (
    ConferenceDivisionStandingsParser,
    PlayByPlaysParser,
    PlayerAdvancedSeasonTotalsParser,
    PlayerBoxScoresParser,
    PlayerDataParser,
    PlayerSeasonBoxScoresParser,
    PlayerSeasonTotalsParser,
    ScheduledGamesParser,
    SearchResultsParser,
    TeamTotalsParser,
)
from courtside_data.legacy.parsers.extractors import (
    PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT,
    PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX,
    SEARCH_RESULT_NAME_REGEX,
    PeriodDetailsParser,
    PeriodTimestampParser,
    PlayerBoxScoreOutcomeParser,
    ResourceLocationParser,
    ScheduledStartTimeParser,
    ScoresParser,
    SearchResultNameParser,
    SecondsPlayedParser,
)
from courtside_data.legacy.parsers.mappers import (
    DivisionNameParser,
    LeagueAbbreviationParser,
    LocationAbbreviationParser,
    OutcomeAbbreviationParser,
    PositionAbbreviationParser,
    TeamAbbreviationParser,
    TeamNameParser,
    TeamStandingsParser,
)

__all__ = [
    "PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT",
    "PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX",
    "SEARCH_RESULT_NAME_REGEX",
    "ConferenceDivisionStandingsParser",
    "DivisionNameParser",
    "LeagueAbbreviationParser",
    "LocationAbbreviationParser",
    "OutcomeAbbreviationParser",
    "PeriodDetailsParser",
    "PeriodTimestampParser",
    "PlayByPlaysParser",
    "PlayerAdvancedSeasonTotalsParser",
    "PlayerBoxScoreOutcomeParser",
    "PlayerBoxScoresParser",
    "PlayerDataParser",
    "PlayerSeasonBoxScoresParser",
    "PlayerSeasonTotalsParser",
    "PositionAbbreviationParser",
    "ResourceLocationParser",
    "ScheduledGamesParser",
    "ScheduledStartTimeParser",
    "ScoresParser",
    "SearchResultNameParser",
    "SearchResultsParser",
    "SecondsPlayedParser",
    "TeamAbbreviationParser",
    "TeamNameParser",
    "TeamStandingsParser",
    "TeamTotalsParser",
]
