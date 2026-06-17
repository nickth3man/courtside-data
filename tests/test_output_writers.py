"""Offline CSV/JSON writer regression tests (replaces live e2e file comparisons).

Golden files live under ``tests/golden/writers/``. On first run, missing
files are written for review and the test skips.
"""

from __future__ import annotations

import filecmp
from dataclasses import dataclass
from pathlib import Path

import pytest

from courtside_data.data import TEAM_ABBREVIATIONS_TO_TEAM, OutputType, OutputWriteOption
from tests.fixture_manifest import ALL_CASES, MULTI_REQUEST_CASES, Case

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


def test_multi_request_cases_non_empty() -> None:
    assert MULTI_REQUEST_CASES, "Expected resolved multi-request manifest cases"
