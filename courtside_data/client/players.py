"""Per-player endpoints: career stats, splits, shooting, salaries, and more."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.data import OutputType, OutputWriteOption


def player_career_stats(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Season-by-season per-game career statistics for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_career_stats",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_playoff_series(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Playoff series results for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_playoff_series",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_adjusted_shooting(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """League-adjusted shooting statistics for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_adjusted_shooting",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_play_by_play(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Play-by-play position and usage statistics for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_play_by_play",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_game_highs(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Regular-season game highs for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_game_highs",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_all_star(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """All-Star game appearances for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_all_star",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_similarity_scores(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Career similarity scores for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_similarity_scores",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_salaries(
    player_identifier: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Year-by-year salaries for a player.

    URL: /players/{player_identifier[0]}/{player_identifier}.html
    """
    return _run_endpoint(
        "player_salaries",
        {"player_identifier": player_identifier},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_splits(
    player_identifier: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Statistical splits for a player in a season.

    URL: /players/{player_identifier[0]}/{player_identifier}/splits/{season_end_year}
    """
    return _run_endpoint(
        "player_splits",
        {"player_identifier": player_identifier, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_on_off(
    player_identifier: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """On/off court impact statistics for a player in a season.

    URL: /players/{player_identifier[0]}/{player_identifier}/on-off/{season_end_year}
    """
    return _run_endpoint(
        "player_on_off",
        {"player_identifier": player_identifier, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_shot_charts(
    player_identifier: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Shooting distance/zone breakdown for a player in a season.

    URL: /players/{player_identifier[0]}/{player_identifier}/shooting/{season_end_year}
    """
    return _run_endpoint(
        "player_shot_charts",
        {"player_identifier": player_identifier, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )
