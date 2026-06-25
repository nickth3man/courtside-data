"""Focused tests for the P0 provenance-driven fixes.

Covers three evidence-backed regressions where valid source rows were dropped:

1. Historical draft team abbreviations ``BAL`` (1963-73 Baltimore Bullets) and
   ``CIN`` (Cincinnati Royals) now resolve through the team lookup.
2. ``CareerLeadersRow.rank`` tolerates blank/nbsp rank cells (tied entries).
3. ``SeasonAwardsRow`` / ``SeasonAwardsVotingRow`` parse BR's tied-rank suffix
   (``"7T"`` / ``"10T"``) and surface the tie via a ``rank_tied`` companion
   field instead of dropping the row.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from courtside_data.client._pipelines.drop_reasons import DROP_REASON_INVALID_VALUE
from courtside_data.client._pipelines.pydantic import _validate_row_model_rows_detailed
from courtside_data.domain import (
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
    Team,
)
from courtside_data.parsing.generic import find_table
from courtside_data.schemas._fields import BRInt, TeamField
from courtside_data.schemas.awards import CareerLeadersRow, SeasonAwardsRow, SeasonAwardsVotingRow
from parsel import Selector
from pydantic import BaseModel, TypeAdapter, ValidationError

from tests.fixture_manifest import case_for

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAREER_LEADERS_FIXTURE = PROJECT_ROOT / "raw" / "career_leaders" / "default.html"
SEASON_AWARDS_VOTING_FIXTURE = PROJECT_ROOT / "raw" / "season_awards_voting" / "awards_2025.html"


# ---------------------------------------------------------------------------
# 1. Historical team abbreviations
# ---------------------------------------------------------------------------


class TestHistoricalTeamAbbreviations:
    """``BAL`` and ``CIN`` are real historical drafting teams and must resolve."""

    def test_bal_maps_to_baltimore_bullets(self) -> None:
        assert TEAM_ABBREVIATIONS_TO_TEAM["BAL"] is Team.BALTIMORE_BULLETS

    def test_cin_maps_to_cincinnati_royals(self) -> None:
        assert TEAM_ABBREVIATIONS_TO_TEAM["CIN"] is Team.CINCINNATI_ROYALS
        assert Team.CINCINNATI_ROYALS.value == "CINCINNATI ROYALS"

    def test_cincinnati_royals_name_resolves(self) -> None:
        assert TEAM_NAME_TO_TEAM["CINCINNATI ROYALS"] is Team.CINCINNATI_ROYALS

    def test_blb_still_maps_to_defunct_baltimore_bullets(self) -> None:
        """The original BAA Baltimore Bullets abbreviation is unaffected."""
        assert TEAM_ABBREVIATIONS_TO_TEAM["BLB"] is Team.BALTIMORE_BULLETS

    def test_reverse_canonical_for_baltimore_bullets_preserved_as_blb(self) -> None:
        """Adding ``BAL`` must not change the existing reverse-lookup canonical."""
        assert TEAM_TO_TEAM_ABBREVIATION[Team.BALTIMORE_BULLETS] == "BLB"

    def test_team_field_validates_bal_and_cin(self) -> None:
        adapter = TypeAdapter(TeamField)
        assert adapter.validate_python("BAL") is Team.BALTIMORE_BULLETS
        assert adapter.validate_python("CIN") is Team.CINCINNATI_ROYALS

    @pytest.mark.parametrize("bad", ["NOT_A_REAL_TEAM", "XYZ", "BALTIMORE", "CINN"])
    def test_unknown_abbreviations_still_rejected(self, bad: str) -> None:
        adapter = TypeAdapter(TeamField)
        with pytest.raises(ValidationError):
            adapter.validate_python(bad)


# ---------------------------------------------------------------------------
# 2. CareerLeadersRow rank — blank/nbsp tied cells retained as None
# ---------------------------------------------------------------------------


class TestCareerLeadersRank:
    def test_numeric_rank_parses_as_int(self) -> None:
        row = CareerLeadersRow.model_validate({"rank": "1", "player": "LeBron James", "value": "43440"})
        assert row.rank == 1

    @pytest.mark.parametrize("blank", ["", " ", "\xa0"])
    def test_blank_rank_retained_as_none(self, blank: str) -> None:
        """Blank/nbsp rank cells (tied entries) must not drop the row."""
        row = CareerLeadersRow.model_validate({"rank": blank, "player": "Tied Player", "value": "27000"})
        assert row.rank is None
        assert row.player == "Tied Player"

    def test_garbage_rank_still_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CareerLeadersRow.model_validate({"rank": "abc", "player": "P", "value": "V"})


# ---------------------------------------------------------------------------
# 3. SeasonAwardsRow tied ranks — suffix stripped, tie flagged
# ---------------------------------------------------------------------------


class TestAwardTiedRank:
    @pytest.mark.parametrize(("tied", "value"), [("7T", 7), ("10T", 10), ("12T", 12)])
    def test_tied_rank_strips_suffix_and_flags(self, tied: str, value: int) -> None:
        row = SeasonAwardsRow.model_validate({"rank": tied, "player": "P"})
        assert row.rank == value
        assert row.rank_tied is True

    def test_plain_rank_not_flagged_as_tied(self) -> None:
        row = SeasonAwardsRow.model_validate({"rank": "3", "player": "P"})
        assert row.rank == 3
        assert row.rank_tied is False

    def test_blank_rank_is_none_and_not_tied(self) -> None:
        row = SeasonAwardsRow.model_validate({"rank": "", "player": "P"})
        assert row.rank is None
        assert row.rank_tied is False

    def test_tied_rank_preserved_through_voting_subclass(self) -> None:
        row = SeasonAwardsVotingRow.model_validate({"rank": "7T", "player": "P", "age": "28"})
        assert row.rank == 7
        assert row.rank_tied is True

    def test_lowercase_t_suffix_handled(self) -> None:
        # Defensive: BR uses uppercase T, but tolerate the suffix case-insensitively.
        row = SeasonAwardsRow.model_validate({"rank": "7t", "player": "P"})
        assert row.rank == 7
        assert row.rank_tied is True

    def test_garbage_rank_still_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SeasonAwardsRow.model_validate({"rank": "abc", "player": "P"})


# ---------------------------------------------------------------------------
# 4. Regression — general BRInt unaffected
# ---------------------------------------------------------------------------


class _IntRow(BaseModel):
    """Minimal model exercising the general-purpose ``BRInt`` (unrelated fields)."""

    n: BRInt


def test_general_brint_still_rejects_non_integer() -> None:
    """The rank-specific tolerance must not bleed into the general BRInt validator."""
    assert _IntRow.model_validate({"n": "42"}).n == 42
    with pytest.raises(ValidationError):
        _IntRow.model_validate({"n": "7T"})
    with pytest.raises(ValidationError):
        _IntRow.model_validate({"n": ""})


# ---------------------------------------------------------------------------
# 5. End-to-end fixture row-count assertions (the audited cases)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not CAREER_LEADERS_FIXTURE.exists(), reason="career_leaders fixture missing")
def test_career_leaders_fixture_retains_all_rows(make_offline_client) -> None:
    """Audited case: 250 source rows, previously 8 dropped on blank rank."""
    case = case_for("career_leaders")
    if case is None:
        pytest.skip("no career_leaders manifest case")
    client = make_offline_client(case)
    result = client.career_leaders()
    assert len(result) == 250
    assert all(isinstance(row, CareerLeadersRow) for row in result)
    # Some retained rows carry a None rank (the previously-dropped tied entries).
    assert any(row.rank is None for row in result)


@pytest.mark.skipif(not SEASON_AWARDS_VOTING_FIXTURE.exists(), reason="season_awards_voting fixture missing")
def test_season_awards_voting_fixture_retains_tied_mvp_ranks(make_offline_client) -> None:
    """Audited case: 12 MVP source rows, previously 5 dropped on 7T/10T ranks."""
    case = case_for("season_awards_voting", season_end_year=2025, award="mvp")
    if case is None:
        pytest.skip("no season_awards_voting mvp-2025 manifest case")
    client = make_offline_client(case)
    result = client.season_awards_voting(season_end_year=2025, award="mvp")
    assert len(result) == 12
    assert all(isinstance(row, SeasonAwardsVotingRow) for row in result)
    # Tied ranks are retained and flagged.
    assert any(row.rank_tied for row in result)
    # No rank value was silently invented: plain ranks stay int, tied ranks keep the int base.
    assert all(isinstance(row.rank, int) for row in result)


@pytest.mark.skipif(not SEASON_AWARDS_VOTING_FIXTURE.exists(), reason="season_awards_voting fixture missing")
def test_season_awards_voting_fixture_no_invalid_value_drops() -> None:
    """Direct parse path for the MVP table: zero ``invalid_value`` rank drops."""
    html = SEASON_AWARDS_VOTING_FIXTURE.read_text(encoding="utf-8")
    table = find_table(Selector(text=html), "mvp")
    assert table is not None, "MVP table missing from awards_2025 fixture"
    from courtside_data.parsing import rows

    parser_rows = [row for row, _ in rows.raw_rows_from_table(table)]

    validated, dropped, _kept, _details, _drift = _validate_row_model_rows_detailed(SeasonAwardsVotingRow, parser_rows)

    assert dropped.get(DROP_REASON_INVALID_VALUE, 0) == 0
    assert len(validated) == len(parser_rows)


@pytest.mark.skipif(not SEASON_AWARDS_VOTING_FIXTURE.exists(), reason="season_awards_voting fixture missing")
def test_season_awards_voting_fixture_has_tied_ranks() -> None:
    """The MVP fixture really does carry tied ranks (7T/10T) that are now retained."""
    html = SEASON_AWARDS_VOTING_FIXTURE.read_text(encoding="utf-8")
    table = find_table(Selector(text=html), "mvp")
    assert table is not None
    from courtside_data.parsing import rows

    parser_rows = [row for row, _ in rows.raw_rows_from_table(table)]
    raw_ranks = {str(r.get("rank")) for r in parser_rows}
    assert any(str(r).upper().endswith("T") for r in raw_ranks if r not in (None, "")), (
        f"expected at least one tied rank (e.g. '7T') in fixture; got {raw_ranks}"
    )
