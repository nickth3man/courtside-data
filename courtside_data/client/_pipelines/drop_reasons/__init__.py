"""Row drop and validation-failure reason classification."""

from __future__ import annotations

from courtside_data.client._pipelines.drop_reasons.constants import (
    DROP_REASON_AGGREGATE_ROW,
    DROP_REASON_BLANK_ROW,
    DROP_REASON_COMBINED_TEAM,
    DROP_REASON_HISTORICAL_TEAM_NAME,
    DROP_REASON_INVALID_DATE,
    DROP_REASON_INVALID_PLAYER_VALUE,
    DROP_REASON_INVALID_TEAM_VALUE,
    DROP_REASON_INVALID_VALUE,
    DROP_REASON_MALFORMED_ROW,
    DROP_REASON_MISSING_BOX_SCORE_LINK,
    DROP_REASON_MISSING_REQUIRED_FIELD,
    DROP_REASON_MONTH_HEADER,
    DROP_REASON_NEUTRAL_SITE_NOTE,
    DROP_REASON_PARSER_EXCLUDED,
    DROP_REASON_PLAYOFFS_MARKER,
    DROP_REASON_POSTPONED_GAME,
    DROP_REASON_REPEATED_HEADER,
    DROP_REASON_SCHEMA_VALIDATION_ERROR,
    DROP_REASON_UNKNOWN,
    DROP_REASON_UNSUPPORTED_SENTINEL_VALUE,
    EXPECTED_DROP_REASONS,
    UNRESOLVED_DROP_REASONS,
)
from courtside_data.client._pipelines.drop_reasons.helpers import normalized_cell_value
from courtside_data.client._pipelines.drop_reasons.row import (
    row_drop_reason,
    summarize_drop_counts,
)
from courtside_data.client._pipelines.drop_reasons.schedule import (
    _schedule_drop_reason,  # noqa: F401  (re-exported for backward compat)
)
from courtside_data.client._pipelines.drop_reasons.sentinel import (
    sentinel_marker,
    sentinel_row_diagnostics,
)
from courtside_data.client._pipelines.drop_reasons.validation import (
    validation_error_drop_reason,
)

__all__ = [
    "DROP_REASON_AGGREGATE_ROW",
    "DROP_REASON_BLANK_ROW",
    "DROP_REASON_COMBINED_TEAM",
    "DROP_REASON_HISTORICAL_TEAM_NAME",
    "DROP_REASON_INVALID_DATE",
    "DROP_REASON_INVALID_PLAYER_VALUE",
    "DROP_REASON_INVALID_TEAM_VALUE",
    "DROP_REASON_INVALID_VALUE",
    "DROP_REASON_MALFORMED_ROW",
    "DROP_REASON_MISSING_BOX_SCORE_LINK",
    "DROP_REASON_MISSING_REQUIRED_FIELD",
    "DROP_REASON_MONTH_HEADER",
    "DROP_REASON_NEUTRAL_SITE_NOTE",
    "DROP_REASON_PARSER_EXCLUDED",
    "DROP_REASON_PLAYOFFS_MARKER",
    "DROP_REASON_POSTPONED_GAME",
    "DROP_REASON_REPEATED_HEADER",
    "DROP_REASON_SCHEMA_VALIDATION_ERROR",
    "DROP_REASON_UNKNOWN",
    "DROP_REASON_UNSUPPORTED_SENTINEL_VALUE",
    "EXPECTED_DROP_REASONS",
    "UNRESOLVED_DROP_REASONS",
    "normalized_cell_value",
    "row_drop_reason",
    "sentinel_marker",
    "sentinel_row_diagnostics",
    "summarize_drop_counts",
    "validation_error_drop_reason",
]
