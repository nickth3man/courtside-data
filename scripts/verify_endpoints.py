"""
Live verification of all new endpoints against basketball-reference.com.
Respects rate limits with 5s + 2s jitter between requests.
Stops immediately if a 429 (rate limit) response is received.
"""
import time
import random
import sys
import requests
from courtside_data.client import (
    league_per_game_stats, league_per_36_minutes, league_totals,
    rookie_stats, standings_by_date, attendance, league_transactions,
    league_per_100_possessions, league_shooting, playoff_per_game, playoff_totals,
    draft_picks, season_leaders, career_leaders, playoff_bracket, season_awards,
    player_career_stats, player_playoff_series, player_splits, player_on_off, player_shot_charts,
    player_adjusted_shooting, player_play_by_play, player_game_highs, player_all_star,
    player_similarity_scores, player_salaries,
    team_roster, team_injury_report, team_and_opponent, team_misc_four_factors,
    team_schedule, team_transactions,
    team_splits, team_contracts, team_lineups, team_starting_lineups,
    team_on_off, team_opponent_stats, franchise_history,
)

# Test parameters
SEASON = 2024
PLAYER_ID = "jamesle01"  # LeBron James
TEAM = "LAL"

# Rate limiting (on top of the HTTP service's built-in 3.5s + 1.2s jitter)
DELAY = 5.0  # seconds between requests
JITTER = 2.0  # random jitter


def sleep_with_jitter():
    delay = DELAY + random.uniform(0, JITTER)
    time.sleep(delay)


def test_endpoint(name, func, *args, **kwargs):
    """Test a single endpoint and return (name, success, message).

    Returns (name, False, "429: ...") on rate limits so the caller can stop.
    """
    try:
        result = func(*args, **kwargs)
        if not isinstance(result, list):
            return (name, False, f"Expected list, got {type(result).__name__}")
        if len(result) == 0:
            return (name, False, "Empty result (no data)")
        # Check first row has keys
        first_row = result[0]
        if not isinstance(first_row, dict):
            return (name, False, f"Expected dict row, got {type(first_row).__name__}")
        if len(first_row) == 0:
            return (name, False, "Empty dict (no keys)")
        return (name, True, f"OK ({len(result)} rows, {len(first_row)} keys)")
    except requests.exceptions.HTTPError as http_error:
        status = http_error.response.status_code if http_error.response is not None else "?"
        msg = str(http_error)[:100]
        if status == 429:
            return (name, False, f"429 RATE LIMITED: {msg}")
        return (name, False, f"HTTP {status}: {msg}")
    except Exception as e:
        return (name, False, str(e)[:200])


def main():
    """Run all endpoint tests with rate limiting."""
    tests = [
        # League endpoints
        ("league_per_game_stats", league_per_game_stats, [SEASON]),
        ("league_per_36_minutes", league_per_36_minutes, [SEASON]),
        ("league_totals", league_totals, [SEASON]),
        ("rookie_stats", rookie_stats, [SEASON]),
        ("standings_by_date", standings_by_date, [SEASON]),
        ("attendance", attendance, [SEASON]),
        ("league_transactions", league_transactions, [SEASON]),
        ("league_per_100_possessions", league_per_100_possessions, [SEASON]),
        ("league_shooting", league_shooting, [SEASON]),
        ("playoff_per_game", playoff_per_game, [SEASON]),
        ("playoff_totals", playoff_totals, [SEASON]),

        # Draft & Awards
        ("draft_picks", draft_picks, [SEASON]),
        ("season_leaders", season_leaders, []),           # no season param
        ("career_leaders", career_leaders, []),           # no season param
        ("playoff_bracket", playoff_bracket, [SEASON]),
        ("season_awards", season_awards, [SEASON]),

        # Player endpoints
        ("player_career_stats", player_career_stats, [PLAYER_ID]),
        ("player_playoff_series", player_playoff_series, [PLAYER_ID]),
        ("player_splits", player_splits, [PLAYER_ID, SEASON]),
        ("player_on_off", player_on_off, [PLAYER_ID, SEASON]),
        ("player_shot_charts", player_shot_charts, [PLAYER_ID, SEASON]),
        ("player_adjusted_shooting", player_adjusted_shooting, [PLAYER_ID]),
        ("player_play_by_play", player_play_by_play, [PLAYER_ID]),
        ("player_game_highs", player_game_highs, [PLAYER_ID]),
        ("player_all_star", player_all_star, [PLAYER_ID]),
        ("player_similarity_scores", player_similarity_scores, [PLAYER_ID]),
        ("player_salaries", player_salaries, [PLAYER_ID]),

        # Team endpoints
        ("team_roster", team_roster, [TEAM, SEASON]),
        ("team_injury_report", team_injury_report, [TEAM, SEASON]),
        ("team_and_opponent", team_and_opponent, [TEAM, SEASON]),
        ("team_misc_four_factors", team_misc_four_factors, [TEAM, SEASON]),
        ("team_schedule", team_schedule, [TEAM, SEASON]),
        ("team_transactions", team_transactions, [TEAM, SEASON]),
        ("team_splits", team_splits, [TEAM, SEASON]),
        ("team_contracts", team_contracts, [TEAM]),
        ("team_lineups", team_lineups, [TEAM, SEASON]),
        ("team_starting_lineups", team_starting_lineups, [TEAM, SEASON]),
        ("team_on_off", team_on_off, [TEAM, SEASON]),
        ("team_opponent_stats", team_opponent_stats, [TEAM, SEASON]),
        ("franchise_history", franchise_history, [TEAM]),
    ]

    print(f"Testing {len(tests)} endpoints with {DELAY}s + {JITTER}s jitter")
    print(f"Season: {SEASON}, Player: {PLAYER_ID}, Team: {TEAM}")
    print("=" * 60)

    passed = 0
    failed = 0
    results = []

    for i, (name, func, args) in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] Testing {name}...", end=" ", flush=True)
        result = test_endpoint(name, func, *args)
        results.append(result)

        if result[1]:
            print(f"[PASS] {result[2]}")
            passed += 1
        else:
            print(f"[FAIL] {result[2]}")
            failed += 1

            # Stop immediately on 429 rate limit
            if result[2].startswith("429"):
                print("\n!!! RATE LIMITED (429) - stopping further requests to avoid ban !!!")
                break

        # Rate limiting (skip after last request)
        if i < len(tests):
            sleep_with_jitter()

    print("=" * 60)
    total_tested = len(results)
    print(f"Results: {passed} passed, {failed} failed out of {total_tested} tested")

    # Note any skipped tests
    if total_tested < len(tests):
        skipped = len(tests) - total_tested
        print(f"({skipped} tests skipped due to early termination)")

    if failed > 0:
        print("\nFailed endpoints:")
        for name, success, msg in results:
            if not success:
                print(f"  - {name}: {msg}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
