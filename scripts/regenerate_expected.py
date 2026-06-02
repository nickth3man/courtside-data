#!/usr/bin/env python3
"""Regenerate expected output snapshots for integration tests.

Usage:
    scripts/regenerate_expected.py --module players_season_totals --year 2018          # dry-run (default)
    scripts/regenerate_expected.py --module players_season_totals --year 2018 --apply  # actually copy
    scripts/regenerate_expected.py --module players_season_totals --year 2018 --format json
    scripts/regenerate_expected.py --all --apply                                       # regenerate everything

The script runs the pytest snapshot test node-id with BR_REGEN=1 (which prevents the
test's tearDown from deleting the generated file), then diffs or copies the generated
output onto the expected snapshot.  A tripwire assertion (the in-memory test_length)
is always run first to protect against silently capturing a parser regression.
"""

import argparse
import difflib
import filecmp
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure stdout can handle Unicode characters (e.g. accented player names)
if sys.stdout.encoding and sys.stdout.encoding.upper() != "UTF-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass  # Python < 3.7, fall back to default

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Tripwire lengths – source of truth: the test_length assertions in each
# tests/integration/client/test_<module>.py file.
# Keys are (module_name, year_or_date).  If a year is not listed the tripwire
# is skipped (a warning is printed).
# ---------------------------------------------------------------------------
TRIPWIRE_LENGTHS: dict[tuple[str, int], int] = {
    # players_season_totals – Test{year}InMemoryTotals::test_length
    ("players_season_totals", 2001): 490,
    ("players_season_totals", 2002): 470,
    ("players_season_totals", 2003): 456,
    ("players_season_totals", 2004): 517,
    ("players_season_totals", 2005): 526,
    ("players_season_totals", 2006): 512,
    ("players_season_totals", 2007): 487,
    ("players_season_totals", 2008): 527,
    ("players_season_totals", 2009): 515,
    ("players_season_totals", 2010): 512,
    ("players_season_totals", 2011): 542,
    ("players_season_totals", 2012): 515,
    ("players_season_totals", 2013): 523,
    ("players_season_totals", 2014): 548,
    ("players_season_totals", 2015): 575,
    ("players_season_totals", 2016): 528,
    ("players_season_totals", 2017): 542,
    ("players_season_totals", 2018): 605,
    ("players_season_totals", 2019): 622,
    # season_schedule – TestSeasonScheduleInMemoryOutput::test_2018_season_schedule_length
    ("season_schedule", 2018): 1416,
    # standings – Test{year}StandingsInMemory::test_{year}_standings
    ("standings", 2000): 29,
    ("standings", 2001): 29,
    ("standings", 2002): 29,
    ("standings", 2005): 30,
    ("standings", 2020): 30,
    # team_box_scores – Test20010101TeamBoxScoresInMemoryOutput::test_length
    ("team_box_scores", 2001): 4,
    # player_box_scores – Test20010101::test_2001_01_01_player_box_scores_length
    ("player_box_scores", 2001): 39,
    ("player_box_scores", 2018): 82,
    # player_advanced_season_totals
    ("player_advanced_season_totals", 2018): 605,
    ("player_advanced_season_totals", 2019): 622,
}


@dataclass(frozen=True)
class ModuleSnapshotInfo:
    """Metadata about a snapshot-testing module."""
    years: list[int]
    formats: list[str]
    test_file: str
    expected_dir: str
    generated_dir: str
    # (year, fmt) -> pytest node-id string for the snapshot test
    snapshot_node: Callable[[int, str], str | None]
    # (year) -> pytest node-id string for the length tripwire
    tripwire_node: Callable[[int], str | None] = field(default=lambda y: None)


def _make_players_node(year, fmt):
    cls_name = f"Test{year}PlayerSeason{fmt.upper()}Totals"
    test_name = f"test_{year}_{fmt}_output"
    return f"tests/integration/client/test_players_season_totals.py::{cls_name}::{test_name}"


def _make_players_tripwire(year):
    return f"tests/integration/client/test_players_season_totals.py::Test{year}InMemoryTotals::test_length"


def _make_schedule_node(year, fmt):
    if year == 2001:
        cls_name_csv = "Test2001SeasonScheduleCsvOutput"
        cls_name_json = "Test2018SeasonScheduleJsonOutput"  # NB: class name says 2018 but mock uses 2001
    else:  # 2018
        cls_name_csv = "Test2018SeasonScheduleCsvOutput"
        cls_name_json = "Test2018SeasonScheduleJsonOutput"
    cls_name = cls_name_csv if fmt == "csv" else cls_name_json
    test_name = "test_output" if fmt == "csv" else "test_file_output"
    return f"tests/integration/client/test_season_schedule.py::{cls_name}::{test_name}"


def _make_schedule_tripwire(year):
    if year == 2018:
        return "tests/integration/client/test_season_schedule.py::TestSeasonScheduleInMemoryOutput::test_2018_season_schedule_length"
    return None


def _make_standings_node(year, fmt):
    if year == 2001:
        cls_csv = "TestCSVStandingsFor2001"
        cls_json = "TestJSONPlayerBoxScores2001"
    else:  # 2019
        cls_csv = "TestCSVStandingsFor2019"
        cls_json = "TestJSONPlayerBoxScores2019"
    cls_name = cls_csv if fmt == "csv" else cls_json
    return f"tests/integration/client/test_standings.py::{cls_name}::test_{year}_standings"


def _make_standings_tripwire(year):
    return f"tests/integration/client/test_standings.py::Test{year}StandingsInMemory::test_{year}_standings"


def _make_team_box_node(year, fmt):
    cls_name = "TestTeamBoxScoresCSVOutput" if fmt == "csv" else "TestTeamBoxScoresJSONOutput"
    test_name = "test_output"
    return f"tests/integration/client/test_team_box_scores.py::{cls_name}::{test_name}"


def _make_team_box_tripwire(year):
    if year == 2001:
        return "tests/integration/client/test_team_box_scores.py::Test20010101TeamBoxScoresInMemoryOutput::test_length"
    return None


def _make_player_box_node(year, fmt):
    # Player box scores only have snapshot tests for 2001-01-01
    if year == 2001:
        test_name = f"test_{fmt}_output"
        return f"tests/integration/client/test_player_box_scores.py::Test20010101::{test_name}"
    return None


def _make_player_box_tripwire(year):
    if year == 2001:
        return "tests/integration/client/test_player_box_scores.py::Test20010101::test_2001_01_01_player_box_scores_length"
    if year == 2018:
        return "tests/integration/client/test_player_box_scores.py::Test20180101::test_player_box_scores_length"
    return None


def _make_advanced_node(year, fmt):
    cls_name = f"Test{year}PlayerAdvancedSeasonTotals{fmt.upper()}Output"
    return f"tests/integration/client/test_players_advanced_season_totals.py::{cls_name}::test_players_advanced_season_totals_{fmt}"


def _make_advanced_tripwire(year):
    if year == 2018:
        return "tests/integration/client/test_players_advanced_season_totals.py::TestPlayerAdvancedSeasonTotalsInMemoryOutput::test_2018_players_advanced_season_totals_length"
    if year == 2019:
        return "tests/integration/client/test_players_advanced_season_totals.py::Test2019::test_length"
    return None


SNAPSHOT_MODULES: dict[str, ModuleSnapshotInfo] = {
    "players_season_totals": ModuleSnapshotInfo(
        years=list(range(2001, 2019)),
        formats=["json", "csv"],
        test_file="tests/integration/client/test_players_season_totals.py",
        expected_dir="tests/integration/client/output/expected/players_season_totals",
        generated_dir="tests/integration/client/output/generated/players_season_totals",
        snapshot_node=_make_players_node,
        tripwire_node=_make_players_tripwire,
    ),
    "season_schedule": ModuleSnapshotInfo(
        years=[2001, 2018],
        formats=["json", "csv"],
        test_file="tests/integration/client/test_season_schedule.py",
        expected_dir="tests/integration/client/output/expected/season_schedule",
        generated_dir="tests/integration/client/output/generated/season_schedule",
        snapshot_node=_make_schedule_node,
        tripwire_node=_make_schedule_tripwire,
    ),
    "standings": ModuleSnapshotInfo(
        years=[2001, 2019],
        formats=["json", "csv"],
        test_file="tests/integration/client/test_standings.py",
        expected_dir="tests/integration/client/output/expected/standings",
        generated_dir="tests/integration/client/output/generated/standings",
        snapshot_node=_make_standings_node,
        tripwire_node=_make_standings_tripwire,
    ),
    "team_box_scores": ModuleSnapshotInfo(
        years=[2018],
        formats=["json", "csv"],
        test_file="tests/integration/client/test_team_box_scores.py",
        expected_dir="tests/integration/client/output/expected/team_box_scores",
        generated_dir="tests/integration/client/output/generated/team_box_scores",
        snapshot_node=_make_team_box_node,
        tripwire_node=_make_team_box_tripwire,
    ),
    "player_box_scores": ModuleSnapshotInfo(
        years=[2001],
        formats=["json", "csv"],
        test_file="tests/integration/client/test_player_box_scores.py",
        expected_dir="tests/integration/client/output/expected/player_box_scores",
        generated_dir="tests/integration/client/output/generated/player_box_scores",
        snapshot_node=_make_player_box_node,
        tripwire_node=_make_player_box_tripwire,
    ),
    "player_advanced_season_totals": ModuleSnapshotInfo(
        years=[2001, 2016, 2017, 2018, 2019],
        formats=["json", "csv"],
        test_file="tests/integration/client/test_players_advanced_season_totals.py",
        expected_dir="tests/integration/client/output/expected/player_advanced_season_totals",
        generated_dir="tests/integration/client/output/generated/player_advanced_season_totals",
        snapshot_node=_make_advanced_node,
        tripwire_node=_make_advanced_tripwire,
    ),
}


def _output_filename(year, fmt, module):
    """Return the output file name (relative inside expected/generated dir)."""
    if module == "team_box_scores":
        # Always 2018-01-01 for the snapshot test
        return f"2018/01/01.{fmt}"
    if module == "player_box_scores":
        # Always 2001-01-01 for the snapshot
        return f"2001/1/1.{fmt}"
    return f"{year}.{fmt}"


def resolve_generated_path(module_key: str, year: int, fmt: str) -> Path:
    info = SNAPSHOT_MODULES[module_key]
    return REPO_ROOT / info.generated_dir / _output_filename(year, fmt, module_key)


def resolve_expected_path(module_key: str, year: int, fmt: str) -> Path:
    info = SNAPSHOT_MODULES[module_key]
    return REPO_ROOT / info.expected_dir / _output_filename(year, fmt, module_key)


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def run_tripwire(node_id: str, expected_length: int) -> tuple[bool, str]:
    """Run the in-memory tripwire test and return (passed, detail)."""
    env = os.environ.copy()
    env["BR_REGEN"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--no-header", "--tb=short", node_id],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "timed out after 30s"

    if result.returncode != 0:
        # Try to extract the expected vs actual from output
        return False, result.stdout + result.stderr

    return True, ""


def run_snapshot_test(node_id: str) -> tuple[bool, str]:
    """Run the snapshot test with BR_REGEN=1 so generated output is preserved.

    The test is expected to "fail" during regeneration because filecmp.cmp
    detects drift — that is the scenario we are here to fix.  We ignore the
    return code and instead check afterward whether the generated file exists.
    """
    env = os.environ.copy()
    env["BR_REGEN"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--no-header", "--tb=short", node_id],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "timed out after 30s"

    _ = result  # return code intentionally ignored — drift is expected
    return True, ""


def print_diff(generated_path: Path, expected_path: Path) -> None:
    """Print unified diff between generated and expected files."""
    try:
        gen_lines = generated_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except FileNotFoundError:
        print(f"  (generated file not found: {generated_path})")
        return

    try:
        exp_lines = expected_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except FileNotFoundError:
        exp_lines = []

    diff = list(difflib.unified_diff(
        exp_lines, gen_lines,
        fromfile=str(expected_path),
        tofile=str(generated_path),
    ))
    out = sys.stdout
    for line in diff:
        try:
            out.write(line)
        except UnicodeEncodeError:
            out.write(line.encode(out.encoding or "utf-8", errors="replace").decode(out.encoding or "utf-8"))
    out.flush()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Regenerate expected output snapshots for integration tests.",
    )
    parser.add_argument("--apply", action="store_true",
                        help="Actually copy generated → expected. Default is dry-run (show diff).")
    parser.add_argument("--module", choices=list(SNAPSHOT_MODULES.keys()),
                        help="Module to regenerate (required unless --all).")
    parser.add_argument("--year", type=int,
                        help="4-digit year (required unless --all).")
    parser.add_argument("--format", choices=["json", "csv"],
                        help="Output format. If omitted, regenerate both.")
    parser.add_argument("--all", action="store_true",
                        help="Regenerate every known (module, year) combination.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Build list of (module_key, year, format) tuples to process
    jobs: list[tuple[str, int, str]] = []

    if args.all:
        for module_key, info in SNAPSHOT_MODULES.items():
            for year in info.years:
                for fmt in info.formats:
                    jobs.append((module_key, year, fmt))
    else:
        if not args.module:
            print("error: --module is required (or use --all)", file=sys.stderr)
            return 1
        if args.year is None:
            print("error: --year is required (or use --all)", file=sys.stderr)
            return 1
        module_key = args.module
        if module_key not in SNAPSHOT_MODULES:
            print(f"error: unknown module {module_key!r}", file=sys.stderr)
            return 1
        info = SNAPSHOT_MODULES[module_key]
        if args.year not in info.years:
            print(f"warning: year {args.year} has no snapshot tests for module {module_key!r} (known years: {info.years})", file=sys.stderr)
            # Still proceed — maybe someone added fixtures but not tripwires yet
        formats = [args.format] if args.format else info.formats
        for fmt in formats:
            jobs.append((module_key, args.year, fmt))

    if not jobs:
        print("No jobs to process.", file=sys.stderr)
        return 0

    dry_run = not args.apply

    counts = {"unchanged": 0, "regenerated": 0, "aborted": 0, "failed": 0}

    for module_key, year, fmt in jobs:
        label = f"{module_key}_{year}_{fmt}"
        info = SNAPSHOT_MODULES[module_key]
        node_id = info.snapshot_node(year, fmt)
        if node_id is None:
            print(f"[skip] {label}: no snapshot test node-id")
            continue

        generated_path = resolve_generated_path(module_key, year, fmt)
        expected_path = resolve_expected_path(module_key, year, fmt)

        print(f"\n{'='*60}")
        print(f"[{label}]")
        print(f"  snapshot node : {node_id}")
        print(f"  generated     : {generated_path.relative_to(REPO_ROOT)}")
        print(f"  expected      : {expected_path.relative_to(REPO_ROOT)}")
        print(f"  mode          : {'dry-run' if dry_run else 'apply'}")

        try:
            # 1. Tripwire check
            tripwire_node = info.tripwire_node(year)
            tripwire_key = (module_key, year)
            expected_length = TRIPWIRE_LENGTHS.get(tripwire_key)

            if tripwire_node and expected_length is not None:
                print(f"  tripwire      : {tripwire_node} (expecting {expected_length} rows)")
                passed, detail = run_tripwire(tripwire_node, expected_length)
                if not passed:
                    print(f"  [abort] tripwire FAILED — expected {expected_length} rows, got mismatch")
                    print(f"    pytest output:\n{detail}")
                    counts["aborted"] += 1
                    continue
                print(f"  tripwire      : OK ({expected_length} rows)")
            elif tripwire_node and expected_length is None:
                # New year — no known length, warn but continue
                print(f"  [warning] no tripwire length known for {module_key}/{year} — skipping tripwire check")
            else:
                print(f"  tripwire      : (none for this year)")

            # 2. Run the snapshot test
            gen_dir = generated_path.parent
            gen_dir.mkdir(parents=True, exist_ok=True)

            # Remove stale generated file before the test
            if generated_path.exists():
                generated_path.unlink()

            passed, detail = run_snapshot_test(node_id)
            if not passed:
                print(f"  [failed] pytest snapshot test failed")
                print(f"    pytest output:\n{detail}")
                counts["failed"] += 1
                continue

            # 3. Check if generated file exists
            if not generated_path.exists():
                print(f"  [failed] generated file not found after test: {generated_path}")
                counts["failed"] += 1
                continue

            # 4. Compare / copy
            if expected_path.exists() and filecmp.cmp(str(generated_path), str(expected_path), shallow=False):
                print(f"  unchanged     : generated matches expected")
                if not dry_run:
                    pass  # nothing to do
                counts["unchanged"] += 1
            else:
                if dry_run:
                    print(f"  [diff] generated differs from expected:")
                    print_diff(generated_path, expected_path)
                else:
                    expected_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(generated_path), str(expected_path))
                    print(f"  copied        : {generated_path} → {expected_path}")
                counts["regenerated"] += 1
        except Exception as exc:
            print(f"  [error] unexpected exception: {exc}")
            counts["failed"] += 1

    # Summary
    print(f"\n{'='*60}")
    print("Regeneration summary:")
    print(f"  Unchanged  : {counts['unchanged']}")
    print(f"  Regenerated: {counts['regenerated']}")
    print(f"  Aborted    : {counts['aborted']}")
    print(f"  Failed     : {counts['failed']}")

    return 1 if counts["aborted"] or counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
