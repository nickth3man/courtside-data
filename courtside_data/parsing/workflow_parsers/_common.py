"""Shared, transport-free helpers used by more than one domain module.

These are transport-free row helpers used by native workflow steps. They
operate on a parsel ``Selector`` or a pre-located table selector; the fetch
step is performed by the workflow executor.

Why a separate module? Three of the four helpers are shared across
domains: ``_generic_table_rows`` is used by ``_schedule_rows`` and the
awards/search paths; ``_player_totals_rows`` and
``_player_season_box_score_rows`` are used by two player endpoints each.
Keeping them in a single module avoids circular imports between
``schedule``/``awards``/``players``.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Protocol

from parsel import Selector

from courtside_data._frozen import frozen_slot
from courtside_data.client._pipelines.drop_reasons import row_drop_reason
from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.parsing import cells, rows
from courtside_data.parsing.generic import find_table
from courtside_data.parsing.workflow_parsers._diagnostics import (
    IGNORE_COMBINED_TEAM,
    IGNORE_INACTIVE_GAME,
    IGNORE_MISSING_DATE,
    IGNORE_MISSING_NAME_OR_TEAM,
    IGNORE_MISSING_TABLE,
    increment_ignored,
    merge_ignored_counts,
    merge_numeric_stats,
)


@frozen_slot
class ExtractResult:
    """Rows extracted from a table plus the parser-diagnostics stats dict.

    The three ``*_rows_with_stats`` helpers in this module return this
    dataclass so the rows and the diagnostics move together as a single
    value. The bare ``*_rows`` wrappers just unwrap :attr:`rows` for the
    call sites that only need the row list.
    """

    rows: list[dict[str, Any]]
    stats: dict[str, Any]


class StatsExtractor(Protocol):
    """A callable that extracts rows + diagnostics stats from a selector/table.

    Each ``*_rows_with_stats`` helper in this module matches this shape;
    the protocol is the type-level handle for treating them uniformly
    (e.g. when building a registry of extractors).
    """

    def __call__(self, *args: Any, **kwargs: Any) -> ExtractResult: ...


__all__ = [
    "ExtractResult",
    "StatsExtractor",
    "_generic_table_rows",
    "_merge_schedule_stats",
    "_merge_search_stats",
    "_merge_team_box_score_stats",
    "_player_season_box_score_rows",
    "_player_season_box_score_rows_with_stats",
    "_player_totals_rows",
    "_player_totals_rows_with_stats",
    "_record_schedule_diagnostics",
    "_record_standings_diagnostics",
    "_schedule_rows",
    "_schedule_rows_with_stats",
]


def _generic_table_rows(selector: Selector, table_id: str) -> list[dict[str, Any]]:
    """Return raw ``data-stat`` rows for ``table#<table_id>`` on ``selector``.

    Returns an empty list when the table is missing.
    """
    table_selector = find_table(selector, table_id)
    if table_selector is None:
        return []
    return [row for row, _ in rows.raw_rows_from_table(table_selector)]


def _player_totals_rows_with_stats(
    selector: Selector,
    table_id: str,
    *,
    include_combined: bool,
) -> ExtractResult:
    """Extract league-wide player totals rows and parser diagnostics."""
    table_selector = find_table(selector, table_id)
    ignored_row_reason_counts: dict[str, int] = {}
    repeated_header_count = 0

    if table_selector is None:
        return ExtractResult(
            rows=[],
            stats={
                "player_count": 0,
                "raw_row_count": 0,
                "raw_column_count": 0,
                "stat_table_count": 0,
                "basic_table_count": 0,
                "advanced_table_count": 0,
                "missing_table_count": 1,
                "ranked_row_count": 0,
                "repeated_header_count": 0,
                "ignored_row_reason_counts": {IGNORE_MISSING_TABLE: 1},
                "selected_table_id": table_id,
            },
        )

    raw_rows = list(rows.raw_rows_from_table(table_selector))
    raw_row_count = len(raw_rows)
    raw_column_count = len(raw_rows[0][0]) if raw_rows else 0
    ranked_row_count = sum(1 for row, _ in raw_rows if row.get("ranker") not in (None, ""))

    for row, _ in raw_rows:
        if row_drop_reason(row) == "repeated_header":
            repeated_header_count += 1

    parsed_rows: list[dict[str, Any]] = []
    endpoint_name = "players_advanced_season_totals" if table_id == "advanced" else "players_season_totals"
    for row_index, (row, metadata) in enumerate(raw_rows):
        if not row.get("name_display") or not row.get("team_name_abbr"):
            increment_ignored(ignored_row_reason_counts, IGNORE_MISSING_NAME_OR_TEAM)
            continue
        if not include_combined and cells.is_combined_team(row):
            increment_ignored(ignored_row_reason_counts, IGNORE_COMBINED_TEAM)
            continue
        row["slug"] = cells.slug_from_metadata(metadata, "name_display")
        cells.require_slug(endpoint_name, row, row_index)
        if table_id == "advanced":
            row["is_combined_totals"] = cells.is_combined_team(row)
        parsed_rows.append(row)

    stats = {
        "player_count": len(parsed_rows),
        "raw_row_count": raw_row_count,
        "raw_column_count": raw_column_count,
        "stat_table_count": 1,
        "basic_table_count": 1 if table_id == "totals_stats" else 0,
        "advanced_table_count": 1 if table_id == "advanced" else 0,
        "missing_table_count": 0,
        "ranked_row_count": ranked_row_count,
        "repeated_header_count": repeated_header_count,
        "ignored_row_reason_counts": ignored_row_reason_counts,
        "selected_table_id": table_id,
        "season_count": 1,
    }
    return ExtractResult(rows=parsed_rows, stats=stats)


def _player_totals_rows(selector: Selector, table_id: str, *, include_combined: bool) -> list[dict[str, Any]]:
    """Extract one of the two league-wide player totals tables.

    ``table_id`` is either ``"totals_stats"`` (regular season totals) or
    ``"advanced"`` (advanced season totals). The function filters out
    rows missing the player's display name or team, optionally drops
    "combined" rows from multi-team stints (``include_combined=False``),
    and injects the player ``slug`` (raising :class:`MissingPlayerSlug`
    if the BR page omits ``data-append-csv``). The
    ``is_combined_totals`` flag is preserved on the ``"advanced"`` table
    for downstream consumers.
    """
    return _player_totals_rows_with_stats(selector, table_id, include_combined=include_combined).rows


def _player_season_box_score_rows_with_stats(
    table_selector: Selector,
    *,
    include_inactive_games: bool,
) -> ExtractResult:
    """Extract per-player season game-log rows and parser diagnostics."""
    ignored_row_reason_counts: dict[str, int] = {}
    parsed_rows: list[dict[str, Any]] = []
    starter_count = 0
    bench_count = 0
    raw_rows = list(rows.raw_rows_from_table(table_selector))
    raw_row_count = len(raw_rows)
    raw_column_count = len(raw_rows[0][0]) if raw_rows else 0

    for row, metadata in raw_rows:
        if not row.get("date") and not row.get("date_game"):
            increment_ignored(ignored_row_reason_counts, IGNORE_MISSING_DATE)
            continue

        active = "colspan" not in metadata.get("is_starter", {})
        if not active and not include_inactive_games:
            increment_ignored(ignored_row_reason_counts, IGNORE_INACTIVE_GAME)
            continue

        row["active"] = active
        parsed_rows.append(row)
        if active:
            games_started = str(row.get("gs") or row.get("is_starter") or "").strip()
            if games_started == "1":
                starter_count += 1
            elif games_started == "0":
                bench_count += 1

    stats = {
        "game_count": len(parsed_rows),
        "player_count": 1,
        "starter_count": starter_count,
        "bench_count": bench_count,
        "stat_table_count": 1,
        "basic_table_count": 1,
        "advanced_table_count": 0,
        "raw_row_count": raw_row_count,
        "raw_column_count": raw_column_count,
        "ignored_row_reason_counts": ignored_row_reason_counts,
    }
    return ExtractResult(rows=parsed_rows, stats=stats)


def _player_season_box_score_rows(
    table_selector: Selector,
    *,
    include_inactive_games: bool,
) -> list[dict[str, Any]]:
    """Extract one of the per-player season game-log tables.

    A row with no date (``date`` and ``date_game`` both empty) is skipped
    entirely (sub-header / column-spacer). Otherwise the row is tagged
    ``"active"`` from the absence of a ``colspan`` attribute on the
    ``is_starter`` cell — the BR convention for the inactive "Did Not
    Play" / "Did Not Dress" rows — and the row is dropped when
    ``include_inactive_games=False``.
    """
    return _player_season_box_score_rows_with_stats(
        table_selector,
        include_inactive_games=include_inactive_games,
    ).rows


def _schedule_rows_with_stats(selector: Selector) -> ExtractResult:
    """Return schedule rows and parser diagnostics for one month page."""
    all_rows = _generic_table_rows(selector, "schedule")
    ignored_row_reason_counts: dict[str, int] = {}
    kept_rows: list[dict[str, Any]] = []
    postponed_game_count = 0
    box_score_link_count = 0
    missing_box_score_link_count = 0

    for row in all_rows:
        if not row.get("visitor_team_name") or not row.get("home_team_name"):
            ignored_row_reason_counts["missing_teams"] = ignored_row_reason_counts.get("missing_teams", 0) + 1
            continue
        kept_rows.append(row)
        remarks = str(row.get("game_remarks") or "").lower()
        if "postponed" in remarks:
            postponed_game_count += 1
        box_score_text = row.get("box_score_text")
        if box_score_text and str(box_score_text).strip():
            box_score_link_count += 1
        else:
            missing_box_score_link_count += 1

    stats = {
        "game_count": len(kept_rows),
        "postponed_game_count": postponed_game_count,
        "box_score_link_count": box_score_link_count,
        "missing_box_score_link_count": missing_box_score_link_count,
        "ignored_row_reason_counts": ignored_row_reason_counts,
        "candidate_row_count": len(all_rows),
    }
    return ExtractResult(rows=kept_rows, stats=stats)


def _schedule_rows(selector: Selector) -> list[dict[str, Any]]:
    """Return the schedule rows for a single month page.

    Wraps :func:`_generic_table_rows` with the BR-specific guard that
    both the visitor and home team names must be present (rows lacking
    either are all-star / exhibition / data-spacer rows).
    """
    return _schedule_rows_with_stats(selector).rows


# --- Relocated merger / diagnostics helpers (kept alive by the workflow step engine) ---
# These five helpers used to live in per-endpoint modules under
# ``workflow_parsers/`` (``boxscores``, ``schedule``, ``search``, ``standings``).
# The declarative step engine in ``courtside_data/parsing/workflows/_steps/`` is
# the only remaining caller, so they were hoisted here to keep the per-endpoint
# modules deletable.

_TEAM_BOX_SCORE_AGGREGATE_KEYS = (
    "game_count",
    "team_count",
    "stat_table_count",
    "basic_table_count",
    "advanced_table_count",
    "empty_table_count",
)


def _merge_team_box_score_stats(aggregate: dict[str, Any], page_stats: dict[str, Any]) -> None:
    merge_numeric_stats(aggregate, page_stats, keys=_TEAM_BOX_SCORE_AGGREGATE_KEYS)
    ignored = aggregate.setdefault("ignored_row_reason_counts", Counter())
    merge_ignored_counts(ignored, page_stats.get("ignored_row_reason_counts") or {})


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


def _merge_search_stats(aggregate: dict[str, Any], page_stats: dict[str, Any]) -> None:
    aggregate["candidate_count"] = aggregate.get("candidate_count", 0) + page_stats.get("candidate_count", 0)
    aggregate["matched_result_count"] = aggregate.get("matched_result_count", 0) + page_stats.get(
        "matched_result_count", 0
    )
    ignored = aggregate.setdefault("ignored_result_reason_counts", Counter())
    for reason, count in (page_stats.get("ignored_result_reason_counts") or {}).items():
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
        workflow_diagnostics={
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
