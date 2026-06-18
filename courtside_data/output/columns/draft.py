"""CSV column contract for the draft Basketball-Reference endpoint.

Covers the ``draft_picks`` table (``/draft/NBA_{year}.html``) — pick overall,
player, college, drafting team, career totals, and per-game averages.
"""

DRAFT_PICKS_COLUMN_NAMES = [
    "pick_overall",
    "player",
    "college_name",
    "team_id",
    "seasons",
    "g",
    "mp",
    "pts",
    "trb",
    "ast",
    "fg_pct",
    "fg3_pct",
    "ft_pct",
    "mp_per_g",
    "pts_per_g",
    "trb_per_g",
    "ast_per_g",
    "ws",
    "ws_per_48",
    "bpm",
    "vorp",
]
