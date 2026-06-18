"""Unit tests for seven-game playoff series outcomes parsing."""

from __future__ import annotations

from pathlib import Path

import pytest
from courtside_data.parsing import rows
from courtside_data.schemas.playoffs import SevenGamePlayoffSeriesOutcomesRow
from parsel import Selector

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "raw"
    / "friv_7_game_playoff_series_outcomes_team_is_down"
    / "7-game-playoff-series-outcomes-22111.html"
)


@pytest.fixture
def team_is_down_rows() -> list[dict]:
    html = FIXTURE.read_text(encoding="utf-8")
    table = Selector(text=html).css("table#team-is-down")[0]
    return [rows.parse_friv_playoff_outcomes_row(row) for row in table.css("tbody tr:not(.thead)") if row.css("td")]


def test_aggregate_row(team_is_down_rows: list[dict]) -> None:
    row = next(item for item in team_is_down_rows if item["record"] == "1-2" and item["aggregate"])
    assert row["gameslist"] == "All series"
    assert row["pattern"] == ""
    assert row["pattern_from_spans"] is None
    assert row["patterns_agree"] is None
    assert row["games_played"] == []
    assert row["games_remaining"] == []
    SevenGamePlayoffSeriesOutcomesRow.model_validate(row)


def test_ambiguous_gameslist_paths_are_disambiguated(team_is_down_rows: list[dict]) -> None:
    paths = [
        item
        for item in team_is_down_rows
        if item["record"] == "1-2" and not item["aggregate"] and item["gameslist_display"] == "A A H / HAHA"
    ]
    assert len(paths) == 3
    assert {item["pattern"] for item in paths} == {"A0A0H1", "A0A1H0", "A1A0H0"}
    assert all(item["patterns_agree"] is True for item in paths)
    assert paths[0]["games_played"] == [
        {"game": 1, "location": "away", "result": "loss"},
        {"game": 2, "location": "away", "result": "loss"},
        {"game": 3, "location": "home", "result": "win"},
    ]
    assert paths[0]["games_remaining"] == ["home", "away", "home", "away"]


def test_pattern_from_spans_matches_href_pattern(team_is_down_rows: list[dict]) -> None:
    detail_rows = [item for item in team_is_down_rows if not item["aggregate"]]
    assert detail_rows
    assert all(item["patterns_agree"] is True for item in detail_rows if item["pattern"])


def test_all_rows_validate_as_row_model(team_is_down_rows: list[dict]) -> None:
    validated = [SevenGamePlayoffSeriesOutcomesRow.model_validate(row) for row in team_is_down_rows]
    assert len(validated) == 46
