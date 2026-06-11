# ── Legacy endpoints (explicit imports) ──────────────────────────────────
from courtside_data.client import (
    play_by_play,
    player_box_scores,
    playoff_player_box_scores,
    regular_season_player_box_scores,
    search,
    season_schedule,
    standings,
    team_box_scores,
)
from courtside_data.client import (
    players_advanced_season_totals as player_advanced_season_totals,
)
from courtside_data.client import (
    players_season_totals as player_season_totals,
)

# ── Beta endpoints (generated from ENDPOINTS registry) ───────────────────
from courtside_data.endpoints import ENDPOINTS
from courtside_data import client as _client

# Make beta functions reachable at package level
for _name in ENDPOINTS:
    globals()[_name] = getattr(_client, _name)

# Export both tiers
__all__ = [
    # Legacy
    "standings",
    "player_box_scores",
    "team_box_scores",
    "season_schedule",
    "play_by_play",
    "player_season_totals",
    "player_advanced_season_totals",
    "regular_season_player_box_scores",
    "playoff_player_box_scores",
    "search",
    # Beta (auto-generated from ENDPOINTS)
    *sorted(ENDPOINTS.keys()),
]
