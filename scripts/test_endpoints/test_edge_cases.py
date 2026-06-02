"""Test edge cases / error paths for the endpoints."""
import json
import sys
import time
import traceback
from datetime import datetime, timezone

from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team
from basketball_reference_web_scraper.errors import (
    InvalidDate,
    InvalidPlayerAndSeason,
    InvalidSearch,
    InvalidSeason,
)


EDGE_CASES = [
    # (name, fn, expected_exception_type_or_None)
    (
        "search_short_term_LeBron_only",
        lambda: client.search(term="LeBron"),
        None,
    ),
    (
        "search_no_results_xyzzy123",
        lambda: client.search(term="xyzzy123_no_such_player"),
        InvalidSearch,
    ),
    (
        "standings_pre_year_2000",
        lambda: client.standings(season_end_year=1900),
        InvalidSeason,
    ),
    (
        "standings_future_year",
        lambda: client.standings(season_end_year=2099),
        InvalidSeason,
    ),
    (
        "player_box_scores_invalid_date",
        lambda: client.player_box_scores(day=15, month=4, year=1850),
        InvalidDate,
    ),
    (
        "team_box_scores_invalid_date",
        lambda: client.team_box_scores(day=15, month=4, year=1850),
        InvalidDate,
    ),
    (
        "season_schedule_pre_bbref",
        lambda: client.season_schedule(season_end_year=1900),
        InvalidSeason,
    ),
    (
        "players_season_totals_pre_bbref",
        lambda: client.players_season_totals(season_end_year=1900),
        InvalidSeason,
    ),
    (
        "players_advanced_season_totals_pre_bbref",
        lambda: client.players_advanced_season_totals(season_end_year=1900),
        InvalidSeason,
    ),
    (
        "regular_season_player_box_scores_invalid_player",
        lambda: client.regular_season_player_box_scores(player_identifier="zzzzz99", season_end_year=2018),
        InvalidPlayerAndSeason,
    ),
    (
        "playoff_player_box_scores_invalid_player",
        lambda: client.playoff_player_box_scores(player_identifier="zzzzz99", season_end_year=2018),
        InvalidPlayerAndSeason,
    ),
    (
        "regular_season_player_box_scores_invalid_season",
        lambda: client.regular_season_player_box_scores(player_identifier="jamesle01", season_end_year=1900),
        InvalidPlayerAndSeason,
    ),
    (
        "play_by_play_invalid_date",
        lambda: client.play_by_play(home_team=Team.GOLDEN_STATE_WARRIORS, day=15, month=4, year=1850),
        InvalidDate,
    ),
]


def run_one(name, fn, expected):
    started = time.perf_counter()
    record = {
        "name": name,
        "expected_exception": expected.__name__ if expected else None,
        "actual_status": None,
        "actual_exception_type": None,
        "actual_exception_message": None,
        "duration_seconds": None,
    }
    try:
        value = fn()
    except Exception as exc:
        record["actual_status"] = "RAISED"
        record["actual_exception_type"] = type(exc).__name__
        record["actual_exception_message"] = str(exc)
    else:
        record["actual_status"] = "RETURNED"
        if isinstance(value, list):
            record["returned_length"] = len(value)
        elif isinstance(value, dict):
            record["returned_keys"] = list(value.keys())
    record["duration_seconds"] = round(time.perf_counter() - started, 3)
    return record


def main():
    results = []
    for name, fn, expected in EDGE_CASES:
        rec = run_one(name, fn, expected)
        results.append(rec)
        marker = "PASS" if (
            (expected is None and rec["actual_status"] == "RETURNED")
            or (expected is not None and rec["actual_exception_type"] == expected.__name__)
        ) else "FAIL"
        rec["match"] = marker
        print(f"{marker:4}  {name:55s}  expected={rec['expected_exception'] or '-':25s} actual={rec['actual_exception_type'] or rec['actual_status']}")
        time.sleep(2)
    out_path = "scripts/test_endpoints/edge_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}, f, indent=2, default=str)
    print(f"\nWrote {out_path}")
    matches = sum(1 for r in results if r["match"] == "PASS")
    print(f"Summary: {matches}/{len(results)} matched expected behavior")


if __name__ == "__main__":
    main()
