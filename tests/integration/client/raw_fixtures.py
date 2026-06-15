"""Resolve integration-test HTML fixtures to the committed ``raw/`` corpus.

The legacy ``tests/integration/files/`` tree was removed in favour of the
``raw/`` corpus (downloaded by ``scripts.raw_download`` and now committed). The
two layouts differ: ``raw/`` is keyed by the registry endpoint name and a
per-example id that can encode call parameters (e.g. season + flag), whereas the
old tree used ad-hoc ``<endpoint>/<year>.html`` paths.

This module centralizes that mapping. Each helper returns the HTML body for a
given example, or calls :func:`pytest.skip` when the corpus does not yet contain
it — so a partially-populated corpus yields skips (pending download) rather than
``FileNotFoundError``.
"""

from __future__ import annotations

import pathlib
import re

import pytest

# tests/integration/client/raw_fixtures.py -> repo root is three parents up.
RAW_ROOT = pathlib.Path(__file__).resolve().parents[3] / "raw"


def read(relative_path: str) -> str:
    """Return the HTML body at ``raw/<relative_path>``; skip if absent."""
    path = RAW_ROOT / relative_path
    if not path.is_file():
        pytest.skip(f"raw corpus missing fixture {relative_path!r}; run scripts.raw_download to add it")
    return path.read_text(encoding="utf8")


def _first_match(glob: str) -> str:
    """Return the body of the first file matching ``glob`` under raw/; skip if none."""
    matches = sorted(RAW_ROOT.glob(glob))
    if not matches:
        pytest.skip(f"raw corpus has no fixture matching {glob!r}; run scripts.raw_download to add it")
    return matches[0].read_text(encoding="utf8")


def players_season_totals(year: int) -> str:
    """League season totals page for ``year`` (raw: ``players_season_totals/<year>.html``)."""
    return read(f"players_season_totals/{year}.html")


def players_advanced_season_totals(year: int) -> str:
    """Advanced season totals page for ``year``.

    The corpus encodes the ``include_combined_values`` flag in the example id
    (e.g. ``2019_true.html``), but the page body is identical regardless of the
    flag — the flag only affects post-fetch row filtering — so any example for
    the season is acceptable.
    """
    return _first_match(f"players_advanced_season_totals/{year}_*.html")


def standings(year: int) -> str:
    """League index page for ``year`` (raw: ``standings/<year>.html``)."""
    return read(f"standings/{year}.html")


def player_daily_box_scores(year: int, month: int, day: int) -> str:
    """Daily-leaders page (raw: ``player_box_scores/<year>_<mm>_<dd>.html``)."""
    return read(f"player_box_scores/{year}_{month:02d}_{day:02d}.html")


def play_by_play_game(game_id: str) -> str:
    """The pbp game page for ``game_id`` (raw: ``play_by_play/<example>/<game_id>.html``)."""
    return _first_match(f"play_by_play/*/{game_id}.html")


def gamelog(player_identifier: str, year: int) -> str:
    """A player's season gamelog page.

    Regular-season and playoff box scores are parsed from the *same* gamelog
    URL, so a single corpus file (stored under either endpoint dir) serves both.
    """
    for endpoint_dir in ("regular_season_player_box_scores", "playoff_player_box_scores"):
        path = RAW_ROOT / endpoint_dir / f"{player_identifier}_{year}.html"
        if path.is_file():
            return path.read_text(encoding="utf8")
    pytest.skip(f"raw corpus missing gamelog for {player_identifier!r} {year}; run scripts.raw_download to add it")


def season_schedule_dir(year: int) -> pathlib.Path:
    """Directory of a season's schedule pages (``index.html`` + ``<month>.html``)."""
    path = RAW_ROOT / "season_schedule" / str(year)
    if not path.is_dir():
        pytest.skip(f"raw corpus missing season_schedule/{year}; run scripts.raw_download to add it")
    return path


def team_box_scores_dir(year: int, month: int, day: int) -> pathlib.Path:
    """Directory of a day's team box scores (``index.html`` + ``<game_id>.html``)."""
    path = RAW_ROOT / "team_box_scores" / f"{year}_{month:02d}_{day:02d}"
    if not path.is_dir():
        pytest.skip(f"raw corpus missing team_box_scores/{year}_{month:02d}_{day:02d}; run scripts.raw_download")
    return path


def team_box_scores_index(year: int, month: int, day: int) -> str:
    """The daily boxscores index page (raw: ``team_box_scores/<date>/index.html``)."""
    path = team_box_scores_dir(year, month, day) / "index.html"
    if not path.is_file():
        pytest.skip(f"raw corpus missing team_box_scores index for {year}-{month}-{day}")
    return path.read_text(encoding="utf8")


def team_box_score_game(year: int, month: int, day: int, game_id: str) -> str:
    """A single game's box-score page from a day's team_box_scores directory."""
    path = team_box_scores_dir(year, month, day) / f"{game_id}.html"
    if not path.is_file():
        pytest.skip(f"raw corpus missing team box score {game_id} for {year}-{month}-{day}")
    return path.read_text(encoding="utf8")


def schedule_page(legacy_path: str) -> str:
    """Resolve a legacy ``files/schedule/<path>`` reference to the raw corpus.

    ``"<year>/<year>.html"`` maps to ``season_schedule/<year>/index.html``.
    """
    parts = legacy_path.split("/")
    if len(parts) == 2:
        return read(f"season_schedule/{parts[0]}/index.html")
    return read(f"season_schedule/{legacy_path}")


# Search example ids in the corpus are filename-safe slugs of the query term.
_SEARCH_SLUGS = {
    "kobe": "kobe",
    "kobe bryant": "kobe_bryant",
    "Alonzo Mourning": "alonzo_mourning",
    "Dominique Wilkins": "dominique_wilkins",
    "Rick Barry": "rick_barry",
    "jaebaebae": "jaebaebae",
}


def _search_slug(term: str) -> str:
    return _SEARCH_SLUGS.get(term) or re.sub(r"[^a-z0-9]+", "_", term.lower()).strip("_")


def search_term(term: str) -> str:
    """Search results/redirect page for ``term`` (raw: ``search/<slug>.html``)."""
    return read(f"search/{_search_slug(term)}.html")


def search_ja_page(page: int) -> str:
    """One page of the paginated ``ja`` search (raw: ``search/ja_page_<n>.html``)."""
    return read(f"search/ja_page_{page}.html")


def seven_game_playoff_series_outcomes_page() -> str:
    """The 7-game playoff series outcomes page.

    The three endpoint variants (team-is-down, team-is-tied, team-is-up) all
    live on the same Basketball-Reference page, so the corpus stores a single
    fixture under the ``team_is_down`` family and resolves the other two to it.
    """
    for endpoint_dir in (
        "friv_7_game_playoff_series_outcomes_team_is_down",
        "friv_7_game_playoff_series_outcomes",
    ):
        path = RAW_ROOT / endpoint_dir / "7-game-playoff-series-outcomes-22111.html"
        if path.is_file():
            return path.read_text(encoding="utf8")
    pytest.skip("raw corpus missing 7-game-playoff-series-outcomes page; run scripts.raw_download to add it")
