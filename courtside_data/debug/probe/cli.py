"""Command-line entry point for the endpoint probe.

Builds the argument parser and wires parsed args into :func:`probe_endpoints`,
printing a small JSON summary and returning a shell exit code.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from courtside_data.debug.probe.runner import probe_endpoints


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe every courtside-data endpoint live and write a report.")
    parser.add_argument(
        "--endpoint",
        "-e",
        action="append",
        dest="endpoints",
        metavar="NAME",
        help="Probe only this endpoint (repeatable). Default: all registry endpoints.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Summary report path (default: <debug log dir>/endpoint_probe_report_<timestamp>.json)",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=None,
        help="Optional CSV report path. When omitted, only the JSON report is written.",
    )
    parser.add_argument(
        "--resume-from",
        type=Path,
        default=None,
        help="Resume a partial probe CSV/JSON report and skip endpoints already marked ok.",
    )
    parser.add_argument(
        "--debug-detail-level",
        choices=("summary", "normal", "full"),
        default=None,
        help="Trace artifact detail level (sets COURTSIDE_DEBUG_DETAIL_LEVEL).",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Enable hishel HTTP caching for repeated probe debugging runs.",
    )
    parser.add_argument(
        "--params-json",
        default=None,
        help="JSON object of endpoint params. Requires exactly one --endpoint and only affects this probe run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    params_override = None
    if args.params_json is not None:
        try:
            loaded = orjson.loads(args.params_json)
        except orjson.JSONDecodeError as exc:
            print(f"Invalid --params-json: {exc}", file=sys.stderr)
            return 2
        if not isinstance(loaded, dict):
            print("--params-json must decode to a JSON object.", file=sys.stderr)
            return 2
        params_override = dict(loaded)
    try:
        report = probe_endpoints(
            endpoints=args.endpoints,
            output_path=args.output,
            csv_output_path=args.csv_output,
            resume_from=args.resume_from,
            debug_detail_level=args.debug_detail_level,
            use_cache=args.use_cache,
            params_override=params_override,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    summary_keys = ("report_path", "csv_report_path", "ok_count", "failed_count", "failed_endpoints")
    summary = {key: report[key] for key in summary_keys if key in report}
    print(orjson.dumps(summary, option=orjson.OPT_INDENT_2).decode("utf-8"))
    return 0 if report["failed_count"] == 0 and not report["missing_sample_params"] else 1
