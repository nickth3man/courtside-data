"""Executable workflow step implementations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx
from parsel import Selector

from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.domain import TEAM_TO_TEAM_ABBREVIATION
from courtside_data.errors import InvalidPlayerAndSeason
from courtside_data.parsing import cells, rows
from courtside_data.parsing.generic import find_table
from courtside_data.parsing.tables import GenericTable
from courtside_data.parsing.workflow_parsers._common import _schedule_rows_with_stats
from courtside_data.parsing.workflow_parsers._diagnostics import emit_workflow_endpoint_diagnostics
from courtside_data.parsing.workflow_parsers.boxscores import _merge_team_box_score_stats
from courtside_data.parsing.workflow_parsers.schedule import _merge_schedule_stats, _record_schedule_diagnostics
from courtside_data.parsing.workflow_parsers.search import _merge_search_stats
from courtside_data.parsing.workflow_parsers.standings import _record_standings_diagnostics
from courtside_data.parsing.workflows._parser_registry import PARSER_REGISTRY
from courtside_data.schemas._fields import _team_field

if TYPE_CHECKING:
    from courtside_data.parsing.workflows._context import WorkflowExecutionContext

    ErrorFactory = Callable[[WorkflowExecutionContext], Exception]
    ParserWithStats = Callable[[Selector], tuple[list[dict[str, Any]], dict[str, Any]]]
    StatsMerger = Callable[[dict[str, Any], dict[str, Any]], None]


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


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class NormalizeAwardIdStep:
    """Normalize an award parameter into the Basketball Reference table id."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        context.scratch["table_id"] = str(context.params["award"]).strip().lower().replace("-", "_")


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class ParsePlayerGameLogStep:
    """Parse the selected player game-log table through the parser registry."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parse = PARSER_REGISTRY["player_game_log_table"]
        rows, stats = parse(
            context.scratch["game_log_table"],
            include_inactive_games=context.params.get("include_inactive_games", False),
        )
        context.scratch["rows"] = rows
        context.scratch["parser_stats"] = stats


@dataclass(frozen=True, slots=True)
class ParsePlayerTotalsStep:
    """Parse a league-wide player totals page through the parser registry."""

    table_id: str
    include_combined_param: str | None = None

    def execute(self, context: WorkflowExecutionContext) -> None:
        include_combined = False
        if self.include_combined_param is not None:
            include_combined = bool(context.params.get(self.include_combined_param, False))
        parse = PARSER_REGISTRY["player_totals_page"]
        rows, stats = parse(
            context.scratch["totals_page"],
            table_id=self.table_id,
            include_combined=include_combined,
        )
        context.scratch["rows"] = rows
        context.scratch["parser_stats"] = stats
        context.scratch["table_id"] = self.table_id


@dataclass(frozen=True, slots=True)
class ParseOptionalTableRowsStep:
    """Parse selected table rows, returning an empty list when the table is missing."""

    table_var: str
    parser_id: str

    def execute(self, context: WorkflowExecutionContext) -> None:
        table = context.scratch[self.table_var]
        context.scratch["rows"] = [] if table is None else PARSER_REGISTRY[self.parser_id](table)


@dataclass(frozen=True, slots=True)
class EmitPlayerGameLogDiagnosticsStep:
    """Emit parser diagnostics for a player game-log workflow."""

    parser_name: str
    table_id: str

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        stats = {
            **context.scratch["parser_stats"],
            "season_count": 1,
            "selected_table_id": self.table_id,
        }
        emit_workflow_endpoint_diagnostics(
            parser_name=self.parser_name,
            endpoint_name=context.endpoint_name,
            rows=parsed_rows,
            source_sections=[f"table#{self.table_id}"],
            stats=stats,
            selected_table_id=self.table_id,
            candidate_table_ids=[self.table_id],
        )
        return parsed_rows


@dataclass(frozen=True, slots=True)
class EmitPlayerTotalsDiagnosticsStep:
    """Emit parser diagnostics for a league-wide player totals workflow."""

    parser_name: str
    table_id: str

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        emit_workflow_endpoint_diagnostics(
            parser_name=self.parser_name,
            endpoint_name=context.endpoint_name,
            rows=parsed_rows,
            source_sections=[f"table#{self.table_id}"],
            stats=context.scratch["parser_stats"],
            selected_table_id=self.table_id,
            candidate_table_ids=[self.table_id],
        )
        return parsed_rows


@dataclass(frozen=True, slots=True)
class EmitAwardVotingDiagnosticsStep:
    """Emit parser diagnostics for season award voting rows."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        table_id = context.scratch["table_id"]
        trace = current_debug_trace()
        if trace is not None and context.scratch["award_table"] is not None:
            emit_parser_diagnostics(
                trace,
                parser_name="season_awards_voting",
                rows=parsed_rows,
                source_sections=[f"table#{table_id}"],
                workflow_diagnostics={"award_table_id": table_id},
            )
        return parsed_rows


@dataclass(frozen=True, slots=True)
class EmitPlayoffBracketDiagnosticsStep:
    """Emit parser diagnostics for playoff bracket rows."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        trace = current_debug_trace()
        if trace is not None and context.scratch["bracket_table"] is not None:
            emit_parser_diagnostics(
                trace,
                parser_name="playoff_bracket",
                rows=parsed_rows,
                source_sections=["table#all_playoffs"],
                workflow_diagnostics={"series_count": len(parsed_rows)},
            )
        return parsed_rows


@dataclass(frozen=True, slots=True)
class EmitFrivOutcomesDiagnosticsStep:
    """Emit parser diagnostics and raw-row artifact for Friv outcome rows."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        table_id = context.scratch["table_id"]
        trace = current_debug_trace()
        if trace is not None and context.scratch["outcome_table"] is not None:
            trace.record("parse", "friv_playoff_outcomes_parsed", table_id=table_id, row_count=len(parsed_rows))
            trace.artifact("raw_rows", parsed_rows)
            emit_parser_diagnostics(
                trace,
                parser_name="friv_playoff_outcomes",
                rows=parsed_rows,
                source_sections=[f"table#{table_id}"],
                workflow_diagnostics={"table_id": table_id},
            )
        return parsed_rows


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
        emit_workflow_endpoint_diagnostics(
            parser_name="team_box_scores",
            endpoint_name="team_box_scores",
            rows=parsed_rows,
            source_sections=["td.gamelink a", 'table.stats_table[id$="-game-basic"]'],
            stats=context.scratch["parser_stats"],
        )
        return parsed_rows


# ── player_box_scores (daily leaders friv page) ─────────────────────────────


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class ParsePlayerBoxScoresStep:
    """Parse the daily-leaders table, requiring at least one player row."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_player_box_scores_from_table_with_stats(context.scratch["stats_table"])
        if not parsed_rows:
            raise _invalid_date_from_context(context)
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@dataclass(frozen=True, slots=True)
class ParseBoxScorePlayerBasicStep:
    """Parse per-player basic rows from a single game box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_player_basic_with_stats(context.scratch["box_score_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@dataclass(frozen=True, slots=True)
class ParseBoxScoreGameInfoStep:
    """Parse game-level metadata from a single box-score page."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_box_score_game_info_with_stats(context.scratch["box_score_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@dataclass(frozen=True, slots=True)
class EmitPlayerBoxScoresDiagnosticsStep:
    """Emit parser diagnostics for the daily-leaders table."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        emit_workflow_endpoint_diagnostics(
            parser_name="player_box_scores",
            endpoint_name="player_box_scores",
            rows=parsed_rows,
            source_sections=["table#stats"],
            stats=context.scratch["parser_stats"],
            selected_table_id="stats",
        )
        return parsed_rows


@dataclass(frozen=True, slots=True)
class EmitBoxScoreDiagnosticsStep:
    """Emit diagnostics for single-game box-score page readers."""

    parser_name: str
    source_sections: tuple[str, ...]

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        emit_workflow_endpoint_diagnostics(
            parser_name=self.parser_name,
            endpoint_name=context.endpoint_name,
            rows=parsed_rows,
            source_sections=self.source_sections,
            stats=context.scratch["parser_stats"],
        )
        return parsed_rows


# ── play_by_play (daily index → per-game pbp page) ──────────────────────────


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class FetchPlayByPlayPageStep:
    """Fetch the per-game play-by-play page for the resolved game path."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        game_url_path = context.scratch["game_url_path"]
        url = context.fetch.url(f"/boxscores/pbp/{game_url_path.split('/')[-1]}")
        context.scratch["play_by_play_url"] = url
        context.scratch["play_by_play_page"] = context.fetch.get_selector(url=url)


@dataclass(frozen=True, slots=True)
class ResolvePlayByPlayTeamLabelsStep:
    """Read the scorebox team names and convert them to away/home abbreviations."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        selector = context.scratch["play_by_play_page"]
        team_names = [cells.cell_text(team_name) for team_name in selector.css("#content div.scorebox strong a")]
        context.scratch["away_team"] = cells.team_abbreviation_from_name(team_names[0])
        context.scratch["home_team_abbreviation"] = cells.team_abbreviation_from_name(team_names[1])


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class EmitPlayByPlayDiagnosticsStep:
    """Emit parser diagnostics for parsed and ignored play-by-play events."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        stats = context.scratch["parser_stats"]
        trace = current_debug_trace()
        if trace is not None:
            emit_parser_diagnostics(
                trace,
                parser_name="play_by_play",
                rows=parsed_rows,
                source_sections=["table#pbp"],
                parsed_event_count=stats["parsed_event_count"],
                ignored_event_count=stats["ignored_event_count"],
                ignored_event_reason_counts=stats["ignored_event_reason_counts"],
                period_count=stats["period_count"],
                score_event_count=stats["score_event_count"],
                substitution_event_count=stats["substitution_event_count"],
            )
        return parsed_rows


# ── standings (single league page, both conference blocks) ──────────────────


@dataclass(frozen=True, slots=True)
class ParseStandingsBlocksStep:
    """Parse Eastern and Western conference standings sections."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        parsed_rows, stats = rows.parse_standings_with_stats(context.scratch["league_page"])
        context.scratch["rows"] = parsed_rows
        context.scratch["parser_stats"] = stats


@dataclass(frozen=True, slots=True)
class EmitStandingsDiagnosticsStep:
    """Emit parser diagnostics for conference, division, and team counts."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        parsed_rows = context.scratch["rows"]
        _record_standings_diagnostics(
            parser_name="standings",
            parsed_rows=parsed_rows,
            source_sections=["table#divs_standings_E", "table#divs_standings_W"],
            stats=context.scratch["parser_stats"],
        )
        return parsed_rows


# ── standings_by_date (one page per conference) ─────────────────────────────


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class FetchStandingsConferencePagesStep:
    """Fetch one standings-by-date page per conference."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        context.scratch["conference_pages"] = [
            context.fetch.get_selector(url=url) for url in context.scratch["conference_urls"]
        ]


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class AttachStandingsConferenceStep:
    """Attach the human conference label to each parsed standings row."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        standings_rows: list[dict[str, Any]] = []
        for conference_name, raw_rows in context.scratch["conference_rows"]:
            for row in raw_rows:
                standings_rows.append({"conference": conference_name, **row})
        context.scratch["rows"] = standings_rows


@dataclass(frozen=True, slots=True)
class EmitStandingsByDateDiagnosticsStep:
    """Emit parser diagnostics for fetched sections and parsed teams."""

    def execute(self, context: WorkflowExecutionContext) -> list[dict[str, Any]]:
        standings_rows = context.scratch["rows"]
        stats = context.scratch["parser_stats"]
        trace = current_debug_trace()
        if trace is not None:
            emit_parser_diagnostics(
                trace,
                parser_name="standings_by_date",
                rows=standings_rows,
                source_sections=stats["source_sections"],
                ignored_row_reason_counts=dict(stats["ignored_row_reason_counts"]),
                workflow_diagnostics={
                    "conference_count": len(stats["conference_names"]),
                    "team_count": len(standings_rows),
                    "standings_section_count": len(stats["source_sections"]),
                },
            )
        return standings_rows


# ── search (index pagination cycle or player redirect) ──────────────────────


@dataclass(frozen=True, slots=True)
class FetchSearchResponseStep:
    """Fetch Basketball Reference search results for the requested term."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        response = context.fetch.get(
            url=context.fetch.url("/search/search.fcgi"),
            params={"search": context.params["term"]},
        )
        response.raise_for_status()
        context.scratch["search_response"] = response


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class PaginateSearchResultsStep:
    """Follow ``Next 100`` pagination links with a cycle guard, merging each page."""

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


@dataclass(frozen=True, slots=True)
class BuildSearchResultStep:
    """Wrap the accumulated player rows in the stable ``{"players": [...]}`` result."""

    def execute(self, context: WorkflowExecutionContext) -> None:
        player_results = context.scratch["search_player_results"]
        context.scratch["search_aggregate_stats"]["result_count"] = len(player_results)
        context.scratch["players"] = {"players": player_results}


@dataclass(frozen=True, slots=True)
class EmitSearchDiagnosticsStep:
    """Emit search diagnostics including source branch, counts, and ignored results."""

    def execute(self, context: WorkflowExecutionContext) -> dict[str, list[dict[str, Any]]]:
        player_results = context.scratch["search_player_results"]
        aggregate_stats = context.scratch["search_aggregate_stats"]
        ignored = aggregate_stats["ignored_result_reason_counts"]
        trace = current_debug_trace()
        if trace is not None:
            emit_parser_diagnostics(
                trace,
                parser_name="search",
                rows=player_results,
                source_sections=context.scratch["search_source_sections"],
                ignored_event_count=sum(ignored.values()) if ignored else None,
                ignored_event_reason_counts=dict(ignored) if ignored else None,
                workflow_diagnostics={
                    "query": aggregate_stats["query"],
                    "result_count": len(player_results),
                    "candidate_count": aggregate_stats.get("candidate_count"),
                    "matched_result_count": aggregate_stats.get("matched_result_count"),
                    "ignored_result_reason_counts": dict(ignored) if ignored else {},
                    "result_source": aggregate_stats.get("result_source"),
                },
            )
        return context.scratch["players"]


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
