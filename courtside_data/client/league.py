"""League-wide season tables: per-game/per-36/per-100/totals/shooting
stats, rookies, standings, attendance, and transactions."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.data import OutputType, OutputWriteOption


def league_per_game_stats(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """League-wide per-game player statistics for a season.

    URL: /leagues/NBA_{season_end_year}_per_game.html
    """
    return _run_endpoint(
        "league_per_game_stats",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def league_per_36_minutes(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """League-wide per-36-minute player statistics for a season.

    URL: /leagues/NBA_{season_end_year}_per_minute.html
    """
    return _run_endpoint(
        "league_per_36_minutes",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def league_totals(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """League-wide total player statistics for a season.

    URL: /leagues/NBA_{season_end_year}_totals.html
    """
    return _run_endpoint(
        "league_totals",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def league_per_100_possessions(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """League-wide per-100-possessions player statistics for a season.

    URL: /leagues/NBA_{season_end_year}_per_poss.html
    """
    return _run_endpoint(
        "league_per_100_possessions",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def league_shooting(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """League-wide shooting statistics for a season.

    URL: /leagues/NBA_{season_end_year}_shooting.html
    """
    return _run_endpoint(
        "league_shooting",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def league_transactions(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """League-wide transactions for a season.

    URL: /leagues/NBA_{season_end_year}_transactions.html
    """
    return _run_endpoint(
        "league_transactions",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def rookie_stats(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Rookie statistics for a season.

    URL: /leagues/NBA_{season_end_year}_rookies.html
    """
    return _run_endpoint(
        "rookie_stats",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def standings(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Eastern and Western conference standings for a season.

    URL: /leagues/NBA_{season_end_year}.html
    """
    return _run_endpoint(
        "standings",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def standings_by_date(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Day-by-day standings for both conferences for a season.

    URL: /leagues/NBA_{season_end_year}_standings_by_date_{conference}.html
    """
    return _run_endpoint(
        "standings_by_date",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def attendance(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Per-team arena attendance for a season.

    URL: /leagues/NBA_{season_end_year}.html
    """
    return _run_endpoint(
        "attendance",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )
