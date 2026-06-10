"""Type coercion layer for basketball-reference scraper output.

Generic endpoints return all values as raw strings from HTML. This module
converts them to proper Python types (int, float) using a column-name registry
plus heuristic fallback rules.

Legacy endpoints already produce typed values — coercion is idempotent for them
(values already matching the target type pass through unchanged).
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

# ─── Coercion functions ────────────────────────────────────────────────


def coerce_int(value: Any) -> int | Any:
    """Convert str to int. Pass through non-str values (already typed)."""
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped or stripped == "\xa0":
        return 0
    try:
        return int(stripped)
    except ValueError:
        return value  # can't parse, leave as-is


def coerce_float(value: Any) -> float | Any:
    """Convert str to float. Pass through non-str values."""
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped or stripped == "\xa0":
        return 0.0
    try:
        return float(stripped)
    except ValueError:
        return value


def coerce_int_or_none(value: Any) -> int | None | Any:
    """Convert str to int, empty str to None. Pass through non-str."""
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped or stripped == "\xa0":
        return None
    try:
        return int(stripped)
    except ValueError:
        return value


def coerce_float_or_none(value: Any) -> float | None | Any:
    """Convert str to float, empty str to None. Pass through non-str."""
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped or stripped == "\xa0":
        return None
    try:
        return float(stripped)
    except ValueError:
        return value


# ─── Column → type mapping ─────────────────────────────────────────────

# Explicit column-type registry. Keys are the raw data-stat / dict key names
# that appear in scraped rows. Values are coercion functions.
_COLUMN_TYPE_MAP: dict[str, Callable] = {
    # ── Player identity ──
    "name_display": lambda v: v,  # str pass-through
    "slug": lambda v: v,
    "name": lambda v: v,
    "identifier": lambda v: v,
    "player": lambda v: v,
    "college_name": lambda v: v,
    "college": lambda v: v,
    "pos": lambda v: v,
    "positions": lambda v: v,
    "flag": lambda v: v,
    "team_name_abbr": lambda v: v,
    "team_id": lambda v: v,
    "team_abbreviation": lambda v: v,
    "team": lambda v: v,  # could be Team enum (legacy) or str (generic)
    "opponent": lambda v: v,
    "location": lambda v: v,
    "outcome": lambda v: v,
    "conference": lambda v: v,
    "division": lambda v: v,
    "league_id": lambda v: v,
    "leagues": lambda v: v,
    "season": lambda v: v,
    "date": lambda v: v,
    "start_time": lambda v: v,
    "description": lambda v: v,
    "transaction": lambda v: v,
    "award": lambda v: v,
    "stat": lambda v: v,
    "value": lambda v: v,
    "period_type": lambda v: v,
    "relevant_team": lambda v: v,
    "away_team": lambda v: v,
    "home_team": lambda v: v,
    "series": lambda v: v,
    "result": lambda v: v,
    "split_type": lambda v: v,
    "stat_type": lambda v: v,
    "situation": lambda v: v,
    "shot_type": lambda v: v,
    "lineup": lambda v: v,
    "streak": lambda v: v,
    "birth_date": lambda v: v,
    "height": lambda v: v,
    "weight": lambda v: v,
    "number": lambda v: v,  # jersey number (could be "00")
    "starts": lambda v: v,
    "active": lambda v: v,

    # ── Integer stats ──
    "age": coerce_int_or_none,
    "games": coerce_int,
    "games_played": coerce_int,
    "games_started": coerce_int,
    "mp": coerce_int,  # total minutes
    "minutes_played": coerce_int,
    "seconds_played": coerce_int,
    "fg": coerce_int,
    "fga": coerce_int,
    "fg_per_g": coerce_float,
    "fga_per_g": coerce_float,
    "fg3": coerce_int,
    "fg3a": coerce_int,
    "fg3_per_g": coerce_float,
    "fg3a_per_g": coerce_float,
    "fg2": coerce_int,
    "fg2a": coerce_int,
    "fg2_per_g": coerce_float,
    "fg2a_per_g": coerce_float,
    "ft": coerce_int,
    "fta": coerce_int,
    "ft_per_g": coerce_float,
    "fta_per_g": coerce_float,
    "orb": coerce_int,
    "drb": coerce_int,
    "trb": coerce_int,
    "ast": coerce_int,
    "stl": coerce_int,
    "blk": coerce_int,
    "tov": coerce_int,
    "pf": coerce_int,
    "pts": coerce_int,
    "orb_per_g": coerce_float,
    "drb_per_g": coerce_float,
    "trb_per_g": coerce_float,
    "ast_per_g": coerce_float,
    "stl_per_g": coerce_float,
    "blk_per_g": coerce_float,
    "tov_per_g": coerce_float,
    "pf_per_g": coerce_float,
    "pts_per_g": coerce_float,
    "made_field_goals": coerce_int,
    "attempted_field_goals": coerce_int,
    "made_three_point_field_goals": coerce_int,
    "attempted_three_point_field_goals": coerce_int,
    "made_free_throws": coerce_int,
    "attempted_free_throws": coerce_int,
    "offensive_rebounds": coerce_int,
    "defensive_rebounds": coerce_int,
    "assists": coerce_int,
    "steals": coerce_int,
    "blocks": coerce_int,
    "turnovers": coerce_int,
    "personal_fouls": coerce_int,
    "points": coerce_int,
    "points_scored": coerce_int,
    "away_score": coerce_int,
    "home_score": coerce_int,
    "away_team_score": coerce_int,
    "home_team_score": coerce_int,

    # ── More integer stats ──
    "wins": coerce_int,
    "losses": coerce_int,
    "rank": coerce_int,
    "pick_overall": coerce_int,
    "seasons": coerce_int,
    "years_experience": coerce_int,
    "years_remaining": coerce_int,
    "salary": coerce_int,  # NBA salaries are whole dollars
    "overtimes": coerce_int,
    "home_games": coerce_int,
    "away_games": coerce_int,
    "home_attendance": coerce_int,
    "away_attendance": coerce_int,
    "game_number": coerce_int,
    "period": coerce_int,
    "num_shots_heaved": coerce_int,
    "made": coerce_int,
    "attempted": coerce_int,

    # ── Float stats ──
    "fg_pct": coerce_float,
    "fg3_pct": coerce_float,
    "fg2_pct": coerce_float,
    "efg_pct": coerce_float,
    "ft_pct": coerce_float,
    "ts_pct": coerce_float,
    "game_score": coerce_float,
    "plus_minus": coerce_float,
    "remaining_seconds_in_period": coerce_float,
    "is_combined_totals": coerce_float,
    "win_loss_pct": coerce_float,
    "gb": coerce_float,
    "srs": coerce_float,
    "ws": coerce_float,
    "ws_per_48": coerce_float,
    "bpm": coerce_float,
    "vorp": coerce_float,
    "similarity_score": coerce_float,

    # ── Per-36 / per-100 / per-g (float) ──
    "mp_per_g": coerce_float,
    "fg_per_36_min": coerce_float,
    "fga_per_36_min": coerce_float,
    "fg3_per_36_min": coerce_float,
    "fg3a_per_36_min": coerce_float,
    "fg2_per_36_min": coerce_float,
    "fg2a_per_36_min": coerce_float,
    "ft_per_36_min": coerce_float,
    "fta_per_36_min": coerce_float,
    "orb_per_36_min": coerce_float,
    "drb_per_36_min": coerce_float,
    "trb_per_36_min": coerce_float,
    "ast_per_36_min": coerce_float,
    "stl_per_36_min": coerce_float,
    "blk_per_36_min": coerce_float,
    "tov_per_36_min": coerce_float,
    "pf_per_36_min": coerce_float,
    "pts_per_36_min": coerce_float,
    "fg_per_100_poss": coerce_float,
    "fga_per_100_poss": coerce_float,
    "fg3_per_100_poss": coerce_float,
    "fg3a_per_100_poss": coerce_float,
    "fg2_per_100_poss": coerce_float,
    "fg2a_per_100_poss": coerce_float,
    "ft_per_100_poss": coerce_float,
    "fta_per_100_poss": coerce_float,
    "orb_per_100_poss": coerce_float,
    "drb_per_100_poss": coerce_float,
    "trb_per_100_poss": coerce_float,
    "ast_per_100_poss": coerce_float,
    "stl_per_100_poss": coerce_float,
    "blk_per_100_poss": coerce_float,
    "tov_per_100_poss": coerce_float,
    "pf_per_100_poss": coerce_float,
    "pts_per_100_poss": coerce_float,

    # ── Percentage/rate stats ──
    "home_attendance_per_g": coerce_float,
    "away_attendance_per_g": coerce_float,
    "pts_per_g": coerce_float,
    "opp_pts_per_g": coerce_float,
    "player_efficiency_rating": coerce_float,
    "true_shooting_percentage": coerce_float,
    "three_point_attempt_rate": coerce_float,
    "free_throw_attempt_rate": coerce_float,
    "offensive_rebound_percentage": coerce_float,
    "defensive_rebound_percentage": coerce_float,
    "total_rebound_percentage": coerce_float,
    "assist_percentage": coerce_float,
    "steal_percentage": coerce_float,
    "block_percentage": coerce_float,
    "turnover_percentage": coerce_float,
    "usage_percentage": coerce_float,
    "offensive_win_shares": coerce_float,
    "defensive_win_shares": coerce_float,
    "win_shares": coerce_float,
    "win_shares_per_48_minutes": coerce_float,
    "offensive_box_plus_minus": coerce_float,
    "defensive_box_plus_minus": coerce_float,
    "box_plus_minus": coerce_float,
    "value_over_replacement_player": coerce_float,
    "pace": coerce_float,
    "tov_pct": coerce_float,
    "orb_pct": coerce_float,
    "ft_rate": coerce_float,
    "opp_efg_pct": coerce_float,
    "opp_tov_pct": coerce_float,
    "drb_pct": coerce_float,
    "opp_ft_rate": coerce_float,
    "adjusted_fg_pct": coerce_float,
    "adjusted_fg3_pct": coerce_float,
    "adjusted_ft_pct": coerce_float,

    # ── Shooting distribution ──
    "fg_pct_from_0_3_ft": coerce_float,
    "fg_pct_from_3_10_ft": coerce_float,
    "fg_pct_from_10_16_ft": coerce_float,
    "fg_pct_from_16_3p": coerce_float,
    "fg_pct_from_3p": coerce_float,
    "pct_fga_from_0_3_ft": coerce_float,
    "pct_fga_from_3_10_ft": coerce_float,
    "pct_fga_from_10_16_ft": coerce_float,
    "pct_fga_from_16_3p": coerce_float,
    "pct_fga_from_3p": coerce_float,
    "fg_pct_from_2p": coerce_float,
    "fg_pct_from_0_3_ft_2": coerce_float,
    "fg_pct_from_corner_3": coerce_float,
    "pct_fga_from_corner_3": coerce_float,
    "pct_shots_heaved": coerce_float,

    # ── Play-by-play ──
    "pct_fg_2pt": coerce_float,
    "pct_fg_3pt": coerce_float,
    "pct_ast_2pt": coerce_float,
    "pct_ast_3pt": coerce_float,
    "pct_dunks": coerce_float,
    "pct_corner_3s": coerce_float,
    "pct_heaves": coerce_float,

    # ── Generic fallback columns (col_N from ad-hoc tables) ──
    # These are used by playoff_bracket, season_awards and other irregular tables.
    # They contain mixed content (dates, team names, scores). Leave as str.
}


def _infer_coercion(column_name: str) -> Callable:
    """Return a coercion function for a column not in the explicit registry.

    Uses naming heuristics based on basketball-reference data-stat conventions.
    """
    name = column_name.lower()

    # Explicit int patterns
    if name in ("g", "mp"):
        return coerce_int

    # Percentage / rate patterns → float
    if (
        name.endswith("_pct")
        or name.endswith("_rate")
        or name.endswith("_percentage")
        or "_per_" in name
        or name.endswith("_per_g")
        or "win_shares" in name
        or "box_plus_minus" in name
        or name.endswith("_vorp")
        or name.endswith("_bpm")
        or name.endswith("_ws")
    ):
        return coerce_float

    # Count / integer patterns
    int_patterns = (
        "games", "wins", "losses", "rank", "pick_", "seasons",
        "years_", "salary", "overtimes", "_attendance", "_games",
        "fg", "fga", "fg3", "fg3a", "fg2", "fg2a",
        "ft", "fta", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pf",
        "pts", "points", "score", "made_", "attempted_",
        "rebounds", "assists", "steals", "blocks", "turnovers",
        "personal_fouls", "seconds_played", "minutes_played",
        "period", "num_shots", "attempted", "made",
    )
    if any(name.startswith(pat) or name.endswith(f"_{pat}") or pat in name for pat in int_patterns):
        return coerce_int

    # Default: leave as str
    return lambda v: v


def get_coercion(column_name: str) -> Callable:
    """Return the coercion function for a given column name.

    Checks the explicit registry first, then falls back to heuristic inference.
    """
    if column_name in _COLUMN_TYPE_MAP:
        return _COLUMN_TYPE_MAP[column_name]
    return _infer_coercion(column_name)


def coerce_row(row: dict[str, Any]) -> dict[str, Any]:
    """Apply type coercion to every value in a row dict.

    Idempotent — already-typed values (int, float, Enum, etc.) pass through
    unchanged. Only raw strings from HTML are converted.
    """
    return {
        key: get_coercion(key)(value)
        for key, value in row.items()
    }


def coerce_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply type coercion to a list of row dicts."""
    return [coerce_row(r) for r in rows]


def coerce_data(data):
    """Apply type coercion to endpoint output data.

    Handles both list[dict] and dict[str, list[dict]] shapes.
    """
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            return coerce_rows(data)
    elif isinstance(data, dict):
        result = {}
        for key, val in data.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                result[key] = coerce_rows(val)
            else:
                result[key] = val
        return result
    return data
