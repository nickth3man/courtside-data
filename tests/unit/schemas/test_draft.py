"""Unit tests for the draft row schema."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import Team
from courtside_data.output.columns import DRAFT_PICKS_COLUMN_NAMES
from courtside_data.schemas.draft import DraftPicksRow


def _full_draft_row() -> dict[str, str]:
    return {
        "pick_overall": "1",
        "player": "LeBron James",
        "college_name": "St. Vincent–St. Mary HS (OH)",
        "team_id": "CLE",
        "seasons": "21",
        "g": "1547",
        "mp": "56453",
        "pts": "40474",
        "trb": "11309",
        "ast": "11209",
        "fg_pct": ".505",
        "fg3_pct": ".345",
        "ft_pct": ".735",
        "mp_per_g": "36.5",
        "pts_per_g": "27.2",
        "trb_per_g": "7.5",
        "ast_per_g": "7.4",
        "ws": "270.5",
        "ws_per_48": ".230",
        "bpm": "8.7",
        "vorp": "150.0",
    }


class TestDraftPicksRow:
    def test_happy_path(self):
        row = DraftPicksRow.model_validate(_full_draft_row())
        assert row.pick_overall == 1
        assert row.player == "LeBron James"
        assert row.team == Team.CLEVELAND_CAVALIERS
        assert row.college_name == "St. Vincent–St. Mary HS (OH)"
        assert row.seasons == 21
        assert row.points == 40474
        assert row.total_rebounds == 11309
        assert row.assists == 11209
        assert row.field_goal_percentage == pytest.approx(0.505)
        assert row.three_point_field_goal_percentage == pytest.approx(0.345)
        assert row.free_throw_percentage == pytest.approx(0.735)
        assert row.points_per_game == pytest.approx(27.2)
        assert row.win_shares == pytest.approx(270.5)
        assert row.box_plus_minus == pytest.approx(8.7)

    def test_empty_optional_cells_become_none(self):
        # Only the required ``pick_overall`` and ``player`` are present;
        # every other column is optional and falls back to ``None`` because
        # it's declared with ``default=None``.
        raw = {
            "pick_overall": "58",
            "player": "Draft Bust",
            "team_id": "BOS",
        }
        row = DraftPicksRow.model_validate(raw)
        assert row.college_name is None
        assert row.seasons is None
        assert row.games is None
        assert row.points is None
        assert row.field_goal_percentage is None
        assert row.points_per_game is None
        assert row.win_shares is None
        assert row.value_over_replacement_player is None

    def test_empty_string_college_name_preserved(self):
        # An explicit empty-string college cell passes through as ``""``
        # (matching the TeamRosterRow pattern); only a missing key yields
        # ``None``.
        raw = _full_draft_row()
        raw["college_name"] = ""
        row = DraftPicksRow.model_validate(raw)
        assert row.college_name == ""

    def test_alias_keys_match_validation_alias(self):
        # The fetcher emits raw dicts keyed by the data-stat names; the
        # model should accept those keys (and ignore extras).
        raw = {
            "pick_overall": "1",
            "player": "LeBron James",
            "college_name": "St. Vincent–St. Mary HS (OH)",
            "team_id": "CLE",
            "extra_column_that_br_might_add": "ignored",
        }
        row = DraftPicksRow.model_validate(raw)
        assert row.player == "LeBron James"
        assert row.team == Team.CLEVELAND_CAVALIERS

    def test_strict_rank_rejects_garbage(self):
        raw = _full_draft_row()
        raw["pick_overall"] = "abc"
        with pytest.raises(ValidationError):
            DraftPicksRow.model_validate(raw)

    def test_strict_points_rejects_garbage(self):
        raw = _full_draft_row()
        raw["pts"] = "not-a-number"
        with pytest.raises(ValidationError):
            DraftPicksRow.model_validate(raw)

    def test_missing_required_pick_overall_raises(self):
        raw = _full_draft_row()
        del raw["pick_overall"]
        with pytest.raises(ValidationError):
            DraftPicksRow.model_validate(raw)

    def test_missing_required_player_raises(self):
        raw = _full_draft_row()
        del raw["player"]
        with pytest.raises(ValidationError):
            DraftPicksRow.model_validate(raw)

    def test_field_count_matches_column_constant(self):
        assert len(DraftPicksRow.model_fields) == len(DRAFT_PICKS_COLUMN_NAMES)
