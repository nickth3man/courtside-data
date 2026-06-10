"""
Live endpoint verification: runs every client endpoint 2x against basketball-reference.com.
Respects rate limits — 3.5s base + 1.2s jitter between calls.
Stops immediately on 429 (rate limit) to avoid getting banned.
Outputs a detailed results document to docs/endpoint_verification_results.md
"""

import datetime
import os
import random
import sys
import time
from collections import OrderedDict

import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from courtside_data.client import (
    attendance,
    career_leaders,
    # Draft & Awards (5)
    draft_picks,
    franchise_history,
    league_per_36_minutes,
    league_per_100_possessions,
    # League (9)
    league_per_game_stats,
    league_shooting,
    league_totals,
    league_transactions,
    play_by_play,
    player_adjusted_shooting,
    player_all_star,
    player_box_scores,
    # Player (11)
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
    # Playoff (2)
    playoff_per_game,
    playoff_player_box_scores,
    playoff_totals,
    regular_season_player_box_scores,
    rookie_stats,
    search,
    season_awards,
    season_leaders,
    season_schedule,
    # Original 10
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
    # Team (13)
    team_roster,
    team_schedule,
    team_splits,
    team_starting_lineups,
    team_transactions,
)
from courtside_data.data import Team

# ---------------------------------------------------------------------------
# Test parameters
# ---------------------------------------------------------------------------
SEASON = 2024
PLAYER_ID = "jamesle01"  # LeBron James
TEAM_ABBR = "LAL"
DATE_DAY, DATE_MONTH, DATE_YEAR = 11, 3, 2024  # March 11, 2024 — known-good date

# Rate limiting
BASE_DELAY = 3.5  # matches HTTPService default
JITTER = 1.2

OUTPUT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs",
    "endpoint_verification_results.md",
)


def sleep_with_jitter():
    delay = BASE_DELAY + random.uniform(0, JITTER)
    time.sleep(delay)


# ---------------------------------------------------------------------------
# Define every endpoint call as a dict
# Each entry: (name, callable, args_tuple, kwargs_dict, is_original)
# ---------------------------------------------------------------------------
def _build_test_suite():
    suite = []

    # ── Original 10 ──
    suite.append(("standings (original)", lambda: standings(SEASON), False))
    suite.append(("player_box_scores (original)", lambda: player_box_scores(DATE_DAY, DATE_MONTH, DATE_YEAR), False))
    suite.append(
        (
            "regular_season_player_box_scores (original)",
            lambda: regular_season_player_box_scores(PLAYER_ID, SEASON),
            False,
        )
    )
    suite.append(("playoff_player_box_scores (original)", lambda: playoff_player_box_scores(PLAYER_ID, SEASON), False))
    suite.append(("season_schedule (original)", lambda: season_schedule(SEASON), False))
    suite.append(("players_season_totals (original)", lambda: players_season_totals(SEASON), False))
    suite.append(("players_advanced_season_totals (original)", lambda: players_advanced_season_totals(SEASON), False))
    suite.append(("team_box_scores (original)", lambda: team_box_scores(DATE_DAY, DATE_MONTH, DATE_YEAR), False))
    suite.append(("play_by_play (original)", lambda: play_by_play(Team.BOSTON_CELTICS, 16, 10, 2018), False))
    suite.append(("search (original)", lambda: search("LeBron James"), False))

    # ── League (9) ──
    suite.append(("league_per_game_stats", lambda: league_per_game_stats(SEASON), True))
    suite.append(("league_per_36_minutes", lambda: league_per_36_minutes(SEASON), True))
    suite.append(("league_totals", lambda: league_totals(SEASON), True))
    suite.append(("rookie_stats", lambda: rookie_stats(SEASON), True))
    suite.append(("standings_by_date", lambda: standings_by_date(SEASON), True))
    suite.append(("attendance", lambda: attendance(SEASON), True))
    suite.append(("league_transactions", lambda: league_transactions(SEASON), True))
    suite.append(("league_per_100_possessions", lambda: league_per_100_possessions(SEASON), True))
    suite.append(("league_shooting", lambda: league_shooting(SEASON), True))

    # ── Playoff (2) ──
    suite.append(("playoff_per_game", lambda: playoff_per_game(SEASON), True))
    suite.append(("playoff_totals", lambda: playoff_totals(SEASON), True))

    # ── Draft & Awards (5) ──
    suite.append(("draft_picks", lambda: draft_picks(SEASON), True))
    suite.append(("season_leaders", lambda: season_leaders(), True))
    suite.append(("career_leaders", lambda: career_leaders(), True))
    suite.append(("playoff_bracket", lambda: playoff_bracket(SEASON), True))
    suite.append(("season_awards", lambda: season_awards(SEASON), True))

    # ── Player (11) ──
    suite.append(("player_career_stats", lambda: player_career_stats(PLAYER_ID), True))
    suite.append(("player_playoff_series", lambda: player_playoff_series(PLAYER_ID), True))
    suite.append(("player_splits", lambda: player_splits(PLAYER_ID, SEASON), True))
    suite.append(("player_on_off", lambda: player_on_off(PLAYER_ID, SEASON), True))
    suite.append(("player_shot_charts", lambda: player_shot_charts(PLAYER_ID, SEASON), True))
    suite.append(("player_adjusted_shooting", lambda: player_adjusted_shooting(PLAYER_ID), True))
    suite.append(("player_play_by_play", lambda: player_play_by_play(PLAYER_ID), True))
    suite.append(("player_game_highs", lambda: player_game_highs(PLAYER_ID), True))
    suite.append(("player_all_star", lambda: player_all_star(PLAYER_ID), True))
    suite.append(("player_similarity_scores", lambda: player_similarity_scores(PLAYER_ID), True))
    suite.append(("player_salaries", lambda: player_salaries(PLAYER_ID), True))

    # ── Team (13) ──
    suite.append(("team_roster", lambda: team_roster(TEAM_ABBR, SEASON), True))
    suite.append(("team_injury_report", lambda: team_injury_report(TEAM_ABBR, SEASON), True))
    suite.append(("team_and_opponent", lambda: team_and_opponent(TEAM_ABBR, SEASON), True))
    suite.append(("team_misc_four_factors", lambda: team_misc_four_factors(TEAM_ABBR, SEASON), True))
    suite.append(("team_schedule", lambda: team_schedule(TEAM_ABBR, SEASON), True))
    suite.append(("team_transactions", lambda: team_transactions(TEAM_ABBR, SEASON), True))
    suite.append(("team_splits", lambda: team_splits(TEAM_ABBR, SEASON), True))
    suite.append(("team_contracts", lambda: team_contracts(TEAM_ABBR), True))
    suite.append(("team_lineups", lambda: team_lineups(TEAM_ABBR, SEASON), True))
    suite.append(("team_starting_lineups", lambda: team_starting_lineups(TEAM_ABBR, SEASON), True))
    suite.append(("team_on_off", lambda: team_on_off(TEAM_ABBR, SEASON), True))
    suite.append(("team_opponent_stats", lambda: team_opponent_stats(TEAM_ABBR, SEASON), True))
    suite.append(("franchise_history", lambda: franchise_history(TEAM_ABBR), True))

    return suite


def test_endpoint(endpoint_name, callable_fn, run_num):
    """Run one endpoint call, return structured result."""
    result = {
        "name": endpoint_name,
        "run": run_num,
        "passed": False,
        "row_count": 0,
        "keys": [],
        "sample_row": None,
        "error_type": None,
        "error_detail": None,
        "status_code": None,
    }
    try:
        data = callable_fn()
        result["passed"] = True
        if isinstance(data, list):
            result["row_count"] = len(data)
            if data:
                first = data[0]
                if isinstance(first, dict):
                    result["keys"] = list(first.keys())
                    # Truncate sample row for large rows
                    result["sample_row"] = dict(list(first.items())[:5])
        elif isinstance(data, dict):
            result["row_count"] = len(data)
            result["keys"] = list(data.keys())
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


def format_run_result(r, run_num):
    """Single-line status for console."""
    if r["passed"]:
        rows = r["row_count"]
        return f"[PASS] Run {run_num}: {rows} rows, {len(r['keys'])} keys"
    else:
        return f"[FAIL] Run {run_num}: {r['error_type']} — {r['error_detail'][:80]}"


def markdown_row(name, r1, r2):
    """Build a Markdown table row from two runs."""
    # Determine status badge
    if r1["passed"] and r2["passed"]:
        badge = "✅"
    elif r1["passed"] or r2["passed"]:
        badge = "⚠️"  # one run failed
    else:
        badge = "❌"

    # Format run details
    def fmt_run(r):
        if r["passed"]:
            return f"✔ {r['row_count']} rows, {len(r['keys'])} keys"
        return f"✘ {r['error_type']}: {r['error_detail'][:100]}"

    return f"| {badge} | {name} | {fmt_run(r1)} | {fmt_run(r2)} |"


def main():
    suite = _build_test_suite()
    total = len(suite)
    print(f"Testing {total} endpoints × 2 runs = {total * 2} total calls")
    print(f"Rate limiting: {BASE_DELAY}s + {JITTER}s jitter")
    print(f"Season: {SEASON}, Player: {PLAYER_ID}, Team: {TEAM_ABBR}, Date: {DATE_MONTH}/{DATE_DAY}/{DATE_YEAR}")
    print("=" * 70)

    all_results = []  # list of (name, r1, r2)

    for i, (name, callable_fn, _is_new) in enumerate(suite, 1):
        print(f"\n[{i}/{total}] {name}")
        print("-" * 50)

        # Run 1
        print("  Calling (1/2)...", end=" ", flush=True)
        r1 = test_endpoint(name, callable_fn, 1)
        print(format_run_result(r1, 1))

        # Rate limit
        sleep_with_jitter()

        # Run 2
        print("  Calling (2/2)...", end=" ", flush=True)
        r2 = test_endpoint(name, callable_fn, 2)
        print(format_run_result(r2, 2))

        all_results.append((name, r1, r2))

        # Stop on rate limit
        if r1["error_type"] == "RATE_LIMITED" or r2["error_type"] == "RATE_LIMITED":
            print("\n!!! RATE LIMITED (429) — stopping further requests !!!")
            break

    # ──────────────────────────────────────────────────────────────────────
    # Write results document
    # ──────────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    passed_both = sum(1 for _, r1, r2 in all_results if r1["passed"] and r2["passed"])
    failed_both = sum(1 for _, r1, r2 in all_results if not r1["passed"] and not r2["passed"])
    partial = sum(1 for _, r1, r2 in all_results if r1["passed"] != r2["passed"])
    total_tested = len(all_results)

    lines = []
    lines.append("# Endpoint Verification Results")
    lines.append("")
    lines.append(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(
        f"**Test Parameters:** Season={SEASON}, Player={PLAYER_ID}, Team={TEAM_ABBR}, Date={DATE_MONTH}/{DATE_DAY}/{DATE_YEAR}"
    )
    lines.append("")
    lines.append(f"**Total Endpoints:** {total_tested}  |  **Calls Made:** {total_tested * 2}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Result | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| ✅ Both runs passed | {passed_both} |")
    lines.append(f"| ⚠️  One run failed | {partial} |")
    lines.append(f"| ❌ Both runs failed | {failed_both} |")
    lines.append("")

    # ── Detail table ──
    lines.append("## Per-Endpoint Results")
    lines.append("")
    lines.append("| Status | Endpoint | Run 1 | Run 2 |")
    lines.append("|--------|----------|-------|-------|")
    for name, r1, r2 in all_results:
        lines.append(markdown_row(name, r1, r2))
    lines.append("")

    # ── Failure details ──
    failures = [(name, r1, r2) for name, r1, r2 in all_results if not r1["passed"] or not r2["passed"]]
    if failures:
        lines.append("## Failure Details")
        lines.append("")
        for name, r1, r2 in failures:
            lines.append(f"### {name}")
            lines.append("")
            lines.append("| Run | Passed | Rows | Detail |")
            lines.append("|-----|--------|------|--------|")
            lines.append(
                f"| 1 | {'Yes' if r1['passed'] else 'No'} | {r1['row_count']} | {r1['error_detail'] or 'OK'} |"
            )
            lines.append(
                f"| 2 | {'Yes' if r2['passed'] else 'No'} | {r2['row_count']} | {r2['error_detail'] or 'OK'} |"
            )
            if not r1["passed"] and r1["error_detail"]:
                lines.append(f"- **Error:** `{r1['error_type']}` — {r1['error_detail']}")
            if not r2["passed"] and r2["error_detail"]:
                lines.append(f"- **Error:** `{r2['error_type']}` — {r2['error_detail']}")
            lines.append("")

    # ── Success details (key samples) ──
    lines.append("## Sample Output Keys (first run)")
    lines.append("")
    lines.append("| Endpoint | Rows | Sample Keys |")
    lines.append("|----------|------|-------------|")
    for name, r1, _r2 in all_results:
        if r1["passed"]:
            keys_str = ", ".join(r1["keys"][:10])
            if len(r1["keys"]) > 10:
                keys_str += ", …"
            lines.append(f"| {name} | {r1['row_count']} | `{keys_str}` |")
    lines.append("")

    # ── Stats at bottom ──
    lines.append("## Stats by Endpoint Category")
    lines.append("")
    categories = OrderedDict(
        [
            ("Original", [0, 0, 0]),
            ("League", [0, 0, 0]),
            ("Playoff", [0, 0, 0]),
            ("Draft/Awards", [0, 0, 0]),
            ("Player", [0, 0, 0]),
            ("Team", [0, 0, 0]),
        ]
    )
    for name, r1, r2 in all_results:
        # simple category mapping by endpoint type
        if "(original)" in name:
            cat = "Original"
        elif (
            name.startswith("league_")
            or name.startswith("standings_by_date")
            or name.startswith("attendance")
            or name.startswith("rookie_")
        ):
            cat = "League"
        elif name in ("playoff_per_game", "playoff_totals"):
            cat = "Playoff"
        elif name in ("draft_picks", "season_leaders", "career_leaders", "playoff_bracket", "season_awards"):
            cat = "Draft/Awards"
        elif name.startswith("player_"):
            cat = "Player"
        elif name.startswith("team_") or name.startswith("franchise_"):
            cat = "Team"
        else:
            continue
        passed = r1["passed"] and r2["passed"]
        partial_f = r1["passed"] != r2["passed"]
        if passed:
            categories[cat][0] += 1
        elif partial_f:
            categories[cat][1] += 1
        else:
            categories[cat][2] += 1

    lines.append("| Category | ✅ Both Pass | ⚠️  Partial | ❌ Both Fail |")
    lines.append("|----------|-------------|-------------|-------------|")
    for cat, (p, par, f) in categories.items():
        total_cat = p + par + f
        lines.append(f"| {cat} ({total_cat}) | {p} | {par} | {f} |")
    lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n" + "=" * 70)
    print(f"Results written to: {OUTPUT_FILE}")
    summary = f"Summary: {passed_both} PASS both runs, {partial} PARTIAL (one fail), {failed_both} FAIL both runs ({total_tested} endpoints)"
    print(summary.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))

    return 0 if failed_both == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
