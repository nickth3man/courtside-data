"""
Integration tests for all 40 new endpoints.

Tests verify the full pipeline (client function -> HTTPService -> ParserService -> output)
using mocked HTTP responses via requests_mock and patched rate limiting.
"""
from unittest.mock import patch

import pytest
import requests_mock

from basketball_reference_web_scraper.client import (
    # League endpoints
    league_per_game_stats,
    league_per_36_minutes,
    league_totals,
    rookie_stats,
    standings_by_date,
    attendance,
    league_transactions,
    league_per_100_possessions,
    league_shooting,
    # Playoff endpoints
    playoff_per_game,
    playoff_totals,
    # Draft and awards
    draft_picks,
    season_leaders,
    career_leaders,
    playoff_bracket,
    season_awards,
    # Player endpoints
    player_career_stats,
    player_playoff_series,
    player_splits,
    player_on_off,
    player_shot_charts,
    player_adjusted_shooting,
    player_play_by_play,
    player_game_highs,
    player_all_star,
    player_similarity_scores,
    player_salaries,
    # Team endpoints
    team_roster,
    team_injury_report,
    team_and_opponent,
    team_misc_four_factors,
    team_schedule,
    team_transactions,
    team_splits,
    team_contracts,
    team_lineups,
    team_starting_lineups,
    team_on_off,
    team_opponent_stats,
    franchise_history,
)

# ---------------------------------------------------------------------------
# HTML fixture templates
# ---------------------------------------------------------------------------

MINIMAL_TABLE = """
<table id="{table_id}">
    <thead>
        <tr><th>Name</th><th>Value</th></tr>
    </thead>
    <tbody>
        <tr><td data-stat="name">Test Player</td><td data-stat="value">100</td></tr>
    </tbody>
</table>
"""

MINIMAL_COMMENTED_TABLE = """
<div>
<!--
<table id="{table_id}">
    <thead>
        <tr><th>Name</th><th>Value</th></tr>
    </thead>
    <tbody>
        <tr><td data-stat="name">Test Player</td><td data-stat="value">100</td></tr>
    </tbody>
</table>
-->
</div>
"""

# ---------------------------------------------------------------------------
# URL builders
# ---------------------------------------------------------------------------

LEAGUE_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
PER_MINUTE_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_per_minute.html"
TOTALS_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
ROOKIES_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_rookies.html"
STANDINGS_BY_DATE_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_standings_by_date_{conference}.html"
ATTENDANCE_URL = "https://www.basketball-reference.com/leagues/NBA_{year}.html"
TRANSACTIONS_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_transactions.html"
PER_POSS_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_per_poss.html"
SHOOTING_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_shooting.html"
DRAFT_URL = "https://www.basketball-reference.com/draft/NBA_{year}.html"
SEASON_LEADERS_URL = "https://www.basketball-reference.com/leaders/per_season.html"
CAREER_LEADERS_URL = "https://www.basketball-reference.com/leaders/"
PLAYOFF_BRACKET_URL = "https://www.basketball-reference.com/playoffs/NBA_{year}.html"
AWARDS_URL = "https://www.basketball-reference.com/awards/awards_{year}.html"

PLAYER_BASE_URL = "https://www.basketball-reference.com/players/j/jamesle01.html"
PLAYER_SPLITS_URL = "https://www.basketball-reference.com/players/j/jamesle01/splits/{year}"
PLAYER_ON_OFF_URL = "https://www.basketball-reference.com/players/j/jamesle01/on-off/{year}"
PLAYER_SHOT_CHARTS_URL = "https://www.basketball-reference.com/players/j/jamesle01/shooting/{year}"

TEAM_URL = "https://www.basketball-reference.com/teams/LAL/{year}.html"
TEAM_GAMES_URL = "https://www.basketball-reference.com/teams/LAL/{year}_games.html"
TEAM_TRANSACTIONS_URL = "https://www.basketball-reference.com/teams/LAL/{year}_transactions.html"
TEAM_SPLITS_URL = "https://www.basketball-reference.com/teams/LAL/{year}/splits/"
TEAM_CONTRACTS_URL = "https://www.basketball-reference.com/contracts/LAL.html"
TEAM_LINEUPS_URL = "https://www.basketball-reference.com/teams/LAL/{year}/lineups/"
TEAM_STARTING_LINEUPS_URL = "https://www.basketball-reference.com/teams/LAL/{year}_start.html"
TEAM_ON_OFF_URL = "https://www.basketball-reference.com/teams/LAL/{year}/on-off/"
TEAM_OPPONENT_URL = "https://www.basketball-reference.com/teams/LAL/{year}.html"
INJURY_URL = "https://www.basketball-reference.com/friv/injuries.fcgi"
FRANCHISE_HISTORY_URL = "https://www.basketball-reference.com/teams/LAL/"


def _mock_url(m, url, html):
    """Register a GET mock for the given URL."""
    m.get(url, text=html, status_code=200)


# ===================================================================
# League Endpoints (9)
# ===================================================================

class TestLeagueEndpoints:
    """Integration tests for league-level stats endpoints."""

    def test_league_per_game_stats(self):
        html = MINIMAL_TABLE.format(table_id="per_game_stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, LEAGUE_URL.format(year=2024), html)
                result = league_per_game_stats(2024)
                assert isinstance(result, list)

    def test_league_per_36_minutes(self):
        html = MINIMAL_TABLE.format(table_id="per_minute_stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PER_MINUTE_URL.format(year=2024), html)
                result = league_per_36_minutes(2024)
                assert isinstance(result, list)

    def test_league_totals(self):
        html = MINIMAL_TABLE.format(table_id="totals_stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TOTALS_URL.format(year=2024), html)
                result = league_totals(2024)
                assert isinstance(result, list)

    def test_rookie_stats(self):
        html = MINIMAL_TABLE.format(table_id="rookies")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, ROOKIES_URL.format(year=2024), html)
                result = rookie_stats(2024)
                assert isinstance(result, list)

    def test_standings_by_date(self):
        html = MINIMAL_TABLE.format(table_id="standings_by_date")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, STANDINGS_BY_DATE_URL.format(year=2024, conference="eastern_conference"), html)
                _mock_url(m, STANDINGS_BY_DATE_URL.format(year=2024, conference="western_conference"), html)
                result = standings_by_date(2024)
                assert isinstance(result, list)

    def test_attendance(self):
        html = MINIMAL_TABLE.format(table_id="attendance")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, ATTENDANCE_URL.format(year=2024), html)
                result = attendance(2024)
                assert isinstance(result, list)

    def test_league_transactions(self):
        html = MINIMAL_TABLE.format(table_id="transactions")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TRANSACTIONS_URL.format(year=2024), html)
                result = league_transactions(2024)
                assert isinstance(result, list)

    def test_league_per_100_possessions(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="per_poss_stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PER_POSS_URL.format(year=2024), html)
                result = league_per_100_possessions(2024)
                assert isinstance(result, list)

    def test_league_shooting(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="shooting_stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, SHOOTING_URL.format(year=2024), html)
                result = league_shooting(2024)
                assert isinstance(result, list)


# ===================================================================
# Playoff Endpoints (2)
# ===================================================================

class TestPlayoffEndpoints:
    """Integration tests for playoff stats endpoints."""

    def test_playoff_per_game(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="playoffs_per_game")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, LEAGUE_URL.format(year=2024), html)
                result = playoff_per_game(2024)
                assert isinstance(result, list)

    def test_playoff_totals(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="playoffs_totals")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TOTALS_URL.format(year=2024), html)
                result = playoff_totals(2024)
                assert isinstance(result, list)


# ===================================================================
# Draft and Awards Endpoints (5)
# ===================================================================

class TestDraftAndAwards:
    """Integration tests for draft, leaders, and awards endpoints."""

    def test_draft_picks(self):
        html = MINIMAL_TABLE.format(table_id="stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, DRAFT_URL.format(year=2024), html)
                result = draft_picks(2024)
                assert isinstance(result, list)

    def test_season_leaders(self):
        html = MINIMAL_TABLE.format(table_id="leaders")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, SEASON_LEADERS_URL, html)
                result = season_leaders()
                assert isinstance(result, list)

    def test_career_leaders(self):
        html = MINIMAL_TABLE.format(table_id="leaders")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, CAREER_LEADERS_URL, html)
                result = career_leaders()
                assert isinstance(result, list)

    def test_playoff_bracket(self):
        html = MINIMAL_TABLE.format(table_id="bracket")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYOFF_BRACKET_URL.format(year=2024), html)
                result = playoff_bracket(2024)
                assert isinstance(result, list)

    def test_season_awards(self):
        html = MINIMAL_TABLE.format(table_id="awards")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, AWARDS_URL.format(year=2024), html)
                result = season_awards(2024)
                assert isinstance(result, list)


# ===================================================================
# Player Endpoints (11)
# ===================================================================

class TestPlayerEndpoints:
    """Integration tests for player-specific endpoints."""

    def test_player_career_stats(self):
        html = MINIMAL_TABLE.format(table_id="per_game")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_career_stats("jamesle01")
                assert isinstance(result, list)

    def test_player_playoff_series(self):
        html = MINIMAL_TABLE.format(table_id="playoffs_per_game")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_playoff_series("jamesle01")
                assert isinstance(result, list)

    def test_player_splits(self):
        html = MINIMAL_TABLE.format(table_id="splits")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_SPLITS_URL.format(year=2024), html)
                result = player_splits("jamesle01", 2024)
                assert isinstance(result, list)

    def test_player_on_off(self):
        html = MINIMAL_TABLE.format(table_id="on-off")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_ON_OFF_URL.format(year=2024), html)
                result = player_on_off("jamesle01", 2024)
                assert isinstance(result, list)

    def test_player_shot_charts(self):
        html = MINIMAL_TABLE.format(table_id="shot_charts")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_SHOT_CHARTS_URL.format(year=2024), html)
                result = player_shot_charts("jamesle01", 2024)
                assert isinstance(result, list)

    def test_player_adjusted_shooting(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="adj_shooting")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_adjusted_shooting("jamesle01")
                assert isinstance(result, list)

    def test_player_play_by_play(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="pbp")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_play_by_play("jamesle01")
                assert isinstance(result, list)

    def test_player_game_highs(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="highs_totals")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_game_highs("jamesle01")
                assert isinstance(result, list)

    def test_player_all_star(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="all_star_g_stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_all_star("jamesle01")
                assert isinstance(result, list)

    def test_player_similarity_scores(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="sim_career")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_similarity_scores("jamesle01")
                assert isinstance(result, list)

    def test_player_salaries(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="salaries")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, PLAYER_BASE_URL, html)
                result = player_salaries("jamesle01")
                assert isinstance(result, list)


# ===================================================================
# Team Endpoints (13)
# ===================================================================

class TestTeamEndpoints:
    """Integration tests for team-specific endpoints."""

    def test_team_roster(self):
        html = MINIMAL_TABLE.format(table_id="roster")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_URL.format(year=2024), html)
                result = team_roster("LAL", 2024)
                assert isinstance(result, list)

    def test_team_injury_report(self):
        html = MINIMAL_TABLE.format(table_id="injuries")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, INJURY_URL, html)
                result = team_injury_report("LAL", 2024)
                assert isinstance(result, list)

    def test_team_and_opponent(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="team_and_opponent")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_URL.format(year=2024), html)
                result = team_and_opponent("LAL", 2024)
                assert isinstance(result, list)

    def test_team_misc_four_factors(self):
        """Uses a commented (hidden) table."""
        html = MINIMAL_COMMENTED_TABLE.format(table_id="team_misc")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_URL.format(year=2024), html)
                result = team_misc_four_factors("LAL", 2024)
                assert isinstance(result, list)

    def test_team_schedule(self):
        html = MINIMAL_TABLE.format(table_id="games")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_GAMES_URL.format(year=2024), html)
                result = team_schedule("LAL", 2024)
                assert isinstance(result, list)

    def test_team_transactions(self):
        html = MINIMAL_TABLE.format(table_id="transactions")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_TRANSACTIONS_URL.format(year=2024), html)
                result = team_transactions("LAL", 2024)
                assert isinstance(result, list)

    def test_team_splits(self):
        html = MINIMAL_TABLE.format(table_id="team_splits")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_SPLITS_URL.format(year=2024), html)
                result = team_splits("LAL", 2024)
                assert isinstance(result, list)

    def test_team_contracts(self):
        """No season_end_year parameter."""
        html = MINIMAL_TABLE.format(table_id="contracts")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_CONTRACTS_URL, html)
                result = team_contracts("LAL")
                assert isinstance(result, list)

    def test_team_lineups(self):
        html = MINIMAL_TABLE.format(table_id="lineups")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_LINEUPS_URL.format(year=2024), html)
                result = team_lineups("LAL", 2024)
                assert isinstance(result, list)

    def test_team_starting_lineups(self):
        html = MINIMAL_TABLE.format(table_id="starting_lineups")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_STARTING_LINEUPS_URL.format(year=2024), html)
                result = team_starting_lineups("LAL", 2024)
                assert isinstance(result, list)

    def test_team_on_off(self):
        html = MINIMAL_TABLE.format(table_id="on-off")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_ON_OFF_URL.format(year=2024), html)
                result = team_on_off("LAL", 2024)
                assert isinstance(result, list)

    def test_team_opponent_stats(self):
        html = MINIMAL_TABLE.format(table_id="opp_stats")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, TEAM_OPPONENT_URL.format(year=2024), html)
                result = team_opponent_stats("LAL", 2024)
                assert isinstance(result, list)

    def test_franchise_history(self):
        """No season_end_year parameter."""
        html = MINIMAL_TABLE.format(table_id="history")
        with patch("time.sleep"):
            with requests_mock.Mocker() as m:
                _mock_url(m, FRANCHISE_HISTORY_URL, html)
                result = franchise_history("LAL")
                assert isinstance(result, list)
