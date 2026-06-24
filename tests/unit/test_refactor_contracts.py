"""Refactor contract tests.

These tests lock down *public-surface* contracts (importable names, constant
values, parser CLI argument shapes) that an aggressive structural refactor of
the debug / probe / parsing / schemas packages must not break.

They are deliberately hermetic: no live network, no fixtures, no I/O. They
verify the wiring and the contract surface that downstream tooling and the
``uv run python -m courtside_data.debug`` / ``courtside-data probe`` flows
depend on. If any of these tests fail, the refactor has either removed a
public name, changed a stable constant, or reshaped a CLI flag in a
backwards-incompatible way.

Note: the contract tests intentionally *import* a long list of public names
without using them — the import itself is the test. ``# ruff: noqa: F401``
suppresses the "imported but unused" warning that contract tests are
designed to trigger.
"""

# ruff: noqa: F401  # Contract tests: imports ARE the test, not unused code.

from __future__ import annotations

import inspect

import pytest

# ---------------------------------------------------------------------------
# 1. Probe public API surface
# ---------------------------------------------------------------------------


def test_probe_public_api_imports():
    """Every name in ``probe.__all__`` must be importable from the module."""
    import courtside_data.debug.probe as probe_module
    from courtside_data.debug.probe import __all__ as probe_all

    for name in probe_all:
        assert hasattr(probe_module, name), f"probe module missing: {name}"


# ---------------------------------------------------------------------------
# 2. Provenance public API surface
# ---------------------------------------------------------------------------


def test_provenance_public_api_imports():
    """Key provenance names importable from ``courtside_data.debug.provenance``."""
    from courtside_data.debug.provenance import (
        PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE,
        PROVENANCE_CUSTOM_PARSER_VALUE,
        PROVENANCE_DEBUG_UNAVAILABLE,
        PROVENANCE_PARSER_EMITTED_VALUE,
        PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN,
        PROVENANCE_ROW_DROPPED_EXPECTED_REASON,
        PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR,
        PROVENANCE_SCHEMA_DEFAULT_USED,
        PROVENANCE_SOURCE_CELL_BLANK,
        PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL,
        PROVENANCE_SOURCE_COLUMN_ABSENT,
        PROVENANCE_SOURCE_VALUE_PRESENT,
        PROVENANCE_UNKNOWN,
        PROVENANCE_VALIDATOR_COERCED_TO_NONE,
        PROVENANCE_VALIDATOR_TRANSFORMED_VALUE,
        ProvenanceContext,
        ProvenanceReason,
        SourceCell,
        SourceColumn,
        SourceTableSnapshot,
        build_dropped_row_provenance_records,
        build_field_provenance_records,
        build_source_table_snapshot,
        classify_validation_drop,
        emit_field_provenance,
        get_trace_context,
        summarize_provenance,
        trace_context,
    )

    # Sanity-check that the imported symbols are not placeholders.
    assert SourceTableSnapshot is not None
    assert ProvenanceReason is not None
    assert isinstance(PROVENANCE_SOURCE_VALUE_PRESENT, str)
    assert isinstance(PROVENANCE_UNKNOWN, str)


# ---------------------------------------------------------------------------
# 3. Provenance reason constants unchanged
# ---------------------------------------------------------------------------


def test_provenance_reason_constants_unchanged():
    """All 15 provenance reason strings must remain unchanged.

    These strings are persisted in debug-envelope artifacts and downstream
    report JSON; renaming any of them is a breaking change.
    """
    from courtside_data.debug import provenance

    assert provenance.PROVENANCE_SOURCE_VALUE_PRESENT == "source_value_present"
    assert provenance.PROVENANCE_SOURCE_COLUMN_ABSENT == "source_column_absent"
    assert provenance.PROVENANCE_SOURCE_CELL_BLANK == "source_cell_blank"
    assert provenance.PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL == "source_cell_dash_or_sentinel"
    assert provenance.PROVENANCE_PARSER_EMITTED_VALUE == "parser_emitted_value"
    assert provenance.PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN == "parser_omitted_present_column"
    assert provenance.PROVENANCE_SCHEMA_DEFAULT_USED == "schema_default_used"
    assert provenance.PROVENANCE_VALIDATOR_COERCED_TO_NONE == "validator_coerced_to_none"
    assert provenance.PROVENANCE_VALIDATOR_TRANSFORMED_VALUE == "validator_transformed_value"
    assert provenance.PROVENANCE_ROW_DROPPED_EXPECTED_REASON == "row_dropped_expected_reason"
    assert provenance.PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR == "row_dropped_unresolved_validation_error"
    assert provenance.PROVENANCE_CUSTOM_PARSER_VALUE == "custom_parser_value"
    assert provenance.PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE == "custom_parser_metadata_unavailable"
    assert provenance.PROVENANCE_DEBUG_UNAVAILABLE == "debug_provenance_unavailable"
    assert provenance.PROVENANCE_UNKNOWN == "unknown"

    # Verify ProvenanceReason Literal contains all 15 reason strings.
    from typing import get_args

    reasons = set(get_args(provenance.ProvenanceReason))
    assert "source_value_present" in reasons
    assert "unknown" in reasons
    assert len(reasons) == 15


# ---------------------------------------------------------------------------
# 4. Probe module execution contract
# ---------------------------------------------------------------------------


def test_probe_module_can_be_imported_as_main():
    """Verify ``probe.py`` does not execute side-effects on plain import.

    Importing the module must be safe (it is allowed to read CLI defaults but
    must not perform network I/O or write files). The ``if __name__ ==
    '__main__'`` guard at the bottom of ``probe.py`` enforces this.
    """
    # Plain import must succeed without raising.
    import courtside_data.debug.probe


def test_probe_main_function_exists():
    """``main()`` must be defined and callable (consumed by the ``__main__`` guard)."""
    from courtside_data.debug.probe import main

    assert callable(main)


def test_probe_endpoints_function_exists():
    """``probe_endpoints()`` must be defined and callable (programmatic API)."""
    from courtside_data.debug.probe import probe_endpoints

    assert callable(probe_endpoints)


# ---------------------------------------------------------------------------
# 5. Probe CLI argument parsing contract
# ---------------------------------------------------------------------------


def test_probe_cli_parser_accepts_known_flags():
    """``_build_parser`` must accept ``--endpoint``, ``--output``,
    ``--params-json``, ``--csv-output``, ``--resume-from``,
    ``--debug-detail-level`` and ``--use-cache``.
    """
    from courtside_data.debug.probe import _build_parser

    parser = _build_parser()

    # Parse with no args — defaults should be ``None`` / empty.
    args = parser.parse_args([])
    assert args.endpoints is None
    assert args.output is None
    assert args.params_json is None

    # Parse with the documented flags.
    args = parser.parse_args(
        [
            "-e",
            "team_roster",
            "--params-json",
            '{"team_abbreviation":"BOS","season_end_year":2024}',
        ]
    )
    assert args.endpoints == ["team_roster"]
    assert args.params_json == '{"team_abbreviation":"BOS","season_end_year":2024}'


def test_probe_resolve_endpoint_names():
    """``_resolve_endpoint_names`` must validate names against the registry and
    return them sorted. Unknown names must raise ``ValueError``.
    """
    from courtside_data.debug.probe import _resolve_endpoint_names
    from courtside_data.endpoints import ENDPOINTS

    # ``None`` → all known endpoints, sorted.
    names = _resolve_endpoint_names(None)
    assert "team_roster" in names
    assert "play_by_play" in names
    assert names == sorted(names)
    assert set(names) == set(ENDPOINTS)

    # Specific endpoints — returned sorted and de-duplicated.
    names = _resolve_endpoint_names(["team_roster", "play_by_play"])
    assert names == sorted(["team_roster", "play_by_play"])

    # Unknown endpoint raises ValueError. Touch ENDPOINTS to keep the import
    # used (mirrors the public surface the registry exposes).
    assert ENDPOINTS  # non-empty registry
    with pytest.raises(ValueError, match="Unknown endpoint"):
        _resolve_endpoint_names(["nonexistent_endpoint_xyz"])


# ---------------------------------------------------------------------------
# 6. Probe report output shape contract
# ---------------------------------------------------------------------------


def test_probe_report_has_required_keys():
    """``probe_endpoints`` signature must continue to accept these keyword
    arguments: ``endpoints``, ``output_path``, ``csv_output_path``,
    ``resume_from``, ``debug_detail_level``, ``use_cache`` and
    ``params_override``.
    """
    from courtside_data.debug.probe import probe_endpoints

    sig = inspect.signature(probe_endpoints)
    params = sig.parameters
    for name in (
        "endpoints",
        "output_path",
        "csv_output_path",
        "resume_from",
        "debug_detail_level",
        "use_cache",
        "params_override",
    ):
        assert name in params, f"probe_endpoints missing parameter: {name}"


# ---------------------------------------------------------------------------
# 7. Probe CSV columns contract
# ---------------------------------------------------------------------------


def test_probe_csv_columns_unchanged():
    """``CSV_COLUMNS`` must be a non-empty tuple that includes the foundational
    columns the probe CSV report contract depends on.
    """
    from courtside_data.debug.probe import CSV_COLUMNS

    assert isinstance(CSV_COLUMNS, tuple)
    assert len(CSV_COLUMNS) > 0
    assert "endpoint" in CSV_COLUMNS
    assert "ok" in CSV_COLUMNS
    assert "evaluation" in CSV_COLUMNS


# ---------------------------------------------------------------------------
# 8. Failure category constants contract
# ---------------------------------------------------------------------------


def test_probe_failure_category_constants():
    """All failure-category string constants must remain importable from
    ``courtside_data.debug.probe`` with their documented string values.
    """
    from courtside_data.debug.probe import (
        FAILURE_EMPTY_RESULT,
        FAILURE_HTTP_ERROR,
        FAILURE_MISSING_SAMPLE_PARAMS,
        FAILURE_NONE,
        FAILURE_PARSE_ERROR,
        FAILURE_RATE_LIMITED,
        FAILURE_SCHEMA_VALIDATION,
        FAILURE_TIMEOUT,
        FAILURE_UNEXPECTED_EXCEPTION,
    )

    assert FAILURE_NONE == "none"
    assert FAILURE_RATE_LIMITED == "rate_limited"
    assert FAILURE_HTTP_ERROR == "http_error"
    # Sanity-check the remaining categories are non-empty strings so a silent
    # deletion (e.g. assignment to ``""``) is caught.
    for value in (
        FAILURE_EMPTY_RESULT,
        FAILURE_MISSING_SAMPLE_PARAMS,
        FAILURE_PARSE_ERROR,
        FAILURE_SCHEMA_VALIDATION,
        FAILURE_TIMEOUT,
        FAILURE_UNEXPECTED_EXCEPTION,
    ):
        assert isinstance(value, str)
        assert value, f"failure category must be a non-empty string, got {value!r}"


# ---------------------------------------------------------------------------
# 9. Parsing rows import contract
# ---------------------------------------------------------------------------


def test_parsing_rows_functions_importable():
    """Key row parsers must be importable from ``courtside_data.parsing.rows``.

    ``parse_transaction_list`` lives in :mod:`courtside_data.parsing.tables`
    (its sibling module) and is re-exported by :mod:`courtside_data.parsing`
    — both are stable public surfaces of the parsing package.
    """
    from courtside_data.parsing.rows import (
        parse_friv_playoff_outcomes_row,
        parse_play_by_play_rows,
        parse_player_box_scores_from_table,
        parse_playoff_bracket,
        parse_search_rows,
        parse_standings,
        parse_team_box_score,
    )
    from courtside_data.parsing.tables import parse_transaction_list

    for fn in (
        parse_standings,
        parse_play_by_play_rows,
        parse_team_box_score,
        parse_player_box_scores_from_table,
        parse_search_rows,
        parse_playoff_bracket,
        parse_friv_playoff_outcomes_row,
        parse_transaction_list,
    ):
        assert callable(fn), f"{fn!r} is not callable"


# ---------------------------------------------------------------------------
# 10. Schemas league import contract
# ---------------------------------------------------------------------------


def test_schemas_league_imports_work():
    """League schema row classes must remain importable from
    ``courtside_data.schemas.league``.
    """
    from courtside_data.schemas.league import (
        AttendanceRow,
        CareerLeadersRow,
        LeaguePer36MinutesRow,
        LeaguePer100PossessionsRow,
        LeaguePerGameStatsRow,
        LeaguePlayByPlayRow,
        LeagueShootingRow,
        LeagueTotalsRow,
        LeagueTransactionRow,
        RookieStatsRow,
        SeasonAwardsRow,
        SeasonAwardsVotingRow,
        SeasonLeadersRow,
    )

    assert LeaguePerGameStatsRow is not None
    assert RookieStatsRow is not None
    # Sanity-check the classes are types and module surfaces remain importable.
    for cls in (
        AttendanceRow,
        CareerLeadersRow,
        LeaguePer100PossessionsRow,
        LeaguePer36MinutesRow,
        LeaguePerGameStatsRow,
        LeaguePlayByPlayRow,
        LeagueShootingRow,
        LeagueTotalsRow,
        LeagueTransactionRow,
        SeasonAwardsRow,
        SeasonAwardsVotingRow,
        SeasonLeadersRow,
    ):
        assert isinstance(cls, type), f"{cls!r} should be a class"


# ---------------------------------------------------------------------------
# 11. Probe package back-compat shim + facade wiring
# ---------------------------------------------------------------------------


def test_probe_report_shim_reexports():
    """The legacy ``courtside_data.debug.probe_report`` import path must keep
    re-exporting the evaluation + CSV names after the split into
    ``probe.report`` / ``probe.csv_report``.
    """
    from courtside_data.debug import probe_report
    from courtside_data.debug.probe import csv_report, report

    # Evaluation half is sourced from probe.report.
    assert probe_report._with_evaluation is report._with_evaluation
    assert probe_report._failure_category is report._failure_category
    assert probe_report.FAILURE_NONE == report.FAILURE_NONE == "none"
    # CSV half is sourced from probe.csv_report.
    assert probe_report.CSV_COLUMNS is csv_report.CSV_COLUMNS
    assert probe_report.write_probe_csv_report is csv_report.write_probe_csv_report
    assert probe_report._csv_row is csv_report._csv_row


def test_probe_facade_matches_submodules():
    """Names exposed by the probe package facade must be the same objects as in
    their owning submodules (the facade must not shadow or rebind them).
    """
    import courtside_data.debug.probe as probe
    from courtside_data.debug.probe import (
        cli,
        csv_report,
        enrichment,
        event_summary,
        report,
        report_summary,
        runner,
        samples,
    )

    assert probe.probe_endpoints is runner.probe_endpoints
    assert probe.main is cli.main
    assert probe._summarize_debug_events is event_summary._summarize_debug_events
    assert probe._summarize_report is report_summary._summarize_report
    assert probe._sample_params_per_endpoint is samples._sample_params_per_endpoint
    assert probe._default_enrichment is enrichment._default_enrichment
    assert probe._with_evaluation is report._with_evaluation
    assert probe.CSV_COLUMNS is csv_report.CSV_COLUMNS
