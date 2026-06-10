import httpx

from courtside_data.data import OutputType
from courtside_data.errors import (
    InvalidDate,
    InvalidPlayer,
    InvalidPlayerAndSeason,
    InvalidSearch,
    InvalidSeason,
    InvalidTeam,
)
from courtside_data.http_service import HTTPService
from courtside_data.output.columns import (
    ATTENDANCE_COLUMN_NAMES,
    BOX_SCORE_COLUMN_NAMES,
    CAREER_LEADERS_COLUMN_NAMES,
    DRAFT_PICKS_COLUMN_NAMES,
    FRANCHISE_HISTORY_COLUMN_NAMES,
    LEAGUE_PER_36_COLUMN_NAMES,
    LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES,
    LEAGUE_PER_GAME_COLUMN_NAMES,
    LEAGUE_SHOOTING_COLUMN_NAMES,
    LEAGUE_TOTALS_COLUMN_NAMES,
    LEAGUE_TRANSACTIONS_COLUMN_NAMES,
    PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES,
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_ALL_STAR_COLUMN_NAMES,
    PLAYER_CAREER_STATS_COLUMN_NAMES,
    PLAYER_GAME_HIGHS_COLUMN_NAMES,
    PLAYER_ON_OFF_COLUMN_NAMES,
    PLAYER_PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_PLAYOFF_SERIES_COLUMN_NAMES,
    PLAYER_SALARIES_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SHOT_CHARTS_COLUMN_NAMES,
    PLAYER_SIMILARITY_SCORES_COLUMN_NAMES,
    PLAYER_SPLITS_COLUMN_NAMES,
    PLAYOFF_BRACKET_COLUMN_NAMES,
    PLAYOFF_PER_GAME_COLUMN_NAMES,
    PLAYOFF_TOTALS_COLUMN_NAMES,
    ROOKIE_STATS_COLUMN_NAMES,
    SCHEDULE_COLUMN_NAMES,
    SEASON_AWARDS_COLUMN_NAMES,
    SEASON_LEADERS_COLUMN_NAMES,
    STANDINGS_BY_DATE_COLUMN_NAMES,
    STANDINGS_COLUMNS_NAMES,
    TEAM_AND_OPPONENT_COLUMN_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
    TEAM_CONTRACTS_COLUMN_NAMES,
    TEAM_INJURY_REPORT_COLUMN_NAMES,
    TEAM_LINEUPS_COLUMN_NAMES,
    TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES,
    TEAM_ON_OFF_COLUMN_NAMES,
    TEAM_OPPONENT_STATS_COLUMN_NAMES,
    TEAM_ROSTER_COLUMN_NAMES,
    TEAM_SCHEDULE_COLUMN_NAMES,
    TEAM_SPLITS_COLUMN_NAMES,
    TEAM_STARTING_LINEUPS_COLUMN_NAMES,
    TEAM_TRANSACTIONS_COLUMN_NAMES,
)
from courtside_data.output.field_types import coerce_data
from courtside_data.output.fields import BasketballReferenceJSONEncoder, format_value
from courtside_data.output.service import OutputService
from courtside_data.output.type_validator import validate_rows
from courtside_data.output.writers import CSVWriter, FileOptions, JSONWriter, OutputOptions
from courtside_data.parser_service import ParserService


def _execute(
    service_call,
    csv_column_names=None,
    error_mappings=None,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
    validate_output=False,
):
    try:
        values = service_call()
    except httpx.HTTPStatusError as http_error:
        if error_mappings:
            factory = error_mappings.get(http_error.response.status_code)
            if factory:
                raise factory() from http_error
        raise http_error
    # Coerce raw string values to proper Python types (idempotent for legacy endpoints)
    values = coerce_data(values)
    # Extract rows and auto-detect column names for CSV output
    if output_type == OutputType.CSV:
        rows = None
        if isinstance(values, list) and values and isinstance(values[0], dict):
            rows = values
        elif isinstance(values, dict):
            for v in values.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    rows = v
                    break
        if rows is not None:
            if csv_column_names is None:
                csv_column_names = list(rows[0].keys())
                # Only filter empty columns in auto-detection mode.
                # Endpoints with explicit column names keep their contract.
                non_empty = [
                    k for k in csv_column_names if any(row.get(k) not in (None, "", set(), []) for row in rows)
                ]
                if non_empty:
                    csv_column_names = non_empty
    # Validate coerced types if requested
    if validate_output and isinstance(values, list) and values and isinstance(values[0], dict):
        report = validate_rows(values, expected_columns=csv_column_names)
        if not report.ok:
            raise ValueError(str(report))
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": csv_column_names},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def standings(season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).standings(season_end_year=season_end_year),
        csv_column_names=STANDINGS_COLUMNS_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_box_scores(
    day, month, year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_box_scores(day=day, month=month, year=year),
        csv_column_names=BOX_SCORE_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidDate(day=day, month=month, year=year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def regular_season_player_box_scores(
    player_identifier,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
    include_inactive_games=False,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).regular_season_player_box_scores(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        ),
        csv_column_names=PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
        error_mappings={
            httpx.codes.INTERNAL_SERVER_ERROR: lambda: InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            ),
            httpx.codes.NOT_FOUND: lambda: InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            ),
        },
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def playoff_player_box_scores(
    player_identifier,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
    include_inactive_games=False,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).playoff_player_box_scores(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        ),
        csv_column_names=PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
        error_mappings={
            httpx.codes.INTERNAL_SERVER_ERROR: lambda: InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            ),
            httpx.codes.NOT_FOUND: lambda: InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            ),
        },
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def season_schedule(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).season_schedule(season_end_year=season_end_year),
        csv_column_names=SCHEDULE_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def players_season_totals(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).players_season_totals(season_end_year=season_end_year),
        csv_column_names=PLAYER_SEASON_TOTALS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def players_advanced_season_totals(
    season_end_year,
    include_combined_values=False,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).players_advanced_season_totals(
            season_end_year, include_combined_values=include_combined_values
        ),
        csv_column_names=PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_box_scores(
    day, month, year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_box_scores(day=day, month=month, year=year),
        csv_column_names=TEAM_BOX_SCORES_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidDate(day=day, month=month, year=year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def play_by_play(
    home_team, day, month, year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).play_by_play(
            home_team=home_team, day=day, month=month, year=year
        ),
        csv_column_names=PLAY_BY_PLAY_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidDate(day=day, month=month, year=year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def search(term, output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).search(term=term),
        # csv_column_names omitted — auto-detected from data so empty columns are stripped
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSearch(term=term)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_roster(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """Fetch team roster data from Basketball Reference.

    Status: Beta - This endpoint is under active development.
    URL: /teams/{team_abbreviation}/{season_end_year}.html
    Table: #roster

    Args:
        team_abbreviation: Team abbreviation (e.g., "BOS" for Boston Celtics)
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Team roster data including player names, numbers, positions, etc.
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_roster(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_ROSTER_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_injury_report(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """Fetch team injury report data from Basketball Reference.

    Status: Beta - This endpoint is under active development.
    URL: /friv/injuries.fcgi
    Table: #injuries

    Args:
        team_abbreviation: Team abbreviation (e.g., "BOS" for Boston Celtics)
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Team injury report data
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_injury_report(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_INJURY_REPORT_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_and_opponent(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """Fetch team and opponent statistics from Basketball Reference.

    Status: Beta - This endpoint is under active development.
    URL: /teams/{team_abbreviation}/{season_end_year}.html
    Table: #team_and_opponent

    Args:
        team_abbreviation: Team abbreviation (e.g., "BOS" for Boston Celtics)
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Team and opponent statistics
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_and_opponent(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_AND_OPPONENT_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_misc_four_factors(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """Fetch team miscellaneous and four factors statistics from Basketball Reference.

    Status: Beta - This endpoint is under active development.
    URL: /teams/{team_abbreviation}/{season_end_year}.html
    Table: #team_misc

    Args:
        team_abbreviation: Team abbreviation (e.g., "BOS" for Boston Celtics)
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Team miscellaneous and four factors statistics
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_misc_four_factors(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def league_per_game_stats(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch league-wide per-game statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_per_game.html
    Table: #per_game_stats

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Per-game statistics for all players in the season
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).league_per_game_stats(season_end_year=season_end_year),
        csv_column_names=LEAGUE_PER_GAME_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def league_per_36_minutes(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch league-wide per-36-minutes statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_per_minute.html
    Table: #per_minute_stats

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Per-36-minutes statistics for all players in the season
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).league_per_36_minutes(season_end_year=season_end_year),
        csv_column_names=LEAGUE_PER_36_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def league_totals(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch league-wide total statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_totals.html
    Table: #totals_stats

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Total statistics for all players in the season
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).league_totals(season_end_year=season_end_year),
        csv_column_names=LEAGUE_TOTALS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def rookie_stats(season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    """Fetch rookie statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_rookies.html
    Table: #rookies

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Rookie statistics for the season
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).rookie_stats(season_end_year=season_end_year),
        csv_column_names=ROOKIE_STATS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def standings_by_date(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch standings by date for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_standings_by_date_{conference}.html
    Table: #standings_by_date

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Standings data organized by date and conference
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).standings_by_date(season_end_year=season_end_year),
        csv_column_names=STANDINGS_BY_DATE_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def attendance(season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    """Fetch NBA attendance data for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}.html
    Table: #advanced-team

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Attendance data including arena names and attendance figures
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).attendance(season_end_year=season_end_year),
        csv_column_names=ATTENDANCE_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def league_transactions(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch league-wide transactions for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_transactions.html
    Table: #transactions

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: League transaction data
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).league_transactions(season_end_year=season_end_year),
        csv_column_names=LEAGUE_TRANSACTIONS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def league_per_100_possessions(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch league-wide per-100-possessions statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_per_poss.html
    Table: #per_poss

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Per-100-possessions statistics for all players in the season
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).league_per_100_possessions(
            season_end_year=season_end_year
        ),
        csv_column_names=LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def league_shooting(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch league-wide shooting statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_shooting.html
    Table: #shooting

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Shooting statistics for all players in the season
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).league_shooting(season_end_year=season_end_year),
        csv_column_names=LEAGUE_SHOOTING_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def playoff_per_game(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch playoff per-game statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_per_game.html
    Table: #per_game_stats_post

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Playoff per-game statistics for all players
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).playoff_per_game(season_end_year=season_end_year),
        csv_column_names=PLAYOFF_PER_GAME_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def playoff_totals(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch playoff total statistics for a season.

    Status: Beta - This endpoint is under active development.
    URL: /leagues/NBA_{season_end_year}_totals.html
    Table: #totals_stats_post

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Playoff total statistics for all players
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).playoff_totals(season_end_year=season_end_year),
        csv_column_names=PLAYOFF_TOTALS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def draft_picks(season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    """Fetch NBA draft picks for a season.

    Status: Beta - This endpoint is under active development.
    URL: /draft/NBA_{season_end_year}.html
    Table: #stats

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Draft pick data including round, pick number, team, and player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).draft_picks(season_end_year=season_end_year),
        csv_column_names=DRAFT_PICKS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def season_leaders(output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    """Fetch per-season statistical leaders from Basketball Reference.

    Status: Beta - This endpoint is under active development.
    URL: /leaders/per_season.html
    Table: #stats_TOT

    Args:
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Per-season statistical leaders
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).season_leaders(),
        csv_column_names=SEASON_LEADERS_COLUMN_NAMES,
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def career_leaders(output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    """Fetch career statistical leaders from Basketball Reference.

    Status: Beta - This endpoint is under active development.
    URL: /leaders/
    Table: #leaders_index

    Args:
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Career statistical leaders
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).career_leaders(),
        csv_column_names=CAREER_LEADERS_COLUMN_NAMES,
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def playoff_bracket(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch NBA playoff bracket for a season.

    Status: Beta - This endpoint is under active development.
    URL: /playoffs/NBA_{season_end_year}.html
    Table: #all_playoffs

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Playoff bracket data with series matchups and results
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).playoff_bracket(season_end_year=season_end_year),
        csv_column_names=PLAYOFF_BRACKET_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def season_awards(
    season_end_year, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch NBA season awards data for a season.

    Status: Beta - This endpoint is under active development.
    URL: /awards/awards_{season_end_year}.html
    Table: #mvp

    Args:
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Season award voting results
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).season_awards(season_end_year=season_end_year),
        csv_column_names=SEASON_AWARDS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidSeason(season_end_year=season_end_year)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_career_stats(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch career statistics for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #per_game_stats

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Career per-game statistics for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_career_stats(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_CAREER_STATS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_playoff_series(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch playoff series statistics for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #playoffs_series

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Playoff series statistics for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_playoff_series(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_PLAYOFF_SERIES_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_splits(
    player_identifier,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """Fetch split statistics for a player in a season.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}/splits/{season_end_year}
    Table: #splits

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Split statistics (home/away, by month, etc.) for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_splits(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        ),
        csv_column_names=PLAYER_SPLITS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_on_off(
    player_identifier,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """Fetch on/off court statistics for a player in a season.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}/on-off/{season_end_year}
    Table: #on-off

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: On/off court statistics for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_on_off(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        ),
        csv_column_names=PLAYER_ON_OFF_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_shot_charts(
    player_identifier,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """Fetch shot chart data for a player in a season.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}/shooting/{season_end_year}
    Table: #shooting

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        season_end_year: The ending year of the NBA season (e.g., 2024 for 2023-24)
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Shot chart data for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_shot_charts(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        ),
        csv_column_names=PLAYER_SHOT_CHARTS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_adjusted_shooting(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch adjusted shooting statistics for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #adj_shooting

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Adjusted shooting statistics for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_adjusted_shooting(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_play_by_play(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch play-by-play statistics for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #pbp_stats

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Play-by-play statistics for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_play_by_play(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_PLAY_BY_PLAY_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_game_highs(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch career game highs for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #highs-reg-season

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Career game high statistics for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_game_highs(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_GAME_HIGHS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_all_star(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch All-Star game statistics for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #all_star

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: All-Star game statistics for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_all_star(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_ALL_STAR_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_similarity_scores(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch similarity scores for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #sims-career

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Similarity scores comparing the player to historical players
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_similarity_scores(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_SIMILARITY_SCORES_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def player_salaries(
    player_identifier, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    """Fetch salary data for a player.

    Status: Beta - This endpoint is under active development.
    URL: /players/{player_identifier}.html
    Table: #all_salaries

    Args:
        player_identifier: Basketball Reference player identifier (e.g., "westbru01")
        output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)
        output_file_path: Path to write output file
        output_write_option: File write mode
        json_options: JSON formatting options

    Returns:
        list[dict]: Salary data for the player
    """
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).player_salaries(
            player_identifier=player_identifier,
        ),
        csv_column_names=PLAYER_SALARIES_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidPlayer(player_identifier=player_identifier)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_schedule(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_schedule(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_SCHEDULE_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_transactions(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_transactions(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_TRANSACTIONS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_splits(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_splits(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_SPLITS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_contracts(
    team_abbreviation, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_contracts(
            team_abbreviation=team_abbreviation,
        ),
        csv_column_names=TEAM_CONTRACTS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_lineups(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_lineups(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_LINEUPS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_starting_lineups(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_starting_lineups(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_STARTING_LINEUPS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_on_off(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_on_off(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_ON_OFF_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def team_opponent_stats(
    team_abbreviation,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).team_opponent_stats(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        ),
        csv_column_names=TEAM_OPPONENT_STATS_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def franchise_history(
    team_abbreviation, output_type=None, output_file_path=None, output_write_option=None, json_options=None
):
    return _execute(
        service_call=lambda: HTTPService(parser=ParserService()).franchise_history(
            team_abbreviation=team_abbreviation,
        ),
        csv_column_names=FRANCHISE_HISTORY_COLUMN_NAMES,
        error_mappings={httpx.codes.NOT_FOUND: lambda: InvalidTeam(team_abbreviation=team_abbreviation)},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )
