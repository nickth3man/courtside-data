from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import pytest
from courtside_data.client._pipelines._drop_reasons import DROP_REASON_INVALID_TEAM_VALUE
from courtside_data.client._pipelines.pydantic import _validate_row_model_rows_detailed
from courtside_data.debug.probe import _summarize_debug_events, probe_endpoints
from courtside_data.debug.probe import main as probe_main
from courtside_data.debug.provenance import (
    PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN,
    PROVENANCE_SCHEMA_DEFAULT_USED,
    PROVENANCE_SOURCE_CELL_BLANK,
    PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL,
    PROVENANCE_SOURCE_COLUMN_ABSENT,
    PROVENANCE_SOURCE_VALUE_PRESENT,
    PROVENANCE_VALIDATOR_TRANSFORMED_VALUE,
    ProvenanceContext,
    build_dropped_row_provenance_records,
    build_field_provenance_records,
    build_source_table_snapshot,
    record_table_provenance,
)
from courtside_data.debug.trace import DebugTrace
from courtside_data.endpoints import ENDPOINTS
from courtside_data.parsing.generic import find_table
from courtside_data.parsing.tables import GenericTable
from courtside_data.schemas._fields import TeamField
from courtside_data.schemas.draft import DraftPicksRow
from courtside_data.schemas.league import RookieStatsRow
from parsel import Selector
from pydantic import BaseModel, BeforeValidator, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOKIE_STATS_1980_FIXTURE = PROJECT_ROOT / "raw" / "rookie_stats" / "1980.html"
DRAFT_PICKS_1965_FIXTURE = PROJECT_ROOT / "raw" / "draft_picks" / "1965.html"


def _none_for_empty_or_dash(value: Any) -> Any:
    if isinstance(value, str) and value.strip() in {"", "-"}:
        return None
    return value


def _uppercase(value: Any) -> Any:
    if isinstance(value, str):
        return value.upper()
    return value


class _FieldProvenanceRow(BaseModel):
    player: str = Field(validation_alias="player")
    blank_pct: Annotated[float | None, BeforeValidator(_none_for_empty_or_dash)] = Field(
        default=None,
        validation_alias="blank_pct",
    )
    dash_pct: Annotated[float | None, BeforeValidator(_none_for_empty_or_dash)] = Field(
        default=None,
        validation_alias="dash_pct",
    )
    transformed_name: Annotated[str, BeforeValidator(_uppercase)] = Field(validation_alias="transformed_name")
    missing_source: str | None = Field(default=None, validation_alias="missing_source")
    parser_omitted: str | None = Field(default=None, validation_alias="parser_omitted")
    schema_default: list[str] = Field(default_factory=list, validation_alias="schema_default")


class _TeamRow(BaseModel):
    team: TeamField = Field(validation_alias="team_id")
    player: str


def test_source_table_snapshot_extracts_normal_table_blank_and_dash_cells() -> None:
    html = """
    <table id="stats">
      <thead><tr>
        <th data-stat="player">Player</th>
        <th data-stat="blank_pct">Blank%</th>
        <th data-stat="dash_pct">Dash%</th>
      </tr></thead>
      <tbody><tr>
        <th data-stat="player">Example Player</th>
        <td data-stat="blank_pct"> </td>
        <td data-stat="dash_pct">-</td>
      </tr></tbody>
    </table>
    """
    table = Selector(text=html).css("table#stats")[0]

    snapshot = build_source_table_snapshot(
        table,
        endpoint_name="example",
        params={},
        table_source="table_id",
        use_header_fallback=False,
        exclude_summary_rows=False,
    )

    assert snapshot.source_table_id == "stats"
    assert snapshot.raw_data_stat_columns == ["player", "blank_pct", "dash_pct"]
    blank_cell = snapshot.cell(0, "blank_pct")
    dash_cell = snapshot.cell(0, "dash_pct")
    assert blank_cell is not None
    assert dash_cell is not None
    assert blank_cell.raw_text == " "
    assert dash_cell.raw_text == "-"


def test_source_table_snapshot_extracts_commented_table() -> None:
    html = """
    <html><body>
      <!--
      <table id="commented">
        <thead><tr><th data-stat="player">Player</th></tr></thead>
        <tbody><tr><td data-stat="player">Hidden Player</td></tr></tbody>
      </table>
      -->
    </body></html>
    """
    selector = Selector(text=html)
    table = find_table(selector, "commented")
    assert table is not None

    snapshot = build_source_table_snapshot(
        table,
        endpoint_name="commented_endpoint",
        params={},
        table_source="commented_table",
        use_header_fallback=False,
        exclude_summary_rows=False,
    )

    assert snapshot.source_table_id == "commented"
    assert snapshot.source_keys == {"player"}
    player_cell = snapshot.cell(0, "player")
    assert player_cell is not None
    assert player_cell.raw_text == "Hidden Player"


def test_generic_field_provenance_classifies_source_parser_validator_and_defaults() -> None:
    html = """
    <table id="stats">
      <thead><tr>
        <th data-stat="player">Player</th>
        <th data-stat="blank_pct">Blank%</th>
        <th data-stat="dash_pct">Dash%</th>
        <th data-stat="transformed_name">Name</th>
        <th data-stat="parser_omitted">Parser Miss</th>
      </tr></thead>
      <tbody><tr>
        <th data-stat="player">Ada</th>
        <td data-stat="blank_pct"> </td>
        <td data-stat="dash_pct">-</td>
        <td data-stat="transformed_name">ada</td>
        <td data-stat="parser_omitted">source-only</td>
      </tr></tbody>
    </table>
    """
    table = Selector(text=html).css("table#stats")[0]
    snapshot = build_source_table_snapshot(
        table,
        endpoint_name="example",
        params={},
        table_source="table_id",
        use_header_fallback=False,
        exclude_summary_rows=False,
    )
    raw_rows = [
        {
            "player": "Ada",
            "blank_pct": " ",
            "dash_pct": "-",
            "transformed_name": "ada",
        }
    ]
    validated = [_FieldProvenanceRow.model_validate(raw_rows[0])]

    records = build_field_provenance_records(
        endpoint_name="example",
        endpoint_params={},
        row_model=_FieldProvenanceRow,
        raw_rows=raw_rows,
        validated_rows=validated,
        kept_row_indices=[0],
        context=ProvenanceContext(source_snapshot=snapshot),
        custom=False,
    )
    by_field = {record["field_name"]: record for record in records}

    assert by_field["player"]["provenance_reason"] == PROVENANCE_SOURCE_VALUE_PRESENT
    assert by_field["blank_pct"]["provenance_reason"] == PROVENANCE_SOURCE_CELL_BLANK
    assert by_field["dash_pct"]["provenance_reason"] == PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL
    assert by_field["transformed_name"]["provenance_reason"] == PROVENANCE_VALIDATOR_TRANSFORMED_VALUE
    assert by_field["parser_omitted"]["provenance_reason"] == PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN
    assert by_field["missing_source"]["provenance_reason"] == PROVENANCE_SOURCE_COLUMN_ABSENT
    assert by_field["missing_source"]["schema_default_used"] is True


def test_field_provenance_classifies_schema_default_when_source_metadata_unavailable() -> None:
    raw_rows = [{"player": "Ada", "transformed_name": "Ada"}]
    validated = [_FieldProvenanceRow.model_validate(raw_rows[0])]

    records = build_field_provenance_records(
        endpoint_name="example",
        endpoint_params={},
        row_model=_FieldProvenanceRow,
        raw_rows=raw_rows,
        validated_rows=validated,
        kept_row_indices=[0],
        context=None,
        custom=False,
    )
    by_field = {record["field_name"]: record for record in records}

    assert by_field["schema_default"]["provenance_reason"] == PROVENANCE_SCHEMA_DEFAULT_USED
    assert by_field["schema_default"]["schema_default_used"] is True


def test_dropped_row_provenance_captures_invalid_team_raw_value_and_source_cell() -> None:
    html = """
    <table id="stats">
      <thead><tr>
        <th data-stat="player">Player</th>
        <th data-stat="team_id">Team</th>
      </tr></thead>
      <tbody><tr>
        <td data-stat="player">Mystery Player</td>
        <td data-stat="team_id">NOT_A_REAL_TEAM</td>
      </tr></tbody>
    </table>
    """
    table = Selector(text=html).css("table#stats")[0]
    snapshot = build_source_table_snapshot(
        table,
        endpoint_name="example",
        params={},
        table_source="table_id",
        use_header_fallback=False,
        exclude_summary_rows=False,
    )
    raw_rows = [{"player": "Mystery Player", "team_id": "NOT_A_REAL_TEAM"}]
    validated, dropped, kept_indices, dropped_details, drift_errors = _validate_row_model_rows_detailed(
        _TeamRow,
        raw_rows,
    )

    assert validated == []
    assert kept_indices == []
    assert drift_errors == []
    assert dropped == {DROP_REASON_INVALID_TEAM_VALUE: 1}

    records = build_dropped_row_provenance_records(
        endpoint_name="example",
        endpoint_params={},
        raw_rows=raw_rows,
        dropped=dropped_details,
        context=ProvenanceContext(source_snapshot=snapshot),
        custom=False,
    )

    assert records[0]["validation_error_drop_reason"] == DROP_REASON_INVALID_TEAM_VALUE
    assert records[0]["raw_values"] == {"team_id": "NOT_A_REAL_TEAM"}
    assert records[0]["source_cells"]["team_id"]["source_cell_raw"] == "NOT_A_REAL_TEAM"


def test_unresolved_dropped_row_provenance_records_schema_validation_error() -> None:
    class _PointsRow(BaseModel):
        player: str
        pts: int

    raw_rows = [{"player": "Mystery Player", "pts": object()}]
    validated, dropped, _kept_indices, dropped_details, drift_errors = _validate_row_model_rows_detailed(
        _PointsRow,
        raw_rows,
    )

    assert validated == []
    assert dropped == {"schema_validation_error": 1}
    assert drift_errors

    records = build_dropped_row_provenance_records(
        endpoint_name="example",
        endpoint_params={},
        raw_rows=raw_rows,
        dropped=dropped_details,
        context=None,
        custom=False,
    )

    assert records[0]["unresolved_drop"] is True
    assert records[0]["raw_values"] == {"pts": raw_rows[0]["pts"]}


def test_probe_summary_consumes_provenance_events() -> None:
    trace = DebugTrace(endpoint="team_roster", params={})
    trace.record(
        "provenance",
        "source_table_provenance",
        parser_missed_column_count=2,
    )
    trace.record(
        "provenance",
        "custom_endpoint_provenance",
        source_cell_mapping_available=False,
        provenance_reason="custom_parser_metadata_unavailable",
    )
    trace.record(
        "provenance",
        "field_provenance_summary",
        provenance_field_count=4,
        provenance_final_none_count=2,
        provenance_reason_counts={"source_value_present": 2, "source_column_absent": 2},
        provenance_none_reason_counts={"source_column_absent": 2},
        parser_missed_column_count=2,
        schema_defaulted_field_count=2,
        validator_coerced_field_count=1,
        validator_transformed_field_count=1,
        provenance_dropped_row_count=1,
        provenance_dropped_row_reason_counts={"invalid_team_value": 1},
        provenance_unresolved_drop_count=0,
        custom_provenance_unavailable_count=0,
    )

    summary = _summarize_debug_events(trace.to_dict(), endpoint_name="team_roster")

    assert summary["provenance_field_count"] == 4
    assert summary["provenance_none_reason_counts_json"] == {"source_column_absent": 2}
    assert summary["parser_missed_column_count"] == 2
    assert summary["provenance_dropped_row_reason_counts_json"] == {"invalid_team_value": 1}
    assert summary["custom_provenance_unavailable_count"] == 1


def test_probe_params_override_requires_single_endpoint(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="exactly one"):
        probe_endpoints(
            endpoints=["team_roster", "rookie_stats"],
            output_path=tmp_path / "probe.json",
            params_override={"season_end_year": 1980},
        )


def test_probe_params_json_rejects_non_object() -> None:
    assert probe_main(["-e", "rookie_stats", "--params-json", "[]"]) == 2


@pytest.mark.skipif(not ROOKIE_STATS_1980_FIXTURE.exists(), reason="1980 rookie_stats fixture missing")
def test_rookie_stats_1980_selected_source_table_has_no_team_column() -> None:
    html = ROOKIE_STATS_1980_FIXTURE.read_text(encoding="utf-8")
    table_id = ENDPOINTS["rookie_stats"].table_id
    assert table_id is not None
    table = find_table(Selector(text=html), table_id)
    assert table is not None

    snapshot = build_source_table_snapshot(
        table,
        endpoint_name="rookie_stats",
        params={"season_end_year": 1980},
        table_source="table_id",
        use_header_fallback=False,
        exclude_summary_rows=False,
    )
    trace = DebugTrace(endpoint="rookie_stats", params={"season_end_year": 1980})
    parser_rows = [row.to_dict() for row in GenericTable(table).rows]
    record_table_provenance(
        trace,
        snapshot=snapshot,
        row_model=RookieStatsRow,
        parser_rows_before_projection=parser_rows,
        parser_rows_after_projection=parser_rows,
    )

    team_like_keys = {"team", "tm", "team_id", "team_name_abbr", "team_name", "franch_id"}
    assert snapshot.source_keys.isdisjoint(team_like_keys)
    assert set(snapshot.raw_data_stat_columns).isdisjoint(team_like_keys)

    validated, _dropped, kept_indices, _dropped_details, _drift_errors = _validate_row_model_rows_detailed(
        RookieStatsRow,
        parser_rows,
    )
    records = build_field_provenance_records(
        endpoint_name="rookie_stats",
        endpoint_params={"season_end_year": 1980},
        row_model=RookieStatsRow,
        raw_rows=parser_rows,
        validated_rows=validated,
        kept_row_indices=kept_indices,
        context=ProvenanceContext(source_snapshot=snapshot),
        custom=False,
    )
    team_records = [record for record in records if record["field_name"] == "team"]

    assert team_records
    assert {record["provenance_reason"] for record in team_records} == {PROVENANCE_SOURCE_COLUMN_ABSENT}


@pytest.mark.skipif(not DRAFT_PICKS_1965_FIXTURE.exists(), reason="1965 draft_picks fixture missing")
def test_draft_picks_1965_historical_team_abbreviations_validate() -> None:
    """BAL (1963-73 Baltimore Bullets) and CIN (Cincinnati Royals) are real
    historical drafting teams that were previously dropped as
    ``invalid_team_value``. They must now validate against the team lookup so
    no source row is lost to an unknown team abbreviation."""
    html = DRAFT_PICKS_1965_FIXTURE.read_text(encoding="utf-8")
    table_id = ENDPOINTS["draft_picks"].table_id
    assert table_id is not None
    table = find_table(Selector(text=html), table_id)
    assert table is not None

    parser_rows = [row.to_dict() for row in GenericTable(table).rows]
    # The 1965 draft table carries 112 pick rows; none should be a team drop.
    historical_team_abbrs = {row["team_id"] for row in parser_rows if row.get("team_id") in {"BAL", "CIN"}}
    assert {"BAL", "CIN"} <= historical_team_abbrs

    validated, dropped, _kept_indices, _dropped_details, _drift_errors = _validate_row_model_rows_detailed(
        DraftPicksRow,
        parser_rows,
    )

    assert dropped.get(DROP_REASON_INVALID_TEAM_VALUE, 0) == 0
    # Every source row is retained (no team-driven loss).
    assert len(validated) == len(parser_rows)
    # BAL/CIN rows resolve to the expected historical Team enum values.
    from courtside_data.data import Team

    validated_teams = {row.team for row in validated if row.team is not None}
    assert Team.BALTIMORE_BULLETS in validated_teams
    assert Team.CINCINNATI_ROYALS in validated_teams


@pytest.mark.skipif(not DRAFT_PICKS_1965_FIXTURE.exists(), reason="1965 draft_picks fixture missing")
def test_draft_picks_1965_invalid_team_provenance_captures_source_team_values() -> None:
    """The provenance machinery must still capture raw source team cells when a
    genuinely invalid team abbreviation appears. BAL/CIN now validate, so this
    is exercised with a synthetic unknown abbreviation spliced into the 1965
    rows (the real 1965 fixture no longer produces team drops)."""
    html = DRAFT_PICKS_1965_FIXTURE.read_text(encoding="utf-8")
    table_id = ENDPOINTS["draft_picks"].table_id
    assert table_id is not None
    table = find_table(Selector(text=html), table_id)
    assert table is not None

    snapshot = build_source_table_snapshot(
        table,
        endpoint_name="draft_picks",
        params={"season_end_year": 1965},
        table_source="table_id",
        use_header_fallback=False,
        exclude_summary_rows=False,
    )
    parser_rows = [row.to_dict() for row in GenericTable(table).rows]
    # Inject a genuinely unknown team abbreviation to exercise the drop path.
    parser_rows[0] = {**parser_rows[0], "team_id": "NOT_A_REAL_TEAM"}

    validated, dropped, _kept_indices, dropped_details, _drift_errors = _validate_row_model_rows_detailed(
        DraftPicksRow,
        parser_rows,
    )

    assert dropped.get(DROP_REASON_INVALID_TEAM_VALUE, 0) > 0
    assert len(validated) == len(parser_rows) - 1

    records = build_dropped_row_provenance_records(
        endpoint_name="draft_picks",
        endpoint_params={"season_end_year": 1965},
        raw_rows=parser_rows,
        dropped=dropped_details,
        context=ProvenanceContext(source_snapshot=snapshot),
        custom=False,
    )
    invalid_team_records = [
        record for record in records if record["validation_error_drop_reason"] == DROP_REASON_INVALID_TEAM_VALUE
    ]

    assert invalid_team_records
    assert all(record["raw_values"]["team_id"] for record in invalid_team_records)
    assert all(record["source_cells"]["team_id"]["source_cell_raw"] for record in invalid_team_records)
