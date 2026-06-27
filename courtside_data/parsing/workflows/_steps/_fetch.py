"""Fetch workflow steps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data._frozen import frozen_slot

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext


@frozen_slot
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


@frozen_slot
class FetchEndpointPathStep:
    """Fetch the endpoint path template rendered with workflow params."""

    output_var: str
    url_var: str | None = None

    def execute(self, context: WorkflowExecutionContext) -> None:
        path = context.endpoint.path.format(**context.params)
        url = context.fetch.url(path)
        if self.url_var is not None:
            context.scratch[self.url_var] = url
        context.scratch[self.output_var] = context.fetch.get_selector(url=url)


@frozen_slot
class FetchResponseStep:
    """Fetch a raw ``httpx.Response`` from a path template with redirect control.

    Unlike the selector-returning fetch steps, this preserves the raw
    response so a downstream step can branch on the status code or the
    final (post-redirect) URL. ``follow_redirects=None`` leaves the
    transport default in place; pass ``False`` to keep a 3xx as-is.
    """

    path_template: str
    output_var: str
    follow_redirects: bool | None = None
    raise_for_status: bool = True

    def execute(self, context: WorkflowExecutionContext) -> None:
        url = context.fetch.url(self.path_template.format(**context.params))
        kwargs: dict[str, Any] = {}
        if self.follow_redirects is not None:
            kwargs["follow_redirects"] = self.follow_redirects
        response = context.fetch.get(url=url, **kwargs)
        if self.raise_for_status:
            response.raise_for_status()
        context.scratch[self.output_var] = response


@frozen_slot
class NormalizeAwardIdStep:
    """Normalize an award parameter into the Basketball Reference table id."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        context.scratch["table_id"] = str(context.params["award"]).strip().lower().replace("-", "_")


@frozen_slot
class FetchSeasonScheduleIndexStep:
    """Build and fetch the season schedule index page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        season_end_year = context.params["season_end_year"]
        url = context.fetch.url(f"/leagues/NBA_{season_end_year}_games.html")
        context.scratch["season_index_url"] = url
        context.scratch["season_index"] = context.fetch.get_selector(url=url)


@frozen_slot
class FetchScheduleMonthsStep:
    """Fetch every linked month schedule page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        month_urls = [context.fetch.url(path) for path in context.scratch["month_url_paths"]]
        context.scratch["month_urls"] = month_urls
        context.scratch["month_pages"] = [context.fetch.get_selector(url=url) for url in month_urls]


@frozen_slot
class FetchPlayByPlayPageStep:
    """Fetch the per-game play-by-play page for the resolved game path."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        game_url_path = context.scratch["game_url_path"]
        url = context.fetch.url(f"/boxscores/pbp/{game_url_path.split('/')[-1]}")
        context.scratch["play_by_play_url"] = url
        context.scratch["play_by_play_page"] = context.fetch.get_selector(url=url)


@frozen_slot
class FetchStandingsConferencePagesStep:
    """Fetch one standings-by-date page per conference."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        context.scratch["conference_pages"] = [
            context.fetch.get_selector(url=url) for url in context.scratch["conference_urls"]
        ]


@frozen_slot
class FetchSearchResponseStep:
    """Fetch Basketball Reference search results for the requested term."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        response = context.fetch.get(
            url=context.fetch.url("/search/search.fcgi"),
            params={"search": context.params["term"]},
        )
        response.raise_for_status()
        context.scratch["search_response"] = response


FetchDailyBoxScoresIndexStep = FetchPathTemplateStep(
    "/boxscores/?day={day}&month={month}&year={year}",
    output_var="daily_index",
    url_var="daily_index_url",
)
