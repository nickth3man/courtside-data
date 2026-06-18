"""pytest-benchmark regression suite for the courtside-data parse pipeline.

Benchmarks the five hot paths in the parse + serialize + debug surface:

1. ``courtside_data.parsing.tables.GenericTable`` row extraction
2. ``courtside_data.parsing.tables.extract_commented_table`` HTML-comment scan
3. ``courtside_data.parsing.generic.GenericEndpointHandler.fetch_table``
   transaction-list fallback path
4. ``courtside_data.output.writers.JSONWriter`` medium-payload serialization
5. ``courtside_data.debug.trace.DebugTrace`` debug-envelope serialization

How to run
----------

The suite is opt-in. The autouse ``_require_benchmark_mode`` fixture below
calls :func:`pytest.skip` unless pytest-benchmark's ``--benchmark-only`` flag
is set, so the default ``pytest tests`` run is unaffected.

Run all benchmarks::

    uv run pytest tests/test_benchmarks.py --benchmark-only -v

Run a single benchmark by node id::

    uv run pytest tests/test_benchmarks.py --benchmark-only -v -k generic_table

Capture historical results in ``.benchmarks/`` for trend comparison::

    uv run pytest tests/test_benchmarks.py --benchmark-only --benchmark-autosave

Compare against a saved run::

    uv run pytest tests/test_benchmarks.py --benchmark-only --benchmark-compare=0001

Fixture loading
---------------

Fixtures are loaded the same way the rest of the suite loads them:
``tests/fixture_manifest.ALL_CASES`` is the source of truth, and
``tests/fixture_transport.FixtureTransport`` + ``build_service`` replay the
captured HTML. Benchmarks never touch the network; the session-wide
``tests/conftest.py`` already blocks sockets for every test.

This file does not modify any production code or existing tests. Each
benchmark exercises a full table page (not a 2-row stub) so the timings
reflect the cost of the actual hot path under realistic input.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from courtside_data.client.courtside_client import CourtsideClient
from courtside_data.data import OutputType, OutputWriteOption
from courtside_data.debug import DebugTrace
from courtside_data.endpoints import ENDPOINTS
from courtside_data.output.fields import BasketballReferenceJSONEncoder
from courtside_data.output.writers import FileOptions, JSONWriter, OutputOptions
from courtside_data.parsing.generic import GenericEndpointHandler
from courtside_data.parsing.tables import GenericTable, extract_commented_table
from courtside_data.schemas.league import LeaguePerGameStatsRow
from parsel import Selector

from tests.fixture_manifest import ALL_CASES, Case
from tests.fixture_transport import FixtureTransport, build_service

# ─── Opt-in gating ─────────────────────────────────────────────────────────
#
# The default test run (no --benchmark-only) must not pay the cost of these
# benchmarks. An autouse fixture here short-circuits every test in this
# module with pytest.skip when benchmarks are not requested. The check is
# cheap (a single attribute read on the parsed CLI options).


@pytest.fixture(autouse=True)
def _require_benchmark_mode(request: pytest.FixtureRequest) -> None:
    """Skip every benchmark unless ``--benchmark-only`` (or its alias) was passed.

    pytest-benchmark registers ``--benchmark-only`` as a CLI flag; the
    resolved value is exposed on ``request.config.option.benchmark_only``.
    We treat that as the source of truth so the default ``pytest tests``
    invocation is unaffected.
    """
    if not getattr(request.config.option, "benchmark_only", False):
        pytest.skip("benchmarks are opt-in; pass --benchmark-only to enable")


# ─── Fixture selection helpers ──────────────────────────────────────────────
#
# Each benchmark picks one representative manifest case so the test
# surfaces a clear, stable identifier in the benchmark report (e.g.
# "league_per_game_stats-2024"). Re-use ALL_CASES as the canonical source.

_CASE_BY_ID: dict[str, Case] = {case.id: case for case in ALL_CASES}


def _first_path(case: Case) -> Path:
    """Return the first ``Path`` value in a manifest case's ``url_to_file`` map.

    Manifest values are either a ``Path`` (serve at 200) or a
    ``(status, headers)`` tuple for error injection. Benchmarks only need
    the happy-path ``Path``; raise if the case is error-injected.
    """
    for value in case.url_to_file.values():
        if isinstance(value, Path):
            return value
    raise ValueError(f"Manifest case {case.id!r} has no Path fixture")


# ─── 1. GenericTable row extraction ─────────────────────────────────────────
#
# Hot path: builds a GenericTable from a Selector and emits one dict per
# row. The realistic input is the per-game stats table for the 2024
# season — 735 player rows, 28+ columns per row.


@pytest.fixture(scope="module")
def league_per_game_table_selector() -> Selector:
    """The ``table#per_game_stats`` Selector from ``league_per_game_stats/2024``."""
    case = _CASE_BY_ID.get("league_per_game_stats-2024")
    if case is None:
        pytest.skip("league_per_game_stats-2024 fixture not in manifest")
    html = _first_path(case).read_text(encoding="utf-8", errors="replace")
    sel = Selector(text=html)
    tables = sel.css("table#per_game_stats")
    if not tables:
        pytest.skip("table#per_game_stats not present in fixture")
    return tables[0]


@pytest.mark.benchmark(group="parse")
def test_bench_generic_table_row_extraction(benchmark, league_per_game_table_selector) -> None:
    """Time the full GenericTable hot path: build rows + to_dict for each row."""

    def _extract() -> list[dict[str, str]]:
        table = GenericTable(league_per_game_table_selector, exclude_summary_rows=True)
        return [row.to_dict() for row in table.rows]

    rows = benchmark(_extract)
    # Sanity check: realistic row count (not a 2-row stub).
    assert len(rows) > 100, f"expected >100 rows, got {len(rows)}"


# ─── 2. extract_commented_table ────────────────────────────────────────────
#
# Hot path: scan every HTML comment in a Basketball-Reference page for a
# ``id="<table_id>"`` match. The team page wraps several per-poss / totals
# tables in comments; scanning all comments per parse is the realistic
# cost (the team_opponent_stats page is 927KB and contains 10+ comments).


@pytest.fixture(scope="module")
def team_opponent_page_selector() -> Selector:
    """A team page Selector that contains multiple commented tables."""
    # Manifest case id is ``<endpoint>-<param1>-<param2>`` with params sorted
    # alphabetically, so season_end_year comes before team_abbreviation.
    case = _CASE_BY_ID.get("team_opponent_stats-2024-BOS")
    if case is None:
        pytest.skip("team_opponent_stats-2024-BOS fixture not in manifest")
    return Selector(text=_first_path(case).read_text(encoding="utf-8", errors="replace"))


@pytest.mark.benchmark(group="parse")
def test_bench_extract_commented_table(benchmark, team_opponent_page_selector) -> None:
    """Time the comment-scan used to locate a table wrapped in ``<!-- ... -->``."""

    def _extract() -> object:
        return extract_commented_table(team_opponent_page_selector, "per_poss")

    table = benchmark(_extract)
    assert table is not None, "expected per_poss table inside HTML comment"


# ─── 3. GenericEndpointHandler.fetch_table (transaction-list fallback) ────
#
# Hot path: the ``transactions`` table on a Basketball-Reference page is
# never a real ``<table>`` — the endpoint declares
# ``transaction_list_fallback=True`` so ``fetch_table`` falls back to
# ``parse_transaction_list``, which walks the ``<ul.page_index>`` tree.
# The 2024 league transactions page has 1040 transaction entries.


@pytest.fixture(scope="module")
def league_transactions_handler() -> tuple[GenericEndpointHandler, dict[str, int]]:
    """A pre-wired fetch_table handler for ``league_transactions/2024``."""
    case = _CASE_BY_ID.get("league_transactions-2024")
    if case is None:
        pytest.skip("league_transactions-2024 fixture not in manifest")
    transport = FixtureTransport(case.url_to_file)
    service = build_service(transport)
    handler = GenericEndpointHandler(service)
    return handler, dict(case.params)


@pytest.mark.benchmark(group="parse")
def test_bench_fetch_table_transaction_list_fallback(benchmark, league_transactions_handler) -> None:
    """Time the full fetch_table pipeline when only the transaction-list fallback matches."""
    handler, params = league_transactions_handler
    endpoint = ENDPOINTS["league_transactions"]

    def _fetch() -> list[dict]:
        return handler.fetch_table(endpoint, **params)

    rows = benchmark(_fetch)
    # Sanity: 2024 league transactions fixture has 1000+ entries.
    assert len(rows) > 500, f"expected >500 transaction rows, got {len(rows)}"


# ─── 4. JSONWriter medium-payload serialization ────────────────────────────
#
# Hot path: ``JSONWriter.write`` with a list of Pydantic row models goes
# through ``_serialize_row_models`` (one ``model_dump(mode="json")`` per
# row) and then ``json.dumps`` with the project's encoder. The realistic
# payload is the 735-row per-game-stats table (validated Pydantic models).


@pytest.fixture(scope="module")
def json_writer_medium_payload() -> tuple[JSONWriter, OutputOptions, list[LeaguePerGameStatsRow]]:
    """A JSONWriter + 735 validated Pydantic row models from league_per_game_stats/2024."""
    case = _CASE_BY_ID.get("league_per_game_stats-2024")
    if case is None:
        pytest.skip("league_per_game_stats-2024 fixture not in manifest")
    transport = FixtureTransport(case.url_to_file)
    service = build_service(transport)
    client = CourtsideClient(service=service)
    # ``output_type=None`` returns the validated Pydantic models without
    # going through the writer — we drive the writer explicitly here.
    rows = client.league_per_game_stats(season_end_year=2024, output_type=None)
    writer = JSONWriter(value_formatter=BasketballReferenceJSONEncoder)
    options = OutputOptions.of(
        file_options=FileOptions.of(path=None, mode=OutputWriteOption.WRITE),
        output_type=OutputType.JSON,
    )
    return writer, options, rows


@pytest.mark.benchmark(group="parse")
def test_bench_json_writer_medium_payload(benchmark, json_writer_medium_payload) -> None:
    """Time ``JSONWriter.write`` over a 735-row Pydantic payload (~900KB of JSON)."""
    writer, options, rows = json_writer_medium_payload

    def _serialize() -> str:
        return writer.write(rows, options)

    serialized = benchmark(_serialize)
    # Sanity: full per-game stats JSON is well over 100KB.
    assert len(serialized) > 100_000, f"expected >100KB JSON, got {len(serialized)} chars"


# ─── 5. DebugTrace envelope serialization ─────────────────────────────────
#
# Hot path: ``DebugTrace.to_dict()`` walks every event/artifact/span and
# produces the ``debug`` half of the debug envelope. The envelope itself
# is ``{"data": <data>, "debug": trace.to_dict()}``, serialized via the
# output service. The benchmark builds a realistic populated trace
# (multiple events, a nested span, an artifact, a row-diagnostics block)
# and times the dict-build + ``json.dumps`` pair.


def _build_realistic_trace() -> DebugTrace:
    """Build a DebugTrace that mirrors a real ``team_roster`` call.

    Includes: execute_start event, a nested ``service_call`` span,
    raw_rows + service_values artifacts, and an ``observe_rows`` block.
    """
    trace = DebugTrace(
        endpoint="team_roster",
        params={"team_abbreviation": "BOS", "season_end_year": 2024},
    )
    trace.record("runner", "execute_start", output_type="JSON", validate_output=True)
    with trace.span("service_call", stage="runner"):
        trace.record("parse", "table_extracted", table_id="roster", row_count=20)
        trace.artifact(
            "raw_rows",
            [{"player": f"Player {i}", "pts": i * 10, "team": "BOS"} for i in range(20)],
        )
    trace.artifact(
        "service_values",
        [{"player": f"Player {i}", "pts": i * 10} for i in range(20)],
    )
    trace.observe_rows(
        "service_values",
        [{"player": f"Player {i}", "pts": i * 10} for i in range(20)],
    )
    trace.metric("row_count", 20)
    return trace


@pytest.mark.benchmark(group="parse")
def test_bench_debug_trace_envelope_serialization(benchmark) -> None:
    """Time the build + serialize of a populated debug envelope."""

    def _build_and_serialize() -> str:
        trace = _build_realistic_trace()
        envelope = {"data": [], "debug": trace.to_dict()}
        return json.dumps(envelope)

    serialized = benchmark(_build_and_serialize)
    # Sanity: envelope should be several KB.
    assert len(serialized) > 1_000, f"expected >1KB debug envelope, got {len(serialized)} chars"


# ─── Module-level guard: manifest drift detector ──────────────────────────
#
# Each benchmark calls ``_CASE_BY_ID.get(...)`` and ``pytest.skip``s if the
# fixture is missing. That converts drift into a SKIPPED benchmark, which is
# the safest failure mode (the suite still runs; a missing fixture is
# surfaced in the report). A separate smoke test would be filtered by
# pytest-benchmark's ``--benchmark-only`` (it would not have a ``benchmark``
# fixture argument), so the skip-on-missing pattern in the per-benchmark
# fixtures above is the drift detector.
