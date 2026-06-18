"""Shared CSV column fragments reused across domain contracts.

The fragments defined here capture the common column patterns that repeat
across league, playoff, and player stat tables. Each fragment is documented
with the domain lists that include it.

Importing from this module rather than duplicating the literal list in every
domain file keeps the column contracts consistent and easy to audit.
"""

# ── Identity columns ────────────────────────────────────────────────────
# Leading columns in:
#   * ``LEAGUE_PER_GAME_COLUMN_NAMES``
#   * ``LEAGUE_PER_36_COLUMN_NAMES``
#   * ``LEAGUE_TOTALS_COLUMN_NAMES``
#   * ``LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES``
#   * ``LEAGUE_SHOOTING_COLUMN_NAMES``
#   * ``LEAGUE_PLAY_BY_PLAY_COLUMN_NAMES``
#   * ``PLAYOFF_PER_GAME_COLUMN_NAMES``
#   * ``PLAYOFF_TOTALS_COLUMN_NAMES``
IDENTITY_COLUMNS = [
    "name_display",
    "age",
    "team_name_abbr",
    "pos",
    "games",
    "games_started",
]

# ── Counting-stat columns (raw, no per-X suffix) ────────────────────────
# Follows ``IDENTITY_COLUMNS + ["mp"]`` in:
#   * ``LEAGUE_TOTALS_COLUMN_NAMES``
#   * ``PLAYOFF_TOTALS_COLUMN_NAMES``
# Precedes the trailing ``["tpl_dbl", "awards"]``.
COUNTING_STAT_COLUMNS = [
    "fg",
    "fga",
    "fg_pct",
    "fg3",
    "fg3a",
    "fg3_pct",
    "fg2",
    "fg2a",
    "fg2_pct",
    "efg_pct",
    "ft",
    "fta",
    "ft_pct",
    "orb",
    "drb",
    "trb",
    "ast",
    "stl",
    "blk",
    "tov",
    "pf",
    "pts",
]

# ── Per-game suffixed stat columns ──────────────────────────────────────
# Follows ``IDENTITY_COLUMNS`` in:
#   * ``LEAGUE_PER_GAME_COLUMN_NAMES``
#   * ``PLAYOFF_PER_GAME_COLUMN_NAMES``
# Also used in ``PLAYER_CAREER_STATS_COLUMN_NAMES`` (after a 7-column
# identity stem).
# Precedes trailing ``["awards"]``.
PER_GAME_STAT_COLUMNS = [
    "mp_per_g",
    "fg_per_g",
    "fga_per_g",
    "fg_pct",
    "fg3_per_g",
    "fg3a_per_g",
    "fg3_pct",
    "fg2_per_g",
    "fg2a_per_g",
    "fg2_pct",
    "efg_pct",
    "ft_per_g",
    "fta_per_g",
    "ft_pct",
    "orb_per_g",
    "drb_per_g",
    "trb_per_g",
    "ast_per_g",
    "stl_per_g",
    "blk_per_g",
    "tov_per_g",
    "pf_per_g",
    "pts_per_g",
]
