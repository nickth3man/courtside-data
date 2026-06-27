"""Selection and iteration workflow steps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx
from parsel import Selector

from courtside_data._frozen import frozen_slot
from courtside_data.errors import InvalidPlayerAndSeason
from courtside_data.parsing.generic import find_table
from courtside_data.parsing.workflows._steps._common import SCHEDULE_MONTH_LINK_SELECTOR, _invalid_date_from_context

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext
    from courtside_data.parsing.workflows._steps._common import ErrorFactory, ParserWithStats


@frozen_slot
class SelectTableStep:
    """Select a table from a selector scratch value."""

    selector_var: str
    output_var: str
    table_id: str | None = None
    table_id_var: str | None = None
    raise_invalid_player_and_season: bool = False

    def execute(self, context: WorkflowExecutionContext) -> None:
        table_id = self.table_id
        if self.table_id_var is not None:
            table_id = context.scratch[self.table_id_var]
        if table_id is None:
            table_id = context.endpoint.table_id
        if table_id is None:
            raise ValueError(f"Workflow step for {context.endpoint_name!r} has no table id.")

        table = find_table(context.scratch[self.selector_var], table_id)
        if table is None and self.raise_invalid_player_and_season:
            raise InvalidPlayerAndSeason(
                player_identifier=context.params["player_identifier"],
                season_end_year=context.params["season_end_year"],
            )
        context.scratch[self.output_var] = table
        context.scratch["table_id"] = table_id


@frozen_slot
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


@frozen_slot
class SelectScheduleMonthLinksStep:
    """Collect non-current month schedule links from the season index."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        selector = context.scratch["season_index"]
        context.scratch["month_url_paths"] = [
            link.attrib["href"] for link in selector.css(SCHEDULE_MONTH_LINK_SELECTOR)
        ]


@frozen_slot
class SelectDailyLeadersStatsTableStep:
    """Select ``table#stats`` from the daily-leaders response or fail the date.

    The friv page returns 200 with the leaders table for a played date;
    any non-OK status (e.g. an un-followed redirect) or a missing table
    means there were no daily leaders, which is an :class:`InvalidDate`.
    """

    def execute(self, context: WorkflowExecutionContext) -> None:
        response = context.scratch["daily_leaders_response"]
        if response.status_code != httpx.codes.OK:
            raise _invalid_date_from_context(context)
        table = find_table(Selector(text=response.text), "stats")
        if table is None:
            raise _invalid_date_from_context(context)
        context.scratch["stats_table"] = table


@frozen_slot
class RequireNonEmptyStep:
    """Raise a domain error when a scratch value is empty."""

    value_var: str
    error_factory: ErrorFactory

    def execute(self, context: WorkflowExecutionContext) -> None:
        if not context.scratch[self.value_var]:
            raise self.error_factory(context)


@frozen_slot
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


SelectGameLinksStep = SelectLinksStep(
    selector_var="daily_index",
    output_var="game_url_paths",
    css="td.gamelink a",
    attr="href",
)
RequireGameLinksStep = RequireNonEmptyStep("game_url_paths", _invalid_date_from_context)
