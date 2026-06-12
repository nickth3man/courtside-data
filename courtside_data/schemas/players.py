"""Row schemas for player-scoped Basketball-Reference endpoints.

Each model is the validation target for one row of one endpoint. Raw rows
arrive as ``dict[str, str]`` keyed by Basketball-Reference ``data-stat``
attribute names; :class:`BRRow` subclasses map those raw keys to stable,
verbose Python attribute names via ``Field(validation_alias=...)`` and
:class:`AliasChoices` for cross-page variance.
"""

from __future__ import annotations

from pydantic import AliasChoices, Field

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow, PerGameStats
from courtside_data.schemas._fields import (
    BRDate,
    BRFloat,
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    BRSalary,
    LeagueField,
    PositionsField,
    TeamField,
    TeamNameField,
)

# ── Private stat-block mixins (player-scoped) ────────────────────────────


class _PlayerGBasedCountingStats:
    """Counting stats whose raw ``data-stat`` for games is ``g`` and minutes
    is ``mp`` (a raw integer total — not a "MM:SS" string)."""

    games_played: BRIntOrNone = Field(default=None, validation_alias="g")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    made_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg")
    attempted_field_goals: BRIntOrNone = Field(default=None, validation_alias="fga")
    made_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3")
    attempted_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3a")
    made_free_throws: BRIntOrNone = Field(default=None, validation_alias="ft")
    attempted_free_throws: BRIntOrNone = Field(default=None, validation_alias="fta")
    offensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="orb")
    defensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="drb")
    total_rebounds: BRIntOrNone = Field(default=None, validation_alias="trb")
    assists: BRIntOrNone = Field(default=None, validation_alias="ast")
    steals: BRIntOrNone = Field(default=None, validation_alias="stl")
    blocks: BRIntOrNone = Field(default=None, validation_alias="blk")
    turnovers: BRIntOrNone = Field(default=None, validation_alias="tov")
    personal_fouls: BRIntOrNone = Field(default=None, validation_alias="pf")
    points: BRIntOrNone = Field(default=None, validation_alias="pts")


class _PlayerPercentageStats:
    """Shooting percentage columns that use BR's ``_pct`` data-stat keys."""

    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")


class _PlayerSeasonContext:
    """Shared context columns: season, age, team, league, position.

    ``team`` is required (every row identifies a team, even if it's a
    multi-team row such as ``"2TM"`` — those rare rows are out of scope for
    ``TeamField`` and surface as a loud validation error).
    """

    season: str = Field(validation_alias="season")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team: TeamField = Field(validation_alias="team_name_abbr")
    league: LeagueField = Field(validation_alias="league_id")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")


# ── Per-game career tables (per_game_stats on the player page) ───────────


class _PlayerCareerPerGameRow(BRRow, _PlayerSeasonContext, PerGameStats):
    """Shared base for the three per-game tables on a player page.

    Inherits the full per-game stat block from :class:`PerGameStats`; the
    ``team`` field is contributed by :class:`_PlayerSeasonContext` (which
    must come earlier in the MRO so its required ``TeamField`` overrides
    ``PerGameStats``' optional ``TeamField | None``).
    """


class PlayerCareerStatsRow(_PlayerCareerPerGameRow):
    """Row from a player's career per-game stats table (``table#per_game_stats``)."""

    # Redefined here purely so the public model name matches the endpoint.
    pass


register("player_career_stats", PlayerCareerStatsRow)


class PlayerPlayoffSeriesRow(_PlayerCareerPerGameRow):
    """Row from a player's playoff-series per-game stats table (``playoffs_series``)."""

    pass


register("player_playoff_series", PlayerPlayoffSeriesRow)


class PlayerAllStarRow(_PlayerCareerPerGameRow):
    """Row from a player's All-Star per-game stats table (``all_star``).

    BR's All-Star table omits the two-point columns; those are inherited
    from :class:`PerGameStats` as optional and remain ``None`` when missing.
    """

    pass


register("player_all_star", PlayerAllStarRow)


# ── Adjusted shooting + play-by-play ────────────────────────────────────


class PlayerAdjustedShootingRow(BRRow, _PlayerGBasedCountingStats, _PlayerSeasonContext, _PlayerPercentageStats):
    """Row from the adjusted-shooting table (``adj_shooting``).

    Adds shooting-rate (per-36) and league-adjusted percentages that the
    generic :class:`_PlayerGBasedCountingStats` block doesn't cover.
    """

    true_shooting_percentage: BRPercentage = Field(default=None, validation_alias="ts_pct")
    field_goals_per_36_minutes: BRFloatOrNone = Field(default=None, validation_alias="fg_per_36_min")
    attempted_field_goals_per_36_minutes: BRFloatOrNone = Field(default=None, validation_alias="fga_per_36_min")
    adjusted_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="adjusted_fg_pct")
    adjusted_three_point_field_goal_percentage: BRPercentage = Field(
        default=None, validation_alias="adjusted_fg3_pct"
    )
    adjusted_free_throw_percentage: BRPercentage = Field(default=None, validation_alias="adjusted_ft_pct")


register("player_adjusted_shooting", PlayerAdjustedShootingRow)


class PlayerPlayByPlayStatsRow(BRRow, _PlayerSeasonContext):
    """Row from the play-by-play derived table (``pbp_stats``).

    Carries percentages of field goals by zone/type — not the live play log
    (that's the ``play_by_play`` endpoint, modeled in ``playbyplay.py``).
    """

    games_played: BRIntOrNone = Field(default=None, validation_alias="g")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    percentage_of_two_point_field_goals: BRPercentage = Field(default=None, validation_alias="pct_fg_2pt")
    percentage_of_three_point_field_goals: BRPercentage = Field(default=None, validation_alias="pct_fg_3pt")
    percentage_assisted_two_point_field_goals: BRPercentage = Field(default=None, validation_alias="pct_ast_2pt")
    percentage_assisted_three_point_field_goals: BRPercentage = Field(
        default=None, validation_alias="pct_ast_3pt"
    )
    percentage_dunks: BRPercentage = Field(default=None, validation_alias="pct_dunks")
    percentage_corner_threes: BRPercentage = Field(default=None, validation_alias="pct_corner_3s")
    percentage_heaves: BRPercentage = Field(default=None, validation_alias="pct_heaves")


register("player_play_by_play", PlayerPlayByPlayStatsRow)


# ── Game highs ───────────────────────────────────────────────────────────


class PlayerGameHighsRow(BRRow):
    """Row from the regular-season game-highs table (``highs-reg-season``).

    The ``opponent`` cell holds the full team name (e.g. ``"Los Angeles
    Lakers"``), not a three-letter abbreviation, so it uses
    :class:`TeamNameField`.
    """

    stat: str = Field(validation_alias="stat")
    value: BRInt = Field(validation_alias="value")
    date: BRDate = Field(validation_alias="date")
    opponent: TeamNameField = Field(validation_alias="opponent")


register("player_game_highs", PlayerGameHighsRow)


# ── Similarity scores, salaries, shot charts (flat tables) ──────────────


class PlayerSimilarityScoresRow(BRRow):
    """Row from the career-similarity scores table (``sims-career``)."""

    rank: BRInt = Field(validation_alias="rank")
    player: str = Field(validation_alias="player")
    similarity_score: BRFloat = Field(validation_alias="similarity_score")


register("player_similarity_scores", PlayerSimilarityScoresRow)


class PlayerSalariesRow(BRRow):
    """Row from the salary history table (``all_salaries``)."""

    season: str = Field(validation_alias="season")
    team: TeamField = Field(validation_alias=AliasChoices("team_id", "team_name_abbr"))
    salary: BRSalary = Field(validation_alias="salary")


register("player_salaries", PlayerSalariesRow)


class PlayerShotChartsRow(BRRow):
    """Row from the shot-type breakdown table (``shooting`` on
    ``/players/{id}/shooting/{year}``).

    Note: this table is a flat shot-type breakdown, not a coordinate
    shot-chart. The columns come from :data:`PLAYER_SHOT_CHARTS_COLUMN_NAMES`.
    """

    shot_type: str = Field(validation_alias="shot_type")
    made: BRIntOrNone = Field(default=None, validation_alias="made")
    attempted: BRIntOrNone = Field(default=None, validation_alias="attempted")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")


register("player_shot_charts", PlayerShotChartsRow)


# ── Splits + on-off (counting-stat tables with ``g`` alias) ──────────────


class PlayerSplitsRow(BRRow, _PlayerGBasedCountingStats, _PlayerPercentageStats):
    """Row from the season splits table (``splits``).

    ``split_type`` and ``value`` carry the split label (e.g. ``"Location"``
    / ``"Home"``); the rest of the row reuses the ``g``-based counting
    block and the percentage block.
    """

    split_type: str = Field(validation_alias="split_type")
    value: str = Field(validation_alias="value")


register("player_splits", PlayerSplitsRow)


class PlayerOnOffRow(BRRow, _PlayerGBasedCountingStats, _PlayerPercentageStats):
    """Row from the on-court vs off-court table (``on-off``).

    ``situation`` is the label (``"On"`` / ``"Off"`` / ``"On-Off"`` /
    ``"Diff"`` — the last two appear in the table footer, not the body).
    """

    situation: str = Field(validation_alias="situation")


register("player_on_off", PlayerOnOffRow)


# ── League-wide season totals (basic + advanced) ─────────────────────────


class PlayerSeasonTotalsRow(BRRow):
    """Row from the league-wide basic season totals table
    (``leagues/NBA_<year>_totals.html``).

    One row per (player, team) for a given season. Combined-totals rows
    (``"2TM"``/``"3TM"``) are filtered out by the legacy table extractor
    before they reach this schema, so ``team`` is always a real
    :class:`Team` abbreviation.
    """

    slug: str = Field(validation_alias="slug")
    name: str = Field(validation_alias="name_display")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team: TeamField = Field(validation_alias="team_name_abbr")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    games_started: BRIntOrNone = Field(default=None, validation_alias="games_started")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    made_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg")
    attempted_field_goals: BRIntOrNone = Field(default=None, validation_alias="fga")
    made_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3")
    attempted_three_point_field_goals: BRIntOrNone = Field(default=None, validation_alias="fg3a")
    made_free_throws: BRIntOrNone = Field(default=None, validation_alias="ft")
    attempted_free_throws: BRIntOrNone = Field(default=None, validation_alias="fta")
    offensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="orb")
    defensive_rebounds: BRIntOrNone = Field(default=None, validation_alias="drb")
    assists: BRIntOrNone = Field(default=None, validation_alias="ast")
    steals: BRIntOrNone = Field(default=None, validation_alias="stl")
    blocks: BRIntOrNone = Field(default=None, validation_alias="blk")
    turnovers: BRIntOrNone = Field(default=None, validation_alias="tov")
    personal_fouls: BRIntOrNone = Field(default=None, validation_alias="pf")
    points: BRIntOrNone = Field(default=None, validation_alias="pts")


register("players_season_totals", PlayerSeasonTotalsRow)


class PlayerAdvancedSeasonTotalsRow(BRRow):
    """Row from the league-wide advanced season totals table
    (``leagues/NBA_<year>_advanced.html``).

    Carries the advanced rate/percentage stat block (PER, TS%, rebound/assist/
    steal/block/turnover/usage percentages, win shares, BPM, VORP) on top of
    the standard identity columns. ``is_combined_totals`` is a derived flag
    computed from the team cell in the legacy extractor (``True`` for
    ``"2TM"``/``"3TM"`` rows); it is included as an optional field so the
    schema matches :data:`PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES` and
    default-initialises to ``False`` when the raw row omits the key.
    """

    slug: str = Field(validation_alias="slug")
    name: str = Field(validation_alias="name_display")
    positions: PositionsField = Field(default_factory=list, validation_alias="pos")
    age: BRIntOrNone = Field(default=None, validation_alias="age")
    team: TeamField = Field(validation_alias="team_name_abbr")
    games_played: BRIntOrNone = Field(default=None, validation_alias="games")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    player_efficiency_rating: BRFloatOrNone = Field(default=None, validation_alias="per")
    true_shooting_percentage: BRPercentage = Field(default=None, validation_alias="ts_pct")
    three_point_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="fg3a_per_fga_pct")
    free_throw_attempt_rate: BRFloatOrNone = Field(default=None, validation_alias="fta_per_fga_pct")
    offensive_rebound_percentage: BRPercentage = Field(default=None, validation_alias="orb_pct")
    defensive_rebound_percentage: BRPercentage = Field(default=None, validation_alias="drb_pct")
    total_rebound_percentage: BRPercentage = Field(default=None, validation_alias="trb_pct")
    assist_percentage: BRPercentage = Field(default=None, validation_alias="ast_pct")
    steal_percentage: BRPercentage = Field(default=None, validation_alias="stl_pct")
    block_percentage: BRPercentage = Field(default=None, validation_alias="blk_pct")
    turnover_percentage: BRPercentage = Field(default=None, validation_alias="tov_pct")
    usage_percentage: BRPercentage = Field(default=None, validation_alias="usg_pct")
    offensive_win_shares: BRFloatOrNone = Field(default=None, validation_alias="ows")
    defensive_win_shares: BRFloatOrNone = Field(default=None, validation_alias="dws")
    win_shares: BRFloatOrNone = Field(default=None, validation_alias="ws")
    win_shares_per_48_minutes: BRFloatOrNone = Field(default=None, validation_alias="ws_per_48")
    offensive_box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="obpm")
    defensive_box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="dbpm")
    box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="bpm")
    value_over_replacement_player: BRFloatOrNone = Field(default=None, validation_alias="vorp")
    is_combined_totals: bool = Field(default=False, validation_alias="is_combined_totals")


register("players_advanced_season_totals", PlayerAdvancedSeasonTotalsRow)
