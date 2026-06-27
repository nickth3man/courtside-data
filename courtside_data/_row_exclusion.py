"""Canonical registry for row-exclusion reasons emitted by courtside-data.

Unifies the two previously-parallel taxonomies -- the parser-side
``IGNORE_*`` constants in :mod:`courtside_data.parsing.workflow_parsers._diagnostics`
and the pipeline-side ``DROP_REASON_*`` constants in
:mod:`courtside_data.client._pipelines.drop_reasons.constants` -- into a single
:class:`RowExclusionReason` enum so callers can reason about every row-exclusion
reason by stage without coordinating two sets of string constants.

The legacy module-level constants remain in place and are defined as
``<enum member>.value``, so the strings emitted at runtime are byte-identical
to the originals. This is a purely additive canonicalization: no diagnostic
string changes, no caller breakage, no behavior change.

Why ``auto()`` instead of literal string values?
------------------------------------------------
The two source taxonomies share one value, ``"combined_team"`` (parser emits it
from :mod:`courtside_data.parsing.workflow_parsers._common`; the pipeline emits
it from :mod:`courtside_data.client._pipelines.drop_reasons.row`). Standard
:class:`enum.Enum` semantics alias any member whose value matches a previously
declared one, which would collapse ``PIPELINE_COMBINED_TEAM`` into
``PARSER_COMBINED_TEAM`` and make the per-member :attr:`stage` property report
the wrong stage. Using :func:`enum.auto` gives every member a distinct internal
identity while :attr:`value` is overridden to return the byte-identical legacy
string looked up in :data:`_LEGACY_VALUES_BY_NAME`.

Stages
------
* ``"parser"`` -- reasons emitted by
  :mod:`courtside_data.parsing.workflow_parsers` into
  ``ignored_row_reason_counts`` before any validation. Historically prefixed
  ``IGNORE_`` in :mod:`courtside_data.parsing.workflow_parsers._diagnostics`.
* ``"pipeline"`` -- reasons emitted by the row-validation pipelines under
  :mod:`courtside_data.client._pipelines.drop_reasons` after parsing but
  before persistence. Historically prefixed ``DROP_REASON_`` in
  :mod:`courtside_data.client._pipelines.drop_reasons.constants`.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Literal

# A reason that appears in both stages (today only ``"combined_team"``) gets a
# dedicated enum member per stage so each member has exactly one stage tag.
# A few reason values share substrings across stages (``"missing_*"``,
# ``"invalid_*"``); the stage prefix on the member name is what disambiguates
# them in code, while :attr:`RowExclusionReason.value` returns the
# byte-identical legacy string.

# Forward declaration of the lookup table. The real table is defined after the
# enum class below so each member name can be referenced as a class attribute.
_LEGACY_VALUES_BY_NAME: dict[str, str] = {}


class RowExclusionReason(Enum):
    """Canonical row-exclusion reason registry.

    Every member's :attr:`value` is byte-identical to the legacy string emitted
    by the corresponding ``IGNORE_*`` or ``DROP_REASON_*`` constant. The
    :attr:`stage` property reports which stage originally emits the reason.
    """

    # --- parser stage (workflow_parsers._diagnostics IGNORE_*) ---
    PARSER_MISSING_DATE = auto()
    PARSER_INACTIVE_GAME = auto()
    PARSER_MISSING_NAME_OR_TEAM = auto()
    PARSER_COMBINED_TEAM = auto()
    PARSER_MISSING_TABLE = auto()
    PARSER_MISSING_FOOTER = auto()
    PARSER_EMPTY_TABLE = auto()

    # --- pipeline stage (drop_reasons.constants DROP_REASON_*) ---
    PIPELINE_BLANK_ROW = auto()
    PIPELINE_REPEATED_HEADER = auto()
    PIPELINE_PARSER_EXCLUDED = auto()
    PIPELINE_AGGREGATE_ROW = auto()
    PIPELINE_COMBINED_TEAM = auto()
    PIPELINE_HISTORICAL_TEAM_NAME = auto()
    PIPELINE_INVALID_TEAM_VALUE = auto()
    PIPELINE_INVALID_PLAYER_VALUE = auto()
    PIPELINE_INVALID_DATE = auto()
    PIPELINE_MISSING_REQUIRED_FIELD = auto()
    PIPELINE_UNSUPPORTED_SENTINEL_VALUE = auto()
    PIPELINE_SCHEMA_VALIDATION_ERROR = auto()
    PIPELINE_UNKNOWN = auto()
    PIPELINE_INVALID_VALUE = auto()
    PIPELINE_MONTH_HEADER = auto()
    PIPELINE_PLAYOFFS_MARKER = auto()
    PIPELINE_POSTPONED_GAME = auto()
    PIPELINE_NEUTRAL_SITE_NOTE = auto()
    PIPELINE_MISSING_BOX_SCORE_LINK = auto()
    PIPELINE_MALFORMED_ROW = auto()

    @property
    def value(self) -> str:
        """Byte-identical legacy string emitted for this reason."""
        return _LEGACY_VALUES_BY_NAME[self.name]

    @property
    def stage(self) -> Literal["parser", "pipeline"]:
        """Originating stage for this exclusion reason."""
        name = self.name
        if name.startswith("PARSER_"):
            return "parser"
        if name.startswith("PIPELINE_"):
            return "pipeline"
        raise AssertionError(f"RowExclusionReason member {name!r} is missing a stage prefix")


# Populate the lookup table after the class body so every member name is a
# defined class attribute. The table is keyed by member name and holds the
# byte-identical legacy string used at every callsite that previously imported
# the ``IGNORE_*`` or ``DROP_REASON_*`` constants.
_LEGACY_VALUES_BY_NAME.update(
    {
        "PARSER_MISSING_DATE": "missing_date",
        "PARSER_INACTIVE_GAME": "inactive_game",
        "PARSER_MISSING_NAME_OR_TEAM": "missing_name_or_team",
        "PARSER_COMBINED_TEAM": "combined_team",
        "PARSER_MISSING_TABLE": "missing_table",
        "PARSER_MISSING_FOOTER": "missing_footer",
        "PARSER_EMPTY_TABLE": "empty_table",
        "PIPELINE_BLANK_ROW": "blank_row",
        "PIPELINE_REPEATED_HEADER": "repeated_header",
        "PIPELINE_PARSER_EXCLUDED": "parser_excluded",
        "PIPELINE_AGGREGATE_ROW": "aggregate_row",
        "PIPELINE_COMBINED_TEAM": "combined_team",
        "PIPELINE_HISTORICAL_TEAM_NAME": "historical_team_name",
        "PIPELINE_INVALID_TEAM_VALUE": "invalid_team_value",
        "PIPELINE_INVALID_PLAYER_VALUE": "invalid_player_value",
        "PIPELINE_INVALID_DATE": "invalid_date",
        "PIPELINE_MISSING_REQUIRED_FIELD": "missing_required_field",
        "PIPELINE_UNSUPPORTED_SENTINEL_VALUE": "unsupported_sentinel_value",
        "PIPELINE_SCHEMA_VALIDATION_ERROR": "schema_validation_error",
        "PIPELINE_UNKNOWN": "unknown",
        "PIPELINE_INVALID_VALUE": "invalid_value",
        "PIPELINE_MONTH_HEADER": "month_header",
        "PIPELINE_PLAYOFFS_MARKER": "playoffs_marker",
        "PIPELINE_POSTPONED_GAME": "postponed_game",
        "PIPELINE_NEUTRAL_SITE_NOTE": "neutral_site_note",
        "PIPELINE_MISSING_BOX_SCORE_LINK": "missing_box_score_link",
        "PIPELINE_MALFORMED_ROW": "malformed_row",
    }
)


__all__ = ["RowExclusionReason"]
