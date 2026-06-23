"""Unit tests for row drop-reason classification and data-quality evaluation."""

from __future__ import annotations

from courtside_data.client._pipelines._data_quality import (
    DATA_QUALITY_CLEAN,
    DATA_QUALITY_LOSSY,
    DATA_QUALITY_WARNINGS,
    evaluate_data_quality,
)
from courtside_data.client._pipelines._drop_reasons import (
    DROP_REASON_AGGREGATE_ROW,
    DROP_REASON_BLANK_ROW,
    DROP_REASON_COMBINED_TEAM,
    DROP_REASON_INVALID_DATE,
    DROP_REASON_INVALID_PLAYER_VALUE,
    DROP_REASON_INVALID_TEAM_VALUE,
    DROP_REASON_INVALID_VALUE,
    DROP_REASON_MONTH_HEADER,
    DROP_REASON_REPEATED_HEADER,
    DROP_REASON_UNSUPPORTED_SENTINEL_VALUE,
    row_drop_reason,
    validation_error_drop_reason,
)
from courtside_data.client._pipelines.pydantic import _validate_row_model_rows
from courtside_data.data import Team
from courtside_data.debug.probe import _csv_row, _with_evaluation
from courtside_data.schemas._fields import TeamNameField
from pydantic import BaseModel, Field


class _SampleRow(BaseModel):
    player: str
    pts: int


class _TeamRow(BaseModel):
    team: TeamNameField = Field(validation_alias="team_name_abbr")
    player: str


def test_historical_team_name_validates() -> None:
    row = {"team_name_abbr": "Buffalo Braves", "player": "McAdoo"}
    validated, dropped = _validate_row_model_rows(_TeamRow, [row])
    assert len(validated) == 1
    assert validated[0].team == Team.BUFFALO_BRAVES
    assert dropped == {}


def test_repeated_header_classified() -> None:
    row = {"player": "player", "pts": "pts"}
    assert row_drop_reason(row) == DROP_REASON_REPEATED_HEADER


def test_aggregate_row_classified() -> None:
    row = {"name_display": "League Average", "team_name_abbr": "LG", "pts": "10"}
    assert row_drop_reason(row) == DROP_REASON_AGGREGATE_ROW


def test_combined_team_classified() -> None:
    row = {"name_display": "Player X", "team_name_abbr": "2TM", "pts": "10"}
    assert row_drop_reason(row) == DROP_REASON_COMBINED_TEAM


def test_schedule_month_header_classified() -> None:
    row = {"date_game": "October", "visitor_team_name": "", "home_team_name": ""}
    assert row_drop_reason(row) == DROP_REASON_MONTH_HEADER


def test_schedule_postponed_not_used_for_valid_game_row() -> None:
    row = {
        "date_game": "Wed, Oct 25, 2023",
        "visitor_team_name": "Boston Celtics",
        "home_team_name": "New York Knicks",
        "game_remarks": "",
        "box_score_text": "Box Score",
    }
    assert row_drop_reason(row) is None


def test_league_per_game_repeated_header_via_validation() -> None:
    raw_rows = [
        {"name_display": "player", "team_name_abbr": "team", "pts": "pts"},
        {"name_display": "Tatum", "team_name_abbr": "BOS", "pts": 26},
    ]

    class LeagueRow(BaseModel):
        name_display: str
        team_name_abbr: str | None = None
        pts: int

    validated, dropped = _validate_row_model_rows(LeagueRow, raw_rows)
    assert len(validated) == 1
    assert dropped == {DROP_REASON_REPEATED_HEADER: 1}


def test_draft_pick_missing_required_field() -> None:
    validated, dropped = _validate_row_model_rows(_SampleRow, [{"pts": 1}, {"player": "A", "pts": 2}])
    assert len(validated) == 1
    assert dropped == {DROP_REASON_INVALID_PLAYER_VALUE: 1}


def test_players_totals_combined_team_preclassified() -> None:
    row = {"name_display": "Player", "team_name_abbr": "3TM", "pts": "10"}
    assert row_drop_reason(row) == DROP_REASON_COMBINED_TEAM


def test_team_on_off_blank_split_rows() -> None:
    row = {"player": "", "split_id": "", "mp": ""}
    assert row_drop_reason(row) == DROP_REASON_BLANK_ROW


def test_validation_invalid_date_reason() -> None:
    from pydantic import ValidationError

    class DateRow(BaseModel):
        date_game: str

    try:
        DateRow.model_validate({"date_game": object()})
    except ValidationError as exc:
        reason = validation_error_drop_reason(exc.errors(), row={"date_game": object()})
    else:
        raise AssertionError("expected validation error")
    assert reason in {DROP_REASON_INVALID_DATE, DROP_REASON_INVALID_VALUE}


def test_validation_invalid_team_reason() -> None:
    from pydantic import ValidationError

    try:
        _TeamRow.model_validate({"team_name_abbr": "NOT_A_REAL_TEAM", "player": "X"})
    except ValidationError as exc:
        reason = validation_error_drop_reason(exc.errors(), row={"team_name_abbr": "NOT_A_REAL_TEAM", "player": "X"})
    else:
        raise AssertionError("expected validation error")
    assert reason == DROP_REASON_INVALID_TEAM_VALUE


def test_probe_csv_includes_data_quality_fields() -> None:
    evaluated = _with_evaluation(
        {
            "endpoint": "team_roster",
            "ok": True,
            "dropped_row_count": 2,
            "dropped_row_reason_counts_json": {"repeated_header": 2},
            "metrics": {"trace.truncated_artifact_count": 1},
        }
    )
    row = _csv_row(evaluated)
    assert row["data_quality_status"] == DATA_QUALITY_WARNINGS
    assert row["expected_drop_count"] == "2"
    assert row["unexpected_drop_count"] == "0"
    assert row["drop_rate_warning"] == "false"
    assert row["trace_truncated_artifact_count"] == "1"


def test_data_quality_lossy_on_invalid_value_drops() -> None:
    quality = evaluate_data_quality(
        ok=True,
        dropped_row_count=3,
        dropped_row_reason_counts={"invalid_value": 3},
    )
    assert quality["data_quality_status"] == DATA_QUALITY_LOSSY
    assert quality["unexpected_drop_count"] == 3


def test_data_quality_clean_when_no_drops() -> None:
    quality = evaluate_data_quality(ok=True, dropped_row_count=0, dropped_row_reason_counts={})
    assert quality["data_quality_status"] == DATA_QUALITY_CLEAN


def test_sentinel_rows_drop_with_specific_reason() -> None:
    raw_rows = [{"player": "did not play", "pts": "bad"}, {"player": "Tatum", "pts": 26}]
    validated, dropped = _validate_row_model_rows(_SampleRow, raw_rows)
    assert len(validated) == 1
    assert dropped == {DROP_REASON_UNSUPPORTED_SENTINEL_VALUE: 1}
