from __future__ import annotations

import json
from pathlib import Path

import pytest
from courtside_data.client._pipelines._drop_reasons import (
    DROP_REASON_INVALID_VALUE,
    DROP_REASON_MISSING_REQUIRED_FIELD,
    DROP_REASON_PARSER_EXCLUDED,
    row_drop_reason,
)
from courtside_data.client._pipelines.pydantic import _validate_row_model_rows
from courtside_data.debug._pipeline_events import emit_parser_diagnostics, record_rows_filtered
from courtside_data.debug.probe import _csv_row, _summarize_debug_events, _summarize_row_counts
from courtside_data.debug.trace import DebugTrace, debug_trace_context
from courtside_data.parsing import rows
from courtside_data.parsing.custom._common import _schedule_rows_with_stats
from courtside_data.parsing.rows import (
    parse_play_by_play_rows_with_stats,
    parse_search_rows_with_stats,
    parse_standings_with_stats,
)
from parsel import Selector
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PBP_FIXTURE = PROJECT_ROOT / "raw" / "play_by_play" / "ATL_2017_01_01" / "201701010ATL.html"
STANDINGS_FIXTURE = PROJECT_ROOT / "raw" / "standings" / "2024.html"
SEARCH_FIXTURE = PROJECT_ROOT / "raw" / "search" / "kobe.html"
SCHEDULE_FIXTURE = PROJECT_ROOT / "raw" / "season_schedule" / "2024" / "index.html"


class _SampleRow(BaseModel):
    player: str
    pts: int


def test_parsed_rows_summary_event_populates_probe_parsed_row_count() -> None:
    trace = DebugTrace(endpoint="team_roster", params={})
    rows = [{"player": "Tatum", "age": 26, "pts": 26}]
    emit_parser_diagnostics(trace, parser_name="generic_table", rows=rows, source_sections=["table#roster"])

    summary = _summarize_debug_events(trace.to_dict(), endpoint_name="team_roster")

    assert summary["parsed_fields_json"] == ["age", "player", "pts"]
    row_counts = _summarize_row_counts(trace.events, output_row_count=1, raw_table_row_count=None)
    assert row_counts["parsed_row_count"] == 1


def test_generic_table_parsed_event_populates_source_sections() -> None:
    trace = DebugTrace(endpoint="team_roster", params={})
    trace.record(
        "parse",
        "generic_table_parsed",
        source="table#roster",
        source_sections=["table#roster"],
        row_count=12,
        column_names=["player", "number"],
    )

    summary = _summarize_debug_events(trace.to_dict(), endpoint_name="team_roster")

    assert summary["source_sections_json"] == ["table#roster"]


def test_rows_filtered_emits_specific_drop_reasons() -> None:
    raw_rows = [
        {"player": "player", "pts": "pts"},
        {"player": "Tatum", "pts": 26},
    ]
    validated, dropped = _validate_row_model_rows(_SampleRow, raw_rows)

    assert len(validated) == 1
    assert dropped == {"repeated_header": 1}
    assert row_drop_reason(raw_rows[0]) == "repeated_header"


def test_validation_drop_reason_missing_required_field() -> None:
    raw_rows = [
        {"pts": 10},
        {"player": "Tatum", "pts": 26},
    ]
    validated, dropped = _validate_row_model_rows(_SampleRow, raw_rows)

    assert len(validated) == 1
    assert dropped == {DROP_REASON_MISSING_REQUIRED_FIELD: 1}


def test_validation_drop_reason_invalid_value() -> None:
    raw_rows = [
        {"player": "Tatum", "pts": "not-a-number"},
        {"player": "Brown", "pts": 24},
    ]
    validated, dropped = _validate_row_model_rows(_SampleRow, raw_rows)

    assert len(validated) == 1
    assert dropped == {DROP_REASON_INVALID_VALUE: 1}


def test_sentinel_rows_that_validate_remain_in_output() -> None:
    raw_rows = [
        {"player": "did not play", "pts": 0},
        {"player": "Tatum", "pts": 26},
    ]
    validated, dropped = _validate_row_model_rows(_SampleRow, raw_rows)

    assert len(validated) == 2
    assert validated[0].player == "did not play"
    assert validated[1].player == "Tatum"
    assert dropped == {}


def test_parser_excluded_sentinel_rows_drop_when_validation_fails() -> None:
    raw_rows = [
        {"player": "did not play", "pts": "bad"},
        {"player": "Tatum", "pts": 26},
    ]
    validated, dropped = _validate_row_model_rows(_SampleRow, raw_rows)

    assert len(validated) == 1
    assert validated[0].player == "Tatum"
    assert dropped == {DROP_REASON_PARSER_EXCLUDED: 1}


def test_validation_success_emits_explicit_zero_values() -> None:
    trace = DebugTrace(endpoint="team_roster", params={})
    from courtside_data.debug._pipeline_events import record_validation_passed

    record_validation_passed(trace, row_model="TeamRosterRow", validated_row_count=12)

    summary = _summarize_debug_events(trace.to_dict(), endpoint_name="team_roster")

    assert summary["validation_status"] == "passed"
    assert summary["validation_error_count"] == 0
    assert summary["validation_error_paths_json"] == []


def test_validation_failure_exposes_count_and_paths() -> None:
    trace = DebugTrace(endpoint="player_career_stats", params={})
    from courtside_data.debug._pipeline_events import record_validation_failed

    errors = [{"loc": ("fg3_pct",), "msg": "Field required", "type": "missing"}]
    record_validation_failed(trace, row_model="PlayerCareerStatsRow", errors=errors)

    summary = _summarize_debug_events(trace.to_dict(), endpoint_name="player_career_stats")

    assert summary["validation_status"] == "failed"
    assert summary["validation_error_count"] == 1
    assert summary["validation_error_paths_json"] == ["fg3_pct"]


def test_validate_row_model_rows_records_filter_reasons_on_trace() -> None:
    trace = DebugTrace(endpoint="team_roster", params={})
    raw_rows = [
        {"player": "player", "pts": "pts"},
        {"player": "Tatum", "pts": 26},
    ]
    validated, dropped = _validate_row_model_rows(_SampleRow, raw_rows)
    record_rows_filtered(trace, dropped_row_reason_counts=dropped)

    assert len(validated) == 1
    row_counts = _summarize_row_counts(trace.events, output_row_count=len(validated), raw_table_row_count=2)
    assert row_counts["dropped_row_reason_counts_json"] == {"repeated_header": 1}
    assert row_counts["dropped_row_count"] == 1


@pytest.mark.skipif(not PBP_FIXTURE.exists(), reason="play_by_play fixture missing")
def test_play_by_play_parser_emits_custom_diagnostics() -> None:
    html = PBP_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    parsed_rows, stats = parse_play_by_play_rows_with_stats(selector, "SAS", "ATL")

    assert parsed_rows
    assert stats["parsed_event_count"] == len(parsed_rows)

    trace = DebugTrace(endpoint="play_by_play", params={})
    emit_parser_diagnostics(
        trace,
        parser_name="play_by_play",
        rows=parsed_rows,
        source_sections=["table#pbp"],
        parsed_event_count=stats["parsed_event_count"],
        ignored_event_count=stats["ignored_event_count"],
        ignored_event_reason_counts=stats["ignored_event_reason_counts"],
        period_count=stats["period_count"],
        score_event_count=stats["score_event_count"],
        substitution_event_count=stats["substitution_event_count"],
    )

    summary = _summarize_debug_events(trace.to_dict(), data=parsed_rows, endpoint_name="play_by_play")

    assert summary["parser_name"] == "play_by_play"
    assert summary["parsed_event_count"] == stats["parsed_event_count"]
    assert summary["period_count"] == stats["period_count"]
    assert summary["source_sections_json"] == ["table#pbp"]
    assert json.loads(json.dumps(summary["ignored_event_reason_counts_json"]))


@pytest.mark.skipif(not STANDINGS_FIXTURE.exists(), reason="standings fixture missing")
def test_standings_parser_emits_custom_diagnostics() -> None:
    html = STANDINGS_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    parsed_rows, stats = parse_standings_with_stats(selector)

    assert parsed_rows
    assert stats["team_count"] == len(parsed_rows)
    assert stats["standings_section_count"] >= 1
    assert stats["conference_count"] >= 1

    trace = DebugTrace(endpoint="standings", params={"season_end_year": 2024})
    emit_parser_diagnostics(
        trace,
        parser_name="standings",
        rows=parsed_rows,
        source_sections=["table#divs_standings_E", "table#divs_standings_W"],
        ignored_row_reason_counts=stats["ignored_row_reason_counts"],
        custom_diagnostics={
            "conference_count": stats["conference_count"],
            "division_count": stats["division_count"],
            "team_count": stats["team_count"],
            "standings_section_count": stats["standings_section_count"],
        },
    )

    summary = _summarize_debug_events(trace.to_dict(), data=parsed_rows, endpoint_name="standings")

    assert summary["parser_name"] == "standings"
    assert summary["parsed_row_count"] == len(parsed_rows)
    assert summary["custom_diagnostics_json"]["team_count"] == len(parsed_rows)
    assert summary["custom_diagnostics_json"]["conference_count"] >= 1


@pytest.mark.skipif(not SEARCH_FIXTURE.exists(), reason="search fixture missing")
def test_search_parser_emits_custom_diagnostics() -> None:
    html = SEARCH_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    parsed_rows, stats = parse_search_rows_with_stats(selector)

    trace = DebugTrace(endpoint="search", params={"term": "kobe"})
    emit_parser_diagnostics(
        trace,
        parser_name="search",
        rows=parsed_rows,
        source_sections=["div#searches div#players"],
        custom_diagnostics={
            "query": "kobe",
            "result_count": len(parsed_rows),
            "candidate_count": stats["candidate_count"],
            "matched_result_count": stats["matched_result_count"],
            "ignored_result_reason_counts": stats["ignored_result_reason_counts"],
        },
    )

    summary = _summarize_debug_events(trace.to_dict(), data=parsed_rows, endpoint_name="search")

    assert summary["parser_name"] == "search"
    assert summary["custom_diagnostics_json"]["query"] == "kobe"
    assert summary["custom_diagnostics_json"]["result_count"] == len(parsed_rows)
    assert summary["custom_diagnostics_json"]["candidate_count"] == stats["candidate_count"]


@pytest.mark.skipif(not SCHEDULE_FIXTURE.exists(), reason="season_schedule fixture missing")
def test_schedule_parser_emits_custom_diagnostics() -> None:
    html = SCHEDULE_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    parsed_rows, stats = _schedule_rows_with_stats(selector)

    assert parsed_rows
    assert stats["game_count"] == len(parsed_rows)

    trace = DebugTrace(endpoint="season_schedule", params={"season_end_year": 2024})
    emit_parser_diagnostics(
        trace,
        parser_name="season_schedule",
        rows=parsed_rows,
        source_sections=["table#schedule"],
        ignored_row_reason_counts=stats["ignored_row_reason_counts"],
        custom_diagnostics={
            "game_count": stats["game_count"],
            "postponed_game_count": stats["postponed_game_count"],
            "box_score_link_count": stats["box_score_link_count"],
            "missing_box_score_link_count": stats["missing_box_score_link_count"],
        },
    )

    summary = _summarize_debug_events(trace.to_dict(), data=parsed_rows, endpoint_name="season_schedule")

    assert summary["parser_name"] == "season_schedule"
    assert summary["custom_diagnostics_json"]["game_count"] == len(parsed_rows)
    assert summary["custom_diagnostics_json"]["box_score_link_count"] >= 0


def test_probe_csv_consumes_custom_diagnostics_json() -> None:
    from courtside_data.debug.probe import _csv_row

    debug = {
        "trace_id": "trace-custom-diag",
        "duration_ms": 1.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {},
        "stage_counts": {},
        "events": [
            {
                "stage": "parse",
                "event": "standings_parsed",
                "status": "ok",
                "attributes": {
                    "parser_name": "standings",
                    "source_sections": ["table#divs_standings_E"],
                    "parsed_row_count": 15,
                    "custom_diagnostics": {
                        "team_count": 15,
                        "conference_count": 2,
                    },
                },
            },
            {
                "stage": "parse",
                "event": "parsed_rows_summary",
                "status": "ok",
                "attributes": {
                    "parser_name": "standings",
                    "parsed_row_count": 15,
                    "parsed_field_count": 5,
                    "parsed_fields": ["conference", "division", "losses", "team", "wins"],
                },
            },
        ],
    }
    summary = _summarize_debug_events(debug, endpoint_name="standings")
    row = _csv_row({"endpoint": "standings", "ok": True, **summary})

    custom = json.loads(row["custom_diagnostics_json"])
    assert custom["team_count"] == 15
    assert custom["conference_count"] == 2
    assert row["parser_name"] == "standings"


PLAYER_BOX_SCORES_FIXTURE = PROJECT_ROOT / "raw" / "player_box_scores" / "2018_01_01.html"
TEAM_BOX_SCORE_FIXTURE = PROJECT_ROOT / "raw" / "team_box_scores" / "2017_01_01" / "201701010ATL.html"
TEAM_BOX_SCORES_INDEX = PROJECT_ROOT / "raw" / "team_box_scores" / "2017_01_01" / "index.html"
PLAYERS_SEASON_TOTALS_FIXTURE = PROJECT_ROOT / "raw" / "players_season_totals" / "2002.html"
REGULAR_SEASON_BOX_FIXTURE = PROJECT_ROOT / "raw" / "regular_season_player_box_scores" / "westbru01_2020.html"
PLAYOFF_BOX_FIXTURE = PROJECT_ROOT / "raw" / "playoff_player_box_scores" / "westbru01_2020.html"
ADVANCED_TOTALS_FIXTURE = PROJECT_ROOT / "raw" / "players_advanced_season_totals" / "1985.html"


@pytest.mark.skipif(not PLAYER_BOX_SCORES_FIXTURE.exists(), reason="player_box_scores fixture missing")
def test_player_box_scores_with_stats_matches_legacy_output() -> None:
    from courtside_data.parsing.generic import find_table

    html = PLAYER_BOX_SCORES_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    table = find_table(selector, "stats")
    assert table is not None

    legacy_rows = rows.parse_player_box_scores_from_table(table)
    parsed_rows, stats = rows.parse_player_box_scores_from_table_with_stats(table)

    assert parsed_rows == legacy_rows
    assert stats["player_count"] == len(parsed_rows)
    assert stats["selected_table_id"] == "stats"


@pytest.mark.skipif(not TEAM_BOX_SCORE_FIXTURE.exists(), reason="team_box_score fixture missing")
def test_team_box_score_parser_emits_custom_diagnostics() -> None:
    html = TEAM_BOX_SCORE_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    parsed_rows, stats = rows.parse_team_box_score_with_stats(selector)
    legacy_rows = rows.parse_team_box_score(selector)

    assert parsed_rows == legacy_rows
    assert stats["game_count"] == 1
    assert stats["team_count"] == 2

    trace = DebugTrace(endpoint="team_box_score", params={})
    from courtside_data.parsing.custom._diagnostics import emit_custom_endpoint_diagnostics

    with debug_trace_context(trace):
        emit_custom_endpoint_diagnostics(
            parser_name="team_box_score",
            endpoint_name="team_box_score",
            rows=parsed_rows,
            source_sections=['table.stats_table[id$="-game-basic"]'],
            stats=stats,
        )
    summary = _summarize_debug_events(trace.to_dict(), data=parsed_rows, endpoint_name="team_box_score")

    assert summary["parser_name"] == "team_box_score"
    assert summary["custom_diagnostics_json"]["team_count"] == 2
    assert summary["custom_diagnostics_json"]["game_count"] == 1


@pytest.mark.skipif(not PLAYERS_SEASON_TOTALS_FIXTURE.exists(), reason="players_season_totals fixture missing")
def test_players_season_totals_with_stats_matches_legacy_output() -> None:
    from courtside_data.parsing.custom._common import _player_totals_rows, _player_totals_rows_with_stats

    html = PLAYERS_SEASON_TOTALS_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    legacy_rows = _player_totals_rows(selector, "totals_stats", include_combined=False)
    parsed_rows, stats = _player_totals_rows_with_stats(selector, "totals_stats", include_combined=False)

    assert parsed_rows == legacy_rows
    assert stats["player_count"] == len(parsed_rows)
    assert stats["selected_table_id"] == "totals_stats"
    assert stats["season_count"] == 1


@pytest.mark.skipif(not REGULAR_SEASON_BOX_FIXTURE.exists(), reason="regular season box score fixture missing")
def test_regular_season_player_box_scores_emits_custom_diagnostics() -> None:
    from courtside_data.parsing.custom._common import (
        _player_season_box_score_rows,
        _player_season_box_score_rows_with_stats,
    )
    from courtside_data.parsing.custom._diagnostics import IGNORE_INACTIVE_GAME, IGNORE_MISSING_DATE
    from courtside_data.parsing.generic import find_table

    html = REGULAR_SEASON_BOX_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    table = find_table(selector, "player_game_log_reg")
    assert table is not None

    legacy_rows = _player_season_box_score_rows(table, include_inactive_games=False)
    parsed_rows, stats = _player_season_box_score_rows_with_stats(table, include_inactive_games=False)

    assert parsed_rows == legacy_rows
    assert stats["game_count"] == len(parsed_rows)
    ignored = stats["ignored_row_reason_counts"]
    assert IGNORE_MISSING_DATE in ignored or IGNORE_INACTIVE_GAME in ignored or not ignored

    trace = DebugTrace(endpoint="regular_season_player_box_scores", params={})
    from courtside_data.parsing.custom._diagnostics import emit_custom_endpoint_diagnostics

    with debug_trace_context(trace):
        emit_custom_endpoint_diagnostics(
            parser_name="regular_season_player_box_scores",
            endpoint_name="regular_season_player_box_scores",
            rows=parsed_rows,
            source_sections=["table#player_game_log_reg"],
            stats={**stats, "season_count": 1, "selected_table_id": "player_game_log_reg"},
            selected_table_id="player_game_log_reg",
        )
    summary = _summarize_debug_events(
        trace.to_dict(), data=parsed_rows, endpoint_name="regular_season_player_box_scores"
    )

    assert summary["parser_name"] == "regular_season_player_box_scores"
    assert summary["selected_table_id"] == "player_game_log_reg"
    assert summary["custom_diagnostics_json"]["game_count"] == len(parsed_rows)


@pytest.mark.skipif(not PLAYOFF_BOX_FIXTURE.exists(), reason="playoff box score fixture missing")
def test_playoff_player_box_scores_with_stats_matches_legacy_output() -> None:
    from courtside_data.parsing.custom._common import (
        _player_season_box_score_rows,
        _player_season_box_score_rows_with_stats,
    )
    from courtside_data.parsing.generic import find_table

    html = PLAYOFF_BOX_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    table = find_table(selector, "player_game_log_post")
    assert table is not None

    legacy_rows = _player_season_box_score_rows(table, include_inactive_games=False)
    parsed_rows, stats = _player_season_box_score_rows_with_stats(table, include_inactive_games=False)

    assert parsed_rows == legacy_rows
    assert stats["game_count"] == len(parsed_rows)


@pytest.mark.skipif(not ADVANCED_TOTALS_FIXTURE.exists(), reason="advanced season totals fixture missing")
def test_players_advanced_season_totals_emits_custom_diagnostics() -> None:
    from courtside_data.parsing.custom._common import _player_totals_rows_with_stats
    from courtside_data.parsing.custom._diagnostics import emit_custom_endpoint_diagnostics

    html = ADVANCED_TOTALS_FIXTURE.read_text(encoding="utf-8")
    selector = Selector(text=html)
    parsed_rows, stats = _player_totals_rows_with_stats(selector, "advanced", include_combined=False)

    trace = DebugTrace(endpoint="players_advanced_season_totals", params={"season_end_year": 1985})
    with debug_trace_context(trace):
        emit_custom_endpoint_diagnostics(
            parser_name="players_advanced_season_totals",
            endpoint_name="players_advanced_season_totals",
            rows=parsed_rows,
            source_sections=["table#advanced"],
            stats=stats,
            selected_table_id="advanced",
        )
    summary = _summarize_debug_events(trace.to_dict(), data=parsed_rows, endpoint_name="players_advanced_season_totals")
    row = _csv_row({"endpoint": "players_advanced_season_totals", "ok": True, **summary})

    assert summary["parser_name"] == "players_advanced_season_totals"
    assert summary["selected_table_id"] == "advanced"
    assert json.loads(row["custom_diagnostics_json"])["advanced_table_count"] == 1


def test_probe_csv_consumes_box_score_custom_diagnostics() -> None:
    debug = {
        "trace_id": "trace-box",
        "duration_ms": 1.0,
        "status": {"code": "ok", "error_type": None, "error_message": None},
        "metrics": {},
        "stage_counts": {},
        "events": [
            {
                "stage": "parse",
                "event": "team_box_scores_parsed",
                "status": "ok",
                "attributes": {
                    "parser_name": "team_box_scores",
                    "source_sections": ["td.gamelink a"],
                    "parsed_row_count": 4,
                    "custom_diagnostics": {
                        "endpoint_name": "team_box_scores",
                        "game_count": 2,
                        "team_count": 4,
                        "selected_table_id": "box-ATL-game-basic",
                        "candidate_table_ids": ["box-ATL-game-basic", "box-SAS-game-basic"],
                    },
                    "ignored_row_reason_counts": {"empty_table": 0},
                },
            },
            {
                "stage": "parse",
                "event": "parsed_rows_summary",
                "status": "ok",
                "attributes": {
                    "parser_name": "team_box_scores",
                    "parsed_row_count": 4,
                    "parsed_field_count": 2,
                    "parsed_fields": ["outcome", "pts"],
                },
            },
        ],
    }
    summary = _summarize_debug_events(debug, endpoint_name="team_box_scores")
    row = _csv_row({"endpoint": "team_box_scores", "ok": True, **summary})

    custom = json.loads(row["custom_diagnostics_json"])
    assert custom["game_count"] == 2
    assert custom["team_count"] == 4
    assert row["selected_table_id"] == "box-ATL-game-basic"
    assert json.loads(row["candidate_table_ids_json"]) == ["box-ATL-game-basic", "box-SAS-game-basic"]
