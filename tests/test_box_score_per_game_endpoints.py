"""Regression tests for per-game box-score workflow endpoints."""

from __future__ import annotations

from pathlib import Path

from courtside_data.domain import Location, Outcome, Team
from courtside_data.parsing.rows import parse_box_score_game_info_with_stats, parse_box_score_player_basic_with_stats
from courtside_data.schemas.boxscores import BoxScoreGameInfoRow, BoxScorePlayerBasicRow
from parsel import Selector

from tests.fixture_manifest import case_for

BOX_SCORE_FIXTURE = Path(__file__).parent.parent / "raw" / "team_box_scores" / "2017_01_01" / "201701010ATL.html"


def _selector() -> Selector:
    return Selector(text=BOX_SCORE_FIXTURE.read_text(encoding="utf-8"))


def test_box_score_player_basic_parser_injects_game_context_and_status() -> None:
    rows, stats = parse_box_score_player_basic_with_stats(_selector())

    assert stats["player_count"] == 25
    assert stats["active_player_count"] == 21
    assert stats["inactive_player_count"] == 4
    assert stats["basic_table_count"] == 2

    first = BoxScorePlayerBasicRow.model_validate(rows[0])
    assert first.slug == "aldrila01"
    assert first.name == "LaMarcus Aldridge"
    assert first.team is Team.SAN_ANTONIO_SPURS
    assert first.opponent is Team.ATLANTA_HAWKS
    assert first.location is Location.AWAY
    assert first.outcome is Outcome.LOSS
    assert first.is_starter is True
    assert first.seconds_played == 2607
    assert first.plus_minus == 18

    dnp = BoxScorePlayerBasicRow.model_validate(next(row for row in rows if row["slug"] == "bertada01"))
    assert dnp.status == "Did Not Play"
    assert dnp.is_starter is False
    assert dnp.seconds_played is None


def test_box_score_game_info_parser_extracts_footer_metadata() -> None:
    rows, stats = parse_box_score_game_info_with_stats(_selector())

    assert stats["official_count"] == 3
    assert stats["inactive_player_count"] == 4

    info = BoxScoreGameInfoRow.model_validate(rows[0])
    assert info.game_date.isoformat() == "2017-01-01"
    assert info.home_team is Team.ATLANTA_HAWKS
    assert info.away_team is Team.SAN_ANTONIO_SPURS
    assert info.home_team_score == 114
    assert info.away_team_score == 112
    assert info.arena == "Philips Arena, Atlanta, Georgia"
    assert info.attendance == 18088
    assert info.duration == "2:44"
    assert info.tip_off == "6:00 PM"
    assert info.officials == ["Tony Brown", "Pat Fraher", "Haywoode Workman"]
    assert info.inactive_home == ["Taurean Prince", "Mike Scott", "Tiago Splitter"]
    assert info.inactive_away == ["Bryn Forbes"]


def test_box_score_player_basic_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_player_basic", game_id="201701010ATL")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_player_basic(**case.params)

    assert len(result) == 25
    assert all(isinstance(row, BoxScorePlayerBasicRow) for row in result)


def test_box_score_game_info_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_game_info", game_id="201701010ATL")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_game_info(**case.params)

    assert len(result) == 1
    assert isinstance(result[0], BoxScoreGameInfoRow)
