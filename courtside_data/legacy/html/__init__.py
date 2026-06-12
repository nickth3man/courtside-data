"""Page-object models for the legacy Basketball Reference endpoints.

lxml-backed page/row classes grouped by domain (boxscores, totals,
play_by_play, schedule, search, standings, contracts). Generic endpoints do
not use these — they go through ``courtside_data.tables.GenericTable``.
Everything is re-exported here, so ``from courtside_data.legacy.html import
X`` keeps working regardless of which submodule defines ``X``.
"""

from courtside_data.legacy.html.boxscores import (
    BasicBoxScoreRow,
    BoxScoresPage,
    DailyBoxScoresPage,
    DailyLeadersPage,
    PlayerBoxScoreRow,
    PlayerGameBoxScoreRow,
    PlayerIdentificationRow,
    PlayerSeasonBoxScoresPage,
    PlayerSeasonBoxScoresRow,
    PlayerSeasonBoxScoresTable,
    PlayerSeasonGameLogRow,
    StatisticsTable,
)
from courtside_data.legacy.html.contracts import PlayerContractsRow
from courtside_data.legacy.html.play_by_play import (
    PlayByPlayPage,
    PlayByPlayRow,
    PlayByPlayTable,
)
from courtside_data.legacy.html.schedule import SchedulePage, ScheduleRow
from courtside_data.legacy.html.search import (
    PlayerPage,
    PlayerPageTotalsRow,
    PlayerPageTotalsTable,
    PlayerSearchResult,
    SearchPage,
    SearchResult,
)
from courtside_data.legacy.html.standings import (
    ConferenceDivisionStandingsRow,
    ConferenceDivisionStandingsTable,
    DivisionStandings,
    StandingsPage,
)
from courtside_data.legacy.html.totals import (
    PlayerAdvancedSeasonTotalsRow,
    PlayerAdvancedSeasonTotalsTable,
    PlayerSeasonTotalsRow,
    PlayerSeasonTotalTable,
)

__all__ = [
    "BasicBoxScoreRow",
    "BoxScoresPage",
    "ConferenceDivisionStandingsRow",
    "ConferenceDivisionStandingsTable",
    "DailyBoxScoresPage",
    "DailyLeadersPage",
    "DivisionStandings",
    "PlayByPlayPage",
    "PlayByPlayRow",
    "PlayByPlayTable",
    "PlayerAdvancedSeasonTotalsRow",
    "PlayerAdvancedSeasonTotalsTable",
    "PlayerBoxScoreRow",
    "PlayerContractsRow",
    "PlayerGameBoxScoreRow",
    "PlayerIdentificationRow",
    "PlayerPage",
    "PlayerPageTotalsRow",
    "PlayerPageTotalsTable",
    "PlayerSearchResult",
    "PlayerSeasonBoxScoresPage",
    "PlayerSeasonBoxScoresRow",
    "PlayerSeasonBoxScoresTable",
    "PlayerSeasonGameLogRow",
    "PlayerSeasonTotalTable",
    "PlayerSeasonTotalsRow",
    "SchedulePage",
    "ScheduleRow",
    "SearchPage",
    "SearchResult",
    "StandingsPage",
    "StatisticsTable",
]
