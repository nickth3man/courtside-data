"""Drop-reason constants (single source of truth).

The ``DROP_REASON_*`` constants are module-level aliases of the
corresponding :class:`~courtside_data._row_exclusion.RowExclusionReason`
member's ``.value``. The emitted string is byte-identical to the legacy
literal; this is a purely additive canonicalization.
"""

from __future__ import annotations

from courtside_data._row_exclusion import RowExclusionReason

# ---------------------------------------------------------------------------
# Drop reason constants (single source of truth)
# ---------------------------------------------------------------------------

DROP_REASON_BLANK_ROW = RowExclusionReason.PIPELINE_BLANK_ROW.value
DROP_REASON_REPEATED_HEADER = RowExclusionReason.PIPELINE_REPEATED_HEADER.value
DROP_REASON_PARSER_EXCLUDED = RowExclusionReason.PIPELINE_PARSER_EXCLUDED.value
DROP_REASON_AGGREGATE_ROW = RowExclusionReason.PIPELINE_AGGREGATE_ROW.value
DROP_REASON_COMBINED_TEAM = RowExclusionReason.PIPELINE_COMBINED_TEAM.value
DROP_REASON_HISTORICAL_TEAM_NAME = RowExclusionReason.PIPELINE_HISTORICAL_TEAM_NAME.value
DROP_REASON_INVALID_TEAM_VALUE = RowExclusionReason.PIPELINE_INVALID_TEAM_VALUE.value
DROP_REASON_INVALID_PLAYER_VALUE = RowExclusionReason.PIPELINE_INVALID_PLAYER_VALUE.value
DROP_REASON_INVALID_DATE = RowExclusionReason.PIPELINE_INVALID_DATE.value
DROP_REASON_MISSING_REQUIRED_FIELD = RowExclusionReason.PIPELINE_MISSING_REQUIRED_FIELD.value
DROP_REASON_UNSUPPORTED_SENTINEL_VALUE = RowExclusionReason.PIPELINE_UNSUPPORTED_SENTINEL_VALUE.value
DROP_REASON_SCHEMA_VALIDATION_ERROR = RowExclusionReason.PIPELINE_SCHEMA_VALIDATION_ERROR.value
DROP_REASON_UNKNOWN = RowExclusionReason.PIPELINE_UNKNOWN.value
DROP_REASON_INVALID_VALUE = RowExclusionReason.PIPELINE_INVALID_VALUE.value

# Schedule-specific (parser/validation classification)
DROP_REASON_MONTH_HEADER = RowExclusionReason.PIPELINE_MONTH_HEADER.value
DROP_REASON_PLAYOFFS_MARKER = RowExclusionReason.PIPELINE_PLAYOFFS_MARKER.value
DROP_REASON_POSTPONED_GAME = RowExclusionReason.PIPELINE_POSTPONED_GAME.value
DROP_REASON_NEUTRAL_SITE_NOTE = RowExclusionReason.PIPELINE_NEUTRAL_SITE_NOTE.value
DROP_REASON_MISSING_BOX_SCORE_LINK = RowExclusionReason.PIPELINE_MISSING_BOX_SCORE_LINK.value
DROP_REASON_MALFORMED_ROW = RowExclusionReason.PIPELINE_MALFORMED_ROW.value

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
