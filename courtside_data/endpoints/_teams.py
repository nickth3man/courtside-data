"""Team-page endpoint registrations."""

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
from courtside_data.endpoints._table import _team
from courtside_data.output.columns import (
    FRANCHISE_HISTORY_COLUMN_NAMES,
    TEAM_AND_OPPONENT_COLUMN_NAMES,
    TEAM_CONTRACTS_COLUMN_NAMES,
    TEAM_INJURY_REPORT_COLUMN_NAMES,
    TEAM_LINEUPS_COLUMN_NAMES,
    TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES,
    TEAM_ON_OFF_COLUMN_NAMES,
    TEAM_OPPONENT_STATS_COLUMN_NAMES,
    TEAM_ROSTER_COLUMN_NAMES,
    TEAM_SCHEDULE_COLUMN_NAMES,
    TEAM_SPLITS_COLUMN_NAMES,
    TEAM_STARTING_LINEUPS_COLUMN_NAMES,
    TEAM_TRANSACTIONS_COLUMN_NAMES,
)
from courtside_data.schemas import schedule, teams

TEAM_ENDPOINTS = {
    "team_roster": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        table_id="roster",
        row_model=teams.TeamRosterRow,
        csv_columns=TEAM_ROSTER_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    # League-wide injury page; team/season parameters are accepted for API
    # symmetry but do not affect the request.
    "team_injury_report": _team(
        "/friv/injuries.fcgi",
        table_id="injuries",
        row_model=teams.TeamInjuryReportRow,
        csv_columns=TEAM_INJURY_REPORT_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "team_and_opponent": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        commented_table_id="team_and_opponent",
        row_model=teams.TeamAndOpponentRow,
        csv_columns=TEAM_AND_OPPONENT_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "team_misc_four_factors": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        commented_table_id="team_misc",
        row_model=teams.TeamMiscFourFactorsRow,
        csv_columns=TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    # Scrapes the same #team_and_opponent table as team_and_opponent; kept as a
    # separate endpoint with its own column set.
    "team_opponent_stats": _team(
        "/teams/{team_abbreviation}/{season_end_year}.html",
        commented_table_id="team_and_opponent",
        row_model=teams.TeamOpponentStatsRow,
        csv_columns=TEAM_OPPONENT_STATS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "team_schedule": _team(
        "/teams/{team_abbreviation}/{season_end_year}_games.html",
        table_id="games",
        row_model=schedule.TeamScheduleRow,
        csv_columns=TEAM_SCHEDULE_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "team_transactions": _team(
        "/teams/{team_abbreviation}/{season_end_year}_transactions.html",
        table_id="transactions",
        transaction_list_fallback=True,
        row_model=teams.TeamTransactionsRow,
        csv_columns=TEAM_TRANSACTIONS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TRANSACTION_LIST,
            features=frozenset({EndpointFeature.TRANSACTION_LIST_FALLBACK}),
        ),
    ),
    "team_splits": _team(
        "/teams/{team_abbreviation}/{season_end_year}/splits/",
        table_id="team_splits",
        row_model=teams.TeamSplitsRow,
        csv_columns=TEAM_SPLITS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "team_contracts": _team(
        "/contracts/{team_abbreviation}.html",
        params=("team_abbreviation",),
        table_id="contracts",
        row_model=teams.TeamContractsRow,
        csv_columns=TEAM_CONTRACTS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "team_lineups": _team(
        "/teams/{team_abbreviation}/{season_end_year}/lineups/",
        commented_table_id="lineups_5-man_",
        row_model=teams.TeamLineupsRow,
        csv_columns=TEAM_LINEUPS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.COMMENTED_TABLE,
            features=frozenset({EndpointFeature.COMMENTED_TABLE}),
        ),
    ),
    "team_starting_lineups": _team(
        "/teams/{team_abbreviation}/{season_end_year}_start.html",
        table_id="starting_lineups_po0",
        row_model=teams.TeamStartingLineupsRow,
        csv_columns=TEAM_STARTING_LINEUPS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "team_on_off": _team(
        "/teams/{team_abbreviation}/{season_end_year}/on-off/",
        table_id="on_off",
        row_model=teams.TeamOnOffRow,
        csv_columns=TEAM_ON_OFF_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
    "franchise_history": _team(
        "/teams/{team_abbreviation}/",
        params=("team_abbreviation",),
        table_id="{team_abbreviation}",
        row_model=teams.FranchiseHistoryRow,
        csv_columns=FRANCHISE_HISTORY_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
        ),
    ),
}
