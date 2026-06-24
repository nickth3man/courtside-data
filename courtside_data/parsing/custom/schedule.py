"""Schedule endpoints (``season_schedule``, ``schedule_for_month``).

The season-schedule page (``/leagues/NBA_{year}_games.html``) is a
month-tabbed view: the "current" month's table is inline, and the other
months are sibling links in ``div#content div.filter
div:not([class*="current"]) a``. The handler reads the current month
first, then iterates every other month link and reads its page in
turn, accumulating the rows.

The per-month endpoint is exposed publicly (``schedule_for_month``) so
the runner can dispatch it when only a single month's page is wanted
(the generic registry path is also available via
:func:`courtside_data.parsing.generic.GenericEndpointHandler.fetch_table`).
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any

from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.parsing.custom._common import _schedule_rows_with_stats

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = ["schedule_for_month", "season_schedule"]


def _merge_schedule_stats(aggregate: dict[str, Any], page_stats: dict[str, Any]) -> None:
    aggregate["game_count"] = aggregate.get("game_count", 0) + page_stats.get("game_count", 0)
    aggregate["postponed_game_count"] = aggregate.get("postponed_game_count", 0) + page_stats.get(
        "postponed_game_count", 0
    )
    aggregate["box_score_link_count"] = aggregate.get("box_score_link_count", 0) + page_stats.get(
        "box_score_link_count", 0
    )
    aggregate["missing_box_score_link_count"] = aggregate.get("missing_box_score_link_count", 0) + page_stats.get(
        "missing_box_score_link_count", 0
    )
    aggregate["candidate_row_count"] = aggregate.get("candidate_row_count", 0) + page_stats.get(
        "candidate_row_count", 0
    )
    ignored = aggregate.setdefault("ignored_row_reason_counts", Counter())
    for reason, count in (page_stats.get("ignored_row_reason_counts") or {}).items():
        ignored[reason] += count


def _record_schedule_diagnostics(
    *,
    parser_name: str,
    parsed_rows: list[dict[str, Any]],
    stats: dict[str, Any],
    month_page_count: int,
) -> None:
    trace = current_debug_trace()
    if trace is None:
        return
    ignored = stats.get("ignored_row_reason_counts") or {}
    emit_parser_diagnostics(
        trace,
        parser_name=parser_name,
        rows=parsed_rows,
        source_sections=["table#schedule"],
        ignored_event_count=sum(ignored.values()) if isinstance(ignored, dict) else None,
        ignored_event_reason_counts=ignored if isinstance(ignored, dict) else None,
        ignored_row_reason_counts=ignored if isinstance(ignored, dict) else None,
        custom_diagnostics={
            "game_count": stats.get("game_count"),
            "postponed_game_count": stats.get("postponed_game_count"),
            "box_score_link_count": stats.get("box_score_link_count"),
            "missing_box_score_link_count": stats.get("missing_box_score_link_count"),
            "month_page_count": month_page_count,
            "candidate_row_count": stats.get("candidate_row_count"),
            "ignored_row_reason_counts": dict(ignored) if isinstance(ignored, dict) else {},
        },
    )
    trace.artifact(
        "schedule_diagnostics",
        {
            "ignored_row_reason_counts": dict(ignored) if isinstance(ignored, dict) else {},
            "game_count": stats.get("game_count"),
            "postponed_game_count": stats.get("postponed_game_count"),
            "missing_box_score_link_count": stats.get("missing_box_score_link_count"),
            "candidate_row_count": stats.get("candidate_row_count"),
            "month_page_count": month_page_count,
        },
    )


def schedule_for_month(facade: FetchFacade, url: str) -> list[dict[str, Any]]:
    """Return the schedule rows for one month page at absolute ``url``."""
    selector = facade.get_selector(url=url)
    parsed_rows, stats = _schedule_rows_with_stats(selector)
    _record_schedule_diagnostics(
        parser_name="schedule_for_month",
        parsed_rows=parsed_rows,
        stats=stats,
        month_page_count=1,
    )
    return parsed_rows


def season_schedule(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return the schedule rows for every month of ``season_end_year``.

    Reads the season index page (the inline current month is the first
    batch) and then walks the month links in ``div.filter`` to read the
    other months.
    """
    url = facade.url(f"/leagues/NBA_{season_end_year}_games.html")

    selector = facade.get_selector(url=url)
    season_schedule_values, first_stats = _schedule_rows_with_stats(selector)
    aggregate_stats: dict[str, Any] = {
        "game_count": 0,
        "postponed_game_count": 0,
        "box_score_link_count": 0,
        "missing_box_score_link_count": 0,
        "candidate_row_count": 0,
        "ignored_row_reason_counts": Counter(),
    }
    _merge_schedule_stats(aggregate_stats, first_stats)
    month_page_count = 1

    for month_url_path in [
        link.attrib["href"] for link in selector.css('div#content div.filter div:not([class*="current"]) a')
    ]:
        month_url = facade.url(month_url_path)
        month_selector = facade.get_selector(url=month_url)
        monthly_schedule, month_stats = _schedule_rows_with_stats(month_selector)
        season_schedule_values.extend(monthly_schedule)
        _merge_schedule_stats(aggregate_stats, month_stats)
        month_page_count += 1

    _record_schedule_diagnostics(
        parser_name="season_schedule",
        parsed_rows=season_schedule_values,
        stats=aggregate_stats,
        month_page_count=month_page_count,
    )
    return season_schedule_values
