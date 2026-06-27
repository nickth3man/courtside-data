"""Game-level and search endpoints backed by bespoke HTTPService methods:
box scores, schedules, play-by-play, season totals, and player search."""

from __future__ import annotations

from typing import Any

from courtside_data.client._runner import _run_endpoint
from courtside_data.domain import OutputType, OutputWriteOption, Team


def box_score_player_basic(
    game_id: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Per-player basic box-score rows for one game.

    URL: /boxscores/{game_id}.html
    """
    return _run_endpoint(
        "box_score_player_basic",
        {"game_id": game_id},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def box_score_player_advanced(
    game_id: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Per-player advanced box-score rows for one game.

    URL: /boxscores/{game_id}.html
    """
    return _run_endpoint(
        "box_score_player_advanced",
        {"game_id": game_id},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def box_score_game_info(
    game_id: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Game-level metadata for one box-score page.

    URL: /boxscores/{game_id}.html
    """
    return _run_endpoint(
        "box_score_game_info",
        {"game_id": game_id},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def box_score_line_score(
    game_id: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Per-team line-score rows for one game.

    URL: /boxscores/{game_id}.html
    """
    return _run_endpoint(
        "box_score_line_score",
        {"game_id": game_id},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def box_score_player_quarter_splits(
    game_id: str,
    period: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Per-player period-split box-score rows for one game.

    URL: /boxscores/{game_id}.html
    """
    return _run_endpoint(
        "box_score_player_quarter_splits",
        {"game_id": game_id, "period": period},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def box_score_team_four_factors(
    game_id: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Per-team Four Factors rows for one game.

    URL: /boxscores/{game_id}.html
    """
    return _run_endpoint(
        "box_score_team_four_factors",
        {"game_id": game_id},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def player_box_scores(
    day: int,
    month: int,
    year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Player box scores for all games on a date.

    URL: /friv/dailyleaders.cgi?month={month}&day={day}&year={year}
    """
    return _run_endpoint(
        "player_box_scores",
        {"day": day, "month": month, "year": year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def team_box_scores(
    day: int,
    month: int,
    year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Team box scores for all games on a date.

    URL: /boxscores/?month={month}&day={day}&year={year}
    """
    return _run_endpoint(
        "team_box_scores",
        {"day": day, "month": month, "year": year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def play_by_play(
    home_team: Team,
    day: int,
    month: int,
    year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Play-by-play events for the game hosted by ``home_team`` on a date.

    URL: /boxscores/pbp/
    """
    return _run_endpoint(
        "play_by_play",
        {"home_team": home_team, "day": day, "month": month, "year": year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def regular_season_player_box_scores(
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Game-by-game regular season box scores for a player in a season.

    URL: /players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}
    """
    return _run_endpoint(
        "regular_season_player_box_scores",
        {
            "player_identifier": player_identifier,
            "season_end_year": season_end_year,
            "include_inactive_games": include_inactive_games,
        },
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def playoff_player_box_scores(
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Game-by-game playoff box scores for a player in a season.

    URL: /players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}
    """
    return _run_endpoint(
        "playoff_player_box_scores",
        {
            "player_identifier": player_identifier,
            "season_end_year": season_end_year,
            "include_inactive_games": include_inactive_games,
        },
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def season_schedule(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Full season schedule and results (all months).

    URL: /leagues/NBA_{season_end_year}_games.html
    """
    return _run_endpoint(
        "season_schedule",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def players_season_totals(
    season_end_year: int,
    include_combined_values: bool = False,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Season total statistics for all players (typed parser chain).

    URL: /leagues/NBA_{season_end_year}_totals.html
    """
    return _run_endpoint(
        "players_season_totals",
        {"season_end_year": season_end_year, "include_combined_values": include_combined_values},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def players_advanced_season_totals(
    season_end_year: int,
    include_combined_values: bool = False,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Advanced season statistics for all players.

    URL: /leagues/NBA_{season_end_year}_advanced.html
    """
    return _run_endpoint(
        "players_advanced_season_totals",
        {"season_end_year": season_end_year, "include_combined_values": include_combined_values},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )


def search(
    term: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    raw: bool = False,
    debug: bool = False,
) -> Any:
    """Search Basketball Reference for players matching a term.

    URL: /search/search.fcgi?search={term}
    """
    return _run_endpoint(
        "search",
        {"term": term},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
        raw=raw,
        debug=debug,
    )
