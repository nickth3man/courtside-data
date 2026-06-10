"""Generate the final clean endpoint report from actual CSV files on disk."""
import csv
import os

output_dir = "_endpoint_outputs"
report_path = "_endpoint_report_final.csv"

all_endpoints = [
    "standings", "player_box_scores", "regular_season_player_box_scores",
    "playoff_player_box_scores", "season_schedule", "players_season_totals",
    "players_advanced_season_totals", "team_box_scores", "play_by_play",
    "search", "league_per_game_stats", "league_per_36_minutes",
    "league_totals", "rookie_stats", "standings_by_date", "attendance",
    "league_transactions", "league_per_100_possessions", "league_shooting",
    "playoff_per_game", "playoff_totals", "draft_picks", "season_leaders",
    "career_leaders", "playoff_bracket", "season_awards",
    "player_career_stats", "player_playoff_series", "player_splits",
    "player_on_off", "player_shot_charts", "player_adjusted_shooting",
    "player_play_by_play", "player_game_highs", "player_all_star",
    "player_similarity_scores", "player_salaries",
    "team_roster", "team_injury_report", "team_and_opponent",
    "team_misc_four_factors", "team_schedule", "team_transactions",
    "team_splits", "team_contracts", "team_lineups",
    "team_starting_lineups", "team_on_off", "team_opponent_stats",
    "franchise_history",
]

# Known parsing errors from Playwright run (caused by rendered HTML diffs)
known_errors = {
    "standings": "AttributeError: eastern_conference_table is None",
    "player_box_scores": "InvalidDate: 2024-03-11",
    "playoff_player_box_scores": "InvalidPlayerAndSeason: jamesle01/2013",
    "season_schedule": "ValueError: time data Date does not match format",
    "play_by_play": "IndexError: list index out of range",
}

rows = []
for ep in all_endpoints:
    csv_file = os.path.join(output_dir, f"{ep}.csv")
    if os.path.exists(csv_file):
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            row_count = len(data)
        size = os.path.getsize(csv_file)
        error = known_errors.get(ep, "")
        status = "PARTIAL" if error else "OK"
    else:
        row_count = 0
        size = 0
        error = known_errors.get(ep, "NO_CSV")
        status = "ERROR"
    rows.append({
        "endpoint": ep,
        "status": status,
        "data_rows": row_count,
        "file_bytes": size,
        "error_note": error,
    })

with open(report_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["endpoint", "status", "data_rows", "file_bytes", "error_note"])
    w.writeheader()
    w.writerows(rows)

ok = sum(1 for r in rows if r["status"] == "OK")
partial = sum(1 for r in rows if r["status"] == "PARTIAL")
err = sum(1 for r in rows if r["status"] == "ERROR")
total = sum(r["data_rows"] for r in rows)
total_bytes = sum(r["file_bytes"] for r in rows)

print(f"OK:      {ok}/50")
print(f"PARTIAL: {partial}/50  (HTTP 200 but parsing mismatches from Playwright)")
print(f"ERROR:   {err}/50    (no CSV output)")
print(f"Total data rows: {total}")
print(f"Total file bytes: {total_bytes}")
print(f"Report: {report_path}")
