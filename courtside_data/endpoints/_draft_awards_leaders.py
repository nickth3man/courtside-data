"""Draft, awards, and leaderboard endpoint registrations."""

from __future__ import annotations

from courtside_data.endpoints._metadata import (
    EndpointDomain,
    EndpointFeature,
    EndpointKind,
    EndpointMetadata,
    EndpointScope,
    ParserShape,
    RequestShape,
)
from courtside_data.endpoints._table import EndpointSpec, _season
from courtside_data.endpoints._workflow import WorkflowSpec, WorkflowStep
from courtside_data.output.columns import (
    CAREER_LEADERS_COLUMN_NAMES,
    DRAFT_PICKS_COLUMN_NAMES,
    SEASON_AWARDS_COLUMN_NAMES,
    SEASON_AWARDS_VOTING_COLUMN_NAMES,
    SEASON_LEADERS_COLUMN_NAMES,
)
from courtside_data.schemas import draft, league

_SEASON_AWARDS_VOTING_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="normalize_award_id",
            kind="derive",
            description="Normalize the award parameter into the Basketball Reference table id.",
            inputs=("award",),
            outputs=("table_id",),
        ),
        WorkflowStep(
            id="fetch_awards_page",
            kind="fetch",
            description="Fetch the season awards page.",
            inputs=("season_end_year",),
            outputs=("awards_page",),
        ),
        WorkflowStep(
            id="select_award_table",
            kind="select",
            description="Select the normalized award table, returning no rows when it is absent.",
            inputs=("awards_page", "table_id"),
            outputs=("award_table",),
        ),
        WorkflowStep(
            id="parse_award_rows",
            kind="parse",
            description="Parse raw data-stat rows from the selected award voting table.",
            inputs=("award_table",),
            outputs=("rows",),
            parser_id="awards_voting_table",
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind="diagnostics",
            description="Record parser diagnostics with the selected award table id.",
            inputs=("rows", "table_id"),
        ),
    ),
)

DRAFT_AWARDS_LEADERS_ENDPOINTS = {
    "draft_picks": _season(
        "/draft/NBA_{season_end_year}.html",
        table_id="stats",
        row_model=draft.DraftPicksRow,
        csv_columns=DRAFT_PICKS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.DRAFT_AWARDS_LEADERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "season_awards": _season(
        "/awards/awards_{season_end_year}.html",
        table_id="mvp",
        fallback_table_ids=("nba_mvp",),
        row_model=league.SeasonAwardsRow,
        csv_columns=SEASON_AWARDS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.DRAFT_AWARDS_LEADERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.FALLBACK_TABLE_IDS}),
        ),
    ),
    "season_awards_voting": _season(
        "/awards/awards_{season_end_year}.html",
        params=("season_end_year", "award"),
        table_id="{award}",
        fallback_table_ids=(
            "mvp",
            "roy",
            "dpoy",
            "smoy",
            "mip",
            "clutch_poy",
            "coy",
            "leading_all_nba",
            "leading_all_defense",
            "leading_all_rookie",
        ),
        row_model=league.SeasonAwardsVotingRow,
        csv_columns=SEASON_AWARDS_VOTING_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.DRAFT_AWARDS_LEADERS,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.FALLBACK_TABLE_IDS, EndpointFeature.CUSTOM_DIAGNOSTICS}),
        ),
        workflow=_SEASON_AWARDS_VOTING_WORKFLOW,
    ),
    "season_leaders": EndpointSpec(
        path="/leaders/per_season.html",
        table_id="stats_TOT",
        use_header_fallback=True,
        # The third column header rotates with the active stat category
        # (``per``, ``pts``, ``ast`` ...). ``value_column`` renames the rightmost
        # non-text column to a stable ``value`` key so the row model validates.
        value_column=True,
        row_model=league.SeasonLeadersRow,
        csv_columns=SEASON_LEADERS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.DRAFT_AWARDS_LEADERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.HEADER_FALLBACK, EndpointFeature.VALUE_COLUMN}),
        ),
    ),
    "career_leaders": EndpointSpec(
        # Re-registered from ``/leaders/`` (a navigation index) to the
        # canonical career-points leaderboard at ``/leaders/pts_career.html``.
        # The previous registration targeted ``table#leaders_index``, a
        # stat-category navigation page whose rows don't match the
        # rank/player/value schema. ``/leaders/pts_career.html`` is a real
        # per-stat leaderboard (``table#tot``, columns Rank/Player/PTS) and
        # is the default career leaderboard BR surfaces.
        path="/leaders/pts_career.html",
        table_id="tot",
        use_header_fallback=True,
        value_column=True,
        row_model=league.CareerLeadersRow,
        csv_columns=CAREER_LEADERS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.DRAFT_AWARDS_LEADERS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.STATIC,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.HEADER_FALLBACK, EndpointFeature.VALUE_COLUMN}),
        ),
    ),
}
