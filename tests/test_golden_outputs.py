"""Tier-2 golden-output tests for a curated subset of offline cases.

On first run, missing golden JSON files are written automatically so callers
can review and commit them. Subsequent runs compare actual output to the
saved golden via :mod:`deepdiff` for readable drift failures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from courtside_data.endpoints import ENDPOINTS
from deepdiff import DeepDiff

from tests.fixture_manifest import GENERIC_CASES, Case

GOLDEN_DIR = Path(__file__).parent / "golden"

# Curated, stable cases spanning league / team / player tables (all Tier-1 green).
GOLDEN_CASE_IDS: tuple[str, ...] = (
    "draft_picks-2024",
    "team_roster-2024-BOS",
    "league_per_game_stats-2024",
    "player_career_stats-jamesle01",
    "team_injury_report-2024-BOS",
)

_CASE_BY_ID: dict[str, Case] = {case.id: case for case in GENERIC_CASES}


def _resolve_golden_cases() -> list[Case]:
    missing = [case_id for case_id in GOLDEN_CASE_IDS if case_id not in _CASE_BY_ID]
    if missing:
        pytest.fail(f"Golden case ids not found in GENERIC_CASES: {missing}")
    return [_CASE_BY_ID[case_id] for case_id in GOLDEN_CASE_IDS]


_GOLDEN_CASES = _resolve_golden_cases()


def _serialize_rows(rows: list[Any]) -> list[dict[str, Any]]:
    return [row.model_dump(mode="json") for row in rows]


@pytest.mark.parametrize("case", _GOLDEN_CASES, ids=[case.id for case in _GOLDEN_CASES])
def test_golden_output(case: Case, make_offline_client) -> None:
    client = make_offline_client(case)
    result = getattr(client, case.endpoint_name)(**case.params)

    endpoint = ENDPOINTS[case.endpoint_name]
    assert endpoint.row_model is not None
    assert isinstance(result, list)
    assert result

    actual = _serialize_rows(result)
    golden_path = GOLDEN_DIR / f"{case.id}.json"

    if not golden_path.exists():
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        golden_path.write_text(f"{json.dumps(actual, indent=2, sort_keys=True)}\n", encoding="utf-8")
        pytest.skip(f"Generated golden fixture: {golden_path.relative_to(Path(__file__).parent)}")

    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    diff = DeepDiff(expected, actual, ignore_order=True)
    assert not diff, f"Golden drift for {case.id}:\n{diff.pretty()}"
