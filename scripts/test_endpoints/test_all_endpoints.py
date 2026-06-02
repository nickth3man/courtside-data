"""Test every endpoint of basketball_reference_web_scraper and record results.

For each endpoint we:
  1. Call it with sensible arguments
  2. Record status, sample output, and any exception

The output is written both to stdout and to scripts/test_endpoints/results.json
so the markdown report can be regenerated from structured data.
"""
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import (
    OutputType,
    OutputWriteOption,
    Team,
)


HERE = os.path.dirname(os.path.abspath(__file__))


def _summarize(value, max_items=2, max_str=120):
    """Return a short, JSON-serializable summary of an arbitrary return value."""
    if isinstance(value, list):
        sample = value[:max_items]
        return {
            "type": "list",
            "length": len(value),
            "sample": sample,
        }
    if isinstance(value, dict):
        return {"type": "dict", "keys": list(value.keys())[:10], "value": str(value)[:max_str]}
    return {"type": type(value).__name__, "value": str(value)[:max_str]}


def _run(name, fn):
    """Run a single endpoint call, returning a structured result record."""
    record = {
        "endpoint": name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": None,
        "duration_seconds": None,
        "result_summary": None,
        "exception_type": None,
        "exception_message": None,
        "traceback": None,
    }
    started = time.perf_counter()
    try:
        value = fn()
    except Exception as exc:
        record["status"] = "FAIL"
        record["exception_type"] = type(exc).__name__
        record["exception_message"] = str(exc)
        record["traceback"] = traceback.format_exc()
    else:
        record["status"] = "PASS"
        record["result_summary"] = _summarize(value)
    record["duration_seconds"] = round(time.perf_counter() - started, 3)
    record["finished_at"] = datetime.now(timezone.utc).isoformat()
    return record


def _case(name, fn):
    """Run a single endpoint and print a one-line summary."""
    print(f"\n=== {name} ===", flush=True)
    record = _run(name, fn)
    print(f"status: {record['status']}  duration: {record['duration_seconds']}s")
    if record["status"] == "PASS":
        summary = record["result_summary"]
        print(f"return type: {summary.get('type')}")
        if "length" in summary:
            print(f"return length: {summary['length']}")
            if summary["sample"]:
                print("first sample row keys:", list(summary["sample"][0].keys())[:10] if isinstance(summary["sample"][0], dict) else summary["sample"][0])
    else:
        print(f"EXCEPTION ({record['exception_type']}): {record['exception_message']}")
    return record


def main():
    # Sensible defaults: known-good historical dates/players from the integration fixtures
    cases = [
        (
            "search",
            lambda: client.search(term="LeBron James"),
        ),
        (
            "standings",
            lambda: client.standings(season_end_year=2018),
        ),
        (
            "player_box_scores",
            lambda: client.player_box_scores(day=1, month=1, year=2017),
        ),
        (
            "team_box_scores",
            lambda: client.team_box_scores(day=1, month=1, year=2017),
        ),
        (
            "season_schedule",
            lambda: client.season_schedule(season_end_year=2018),
        ),
        (
            "players_season_totals",
            lambda: client.players_season_totals(season_end_year=2018),
        ),
        (
            "players_advanced_season_totals",
            lambda: client.players_advanced_season_totals(season_end_year=2018, include_combined_values=False),
        ),
        (
            "regular_season_player_box_scores",
            # LeBron's BBRef identifier is jamesle01
            lambda: client.regular_season_player_box_scores(player_identifier="jamesle01", season_end_year=2018),
        ),
        (
            "playoff_player_box_scores",
            lambda: client.playoff_player_box_scores(player_identifier="jamesle01", season_end_year=2018),
        ),
        (
            "play_by_play",
            # 2018 Finals Game 1: CLE @ GSW on 2018-05-31
            lambda: client.play_by_play(home_team=Team.GOLDEN_STATE_WARRIORS, day=31, month=5, year=2018),
        ),
    ]

    results = []
    for name, fn in cases:
        results.append(_case(name, fn))
        # Be polite to basketball-reference.com between endpoints
        time.sleep(3)

    out_path = os.path.join(HERE, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}, f, indent=2, default=str)
    print(f"\nWrote {out_path}")

    # Final summary table
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"\nSummary: {passed} passed, {failed} failed (of {len(results)})")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
