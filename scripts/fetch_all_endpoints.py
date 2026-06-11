"""Fetch data from every endpoint and write results to a JSON file.

Calls all legacy + beta endpoints with sensible defaults and records
the output (summarized) along with timing and status.
"""

import json
import os
import sys
import time
import traceback
from datetime import UTC, datetime

from courtside_data import client
from courtside_data.data import Team

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "all_endpoints_results.json")

# ── Sensible default parameters ────────────────────────────────────────────
SEASON = 2018
PLAYER = "jamesle01"
TEAM_ABBR = "GSW"
SEARCH_TERM = "LeBron James"
BOX_DAY, BOX_MONTH, BOX_YEAR = 1, 1, 2017
PBP_TEAM = Team.GOLDEN_STATE_WARRIORS
PBP_DAY, PBP_MONTH, PBP_YEAR = 31, 5, 2018


def summarize(value, max_items=2, max_str=200):
    """Return a short, JSON-serializable summary of any return value."""
    if isinstance(value, list):
        sample = value[:max_items]
        return {"type": "list", "length": len(value), "sample": sample}
    if isinstance(value, dict):
        return {
            "type": "dict",
            "keys": list(value.keys())[:10],
            "value": str(value)[:max_str],
        }
    return {"type": type(value).__name__, "value": str(value)[:max_str]}


def run(name, fn):
    """Run one endpoint call, returning a structured result record."""
    record = {
        "endpoint": name,
        "started_at": datetime.now(UTC).isoformat(),
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
        record["result_summary"] = summarize(value)
    record["duration_seconds"] = round(time.perf_counter() - started, 3)
    record["finished_at"] = datetime.now(UTC).isoformat()
    return record


def case(name, fn):
    """Run and print a one-line summary."""
    print(f"\n>>> {name}", flush=True)
    record = run(name, fn)
    status = record["status"]
    dur = record["duration_seconds"]
    if status == "PASS":
        s = record["result_summary"]
        print(f"    PASS {dur}s - {s.get('type')} (len={s.get('length', '')})")
    else:
        print(f"    FAIL {dur}s - {record['exception_type']}: {record['exception_message']}")
    return record


WAIT = 3.5  # seconds between requests


def main():
    cases = [
        # ── Legacy endpoints (10) ──
        ("search", lambda: client.search(term=SEARCH_TERM)),
        ("standings", lambda: client.standings(season_end_year=SEASON)),
        ("player_box_scores", lambda: client.player_box_scores(day=BOX_DAY, month=BOX_MONTH, year=BOX_YEAR)),
        ("team_box_scores", lambda: client.team_box_scores(day=BOX_DAY, month=BOX_MONTH, year=BOX_YEAR)),
        ("season_schedule", lambda: client.season_schedule(season_end_year=SEASON)),
        ("players_season_totals", lambda: client.players_season_totals(season_end_year=SEASON)),
        ("players_advanced_season_totals", lambda: client.players_advanced_season_totals(season_end_year=SEASON)),
        (
            "regular_season_player_box_scores",
            lambda: client.regular_season_player_box_scores(player_identifier=PLAYER, season_end_year=SEASON),
        ),
        (
            "playoff_player_box_scores",
            lambda: client.playoff_player_box_scores(player_identifier=PLAYER, season_end_year=SEASON),
        ),
        ("play_by_play", lambda: client.play_by_play(home_team=PBP_TEAM, day=PBP_DAY, month=PBP_MONTH, year=PBP_YEAR)),
        # ── League-wide season endpoints ──
        ("league_per_game_stats", lambda: client.league_per_game_stats(season_end_year=SEASON)),
        ("league_per_36_minutes", lambda: client.league_per_36_minutes(season_end_year=SEASON)),
        ("league_totals", lambda: client.league_totals(season_end_year=SEASON)),
        ("league_per_100_possessions", lambda: client.league_per_100_possessions(season_end_year=SEASON)),
        ("league_shooting", lambda: client.league_shooting(season_end_year=SEASON)),
        ("league_transactions", lambda: client.league_transactions(season_end_year=SEASON)),
        ("rookie_stats", lambda: client.rookie_stats(season_end_year=SEASON)),
        ("standings_by_date", lambda: client.standings_by_date(season_end_year=SEASON)),
        ("attendance", lambda: client.attendance(season_end_year=SEASON)),
        # ── Playoff endpoints ──
        ("playoff_per_game", lambda: client.playoff_per_game(season_end_year=SEASON)),
        ("playoff_totals", lambda: client.playoff_totals(season_end_year=SEASON)),
        ("playoff_bracket", lambda: client.playoff_bracket(season_end_year=SEASON)),
        # ── Draft, awards, leaders ──
        ("draft_picks", lambda: client.draft_picks(season_end_year=SEASON)),
        ("season_awards", lambda: client.season_awards(season_end_year=SEASON)),
        ("season_leaders", lambda: client.season_leaders()),
        ("career_leaders", lambda: client.career_leaders()),
        # ── Player page endpoints ──
        ("player_career_stats", lambda: client.player_career_stats(player_identifier=PLAYER)),
        ("player_playoff_series", lambda: client.player_playoff_series(player_identifier=PLAYER)),
        ("player_adjusted_shooting", lambda: client.player_adjusted_shooting(player_identifier=PLAYER)),
        ("player_play_by_play", lambda: client.player_play_by_play(player_identifier=PLAYER)),
        ("player_game_highs", lambda: client.player_game_highs(player_identifier=PLAYER)),
        ("player_all_star", lambda: client.player_all_star(player_identifier=PLAYER)),
        ("player_similarity_scores", lambda: client.player_similarity_scores(player_identifier=PLAYER)),
        ("player_salaries", lambda: client.player_salaries(player_identifier=PLAYER)),
        ("player_splits", lambda: client.player_splits(player_identifier=PLAYER, season_end_year=SEASON)),
        ("player_on_off", lambda: client.player_on_off(player_identifier=PLAYER, season_end_year=SEASON)),
        ("player_shot_charts", lambda: client.player_shot_charts(player_identifier=PLAYER, season_end_year=SEASON)),
        # ── Team page endpoints ──
        ("team_roster", lambda: client.team_roster(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        ("team_injury_report", lambda: client.team_injury_report(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        ("team_and_opponent", lambda: client.team_and_opponent(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        (
            "team_misc_four_factors",
            lambda: client.team_misc_four_factors(team_abbreviation=TEAM_ABBR, season_end_year=SEASON),
        ),
        (
            "team_opponent_stats",
            lambda: client.team_opponent_stats(team_abbreviation=TEAM_ABBR, season_end_year=SEASON),
        ),
        ("team_schedule", lambda: client.team_schedule(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        ("team_transactions", lambda: client.team_transactions(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        ("team_splits", lambda: client.team_splits(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        ("team_contracts", lambda: client.team_contracts(team_abbreviation=TEAM_ABBR)),
        ("team_lineups", lambda: client.team_lineups(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        (
            "team_starting_lineups",
            lambda: client.team_starting_lineups(team_abbreviation=TEAM_ABBR, season_end_year=SEASON),
        ),
        ("team_on_off", lambda: client.team_on_off(team_abbreviation=TEAM_ABBR, season_end_year=SEASON)),
        ("franchise_history", lambda: client.franchise_history(team_abbreviation=TEAM_ABBR)),
    ]

    total = len(cases)
    print(f"=== Fetching {total} endpoints (season={SEASON}, player={PLAYER}, team={TEAM_ABBR}) ===")
    print(f"Rate limit: ~{WAIT}s between requests - estimated {round(total * WAIT / 60, 1)} min total")

    results = []
    for i, (name, fn) in enumerate(cases, 1):
        print(f"\n[{i}/{total}] ", end="")
        record = case(name, fn)
        results.append(record)
        if i < total:
            time.sleep(WAIT)

    # Write results
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "parameters": {
                    "season_end_year": SEASON,
                    "player_identifier": PLAYER,
                    "team_abbreviation": TEAM_ABBR,
                    "search_term": SEARCH_TERM,
                    "box_date": f"{BOX_YEAR}-{BOX_MONTH:02d}-{BOX_DAY:02d}",
                },
                "total_endpoints": total,
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )
    print(f"\n\nResults written to {OUTPUT}")

    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total_dur = sum(r["duration_seconds"] or 0 for r in results)
    print(f"\n{'=' * 60}")
    print(f"Summary: {passed} PASSED, {failed} FAILED (of {total})")
    print(f"Total wall time: ~{total_dur:.0f}s ({total_dur / 60:.1f} min)")
    print(f"{'=' * 60}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
