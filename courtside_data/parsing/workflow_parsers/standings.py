"""League-wide standings endpoints (``standings``, ``standings_by_date``).

Both endpoints render the NBA's per-conference standings but at different
URLs and on different table shapes: ``standings`` reads the single
``/leagues/NBA_{year}.html`` page (which carries both the East and West
tables inline) and walks them via :func:`rows.parse_standings`;
``standings_by_date`` reads the template-driven ``/leagues/NBA_{year}_standings_by_date_…``
pages (one per conference) and flattens the rows with a manually
attached ``"conference"`` key.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any

from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.endpoints import ENDPOINTS
from courtside_data.parsing import rows
from courtside_data.parsing.tables import GenericTable

if TYPE_CHECKING:
    from courtside_data.parsing.workflow_parsers._fetch import FetchFacade

__all__ = ["standings", "standings_by_date"]


def _record_standings_diagnostics(
    *,
    parser_name: str,
    parsed_rows: list[dict[str, Any]],
    source_sections: list[str],
    stats: dict[str, Any],
) -> None:
    trace = current_debug_trace()
    if trace is None:
        return
    ignored = stats.get("ignored_row_reason_counts") or {}
    emit_parser_diagnostics(
        trace,
        parser_name=parser_name,
        rows=parsed_rows,
        source_sections=source_sections,
        ignored_event_count=sum(ignored.values()) if isinstance(ignored, dict) else None,
        ignored_event_reason_counts=ignored if isinstance(ignored, dict) else None,
        ignored_row_reason_counts=ignored if isinstance(ignored, dict) else None,
        workflow_diagnostics={
            key: stats[key]
            for key in (
                "conference_count",
                "division_count",
                "team_count",
                "standings_section_count",
            )
            if key in stats
        },
    )


def standings(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return both-conference standings for ``season_end_year``."""
    url = facade.url(f"/leagues/NBA_{season_end_year}.html")
    selector = facade.get_selector(url=url)
    parsed_rows, stats = rows.parse_standings_with_stats(selector)
    _record_standings_diagnostics(
        parser_name="standings",
        parsed_rows=parsed_rows,
        source_sections=["table#divs_standings_E", "table#divs_standings_W"],
        stats=stats,
    )
    return parsed_rows


def standings_by_date(facade: FetchFacade, season_end_year: int) -> list[dict[str, Any]]:
    """Return the standings on the season's last day, tagged with conference.

    The registry's ``standings_by_date`` path template embeds an internal
    ``conference`` placeholder (not exposed as a public call param); this
    function iterates the two conferences, fetches each page, and flattens
    every table row with a ``"conference"`` key set to the human name
    ("Eastern" / "Western").
    """
    endpoint = ENDPOINTS["standings_by_date"]
    standings_rows: list[dict[str, Any]] = []
    source_sections: list[str] = []
    ignored_row_reason_counts: Counter[str] = Counter()
    conference_names: set[str] = set()

    for conference, conference_name in [
        ("eastern_conference", "Eastern"),
        ("western_conference", "Western"),
    ]:
        url = facade.url(endpoint.path.format(season_end_year=season_end_year, conference=conference))
        selector = facade.get_selector(url=url)
        table_selector = selector.css(f"table#{endpoint.table_id}")
        if not table_selector:
            ignored_row_reason_counts["missing_table"] += 1
            continue
        source_sections.append(f"table#{endpoint.table_id}")
        conference_names.add(conference_name)
        table = GenericTable(table_selector[0])
        for row in table.rows:
            standings_rows.append({"conference": conference_name, **row.to_dict()})

    trace = current_debug_trace()
    if trace is not None:
        emit_parser_diagnostics(
            trace,
            parser_name="standings_by_date",
            rows=standings_rows,
            source_sections=source_sections,
            ignored_row_reason_counts=dict(ignored_row_reason_counts),
            workflow_diagnostics={
                "conference_count": len(conference_names),
                "team_count": len(standings_rows),
                "standings_section_count": len(source_sections),
            },
        )
    return standings_rows
