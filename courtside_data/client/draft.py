"""Draft picks, season awards, and season/career statistical leaders."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.data import OutputType, OutputWriteOption


def draft_picks(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Draft picks for a draft year.

    URL: /draft/NBA_{season_end_year}.html
    """
    return _run_endpoint(
        "draft_picks",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def season_awards(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Season award voting results (MVP table).

    URL: /awards/awards_{season_end_year}.html
    """
    return _run_endpoint(
        "season_awards",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def season_leaders(
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Single-season statistical leaders across league history.

    URL: /leaders/per_season.html
    """
    return _run_endpoint(
        "season_leaders",
        {},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )


def career_leaders(
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    """Career statistical leaders across league history.

    URL: /leaders/
    """
    return _run_endpoint(
        "career_leaders",
        {},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
    )
