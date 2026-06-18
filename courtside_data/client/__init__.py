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

from __future__ import annotations

from courtside_data.client.draft import (  # noqa: F401
    career_leaders,
    draft_picks,
    season_awards,
    season_awards_voting,
    season_leaders,
)
from courtside_data.client.games import (  # noqa: F401
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
from courtside_data.client.league import (  # noqa: F401
    attendance,
    league_per_36_minutes,
    league_per_100_possessions,
    league_per_game_stats,
    league_play_by_play,
    league_shooting,
    league_totals,
    league_transactions,
    rookie_stats,
    standings,
    standings_by_date,
)
from courtside_data.client.players import (  # noqa: F401
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
from courtside_data.client.playoffs import (  # noqa: F401
    friv_7_game_playoff_series_outcomes_team_is_down,
    friv_7_game_playoff_series_outcomes_team_is_tied,
    friv_7_game_playoff_series_outcomes_team_is_up,
    playoff_bracket,
    playoff_per_game,
    playoff_totals,
)
from courtside_data.client.teams import (  # noqa: F401
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
from courtside_data.endpoints import ENDPOINTS
from courtside_data.http_service import HTTPService  # noqa: F401

ENDPOINT_FUNCTION_NAMES: tuple[str, ...] = tuple(ENDPOINTS)

# Imported after the endpoint functions exist: CourtsideClient resolves its
# methods through this module at call time.
from courtside_data.client.courtside_client import CourtsideClient  # noqa: E402,F401

# ``__all__`` is derived from the ENDPOINTS registry (the single source of
# truth for every endpoint function) plus the two non-endpoint public symbols
# ``CourtsideClient`` and ``HTTPService``. Adding a new endpoint to
# ``ENDPOINTS`` and importing it above automatically grows this list — no
# hand-maintained enumeration to drift.
__all__ = sorted(set(ENDPOINT_FUNCTION_NAMES) | {"CourtsideClient", "HTTPService"})
