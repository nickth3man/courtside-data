"""Command-line interface, generated from the ENDPOINTS registry.

Every registry endpoint becomes a subcommand whose options mirror its call
parameters::

    courtside-data league_per_game_stats --season-end-year 2024
    courtside-data team_roster --team-abbreviation BOS --season-end-year 2024 \\
        --output-type csv --output-file roster.csv
    courtside-data list

Results print as JSON to stdout unless ``--output-file`` is given.

When stdout is a TTY, the ``list`` subcommand renders a :mod:`rich.table.Table`
and ``--debug`` envelopes render with :class:`rich.json.JSON` for nicer human
readability. Piped / non-TTY output stays plain so scripts, ``--output-file``
paths, and existing test fixtures are unaffected. ``rich`` is imported lazily
inside the rendering helpers so non-TTY command output keeps minimal imports.
"""

from __future__ import annotations

import argparse
import json
import sys

from courtside_data import client
from courtside_data.domain import OutputType, OutputWriteOption, Team
from courtside_data.endpoints import ENDPOINTS

_INT_PARAMS = {"season_end_year", "day", "month", "year"}
_FLAG_PARAMS = {"include_inactive_games", "include_combined_values"}


def _print_endpoint_list_rich() -> None:
    """Render the ``list`` subcommand output as a :class:`rich.table.Table`."""
    from rich.console import Console
    from rich.table import Table

    table = Table(
        title="courtside-data endpoints",
        header_style="bold",
        show_lines=False,
    )
    table.add_column("endpoint", style="cyan", no_wrap=True)
    table.add_column("params", style="white")
    for name, endpoint in ENDPOINTS.items():
        params = ", ".join(endpoint.params)
        table.add_row(name, params)
    Console().print(table)


def _print_debug_envelope_rich(envelope_text: str) -> None:
    """Render a debug envelope with :class:`rich.json.JSON`.

    The caller already serialized the envelope to a JSON string via the
    project's output writers — we parse it back into a Python object so
    ``rich.json.JSON`` can pretty-print and syntax-highlight it.
    """
    from rich.console import Console
    from rich.json import JSON

    payload = json.loads(envelope_text)
    Console().print(JSON.from_data(payload, indent=2, highlight=True))


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
        flag = f"--{param.replace('_', '-')}"
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="return a structured debug trace with the result and save it under ./logs "
        "(override the directory with COURTSIDE_DEBUG_LOG_DIR)",
    )


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

    is_tty = sys.stdout.isatty()
    use_rich = is_tty

    if args.endpoint == "list":
        if use_rich:
            _print_endpoint_list_rich()
        else:
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
    if args.debug and output_type == OutputType.CSV:
        parser.error("--debug requires JSON output")

    endpoint_options = {
        "output_type": output_type,
        "output_file_path": args.output_file,
        "output_write_option": OutputWriteOption.APPEND if args.append else None,
    }
    if args.debug:
        endpoint_options["debug"] = True

    result = func(
        **call_params,
        **endpoint_options,
    )
    if args.output_file:
        print(f"Wrote {args.output_file}")
    elif result is not None:
        if args.debug and use_rich:
            _print_debug_envelope_rich(result)
        else:
            print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
