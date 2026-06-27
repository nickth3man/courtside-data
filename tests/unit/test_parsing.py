"""Unit tests for the pure parsing helpers in :mod:`courtside_data.parsing.cells` and
:mod:`courtside_data.parsing.rows`.

These functions were extracted out of ``HTTPService`` so they can be exercised
directly (rather than only incidentally through the HTTP stack). The tests
cover both the happy paths and the edge branches (empty/None inputs, ties,
no-match fall-throughs).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from courtside_data.domain import (
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
    Division,
    Team,
)
from courtside_data.errors import MissingPlayerSlug
from courtside_data.parsing import cells, rows
from parsel import Selector


def _td(html: str) -> Selector:
    """Wrap an inner-HTML snippet in a ``td`` and return that cell's Selector."""
    return Selector(text=f"<table><tr><td>{html}</td></tr></table>").css("td")[0]


def test_cell_text_collapses_space_before_punctuation() -> None:
    assert cells.cell_text(_td("Smith , Jr .")) == "Smith, Jr."


def test_cell_text_removes_asterisks() -> None:
    assert cells.cell_text(_td("LeBron*")) == "LeBron"


def test_slug_from_metadata() -> None:
    metadata = {"name_display": {"data-append-csv": "jamesle01"}}
    assert cells.slug_from_metadata(metadata, "name_display") == "jamesle01"
    assert cells.slug_from_metadata({}, "name_display") == ""


def test_require_slug_passes_when_present() -> None:
    cells.require_slug("endpoint", {"slug": "jamesle01"}, 0)  # does not raise


def test_require_slug_raises_when_absent() -> None:
    with pytest.raises(MissingPlayerSlug):
        cells.require_slug("player_box_scores", {"name_display": "Nobody"}, 3)


def test_is_combined_team() -> None:
    assert cells.is_combined_team({"team_name_abbr": "2TM"}) is True
    assert cells.is_combined_team({"team_name_abbr": "BOS"}) is False
    assert cells.is_combined_team({}) is False


def test_team_abbreviation_from_name_round_trips() -> None:
    name = next(iter(TEAM_NAME_TO_TEAM))  # uppercase team-name key
    expected = TEAM_TO_TEAM_ABBREVIATION[TEAM_NAME_TO_TEAM[name]]
    assert cells.team_abbreviation_from_name(name) == expected


def test_team_name_from_abbreviation() -> None:
    abbr = next(iter(TEAM_ABBREVIATIONS_TO_TEAM))
    expected = TEAM_ABBREVIATIONS_TO_TEAM[abbr].value.title()
    assert cells.team_name_from_abbreviation(abbr) == expected


def test_score_outcome() -> None:
    assert cells.score_outcome("100", "90") == "W"
    assert cells.score_outcome("90", "100") == "L"
    assert cells.score_outcome("100", "100") is None


def test_period_number_and_type() -> None:
    assert cells.period_number(3) == 3
    assert cells.period_number(5) == 1
    assert cells.period_type(4) == "QUARTER"
    assert cells.period_type(5) == "OVERTIME"


def test_remaining_seconds() -> None:
    assert cells.remaining_seconds("2:30.0") == 150.0


def test_standings_team_value() -> None:
    team = next(iter(Team))
    assert cells.standings_team_value(f"{team.value} (1)") == team.value
    assert cells.standings_team_value("ZZZ NOT A TEAM") == "ZZZ NOT A TEAM"
    assert cells.standings_team_value("Buffalo Braves") == Team.BUFFALO_BRAVES.value
    assert cells.standings_team_value("Capital Bullets") == Team.CAPITAL_BULLETS.value
    assert cells.standings_team_value("Kansas City-Omaha Kings") == Team.KANSAS_CITY_OMAHA_KINGS.value


STANDINGS_1974_FIXTURE = Path(__file__).resolve().parents[2] / "raw" / "standings" / "1974.html"


def test_standings_1974_validates_all_teams() -> None:
    from courtside_data.client._pipelines.pydantic import _validate_row_model_rows
    from courtside_data.schemas.standings import StandingsRow

    assert STANDINGS_1974_FIXTURE.exists(), f"missing fixture: {STANDINGS_1974_FIXTURE}"
    html = STANDINGS_1974_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    parsed_rows, _stats = rows.parse_standings_with_stats(selector)

    assert len(parsed_rows) == 17
    validated, dropped = _validate_row_model_rows(StandingsRow, parsed_rows)

    assert len(validated) == 17
    assert dropped == {}


def test_division_value() -> None:
    division = next(iter(Division))
    assert cells.division_value(f"{division.value} Division") == division.value
    assert cells.division_value("Bogus Name") is None


def test_resource_identifier() -> None:
    assert cells.resource_identifier("/players/j/jamesle01.html") == "jamesle01"
    assert cells.resource_identifier("") == ""
    assert cells.resource_identifier(None) == ""


def test_search_result_name() -> None:
    assert cells.search_result_name("LeBron James (2003-2024)") == "LeBron James"
    assert cells.search_result_name(None) == ""


def test_extract_pattern_from_href() -> None:
    assert cells.extract_pattern_from_href("/x?pattern=HA1H0") == "HA1H0"
    assert cells.extract_pattern_from_href("/x?other=1") == ""
    assert cells.extract_pattern_from_href("") == ""


def test_pattern_to_games_played() -> None:
    assert cells.pattern_to_games_played("H1A0") == [
        {"game": 1, "location": "home", "result": "win"},
        {"game": 2, "location": "away", "result": "loss"},
    ]
    assert cells.pattern_to_games_played("X1") == []  # invalid location char
    assert cells.pattern_to_games_played("H") == []  # missing result char
    assert cells.pattern_to_games_played("HZ") == []  # invalid result char


def test_remaining_locations_from_text() -> None:
    assert cells.remaining_locations_from_text("H A H") == ["home", "away", "home"]
    assert cells.remaining_locations_from_text("") == []
    assert cells.remaining_locations_from_text("XYZ") == []


def test_pattern_from_gameslist_spans() -> None:
    cell = _td(
        '<span style="color:#080">H</span>'
        '<span style="color:#f00">A</span>'
        "<span>H</span>"
        "<span>/</span>"
        '<span style="color:#080">A</span>'
    )
    # win-color → H1, loss-color → A0, no-color → H; the slash stops collection.
    assert cells.pattern_from_gameslist_spans(cell) == "H1A0H"


def test_pattern_from_gameslist_spans_returns_none_when_empty() -> None:
    assert cells.pattern_from_gameslist_spans(_td("<span>X</span>")) is None


def test_remaining_text_from_gameslist() -> None:
    assert cells.remaining_text_from_gameslist(_td("H1A0 / H A")) == "HA"
    assert cells.remaining_text_from_gameslist(_td("H1A0")) == ""


def test_parse_friv_playoff_outcomes_row_aggregate() -> None:
    row = _friv_row(record="4-3", gameslist="All series", wl="W", href="")
    result = rows.parse_friv_playoff_outcomes_row(row)
    assert result["aggregate"] is True
    assert result["games_played"] == []
    assert result["games_remaining"] == []


def test_parse_friv_playoff_outcomes_row_single_series() -> None:
    row = _friv_row(
        record="1-0",
        gameslist='<span style="color:#080">H</span>',
        wl="W",
        href="/x?pattern=H1",
    )
    result = rows.parse_friv_playoff_outcomes_row(row)
    assert result["aggregate"] is False
    assert result["pattern"] == "H1"
    assert result["games_played"] == [{"game": 1, "location": "home", "result": "win"}]


def _friv_row(*, record: str, gameslist: str, wl: str, href: str) -> Selector:
    wl_cell = f'<td data-stat="wl"><a href="{href}">{wl}</a></td>' if href else f'<td data-stat="wl">{wl}</td>'
    html = (
        "<table><tr>"
        f'<td data-stat="record">{record}</td>'
        f'<td data-stat="gameslist">{gameslist}</td>'
        f"{wl_cell}"
        "</tr></table>"
    )
    return Selector(text=html).css("tr")[0]
