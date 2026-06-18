"""Shared, transport-free helpers used by more than one domain module.

These are the free-function equivalents of the four private ``_xxx_rows``
methods that previously lived on :class:`CustomEndpointHandler`. They
operate on a parsel ``Selector`` (or a pre-located table selector) and
have no need for a :class:`~courtside_data.parsing.custom._fetch.FetchFacade`:
the fetch step is performed by the calling domain function.

Why a separate module? Three of the four helpers are shared across
domains: ``_generic_table_rows`` is used by ``_schedule_rows`` and the
awards/search paths; ``_player_totals_rows`` and
``_player_season_box_score_rows`` are used by two player endpoints each.
Keeping them in a single module avoids circular imports between
``schedule``/``awards``/``players``.
"""

from __future__ import annotations

from typing import Any

from parsel import Selector

from courtside_data.parsing import cells, rows
from courtside_data.parsing.generic import find_table

__all__ = [
    "_generic_table_rows",
    "_player_season_box_score_rows",
    "_player_totals_rows",
    "_schedule_rows",
]


def _generic_table_rows(selector: Selector, table_id: str) -> list[dict[str, Any]]:
    """Return raw ``data-stat`` rows for ``table#<table_id>`` on ``selector``.

    Returns an empty list when the table is missing (mirrors the historic
    ``CustomEndpointHandler._generic_table_rows`` contract).
    """
    table_selector = find_table(selector, table_id)
    if table_selector is None:
        return []
    return [row for row, _ in rows.raw_rows_from_table(table_selector)]


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
    table_selector = find_table(selector, table_id)
    if table_selector is None:
        return []

    parsed_rows: list[dict[str, Any]] = []
    endpoint_name = "players_advanced_season_totals" if table_id == "advanced" else "players_season_totals"
    for row_index, (row, metadata) in enumerate(rows.raw_rows_from_table(table_selector)):
        if not row.get("name_display") or not row.get("team_name_abbr"):
            continue
        if not include_combined and cells.is_combined_team(row):
            continue
        row["slug"] = cells.slug_from_metadata(metadata, "name_display")
        cells.require_slug(endpoint_name, row, row_index)
        if table_id == "advanced":
            row["is_combined_totals"] = cells.is_combined_team(row)
        parsed_rows.append(row)
    return parsed_rows


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
    parsed_rows: list[dict[str, Any]] = []
    for row, metadata in rows.raw_rows_from_table(table_selector):
        if not row.get("date") and not row.get("date_game"):
            continue

        active = "colspan" not in metadata.get("is_starter", {})
        if not active and not include_inactive_games:
            continue

        row["active"] = active
        parsed_rows.append(row)
    return parsed_rows


def _schedule_rows(selector: Selector) -> list[dict[str, Any]]:
    """Return the schedule rows for a single month page.

    Wraps :func:`_generic_table_rows` with the BR-specific guard that
    both the visitor and home team names must be present (rows lacking
    either are all-star / exhibition / data-spacer rows).
    """
    return [
        row
        for row in _generic_table_rows(selector, "schedule")
        if row.get("visitor_team_name") and row.get("home_team_name")
    ]
