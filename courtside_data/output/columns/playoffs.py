"""CSV column contracts for playoff-scoped Basketball-Reference endpoints.

Covers the playoff per-game and totals stat tables (structurally identical
to the league per-game and totals layouts), the playoff bracket results, and
the 7-game playoff series outcomes (Friv) aggregator.
"""

from courtside_data.output.columns._blocks import (
    COUNTING_STAT_COLUMNS,
    IDENTITY_COLUMNS,
    PER_GAME_STAT_COLUMNS,
)

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
    *IDENTITY_COLUMNS,
    *PER_GAME_STAT_COLUMNS,
    "awards",
]

PLAYOFF_TOTALS_COLUMN_NAMES = [
    *IDENTITY_COLUMNS,
    "mp",
    *COUNTING_STAT_COLUMNS,
    "tpl_dbl",
    "awards",
]

PLAYOFF_BRACKET_COLUMN_NAMES = ["series", "team", "result"]
