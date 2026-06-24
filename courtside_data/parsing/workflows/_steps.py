"""Executable workflow step implementations."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from courtside_data.parsing.custom import dispatch_custom_endpoint
from courtside_data.parsing.custom._common import _schedule_rows_with_stats
from courtside_data.parsing.custom.schedule import _merge_schedule_stats, _record_schedule_diagnostics

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext


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
