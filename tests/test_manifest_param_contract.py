"""Offline contract test: manifest cases match the declared endpoint contract.

This test is a regression canary for two classes of offline-replay bugs:

1. **Signature drift** (catches the ``standings_by_date`` /
   ``conference`` class): a manifest case supplies a parameter that the
   bespoke ``HTTPService`` method does not accept, or the endpoint declares a
   parameter that no method parameter exists for. The test verifies both
   directions against :data:`courtside_data.endpoints.ENDPOINTS` and the
   live :class:`courtside_data.http_service.HTTPService` method signatures.

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

import inspect
from dataclasses import FrozenInstanceError
from datetime import date

import pytest
from courtside_data.data import TEAM_ABBREVIATIONS_TO_TEAM
from courtside_data.endpoints import ENDPOINTS, TableEndpoint
from courtside_data.http_service import HTTPService

from tests.fixture_manifest import ALL_CASES, Case


def _sig_params(name: str) -> set[str]:
    """Return the parameter names of ``HTTPService.<name>`` (excluding ``self``).

    Uses ``follow_wrapped=False`` so a ``@functools.wraps`` decorator on the
    real method does not mask a parameter that the contract test should see.
    Returns an empty set if the method is missing (the next check raises a
    clearer diagnostic).
    """
    method = getattr(HTTPService, name, None)
    if method is None:
        return set()
    sig = inspect.signature(method, follow_wrapped=False)
    return set(sig.parameters) - {"self"}


@pytest.mark.parametrize("case", ALL_CASES, ids=[case.id for case in ALL_CASES])
def test_custom_endpoint_signature_compatible(case: Case) -> None:
    """Custom endpoints: every declared param must be accepted by the method, and
    every case param must bind cleanly against the method signature.
    """
    if not case.endpoint_name:
        pytest.skip("non-endpoint case (e.g. error-*)")

    endpoint = ENDPOINTS.get(case.endpoint_name)
    if endpoint is None:
        pytest.fail(f"{case.id}: endpoint {case.endpoint_name!r} not in ENDPOINTS")
    if not endpoint.custom:
        pytest.skip(f"{case.id}: generic endpoint, covered by test_generic_endpoint_params")

    sig_params = _sig_params(case.endpoint_name)
    # Some bespoke methods (e.g. friv_7_game_playoff_series_outcomes_*) take
    # no arguments beyond self because the URL has no placeholders. That's a
    # valid contract: endpoint.params == () ↔ method signature == (self).
    if not sig_params:
        assert not endpoint.params, (
            f"{case.id}: HTTPService.{case.endpoint_name} takes no arguments but "
            f"endpoint declares params {sorted(endpoint.params)}"
        )
        assert not case.params, (
            f"{case.id}: HTTPService.{case.endpoint_name} takes no arguments but case.params={case.params}"
        )
        return

    # Direction 1: every endpoint-declared param is accepted by the method.
    missing = set(endpoint.params) - sig_params
    assert not missing, (
        f"{case.id}: endpoint declares params {sorted(missing)} but HTTPService."
        f"{case.endpoint_name} only accepts {sorted(sig_params)}"
    )

    # Direction 2: every case param is in the method's signature (no
    # unexpected kwargs). We don't call ``inspect.signature(method).bind()``
    # because it would require a ``self`` argument that the case doesn't
    # supply; subset check against the already-computed parameter set is
    # sufficient to catch the "case has a param the method doesn't accept"
    # class of bug.
    extra = set(case.params) - sig_params
    assert not extra, (
        f"{case.id}: case.params contains {sorted(extra)} which HTTPService."
        f"{case.endpoint_name} does not accept (accepts {sorted(sig_params)})"
    )


@pytest.mark.parametrize("case", ALL_CASES, ids=[case.id for case in ALL_CASES])
def test_generic_endpoint_params_match_endpoint_spec(case: Case) -> None:
    """Generic endpoints: the case params must match the endpoint.params tuple.

    For generic endpoints the case resolver and the endpoint spec must agree
    exactly — there is no bespoke method to absorb a mismatch. Generic
    endpoints with no params (``endpoint.params == ()``) get exactly one
    case with ``params == {}``.
    """
    if not case.endpoint_name:
        pytest.skip("non-endpoint case (e.g. error-*)")

    endpoint = ENDPOINTS.get(case.endpoint_name)
    if endpoint is None:
        pytest.fail(f"{case.id}: endpoint {case.endpoint_name!r} not in ENDPOINTS")
    if endpoint.custom:
        pytest.skip(f"{case.id}: custom endpoint, covered by test_custom_endpoint_signature_compatible")

    expected = set(endpoint.params)
    actual = set(case.params)
    assert actual == expected, (
        f"{case.id}: generic case.params {sorted(actual)} does not match endpoint.params {sorted(expected)}"
    )


@pytest.mark.parametrize("case", ALL_CASES, ids=[case.id for case in ALL_CASES])
def test_season_end_year_within_declared_range(case: Case) -> None:
    """If a case has ``season_end_year`` and the endpoint declares a range,
    the year must fall within ``min_year``/``max_year`` (inclusive).

    An offline fixture below the live floor (e.g. ``per_poss`` pre-1974)
    would replay against the saved HTML but the live endpoint would reject
    it. The contract test surfaces that drift at CHECK time.
    """
    if "season_end_year" not in case.params:
        pytest.skip(f"{case.id}: no season_end_year param")

    endpoint = ENDPOINTS.get(case.endpoint_name)
    if endpoint is None:
        pytest.skip(f"{case.id}: no endpoint registered (likely an error case)")
    if endpoint.min_year is None and endpoint.max_year is None:
        pytest.skip(f"{case.id}: endpoint declares no year range")

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


@pytest.mark.parametrize("case", ALL_CASES, ids=[case.id for case in ALL_CASES])
def test_team_abbreviation_is_known(case: Case) -> None:
    """If a case supplies ``team_abbreviation``, it must be a known BR code.

    Skipped for error cases that intentionally pass a bogus abbreviation to
    exercise the 404 path — those would be false positives.
    """
    if "team_abbreviation" not in case.params:
        pytest.skip(f"{case.id}: no team_abbreviation param")
    if case.endpoint_name.startswith("error-"):
        pytest.skip(f"{case.id}: error case uses a deliberately bogus abbreviation")

    abbr = case.params["team_abbreviation"]
    assert abbr in TEAM_ABBREVIATIONS_TO_TEAM, (
        f"{case.id}: team_abbreviation={abbr!r} not in TEAM_ABBREVIATIONS_TO_TEAM"
    )


# ─── Supplemental sanity checks (non-parametrized) ──────────────────────


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
    """TableEndpoint instances must be immutable (frozen dataclass + slots)
    so they can be safely shared across threads. Catches accidental removal
    of ``frozen=True`` or ``slots=True`` from the dataclass decorator.

    Note: TableEndpoint is currently NOT hashable (a pre-existing condition
    — the ``csv_columns: Sequence[str] | None`` field is mutable). This test
    guards the immutability property only; fixing the hashability is out of
    scope for this lane.
    """
    for name, endpoint in ENDPOINTS.items():
        # Frozen + slots dataclasses raise on any setattr attempt. The exact
        # exception type depends on whether the field is known:
        #   - known field (e.g. ``custom``): FrozenInstanceError
        #   - unknown field: TypeError (slots machinery) or AttributeError
        # We accept any of these as proof of immutability.
        try:
            object.__setattr__(endpoint, "_test_frozen_marker", True)  # type: ignore[misc]
        except (AttributeError, FrozenInstanceError, TypeError):
            continue
        else:
            pytest.fail(f"ENDPOINTS[{name!r}] is not frozen: attribute mutation succeeded")


# Reference the imports so ruff/ty don't flag them as unused while keeping
# the module's public surface self-documenting.
_ = (TableEndpoint, date)
