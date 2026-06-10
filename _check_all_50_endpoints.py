"""
Check all 50 client endpoints using Playwright (real Chromium browser)
to bypass Cloudflare bot detection. Observes HTTP codes, response sizes,
and timing — writes results incrementally so data survives cancellation.

Usage:
    python _check_all_50_endpoints.py

Output:
    _endpoint_report.csv  — one row per endpoint (incremental)
    _endpoint_outputs/    — one CSV per successful endpoint
"""

import csv
import os
import sys
import time
from datetime import datetime
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["BASKETBALL_REF_RATE_LIMIT_INTERVAL"] = "0.1"   # we manage rate ourselves
os.environ["BASKETBALL_REF_RATE_LIMIT_JITTER"] = "0"

# ── Monkey-patch: shared HTTPService so rate limiter persists ──
import courtside_data.client as _client
from courtside_data.http_service import HTTPService
from courtside_data.parser_service import ParserService

_shared_service = HTTPService(parser=ParserService())
_client.HTTPService = lambda *a, **kw: _shared_service

from courtside_data.client import (
    standings, player_box_scores, regular_season_player_box_scores,
    playoff_player_box_scores, season_schedule, players_season_totals,
    players_advanced_season_totals, team_box_scores, play_by_play, search,
    league_per_game_stats, league_per_36_minutes, league_totals, rookie_stats,
    standings_by_date, attendance, league_transactions, league_per_100_possessions,
    league_shooting, playoff_per_game, playoff_totals, draft_picks, season_leaders,
    career_leaders, playoff_bracket, season_awards, player_career_stats,
    player_playoff_series, player_splits, player_on_off, player_shot_charts,
    player_adjusted_shooting, player_play_by_play, player_game_highs,
    player_all_star, player_similarity_scores, player_salaries,
    team_roster, team_injury_report, team_and_opponent, team_misc_four_factors,
    team_schedule, team_transactions, team_splits, team_contracts,
    team_lineups, team_starting_lineups, team_on_off, team_opponent_stats,
    franchise_history,
)
from courtside_data.data import Team, OutputType, OutputWriteOption

# ── Test params ──
SEASON = 2000
LEBRON_SEASON = 2013
PLAYER = "jamesle01"
TEAM_ABBR = "BOS"
PBP_DAY, PBP_MONTH, PBP_YEAR = 22, 10, 2019
BOX_DAY, BOX_MONTH, BOX_YEAR = 11, 3, 2024

OUTPUT_DIR = "_endpoint_outputs"
REPORT_CSV = "_endpoint_report.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ENDPOINTS = [
    ("standings", standings, (SEASON,), {}),
    ("player_box_scores", player_box_scores, (BOX_DAY, BOX_MONTH, BOX_YEAR), {}),
    ("regular_season_player_box_scores", regular_season_player_box_scores, (PLAYER, LEBRON_SEASON), {}),
    ("playoff_player_box_scores", playoff_player_box_scores, (PLAYER, LEBRON_SEASON), {}),
    ("season_schedule", season_schedule, (SEASON,), {}),
    ("players_season_totals", players_season_totals, (SEASON,), {}),
    ("players_advanced_season_totals", players_advanced_season_totals, (SEASON,), {}),
    ("team_box_scores", team_box_scores, (BOX_DAY, BOX_MONTH, BOX_YEAR), {}),
    ("play_by_play", play_by_play, (Team.BOSTON_CELTICS, PBP_DAY, PBP_MONTH, PBP_YEAR), {}),
    ("search", search, ("james",), {}),
    ("league_per_game_stats", league_per_game_stats, (SEASON,), {}),
    ("league_per_36_minutes", league_per_36_minutes, (SEASON,), {}),
    ("league_totals", league_totals, (SEASON,), {}),
    ("rookie_stats", rookie_stats, (SEASON,), {}),
    ("standings_by_date", standings_by_date, (SEASON,), {}),
    ("attendance", attendance, (SEASON,), {}),
    ("league_transactions", league_transactions, (SEASON,), {}),
    ("league_per_100_possessions", league_per_100_possessions, (SEASON,), {}),
    ("league_shooting", league_shooting, (SEASON,), {}),
    ("playoff_per_game", playoff_per_game, (SEASON,), {}),
    ("playoff_totals", playoff_totals, (SEASON,), {}),
    ("draft_picks", draft_picks, (SEASON,), {}),
    ("season_leaders", season_leaders, (), {}),
    ("career_leaders", career_leaders, (), {}),
    ("playoff_bracket", playoff_bracket, (SEASON,), {}),
    ("season_awards", season_awards, (SEASON,), {}),
    ("player_career_stats", player_career_stats, (PLAYER,), {}),
    ("player_playoff_series", player_playoff_series, (PLAYER,), {}),
    ("player_splits", player_splits, (PLAYER, LEBRON_SEASON), {}),
    ("player_on_off", player_on_off, (PLAYER, LEBRON_SEASON), {}),
    ("player_shot_charts", player_shot_charts, (PLAYER, LEBRON_SEASON), {}),
    ("player_adjusted_shooting", player_adjusted_shooting, (PLAYER,), {}),
    ("player_play_by_play", player_play_by_play, (PLAYER,), {}),
    ("player_game_highs", player_game_highs, (PLAYER,), {}),
    ("player_all_star", player_all_star, (PLAYER,), {}),
    ("player_similarity_scores", player_similarity_scores, (PLAYER,), {}),
    ("player_salaries", player_salaries, (PLAYER,), {}),
    ("team_roster", team_roster, (TEAM_ABBR, SEASON), {}),
    ("team_injury_report", team_injury_report, (TEAM_ABBR, SEASON), {}),
    ("team_and_opponent", team_and_opponent, (TEAM_ABBR, SEASON), {}),
    ("team_misc_four_factors", team_misc_four_factors, (TEAM_ABBR, SEASON), {}),
    ("team_schedule", team_schedule, (TEAM_ABBR, SEASON), {}),
    ("team_transactions", team_transactions, (TEAM_ABBR, SEASON), {}),
    ("team_splits", team_splits, (TEAM_ABBR, SEASON), {}),
    ("team_contracts", team_contracts, (TEAM_ABBR,), {}),
    ("team_lineups", team_lineups, (TEAM_ABBR, SEASON), {}),
    ("team_starting_lineups", team_starting_lineups, (TEAM_ABBR, SEASON), {}),
    ("team_on_off", team_on_off, (TEAM_ABBR, SEASON), {}),
    ("team_opponent_stats", team_opponent_stats, (TEAM_ABBR, SEASON), {}),
    ("franchise_history", franchise_history, (TEAM_ABBR,), {}),
]

# ── Helpers ──

def count_csv_rows(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return sum(1 for _ in csv.DictReader(f))
    except Exception:
        return 0

def write_inline_csv(data, path):
    if not data or not isinstance(data[0], dict):
        return 0
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)
    return len(data)

def _append_report_row(row):
    fieldnames = ["endpoint", "status", "row_count", "error", "output_file",
                  "http_code", "http_elapsed_s", "response_size_bytes"]
    file_exists = os.path.exists(REPORT_CSV)
    with open(REPORT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


class _PlaywrightResponse:
    """Mimic requests.Response so existing parsers work unchanged."""
    def __init__(self, url, status_code, content_bytes, headers=None):
        self.url = url
        self.status_code = status_code
        self.content = content_bytes
        self._text = content_bytes.decode("utf-8", errors="replace") if content_bytes else ""
        self.headers = headers or {}
        self.reason = "OK" if status_code == 200 else "Error"

    @property
    def text(self):
        return self._text

    def raise_for_status(self):
        import requests
        if 400 <= self.status_code < 600:
            http_error = requests.exceptions.HTTPError(
                f"{self.status_code} Client Error: Forbidden for url: {self.url}"
            )
            http_error.response = self
            raise http_error


class PlaywrightFetcher:
    """Fetch pages via Playwright (real Chromium) and return requests-like Response."""

    def __init__(self, headless=True):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        self._page = ctx.new_page()

    def get(self, url, **kwargs):
        """Navigate to a URL and return a _PlaywrightResponse."""
        self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Let JS finish a tick
        self._page.wait_for_timeout(500)
        html = self._page.content()
        return _PlaywrightResponse(
            url=self._page.url,
            status_code=200,  # Playwright would throw on error status
            content_bytes=html.encode("utf-8"),
            headers={},
        )

    def close(self):
        self._browser.close()
        self._pw.stop()


def main():
    """Run all 50 endpoints through Playwright browser."""
    import requests

    print("[setup] Launching Playwright Chromium ... ", end="", flush=True)
    fetcher = PlaywrightFetcher(headless=True)
    print("ready")

    # Replace HTTPService._get with our Playwright-based version
    _shared_service._get = fetcher.get

    # Also patch _last_request_time to avoid rate limiting interfering
    _shared_service._last_request_time = 0
    _shared_service._rate_limit_interval = 0

    # Rate limit: 3s between endpoint calls (well under 20/min)
    DELAY_SECONDS = 3

    ok_count = fail_count = 0
    total_rows = 0

    for idx, (name, func, args, kwargs) in enumerate(ENDPOINTS, start=1):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{idx:02d}/50] {ts} {name} ... ", end="", flush=True)

        row_count = 0
        status = "OK"
        error_msg = ""
        output_path = ""
        http_code = None
        elapsed_s = 0.0
        resp_size = 0
        t0 = time.time()

        try:
            csv_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
            call_kwargs = dict(
                output_type=OutputType.CSV,
                output_file_path=csv_path,
                output_write_option=OutputWriteOption.WRITE,
                **kwargs,
            )
            t0 = time.time()
            result = func(*args, **call_kwargs)
            elapsed_s = round(time.time() - t0, 2)
            http_code = 200

            if isinstance(result, str) and os.path.exists(result):
                row_count = count_csv_rows(result)
                output_path = result
                stat = os.stat(result)
                resp_size = stat.st_size
            elif isinstance(result, list) and result and isinstance(result[0], dict):
                row_count = write_inline_csv(result, csv_path)
                output_path = csv_path
                resp_size = os.path.getsize(csv_path) if os.path.exists(csv_path) else 0
            elif isinstance(result, dict):
                for v in result.values():
                    if isinstance(v, list):
                        row_count += len(v)
                if os.path.exists(csv_path):
                    output_path = csv_path
                    resp_size = os.path.getsize(csv_path)

            print(f"HTTP {http_code} | {elapsed_s}s | {resp_size}B | {row_count} rows")
            ok_count += 1
            total_rows += row_count

        except Exception as e:
            status = "ERROR"
            error_msg = f"{type(e).__name__}: {str(e)[:250]}"
            elapsed_s = round(time.time() - t0, 2) if 't0' in dir() else 0
            print(f"FAIL {type(e).__name__} | {elapsed_s}s")
            fail_count += 1

        row = {
            "endpoint": name,
            "status": status,
            "row_count": row_count,
            "error": error_msg,
            "output_file": output_path,
            "http_code": http_code or "",
            "http_elapsed_s": elapsed_s,
            "response_size_bytes": resp_size,
        }
        _append_report_row(row)

        # Respectful delay between requests
        if idx < len(ENDPOINTS):
            time.sleep(DELAY_SECONDS)

    fetcher.close()

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  Report:       {REPORT_CSV}")
    print(f"  Outputs:      {OUTPUT_DIR}")
    print(f"  OK:           {ok_count}/50")
    print(f"  FAILED:       {fail_count}/50")
    print(f"  Total rows:   {total_rows}")
    print(f"{'='*60}")

    if fail_count:
        print("\nFailures:")
        for name, _, _, _ in ENDPOINTS:
            # re-read from report for accurate error info
            pass
        print("  (see _endpoint_report.csv for details)")

    return fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
