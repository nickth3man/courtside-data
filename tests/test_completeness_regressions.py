"""Focused regressions for completeness bugs reported from public fixtures."""

from __future__ import annotations

from courtside_data.domain import Team

from tests.fixture_manifest import case_for


def test_players_season_totals_can_include_siakam_combined_totals(make_offline_client) -> None:
    case = case_for("players_season_totals", season_end_year=2024, include_combined_values=False)
    assert case is not None
    client = make_offline_client(case)

    rows = client.players_season_totals(2024, include_combined_values=True)
    siakam_rows = [row for row in rows if row.name == "Pascal Siakam"]

    assert [(row.team, row.games_played, row.points) for row in siakam_rows] == [
        ("2TM", 80, 1737),
        (Team.TORONTO_RAPTORS, 39, 865),
        (Team.INDIANA_PACERS, 41, 872),
    ]


def test_players_season_totals_default_still_drops_siakam_combined_totals(make_offline_client) -> None:
    case = case_for("players_season_totals", season_end_year=2024, include_combined_values=False)
    assert case is not None
    client = make_offline_client(case)

    rows = client.players_season_totals(2024)
    siakam_rows = [row for row in rows if row.name == "Pascal Siakam"]

    assert [(row.team, row.games_played, row.points) for row in siakam_rows] == [
        (Team.TORONTO_RAPTORS, 39, 865),
        (Team.INDIANA_PACERS, 41, 872),
    ]


def test_league_transactions_preserves_siakam_trade_teams_and_legs(make_offline_client) -> None:
    case = case_for("league_transactions", season_end_year=2024)
    assert case is not None
    client = make_offline_client(case)

    rows = client.league_transactions(2024)
    siakam_rows = [row for row in rows if "Pascal Siakam" in row.transaction]

    assert len(siakam_rows) == 1
    siakam_trade = siakam_rows[0]
    assert siakam_trade.from_team_abbreviations == ["IND"]
    assert siakam_trade.to_team_abbreviations == ["NOP", "TOR"]
    assert "traded cash to the New Orleans Pelicans for Kira Lewis Jr." in siakam_trade.transaction
    assert "to the Toronto Raptors for Pascal Siakam" in siakam_trade.transaction
