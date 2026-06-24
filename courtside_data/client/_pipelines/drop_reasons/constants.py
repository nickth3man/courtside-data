"""Drop-reason constants (single source of truth)."""

from __future__ import annotations

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
