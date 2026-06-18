"""CSV column contracts for Basketball-Reference endpoints.

This package is intentionally small at the top level. Domain modules
contribute one ``*_COLUMN_NAMES`` list per endpoint; consumers import the
specific contract list they need from here.

The explicit per-endpoint lists exist because there is no way to derive
CSV column names from the legacy typed values directly — enums, lists, and
other non-string types do not round-trip through ``csv.DictWriter`` without
the writer knowing which columns to emit.

Importing the domain submodules here is what populates the module
namespace. The domain modules themselves hold no side effects beyond
defining the lists; no registries or adapters are wired up by import.
"""

# Domain modules — each defines one or more ``*_COLUMN_NAMES`` lists.
from courtside_data.output.columns import (
    _common,
    _misc,
    boxscores,
    draft,
    league,
    players,
    playoffs,
    standings,
    teams,
)

# Shared primitive consumed by ``boxscores.BOX_SCORE_COLUMN_NAMES`` and
# ``boxscores.PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES``.
from courtside_data.output.columns._common import SHARED_COLUMN_NAMES

# Per-endpoint contracts — re-exported at the package root so existing
# ``from courtside_data.output.columns import X`` imports keep working.
from courtside_data.output.columns._misc import (
    PLAY_BY_PLAY_COLUMN_NAMES,
    SCHEDULE_COLUMN_NAMES,
    SEARCH_RESULTS_COLUMN_NAMES,
)
from courtside_data.output.columns.boxscores import (
    BOX_SCORE_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
)
from courtside_data.output.columns.draft import DRAFT_PICKS_COLUMN_NAMES
from courtside_data.output.columns.league import (
    ATTENDANCE_COLUMN_NAMES,
    CAREER_LEADERS_COLUMN_NAMES,
    LEAGUE_PER_36_COLUMN_NAMES,
    LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES,
    LEAGUE_PER_GAME_COLUMN_NAMES,
    LEAGUE_PLAY_BY_PLAY_COLUMN_NAMES,
    LEAGUE_SHOOTING_COLUMN_NAMES,
    LEAGUE_TOTALS_COLUMN_NAMES,
    LEAGUE_TRANSACTIONS_COLUMN_NAMES,
    ROOKIE_STATS_COLUMN_NAMES,
    SEASON_AWARDS_COLUMN_NAMES,
    SEASON_AWARDS_VOTING_COLUMN_NAMES,
    SEASON_LEADERS_COLUMN_NAMES,
)
from courtside_data.output.columns.players import (
    PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES,
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_ALL_STAR_COLUMN_NAMES,
    PLAYER_CAREER_STATS_COLUMN_NAMES,
    PLAYER_GAME_HIGHS_COLUMN_NAMES,
    PLAYER_ON_OFF_COLUMN_NAMES,
    PLAYER_PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_PLAYOFF_SERIES_COLUMN_NAMES,
    PLAYER_SALARIES_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SHOT_CHARTS_COLUMN_NAMES,
    PLAYER_SIMILARITY_SCORES_COLUMN_NAMES,
    PLAYER_SPLITS_COLUMN_NAMES,
)
from courtside_data.output.columns.playoffs import (
    FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES,
    PLAYOFF_BRACKET_COLUMN_NAMES,
    PLAYOFF_PER_GAME_COLUMN_NAMES,
    PLAYOFF_TOTALS_COLUMN_NAMES,
)
from courtside_data.output.columns.standings import (
    STANDINGS_BY_DATE_COLUMN_NAMES,
    STANDINGS_COLUMNS_NAMES,
)
from courtside_data.output.columns.teams import (
    FRANCHISE_HISTORY_COLUMN_NAMES,
    TEAM_AND_OPPONENT_COLUMN_NAMES,
    TEAM_CONTRACTS_COLUMN_NAMES,
    TEAM_INJURY_REPORT_COLUMN_NAMES,
    TEAM_LINEUPS_COLUMN_NAMES,
    TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES,
    TEAM_ON_OFF_COLUMN_NAMES,
    TEAM_OPPONENT_STATS_COLUMN_NAMES,
    TEAM_ROSTER_COLUMN_NAMES,
    TEAM_SCHEDULE_COLUMN_NAMES,
    TEAM_SPLITS_COLUMN_NAMES,
    TEAM_STARTING_LINEUPS_COLUMN_NAMES,
    TEAM_TRANSACTIONS_COLUMN_NAMES,
)

__all__ = [
    "ATTENDANCE_COLUMN_NAMES",
    "BOX_SCORE_COLUMN_NAMES",
    "CAREER_LEADERS_COLUMN_NAMES",
    "DRAFT_PICKS_COLUMN_NAMES",
    "FRANCHISE_HISTORY_COLUMN_NAMES",
    "FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES",
    "LEAGUE_PER_36_COLUMN_NAMES",
    "LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES",
    "LEAGUE_PER_GAME_COLUMN_NAMES",
    "LEAGUE_PLAY_BY_PLAY_COLUMN_NAMES",
    "LEAGUE_SHOOTING_COLUMN_NAMES",
    "LEAGUE_TOTALS_COLUMN_NAMES",
    "LEAGUE_TRANSACTIONS_COLUMN_NAMES",
    "PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES",
    "PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES",
    "PLAYER_ALL_STAR_COLUMN_NAMES",
    "PLAYER_CAREER_STATS_COLUMN_NAMES",
    "PLAYER_GAME_HIGHS_COLUMN_NAMES",
    "PLAYER_ON_OFF_COLUMN_NAMES",
    "PLAYER_PLAYOFF_SERIES_COLUMN_NAMES",
    "PLAYER_PLAY_BY_PLAY_COLUMN_NAMES",
    "PLAYER_SALARIES_COLUMN_NAMES",
    "PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES",
    "PLAYER_SEASON_TOTALS_COLUMN_NAMES",
    "PLAYER_SHOT_CHARTS_COLUMN_NAMES",
    "PLAYER_SIMILARITY_SCORES_COLUMN_NAMES",
    "PLAYER_SPLITS_COLUMN_NAMES",
    "PLAYOFF_BRACKET_COLUMN_NAMES",
    "PLAYOFF_PER_GAME_COLUMN_NAMES",
    "PLAYOFF_TOTALS_COLUMN_NAMES",
    "PLAY_BY_PLAY_COLUMN_NAMES",
    "ROOKIE_STATS_COLUMN_NAMES",
    "SCHEDULE_COLUMN_NAMES",
    "SEARCH_RESULTS_COLUMN_NAMES",
    "SEASON_AWARDS_COLUMN_NAMES",
    "SEASON_AWARDS_VOTING_COLUMN_NAMES",
    "SEASON_LEADERS_COLUMN_NAMES",
    "SHARED_COLUMN_NAMES",
    "STANDINGS_BY_DATE_COLUMN_NAMES",
    "STANDINGS_COLUMNS_NAMES",
    "TEAM_AND_OPPONENT_COLUMN_NAMES",
    "TEAM_BOX_SCORES_COLUMN_NAMES",
    "TEAM_CONTRACTS_COLUMN_NAMES",
    "TEAM_INJURY_REPORT_COLUMN_NAMES",
    "TEAM_LINEUPS_COLUMN_NAMES",
    "TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES",
    "TEAM_ON_OFF_COLUMN_NAMES",
    "TEAM_OPPONENT_STATS_COLUMN_NAMES",
    "TEAM_ROSTER_COLUMN_NAMES",
    "TEAM_SCHEDULE_COLUMN_NAMES",
    "TEAM_SPLITS_COLUMN_NAMES",
    "TEAM_STARTING_LINEUPS_COLUMN_NAMES",
    "TEAM_TRANSACTIONS_COLUMN_NAMES",
    "_common",
    "_misc",
    "boxscores",
    "draft",
    "league",
    "players",
    "playoffs",
    "standings",
    "teams",
]
