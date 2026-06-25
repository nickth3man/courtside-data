"""Native workflow endpoint registrations."""

from __future__ import annotations

from courtside_data.endpoints._error_mapping import NOT_FOUND_OR_SERVER_ERROR
from courtside_data.endpoints._metadata import (
    EndpointDomain,
    EndpointFeature,
    EndpointKind,
    EndpointMetadata,
    EndpointScope,
    ParserShape,
    RequestShape,
)
from courtside_data.endpoints._table import _endpoint, _season
from courtside_data.endpoints._workflow import WorkflowSpec, WorkflowStep, WorkflowStepKind
from courtside_data.errors import InvalidDate, InvalidPlayerAndSeason, InvalidSearch
from courtside_data.output.columns import (
    BOX_SCORE_COLUMN_NAMES,
    PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    SCHEDULE_COLUMN_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
)
from courtside_data.schemas import boxscores, playbyplay, players, schedule, search

_PLAYER_BOX_SCORES_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_daily_leaders",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the Basketball Reference daily player leaders page without following redirects.",
            inputs=("day", "month", "year"),
            outputs=("daily_leaders_response",),
        ),
        WorkflowStep(
            id="select_stats_table",
            kind=WorkflowStepKind.SELECT,
            description="Select table#stats and fail the date lookup when the table is missing.",
            inputs=("daily_leaders_response",),
            outputs=("stats_table",),
        ),
        WorkflowStep(
            id="parse_player_box_scores",
            kind=WorkflowStepKind.PARSE,
            description="Parse each player leader row and require at least one parsed row.",
            inputs=("stats_table",),
            outputs=("rows", "parser_stats"),
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics for table selection, parsed rows, and ignored rows.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_TEAM_BOX_SCORES_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_daily_index",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the daily box-score index for the requested date.",
            inputs=("day", "month", "year"),
            outputs=("daily_index",),
        ),
        WorkflowStep(
            id="select_game_links",
            kind=WorkflowStepKind.SELECT,
            description="Collect every td.gamelink anchor from the daily index.",
            inputs=("daily_index",),
            outputs=("game_url_paths",),
        ),
        WorkflowStep(
            id="require_game_links",
            kind=WorkflowStepKind.VALIDATE,
            description="Fail the date lookup when the daily index has no game links.",
            inputs=("game_url_paths",),
        ),
        WorkflowStep(
            id="fetch_and_parse_each_game",
            kind=WorkflowStepKind.FANOUT,
            description="Fetch each linked game box-score page and parse its team total rows.",
            inputs=("game_url_paths",),
            outputs=("game_rows", "game_stats"),
        ),
        WorkflowStep(
            id="merge_rows",
            kind=WorkflowStepKind.MERGE,
            description="Append rows from every game.",
            inputs=("game_rows",),
            outputs=("rows",),
        ),
        WorkflowStep(
            id="merge_parser_stats",
            kind=WorkflowStepKind.MERGE,
            description="Merge parser statistics across pages.",
            inputs=("game_stats",),
            outputs=("parser_stats",),
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record aggregate parser diagnostics for the daily fanout.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_PLAY_BY_PLAY_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_daily_index",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the daily box-score index for the requested date.",
            inputs=("home_team", "day", "month", "year"),
            outputs=("daily_index",),
        ),
        WorkflowStep(
            id="resolve_game_link",
            kind=WorkflowStepKind.SELECT,
            description="Resolve the play-by-play game path for the requested home team.",
            inputs=("daily_index", "home_team"),
            outputs=("game_url_path",),
        ),
        WorkflowStep(
            id="fetch_play_by_play",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the selected per-game play-by-play page.",
            inputs=("game_url_path",),
            outputs=("play_by_play_page",),
        ),
        WorkflowStep(
            id="resolve_team_labels",
            kind=WorkflowStepKind.DERIVE,
            description="Read the scorebox team names and convert them to away/home abbreviations.",
            inputs=("play_by_play_page",),
            outputs=("away_team", "home_team_abbreviation"),
        ),
        WorkflowStep(
            id="parse_play_by_play",
            kind=WorkflowStepKind.PARSE,
            description="Parse scoring, substitution, period, and possession events from table#pbp.",
            inputs=("play_by_play_page", "away_team", "home_team_abbreviation"),
            outputs=("rows", "parser_stats"),
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics for parsed and ignored play-by-play events.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_REGULAR_SEASON_PLAYER_BOX_SCORES_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_player_gamelog",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the player's season game-log page.",
            inputs=("player_identifier", "season_end_year"),
            outputs=("gamelog_page",),
        ),
        WorkflowStep(
            id="select_regular_season_table",
            kind=WorkflowStepKind.SELECT,
            description="Select table#player_game_log_reg and fail the player-season lookup when it is missing.",
            inputs=("gamelog_page",),
            outputs=("game_log_table",),
        ),
        WorkflowStep(
            id="parse_player_game_log",
            kind=WorkflowStepKind.PARSE,
            description="Parse regular-season game rows, optionally retaining inactive games.",
            inputs=("game_log_table", "include_inactive_games"),
            outputs=("rows", "parser_stats"),
            parser_id="player_game_log_table",
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics for the selected regular-season game-log table.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_PLAYOFF_PLAYER_BOX_SCORES_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_player_gamelog",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the player's season game-log page.",
            inputs=("player_identifier", "season_end_year"),
            outputs=("gamelog_page",),
        ),
        WorkflowStep(
            id="select_playoff_table",
            kind=WorkflowStepKind.SELECT,
            description="Select table#player_game_log_post and fail the player-season lookup when it is missing.",
            inputs=("gamelog_page",),
            outputs=("game_log_table",),
        ),
        WorkflowStep(
            id="parse_player_game_log",
            kind=WorkflowStepKind.PARSE,
            description="Parse playoff game rows, optionally retaining inactive games.",
            inputs=("game_log_table", "include_inactive_games"),
            outputs=("rows", "parser_stats"),
            parser_id="player_game_log_table",
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics for the selected playoff game-log table.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_SEASON_SCHEDULE_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_season_index",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the season schedule index page.",
            inputs=("season_end_year",),
            outputs=("season_index",),
        ),
        WorkflowStep(
            id="parse_inline_month",
            kind=WorkflowStepKind.PARSE,
            description="Parse schedule rows from the inline current-month table.",
            inputs=("season_index",),
            outputs=("inline_rows", "inline_stats"),
        ),
        WorkflowStep(
            id="select_month_links",
            kind=WorkflowStepKind.SELECT,
            description="Collect links for non-current month schedule pages.",
            inputs=("season_index",),
            outputs=("month_url_paths",),
        ),
        WorkflowStep(
            id="fetch_months",
            kind=WorkflowStepKind.FETCH,
            description="Fetch each linked month schedule page.",
            inputs=("month_url_paths",),
            outputs=("month_pages",),
        ),
        WorkflowStep(
            id="parse_months",
            kind=WorkflowStepKind.PARSE,
            description="Parse schedule rows and statistics from each fetched month page.",
            inputs=("month_pages",),
            outputs=("month_rows", "month_stats"),
        ),
        WorkflowStep(
            id="merge_rows",
            kind=WorkflowStepKind.MERGE,
            description="Append inline and fetched month rows while merging schedule diagnostics.",
            inputs=("inline_rows", "inline_stats", "month_rows", "month_stats"),
            outputs=("rows", "parser_stats"),
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record aggregate parser diagnostics for the season schedule.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_PLAYERS_SEASON_TOTALS_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_totals_page",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the league-wide player totals page for the season.",
            inputs=("season_end_year",),
            outputs=("totals_page",),
        ),
        WorkflowStep(
            id="select_totals_table",
            kind=WorkflowStepKind.SELECT,
            description="Select table#totals_stats.",
            inputs=("totals_page",),
            outputs=("totals_table",),
        ),
        WorkflowStep(
            id="parse_player_totals",
            kind=WorkflowStepKind.PARSE,
            description="Parse player totals rows while dropping combined-team rows.",
            inputs=("totals_table",),
            outputs=("rows", "parser_stats"),
            parser_id="player_totals_page",
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics for the selected totals table.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_PLAYERS_ADVANCED_SEASON_TOTALS_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_advanced_page",
            kind=WorkflowStepKind.FETCH,
            description="Fetch the league-wide advanced player totals page for the season.",
            inputs=("season_end_year",),
            outputs=("advanced_page",),
        ),
        WorkflowStep(
            id="select_advanced_table",
            kind=WorkflowStepKind.SELECT,
            description="Select table#advanced.",
            inputs=("advanced_page",),
            outputs=("advanced_table",),
        ),
        WorkflowStep(
            id="parse_advanced_totals",
            kind=WorkflowStepKind.PARSE,
            description="Parse advanced player totals rows, optionally retaining combined-team values.",
            inputs=("advanced_table", "include_combined_values"),
            outputs=("rows", "parser_stats"),
            parser_id="player_totals_page",
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record parser diagnostics for the selected advanced totals table.",
            inputs=("rows", "parser_stats"),
        ),
    ),
)

_SEARCH_WORKFLOW = WorkflowSpec(
    steps=(
        WorkflowStep(
            id="fetch_search",
            kind=WorkflowStepKind.FETCH,
            description="Fetch Basketball Reference search results for the requested term.",
            inputs=("term",),
            outputs=("search_response",),
        ),
        WorkflowStep(
            id="branch_redirect_or_results",
            kind=WorkflowStepKind.BRANCH,
            description="Choose the search-index parser or direct-player parser based on the final response URL.",
            inputs=("search_response",),
            outputs=("result_source", "first_page_rows", "pagination_url"),
        ),
        WorkflowStep(
            id="paginate_results",
            kind=WorkflowStepKind.FETCH,
            description="Follow Next 100 pagination links with a cycle guard and merge page results.",
            inputs=("pagination_url",),
            outputs=("paginated_rows", "parser_stats"),
        ),
        WorkflowStep(
            id="parse_search_results",
            kind=WorkflowStepKind.PARSE,
            description="Return the stable players result wrapper for either branch.",
            inputs=("first_page_rows", "paginated_rows", "parser_stats"),
            outputs=("players",),
        ),
        WorkflowStep(
            id="emit_diagnostics",
            kind=WorkflowStepKind.DIAGNOSTICS,
            description="Record search diagnostics including source branch, counts, and ignored results.",
            inputs=("players", "parser_stats", "result_source"),
        ),
    ),
    result="players",
)

WORKFLOW_ENDPOINTS = {
    "player_box_scores": _endpoint(
        "/friv/dailyleaders.cgi?month={month}&day={day}&year={year}",
        params=("day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        row_model=boxscores.PlayerBoxScoreRow,
        csv_columns=BOX_SCORE_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.REQUIRES_NON_EMPTY, EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_PLAYER_BOX_SCORES_WORKFLOW,
    ),
    "team_box_scores": _endpoint(
        "/boxscores/?month={month}&day={day}&year={year}",
        params=("day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        row_model=boxscores.TeamBoxScoreRow,
        csv_columns=TEAM_BOX_SCORES_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE,
            request_shape=RequestShape.MULTI_REQUEST,
            parser_shape=ParserShape.MULTI_TABLE,
            features=frozenset(
                {
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.AGGREGATES_ROWS,
                    EndpointFeature.WORKFLOW_DIAGNOSTICS,
                }
            ),
        ),
        workflow=_TEAM_BOX_SCORES_WORKFLOW,
    ),
    "play_by_play": _endpoint(
        "/boxscores/pbp/",
        params=("home_team", "day", "month", "year"),
        error=InvalidDate,
        error_params=("day", "month", "year"),
        row_model=playbyplay.PlayByPlayRow,
        csv_columns=PLAY_BY_PLAY_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.DATE_TEAM,
            request_shape=RequestShape.MULTI_REQUEST,
            parser_shape=ParserShape.PLAY_BY_PLAY,
            features=frozenset(
                {
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.ENUM_PARAM_COERCION,
                    EndpointFeature.DERIVED_FIELDS,
                    EndpointFeature.WORKFLOW_DIAGNOSTICS,
                }
            ),
        ),
        workflow=_PLAY_BY_PLAY_WORKFLOW,
    ),
    "regular_season_player_box_scores": _endpoint(
        "/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}",
        params=("player_identifier", "season_end_year", "include_inactive_games"),
        error=InvalidPlayerAndSeason,
        error_params=("player_identifier", "season_end_year"),
        error_status_codes=NOT_FOUND_OR_SERVER_ERROR,
        row_model=boxscores.RegularSeasonPlayerBoxScoreRow,
        csv_columns=PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.PLAYER_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_REGULAR_SEASON_PLAYER_BOX_SCORES_WORKFLOW,
    ),
    "playoff_player_box_scores": _endpoint(
        "/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}",
        params=("player_identifier", "season_end_year", "include_inactive_games"),
        error=InvalidPlayerAndSeason,
        error_params=("player_identifier", "season_end_year"),
        error_status_codes=NOT_FOUND_OR_SERVER_ERROR,
        row_model=boxscores.PlayoffPlayerBoxScoreRow,
        csv_columns=PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.PLAYER_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_PLAYOFF_PLAYER_BOX_SCORES_WORKFLOW,
    ),
    "season_schedule": _season(
        "/leagues/NBA_{season_end_year}_games.html",
        row_model=schedule.SeasonScheduleRow,
        csv_columns=SCHEDULE_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.MULTI_REQUEST,
            parser_shape=ParserShape.MULTI_TABLE,
            features=frozenset(
                {
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.AGGREGATES_ROWS,
                    EndpointFeature.WORKFLOW_DIAGNOSTICS,
                }
            ),
        ),
        workflow=_SEASON_SCHEDULE_WORKFLOW,
    ),
    "players_season_totals": _season(
        "/leagues/NBA_{season_end_year}_totals.html",
        row_model=players.PlayerSeasonTotalsRow,
        csv_columns=PLAYER_SEASON_TOTALS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_PLAYERS_SEASON_TOTALS_WORKFLOW,
    ),
    "players_advanced_season_totals": _season(
        "/leagues/NBA_{season_end_year}_advanced.html",
        params=("season_end_year", "include_combined_values"),
        row_model=players.PlayerAdvancedSeasonTotalsRow,
        csv_columns=PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.DERIVED_FIELDS, EndpointFeature.WORKFLOW_DIAGNOSTICS}),
        ),
        workflow=_PLAYERS_ADVANCED_SEASON_TOTALS_WORKFLOW,
    ),
    # csv_columns omitted - auto-detected from data so empty columns are stripped.
    "search": _endpoint(
        "/search/search.fcgi?search={term}",
        params=("term",),
        error=InvalidSearch,
        error_params=("term",),
        row_model=search.SearchResultRow,
        metadata=EndpointMetadata(
            domain=EndpointDomain.GAMES,
            kind=EndpointKind.WORKFLOW,
            scope=EndpointScope.SEARCH,
            request_shape=RequestShape.PAGINATED,
            parser_shape=ParserShape.SEARCH_RESULTS,
            features=frozenset(
                {
                    EndpointFeature.PAGINATED,
                    EndpointFeature.REDIRECTS,
                    EndpointFeature.FANOUT_LINKS,
                    EndpointFeature.WORKFLOW_DIAGNOSTICS,
                }
            ),
        ),
        workflow=_SEARCH_WORKFLOW,
    ),
}
