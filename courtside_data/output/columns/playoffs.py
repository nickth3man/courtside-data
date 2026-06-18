"""CSV column contracts for playoff-scoped Basketball-Reference endpoints.

Covers the playoff per-game and totals stat tables (structurally identical
to the league per-game and totals layouts), the playoff bracket results, and
the 7-game playoff series outcomes (Friv) aggregator.
"""

FRIV_7_GAME_PLAYOFF_SERIES_OUTCOMES_COLUMN_NAMES = [
    "record",
    "gameslist",
    "wl",
    "aggregate",
    "pattern",
    "pattern_from_spans",
    "patterns_agree",
    "gameslist_display",
    "games_played",
    "games_remaining",
]

PLAYOFF_PER_GAME_COLUMN_NAMES = [
    "name_display",
    "age",
    "team_name_abbr",
    "pos",
    "games",
    "games_started",
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
    "awards",
]

PLAYOFF_TOTALS_COLUMN_NAMES = [
    "name_display",
    "age",
    "team_name_abbr",
    "pos",
    "games",
    "games_started",
    "mp",
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
    "tpl_dbl",
    "awards",
]

PLAYOFF_BRACKET_COLUMN_NAMES = ["series", "team", "result"]
