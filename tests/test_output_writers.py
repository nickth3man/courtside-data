"""Offline CSV/JSON writer regression tests (replaces live e2e file comparisons).

Golden files live under ``tests/golden/writers/``. On first run, missing
files are written for review and the test skips.
"""

from __future__ import annotations

import csv
import filecmp
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from courtside_data.domain import TEAM_ABBREVIATIONS_TO_TEAM, OutputType, OutputWriteOption
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import InvalidTeam
from courtside_data.output.fields import format_value
from courtside_data.output.service import OutputService
from courtside_data.output.writers import (
    CSVWriter,
    DataFrameWriter,
    FileOptions,
    JSONWriter,
    OutputOptions,
    _serialize_row_models,
)
from courtside_data.schemas import boxscores
from pydantic import BaseModel

from tests.fixture_manifest import ALL_CASES, ERROR_CASES, MULTI_REQUEST_CASES, Case

GOLDEN_DIR = Path(__file__).parent / "golden" / "writers"


@dataclass(frozen=True, slots=True)
class WriterCase:
    case_id: str
    output_type: OutputType
    extension: str


WRITER_CASES: tuple[WriterCase, ...] = (
    WriterCase("player_box_scores-1-1-2018", OutputType.CSV, "csv"),
    WriterCase("player_box_scores-1-1-2018", OutputType.JSON, "json"),
    WriterCase("play_by_play-1-ATL-1-2017", OutputType.CSV, "csv"),
    WriterCase("play_by_play-1-ATL-1-2017", OutputType.JSON, "json"),
)

_CASE_BY_ID: dict[str, Case] = {case.id: case for case in ALL_CASES}

_BOX_SCORE_CSV_CONTRACT_CASES = (
    ("player_box_scores", "player_box_scores-1-1-2018", boxscores.PlayerBoxScoreRow),
    ("team_box_scores", "team_box_scores-1-1-2001", boxscores.TeamBoxScoreRow),
    (
        "regular_season_player_box_scores",
        "regular_season_player_box_scores-false-westbru01-2020",
        boxscores.RegularSeasonPlayerBoxScoreRow,
    ),
    (
        "playoff_player_box_scores",
        "playoff_player_box_scores-false-westbru01-2020",
        boxscores.PlayoffPlayerBoxScoreRow,
    ),
)


def _resolved_params(case: Case) -> dict:
    params = dict(case.params)
    if case.endpoint_name == "play_by_play":
        abbr = params.pop("home_team")
        params["home_team"] = TEAM_ABBREVIATIONS_TO_TEAM[abbr]
    return params


@pytest.mark.parametrize("writer_case", WRITER_CASES, ids=[f"{wc.case_id}.{wc.extension}" for wc in WRITER_CASES])
def test_writer_output_matches_golden(writer_case: WriterCase, make_offline_client, tmp_path: Path) -> None:
    case = _CASE_BY_ID.get(writer_case.case_id)
    if case is None:
        pytest.fail(f"Writer case id not found in manifest: {writer_case.case_id}")

    output_path = tmp_path / f"out.{writer_case.extension}"
    client = make_offline_client(case)
    getattr(client, case.endpoint_name)(
        **_resolved_params(case),
        output_type=writer_case.output_type,
        output_file_path=str(output_path),
        output_write_option=OutputWriteOption.WRITE,
    )

    golden_path = GOLDEN_DIR / f"{writer_case.case_id}.{writer_case.extension}"
    if not golden_path.exists():
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        golden_path.write_bytes(output_path.read_bytes())
        pytest.skip(f"Generated writer golden: {golden_path.relative_to(Path(__file__).parent)}")

    assert filecmp.cmp(output_path, golden_path, shallow=False), (
        f"Writer output drift for {writer_case.case_id}.{writer_case.extension}"
    )


def test_writer_case_ids_exist_in_manifest() -> None:
    missing = [wc.case_id for wc in WRITER_CASES if wc.case_id not in _CASE_BY_ID]
    assert not missing, f"Writer golden case ids missing from manifest: {missing}"


@pytest.mark.parametrize(
    ("endpoint_name", "case_id", "row_model"),
    _BOX_SCORE_CSV_CONTRACT_CASES,
    ids=[endpoint_name for endpoint_name, _, _ in _BOX_SCORE_CSV_CONTRACT_CASES],
)
def test_box_score_endpoint_csv_columns_match_row_model(
    endpoint_name: str,
    case_id: str,
    row_model: type[BaseModel],
) -> None:
    endpoint = ENDPOINTS[endpoint_name]

    assert case_id in _CASE_BY_ID
    assert list(endpoint.csv_columns or ()) == list(row_model.model_fields)


@pytest.mark.parametrize(
    ("endpoint_name", "case_id", "row_model"),
    _BOX_SCORE_CSV_CONTRACT_CASES,
    ids=[endpoint_name for endpoint_name, _, _ in _BOX_SCORE_CSV_CONTRACT_CASES],
)
def test_box_score_csv_output_fields_match_row_model(
    endpoint_name: str,
    case_id: str,
    row_model: type[BaseModel],
    make_offline_client,
    tmp_path: Path,
) -> None:
    case = _CASE_BY_ID[case_id]
    output_path = tmp_path / f"{endpoint_name}.csv"
    client = make_offline_client(case)

    getattr(client, endpoint_name)(
        **case.params,
        output_type=OutputType.CSV,
        output_file_path=str(output_path),
        output_write_option=OutputWriteOption.WRITE,
    )

    with output_path.open(newline="", encoding="utf8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    expected_fields = list(row_model.model_fields)
    assert reader.fieldnames == expected_fields
    assert rows
    assert all(list(row) == expected_fields for row in rows)


def test_multi_request_cases_non_empty() -> None:
    assert MULTI_REQUEST_CASES, "Expected resolved multi-request manifest cases"


def test_output_options_unknown_type_raises() -> None:
    with pytest.raises(ValueError, match="Unknown output type"):
        OutputOptions.of(
            file_options=FileOptions.of(path="out.txt"),
            output_type=object(),  # type: ignore[arg-type]
        )


def test_output_service_unknown_type_raises() -> None:
    service = OutputService(
        json_writer=JSONWriter(),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    options = OutputOptions(
        file_options=FileOptions.of(path="out.txt"),
        formatting_options={},
        output_type=object(),  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError, match="Unknown output type"):
        service.output(data=[], options=options)


def test_dataframe_writer_rejects_file_output(tmp_path: Path) -> None:
    writer = DataFrameWriter()
    options = OutputOptions.of(
        file_options=FileOptions.of(path=str(tmp_path / "frame.csv")),
        output_type=OutputType.DATAFRAME,
        csv_options={"column_names": ["a"]},
    )
    with pytest.raises(ValueError, match="output_file_path is not supported"):
        writer.write([{"a": 1}], options)


def test_csv_writer_writes_header_only_for_empty_rows(tmp_path: Path) -> None:
    writer = CSVWriter(value_formatter=format_value)
    output_path = tmp_path / "empty.csv"
    options = OutputOptions.of(
        file_options=FileOptions.of(path=str(output_path)),
        output_type=OutputType.CSV,
        csv_options={"column_names": ["col_a", "col_b"]},
    )
    writer.write([], options)
    assert output_path.read_text(encoding="utf8") == "col_a,col_b\n"


def test_serialize_row_models_passthrough_scalar() -> None:
    assert _serialize_row_models(42) == 42
    assert _serialize_row_models("plain") == "plain"


def test_json_writer_serializes_scalar_data() -> None:
    writer = JSONWriter()
    options = OutputOptions.of(
        file_options=FileOptions.of(path=None),
        output_type=OutputType.JSON,
    )
    assert writer.write("plain", options) == '"plain"'


def test_debug_mode_flushes_trace_on_success(make_offline_client, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("COURTSIDE_DEBUG_LOG_DIR", str(tmp_path))
    case = _CASE_BY_ID.get("player_box_scores-1-1-2018")
    if case is None:
        pytest.fail("player_box_scores-1-1-2018 fixture not in manifest")

    client = make_offline_client(case)
    envelope = client.player_box_scores(**case.params, debug=True)

    assert isinstance(envelope, dict)
    assert "data" in envelope
    assert "debug" in envelope

    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    log_data = json.loads(log_files[0].read_text(encoding="utf8"))
    assert "debug" in log_data
    assert log_data["debug"]["endpoint"] == "player_box_scores"
    assert log_data["debug"]["status"]["code"] == "ok"


def test_debug_mode_flushes_trace_on_failure(make_offline_client, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("COURTSIDE_DEBUG_LOG_DIR", str(tmp_path))
    case = next(case for case in ERROR_CASES if case.endpoint_name == "error-invalid_team")
    client = make_offline_client(case)

    with pytest.raises(InvalidTeam):
        client.team_roster(**case.params, debug=True)

    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    log_data = json.loads(log_files[0].read_text(encoding="utf8"))
    assert log_data["data"] is None
    assert log_data["debug"]["status"]["code"] == "error"
    assert log_data["debug"]["status"]["error_type"] == "InvalidTeam"
