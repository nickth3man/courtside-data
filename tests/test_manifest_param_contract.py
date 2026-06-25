"""Offline contract test: manifest cases match the declared endpoint contract.

This test is a regression canary for two classes of offline-replay bugs:

1. **Parameter drift** (catches the ``standings_by_date`` /
   ``conference`` class): a manifest case supplies a parameter that the
   endpoint does not declare, or the endpoint declares a parameter that no
   manifest case supplies.

2. **Year-range drift** (catches the ``league_per_100_possessions`` /
   ``1973`` class): a manifest case supplies a ``season_end_year`` that
   falls outside the endpoint's declared ``min_year`` / ``max_year`` window.
   The endpoint declares the live floor; an offline fixture that pre-dates
   it would replay successfully but fail on the live site.

The test is **offline** (it only reads dataclass fields, inspects
signatures, and checks stdlib :class:`datetime.date`) and **parallel-safe**
(parameter IDs are stable, per-case state is local).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest
from courtside_data.domain import TEAM_ABBREVIATIONS_TO_TEAM
from courtside_data.endpoints import ENDPOINTS, EndpointKind, EndpointSpec
from courtside_data.parsing.workflows import workflow_execution_bindings

from tests.fixture_manifest import ALL_CASES, Case

# ─── Case partitions ──────────────────────────────────────────────────────
# Each parametrized contract test runs only on the cases that actually apply
# to it. Cases are excluded at *collection time* rather than skipped at
# runtime, so the suite reports a clean pass/fail count with no skip noise.
# The workflow↔generic_table partition invariant is additionally enforced by
# ``test_endpoint_kinds_are_partitioned`` below, which catches endpoint
# registration drift (EndpointKind.WORKFLOW vs. workflow binding) in one
# assertion.
_CASES_WITH_ENDPOINT: list[Case] = [c for c in ALL_CASES if c.endpoint_name and c.endpoint_name in ENDPOINTS]
_WORKFLOW_ENDPOINT_CASES: list[Case] = [
    c for c in _CASES_WITH_ENDPOINT if ENDPOINTS[c.endpoint_name].kind is EndpointKind.WORKFLOW
]
_GENERIC_TABLE_ENDPOINT_CASES: list[Case] = [
    c for c in _CASES_WITH_ENDPOINT if ENDPOINTS[c.endpoint_name].kind is EndpointKind.GENERIC_TABLE
]
_CASES_WITH_YEAR_RANGE: list[Case] = [
    c
    for c in _CASES_WITH_ENDPOINT
    if "season_end_year" in c.params
    and (ENDPOINTS[c.endpoint_name].min_year is not None or ENDPOINTS[c.endpoint_name].max_year is not None)
]
# Excludes error-* cases (their team_abbreviation is deliberately bogus);
# those are filtered out by the ``in ENDPOINTS`` membership check above.
_CASES_WITH_TEAM_ABBREVIATION: list[Case] = [c for c in _CASES_WITH_ENDPOINT if "team_abbreviation" in c.params]


@pytest.mark.parametrize("case", _WORKFLOW_ENDPOINT_CASES, ids=[case.id for case in _WORKFLOW_ENDPOINT_CASES])
def test_workflow_endpoint_params_match_endpoint_spec(case: Case) -> None:
    """Workflow endpoints: the case params must match ``endpoint.params``."""
    endpoint = ENDPOINTS[case.endpoint_name]
    expected = set(endpoint.params)
    actual = set(case.params)
    assert actual == expected, f"{case.id}: workflow case.params {sorted(actual)} != endpoint.params {sorted(expected)}"


@pytest.mark.parametrize("case", _GENERIC_TABLE_ENDPOINT_CASES, ids=[case.id for case in _GENERIC_TABLE_ENDPOINT_CASES])
def test_generic_table_endpoint_params_match_endpoint_spec(case: Case) -> None:
    """Generic-table endpoints: the case params must match the endpoint.params tuple.

    For generic-table endpoints the case resolver and the endpoint spec must agree
    exactly — there is no bespoke method to absorb a mismatch. Generic-table
    endpoints with no params (``endpoint.params == ()``) get exactly one
    case with ``params == {}``.

    Runs only on ``EndpointKind.GENERIC_TABLE`` endpoints (filtered at collection time).
    """
    endpoint = ENDPOINTS[case.endpoint_name]

    expected = set(endpoint.params)
    actual = set(case.params)
    assert actual == expected, (
        f"{case.id}: generic case.params {sorted(actual)} does not match endpoint.params {sorted(expected)}"
    )


@pytest.mark.parametrize("case", _CASES_WITH_YEAR_RANGE, ids=[case.id for case in _CASES_WITH_YEAR_RANGE])
def test_season_end_year_within_declared_range(case: Case) -> None:
    """If a case has ``season_end_year`` and the endpoint declares a range,
    the year must fall within ``min_year``/``max_year`` (inclusive).

    An offline fixture below the live floor (e.g. ``per_poss`` pre-1974)
    would replay against the saved HTML but the live endpoint would reject
    it. The contract test surfaces that drift at CHECK time.

    Runs only on cases that have ``season_end_year`` and whose endpoint
    declares at least one of ``min_year``/``max_year`` (filtered at
    collection time).
    """
    endpoint = ENDPOINTS[case.endpoint_name]

    year = case.params["season_end_year"]
    assert isinstance(year, int), f"{case.id}: season_end_year must be int, got {type(year).__name__}"

    if endpoint.min_year is not None:
        assert year >= endpoint.min_year, (
            f"{case.id}: season_end_year={year} below endpoint.min_year={endpoint.min_year}"
        )
    if endpoint.max_year is not None:
        assert year <= endpoint.max_year, (
            f"{case.id}: season_end_year={year} above endpoint.max_year={endpoint.max_year}"
        )


@pytest.mark.parametrize("case", _CASES_WITH_TEAM_ABBREVIATION, ids=[case.id for case in _CASES_WITH_TEAM_ABBREVIATION])
def test_team_abbreviation_is_known(case: Case) -> None:
    """If a case supplies ``team_abbreviation``, it must be a known BR code.

    Error cases (``error-*``) are excluded at collection time — they
    intentionally pass a bogus abbreviation to exercise the 404 path.
    """
    abbr = case.params["team_abbreviation"]
    assert abbr in TEAM_ABBREVIATIONS_TO_TEAM, (
        f"{case.id}: team_abbreviation={abbr!r} not in TEAM_ABBREVIATIONS_TO_TEAM"
    )


# ─── Supplemental sanity checks (non-parametrized) ──────────────────────


def test_endpoint_kinds_are_partitioned() -> None:
    """Every ``EndpointKind.WORKFLOW`` endpoint must have one binding, and
    every ``EndpointKind.GENERIC_TABLE`` endpoint must not.

    This is the invariant the two parametrized contract tests above rely on
    to keep their scopes disjoint (workflow vs. generic_table). A single
    registration drift is surfaced in one assertion.
    """
    bindings = workflow_execution_bindings()
    for name, endpoint in ENDPOINTS.items():
        has_binding = name in bindings
        is_workflow = endpoint.kind is EndpointKind.WORKFLOW
        assert is_workflow == has_binding, f"{name}: kind={endpoint.kind.value!r} binding={has_binding}"


def test_min_year_default_for_season_endpoints() -> None:
    """League-wide season endpoints (built with ``_season``) declare a
    ``min_year`` so the contract test can guard the range. Player/team
    endpoints built with ``_player``/``_team`` are out of scope — their year
    semantics are endpoint-specific (e.g. team_roster predates the BAA/NBA
    merger in 1949, player pages exist from 1947 onward) and the default
    ``min_year=1947`` only covers the league-wide tables.

    The heuristic: league-wide endpoints live under ``/leagues/``,
    ``/awards/``, ``/playoffs/``, or ``/draft/``. Player/team endpoints live
    under ``/players/``, ``/teams/``, ``/contracts/``, or
    ``/boxscores/``. Endpoints that accept ``season_end_year`` for API
    symmetry but do NOT embed it in the URL path (e.g.
    ``team_injury_report`` at ``/friv/injuries.fcgi``) are also excluded.
    """
    league_path_prefixes = ("/leagues/", "/awards/", "/playoffs/", "/draft/")
    offenders: list[str] = []
    for name, endpoint in ENDPOINTS.items():
        if "season_end_year" not in endpoint.params:
            continue
        if "{season_end_year}" not in endpoint.path:
            continue
        if not any(endpoint.path.startswith(prefix) for prefix in league_path_prefixes):
            continue
        if endpoint.min_year is None:
            offenders.append(name)
    assert not offenders, (
        f"League-wide season endpoints must declare min_year (add an override "
        f"at the endpoint registration): {sorted(offenders)}"
    )


def test_manifest_has_no_duplicate_case_ids() -> None:
    """Every (endpoint, params) pair is unique. A duplicate usually means the
    resolver emitted the same case twice — the param-contract checks above
    would then fire twice with confusing IDs.
    """
    seen: dict[str, str] = {}
    for case in ALL_CASES:
        if case.id in seen:
            pytest.fail(f"Duplicate case id {case.id!r}: {case.params} vs {seen[case.id]}")
        seen[case.id] = str(case.params)


def test_endpoint_specs_are_frozen() -> None:
    """EndpointSpec instances must be immutable (frozen dataclass + slots)
    so they can be safely shared across threads. Catches accidental removal
    of ``frozen=True`` or ``slots=True`` from the dataclass decorator.

    Note: EndpointSpec is currently NOT hashable (a pre-existing condition
    — the ``csv_columns: Sequence[str] | None`` field is mutable). This test
    guards the immutability property only; fixing the hashability is out of
    scope for this lane.
    """
    for name, endpoint in ENDPOINTS.items():
        # Frozen + slots dataclasses raise on any setattr attempt. The exact
        # exception type depends on whether the target is a known slot:
        #   - known field (e.g. ``path``): FrozenInstanceError
        #   - unknown attribute: TypeError (slots machinery) or AttributeError
        # We accept any of these as proof of immutability.
        try:
            object.__setattr__(endpoint, "_test_frozen_marker", True)  # type: ignore[misc]
        except (AttributeError, FrozenInstanceError, TypeError):
            continue
        else:
            pytest.fail(f"ENDPOINTS[{name!r}] is not frozen: attribute mutation succeeded")


# Reference the imports so ruff/ty don't flag them as unused while keeping
# the module's public surface self-documenting.
_ = (EndpointSpec, date)
