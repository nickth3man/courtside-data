"""Regression tests for per-game box-score workflow endpoints."""

from __future__ import annotations

from pathlib import Path

from courtside_data.domain import Location, Outcome, Team
from courtside_data.parsing.rows import (
    parse_box_score_game_info_with_stats,
    parse_box_score_line_score_with_stats,
    parse_box_score_player_advanced_with_stats,
    parse_box_score_player_basic_with_stats,
    parse_box_score_player_quarter_splits_with_stats,
    parse_box_score_team_four_factors_with_stats,
)
from courtside_data.schemas.boxscores import (
    BoxScoreGameInfoRow,
    BoxScoreLineScoreRow,
    BoxScorePlayerAdvancedRow,
    BoxScorePlayerBasicRow,
    BoxScorePlayerQuarterSplitRow,
    BoxScoreTeamFourFactorsRow,
)
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


def test_box_score_player_advanced_parser_extracts_player_context() -> None:
    rows, stats = parse_box_score_player_advanced_with_stats(_selector())

    assert stats["player_count"] == 25
    assert stats["advanced_table_count"] == 2

    first = BoxScorePlayerAdvancedRow.model_validate(rows[0])
    assert first.slug == "aldrila01"
    assert first.name == "LaMarcus Aldridge"
    assert first.team is Team.SAN_ANTONIO_SPURS
    assert first.opponent is Team.ATLANTA_HAWKS
    assert first.seconds_played == 2607
    assert first.true_shooting_percentage == 0.755
    assert first.offensive_rating == 137.0


def test_box_score_team_four_factors_parser_extracts_commented_table() -> None:
    rows, stats = parse_box_score_team_four_factors_with_stats(_selector())

    assert stats["team_count"] == 2
    assert stats["selected_table_id"] == "four_factors"
    assert stats["raw_column_count"] == 7

    away = BoxScoreTeamFourFactorsRow.model_validate(rows[0])
    home = BoxScoreTeamFourFactorsRow.model_validate(rows[1])
    assert away.team is Team.SAN_ANTONIO_SPURS
    assert away.pace == 92.0
    assert away.effective_field_goal_percentage == 0.517
    assert away.turnover_percentage == 10.7
    assert away.offensive_rebound_percentage == 20.5
    assert away.free_throw_attempt_rate == 0.211
    assert away.offensive_rating == 110.3
    assert home.team is Team.ATLANTA_HAWKS
    assert home.offensive_rating == 112.3


def test_box_score_line_score_parser_extracts_overtime_points() -> None:
    rows, stats = parse_box_score_line_score_with_stats(_selector())

    assert stats["team_count"] == 2
    assert stats["overtime_period_count"] == 1

    away = BoxScoreLineScoreRow.model_validate(rows[0])
    home = BoxScoreLineScoreRow.model_validate(rows[1])
    assert away.team is Team.SAN_ANTONIO_SPURS
    assert away.first_quarter_points == 27
    assert away.overtime_points == [12]
    assert away.total_points == 112
    assert home.team is Team.ATLANTA_HAWKS
    assert home.overtime_points == [14]
    assert home.total_points == 114


def test_box_score_player_quarter_splits_parser_extracts_selected_period() -> None:
    rows, stats = parse_box_score_player_quarter_splits_with_stats(_selector(), period="q1")

    assert stats["player_count"] == 25
    assert stats["selected_period"] == "q1"

    first = BoxScorePlayerQuarterSplitRow.model_validate(rows[0])
    assert first.period == "q1"
    assert first.slug == "aldrila01"
    assert first.team is Team.SAN_ANTONIO_SPURS
    assert first.opponent is Team.ATLANTA_HAWKS
    assert first.seconds_played == 597
    assert first.points == 5


def test_box_score_player_basic_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_player_basic", game_id="201701010ATL")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_player_basic(**case.params)

    assert len(result) == 25
    assert all(isinstance(row, BoxScorePlayerBasicRow) for row in result)


def test_box_score_player_advanced_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_player_advanced", game_id="201701010ATL")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_player_advanced(**case.params)

    assert len(result) == 25
    assert all(isinstance(row, BoxScorePlayerAdvancedRow) for row in result)


def test_box_score_game_info_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_game_info", game_id="201701010ATL")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_game_info(**case.params)

    assert len(result) == 1
    assert isinstance(result[0], BoxScoreGameInfoRow)


def test_box_score_line_score_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_line_score", game_id="201701010ATL")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_line_score(**case.params)

    assert len(result) == 2
    assert all(isinstance(row, BoxScoreLineScoreRow) for row in result)


def test_box_score_player_quarter_splits_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_player_quarter_splits", game_id="201701010ATL", period="q1")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_player_quarter_splits(**case.params)

    assert len(result) == 25
    assert all(isinstance(row, BoxScorePlayerQuarterSplitRow) for row in result)


def test_box_score_team_four_factors_executes_from_offline_fixture(make_offline_client) -> None:
    case = case_for("box_score_team_four_factors", game_id="201701010ATL")
    assert case is not None
    client = make_offline_client(case)

    result = client.box_score_team_four_factors(**case.params)

    assert len(result) == 2
    assert all(isinstance(row, BoxScoreTeamFourFactorsRow) for row in result)
