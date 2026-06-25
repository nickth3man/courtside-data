"""Playoff per-game and total statistics plus bracket results."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.domain import OutputType, OutputWriteOption


def playoff_per_game(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Playoff per-game player statistics for a season.

    URL: /leagues/NBA_{season_end_year}_per_game.html
    """
    return _run_endpoint(
        "playoff_per_game",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def playoff_totals(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Playoff total player statistics for a season.

    URL: /leagues/NBA_{season_end_year}_totals.html
    """
    return _run_endpoint(
        "playoff_totals",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def playoff_bracket(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Playoff bracket series results for a season.

    URL: /playoffs/NBA_{season_end_year}.html
    """
    return _run_endpoint(
        "playoff_bracket",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def friv_7_game_playoff_series_outcomes_team_is_down(
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Seven-game playoff series outcomes for teams trailing in the series.

    URL: /friv/7-game-playoff-series-outcomes-22111.html
    """
    return _run_endpoint(
        "friv_7_game_playoff_series_outcomes_team_is_down",
        {},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def friv_7_game_playoff_series_outcomes_team_is_tied(
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Seven-game playoff series outcomes for teams tied in the series.

    URL: /friv/7-game-playoff-series-outcomes-22111.html
    """
    return _run_endpoint(
        "friv_7_game_playoff_series_outcomes_team_is_tied",
        {},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def friv_7_game_playoff_series_outcomes_team_is_up(
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Seven-game playoff series outcomes for teams leading in the series.

    URL: /friv/7-game-playoff-series-outcomes-22111.html
    """
    return _run_endpoint(
        "friv_7_game_playoff_series_outcomes_team_is_up",
        {},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )
