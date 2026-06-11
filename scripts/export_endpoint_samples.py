"""Export two live sample calls for every public scraper endpoint.

The output is intentionally compact: one CSV row per endpoint call with the
total row count and up to two sample records serialized as JSON.
"""

import csv
import json
import sys
from pathlib import Path

import httpx

from courtside_data.data import Team
from courtside_data.http_service import HTTPService
from courtside_data.parser_service import ParserService

OUTPUT_PATH = Path("endpoint_samples.csv")
RATE_LIMIT_INTERVAL = 5.0
RATE_LIMIT_JITTER = 2.0


def _normalize_result(result):
    if isinstance(result, dict) and "players" in result:
        return result["players"]
    if isinstance(result, list):
        return result
    return [{"value": result}]


def _json(value):
    return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)


def _call_specs(service):
    return [
        ("standings", lambda: service.standings(2024), {"season_end_year": 2024}),
        ("standings", lambda: service.standings(2025), {"season_end_year": 2025}),
        ("player_box_scores", lambda: service.player_box_scores(25, 12, 2023), {"day": 25, "month": 12, "year": 2023}),
        ("player_box_scores", lambda: service.player_box_scores(27, 1, 2024), {"day": 27, "month": 1, "year": 2024}),
        (
            "regular_season_player_box_scores",
            lambda: service.regular_season_player_box_scores("jamesle01", 2024),
            {"player_identifier": "jamesle01", "season_end_year": 2024},
        ),
        (
            "regular_season_player_box_scores",
            lambda: service.regular_season_player_box_scores("curryst01", 2024),
            {"player_identifier": "curryst01", "season_end_year": 2024},
        ),
        (
            "playoff_player_box_scores",
            lambda: service.playoff_player_box_scores("jamesle01", 2023),
            {"player_identifier": "jamesle01", "season_end_year": 2023},
        ),
        (
            "playoff_player_box_scores",
            lambda: service.playoff_player_box_scores("curryst01", 2022),
            {"player_identifier": "curryst01", "season_end_year": 2022},
        ),
        ("season_schedule", lambda: service.season_schedule(2024), {"season_end_year": 2024}),
        ("season_schedule", lambda: service.season_schedule(2025), {"season_end_year": 2025}),
        ("players_season_totals", lambda: service.players_season_totals(2024), {"season_end_year": 2024}),
        ("players_season_totals", lambda: service.players_season_totals(2025), {"season_end_year": 2025}),
        (
            "players_advanced_season_totals",
            lambda: service.players_advanced_season_totals(2024),
            {"season_end_year": 2024},
        ),
        (
            "players_advanced_season_totals",
            lambda: service.players_advanced_season_totals(2025),
            {"season_end_year": 2025},
        ),
        ("team_box_scores", lambda: service.team_box_scores(25, 12, 2023), {"day": 25, "month": 12, "year": 2023}),
        ("team_box_scores", lambda: service.team_box_scores(27, 1, 2024), {"day": 27, "month": 1, "year": 2024}),
        (
            "play_by_play",
            lambda: service.play_by_play(Team.LOS_ANGELES_LAKERS, 25, 12, 2023),
            {"home_team": "LOS_ANGELES_LAKERS", "day": 25, "month": 12, "year": 2023},
        ),
        (
            "play_by_play",
            lambda: service.play_by_play(Team.GOLDEN_STATE_WARRIORS, 27, 1, 2024),
            {"home_team": "GOLDEN_STATE_WARRIORS", "day": 27, "month": 1, "year": 2024},
        ),
        ("search", lambda: service.search("LeBron James"), {"term": "LeBron James"}),
        ("search", lambda: service.search("Stephen Curry"), {"term": "Stephen Curry"}),
        (
            "team_roster",
            lambda: service.team_roster("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_roster",
            lambda: service.team_roster("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_injury_report",
            lambda: service.team_injury_report("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_injury_report",
            lambda: service.team_injury_report("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_and_opponent",
            lambda: service.team_and_opponent("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_and_opponent",
            lambda: service.team_and_opponent("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_misc_four_factors",
            lambda: service.team_misc_four_factors("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_misc_four_factors",
            lambda: service.team_misc_four_factors("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        ("league_per_game_stats", lambda: service.league_per_game_stats(2024), {"season_end_year": 2024}),
        ("league_per_game_stats", lambda: service.league_per_game_stats(2025), {"season_end_year": 2025}),
        ("league_per_36_minutes", lambda: service.league_per_36_minutes(2024), {"season_end_year": 2024}),
        ("league_per_36_minutes", lambda: service.league_per_36_minutes(2025), {"season_end_year": 2025}),
        ("league_totals", lambda: service.league_totals(2024), {"season_end_year": 2024}),
        ("league_totals", lambda: service.league_totals(2025), {"season_end_year": 2025}),
        ("rookie_stats", lambda: service.rookie_stats(2024), {"season_end_year": 2024}),
        ("rookie_stats", lambda: service.rookie_stats(2025), {"season_end_year": 2025}),
        ("standings_by_date", lambda: service.standings_by_date(2024), {"season_end_year": 2024}),
        ("standings_by_date", lambda: service.standings_by_date(2025), {"season_end_year": 2025}),
        ("attendance", lambda: service.attendance(2024), {"season_end_year": 2024}),
        ("attendance", lambda: service.attendance(2025), {"season_end_year": 2025}),
        ("league_transactions", lambda: service.league_transactions(2024), {"season_end_year": 2024}),
        ("league_transactions", lambda: service.league_transactions(2025), {"season_end_year": 2025}),
        ("league_per_100_possessions", lambda: service.league_per_100_possessions(2024), {"season_end_year": 2024}),
        ("league_per_100_possessions", lambda: service.league_per_100_possessions(2025), {"season_end_year": 2025}),
        ("league_shooting", lambda: service.league_shooting(2024), {"season_end_year": 2024}),
        ("league_shooting", lambda: service.league_shooting(2025), {"season_end_year": 2025}),
        ("playoff_per_game", lambda: service.playoff_per_game(2024), {"season_end_year": 2024}),
        ("playoff_per_game", lambda: service.playoff_per_game(2025), {"season_end_year": 2025}),
        ("playoff_totals", lambda: service.playoff_totals(2024), {"season_end_year": 2024}),
        ("playoff_totals", lambda: service.playoff_totals(2025), {"season_end_year": 2025}),
        ("draft_picks", lambda: service.draft_picks(2024), {"season_end_year": 2024}),
        ("draft_picks", lambda: service.draft_picks(2025), {"season_end_year": 2025}),
        ("season_leaders", service.season_leaders, {}),
        ("season_leaders", service.season_leaders, {}),
        ("career_leaders", service.career_leaders, {}),
        ("career_leaders", service.career_leaders, {}),
        ("playoff_bracket", lambda: service.playoff_bracket(2024), {"season_end_year": 2024}),
        ("playoff_bracket", lambda: service.playoff_bracket(2025), {"season_end_year": 2025}),
        ("season_awards", lambda: service.season_awards(2024), {"season_end_year": 2024}),
        ("season_awards", lambda: service.season_awards(2025), {"season_end_year": 2025}),
        ("player_career_stats", lambda: service.player_career_stats("jamesle01"), {"player_identifier": "jamesle01"}),
        ("player_career_stats", lambda: service.player_career_stats("curryst01"), {"player_identifier": "curryst01"}),
        (
            "player_playoff_series",
            lambda: service.player_playoff_series("jamesle01"),
            {"player_identifier": "jamesle01"},
        ),
        (
            "player_playoff_series",
            lambda: service.player_playoff_series("curryst01"),
            {"player_identifier": "curryst01"},
        ),
        (
            "player_splits",
            lambda: service.player_splits("jamesle01", 2024),
            {"player_identifier": "jamesle01", "season_end_year": 2024},
        ),
        (
            "player_splits",
            lambda: service.player_splits("curryst01", 2024),
            {"player_identifier": "curryst01", "season_end_year": 2024},
        ),
        (
            "player_on_off",
            lambda: service.player_on_off("jamesle01", 2024),
            {"player_identifier": "jamesle01", "season_end_year": 2024},
        ),
        (
            "player_on_off",
            lambda: service.player_on_off("curryst01", 2024),
            {"player_identifier": "curryst01", "season_end_year": 2024},
        ),
        (
            "player_shot_charts",
            lambda: service.player_shot_charts("jamesle01", 2024),
            {"player_identifier": "jamesle01", "season_end_year": 2024},
        ),
        (
            "player_shot_charts",
            lambda: service.player_shot_charts("curryst01", 2024),
            {"player_identifier": "curryst01", "season_end_year": 2024},
        ),
        (
            "player_adjusted_shooting",
            lambda: service.player_adjusted_shooting("jamesle01"),
            {"player_identifier": "jamesle01"},
        ),
        (
            "player_adjusted_shooting",
            lambda: service.player_adjusted_shooting("curryst01"),
            {"player_identifier": "curryst01"},
        ),
        ("player_play_by_play", lambda: service.player_play_by_play("jamesle01"), {"player_identifier": "jamesle01"}),
        ("player_play_by_play", lambda: service.player_play_by_play("curryst01"), {"player_identifier": "curryst01"}),
        ("player_game_highs", lambda: service.player_game_highs("jamesle01"), {"player_identifier": "jamesle01"}),
        ("player_game_highs", lambda: service.player_game_highs("curryst01"), {"player_identifier": "curryst01"}),
        ("player_all_star", lambda: service.player_all_star("jamesle01"), {"player_identifier": "jamesle01"}),
        ("player_all_star", lambda: service.player_all_star("curryst01"), {"player_identifier": "curryst01"}),
        (
            "player_similarity_scores",
            lambda: service.player_similarity_scores("jamesle01"),
            {"player_identifier": "jamesle01"},
        ),
        (
            "player_similarity_scores",
            lambda: service.player_similarity_scores("curryst01"),
            {"player_identifier": "curryst01"},
        ),
        ("player_salaries", lambda: service.player_salaries("jamesle01"), {"player_identifier": "jamesle01"}),
        ("player_salaries", lambda: service.player_salaries("curryst01"), {"player_identifier": "curryst01"}),
        (
            "team_schedule",
            lambda: service.team_schedule("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_schedule",
            lambda: service.team_schedule("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_transactions",
            lambda: service.team_transactions("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_transactions",
            lambda: service.team_transactions("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_splits",
            lambda: service.team_splits("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_splits",
            lambda: service.team_splits("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        ("team_contracts", lambda: service.team_contracts("LAL"), {"team_abbreviation": "LAL"}),
        ("team_contracts", lambda: service.team_contracts("BOS"), {"team_abbreviation": "BOS"}),
        (
            "team_lineups",
            lambda: service.team_lineups("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_lineups",
            lambda: service.team_lineups("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_starting_lineups",
            lambda: service.team_starting_lineups("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_starting_lineups",
            lambda: service.team_starting_lineups("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_on_off",
            lambda: service.team_on_off("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_on_off",
            lambda: service.team_on_off("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        (
            "team_opponent_stats",
            lambda: service.team_opponent_stats("LAL", 2024),
            {"team_abbreviation": "LAL", "season_end_year": 2024},
        ),
        (
            "team_opponent_stats",
            lambda: service.team_opponent_stats("BOS", 2024),
            {"team_abbreviation": "BOS", "season_end_year": 2024},
        ),
        ("franchise_history", lambda: service.franchise_history("LAL"), {"team_abbreviation": "LAL"}),
        ("franchise_history", lambda: service.franchise_history("BOS"), {"team_abbreviation": "BOS"}),
    ]


def main():
    service = HTTPService(
        parser=ParserService(),
        session=httpx.Client(),
        rate_limit_interval=RATE_LIMIT_INTERVAL,
        rate_limit_jitter=RATE_LIMIT_JITTER,
    )
    specs = _call_specs(service)
    endpoint_call_counts = {}

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "endpoint",
                "call_index",
                "args_json",
                "status",
                "row_count",
                "sample_rows_json",
                "error",
            ],
        )
        writer.writeheader()

        for index, (endpoint, call, args) in enumerate(specs, 1):
            endpoint_call_counts[endpoint] = endpoint_call_counts.get(endpoint, 0) + 1
            call_index = endpoint_call_counts[endpoint]
            print(f"[{index}/{len(specs)}] {endpoint} call {call_index}", flush=True)

            status = "ok"
            error = ""
            rows = []
            try:
                rows = _normalize_result(call())
            except httpx.HTTPStatusError as exc:
                status = "http_error"
                error = str(exc)
                if exc.response.status_code == 429:
                    writer.writerow(
                        {
                            "endpoint": endpoint,
                            "call_index": call_index,
                            "args_json": _json(args),
                            "status": status,
                            "row_count": 0,
                            "sample_rows_json": "[]",
                            "error": error,
                        }
                    )
                    print("Rate limited with HTTP 429; stopping.", file=sys.stderr)
                    return 1
            except Exception as exc:
                status = "error"
                error = str(exc)

            writer.writerow(
                {
                    "endpoint": endpoint,
                    "call_index": call_index,
                    "args_json": _json(args),
                    "status": status,
                    "row_count": len(rows),
                    "sample_rows_json": _json(rows[:2]),
                    "error": error,
                }
            )

    print(f"Wrote {len(specs)} calls to {OUTPUT_PATH.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
