"""Per-team endpoints: rosters, schedules, lineups, contracts, and franchise history."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.domain import OutputType, OutputWriteOption


def team_roster(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Roster for a team in a season.

    URL: /teams/{team_abbreviation}/{season_end_year}.html
    """
    return _run_endpoint(
        "team_roster",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_injury_report(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Current league-wide injury report.

    Team/season parameters are accepted for API symmetry but do not affect
    the request.

    URL: /friv/injuries.fcgi
    """
    return _run_endpoint(
        "team_injury_report",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_and_opponent(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Team and opponent aggregate statistics for a season.

    URL: /teams/{team_abbreviation}/{season_end_year}.html
    """
    return _run_endpoint(
        "team_and_opponent",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_misc_four_factors(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Miscellaneous team statistics including four factors for a season.

    URL: /teams/{team_abbreviation}/{season_end_year}.html
    """
    return _run_endpoint(
        "team_misc_four_factors",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_opponent_stats(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Opponent statistics against a team for a season.

    URL: /teams/{team_abbreviation}/{season_end_year}.html
    """
    return _run_endpoint(
        "team_opponent_stats",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_schedule(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Game-by-game schedule and results for a team in a season.

    URL: /teams/{team_abbreviation}/{season_end_year}_games.html
    """
    return _run_endpoint(
        "team_schedule",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_transactions(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Transactions for a team in a season.

    URL: /teams/{team_abbreviation}/{season_end_year}_transactions.html
    """
    return _run_endpoint(
        "team_transactions",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_splits(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Statistical splits for a team in a season.

    URL: /teams/{team_abbreviation}/{season_end_year}/splits/
    """
    return _run_endpoint(
        "team_splits",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_contracts(
    team_abbreviation: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Current player contracts for a team.

    URL: /contracts/{team_abbreviation}.html
    """
    return _run_endpoint(
        "team_contracts",
        {"team_abbreviation": team_abbreviation},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_lineups(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Five-man lineup statistics for a team in a season.

    URL: /teams/{team_abbreviation}/{season_end_year}/lineups/
    """
    return _run_endpoint(
        "team_lineups",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_starting_lineups(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Game-by-game starting lineups for a team in a season.

    URL: /teams/{team_abbreviation}/{season_end_year}_start.html
    """
    return _run_endpoint(
        "team_starting_lineups",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_on_off(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """On/off court statistics for a team in a season.

    URL: /teams/{team_abbreviation}/{season_end_year}/on-off/
    """
    return _run_endpoint(
        "team_on_off",
        {"team_abbreviation": team_abbreviation, "season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def franchise_history(
    team_abbreviation: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Season-by-season franchise history for a team.

    URL: /teams/{team_abbreviation}/
    """
    return _run_endpoint(
        "franchise_history",
        {"team_abbreviation": team_abbreviation},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )
