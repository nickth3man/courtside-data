"""Schedule-specific drop reason classification."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from courtside_data.client._pipelines.drop_reasons.constants import (
    _MONTH_NAMES,
    DROP_REASON_MALFORMED_ROW,
    DROP_REASON_MISSING_BOX_SCORE_LINK,
    DROP_REASON_MONTH_HEADER,
    DROP_REASON_NEUTRAL_SITE_NOTE,
    DROP_REASON_PLAYOFFS_MARKER,
    DROP_REASON_POSTPONED_GAME,
)
from courtside_data.client._pipelines.drop_reasons.helpers import (
    _field_text,
    normalized_cell_value,
)


def _is_schedule_row(row: Mapping[str, Any]) -> bool:
    return "visitor_team_name" in row or "home_team_name" in row or "away_team_name" in row


def _schedule_drop_reason(row: Mapping[str, Any]) -> str | None:
    """Classify non-game or schedule-specific rows before pydantic validation."""
    if not _is_schedule_row(row):
        return None

    visitor = _field_text(row, "visitor_team_name", "away_team_name")
    home = _field_text(row, "home_team_name")
    date_game = _field_text(row, "date_game", "date")

    if not visitor and not home:
        if date_game and any(month in normalized_cell_value(date_game) for month in _MONTH_NAMES):
            return DROP_REASON_MONTH_HEADER
        return DROP_REASON_MALFORMED_ROW

    remarks = normalized_cell_value(_field_text(row, "game_remarks") or "")
    if "postponed" in remarks:
        return DROP_REASON_POSTPONED_GAME
    if "playoffs" in remarks or "playoff" in remarks:
        return DROP_REASON_PLAYOFFS_MARKER
    if "neutral site" in remarks or ("at " in remarks and "neutral" in remarks):
        return DROP_REASON_NEUTRAL_SITE_NOTE

    if not date_game:
        return DROP_REASON_MALFORMED_ROW

    box_score = _field_text(row, "box_score_text")
    if box_score is None and remarks and "tbd" not in remarks and (not visitor or not home):
        return DROP_REASON_MISSING_BOX_SCORE_LINK

    return None
