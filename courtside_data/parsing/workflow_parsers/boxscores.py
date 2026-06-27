"""Box-score family endpoints (``player_box_scores``, ``team_box_score``,
``team_box_scores``, ``play_by_play``).

These four endpoints all read pages rooted at ``/boxscores/...``:

* ``team_box_score`` reads a single game's box score page and returns the
  two team totals (``<tfoot>`` rows of every ``table.stats_table`` whose
  id starts with ``box-``).
* ``team_box_scores`` reads the daily ``/boxscores/`` index, collects
  every game link, and reuses :func:`team_box_score` per game.
* ``player_box_scores`` reads the daily-leaders friv page
  (``/friv/dailyleaders.cgi?month=…``) and returns one row per
  player-leader, requiring a player slug (raises
  :class:`InvalidDate` when the page has no leaders table).
* ``play_by_play`` resolves the right game URL from the daily
  ``/boxscores/`` index, then reads the per-game ``/boxscores/pbp/…``
  page and walks each play.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any

import httpx
from parsel import Selector

from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import emit_parser_diagnostics
from courtside_data.domain import TEAM_TO_TEAM_ABBREVIATION, Team
from courtside_data.errors import InvalidDate
from courtside_data.parsing import cells, rows
from courtside_data.parsing.generic import find_table
from courtside_data.parsing.workflow_parsers._diagnostics import (
    emit_workflow_endpoint_diagnostics,
    merge_ignored_counts,
    merge_numeric_stats,
)

if TYPE_CHECKING:
    from courtside_data.parsing.workflow_parsers._fetch import FetchFacade

__all__ = [
    "play_by_play",
    "player_box_scores",
    "team_box_score",
    "team_box_scores",
]

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


def play_by_play(
    facade: FetchFacade,
    home_team: Team,
    day: int,
    month: int,
    year: int,
) -> list[dict[str, Any]]:
    """Return every play of the game whose home team is ``home_team`` on ``year-month-day``.

    Resolution: scrape the daily ``/boxscores/`` index, find the link
    whose path ends with the team's abbreviation (via
    :func:`rows.resolve_pbp_game_url_path`), then scrape the per-game
    ``/boxscores/pbp/…`` page. The two team names are read from the
    scorebox and used to label the away/home sides in the play rows.
    Raises :class:`InvalidDate` when no matching game link is found.
    """
    abbr = TEAM_TO_TEAM_ABBREVIATION[home_team]
    boxscores_selector = facade.get_selector(
        url=facade.url(f"/boxscores/?day={day}&month={month}&year={year}"),
    )
    game_url_path = rows.resolve_pbp_game_url_path(boxscores_selector, abbr)
    if game_url_path is None:
        raise InvalidDate(day=day, month=month, year=year)
    url = facade.url(f"/boxscores/pbp/{game_url_path.split('/')[-1]}")
    selector = facade.get_selector(url=url)
    team_names = [cells.cell_text(team_name) for team_name in selector.css("#content div.scorebox strong a")]
    away_team = cells.team_abbreviation_from_name(team_names[0])
    home_team_abbreviation = cells.team_abbreviation_from_name(team_names[1])
    parsed_rows, stats = rows.parse_play_by_play_rows_with_stats(selector, away_team, home_team_abbreviation)
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


def player_box_scores(facade: FetchFacade, day: int, month: int, year: int) -> list[dict[str, Any]]:
    """Return one row per player on the daily-leaders friv page.

    The friv endpoint follows no redirect by default (the page itself is
    a 200 OK), so the response body is parsed in place. Raises
    :class:`InvalidDate` when the page has no leaders ``<table#stats>``
    or the leaders table yields no rows.
    """
    url = facade.url(f"/friv/dailyleaders.cgi?month={month}&day={day}&year={year}")

    response = facade.get(url=url, follow_redirects=False)

    response.raise_for_status()

    if response.status_code == httpx.codes.OK:
        selector = Selector(text=response.text)
        table = find_table(selector, "stats")
        if table is None:
            raise InvalidDate(day=day, month=month, year=year)
        parsed_rows, stats = rows.parse_player_box_scores_from_table_with_stats(table)
        if not parsed_rows:
            raise InvalidDate(day=day, month=month, year=year)
        emit_workflow_endpoint_diagnostics(
            parser_name="player_box_scores",
            endpoint_name="player_box_scores",
            rows=parsed_rows,
            source_sections=["table#stats"],
            stats=stats,
            selected_table_id="stats",
        )
        return parsed_rows

    raise InvalidDate(day=day, month=month, year=year)


def team_box_score(facade: FetchFacade, game_url_path: str) -> list[dict[str, Any]]:
    """Return the two team totals (one row per side) for one game."""
    url = facade.url(game_url_path)
    selector = facade.get_selector(url=url)
    parsed_rows, stats = rows.parse_team_box_score_with_stats(selector)
    emit_workflow_endpoint_diagnostics(
        parser_name="team_box_score",
        endpoint_name="team_box_score",
        rows=parsed_rows,
        source_sections=['table.stats_table[id$="-game-basic"]'],
        stats=stats,
    )
    return parsed_rows


def team_box_scores(facade: FetchFacade, day: int, month: int, year: int) -> list[dict[str, Any]]:
    """Return team box-score rows for every game on ``year-month-day``.

    The daily ``/boxscores/`` index lists every game as a ``td.gamelink a``
    element; the function iterates the list and reuses
    :func:`team_box_score` per game. Raises :class:`InvalidDate` when the
    index lists no games.
    """
    url = facade.url(f"/boxscores/?day={day}&month={month}&year={year}")

    selector = facade.get_selector(url=url)
    game_url_paths = [link.attrib["href"] for link in selector.css("td.gamelink a")]
    if not game_url_paths:
        raise InvalidDate(day=day, month=month, year=year)

    aggregate_stats: dict[str, Any] = {
        "game_count": 0,
        "team_count": 0,
        "stat_table_count": 0,
        "basic_table_count": 0,
        "advanced_table_count": 0,
        "empty_table_count": 0,
        "ignored_row_reason_counts": Counter(),
    }
    all_rows: list[dict[str, Any]] = []
    for game_url_path in game_url_paths:
        game_selector = facade.get_selector(url=facade.url(game_url_path))
        game_rows, game_stats = rows.parse_team_box_score_with_stats(game_selector)
        all_rows.extend(game_rows)
        _merge_team_box_score_stats(aggregate_stats, game_stats)

    emit_workflow_endpoint_diagnostics(
        parser_name="team_box_scores",
        endpoint_name="team_box_scores",
        rows=all_rows,
        source_sections=["td.gamelink a", 'table.stats_table[id$="-game-basic"]'],
        stats=aggregate_stats,
    )
    return all_rows
