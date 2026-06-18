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

from typing import TYPE_CHECKING, Any

import httpx
from parsel import Selector

from courtside_data.data import TEAM_TO_TEAM_ABBREVIATION, Team
from courtside_data.errors import InvalidDate
from courtside_data.parsing import cells, rows
from courtside_data.parsing.generic import find_table

if TYPE_CHECKING:
    from courtside_data.parsing.custom._fetch import FetchFacade

__all__ = [
    "play_by_play",
    "player_box_scores",
    "team_box_score",
    "team_box_scores",
]


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
    return rows.parse_play_by_play_rows(selector, away_team, home_team_abbreviation)


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
        parsed_rows = []
        for row_index, (row, metadata) in enumerate(rows.raw_rows_from_table(table)):
            row["slug"] = cells.slug_from_metadata(metadata, "player")
            cells.require_slug("player_box_scores", row, row_index)
            parsed_rows.append(row)
        if not parsed_rows:
            raise InvalidDate(day=day, month=month, year=year)
        return parsed_rows

    raise InvalidDate(day=day, month=month, year=year)


def team_box_score(facade: FetchFacade, game_url_path: str) -> list[dict[str, Any]]:
    """Return the two team totals (one row per side) for one game."""
    url = facade.url(game_url_path)
    selector = facade.get_selector(url=url)
    return rows.parse_team_box_score(selector)


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

    return [
        box_score
        for game_url_path in game_url_paths
        for box_score in team_box_score(facade, game_url_path=game_url_path)
    ]
