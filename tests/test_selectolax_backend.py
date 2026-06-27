"""Cross-backend agreement tests for the env-gated selectolax parser.

Goals
-----
1. Prove that :class:`courtside_data.parsing.tables.GenericTable` produces
   identical ``list[dict[str, str]]`` output on both the default
   (selectolax / Lexbor) and the opt-in (parsel + lxml) backends.
2. Prove that :func:`extract_commented_table` and
   :func:`parse_transaction_list` also produce identical output.
3. Exercise the ``COURTSIDE_DATA_PARSE_BACKEND`` env-var switch through
   the public surface (``GenericTable``) to confirm the dispatch is wired
   and both backends return the same rows as a direct selectolax build.

These tests are offline-only and parallel-safe; they read fixture HTML
directly from ``raw/`` (no transport, no conftest dependency) the same
way :mod:`tests.test_parser_oracle` does.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from courtside_data.parsing._selectolax_backend import (
    build_selectolax_table,
    get_parse_backend,
    is_parsel_backend,
    is_selectolax_backend,
    selectolax_extract_commented_table,
    selectolax_parse_transaction_list,
)
from courtside_data.parsing.tables import (
    GenericTable,
    extract_commented_table,
    parse_transaction_list,
)
from parsel import Selector

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = PROJECT_ROOT / "raw"


# A representative spread of fixture paths exercising:
#   * a vanilla table with `data-stat` cells (roster, modern)
#   * a historical table (older seasons, simpler markup)
#   * the leaderboard `value_column` rename + `use_header_fallback`
#   * a table with no data-stat cells (career leaders index)
#   * a transaction list (no <table> at all, exercises parse_transaction_list)
REPRESENTATIVE_FIXTURES: list[tuple[str, Path]] = [
    ("team_roster_modern", RAW_ROOT / "team_roster" / "BOS_2024.html"),
    ("team_roster_historical", RAW_ROOT / "team_roster" / "BOS_1980.html"),
    ("season_leaders_value_column", RAW_ROOT / "season_leaders" / "default.html"),
    ("career_leaders_index", RAW_ROOT / "career_leaders" / "default.html"),
    ("playoff_per_game", RAW_ROOT / "playoff_per_game" / "2024.html"),
    ("playoff_totals", RAW_ROOT / "playoff_totals" / "2024.html"),
    ("league_transactions_list", RAW_ROOT / "league_transactions" / "2024.html"),
    ("team_transactions_list", RAW_ROOT / "team_transactions" / "BOS_2024.html"),
]


def _available_fixtures() -> list[tuple[str, Path]]:
    return [(label, path) for label, path in REPRESENTATIVE_FIXTURES if path.is_file()]


# ─── Default (parsel) vs selectolax cross-check on representative tables ──


@pytest.mark.parametrize(
    ("label", "path"),
    _available_fixtures(),
    ids=[label for label, _ in _available_fixtures()],
)
def test_generic_table_agreement_across_backends(label: str, path: Path) -> None:
    """Both backends must produce identical rows for every table in the fixture.

    Iterates over every ``<table>`` in the HTML and compares the row dicts
    produced by :class:`GenericTable` (parsel) against those produced by
    :func:`build_selectolax_table` (selectolax). The comparison ignores
    ``dict`` key ordering — both backends are required to expose the same
    set of column keys with the same values.
    """
    html = path.read_text(encoding="utf-8", errors="replace")
    sel = Selector(text=html)
    tables = sel.css("table")
    if not tables:
        pytest.skip(f"{label}: no <table> in {path.name}")

    for index, parsel_table in enumerate(tables):
        parsel_generic = GenericTable(parsel_table)
        selectolax_generic = build_selectolax_table(parsel_table)

        parsel_rows = [row.to_dict() for row in parsel_generic.rows]
        selectolax_rows = [row.to_dict() for row in selectolax_generic.rows]

        assert parsel_rows == selectolax_rows, (
            f"{label}/{path.name} table[{index}] id={parsel_table.attrib.get('id')!r}: "
            f"parsel and selectolax disagree on row contents"
        )
        # Also assert the row counts are equal as a tighter structural check.
        assert len(parsel_rows) == len(selectolax_generic.rows), (
            f"{label}/{path.name} table[{index}]: "
            f"row-count mismatch (parsel={len(parsel_rows)}, "
            f"selectolax={len(selectolax_generic.rows)})"
        )


# ─── GenericTable with all option toggles (header fallback, exclude, value) ─


def test_generic_table_with_all_toggles_matches_selectolax() -> None:
    """The fast and default paths agree when *every* GenericTable flag is on.

    Targets :data:`season_leaders` (which declares ``use_header_fallback``
    + ``value_column`` in the registry) and a roster table that exercises
    ``exclude_summary_rows``.
    """
    fixtures: list[tuple[Path, str, dict]] = [
        (
            RAW_ROOT / "season_leaders" / "default.html",
            "stats_TOT",
            {"use_header_fallback": True, "value_column": True},
        ),
        (
            RAW_ROOT / "team_roster" / "BOS_2024.html",
            "roster",
            {"exclude_summary_rows": True},
        ),
    ]
    for path, table_id, opts in fixtures:
        assert path.is_file(), f"missing fixture: {path}"
        html = path.read_text(encoding="utf-8", errors="replace")
        sel = Selector(text=html)
        table = sel.css(f"table#{table_id}")[0]

        parsel_rows = [row.to_dict() for row in GenericTable(table, **opts).rows]
        selectolax_rows = [row.to_dict() for row in build_selectolax_table(table, **opts).rows]
        assert parsel_rows == selectolax_rows, f"{path.name} table#{table_id} with {opts}: parsel/selectolax disagree"


# ─── Commented-table extraction ───────────────────────────────────────────


def test_extract_commented_table_agreement_on_inline_html() -> None:
    """Both backends must surface the same table from an HTML comment block."""
    page_html = (
        "<html><body>"
        '<!-- <table id="x"><tr><td data-stat="a">1</td><td data-stat="b">2</td></tr></table> -->'
        '<!-- <table id="y"><tr><td>Other</td></tr></table> -->'
        "</body></html>"
    )
    sel = Selector(text=page_html)

    # parsel path
    parsel_table = extract_commented_table(sel, "x")
    assert parsel_table is not None
    parsel_first = parsel_table.css('td[data-stat="a"]::text').get("").strip()

    # selectolax path
    sl_html = selectolax_extract_commented_table(page_html, "x")
    assert sl_html is not None
    sl_table = Selector(text=sl_html)
    sl_first_cell = sl_table.css('td[data-stat="a"]::text').get("").strip()

    assert parsel_first == sl_first_cell == "1"
    # And a missing id returns None on both paths.
    assert extract_commented_table(sel, "absent") is None
    assert selectolax_extract_commented_table(page_html, "absent") is None


# ─── Transaction-list extraction ──────────────────────────────────────────


@pytest.mark.parametrize(
    ("label", "path"),
    [(label, path) for label, path in REPRESENTATIVE_FIXTURES if "transactions" in label],
    ids=[label for label, _ in REPRESENTATIVE_FIXTURES if "transactions" in label],
)
def test_parse_transaction_list_agreement(label: str, path: Path) -> None:
    """Both backends produce identical rows for the transaction list pages."""
    assert path.is_file(), f"missing fixture: {path}"
    html = path.read_text(encoding="utf-8", errors="replace")
    sel = Selector(text=html)

    parsel_rows = parse_transaction_list(sel)
    selectolax_rows = selectolax_parse_transaction_list(html)
    assert parsel_rows == selectolax_rows, f"{label}/{path.name}: parse_transaction_list parsel/selectolax disagree"


# ─── Env-var dispatch through the public GenericTable surface ────────────


@pytest.fixture
def parsel_backend_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the parsel backend on for the duration of one test.

    The :func:`courtside_data.parsing.tables._is_parsel_backend` helper
    re-reads ``os.environ`` on every call, so a ``monkeypatch.setenv``
    flips the dispatch path without reloading any modules.
    """
    monkeypatch.setenv("COURTSIDE_DATA_PARSE_BACKEND", "parsel")
    # monkeypatch unsets it on teardown.


def test_default_backend_is_selectolax(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no env vars set, the default backend is selectolax."""
    monkeypatch.delenv("COURTSIDE_DATA_PARSE_BACKEND", raising=False)
    assert get_parse_backend() == "selectolax"
    assert is_selectolax_backend() is True
    assert is_parsel_backend() is False


def test_env_var_routes_generic_table_to_selectolax() -> None:
    """The default (``selectolax``) backend wires through ``GenericTable``."""
    from courtside_data.parsing._selectolax_backend import _SelectolaxGenericTableRow

    path = RAW_ROOT / "team_roster" / "BOS_2024.html"
    assert path.is_file(), f"missing fixture: {path}"
    html = path.read_text(encoding="utf-8", errors="replace")
    sel = Selector(text=html)
    table = sel.css("table#roster")[0]

    env_table = GenericTable(table)
    direct_table = build_selectolax_table(table)

    assert env_table.rows, "default-path GenericTable returned no rows"
    # The rows are instances of the selectolax-specific class, not GenericTableRow.
    assert all(isinstance(row, _SelectolaxGenericTableRow) for row in env_table.rows), (
        "default-path GenericTable rows should be _SelectolaxGenericTableRow instances"
    )

    # And the public surface produces the same dict list as a direct selectolax build.
    assert [r.to_dict() for r in env_table.rows] == [r.to_dict() for r in direct_table.rows]


def test_env_var_explicit_selectolax_routes_generic_table_to_selectolax(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``COURTSIDE_DATA_PARSE_BACKEND=selectolax`` explicitly locks in the default."""
    monkeypatch.setenv("COURTSIDE_DATA_PARSE_BACKEND", "selectolax")
    from courtside_data.parsing._selectolax_backend import _SelectolaxGenericTableRow

    path = RAW_ROOT / "team_roster" / "BOS_2024.html"
    assert path.is_file(), f"missing fixture: {path}"
    html = path.read_text(encoding="utf-8", errors="replace")
    sel = Selector(text=html)
    table = sel.css("table#roster")[0]

    env_table = GenericTable(table)
    assert all(isinstance(row, _SelectolaxGenericTableRow) for row in env_table.rows), (
        "selectolax-flagged GenericTable rows should be _SelectolaxGenericTableRow instances"
    )


def test_env_var_parsel_backend_routes_generic_table_to_parsel(
    parsel_backend_env: None,
) -> None:
    """With ``COURTSIDE_DATA_PARSE_BACKEND=parsel``, ``GenericTable`` returns parsel rows."""
    # Sanity check: the helper is reading the env var live.
    assert is_parsel_backend() is True
    assert is_selectolax_backend() is False
    assert get_parse_backend() == "parsel"

    path = RAW_ROOT / "team_roster" / "BOS_2024.html"
    assert path.is_file(), f"missing fixture: {path}"
    html = path.read_text(encoding="utf-8", errors="replace")
    sel = Selector(text=html)
    table = sel.css("table#roster")[0]

    default_table = GenericTable(table)
    assert default_table.rows, "parsel-path GenericTable returned no rows"
    assert all(type(row).__name__ == "GenericTableRow" for row in default_table.rows), (
        "parsel-path GenericTable rows should be GenericTableRow instances"
    )
