"""Team Hub CSV column-ordering contract tests.

These tests pin the team-hub CSV export's header row to the
:class:`~courtside_data.endpoints.EndpointSpec` ``csv_columns`` declaration
in :mod:`courtside_data.endpoints._teams`. The contract is: for every team
endpoint with a non-empty ``csv_columns`` sequence, the CSV header row of
:meth:`TeamHubService.csv` MUST equal ``list(endpoint.csv_columns)`` byte-
for-byte. The fixture transport for team endpoints is intentionally not
wired, so the tests use a small in-memory double that bypasses
:meth:`TeamHubService._run` and feeds the serializer a controlled row.
"""

from __future__ import annotations

import csv
import io

import pytest
from courtside_data.endpoints import ENDPOINTS
from courtside_data.server.team_catalog import TEAM_DATASETS
from courtside_data.server.team_service import TeamHubService


class _FakeRow:
    """Minimal Pydantic-like row double for the CSV serializer path.

    Implements only :meth:`model_dump` (the method
    :meth:`TeamHubService._serialize_rows` calls); the dict it returns
    is built from the keys the test wants to expose.
    """

    def __init__(self, **payload: object) -> None:
        self._payload = payload

    def model_dump(self, mode: str = "python") -> dict[str, object]:
        return dict(self._payload)


class _FakeTeamHubService(TeamHubService):
    """Test double: bypass the fixture transport and return controlled rows."""

    def __init__(self, fake_rows: list[object]) -> None:
        super().__init__(transport="fixture")
        self._fake_rows = fake_rows

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[object]:
        return list(self._fake_rows)


def _team_endpoint_datasets() -> list:
    """Filter :data:`TEAM_DATASETS` to those whose EndpointSpec has csv_columns declared."""
    return [dataset for dataset in TEAM_DATASETS if ENDPOINTS[dataset.endpoint_name].csv_columns]


@pytest.mark.parametrize("dataset", _team_endpoint_datasets(), ids=lambda dataset: dataset.id)
def test_csv_header_matches_endpoint_spec_csv_columns(dataset) -> None:
    """The first row of the CSV export must equal ``list(spec.csv_columns)``.

    Pinning the header to the EndpointSpec declaration makes the contract
    independent of the row payload (which is the player-hub pattern;
    see :meth:`PlayerHubService.csv_for_dataset`).

    The fake row is built with the keys in **reversed** order to catch the
    "fall back to ``rows[0].keys()``" code path: if a future refactor
    drops the ``endpoint.csv_columns`` short-circuit, the CSV header will
    follow the row's key order (reversed) and the test will fail loudly.
    """
    endpoint = ENDPOINTS[dataset.endpoint_name]
    csv_columns = endpoint.csv_columns
    assert csv_columns, f"{dataset.endpoint_name!r} has empty csv_columns; the parametrize filter should skip it"
    expected_header = list(csv_columns)

    # Build one fake row carrying every declared csv_column key in
    # REVERSED order, so the spec-driven order and the row-driven order
    # are observably different.
    reversed_keys = list(reversed(expected_header))
    fake_row = _FakeRow(**{key: f"v_{key}" for key in reversed_keys})
    service = _FakeTeamHubService(fake_rows=[fake_row])
    output = service.csv(
        team_identifier="BOS",
        dataset_id=dataset.id,
        season_end_year=2024,
        include_inactive_games=False,
    )
    # csv.DictWriter always writes a header (the first line) before the
    # data rows; read it back via csv.reader for whitespace-safe parsing.
    first_line = output.splitlines()[0]
    header = next(csv.reader(io.StringIO(first_line)))
    assert header == expected_header, (
        f"{dataset.endpoint_name!r}: CSV header drifts from EndpointSpec.csv_columns; "
        f"expected={expected_header!r}, got={header!r}"
    )


def test_csv_header_is_deterministic_for_repeated_calls() -> None:
    """The header must be stable across calls (no dict-insertion order surprises)."""
    dataset = next(d for d in TEAM_DATASETS if d.id == "roster")
    endpoint = ENDPOINTS[dataset.endpoint_name]
    csv_columns = endpoint.csv_columns
    assert csv_columns, "roster dataset has no csv_columns declared"
    expected_header = list(csv_columns)
    reversed_keys = list(reversed(expected_header))
    fake_row = _FakeRow(**{key: f"v_{key}" for key in reversed_keys})
    service = _FakeTeamHubService(fake_rows=[fake_row])
    first = service.csv(
        team_identifier="BOS", dataset_id=dataset.id, season_end_year=2024, include_inactive_games=False
    )
    second = service.csv(
        team_identifier="BOS", dataset_id=dataset.id, season_end_year=2024, include_inactive_games=False
    )
    first_header = next(csv.reader(io.StringIO(first.splitlines()[0])))
    second_header = next(csv.reader(io.StringIO(second.splitlines()[0])))
    assert first_header == second_header == expected_header
