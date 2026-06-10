"""Page-object models for Basketball Reference HTML.

Legacy endpoints use lxml-backed page/row classes grouped by domain
(boxscores, totals, play_by_play, schedule, search, standings, contracts).
Generic (beta) endpoints use the parsel-backed ``GenericTable`` machinery in
``generic``. Everything is re-exported here, so ``from courtside_data.html
import X`` keeps working regardless of which submodule defines ``X``.
"""

from courtside_data.html.boxscores import (
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
from courtside_data.html.contracts import PlayerContractsRow
from courtside_data.html.generic import (
    GenericTable,
    GenericTableRow,
    extract_commented_table,
)
from courtside_data.html.play_by_play import (
    PlayByPlayPage,
    PlayByPlayRow,
    PlayByPlayTable,
)
from courtside_data.html.schedule import SchedulePage, ScheduleRow
from courtside_data.html.search import (
    PlayerPage,
    PlayerPageTotalsRow,
    PlayerPageTotalsTable,
    PlayerSearchResult,
    SearchPage,
    SearchResult,
)
from courtside_data.html.standings import (
    ConferenceDivisionStandingsRow,
    ConferenceDivisionStandingsTable,
    DivisionStandings,
    StandingsPage,
)
from courtside_data.html.totals import (
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
    "GenericTable",
    "GenericTableRow",
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
    "extract_commented_table",
]
