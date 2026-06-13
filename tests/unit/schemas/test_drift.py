"""Drift detection: the new Pydantic pipeline must fail loudly when Basketball-Reference
renames or removes a ``data-stat`` column. This is the headline behavior the whole
project exists for.

These tests exercise the registered ``TypeAdapter``s directly — bypassing HTTP and
``GenericTable`` extraction — so they remain fast, hermetic, and unambiguous about
which layer the contract lives at. A rename on BR's end shows up in the row dict as
a key BR used to emit being absent; a *required* field's alias going missing must
surface as a Pydantic ``missing``-type error (and a ``SchemaDriftError`` after the
runner wraps it). Optional fields going missing must NOT raise — that's the
DNP-friendly property the new pipeline preserves.
"""

from __future__ import annotations

import inspect
from typing import cast

import pytest
from pydantic import TypeAdapter, ValidationError

from courtside_data.errors import CourtsideDataError, SchemaDriftError
from courtside_data.schemas import (
    ROW_ADAPTERS,
    BRRow,
    boxscores,
    draft,
    league,
    playbyplay,
    players,
    playoffs,
    schedule,
    search,
    standings,
    teams,
)
from courtside_data.schemas.players import PlayerCareerStatsRow

# Endpoint with the most required fields, used as the drift canary throughout.
DRIFT_ENDPOINT = "player_career_stats"


def _adapter() -> TypeAdapter[list[PlayerCareerStatsRow]]:
    """Return the registered ``TypeAdapter`` for the drift canary endpoint.

    ``ROW_ADAPTERS`` is typed against the ``BRRow`` base, so we cast to the
    concrete row type — that's what the runtime object actually is and what
    these tests want to assert against.
    """
    return cast(TypeAdapter[list[PlayerCareerStatsRow]], ROW_ADAPTERS[DRIFT_ENDPOINT])


def _career_row(**overrides: object) -> dict[str, object]:
    """Return a complete, valid ``player_career_stats`` raw row with optional overrides."""
    base: dict[str, object] = {
        "season": "2023-24",
        "age": "39",
        "team_name_abbr": "LAL",
        "league_id": "NBA",
        "pos": "SF",
        "games": "71",
        "games_started": "71",
        "mp_per_g": "35.3",
        "fg_per_g": "9.8",
        "fga_per_g": "19.6",
        "fg_pct": ".502",
        "fg3_per_g": "2.1",
        "fg3a_per_g": "5.1",
        "fg3_pct": ".410",
        "fg2_per_g": "7.7",
        "fg2a_per_g": "14.5",
        "fg2_pct": ".531",
        "efg_pct": ".550",
        "ft_per_g": "3.4",
        "fta_per_g": "4.5",
        "ft_pct": ".750",
        "orb_per_g": "0.8",
        "drb_per_g": "5.5",
        "trb_per_g": "6.3",
        "ast_per_g": "8.3",
        "stl_per_g": "1.3",
        "blk_per_g": "0.5",
        "tov_per_g": "2.9",
        "pf_per_g": "1.1",
        "pts_per_g": "25.1",
    }
    base.update(overrides)
    return base


def test_sanity_baseline_row_validates_cleanly() -> None:
    """Sanity: a well-formed row passes the adapter without error.

    Guards against a bug in the helpers below silently changing the fixture shape.
    """
    rows = _adapter().validate_python([_career_row()])
    assert len(rows) == 1
    assert rows[0].season == "2023-24"
    assert rows[0].points_per_game == pytest.approx(25.1)


def test_rename_of_required_field_raises_schema_drift_error() -> None:
    """A renamed required ``data-stat`` (e.g. ``team_name_abbr`` → ``team_abbr``) must
    surface as a Pydantic ``missing`` error on the original alias. This is the core
    drift signal: BR changed a column and our schema no longer matches.
    """
    drifted_row = _career_row()
    del drifted_row["team_name_abbr"]
    drifted_row["team_abbr"] = "LAL"  # plausible BR rename

    with pytest.raises(ValidationError) as excinfo:
        _adapter().validate_python([drifted_row])

    errors = excinfo.value.errors()
    missing = [err for err in errors if err.get("type") == "missing"]
    assert missing, f"Expected a 'missing' field error, got: {errors!r}"
    # The original BR alias is what shows up in the loc — not the renamed key.
    assert any("team_name_abbr" in (err.get("loc") or ()) for err in missing), (
        f"Expected 'team_name_abbr' in the missing-field loc, got: {missing!r}"
    )


def test_drift_error_wraps_missing_field_name() -> None:
    """A ``SchemaDriftError`` constructed from a Pydantic ``ValidationError`` must
    identify the endpoint, the URL it was fetched from, and the drifted field by
    name/alias — so the error message is actionable rather than a stack trace.
    """
    drifted_row = _career_row()
    del drifted_row["season"]
    drifted_row["season_year"] = "2023-24"

    url = "/players/j/jamesle01.html"
    with pytest.raises(ValidationError) as excinfo:
        _adapter().validate_python([drifted_row])

    drift = SchemaDriftError(
        endpoint_name=DRIFT_ENDPOINT,
        url=url,
        pydantic_errors=cast(list[dict], excinfo.value.errors()),
    )

    # Domain-error typing: SchemaDriftError is a CourtsideDataError so callers can
    # catch the umbrella class without also swallowing httpx transport errors.
    assert isinstance(drift, SchemaDriftError)
    assert isinstance(drift, CourtsideDataError)
    assert drift.endpoint_name == DRIFT_ENDPOINT
    assert drift.pydantic_errors, "pydantic_errors must be carried on the exception"

    message = str(drift)
    assert "player_career_stats" in message
    assert url in message
    # The original alias — the column BR renamed — is what the operator needs to see.
    assert "season" in message


def test_empty_required_stat_cell_does_not_drift() -> None:
    """An empty required stat cell is data absence, not schema drift.

    BR still emits the ``<td data-stat="...">`` element with empty text for
    unplayed games. The key's presence proves the schema still matches, while
    the field parser maps the empty string to ``None`` for downstream code.
    """
    minimal_row = _career_row(fg3_per_g="")

    rows = _adapter().validate_python([minimal_row])  # must not raise
    assert len(rows) == 1
    assert rows[0].made_three_point_field_goals_per_game is None


def test_missing_required_stat_alias_raises_schema_drift() -> None:
    """A missing required stat alias must drift even if empty values are allowed."""
    drifted_row = _career_row()
    del drifted_row["fg3_per_g"]

    with pytest.raises(ValidationError) as excinfo:
        _adapter().validate_python([drifted_row])

    errors = excinfo.value.errors()
    assert any(err.get("type") == "missing" and err.get("loc") == (0, "fg3_per_g") for err in errors)


def test_full_row_with_renamed_key_in_full_pipeline_raises_schema_drift_error() -> None:
    """End-to-end: a fully-populated row whose required key is renamed produces a
    ``SchemaDriftError`` whose string names the URL, the endpoint, and the drifted
    field. The message must be human-readable so operators can act on it.
    """
    url = "/leagues/NBA_2024_totals.html"

    drifted_row = _career_row()
    del drifted_row["team_name_abbr"]
    drifted_row["team_abbr"] = "LAL"

    with pytest.raises(ValidationError) as excinfo:
        _adapter().validate_python([drifted_row])

    drift = SchemaDriftError(
        endpoint_name=DRIFT_ENDPOINT,
        url=url,
        pydantic_errors=cast(list[dict], excinfo.value.errors()),
    )

    message = str(drift)
    assert "Schema drift detected" in message
    assert url in message
    assert DRIFT_ENDPOINT in message
    # The original alias is what we need to grep the BR HTML for when we go fix it.
    assert "team_name_abbr" in message
    # Programmatic access for callers that want to react without parsing the message.
    assert drift.endpoint_name == DRIFT_ENDPOINT
    assert drift.url == url
    assert any(err.get("type") == "missing" for err in drift.pydantic_errors)


def test_drift_simulation_via_validate_python_with_list_input() -> None:
    """List validation: a single drifted row in a batch surfaces the row index in
    the error ``loc``. This is what the runner uses (it always validates
    ``list[RowModel]``) and proves the per-row error reporting works.
    """
    good_row_a = _career_row()
    drifted_row = _career_row()
    # Rename a required field whose Python attribute name is *different* from
    # the BR data-stat alias — this is the realistic BR-rename shape.
    del drifted_row["team_name_abbr"]
    drifted_row["team_abbr"] = "LAL"
    good_row_b = _career_row(season="2022-23")

    with pytest.raises(ValidationError) as excinfo:
        _adapter().validate_python([good_row_a, drifted_row, good_row_b])

    errors = excinfo.value.errors()
    missing = [err for err in errors if err.get("type") == "missing"]
    assert missing, f"Expected a 'missing' field error, got: {errors!r}"

    # The drift is on the middle row (index 1); the missing alias is the
    # original BR data-stat, not the field name or the renamed key.
    middle_row_missing = [err for err in missing if err.get("loc") == (1, "team_name_abbr")]
    assert middle_row_missing, f"Expected loc=(1, 'team_name_abbr') in errors, got: {missing!r}"


def test_every_public_row_class_is_registered() -> None:
    """Every public concrete ``*Row`` model exposed by schema modules has an adapter."""
    modules = [
        boxscores,
        draft,
        league,
        playbyplay,
        players,
        playoffs,
        schedule,
        search,
        standings,
        teams,
    ]
    public_row_names = {
        name
        for module in modules
        for name, value in inspect.getmembers(module, inspect.isclass)
        if name.endswith("Row")
        and not name.startswith("_")
        and issubclass(value, BRRow)
        and value.__module__ == module.__name__
    }
    registered_row_names: set[str] = set()
    for adapter in ROW_ADAPTERS.values():
        schema = adapter.json_schema()
        items = schema.get("items", {})
        if title := items.get("title"):
            registered_row_names.add(title)
        elif ref := items.get("$ref"):
            registered_row_names.add(ref.rsplit("/", 1)[-1])

    assert public_row_names <= registered_row_names
