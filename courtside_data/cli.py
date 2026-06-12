"""Command-line interface, generated from the ENDPOINTS registry.

Every registry endpoint becomes a subcommand whose options mirror its call
parameters::

    courtside-data league_per_game_stats --season-end-year 2024
    courtside-data team_roster --team-abbreviation BOS --season-end-year 2024 \\
        --output-type csv --output-file roster.csv
    courtside-data list

Results print as JSON to stdout unless ``--output-file`` is given.
"""

from __future__ import annotations

import argparse

from courtside_data import client
from courtside_data.data import OutputType, OutputWriteOption, Team
from courtside_data.endpoints import ENDPOINTS

_INT_PARAMS = {"season_end_year", "day", "month", "year"}
_FLAG_PARAMS = {"include_inactive_games", "include_combined_values"}


def _team_value(value: str) -> Team:
    normalized = value.strip().upper().replace("-", " ").replace("_", " ")
    try:
        return Team(normalized)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"unknown team {value!r}; expected a full team name like 'BOSTON CELTICS'"
        ) from None


def _add_endpoint_parser(subparsers: argparse._SubParsersAction, name: str, endpoint) -> None:
    doc = (getattr(client, name).__doc__ or "").strip().splitlines()
    summary = doc[0] if doc else name
    parser = subparsers.add_parser(name, help=summary, description=summary)
    for param in endpoint.params:
        flag = "--" + param.replace("_", "-")
        if param in _FLAG_PARAMS:
            parser.add_argument(flag, action="store_true")
        elif param in _INT_PARAMS:
            parser.add_argument(flag, type=int, required=True)
        elif param == "home_team":
            parser.add_argument(flag, type=_team_value, required=True, metavar="TEAM")
        else:
            parser.add_argument(flag, required=True)
    parser.add_argument("--output-type", choices=["json", "csv"], default="json")
    parser.add_argument("--output-file", default=None, help="write to this file instead of stdout")
    parser.add_argument("--append", action="store_true", help="append to the output file instead of overwriting")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="courtside-data",
        description="Fetch Basketball Reference data from the command line.",
    )
    subparsers = parser.add_subparsers(dest="endpoint", required=True, metavar="endpoint")
    subparsers.add_parser("list", help="list every available endpoint and its parameters")
    for name, endpoint in ENDPOINTS.items():
        _add_endpoint_parser(subparsers, name, endpoint)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.endpoint == "list":
        for name, endpoint in ENDPOINTS.items():
            params = ", ".join(endpoint.params)
            print(f"{name}({params})")
        return 0

    endpoint = ENDPOINTS[args.endpoint]
    func = getattr(client, args.endpoint)
    call_params = {param: getattr(args, param) for param in endpoint.params}

    output_type = OutputType.CSV if args.output_type == "csv" else OutputType.JSON
    if output_type == OutputType.CSV and not args.output_file:
        parser.error("--output-type csv requires --output-file")

    result = func(
        **call_params,
        output_type=output_type,
        output_file_path=args.output_file,
        output_write_option=OutputWriteOption.APPEND if args.append else None,
    )
    if args.output_file:
        print(f"Wrote {args.output_file}")
    elif result is not None:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
