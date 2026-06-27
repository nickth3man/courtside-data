"""Parse workflow steps."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any, cast

from courtside_data._frozen import frozen_slot
from courtside_data.parsing import rows
from courtside_data.parsing.tables import GenericTable
from courtside_data.parsing.workflow_parsers._common import ExtractResult, _schedule_rows_with_stats
from courtside_data.parsing.workflows._parser_registry import PARSER_REGISTRY
from courtside_data.parsing.workflows._steps._common import _invalid_date_from_context
from courtside_data.parsing.workflows._steps._select import ForEachUrlPathStep

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext


@frozen_slot
class ParsePlayerGameLogStep:
    """Parse the selected player game-log table through the parser registry."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        result = cast(
            ExtractResult,
            PARSER_REGISTRY["player_game_log_table"](
                context.scratch["game_log_table"],
                include_inactive_games=context.params.get("include_inactive_games", False),
            ),
        )
        context.scratch["rows"] = result.rows
        context.scratch["parser_stats"] = result.stats


@frozen_slot
class ParsePlayerTotalsStep:
    """Parse a league-wide player totals page through the parser registry."""

    table_id: str
    include_combined_param: str | None = None

    def execute(self, context: WorkflowExecutionContext) -> None:
        include_combined = False
        if self.include_combined_param is not None:
            include_combined = bool(context.params.get(self.include_combined_param, False))
        result = cast(
            ExtractResult,
            PARSER_REGISTRY["player_totals_page"](
                context.scratch["totals_page"],
                table_id=self.table_id,
                include_combined=include_combined,
            ),
        )
        context.scratch["rows"] = result.rows
        context.scratch["parser_stats"] = result.stats
        context.scratch["table_id"] = self.table_id


@frozen_slot
class ParseOptionalTableRowsStep:
    """Parse selected table rows, returning an empty list when the table is missing."""

    table_var: str
    parser_id: str

    def execute(self, context: WorkflowExecutionContext) -> None:
        table = context.scratch[self.table_var]
        context.scratch["rows"] = [] if table is None else PARSER_REGISTRY[self.parser_id](table)


@frozen_slot
class ParseInlineScheduleMonthStep:
    """Parse rows and parser statistics from the inline schedule table."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        result = _schedule_rows_with_stats(context.scratch["season_index"])
        context.scratch["inline_rows"] = result.rows
        context.scratch["inline_stats"] = result.stats


@frozen_slot
class ParseScheduleMonthsStep:
    """Parse rows and parser statistics from fetched month pages."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        month_rows = []
        month_stats = []
        for selector in context.scratch["month_pages"]:
            result = _schedule_rows_with_stats(selector)
            month_rows.append(result.rows)
            month_stats.append(result.stats)
        context.scratch["month_rows"] = month_rows
        context.scratch["month_stats"] = month_stats


@frozen_slot
class ParsePlayerBoxScoresStep:
    """Parse the daily-leaders table, requiring at least one player row."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_player_box_scores_from_table_with_stats(context.scratch["stats_table"])
        if not parsed_rows:
            raise _invalid_date_from_context(context)
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseBoxScorePlayerBasicStep:
    """Parse per-player basic rows from a single game box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_player_basic_with_stats(context.scratch["box_score_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseBoxScorePlayerAdvancedStep:
    """Parse per-player advanced rows from a single game box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_player_advanced_with_stats(context.scratch["box_score_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseBoxScoreGameInfoStep:
    """Parse game-level metadata from a single box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_game_info_with_stats(context.scratch["box_score_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseBoxScoreLineScoreStep:
    """Parse team line-score rows from a single game box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_line_score_with_stats(context.scratch["box_score_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseBoxScorePlayerQuarterSplitsStep:
    """Parse per-player period split rows from a single game box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_player_quarter_splits_with_stats(
            context.scratch["box_score_page"],
            period=str(context.params["period"]),
        )
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseBoxScoreTeamFourFactorsStep:
    """Parse per-team Four Factors rows from a single game box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_team_four_factors_with_stats(context.scratch["box_score_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParsePlayByPlayStep:
    """Parse scoring, substitution, period, and possession events from ``table#pbp``."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_play_by_play_rows_with_stats(
            context.scratch["play_by_play_page"],
            context.scratch["away_team"],
            context.scratch["home_team_abbreviation"],
        )
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseStandingsBlocksStep:
    """Parse Eastern and Western conference standings sections."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_standings_with_stats(context.scratch["league_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@frozen_slot
class ParseStandingsConferenceTablesStep:
    """Parse ``table#standings_by_date`` rows from each conference page.

    A conference whose table is absent is counted under ``missing_table``
    and contributes no rows; present tables contribute their
    :class:`GenericTable` rows tagged with the conference label downstream.
    """

    def execute(self, context: WorkflowExecutionContext) -> None:
        table_id = context.endpoint.table_id
        conference_rows: list[tuple[str, list[dict[str, Any]]]] = []
        source_sections: list[str] = []
        ignored_row_reason_counts: Counter[str] = Counter()
        conference_names: set[str] = set()
        for (_, conference_name), selector in zip(
            context.scratch["conference_specs"],
            context.scratch["conference_pages"],
            strict=True,
        ):
            table_selector = selector.css(f"table#{table_id}")
            if not table_selector:
                ignored_row_reason_counts["missing_table"] += 1
                continue
            source_sections.append(f"table#{table_id}")
            conference_names.add(conference_name)
            table = GenericTable(table_selector[0])
            conference_rows.append((conference_name, [row.to_dict() for row in table.rows]))
        context.scratch["conference_rows"] = conference_rows
        context.scratch["parser_stats"] = {
            "source_sections": source_sections,
            "ignored_row_reason_counts": ignored_row_reason_counts,
            "conference_names": conference_names,
        }


ParseEachTeamBoxScoreStep = ForEachUrlPathStep(
    paths_var="game_url_paths",
    rows_var="game_rows",
    stats_var="game_stats",
    parse=rows.parse_team_box_score_with_stats,
    urls_var="game_urls",
)
