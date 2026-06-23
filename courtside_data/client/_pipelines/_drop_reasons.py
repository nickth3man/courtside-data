"""Row drop and validation-failure reason classification for the pydantic pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from courtside_data.data import TEAM_NAME_TO_TEAM

# ---------------------------------------------------------------------------
# Drop reason constants (single source of truth)
# ---------------------------------------------------------------------------

DROP_REASON_BLANK_ROW = "blank_row"
DROP_REASON_REPEATED_HEADER = "repeated_header"
DROP_REASON_PARSER_EXCLUDED = "parser_excluded"
DROP_REASON_AGGREGATE_ROW = "aggregate_row"
DROP_REASON_COMBINED_TEAM = "combined_team"
DROP_REASON_HISTORICAL_TEAM_NAME = "historical_team_name"
DROP_REASON_INVALID_TEAM_VALUE = "invalid_team_value"
DROP_REASON_INVALID_PLAYER_VALUE = "invalid_player_value"
DROP_REASON_INVALID_DATE = "invalid_date"
DROP_REASON_MISSING_REQUIRED_FIELD = "missing_required_field"
DROP_REASON_UNSUPPORTED_SENTINEL_VALUE = "unsupported_sentinel_value"
DROP_REASON_SCHEMA_VALIDATION_ERROR = "schema_validation_error"
DROP_REASON_UNKNOWN = "unknown"
DROP_REASON_INVALID_VALUE = "invalid_value"

# Schedule-specific (parser/validation classification)
DROP_REASON_MONTH_HEADER = "month_header"
DROP_REASON_PLAYOFFS_MARKER = "playoffs_marker"
DROP_REASON_POSTPONED_GAME = "postponed_game"
DROP_REASON_NEUTRAL_SITE_NOTE = "neutral_site_note"
DROP_REASON_MISSING_BOX_SCORE_LINK = "missing_box_score_link"
DROP_REASON_MALFORMED_ROW = "malformed_row"

_AGGREGATE_TEAM_ABBREVIATIONS = frozenset({"TOT", "2TM", "3TM", "4TM", "LG"})
_AGGREGATE_ROW_MARKERS = frozenset(
    {
        "league average",
        "lg average",
        "team totals",
        "total",
        "avg",
        "average",
    }
)
_COMBINED_TEAM_SUFFIX = "TM"

_TEAM_FIELD_NAMES = frozenset(
    {
        "team",
        "team_id",
        "team_name",
        "team_name_abbr",
        "visitor_team_name",
        "home_team_name",
        "away_team_name",
        "opp_name",
    }
)
_PLAYER_FIELD_NAMES = frozenset({"player", "name_display", "name"})
_DATE_FIELD_NAMES = frozenset({"date", "date_game", "start_time"})

_SENTINEL_ROW_VALUES = {
    "did not dress",
    "did not play",
    "inactive",
    "not with team",
    "player suspended",
    "suspended",
    "traded",
    "forfeited",
}

_HEADER_ROW_VALUES = {
    "2p",
    "2p%",
    "2pa",
    "3p",
    "3p%",
    "3pa",
    "age",
    "ast",
    "blk",
    "date",
    "drb",
    "efg%",
    "fg",
    "fg%",
    "fga",
    "ft",
    "ft%",
    "fta",
    "g",
    "gs",
    "lg",
    "mp",
    "opp",
    "orb",
    "pf",
    "player",
    "pos",
    "pts",
    "rk",
    "season",
    "stl",
    "team",
    "tov",
    "trb",
    "w/l",
}

_INVALID_VALUE_ERROR_TYPES = frozenset(
    {
        "bool_parsing",
        "date_parsing",
        "datetime_parsing",
        "decimal_parsing",
        "enum",
        "float_parsing",
        "int_parsing",
        "string_type",
        "time_parsing",
        "type_error",
        "url_parsing",
        "uuid_parsing",
    }
)

# Drops that are expected in normal Basketball-Reference tables.
EXPECTED_DROP_REASONS = frozenset(
    {
        DROP_REASON_BLANK_ROW,
        DROP_REASON_REPEATED_HEADER,
        DROP_REASON_PARSER_EXCLUDED,
        DROP_REASON_AGGREGATE_ROW,
        DROP_REASON_COMBINED_TEAM,
        DROP_REASON_UNSUPPORTED_SENTINEL_VALUE,
        DROP_REASON_MONTH_HEADER,
        DROP_REASON_PLAYOFFS_MARKER,
        DROP_REASON_POSTPONED_GAME,
        DROP_REASON_NEUTRAL_SITE_NOTE,
        DROP_REASON_MISSING_BOX_SCORE_LINK,
        DROP_REASON_MALFORMED_ROW,
    }
)

UNRESOLVED_DROP_REASONS = frozenset(
    {DROP_REASON_INVALID_VALUE, DROP_REASON_UNKNOWN, DROP_REASON_SCHEMA_VALIDATION_ERROR}
)


def normalized_cell_value(value: Any) -> str:
    return " ".join(str(value).strip().lower().replace("\xa0", " ").split())


def _row_values(row: Mapping[str, Any]) -> set[str]:
    return {normalized_cell_value(value) for value in row.values() if value not in (None, "")}


def _field_text(row: Mapping[str, Any], *names: str) -> str | None:
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return str(value).strip()
    return None


def _is_aggregate_row(row: Mapping[str, Any]) -> bool:
    team_abbr = _field_text(row, "team_name_abbr", "team_id", "team")
    if team_abbr is not None and team_abbr.upper() in _AGGREGATE_TEAM_ABBREVIATIONS:
        return True
    values = _row_values(row)
    if values & _AGGREGATE_ROW_MARKERS:
        return True
    name = normalized_cell_value(_field_text(row, "name_display", "player") or "")
    return name in _AGGREGATE_ROW_MARKERS


def _is_combined_team_row(row: Mapping[str, Any]) -> bool:
    team_abbr = _field_text(row, "team_name_abbr", "team_id")
    return team_abbr is not None and team_abbr.upper().endswith(_COMBINED_TEAM_SUFFIX)


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


_MONTH_NAMES = frozenset(
    {
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    }
)


def row_drop_reason(row: dict[str, Any]) -> str | None:
    """Return a parser-level drop reason when the row is clearly non-data."""
    values = _row_values(row)
    if not values:
        return DROP_REASON_BLANK_ROW

    schedule_reason = _schedule_drop_reason(row)
    if schedule_reason is not None:
        return schedule_reason

    if any(any(marker in value for marker in _SENTINEL_ROW_VALUES) for value in values):
        return DROP_REASON_UNSUPPORTED_SENTINEL_VALUE

    if _is_combined_team_row(row):
        return DROP_REASON_COMBINED_TEAM

    if _is_aggregate_row(row):
        return DROP_REASON_AGGREGATE_ROW

    if bool(values) and all(normalized_cell_value(key) in values for key in row):
        return DROP_REASON_REPEATED_HEADER
    if bool(values) and all(value in _HEADER_ROW_VALUES for value in values):
        return DROP_REASON_REPEATED_HEADER

    return None


def _error_field_names(errors: Sequence[Mapping[str, Any]]) -> set[str]:
    names: set[str] = set()
    for error in errors:
        location = error.get("loc")
        if isinstance(location, (list, tuple)):
            for part in location:
                names.add(str(part))
        elif location is not None:
            names.add(str(location))
    return names


def validation_error_drop_reason(
    errors: Sequence[Mapping[str, Any]],
    *,
    row: Mapping[str, Any] | None = None,
) -> str:
    """Map pydantic validation errors to a precise drop-reason category."""
    error_types = {str(error.get("type", "")) for error in errors}
    field_names = _error_field_names(errors)

    if "missing" in error_types:
        if field_names & _PLAYER_FIELD_NAMES:
            return DROP_REASON_INVALID_PLAYER_VALUE
        return DROP_REASON_MISSING_REQUIRED_FIELD

    if any(error_type in {"date_parsing", "datetime_parsing", "time_parsing"} for error_type in error_types):
        return DROP_REASON_INVALID_DATE

    if field_names & _TEAM_FIELD_NAMES and (
        "enum" in error_types or any(error_type.startswith("value_error") for error_type in error_types)
    ):
        if row is not None:
            for name in _TEAM_FIELD_NAMES:
                raw = row.get(name)
                if raw in (None, ""):
                    continue
                normalized = str(raw).strip().upper()
                if (
                    normalized not in TEAM_NAME_TO_TEAM
                    and normalized not in _AGGREGATE_TEAM_ABBREVIATIONS
                    and any(
                        token in normalized
                        for token in ("BRAVES", "BULLETS", "KINGS", "HORNETS", "SUPERSONICS", "WARRIORS")
                    )
                ):
                    return DROP_REASON_HISTORICAL_TEAM_NAME
        return DROP_REASON_INVALID_TEAM_VALUE

    if field_names & _PLAYER_FIELD_NAMES and (
        "string_type" in error_types or any(error_type.startswith("value_error") for error_type in error_types)
    ):
        return DROP_REASON_INVALID_PLAYER_VALUE

    if any(
        error_type in _INVALID_VALUE_ERROR_TYPES or error_type.startswith(("value_error", "type_error"))
        for error_type in error_types
    ):
        return DROP_REASON_INVALID_VALUE

    return DROP_REASON_SCHEMA_VALIDATION_ERROR


def sentinel_marker(row: Mapping[str, Any]) -> str | None:
    """Return the matched sentinel marker when present in ``row`` values."""
    for value in row.values():
        if value in (None, ""):
            continue
        normalized = normalized_cell_value(value)
        for marker in _SENTINEL_ROW_VALUES:
            if marker in normalized:
                return marker
    return None


def sentinel_row_diagnostics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize sentinel-like rows retained in validated output."""
    sentinel_types: dict[str, int] = {}
    for row in rows:
        marker = sentinel_marker(row)
        if marker is None:
            continue
        sentinel_types[marker] = sentinel_types.get(marker, 0) + 1
    return {
        "sentinel_row_count": sum(sentinel_types.values()),
        "sentinel_row_types": sentinel_types,
    }


def summarize_drop_counts(dropped_reasons: Mapping[str, int]) -> dict[str, Any]:
    """Split drop counts into expected vs unexpected buckets for probe reporting."""
    expected = 0
    unexpected = 0
    for reason, count in dropped_reasons.items():
        if reason in EXPECTED_DROP_REASONS:
            expected += count
        elif reason in UNRESOLVED_DROP_REASONS or reason not in EXPECTED_DROP_REASONS:
            unexpected += count
    total = expected + unexpected
    drop_rate = round(unexpected / total, 4) if total else 0.0
    return {
        "expected_drop_count": expected,
        "unexpected_drop_count": unexpected,
        "drop_rate": drop_rate,
    }
