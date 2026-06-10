"""
Scrape all 50 endpoints via the library and write each output as a CSV file.
Respects rate limits — 3.5s base + 1.2s jitter between calls.
Stops immediately on 429 (rate limit) to avoid getting banned.
Output goes to temp_runs/<run_timestamp>/<endpoint_name>.csv
"""

import datetime
import os
import random
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from courtside_data.client import (
    attendance,
    career_leaders,
    draft_picks,
    franchise_history,
    league_per_36_minutes,
    league_per_100_possessions,
    league_per_game_stats,
    league_shooting,
    league_totals,
    league_transactions,
    play_by_play,
    player_adjusted_shooting,
    player_all_star,
    player_box_scores,
    player_career_stats,
    player_game_highs,
    player_on_off,
    player_play_by_play,
    player_playoff_series,
    player_salaries,
    player_shot_charts,
    player_similarity_scores,
    player_splits,
    players_advanced_season_totals,
    players_season_totals,
    playoff_bracket,
    playoff_per_game,
    playoff_player_box_scores,
    playoff_totals,
    regular_season_player_box_scores,
    rookie_stats,
    search,
    season_awards,
    season_leaders,
    season_schedule,
    standings,
    standings_by_date,
    team_and_opponent,
    team_box_scores,
    team_contracts,
    team_injury_report,
    team_lineups,
    team_misc_four_factors,
    team_on_off,
    team_opponent_stats,
    team_roster,
    team_schedule,
    team_splits,
    team_starting_lineups,
    team_transactions,
)
from courtside_data.data import OutputType, OutputWriteOption, Team

# ---------------------------------------------------------------------------
# Test parameters
# ---------------------------------------------------------------------------
SEASON = 2024
PLAYER_ID = "jamesle01"
TEAM_ABBR = "LAL"
DATE_DAY, DATE_MONTH, DATE_YEAR = 11, 3, 2024

BASE_DELAY = 3.5
JITTER = 1.2

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------
RUN_TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "temp_runs",
    RUN_TIMESTAMP,
)


def sleep_with_jitter():
    delay = BASE_DELAY + random.uniform(0, JITTER)
    time.sleep(delay)


def safe_filename(name):
    """Turn endpoint name into a safe filename."""
    safe = name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    return safe


# ---------------------------------------------------------------------------
# Test suite definition
# Each entry: (name, callable, is_new_flag)
# ---------------------------------------------------------------------------
def build_suite():
    suite = []
    suite.append(("standings", lambda **kw: standings(SEASON, **kw)))
    suite.append(("player_box_scores", lambda **kw: player_box_scores(DATE_DAY, DATE_MONTH, DATE_YEAR, **kw)))
    suite.append(
        ("regular_season_player_box_scores", lambda **kw: regular_season_player_box_scores(PLAYER_ID, SEASON, **kw))
    )
    suite.append(("playoff_player_box_scores", lambda **kw: playoff_player_box_scores(PLAYER_ID, SEASON, **kw)))
    suite.append(("season_schedule", lambda **kw: season_schedule(SEASON, **kw)))
    suite.append(("players_season_totals", lambda **kw: players_season_totals(SEASON, **kw)))
    suite.append(("players_advanced_season_totals", lambda **kw: players_advanced_season_totals(SEASON, **kw)))
    suite.append(("team_box_scores", lambda **kw: team_box_scores(DATE_DAY, DATE_MONTH, DATE_YEAR, **kw)))
    suite.append(("play_by_play", lambda **kw: play_by_play(Team.BOSTON_CELTICS, 16, 10, 2018, **kw)))
    suite.append(("search", lambda **kw: search("LeBron James", **kw)))
    suite.append(("league_per_game_stats", lambda **kw: league_per_game_stats(SEASON, **kw)))
    suite.append(("league_per_36_minutes", lambda **kw: league_per_36_minutes(SEASON, **kw)))
    suite.append(("league_totals", lambda **kw: league_totals(SEASON, **kw)))
    suite.append(("rookie_stats", lambda **kw: rookie_stats(SEASON, **kw)))
    suite.append(("standings_by_date", lambda **kw: standings_by_date(SEASON, **kw)))
    suite.append(("attendance", lambda **kw: attendance(SEASON, **kw)))
    suite.append(("league_transactions", lambda **kw: league_transactions(SEASON, **kw)))
    suite.append(("league_per_100_possessions", lambda **kw: league_per_100_possessions(SEASON, **kw)))
    suite.append(("league_shooting", lambda **kw: league_shooting(SEASON, **kw)))
    suite.append(("playoff_per_game", lambda **kw: playoff_per_game(SEASON, **kw)))
    suite.append(("playoff_totals", lambda **kw: playoff_totals(SEASON, **kw)))
    suite.append(("draft_picks", lambda **kw: draft_picks(SEASON, **kw)))
    suite.append(("season_leaders", lambda **kw: season_leaders(**kw)))
    suite.append(("career_leaders", lambda **kw: career_leaders(**kw)))
    suite.append(("playoff_bracket", lambda **kw: playoff_bracket(SEASON, **kw)))
    suite.append(("season_awards", lambda **kw: season_awards(SEASON, **kw)))
    suite.append(("player_career_stats", lambda **kw: player_career_stats(PLAYER_ID, **kw)))
    suite.append(("player_playoff_series", lambda **kw: player_playoff_series(PLAYER_ID, **kw)))
    suite.append(("player_splits", lambda **kw: player_splits(PLAYER_ID, SEASON, **kw)))
    suite.append(("player_on_off", lambda **kw: player_on_off(PLAYER_ID, SEASON, **kw)))
    suite.append(("player_shot_charts", lambda **kw: player_shot_charts(PLAYER_ID, SEASON, **kw)))
    suite.append(("player_adjusted_shooting", lambda **kw: player_adjusted_shooting(PLAYER_ID, **kw)))
    suite.append(("player_play_by_play", lambda **kw: player_play_by_play(PLAYER_ID, **kw)))
    suite.append(("player_game_highs", lambda **kw: player_game_highs(PLAYER_ID, **kw)))
    suite.append(("player_all_star", lambda **kw: player_all_star(PLAYER_ID, **kw)))
    suite.append(("player_similarity_scores", lambda **kw: player_similarity_scores(PLAYER_ID, **kw)))
    suite.append(("player_salaries", lambda **kw: player_salaries(PLAYER_ID, **kw)))
    suite.append(("team_roster", lambda **kw: team_roster(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_injury_report", lambda **kw: team_injury_report(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_and_opponent", lambda **kw: team_and_opponent(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_misc_four_factors", lambda **kw: team_misc_four_factors(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_schedule", lambda **kw: team_schedule(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_transactions", lambda **kw: team_transactions(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_splits", lambda **kw: team_splits(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_contracts", lambda **kw: team_contracts(TEAM_ABBR, **kw)))
    suite.append(("team_lineups", lambda **kw: team_lineups(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_starting_lineups", lambda **kw: team_starting_lineups(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_on_off", lambda **kw: team_on_off(TEAM_ABBR, SEASON, **kw)))
    suite.append(("team_opponent_stats", lambda **kw: team_opponent_stats(TEAM_ABBR, SEASON, **kw)))
    suite.append(("franchise_history", lambda **kw: franchise_history(TEAM_ABBR, **kw)))
    return suite


def run_endpoint_to_csv(name, callable_fn, output_path):
    """Call an endpoint with the library's CSV output and write to file."""
    result = {
        "name": name,
        "output_path": output_path,
        "passed": False,
        "row_count": 0,
        "error_type": None,
        "error_detail": None,
        "status_code": None,
    }
    try:
        # Call via the library's built-in CSV writer
        callable_fn(
            output_type=OutputType.CSV,
            output_file_path=output_path,
            output_write_option=OutputWriteOption.WRITE,
        )
        # Verify the file was written and count rows
        if os.path.exists(output_path):
            with open(output_path, encoding="utf-8") as f:
                row_count = sum(1 for _ in f) - 1  # subtract header
            result["passed"] = True
            result["row_count"] = max(row_count, 0)
        else:
            result["error_type"] = "FileNotFound"
            result["error_detail"] = f"CSV was not written to {output_path}"
        return result
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        result["status_code"] = status
        result["error_type"] = f"HTTP {status}"
        result["error_detail"] = str(e)[:200]
        if status == 429:
            result["error_type"] = "RATE_LIMITED"
    except Exception as e:
        result["error_type"] = type(e).__name__
        result["error_detail"] = str(e)[:300]
    return result


def main():
    suite = build_suite()
    total = len(suite)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Scraping {total} endpoints to CSV files")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Rate limiting: {BASE_DELAY}s + {JITTER}s jitter")
    print(f"Season: {SEASON}, Player: {PLAYER_ID}, Team: {TEAM_ABBR}")
    print("=" * 70)

    passed = 0
    failed = 0
    rate_limited = False
    results = []

    for i, (name, callable_fn) in enumerate(suite, 1):
        filename = safe_filename(name) + ".csv"
        output_path = os.path.join(OUTPUT_DIR, filename)

        print(f"[{i:2d}/{total}] {name:40s} ...", end=" ", flush=True)
        result = run_endpoint_to_csv(name, callable_fn, output_path)
        results.append(result)

        if result["passed"]:
            print(f"OK ({result['row_count']} rows)")
            passed += 1
        else:
            print(f"FAIL — {result['error_type']}: {result['error_detail'][:80]}")
            failed += 1
            if result["error_type"] == "RATE_LIMITED":
                rate_limited = True

        # Stop on rate limit
        if rate_limited:
            print("\n!!! RATE LIMITED (429) — stopping further requests !!!")
            break

        # Rate limit between endpoints
        if i < total:
            sleep_with_jitter()

    # ── Summary ──
    print("=" * 70)
    print(f"Written to: {OUTPUT_DIR}")
    print(f"Results: {passed} passed, {failed} failed out of {len(results)} attempted")
    if rate_limited:
        print("(stopped early due to rate limit)")
        skipped = total - len(results)
        print(f"({skipped} endpoints not attempted)")

    if failed > 0:
        print("\nFailed endpoints:")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['name']}: {r['error_type']} — {r['error_detail']}")

    # ── Write a quick summary CSV too ──
    summary_path = os.path.join(OUTPUT_DIR, "_summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        import csv

        w = csv.writer(f)
        w.writerow(["endpoint", "passed", "rows", "error"])
        for r in results:
            w.writerow(
                [
                    r["name"],
                    "YES" if r["passed"] else "NO",
                    r["row_count"] if r["passed"] else 0,
                    r["error_detail"] or "",
                ]
            )
    print(f"\nSummary also at: {summary_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
