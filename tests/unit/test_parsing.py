"""Unit tests for the pure parsing helpers in :mod:`courtside_data._parsing`.

These functions were extracted out of ``HTTPService`` so they can be exercised
directly (rather than only incidentally through the HTTP stack). The tests
cover both the happy paths and the edge branches (empty/None inputs, ties,
no-match fall-throughs).
"""

from __future__ import annotations

import pytest
from courtside_data import _parsing
from courtside_data.data import (
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
    Division,
    Team,
)
from courtside_data.errors import MissingPlayerSlug
from parsel import Selector


def _td(html: str) -> Selector:
    """Wrap an inner-HTML snippet in a ``td`` and return that cell's Selector."""
    return Selector(text=f"<table><tr><td>{html}</td></tr></table>").css("td")[0]


def test_cell_text_collapses_space_before_punctuation() -> None:
    assert _parsing.cell_text(_td("Smith , Jr .")) == "Smith, Jr."


def test_cell_text_removes_asterisks() -> None:
    assert _parsing.cell_text(_td("LeBron*")) == "LeBron"


def test_slug_from_metadata() -> None:
    metadata = {"name_display": {"data-append-csv": "jamesle01"}}
    assert _parsing.slug_from_metadata(metadata, "name_display") == "jamesle01"
    assert _parsing.slug_from_metadata({}, "name_display") == ""


def test_require_slug_passes_when_present() -> None:
    _parsing.require_slug("endpoint", {"slug": "jamesle01"}, 0)  # does not raise


def test_require_slug_raises_when_absent() -> None:
    with pytest.raises(MissingPlayerSlug):
        _parsing.require_slug("player_box_scores", {"name_display": "Nobody"}, 3)


def test_is_combined_team() -> None:
    assert _parsing.is_combined_team({"team_name_abbr": "2TM"}) is True
    assert _parsing.is_combined_team({"team_name_abbr": "BOS"}) is False
    assert _parsing.is_combined_team({}) is False


def test_team_abbreviation_from_name_round_trips() -> None:
    name = next(iter(TEAM_NAME_TO_TEAM))  # uppercase team-name key
    expected = TEAM_TO_TEAM_ABBREVIATION[TEAM_NAME_TO_TEAM[name]]
    assert _parsing.team_abbreviation_from_name(name) == expected


def test_team_name_from_abbreviation() -> None:
    abbr = next(iter(TEAM_ABBREVIATIONS_TO_TEAM))
    expected = TEAM_ABBREVIATIONS_TO_TEAM[abbr].value.title()
    assert _parsing.team_name_from_abbreviation(abbr) == expected


def test_score_outcome() -> None:
    assert _parsing.score_outcome("100", "90") == "W"
    assert _parsing.score_outcome("90", "100") == "L"
    assert _parsing.score_outcome("100", "100") is None


def test_period_number_and_type() -> None:
    assert _parsing.period_number(3) == 3
    assert _parsing.period_number(5) == 1
    assert _parsing.period_type(4) == "QUARTER"
    assert _parsing.period_type(5) == "OVERTIME"


def test_remaining_seconds() -> None:
    assert _parsing.remaining_seconds("2:30.0") == 150.0


def test_standings_team_value() -> None:
    team = next(iter(Team))
    assert _parsing.standings_team_value(f"{team.value} (1)") == team.value
    assert _parsing.standings_team_value("ZZZ NOT A TEAM") == "ZZZ NOT A TEAM"


def test_division_value() -> None:
    division = next(iter(Division))
    assert _parsing.division_value(f"{division.value} Division") == division.value
    assert _parsing.division_value("Bogus Name") is None


def test_resource_identifier() -> None:
    assert _parsing.resource_identifier("/players/j/jamesle01.html") == "jamesle01"
    assert _parsing.resource_identifier("") == ""
    assert _parsing.resource_identifier(None) == ""


def test_search_result_name() -> None:
    assert _parsing.search_result_name("LeBron James (2003-2024)") == "LeBron James"
    assert _parsing.search_result_name(None) == ""


def test_extract_pattern_from_href() -> None:
    assert _parsing.extract_pattern_from_href("/x?pattern=HA1H0") == "HA1H0"
    assert _parsing.extract_pattern_from_href("/x?other=1") == ""
    assert _parsing.extract_pattern_from_href("") == ""


def test_pattern_to_games_played() -> None:
    assert _parsing.pattern_to_games_played("H1A0") == [
        {"game": 1, "location": "home", "result": "win"},
        {"game": 2, "location": "away", "result": "loss"},
    ]
    assert _parsing.pattern_to_games_played("X1") == []  # invalid location char
    assert _parsing.pattern_to_games_played("H") == []  # missing result char
    assert _parsing.pattern_to_games_played("HZ") == []  # invalid result char


def test_remaining_locations_from_text() -> None:
    assert _parsing.remaining_locations_from_text("H A H") == ["home", "away", "home"]
    assert _parsing.remaining_locations_from_text("") == []
    assert _parsing.remaining_locations_from_text("XYZ") == []


def test_pattern_from_gameslist_spans() -> None:
    cell = _td(
        '<span style="color:#080">H</span>'
        '<span style="color:#f00">A</span>'
        "<span>H</span>"
        "<span>/</span>"
        '<span style="color:#080">A</span>'
    )
    # win-color → H1, loss-color → A0, no-color → H; the slash stops collection.
    assert _parsing.pattern_from_gameslist_spans(cell) == "H1A0H"


def test_pattern_from_gameslist_spans_returns_none_when_empty() -> None:
    assert _parsing.pattern_from_gameslist_spans(_td("<span>X</span>")) is None


def test_remaining_text_from_gameslist() -> None:
    assert _parsing.remaining_text_from_gameslist(_td("H1A0 / H A")) == "HA"
    assert _parsing.remaining_text_from_gameslist(_td("H1A0")) == ""


def test_parse_friv_playoff_outcomes_row_aggregate() -> None:
    row = _friv_row(record="4-3", gameslist="All series", wl="W", href="")
    result = _parsing.parse_friv_playoff_outcomes_row(row)
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
    result = _parsing.parse_friv_playoff_outcomes_row(row)
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
