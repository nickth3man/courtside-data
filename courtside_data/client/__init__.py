"""Public client functions for every Basketball Reference endpoint.

Each function is an explicit, typed ``def`` (so static typing, IDE
auto-complete, and grep all work) whose body is a thin call into
:func:`courtside_data.client._runner._run_endpoint`. All endpoint *metadata*
— URL path, table location, CSV columns, and HTTP-status-to-domain-error
mapping — lives in the :data:`courtside_data.endpoints.ENDPOINTS` registry,
which is the single source of truth. A drift test asserts every function
signature matches its registry entry.

Functions are grouped into category modules mirroring the README's endpoint
table (``league``, ``playoffs``, ``draft``, ``players``, ``teams``,
``games``) and re-exported here, so both ``from courtside_data.client import
X`` and ``client.X`` keep working regardless of which module defines ``X``.

:class:`CourtsideClient` wraps the same functions as methods bound to a
dedicated HTTP session.
"""

from courtside_data.client.draft import (
    career_leaders,
    draft_picks,
    season_awards,
    season_leaders,
)
from courtside_data.client.games import (
    play_by_play,
    player_box_scores,
    players_advanced_season_totals,
    players_season_totals,
    playoff_player_box_scores,
    regular_season_player_box_scores,
    search,
    season_schedule,
    team_box_scores,
)
from courtside_data.client.league import (
    attendance,
    league_per_36_minutes,
    league_per_100_possessions,
    league_per_game_stats,
    league_shooting,
    league_totals,
    league_transactions,
    rookie_stats,
    standings,
    standings_by_date,
)
from courtside_data.client.players import (
    player_adjusted_shooting,
    player_all_star,
    player_career_stats,
    player_game_highs,
    player_on_off,
    player_play_by_play,
    player_playoff_series,
    player_salaries,
    player_shot_charts,
    player_similarity_scores,
    player_splits,
)
from courtside_data.client.playoffs import (
    playoff_bracket,
    playoff_per_game,
    playoff_totals,
)
from courtside_data.client.teams import (
    franchise_history,
    team_and_opponent,
    team_contracts,
    team_injury_report,
    team_lineups,
    team_misc_four_factors,
    team_on_off,
    team_opponent_stats,
    team_roster,
    team_schedule,
    team_splits,
    team_starting_lineups,
    team_transactions,
)

# Re-exported for the registry drift test and for callers that need direct
# service access.
from courtside_data.http_service import HTTPService  # noqa: F401

ENDPOINT_FUNCTION_NAMES: tuple[str, ...] = (
    "attendance",
    "career_leaders",
    "draft_picks",
    "franchise_history",
    "league_per_36_minutes",
    "league_per_100_possessions",
    "league_per_game_stats",
    "league_shooting",
    "league_totals",
    "league_transactions",
    "play_by_play",
    "player_adjusted_shooting",
    "player_all_star",
    "player_box_scores",
    "player_career_stats",
    "player_game_highs",
    "player_on_off",
    "player_play_by_play",
    "player_playoff_series",
    "player_salaries",
    "player_shot_charts",
    "player_similarity_scores",
    "player_splits",
    "players_advanced_season_totals",
    "players_season_totals",
    "playoff_bracket",
    "playoff_per_game",
    "playoff_player_box_scores",
    "playoff_totals",
    "regular_season_player_box_scores",
    "rookie_stats",
    "search",
    "season_awards",
    "season_leaders",
    "season_schedule",
    "standings",
    "standings_by_date",
    "team_and_opponent",
    "team_box_scores",
    "team_contracts",
    "team_injury_report",
    "team_lineups",
    "team_misc_four_factors",
    "team_on_off",
    "team_opponent_stats",
    "team_roster",
    "team_schedule",
    "team_splits",
    "team_starting_lineups",
    "team_transactions",
)

# Imported after the endpoint functions exist: CourtsideClient resolves its
# methods through this module at call time.
from courtside_data.client.courtside_client import CourtsideClient  # noqa: E402

# Kept literal (rather than unpacking ENDPOINT_FUNCTION_NAMES) so ruff
# recognizes the imports above as intentional re-exports.
__all__ = [
    "CourtsideClient",
    "HTTPService",
    "attendance",
    "career_leaders",
    "draft_picks",
    "franchise_history",
    "league_per_36_minutes",
    "league_per_100_possessions",
    "league_per_game_stats",
    "league_shooting",
    "league_totals",
    "league_transactions",
    "play_by_play",
    "player_adjusted_shooting",
    "player_all_star",
    "player_box_scores",
    "player_career_stats",
    "player_game_highs",
    "player_on_off",
    "player_play_by_play",
    "player_playoff_series",
    "player_salaries",
    "player_shot_charts",
    "player_similarity_scores",
    "player_splits",
    "players_advanced_season_totals",
    "players_season_totals",
    "playoff_bracket",
    "playoff_per_game",
    "playoff_player_box_scores",
    "playoff_totals",
    "regular_season_player_box_scores",
    "rookie_stats",
    "search",
    "season_awards",
    "season_leaders",
    "season_schedule",
    "standings",
    "standings_by_date",
    "team_and_opponent",
    "team_box_scores",
    "team_contracts",
    "team_injury_report",
    "team_lineups",
    "team_misc_four_factors",
    "team_on_off",
    "team_opponent_stats",
    "team_roster",
    "team_schedule",
    "team_splits",
    "team_starting_lineups",
    "team_transactions",
]
