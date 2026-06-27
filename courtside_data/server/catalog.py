"""Player Hub dataset and tab catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from courtside_data.endpoints import ENDPOINTS
from courtside_data.server.models import ColumnMeta, DatasetCatalogEntry, DatasetScope, PlayerHubTab


@dataclass(frozen=True, slots=True)
class PlayerHubDataset:
    id: str
    label: str
    endpoint_name: str
    scope: DatasetScope
    description: str
    default_visible_columns: tuple[str, ...]


DATASETS: dict[str, PlayerHubDataset] = {
    "career": PlayerHubDataset(
        id="career",
        label="Career",
        endpoint_name="player_career_stats",
        scope="player",
        description="Season-by-season per-game production.",
        default_visible_columns=(
            "season",
            "age",
            "team_name_abbr",
            "positions",
            "games_played",
            "points_per_game",
            "total_rebounds_per_game",
            "assists_per_game",
            "field_goal_percentage",
            "three_point_field_goal_percentage",
            "effective_field_goal_percentage",
        ),
    ),
    "playoff-series": PlayerHubDataset(
        id="playoff-series",
        label="Playoff Series",
        endpoint_name="player_playoff_series",
        scope="player",
        description="Series-level playoff results and production.",
        default_visible_columns=(
            "year_id",
            "team_name_abbr",
            "playoff_round",
            "opponent_name_abbr",
            "series_result",
            "points_per_game",
            "total_rebounds_per_game",
            "assists_per_game",
            "field_goal_percentage",
        ),
    ),
    "adjusted-shooting": PlayerHubDataset(
        id="adjusted-shooting",
        label="Adjusted Shooting",
        endpoint_name="player_adjusted_shooting",
        scope="player",
        description="Shooting percentages indexed to league environment.",
        default_visible_columns=(
            "year_id",
            "team_name_abbr",
            "games_played",
            "true_shooting_percentage",
            "adjusted_true_shooting_percentage",
            "effective_field_goal_percentage",
            "adjusted_effective_field_goal_percentage",
            "field_goal_points_added",
            "true_shooting_points_added",
        ),
    ),
    "derived-play-by-play": PlayerHubDataset(
        id="derived-play-by-play",
        label="Derived Play-by-Play",
        endpoint_name="player_play_by_play",
        scope="player",
        description="Position, usage, plus-minus, foul, and assisted-shot derived fields.",
        default_visible_columns=(
            "year_id",
            "team_name_abbr",
            "positions",
            "games_played",
            "plus_minus_on",
            "plus_minus_net",
            "assisted_points",
            "and_ones",
        ),
    ),
    "game-highs": PlayerHubDataset(
        id="game-highs",
        label="Game Highs",
        endpoint_name="player_game_highs",
        scope="player",
        description="Regular-season single-game bests by season.",
        default_visible_columns=(
            "season",
            "team",
            "points",
            "total_rebounds",
            "assists",
            "steals",
            "blocks",
            "game_score",
        ),
    ),
    "all-star": PlayerHubDataset(
        id="all-star",
        label="All-Star",
        endpoint_name="player_all_star",
        scope="player",
        description="All-Star appearance box-score lines.",
        default_visible_columns=("season", "team_id", "positions", "points", "total_rebounds", "assists"),
    ),
    "similarity": PlayerHubDataset(
        id="similarity",
        label="Similarity",
        endpoint_name="player_similarity_scores",
        scope="player",
        description="Basketball Reference career similarity scores.",
        default_visible_columns=("player", "sim_score", "year1", "year2", "year3", "year4", "year5"),
    ),
    "salaries": PlayerHubDataset(
        id="salaries",
        label="Salaries",
        endpoint_name="player_salaries",
        scope="player",
        description="Salary history by season.",
        default_visible_columns=("season", "team_name", "salary"),
    ),
    "splits": PlayerHubDataset(
        id="splits",
        label="Splits",
        endpoint_name="player_splits",
        scope="season",
        description="Selected-season splits.",
        default_visible_columns=(
            "split_value",
            "games_played",
            "minutes_played",
            "points_per_game",
            "total_rebounds_per_game",
            "assists_per_game",
            "true_shooting_percentage",
            "usage_percentage",
        ),
    ),
    "on-off": PlayerHubDataset(
        id="on-off",
        label="On/Off",
        endpoint_name="player_on_off",
        scope="season",
        description="Selected-season on/off court impact.",
        default_visible_columns=(
            "split_id",
            "team_id",
            "minutes_played",
            "offensive_rating",
            "opponent_offensive_rating",
            "diff_offensive_rating",
            "diff_effective_field_goal_percentage",
        ),
    ),
    "shooting-breakdown": PlayerHubDataset(
        id="shooting-breakdown",
        label="Shooting Breakdown",
        endpoint_name="player_shot_charts",
        scope="season",
        description="Flat shot-type and distance breakdown, not coordinate shot-chart data.",
        default_visible_columns=(
            "split_value",
            "made_field_goals",
            "attempted_field_goals",
            "field_goal_percentage",
            "made_three_point_field_goals",
            "attempted_three_point_field_goals",
            "effective_field_goal_percentage",
        ),
    ),
    "regular-games": PlayerHubDataset(
        id="regular-games",
        label="Regular Games",
        endpoint_name="regular_season_player_box_scores",
        scope="season",
        description="Game-by-game regular-season box scores.",
        default_visible_columns=(
            "game_number",
            "date",
            "team",
            "opponent",
            "points",
            "total_rebounds",
            "assists",
            "game_score",
        ),
    ),
    "playoff-games": PlayerHubDataset(
        id="playoff-games",
        label="Playoff Games",
        endpoint_name="playoff_player_box_scores",
        scope="season",
        description="Game-by-game playoff box scores.",
        default_visible_columns=(
            "game_number",
            "date",
            "team",
            "opponent",
            "points",
            "total_rebounds",
            "assists",
            "game_score",
        ),
    ),
}


TABS: tuple[PlayerHubTab, ...] = (
    PlayerHubTab(
        id="overview",
        label="Overview",
        description="Hero metrics, career arc, seasons, and source status.",
        scope="player",
        datasets=["career"],
        default_dataset="career",
    ),
    PlayerHubTab(
        id="career",
        label="Career",
        description="Season-by-season career table.",
        scope="player",
        datasets=["career"],
        default_dataset="career",
    ),
    PlayerHubTab(
        id="playoffs",
        label="Playoffs",
        description="Playoff series and playoff game logs.",
        scope="player",
        datasets=["playoff-series", "playoff-games"],
        default_dataset="playoff-series",
    ),
    PlayerHubTab(
        id="shooting",
        label="Shooting",
        description="Adjusted shooting and selected-season shooting breakdown.",
        scope="player",
        datasets=["adjusted-shooting", "shooting-breakdown"],
        default_dataset="adjusted-shooting",
    ),
    PlayerHubTab(
        id="splits",
        label="Splits",
        description="Selected-season splits.",
        scope="season",
        datasets=["splits"],
        default_dataset="splits",
    ),
    PlayerHubTab(
        id="on-off",
        label="On/Off",
        description="Selected-season on/off impact.",
        scope="season",
        datasets=["on-off"],
        default_dataset="on-off",
    ),
    PlayerHubTab(
        id="games",
        label="Games",
        description="Regular-season and playoff game logs.",
        scope="season",
        datasets=["regular-games", "playoff-games"],
        default_dataset="regular-games",
    ),
    PlayerHubTab(
        id="more",
        label="More",
        description="Highs, All-Star, salaries, similarity, and derived play-by-play.",
        scope="player",
        datasets=["game-highs", "all-star", "salaries", "similarity", "derived-play-by-play"],
        default_dataset="game-highs",
    ),
)


NUMERIC_HINTS = (
    "age",
    "games",
    "points",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "percentage",
    "rating",
    "minutes",
    "salary",
    "score",
    "made_",
    "attempted_",
    "plus_minus",
)


def column_label(key: str) -> str:
    initialisms = {
        "id": "ID",
        "fg": "FG",
        "ft": "FT",
        "nba": "NBA",
        "aba": "ABA",
    }
    words = []
    for word in key.split("_"):
        words.append(initialisms.get(word, word.capitalize()))
    return " ".join(words)


def column_meta_for_key(key: str, *, default_visible: bool) -> ColumnMeta:
    lowered = key.lower()
    numeric = any(hint in lowered for hint in NUMERIC_HINTS)
    return ColumnMeta(key=key, label=column_label(key), default_visible=default_visible, numeric=numeric)


def columns_for_dataset(dataset: PlayerHubDataset, sample_row: dict[str, Any] | None = None) -> list[ColumnMeta]:
    endpoint = ENDPOINTS[dataset.endpoint_name]
    keys = list(sample_row) if sample_row is not None else list(endpoint.row_model.model_fields)
    defaults = set(dataset.default_visible_columns)
    return [column_meta_for_key(key, default_visible=key in defaults) for key in keys]


def dataset_entry(dataset: PlayerHubDataset) -> DatasetCatalogEntry:
    return DatasetCatalogEntry(
        id=dataset.id,
        label=dataset.label,
        endpoint_name=dataset.endpoint_name,
        scope=dataset.scope,
        description=dataset.description,
        columns=columns_for_dataset(dataset),
        default_visible_columns=list(dataset.default_visible_columns),
    )


def dataset_by_id(dataset_id: str) -> PlayerHubDataset:
    try:
        return DATASETS[dataset_id]
    except KeyError:
        raise ValueError(f"Unknown Player Hub dataset: {dataset_id}") from None


def player_hub_catalog() -> dict[str, object]:
    return {
        "tabs": [tab.model_dump(mode="json") for tab in TABS],
        "datasets": [dataset_entry(dataset).model_dump(mode="json") for dataset in DATASETS.values()],
    }
