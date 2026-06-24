"""Executable workflow step implementations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from courtside_data.parsing import rows
from courtside_data.parsing.custom import dispatch_custom_endpoint
from courtside_data.parsing.custom._common import _schedule_rows_with_stats
from courtside_data.parsing.custom._diagnostics import emit_custom_endpoint_diagnostics
from courtside_data.parsing.custom.boxscores import _merge_team_box_score_stats
from courtside_data.parsing.custom.schedule import _merge_schedule_stats, _record_schedule_diagnostics

if TYPE_CHECKING:
    from parsel import Selector

    from courtside_data.parsing.workflows._context import WorkflowExecutionContext

    ErrorFactory = Callable[[WorkflowExecutionContext], Exception]
    ParserWithStats = Callable[[Selector], tuple[list[dict[str, Any]], dict[str, Any]]]
    StatsMerger = Callable[[dict[str, Any], dict[str, Any]], None]


@dataclass(frozen=True, slots=True)
class CallCustomHandlerStep:
    """Compatibility step that delegates to the legacy bespoke dispatcher."""

    def execute(self, context: WorkflowExecutionContext) -> Any:
        """Call ``dispatch_custom_endpoint`` and store the result in scratch."""
        result = dispatch_custom_endpoint(
            context.fetch._http,
            context.endpoint_name,
            **dict(context.params),
        )
        result_key = context.endpoint.workflow.result if context.endpoint.workflow is not None else "rows"
        context.scratch[result_key] = result
        return result


LegacyCustomHandlerStep = CallCustomHandlerStep


SCHEDULE_MONTH_LINK_SELECTOR = 'div#content div.filter div:not([class*="current"]) a'


@dataclass(frozen=True, slots=True)
class FetchPathTemplateStep:
    """Fetch a selector from a path template rendered with workflow params."""

    path_template: str
    output_var: str
    url_var: str | None = None

    def execute(self, context: WorkflowExecutionContext) -> None:
        path = self.path_template.format(**context.params)
        url = context.fetch.url(path)
        if self.url_var is not None:
            context.scratch[self.url_var] = url
        context.scratch[self.output_var] = context.fetch.get_selector(url=url)


@dataclass(frozen=True, slots=True)
class SelectLinksStep:
    """Collect attribute values from links in a selector scratch value."""

    selector_var: str
    output_var: str
    css: str
    attr: str

    def execute(self, context: WorkflowExecutionContext) -> None:
        selector = context.scratch[self.selector_var]
        context.scratch[self.output_var] = [
            str(link.attrib[self.attr]) for link in selector.css(self.css) if self.attr in link.attrib
        ]


@dataclass(frozen=True, slots=True)
class RequireNonEmptyStep:
    """Raise a domain error when a scratch value is empty."""

    value_var: str
    error_factory: ErrorFactory

    def execute(self, context: WorkflowExecutionContext) -> None:
        if not context.scratch[self.value_var]:
            raise self.error_factory(context)


@dataclass(frozen=True, slots=True)
class ForEachUrlPathStep:
    """Fetch each URL path, parse the selector, and store per-page results."""

    paths_var: str
    rows_var: str
    stats_var: str
    parse: ParserWithStats
    urls_var: str | None = None

    def execute(self, context: WorkflowExecutionContext) -> None:
        page_rows: list[list[dict[str, Any]]] = []
        page_stats: list[dict[str, Any]] = []
        urls: list[str] = []
        for path in context.scratch[self.paths_var]:
            url = context.fetch.url(path)
            urls.append(url)
            selector = context.fetch.get_selector(url=url)
            parsed_rows, stats = self.parse(selector)
            page_rows.append(parsed_rows)
            page_stats.append(stats)
        context.scratch[self.rows_var] = page_rows
        context.scratch[self.stats_var] = page_stats
        if self.urls_var is not None:
            context.scratch[self.urls_var] = urls


@dataclass(frozen=True, slots=True)
class MergeRowListsStep:
    """Flatten a scratch value containing row lists."""

    input_var: str
    output_var: str = "rows"

    def execute(self, context: WorkflowExecutionContext) -> None:
        merged: list[dict[str, Any]] = []
        for row_list in context.scratch[self.input_var]:
            merged.extend(row_list)
        context.scratch[self.output_var] = merged


@dataclass(frozen=True, slots=True)
class MergeParserStatsStep:
    """Merge per-page parser statistics into one aggregate mapping."""

    input_var: str
    output_var: str
    initial_stats: Callable[[], dict[str, Any]]
    merge: StatsMerger

    def execute(self, context: WorkflowExecutionContext) -> None:
        aggregate = self.initial_stats()
        for stats in context.scratch[self.input_var]:
            self.merge(aggregate, stats)
        context.scratch[self.output_var] = aggregate


def _invalid_date_from_context(context: WorkflowExecutionContext) -> Exception:
    from courtside_data.errors import InvalidDate

    return InvalidDate(
        day=context.params["day"],
        month=context.params["month"],
        year=context.params["year"],
    )


def _empty_team_box_score_stats() -> dict[str, Any]:
    return {
        "game_count": 0,
        "team_count": 0,
        "stat_table_count": 0,
        "basic_table_count": 0,
        "advanced_table_count": 0,
        "empty_table_count": 0,
        "ignored_row_reason_counts": Counter(),
    }


@dataclass(frozen=True, slots=True)
class FetchSeasonScheduleIndexStep:
    """Build and fetch the season schedule index page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        season_end_year = context.params["season_end_year"]
        url = context.fetch.url(f"/leagues/NBA_{season_end_year}_games.html")
        context.scratch["season_index_url"] = url
        context.scratch["season_index"] = context.fetch.get_selector(url=url)


@dataclass(frozen=True, slots=True)
class ParseInlineScheduleMonthStep:
    """Parse rows and parser statistics from the inline schedule table."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        rows, stats = _schedule_rows_with_stats(context.scratch["season_index"])
        context.scratch["inline_rows"] = rows
        context.scratch["inline_stats"] = stats


@dataclass(frozen=True, slots=True)
class SelectScheduleMonthLinksStep:
    """Collect non-current month schedule links from the season index."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        selector = context.scratch["season_index"]
        context.scratch["month_url_paths"] = [
            link.attrib["href"] for link in selector.css(SCHEDULE_MONTH_LINK_SELECTOR)
        ]


@dataclass(frozen=True, slots=True)
class FetchScheduleMonthsStep:
    """Fetch every linked month schedule page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        month_urls = [context.fetch.url(path) for path in context.scratch["month_url_paths"]]
        context.scratch["month_urls"] = month_urls
        context.scratch["month_pages"] = [context.fetch.get_selector(url=url) for url in month_urls]


@dataclass(frozen=True, slots=True)
class ParseScheduleMonthsStep:
    """Parse rows and parser statistics from fetched month pages."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        month_rows = []
        month_stats = []
        for selector in context.scratch["month_pages"]:
            rows, stats = _schedule_rows_with_stats(selector)
            month_rows.append(rows)
            month_stats.append(stats)
        context.scratch["month_rows"] = month_rows
        context.scratch["month_stats"] = month_stats


@dataclass(frozen=True, slots=True)
class MergeScheduleRowsStep:
    """Merge schedule rows and parser statistics across all month pages."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        rows = list(context.scratch["inline_rows"])
        aggregate_stats: dict[str, Any] = {
            "game_count": 0,
            "postponed_game_count": 0,
            "box_score_link_count": 0,
            "missing_box_score_link_count": 0,
            "candidate_row_count": 0,
            "ignored_row_reason_counts": Counter(),
        }
        _merge_schedule_stats(aggregate_stats, context.scratch["inline_stats"])
        month_page_count = 1

        for monthly_rows, stats in zip(
            context.scratch["month_rows"],
            context.scratch["month_stats"],
            strict=True,
        ):
            rows.extend(monthly_rows)
            _merge_schedule_stats(aggregate_stats, stats)
            month_page_count += 1

        context.scratch["rows"] = rows
        context.scratch["parser_stats"] = aggregate_stats
        context.scratch["month_page_count"] = month_page_count


@dataclass(frozen=True, slots=True)
class EmitScheduleDiagnosticsStep:
    """Emit aggregate schedule parser diagnostics."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        rows = context.scratch["rows"]
        _record_schedule_diagnostics(
            parser_name="season_schedule",
            parsed_rows=rows,
            stats=context.scratch["parser_stats"],
            month_page_count=context.scratch["month_page_count"],
        )
        return rows


@dataclass(frozen=True, slots=True)
class EmitTeamBoxScoresDiagnosticsStep:
    """Emit aggregate team box-score parser diagnostics."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        emit_custom_endpoint_diagnostics(
            parser_name="team_box_scores",
            endpoint_name="team_box_scores",
            rows=parsed_rows,
            source_sections=["td.gamelink a", 'table.stats_table[id$="-game-basic"]'],
            stats=context.scratch["parser_stats"],
        )
        return parsed_rows


FetchDailyBoxScoresIndexStep = FetchPathTemplateStep(
    "/boxscores/?day={day}&month={month}&year={year}",
    output_var="daily_index",
    url_var="daily_index_url",
)
SelectGameLinksStep = SelectLinksStep(
    selector_var="daily_index",
    output_var="game_url_paths",
    css="td.gamelink a",
    attr="href",
)
RequireGameLinksStep = RequireNonEmptyStep("game_url_paths", _invalid_date_from_context)
ParseEachTeamBoxScoreStep = ForEachUrlPathStep(
    paths_var="game_url_paths",
    rows_var="game_rows",
    stats_var="game_stats",
    parse=rows.parse_team_box_score_with_stats,
    urls_var="game_urls",
)
MergeTeamBoxScoreRowsStep = MergeRowListsStep(input_var="game_rows")
MergeTeamBoxScoreStatsStep = MergeParserStatsStep(
    input_var="game_stats",
    output_var="parser_stats",
    initial_stats=_empty_team_box_score_stats,
    merge=_merge_team_box_score_stats,
)
