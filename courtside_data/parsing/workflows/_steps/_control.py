"""Merge, branch, paginate, and resolution workflow steps."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from parsel import Selector

from courtside_data._frozen import frozen_slot
from courtside_data.domain import TEAM_TO_TEAM_ABBREVIATION
from courtside_data.parsing import cells, rows
from courtside_data.parsing.workflow_parsers._common import (
    _merge_schedule_stats,
    _merge_search_stats,
    _merge_team_box_score_stats,
)
from courtside_data.parsing.workflows._steps._common import _invalid_date_from_context
from courtside_data.schemas._fields import _team_field

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext
    from courtside_data.parsing.workflows._steps._common import StatsMerger


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


@frozen_slot
class MergeRowListsStep:
    """Flatten a scratch value containing row lists."""

    input_var: str
    output_var: str = "rows"

    def execute(self, context: WorkflowExecutionContext) -> None:
        merged: list[dict[str, Any]] = []
        for row_list in context.scratch[self.input_var]:
            merged.extend(row_list)
        context.scratch[self.output_var] = merged


@frozen_slot
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


@frozen_slot
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


@frozen_slot
class ResolvePlayByPlayGameLinkStep:
    """Resolve the per-game pbp path for the requested home team from the daily index."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        home_team = context.params["home_team"]
        if isinstance(home_team, str):
            home_team = _team_field(home_team)
        abbr = TEAM_TO_TEAM_ABBREVIATION[home_team]
        game_url_path = rows.resolve_pbp_game_url_path(context.scratch["daily_index"], abbr)
        if game_url_path is None:
            raise _invalid_date_from_context(context)
        context.scratch["game_url_path"] = game_url_path


@frozen_slot
class ResolvePlayByPlayTeamLabelsStep:
    """Read the scorebox team names and convert them to away/home abbreviations."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        selector = context.scratch["play_by_play_page"]
        team_names = [cells.cell_text(team_name) for team_name in selector.css("#content div.scorebox strong a")]
        context.scratch["away_team"] = cells.team_abbreviation_from_name(team_names[0])
        context.scratch["home_team_abbreviation"] = cells.team_abbreviation_from_name(team_names[1])


@frozen_slot
class ExpandStandingsConferencesStep:
    """Expand the internal conference template parameter into per-conference URLs."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        season_end_year = context.params["season_end_year"]
        conference_specs = [("eastern_conference", "Eastern"), ("western_conference", "Western")]
        context.scratch["conference_specs"] = conference_specs
        context.scratch["conference_urls"] = [
            context.fetch.url(context.endpoint.path.format(season_end_year=season_end_year, conference=conference))
            for conference, _ in conference_specs
        ]


@frozen_slot
class AttachStandingsConferenceStep:
    """Attach the human conference label to each parsed standings row."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        standings_rows: list[dict[str, Any]] = []
        for conference_name, raw_rows in context.scratch["conference_rows"]:
            for row in raw_rows:
                standings_rows.append({"conference": conference_name, **row})
        context.scratch["rows"] = standings_rows


@frozen_slot
class BranchSearchResultsStep:
    """Branch on the final response URL: search index, player redirect, or neither.

    The index branch parses the first results page and exposes the
    ``Next 100`` link for the pagination step; the redirect branch parses
    the single player page in place. State that both the pagination and
    diagnostics steps consume is staged under ``search_*`` scratch keys.
    """

    def execute(self, context: WorkflowExecutionContext) -> None:
        facade = context.fetch
        response = context.scratch["search_response"]
        player_results: list[dict[str, Any]] = []
        aggregate_stats: dict[str, Any] = {
            "query": context.params["term"],
            "candidate_count": 0,
            "matched_result_count": 0,
            "ignored_result_reason_counts": Counter(),
            "result_source": "unknown",
        }
        source_sections = ["div#searches div#players"]
        pagination_url: str | None = None

        if str(response.url).startswith(facade.url("/search/search.fcgi")):
            aggregate_stats["result_source"] = "search_index"
            selector = Selector(text=response.text)
            page_rows, page_stats = rows.parse_search_rows_with_stats(selector)
            player_results.extend(page_rows)
            _merge_search_stats(aggregate_stats, page_stats)
            pagination_url = rows.parse_search_pagination_url(selector)
        elif str(response.url).startswith(f"{facade.BASE_URL}/players"):
            aggregate_stats["result_source"] = "player_redirect"
            source_sections = ["h1[itemprop=name]", "table#per_game"]
            selector = Selector(text=response.text)
            player_results.extend(rows.parse_player_direct_search_results(selector, str(response.url)))
            aggregate_stats["candidate_count"] = 1
            aggregate_stats["matched_result_count"] = len(player_results)

        context.scratch["search_player_results"] = player_results
        context.scratch["search_aggregate_stats"] = aggregate_stats
        context.scratch["search_source_sections"] = source_sections
        context.scratch["search_pagination_url"] = pagination_url


@frozen_slot
class PaginateSearchResultsStep:
    """Follow ``Next 100`` pagination links with a repeat guard, merging each page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        facade = context.fetch
        player_results = context.scratch["search_player_results"]
        aggregate_stats = context.scratch["search_aggregate_stats"]
        seen_pagination_urls: set[str] = set()
        pagination_url = context.scratch["search_pagination_url"]
        while pagination_url is not None:
            if pagination_url in seen_pagination_urls:
                break
            seen_pagination_urls.add(pagination_url)

            response = facade.get(url=f"{facade.BASE_URL}/search/{pagination_url}")
            response.raise_for_status()

            selector = Selector(text=response.text)
            page_rows, page_stats = rows.parse_search_rows_with_stats(selector)
            player_results.extend(page_rows)
            _merge_search_stats(aggregate_stats, page_stats)
            pagination_url = rows.parse_search_pagination_url(selector)


@frozen_slot
class BuildSearchResultStep:
    """Wrap the accumulated player rows in the stable ``{"players": [...]}`` result."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        player_results = context.scratch["search_player_results"]
        context.scratch["search_aggregate_stats"]["result_count"] = len(player_results)
        context.scratch["players"] = {"players": player_results}


MergeTeamBoxScoreRowsStep = MergeRowListsStep(input_var="game_rows")
MergeTeamBoxScoreStatsStep = MergeParserStatsStep(
    input_var="game_stats",
    output_var="parser_stats",
    initial_stats=_empty_team_box_score_stats,
    merge=_merge_team_box_score_stats,
)
