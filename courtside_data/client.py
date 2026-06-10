from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from typing import Any

import httpx

from courtside_data.data import OutputType, OutputWriteOption
from courtside_data.endpoints import ENDPOINTS, TableEndpoint
from courtside_data.errors import (
    InvalidDate,
    InvalidPlayerAndSeason,
    InvalidSearch,
    InvalidSeason,
)
from courtside_data.http_service import HTTPService
from courtside_data.output.columns import (
    BOX_SCORE_COLUMN_NAMES,
    PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    SCHEDULE_COLUMN_NAMES,
    STANDINGS_COLUMNS_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
)
from courtside_data.output.field_types import coerce_data
from courtside_data.output.fields import BasketballReferenceJSONEncoder, format_value
from courtside_data.output.service import OutputService
from courtside_data.output.type_validator import validate_rows
from courtside_data.output.writers import CSVWriter, FileOptions, JSONWriter, OutputOptions
from courtside_data.parser_service import ParserService


def _execute(
    service_call: Callable[[], Any],
    csv_column_names: Sequence[str] | None = None,
    error_mappings: dict[int, Callable[[], Exception]] | None = None,
    output_type: OutputType | None = None,
    output_file_path: str | None = None,
    output_write_option: OutputWriteOption | None = None,
    json_options: dict[str, Any] | None = None,
    validate_output: bool = False,
) -> Any:
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


# ── Legacy / public API functions (kept exactly as-is) ────────────────────


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


# ── Beta endpoint function generation ─────────────────────────────────────


def _compute_params(name: str, endpoint: TableEndpoint) -> list[str]:
    """Return the ordered parameter names for the given endpoint.

    Custom endpoints take theirs from the bespoke ``HTTPService`` method
    signature; generic endpoints declare them in ``endpoint.params``.
    """
    if endpoint.custom:
        # Use the explicit method signature on HTTPService (skip ``self``).
        sig = inspect.signature(getattr(HTTPService, name))
        return [p for p in sig.parameters if p != "self"]
    return list(endpoint.params)


def _make_beta_function(name: str, endpoint: TableEndpoint, param_names: list[str]) -> Callable[..., Any]:
    """Generate a beta endpoint client function with the proper signature.

    The generated function:

    * Accepts the endpoint-specific parameters + the standard output parameters.
    * Calls ``_execute`` with a ``service_call`` lambda that invokes the
      corresponding ``HTTPService`` method by name.
    * Passes ``endpoint.csv_columns`` and ``endpoint.error_mappings(params)``
      to ``_execute``.
    """
    all_params = list(param_names) + [
        "output_type=None",
        "output_file_path=None",
        "output_write_option=None",
        "json_options=None",
    ]
    params_str = ", ".join(all_params)

    # Build the ``params`` dict literal and the service-call keyword arguments
    params_dict_entries = ", ".join(f'"{p}": {p}' for p in param_names)
    service_args = ", ".join(f"{p}={p}" for p in param_names)

    # Build docstring from endpoint metadata
    table = endpoint.table_id or endpoint.commented_table_id or "(auto)"
    doc_lines = [
        f"Fetch {name.replace('_', ' ')} data from Basketball Reference.",
        "",
        "Status: Beta - This endpoint is under active development.",
        f"URL: {endpoint.path}",
        f"Table: #{table}",
        "",
        "Args:",
        *(f"    {p}: Endpoint-specific parameter" for p in param_names),
        "    output_type: Output format (None for dict, OutputType.CSV, OutputType.JSON)",
        "    output_file_path: Path to write output file",
        "    output_write_option: File write mode",
        "    json_options: JSON formatting options",
        "",
    ]
    doc = "\n    ".join(doc_lines)

    source = f'''def {name}({params_str}):
    """{doc}"""
    endpoint = ENDPOINTS["{name}"]
    params = {{{params_dict_entries}}}
    return _execute(
        service_call=lambda: getattr(HTTPService(parser=ParserService()), "{name}")({service_args}),
        csv_column_names=endpoint.csv_columns,
        error_mappings=endpoint.error_mappings(params),
        output_type=output_type,
        output_file_path=output_file_path,
        output_write_option=output_write_option,
        json_options=json_options,
    )
'''

    namespace: dict[str, Callable[..., Any]] = {}
    exec(source, globals(), namespace)
    return namespace[name]


# ── Register all beta endpoints at import time ─────────────────────────────

for _name in ENDPOINTS:
    _endpoint: TableEndpoint = ENDPOINTS[_name]
    _param_names: list[str] = _compute_params(_name, _endpoint)
    globals()[_name] = _make_beta_function(_name, _endpoint, _param_names)
