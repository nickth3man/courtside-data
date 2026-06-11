"""Public client functions for every Basketball Reference endpoint.

Each function is an explicit, typed ``def`` (so static typing, IDE
auto-complete, and grep all work) whose body is a thin call into
:func:`_run_endpoint`. All endpoint *metadata* — URL path, table location,
CSV columns, and HTTP-status-to-domain-error mapping — lives in the
:data:`courtside_data.endpoints.ENDPOINTS` registry, which is the single
source of truth. A drift test asserts every function signature matches its
registry entry.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import httpx

from courtside_data.data import OutputType, OutputWriteOption, Team
from courtside_data.endpoints import ENDPOINTS
from courtside_data.http_service import HTTPService
from courtside_data.output.field_types import coerce_data
from courtside_data.output.fields import BasketballReferenceJSONEncoder, format_value
from courtside_data.output.service import OutputService
from courtside_data.output.type_validator import validate_rows
from courtside_data.output.writers import CSVWriter, FileOptions, JSONWriter, OutputOptions
from courtside_data.parser_service import ParserService


def _call_with_error_mapping(
    service_call: Callable[[], Any],
    error_mappings: dict[int, Callable[[], Exception]] | None,
) -> Any:
    """Invoke the service call, translating mapped HTTP status codes to domain errors."""
    try:
        return service_call()
    except httpx.HTTPStatusError as http_error:
        if error_mappings:
            factory = error_mappings.get(http_error.response.status_code)
            if factory:
                raise factory() from http_error
        raise


def _extract_rows(values: Any) -> list[dict[str, Any]] | None:
    """Pull the row list out of endpoint output (list[dict] or dict[str, list[dict]])."""
    if isinstance(values, list) and values and isinstance(values[0], dict):
        return values
    if isinstance(values, dict):
        for v in values.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return None


def _detect_csv_columns(rows: list[dict[str, Any]]) -> Sequence[str]:
    """Auto-detect CSV column names from row keys, stripping all-empty columns.

    Only used when an endpoint doesn't declare explicit column names; declared
    columns keep their contract even when empty.
    """
    column_names = list(rows[0].keys())
    non_empty = [k for k in column_names if any(row.get(k) not in (None, "", set(), []) for row in rows)]
    return non_empty or column_names


def _execute(
    service_call: Callable[[], Any],
    csv_column_names: Sequence[str] | None = None,
    error_mappings: dict[int, Callable[[], Exception]] | None = None,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    validate_output: bool = True,
) -> Any:
    values = _call_with_error_mapping(service_call, error_mappings)
    # Coerce raw string values to proper Python types (idempotent for endpoints
    # whose parser chains already produce typed values)
    values = coerce_data(values)

    if output_type == OutputType.CSV and csv_column_names is None:
        rows = _extract_rows(values)
        if rows is not None:
            csv_column_names = _detect_csv_columns(rows)

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


def _run_endpoint(
    name: str,
    params: dict[str, Any],
    *,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Execute the registry-described endpoint ``name`` with bound call params.

    The :data:`ENDPOINTS` entry supplies the metadata (service dispatch, CSV
    columns, error mapping); the caller supplies an explicit, typed signature.
    """
    endpoint = ENDPOINTS[name]

    def service_call() -> Any:
        service = HTTPService(parser=ParserService())
        if endpoint.custom:
            return getattr(service, name)(**params)
        return service.fetch_table(endpoint, **params)

    return _execute(
        service_call=service_call,
        csv_column_names=endpoint.csv_columns,
        error_mappings=endpoint.error_mappings(params),
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


# ── League-wide season tables ──────────────────────────────────────────────


def league_per_game_stats(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def league_per_36_minutes(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def league_totals(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def league_per_100_possessions(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def league_shooting(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def league_transactions(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def rookie_stats(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def standings(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def standings_by_date(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def attendance(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


# ── Playoffs ───────────────────────────────────────────────────────────────


def playoff_per_game(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def playoff_totals(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def playoff_bracket(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


# ── Draft, awards, leaders ─────────────────────────────────────────────────


def draft_picks(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def season_awards(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def season_leaders(
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def career_leaders(
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


# ── Player pages ───────────────────────────────────────────────────────────


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


# ── Team pages ─────────────────────────────────────────────────────────────


def team_roster(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_injury_report(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_and_opponent(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_misc_four_factors(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_opponent_stats(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_schedule(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_transactions(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_splits(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_contracts(
    team_abbreviation: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_lineups(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_starting_lineups(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_on_off(
    team_abbreviation: str,
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def franchise_history(
    team_abbreviation: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


# ── Box scores, schedule, play-by-play, search ─────────────────────────────


def player_box_scores(
    day: int,
    month: int,
    year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def team_box_scores(
    day: int,
    month: int,
    year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def regular_season_player_box_scores(
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def playoff_player_box_scores(
    player_identifier: str,
    season_end_year: int,
    include_inactive_games: bool = False,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def season_schedule(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def players_season_totals(
    season_end_year: int,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
) -> Any:
    """Season total statistics for all players (typed parser chain).

    URL: /leagues/NBA_{season_end_year}_totals.html
    """
    return _run_endpoint(
        "players_season_totals",
        {"season_end_year": season_end_year},
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )


def players_advanced_season_totals(
    season_end_year: int,
    include_combined_values: bool = False,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )


def search(
    term: str,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
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
    )
