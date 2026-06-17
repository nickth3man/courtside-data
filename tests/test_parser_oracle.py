"""Second-parser oracle: selectolax (Lexbor) vs parsel (lxml) table discovery.

Reads fixture HTML directly from ``/raw`` — no transport, no conftest
dependency. If the two parsers disagree on which table exists or how many
data rows it contains, Basketball-Reference markup drift may break production
parsing before pydantic validation catches it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from courtside_data.endpoints import ENDPOINTS
from courtside_data.http_service import _xpath_literal
from parsel import Selector
from selectolax.parser import HTMLParser

from tests.fixture_manifest import ALL_CASES
from tests.fixture_transport import FixtureValue


@dataclass(frozen=True, slots=True)
class _OracleTarget:
    case_id: str
    html_path: Path
    table_id: str


def _fixture_path(value: FixtureValue) -> Path | None:
    return value if isinstance(value, Path) else None


def _build_oracle_targets() -> list[_OracleTarget]:
    """One representative case per generic endpoint with a ``table_id``."""
    seen: set[str] = set()
    targets: list[_OracleTarget] = []
    for case in ALL_CASES:
        if case.endpoint_name in seen:
            continue
        endpoint = ENDPOINTS[case.endpoint_name]
        if endpoint.custom or endpoint.table_id is None:
            continue
        html_path = next(
            (path for path in (_fixture_path(value) for value in case.url_to_file.values()) if path),
            None,
        )
        if html_path is None:
            continue
        rendered_table_id = endpoint.table_id.format(**case.params)
        targets.append(_OracleTarget(case_id=case.id, html_path=html_path, table_id=rendered_table_id))
        seen.add(case.endpoint_name)
    return sorted(targets, key=lambda target: target.case_id)


_ORACLE_TARGETS = _build_oracle_targets()


@pytest.mark.parametrize(
    "target",
    _ORACLE_TARGETS,
    ids=[target.case_id for target in _ORACLE_TARGETS],
)
def test_table_id_selector_agreement(target: _OracleTarget) -> None:
    html = target.html_path.read_text(encoding="utf-8", errors="replace")

    parsel_tables = Selector(text=html).xpath(f"//table[@id={_xpath_literal(target.table_id)}]")
    lexbor_root = HTMLParser(html)
    lexbor_table = lexbor_root.css_first(f"table#{target.table_id}")

    assert bool(parsel_tables) == (lexbor_table is not None), (
        f"table#{target.table_id!r} presence mismatch in {target.html_path.name}"
    )
    if not parsel_tables or lexbor_table is None:
        return

    parsel_row_count = len(parsel_tables[0].xpath(".//tr"))
    lexbor_row_count = len(lexbor_table.css("tr"))
    assert parsel_row_count == lexbor_row_count, (
        f"table#{target.table_id!r} row count mismatch "
        f"(parsel={parsel_row_count}, selectolax={lexbor_row_count}) "
        f"in {target.html_path.name}"
    )


def test_oracle_targets_cover_generic_endpoints() -> None:
    """Sanity check: every non-custom endpoint with ``table_id`` has an oracle target."""
    expected = {name for name, endpoint in ENDPOINTS.items() if not endpoint.custom and endpoint.table_id is not None}
    covered_in_manifest = {case.endpoint_name for case in ALL_CASES if case.endpoint_name in expected}
    oracle_endpoints = {
        target.case_id.rsplit("-", 1)[0] if "-" in target.case_id else target.case_id for target in _ORACLE_TARGETS
    }
    # Map case ids back to endpoint names via ALL_CASES.
    id_to_endpoint = {case.id: case.endpoint_name for case in ALL_CASES}
    oracle_endpoints = {id_to_endpoint[target.case_id] for target in _ORACLE_TARGETS}
    assert oracle_endpoints == covered_in_manifest
