"""Application service for Team Hub API routes.

Mirrors :class:`courtside_data.server.service.PlayerHubService` for the
13 team endpoint specs registered in
:mod:`courtside_data.endpoints._teams`. The hub reuses the same
``CourtsideClient`` + ``build_fixture_service`` plumbing as the player
hub; the public API surface is the 6 routes registered in
:mod:`courtside_data.server.app`.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from courtside_data.client import CourtsideClient
from courtside_data.domain.seasons import current_nba_season_end_year, season_end_year
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import InvalidSearch
from courtside_data.server.fixtures import MissingFixtureError, build_fixture_service
from courtside_data.server.models import EndpointRowsResponse, TransportMode
from courtside_data.server.team_catalog import (
    TEAM_DATASETS,
    team_columns_for_dataset,
    team_dataset_by_id,
)
from courtside_data.server.team_models import (
    FranchiseArcPoint,
    TeamHeroStats,
    TeamHubSummary,
    TeamSearchResult,
)

# Team endpoints are parametrised by ``team_abbreviation`` (and, for most,
# ``season_end_year``) per ``courtside_data.endpoints._table._team``. The
# public API uses ``team_identifier`` as the user-facing path param to
# mirror the player hub's ``player_identifier``; the service maps it onto
# the endpoint's actual param names at call time.
_TEAM_ABBREVIATION_PARAM = "team_abbreviation"
_TEAM_SEASON_PARAM = "season_end_year"
_TEAM_INCLUDE_INACTIVE_PARAM = "include_inactive_games"


def _row_get(row: object, key: str) -> object:
    """Read ``key`` from a row that may be a Pydantic model or a dict.

    Pydantic-BRRow exposes attribute access; the search service's
    fake rows and any future dict-shaped row both expose ``[]`` /
    ``get``. This helper unifies both shapes so the row-projection
    helpers (``_team_hero_stats``, ``_franchise_arc``) can accept
    either.
    """
    if isinstance(row, dict):
        return row.get(key)
    getter = getattr(row, key, None)
    if getter is not None:
        return getter
    getitem = getattr(row, "__getitem__", None)
    if getitem is None:
        return None
    try:
        return getitem(key)
    except (KeyError, TypeError, IndexError):
        return None


# Human-readable team display names. The list is intentionally small —
# it covers the canonical abbreviations the UI has branded in
# ``docs/architecture/team-hub.md``. Unknown abbreviations fall back to
# the raw ``team_identifier`` (mirroring the player hub's
# ``PLAYER_DISPLAY_NAMES`` fallback).
#
# TODO(team-hub): source the display-name map from data instead of a
# hand-curated static dict.
#
# What: replace the static :data:`TEAM_DISPLAY_NAMES` with a lookup
# driven by the ``franchise_history`` endpoint (the
# ``FranchiseHistoryRow`` schema at
# ``courtside_data/schemas/teams.py:286`` exposes ``team_name`` and
# ``season`` columns) so renames and relocations (e.g. the
# Seattle SuperSonics -> OKC Thunder) propagate automatically.
# Where:
#   - courtside_data/server/team_service.py:372  (the
#     ``display_name=TEAM_DISPLAY_NAMES.get(...)`` line in
#     :meth:`TeamHubService.summary`).
#   - courtside_data/schemas/teams.py:286  (``FranchiseHistoryRow``).
#   - courtside_data/server/fixtures.py:49  (``franchise_history`` is
#     already whitelisted in ``TEAM_ENDPOINTS``).
# How:
#   1. Memoize a ``_team_display_name(team_identifier) -> str`` helper
#     that calls the ``franchise_history`` endpoint once per
#     abbreviation, picks the most-recent ``team_name`` from the
#     returned rows, and caches it for the process lifetime.
#   2. Keep :data:`TEAM_DISPLAY_NAMES` as the offline / pre-fixture
#     fallback so the summary still renders in fixture mode before
#     ``franchise_history`` fixtures are captured.
# Decision needed: cache invalidation policy when a team's nickname
# changes mid-process (e.g. live transport is in use for hours);
# player hub has no analog and re-fetches on every summary call, which
# is acceptable here too.
# Verify: ``uv run python -c "from
#   courtside_data.server.team_service import TEAM_DISPLAY_NAMES;
#   assert TEAM_DISPLAY_NAMES['BOS'] == 'Boston Celtics';"`` and
#   ``TestClient(create_app(transport='live')).get(
#   '/api/teams/BOS/summary')['display_name']`` -> ``"Boston Celtics"``.
TEAM_DISPLAY_NAMES: dict[str, str] = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BRK": "Brooklyn Nets",
    "CHA": "Charlotte Hornets",
    "CHH": "Charlotte Hornets",
    "CHO": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "KCK": "Kansas City Kings",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NJN": "New Jersey Nets",
    "NOH": "New Orleans Hornets",
    "NOK": "New Orleans/Oklahoma City Hornets",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHX": "Phoenix Suns",
    "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "SEA": "Seattle SuperSonics",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "VAN": "Vancouver Grizzlies",
    "WAS": "Washington Wizards",
    "WSB": "Washington Bullets",
}


class TeamHubService:
    """Runs existing Courtside Data endpoints for the Team Hub API."""

    def __init__(self, *, transport: TransportMode = "fixture", raw_root: Path | None = None) -> None:
        self.transport = transport
        self.raw_root = raw_root
        self._live_client = CourtsideClient(cache=True) if transport == "live" else None

    # ------------------------------------------------------------------ infra
    def _client_for(self, endpoint_name: str, params: dict[str, object]) -> CourtsideClient:
        if self.transport == "live":
            if self._live_client is None:
                self._live_client = CourtsideClient(cache=True)
            return self._live_client
        service = build_fixture_service(endpoint_name, params, raw_root=self.raw_root)
        return CourtsideClient(service=service)

    def _build_params(
        self,
        endpoint_name: str,
        *,
        team_identifier: str,
        season_end_year: int | None = None,
        include_inactive_games: bool | None = None,
    ) -> dict[str, Any]:
        """Translate the public kwargs into the endpoint's native param dict.

        Looks up the endpoint's declared param names from
        :data:`courtside_data.endpoints.ENDPOINTS` so we never hard-code
        endpoint-specific kwarg names beyond the one the public contract
        guarantees (``team_identifier``).
        """
        spec = ENDPOINTS[endpoint_name]
        params: dict[str, Any] = {}
        for name in spec.params:
            if name == _TEAM_ABBREVIATION_PARAM:
                params[name] = team_identifier
            elif name == _TEAM_SEASON_PARAM:
                if season_end_year is None:
                    # Safety net for direct service callers that bypass the
                    # route layer: :meth:`TeamHubService.summary` always
                    # passes an explicit season (resolved via
                    # :func:`courtside_data.domain.seasons.current_nba_season_end_year`)
                    # and the season_dataset / CSV export routes both pass
                    # ``season_end_year`` from the URL or query string.
                    # This raise is therefore only reached by a direct
                    # ``svc._build_params(...)`` call without a season, and
                    # is intentionally preserved so the CSV export route
                    # can still surface ``400 bad_request`` for a missing
                    # ``season_end_year`` query parameter (see
                    # :func:`courtside_data.server.app.team_export`).
                    raise ValueError(
                        f"Endpoint {endpoint_name!r} requires season_end_year; "
                        "pass season_end_year explicitly or use summary() which "
                        "falls back to current_nba_season_end_year()"
                    )
                params[name] = season_end_year
            elif name == _TEAM_INCLUDE_INACTIVE_PARAM:
                params[name] = bool(include_inactive_games) if include_inactive_games is not None else False
            else:
                # The mapping only knows the three params above. Every
                # team endpoint in :mod:`courtside_data.endpoints._teams`
                # today uses one of those three (``team_contracts`` and
                # ``franchise_history`` override to a single-param
                # ``("team_abbreviation",)`` spec; the rest take the
                # default ``("team_abbreviation", "season_end_year")``
                # pair). ``include_inactive_games`` is forward-compat for
                # future team-box-score endpoints. If a new team endpoint
                # declares a different param, add an ``elif name == "..."``
                # branch here that pulls the value from a public kwarg
                # on :meth:`TeamHubService._build_params`.
                raise NotImplementedError(
                    f"_build_params: endpoint {endpoint_name!r} declares unhandled param {name!r}. "
                    f"Add an elif branch mapping it to a public kwarg. "
                    f"Declared params: {ENDPOINTS[endpoint_name].params}"
                )
        return params

    def _fetch(
        self,
        endpoint_name: str,
        *,
        team_identifier: str,
        season_end_year: int | None = None,
        include_inactive_games: bool | None = None,
    ) -> list[Any]:
        """Run an endpoint and return its raw rows.

        Mirrors :meth:`PlayerHubService._run`; the caller passes the
        public kwargs (``team_identifier``, ``season_end_year``,
        ``include_inactive_games``) and this method maps them onto the
        endpoint's native param names.
        """
        params = self._build_params(
            endpoint_name,
            team_identifier=team_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )
        client = self._client_for(endpoint_name, params)
        endpoint_func = getattr(client, endpoint_name)
        values = endpoint_func(**params, output_type=None)
        return list(values)

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[Any]:
        """Run an endpoint with a fully built native params dict.

        Mirrors :meth:`PlayerHubService._run`; used by the CSV export
        path and the team-summary hero-stats helper where the params
        dict is already in the endpoint's native shape.
        """
        client = self._client_for(endpoint_name, params)
        endpoint_func = getattr(client, endpoint_name)
        values = endpoint_func(**params, output_type=None)
        return list(values)

    def _rows_for_dataset(self, dataset_id: str, params: dict[str, object]) -> EndpointRowsResponse:
        """Run a :class:`TeamDataset` and shape the response envelope.

        Mirrors :meth:`PlayerHubService.rows_for_dataset`; takes the
        native params dict (including the resolved season) so callers
        that already know the season can avoid the public kwargs.
        """
        dataset = team_dataset_by_id(dataset_id)
        rows = self._serialize_rows(self._run(dataset.endpoint_name, params))
        columns = team_columns_for_dataset(dataset, rows[0] if rows else None)
        return EndpointRowsResponse(
            dataset=dataset.id,
            endpoint_name=dataset.endpoint_name,
            params=params,
            row_count=len(rows),
            columns=columns,
            default_visible_columns=list(dataset.default_visible_columns),
            rows=rows,
            transport=self.transport,
        )

    def _empty_rows_response(self, dataset_id: str, season_end_year: int) -> EndpointRowsResponse:
        """Build an empty :class:`EndpointRowsResponse` envelope.

        Used as the fallback when an embedded dataset call (e.g. the
        summary's ``team_roster``) cannot be served in fixture mode.
        """
        dataset = team_dataset_by_id(dataset_id)
        return EndpointRowsResponse(
            dataset=dataset.id,
            endpoint_name=dataset.endpoint_name,
            params={_TEAM_SEASON_PARAM: season_end_year},
            row_count=0,
            columns=team_columns_for_dataset(dataset),
            default_visible_columns=list(dataset.default_visible_columns),
            rows=[],
            transport=self.transport,
        )

    def _franchise_arc(self, team_identifier: str) -> list[FranchiseArcPoint]:
        """Project the ``franchise_history`` table to a sorted win-loss arc.

        Calls the ``franchise_history`` endpoint once per team and
        reduces each :class:`~courtside_data.schemas.teams.FranchiseHistoryRow`
        to a :class:`FranchiseArcPoint`. Rows with an unparseable
        ``season`` field are skipped (defensive — the source schema
        allows ``StrOrNone``). The returned list is sorted by
        ``season_end_year`` ascending so the consumer can plot it
        left-to-right.

        On :class:`MissingFixtureError` the helper returns ``[]`` (no
        raise) so the summary still renders.
        """
        try:
            rows = self._run(
                "franchise_history",
                {_TEAM_ABBREVIATION_PARAM: team_identifier},
            )
        except MissingFixtureError:
            return []
        arc: list[FranchiseArcPoint] = []
        for row in rows:
            # The BR rows have a dict-like ``__getitem__`` plus
            # Pydantic attribute access. Try the attribute first
            # (Pydantic path), then fall back to ``[]`` (dict path)
            # so service-level tests can inject plain dicts.
            season_str = _row_get(row, "season")
            end_year = season_end_year(season_str)
            if end_year is None:
                continue
            wins_raw = _row_get(row, "wins")
            losses_raw = _row_get(row, "losses")
            wins = int(wins_raw) if isinstance(wins_raw, (int, float)) else None
            losses = int(losses_raw) if isinstance(losses_raw, (int, float)) else None
            win_pct: float | None = None
            if wins is not None and losses is not None:
                total = wins + losses
                if total > 0:
                    win_pct = wins / total
            team_name_raw = _row_get(row, "team_name")
            team_name = str(team_name_raw) if team_name_raw is not None else None
            arc.append(
                FranchiseArcPoint(
                    season_end_year=end_year,
                    team_name=team_name,
                    wins=wins,
                    losses=losses,
                    win_pct=win_pct,
                )
            )
        arc.sort(key=lambda p: p.season_end_year)
        return arc

    def _team_hero_stats(self, team_identifier: str, season_end_year: int) -> TeamHeroStats:
        """Extract team hero stats from the ``team_misc_four_factors`` row.

        Mirrors :func:`_hero_stats` in
        :mod:`courtside_data.server.service` but pulls from the
        ``TeamMiscFourFactorsRow`` schema (wins / losses / MOV / SRS /
        ratings / pace) instead of the player career row. On any
        failure (including :class:`MissingFixtureError`) returns a
        :class:`TeamHeroStats` instance with ``team`` populated to the
        requested identifier and every other field ``None`` (the
        graceful-empty contract). The closed-type return shape means
        the summary's ``hero_stats`` field never has to be a ``dict``,
        so the UI doesn't have to guard on field presence.
        """
        try:
            rows = self._run(
                "team_misc_four_factors",
                {
                    _TEAM_ABBREVIATION_PARAM: team_identifier,
                    _TEAM_SEASON_PARAM: season_end_year,
                },
            )
        except MissingFixtureError:
            return TeamHeroStats(team=team_identifier)
        for row in reversed(rows):
            payload = row.model_dump(mode="json") if hasattr(row, "model_dump") else dict(row)
            wins_raw = payload.get("wins")
            losses_raw = payload.get("losses")
            wins = int(wins_raw) if isinstance(wins_raw, (int, float)) else None
            losses = int(losses_raw) if isinstance(losses_raw, (int, float)) else None
            win_pct: float | None = None
            if wins is not None and losses is not None:
                total = wins + losses
                if total > 0:
                    win_pct = wins / total
            return TeamHeroStats(
                season=payload.get("season"),
                team=team_identifier,
                wins=wins,
                losses=losses,
                win_pct=win_pct,
                wins_pyth=payload.get("wins_pyth"),
                losses_pyth=payload.get("losses_pyth"),
                mov=payload.get("mov"),
                srs=payload.get("srs"),
                off_rtg=payload.get("off_rtg"),
                def_rtg=payload.get("def_rtg"),
                pace=payload.get("pace"),
            )
        return TeamHeroStats(team=team_identifier)

    @staticmethod
    def _serialize_rows(rows: list[Any]) -> list[dict[str, Any]]:
        return [row.model_dump(mode="json") if hasattr(row, "model_dump") else dict(row) for row in rows]

    # ------------------------------------------------------------ public API
    def search(self, term: str) -> list[TeamSearchResult]:
        """Search the Basketball-Reference search index and return team rows.

        Reuses the player-hub's ``search`` ``EndpointSpec`` (the no-``idx``
        ``/search/search.fcgi?search={term}`` page) and filters the
        resulting :class:`SearchResultRow` stream to entries with the
        ``type == "team"`` discriminator that
        :func:`courtside_data.parsing._rows_search.parse_search_rows_with_stats`
        now stamps on each card. ``teams`` and ``team_seasons`` both
        collapse to ``type="team"`` (the enum doesn't distinguish the
        franchise-level card from the per-season card); the
        dedupe-by-identifier pass below keeps the franchise card and
        discards the per-season cards, because the franchise card
        appears first in source.

        A term shorter than two characters raises
        :class:`courtside_data.errors.InvalidSearch` (mirrors the
        player-hub's :meth:`PlayerHubService.search_players`
        behaviour). A search with no team rows returns ``[]`` (not an
        error) so the UI can render the empty state.
        """
        term = term.strip()
        if len(term) < 2:
            raise InvalidSearch(term)
        rows = self._run("search", {"term": term})
        seen: set[str] = set()
        results: list[TeamSearchResult] = []
        for r in rows:
            type_value = getattr(r, "type", None)
            if type_value is None and isinstance(r, dict):
                type_value = r.get("type")
            if type_value != "team":
                continue
            # Pydantic-BRRow exposes ``__getitem__``; dict rows expose
            # ``[]``; support both so service-level tests can inject
            # plain dicts.
            identifier = str(r["identifier"])
            if identifier in seen:
                continue
            seen.add(identifier)
            leagues_raw = r.get("leagues") if hasattr(r, "get") else r["leagues"]
            if leagues_raw is None:
                leagues: list[str] = []
            elif isinstance(leagues_raw, str):
                leagues = [leagues_raw]
            else:
                leagues = sorted(str(league) for league in leagues_raw)
            results.append(
                TeamSearchResult(
                    name=str(r["name"]),
                    identifier=identifier,
                    leagues=leagues,
                )
            )
        return results

    def summary(self, team_identifier: str) -> TeamHubSummary:
        """Build the Team Hub overview payload.

        Mirrors :meth:`PlayerHubService.summary` but the embedded
        ``roster`` field replaces the player hub's ``career`` field and
        the hero-stats source is :class:`team_misc_four_factors` (wins,
        losses, MOV, SRS, ratings) instead of the player career row.
        """
        # Default season resolution. ``team_roster`` is a ``team_season``
        # endpoint so we MUST pick a season here. The player hub's
        # ``_default_season`` is data-driven (driven by ``career`` rows);
        # the team hub has no equivalent season-discovery path yet
        # (TODO below), so we fall back to the calendar-driven helper
        # in :mod:`courtside_data.domain.seasons`. It anchors the
        # summary on the most-recently-completed or currently-running
        # NBA season (e.g. 2026-06-27 -> 2026; 2026-10-15 -> 2027).
        default_season = current_nba_season_end_year()

        # Roster (embedded) — best-effort. In fixture mode the team
        # fixture transport is intentionally not wired (see
        # :mod:`courtside_data.server.fixtures`), so a
        # :class:`MissingFixtureError` is expected. We catch and return
        # an empty response so the summary still renders (the UI will
        # show the empty state). All other exceptions propagate.
        try:
            roster = self._rows_for_dataset(
                "roster",
                {
                    _TEAM_ABBREVIATION_PARAM: team_identifier,
                    _TEAM_SEASON_PARAM: default_season,
                },
            )
        except MissingFixtureError:
            # TODO(team-hub): wire team fixture transport so the embedded
            # roster call returns real rows in fixture mode.
            #
            # What: the team-hub fixture transport raises
            # :class:`MissingFixtureError` for every team endpoint (see
            # the guard at the bottom of
            # :func:`courtside_data.server.fixtures.fixture_url_map`),
            # so the embedded ``roster`` call in this method always
            # falls through to :meth:`_empty_rows_response`. The
            # ``raw/`` directory already contains captured HTML under
            # ``raw/team_roster/`` (``BOS_2024.html``,
            # ``BOS_1980.html``, etc.) — the fixtures exist on disk
            # but the transport layer doesn't know how to map a
            # ``team_roster`` request to them.
            # Where:
            #   - courtside_data/server/fixtures.py:189
            #     (the :func:`fixture_url_map` guard that raises).
            #   - courtside_data/server/fixtures.py:142
            #     (the :func:`_player_only_map` pattern to mirror for
            #     team-only endpoints; ``raw/<endpoint>/<id>.html``).
            #   - courtside_data/server/fixtures.py:150
            #     (the :func:`_player_season_map` pattern to mirror
            #     for ``team_season`` endpoints;
            #     ``raw/<endpoint>/<id>_<year>.html``).
            #   - raw/team_roster/BOS_2024.html  (a captured fixture
            #     already in the repo; the transport must look here
            #     first).
            # How:
            #   1. Add :func:`_team_only_map` and
            #     :func:`_team_season_map` helpers in
            #     :mod:`courtside_data.server.fixtures` mirroring
            #     ``_player_only_map`` / ``_player_season_map`` (use
            #     ``_TEAM_ABBREVIATION_PARAM`` instead of
            #     ``player_identifier``).
            #   2. Insert two ``if endpoint_name in TEAM_ENDPOINTS``
            #     and ``if endpoint_name in TEAM_SEASON_ENDPOINTS``
            #     branches in :func:`fixture_url_map` BEFORE the
            #     current guard, returning the new helpers' output.
            #   3. For ``team_injury_report`` (league-wide page that
            #     ignores team/season params), special-case the path
            #     to a ``raw/team_injury_report/default.html``
            #     short-circuit (the page ignores
            #     ``team_abbreviation`` and ``season_end_year``).
            #   4. Once the transport is wired, this ``except``
            #     branch becomes a dead path for fixture mode and can
            #     be removed in favour of letting
            #     :class:`MissingFixtureError` propagate (or
            #     narrowed to a single ``except
            #     MissingFixtureError`` if a real fixture-capture
            #     gap is the expected case).
            # Decision needed: whether to keep the
            # graceful-empty fallback once the transport is wired, or
            # to let :class:`MissingFixtureError` bubble up so a
            # missing fixture is loud (404) rather than silent (empty
            # rows). The current behaviour matches the player hub's
            # "best-effort" approach but the player hub actually has
            # fixtures; the team hub currently does not.
            # Verify: with ``raw/team_roster/BOS_2024.html`` already
            #   present and the transport wired,
            #   ``TestClient(create_app(transport='fixture')).get(
            #   '/api/teams/BOS/summary').json()['roster'][
            #   'row_count']`` is > 0 and ``rows[0]['player']`` is
            #   a real Celtics player.
            roster = self._empty_rows_response("roster", default_season)

        # Hero stats — pull wins / losses / MOV / SRS / ratings from the
        # ``team_misc_four_factors`` endpoint for the default season.
        # Best-effort: on any failure (including MissingFixtureError) we
        # return an empty dict and the UI will hide the hero strip.
        hero_stats = self._team_hero_stats(team_identifier, default_season)

        # TODO(team-hub): there is no season-discovery mechanism for
        # teams yet — replace ``[default_season]`` with the union of
        # (a) ``fixture_seasons_for_team(team_identifier)`` and (b) any
        # seasons derived from live-transport probes in
        # :meth:`summary`.
        #
        # What: walk the ``raw/`` directory per (team, dataset,
        # season) triple and surface every season the team has
        # captured fixtures for, sorted newest-first.
        # Where:
        #   - courtside_data/server/fixtures.py:232  (the player-hub
        #     reference implementation ``fixture_seasons_for_player``;
        #     globs ``raw/<endpoint>/<player>_*.html`` and returns
        #     ``{endpoint_name: [season, ...]}``).
        #   - courtside_data/server/team_service.py:359  (this block,
        #     currently hard-coded ``[default_season]``).
        #   - raw/team_roster/BOS_2024.html  (and the other captured
        #     ``BOS_<year>.html`` files — the walker must glob
        #     ``raw/team_roster/BOS_*.html`` and parse the
        #     ``<year>`` segment the same way the player walker does).
        # How:
        #   1. Add ``fixture_seasons_for_team(team_identifier,
        #     raw_root=None) -> dict[str, list[int]]`` to
        #     :mod:`courtside_data.server.fixtures`. Mirror
        #     ``fixture_seasons_for_player`` line-for-line; the
        #     only differences are: glob pattern is
        #     ``raw/<endpoint>/<team>_*.html`` and the prefix-strip
        #     uses the team identifier.
        #   2. Call it in this method when
        #     ``self.transport == "fixture"`` (the player hub
        #     only uses it in fixture mode too) and union the
        #     values with the live-probed seasons.
        #   3. Set ``available_seasons = sorted(set(
        #     seasons_from_fixtures) | set(seasons_from_live) | {
        #     default_season }, reverse=True)``.
        # Decision needed: live-mode discovery. The player hub
        # doesn't probe live because every player endpoint either
        # has data for every season (career) or is unreachable
        # without a season (splits). The team-hub is similar
        # (no team-hub endpoint is "all seasons for one team"
        # except ``franchise_history``), so live-mode discovery
        # can stay a no-op until a product need appears.
        # Verify (fixture): capture ``raw/team_roster/BOS_2024.html``
        #   and ``raw/team_roster/BOS_2023.html``, then
        #   ``fixture_seasons_for_team("BOS")["team_roster"]`` ==
        #   ``[2024, 2023]``, and
        #   ``TeamHubService(transport='fixture').summary('BOS')[
        #   'available_seasons']`` contains both.
        available_seasons = [default_season]

        # TODO(team-hub): populate ``season_dataset_availability``
        # once ``fixture_seasons_for_team`` (see the TODO above) is
        # wired.
        #
        # What: surface, for each ``team_season``-scope dataset, the
        # list of seasons that have a captured fixture for this
        # team. The shape is ``{dataset_id: [season, ...]}`` (the
        # same shape :func:`courtside_data.server.service.
        # _dataset_availability_by_dataset_id` returns — see
        # ``courtside_data/server/service.py:182`` for the player-hub
        # equivalent).
        # Where:
        #   - courtside_data/server/service.py:182
        #     (the player-hub helper
        #     ``_dataset_availability_by_dataset_id`` that maps
        #     the per-endpoint season map to a per-dataset-id map).
        #   - courtside_data/server/team_service.py:381  (this block,
        #     currently hard-codes ``[default_season]`` for every
        #     team-season dataset).
        #   - courtside_data/server/team_models.py:78
        #     (the :attr:`TeamHubSummary.season_dataset_availability`
        #     field, ``dict[str, list[int]]``).
        # How:
        #   1. Call the new ``fixture_seasons_for_team`` helper to
        #     get a ``{endpoint_name: [season, ...]}`` map.
        #   2. Iterate ``TEAM_DATASETS`` (this module's
        #     :data:`TEAM_DATASETS` tuple). For every
        #     ``scope == "team_season"`` entry, look up
        #     ``endpoint_name -> seasons`` and assign
        #     ``season_dataset_availability[dataset.id] =
        #     sorted(seasons, reverse=True)``.
        #   3. For datasets with no captured fixtures, fall back to
        #     ``[default_season]`` so the season selector still
        #     renders (matches the current "render the empty
        #     state" pattern).
        # Decision needed: whether the ``default_season`` fallback
        # should be omitted (leaving the list empty and forcing the
        # UI to show "no seasons available") for parity with the
        # "loud failure" preference in the search/hero-stats TODOs.
        # The current behaviour is the "graceful empty state"
        # choice.
        # Verify (fixture): capture
        #   ``raw/team_roster/BOS_2024.html``,
        #   ``raw/team_roster/BOS_2023.html``,
        #   ``raw/team_splits/BOS_2024.html``; assert
        #   ``TeamHubService(transport='fixture').summary('BOS')[
        #   'season_dataset_availability']`` is
        #   ``{"roster": [2024, 2023], "splits": [2024],
        #   "and-opponent": [2024], ...}``.
        season_dataset_availability: dict[str, list[int]] = {}
        for dataset in TEAM_DATASETS:
            if dataset.scope == "team_season":
                season_dataset_availability[dataset.id] = [default_season]

        return TeamHubSummary(
            identifier=team_identifier,
            display_name=TEAM_DISPLAY_NAMES.get(team_identifier, team_identifier),
            leagues=["NBA"],
            default_season=default_season,
            available_seasons=available_seasons,
            hero_stats=hero_stats,
            roster=roster,
            season_dataset_availability=season_dataset_availability,
            franchise_arc=self._franchise_arc(team_identifier),
            transport=self.transport,
        )

    def dataset(self, team_identifier: str, dataset_id: str) -> EndpointRowsResponse:
        """Run a ``scope == "team"`` dataset and shape the response.

        Mirrors :meth:`PlayerHubService.rows_for_dataset` for the player
        hub's ``scope == "player"`` path. The current scaffolding routes
        only team-scope datasets (no season in the URL); season-scope
        callers must go through :meth:`season_dataset`.
        """
        dataset = team_dataset_by_id(dataset_id)
        if dataset.scope != "team":
            raise ValueError(f"Dataset {dataset_id!r} requires /seasons/{{season_end_year}}")
        params = self._build_params(
            dataset.endpoint_name,
            team_identifier=team_identifier,
        )
        rows = self._serialize_rows(self._fetch(dataset.endpoint_name, team_identifier=team_identifier))
        columns = team_columns_for_dataset(dataset, rows[0] if rows else None)
        return EndpointRowsResponse(
            dataset=dataset.id,
            endpoint_name=dataset.endpoint_name,
            params=params,
            row_count=len(rows),
            columns=columns,
            default_visible_columns=list(dataset.default_visible_columns),
            rows=rows,
            transport=self.transport,
        )

    def season_dataset(
        self,
        team_identifier: str,
        season_end_year: int,
        dataset_id: str,
        include_inactive_games: bool,
    ) -> EndpointRowsResponse:
        """Run a ``scope == "team_season"`` dataset and shape the response.

        Mirrors :meth:`dataset` but passes the season (and optional
        include-inactive flag) through to the endpoint.
        """
        dataset = team_dataset_by_id(dataset_id)
        if dataset.scope != "team_season":
            raise ValueError(f"Dataset {dataset_id!r} does not require a season")
        params = self._build_params(
            dataset.endpoint_name,
            team_identifier=team_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )
        rows = self._serialize_rows(
            self._fetch(
                dataset.endpoint_name,
                team_identifier=team_identifier,
                season_end_year=season_end_year,
                include_inactive_games=include_inactive_games,
            )
        )
        columns = team_columns_for_dataset(dataset, rows[0] if rows else None)
        return EndpointRowsResponse(
            dataset=dataset.id,
            endpoint_name=dataset.endpoint_name,
            params=params,
            row_count=len(rows),
            columns=columns,
            default_visible_columns=list(dataset.default_visible_columns),
            rows=rows,
            transport=self.transport,
        )

    def csv(
        self,
        team_identifier: str,
        dataset_id: str,
        season_end_year: int | None,
        include_inactive_games: bool,
    ) -> str:
        """Serialize a Team Hub dataset to CSV.

        Mirrors :meth:`PlayerHubService.csv_for_dataset`. The column
        contract is the endpoint's :attr:`csv_columns` (declared on the
        ``EndpointSpec`` in :mod:`courtside_data.endpoints._teams`),
        which gives a stable export order across hubs.
        """
        # The CSV column-ordering contract is enforced by
        # ``tests/server/test_team_hub_csv.py::test_csv_header_matches_endpoint_spec_csv_columns``
        # (parametrized over :data:`TEAM_DATASETS`). For every team
        # endpoint with a non-empty ``csv_columns`` sequence, the
        # header row of this method's output MUST equal
        # ``list(spec.csv_columns)``. The test deliberately feeds a
        # row with keys in reversed order to catch any silent
        # fallback to ``rows[0].keys()`` (the unstable path that
        # mirrors the player hub's ``search`` spec comment in
        # :mod:`courtside_data.endpoints._workflows`).
        #
        # What: today the fieldname list is taken from
        # ``EndpointSpec.csv_columns`` when it is set (all 13 team
        # endpoints declare a ``csv_columns`` sequence in
        # :mod:`courtside_data.endpoints._teams`), with a row-key
        # fallback (``rows[0].keys()``) for the rare case where the
        # spec omits ``csv_columns`` (compare with the player hub's
        # ``search`` spec, which deliberately omits it per the
        # comment in :mod:`courtside_data.endpoints._workflows`:
        # "csv_columns omitted - auto-detected from data so empty
        # columns are stripped"). The fallback's order is
        # dictionary-insertion order from the Pydantic model, which
        # is **not** stable across Python versions or row payloads.
        # Where:
        #   - courtside_data/server/service.py:127
        #     (the player-hub :meth:`PlayerHubService.csv_for_dataset`;
        #     uses :attr:`EndpointRowsResponse.columns` from
        #     :meth:`rows_for_dataset` instead of
        #     ``EndpointSpec.csv_columns`` — its fieldnames are
        #     always ``[column.key for column in
        #     response.columns]``).
        #   - courtside_data/server/team_service.py:482  (the
        #     ``fieldnames = ...`` line in this method).
        #   - courtside_data/endpoints/_teams.py  (the 13 team
        #     EndpointSpec ``csv_columns=`` declarations; all are
        #     set today, but a future addition without one would
        #     silently hit the unstable fallback).
        # How:
        #   1. Mirror the player-hub path: use
        #     ``EndpointRowsResponse.columns`` (built by
        #     :func:`courtside_data.server.team_catalog.
        #     team_columns_for_dataset`) as the fieldname source.
        #     That gives a stable, Pydantic-declared order
        #     independent of the row payload.
        #   2. Drop the ``rows[0].keys()`` fallback (return an
        #     empty CSV with just a header row if there are no
        #     rows AND no ``csv_columns`` — the route's
        #     ``Content-Disposition`` still produces a valid
        #     download).
        #   3. Keep the ``EndpointSpec.csv_columns`` short-circuit
        #     for endpoints whose declared column order diverges
        #     from the Pydantic model (e.g. ``team_opponent_stats``
        #     which projects only the opponent columns of
        #     ``team_and_opponent``).
        # Decision needed: none — this is a stability/clean-up
        # change, not a behaviour change. The CSV files produced
        # today are already correct for endpoints with
        # ``csv_columns``; the only risk is for the no-data + no
        # spec fallback, which currently produces a header-less
        # empty file.
        dataset = team_dataset_by_id(dataset_id)
        endpoint = ENDPOINTS[dataset.endpoint_name]
        params = self._build_params(
            dataset.endpoint_name,
            team_identifier=team_identifier,
            season_end_year=season_end_year,
            include_inactive_games=(include_inactive_games if dataset.scope == "team_season" else None),
        )
        rows = self._serialize_rows(self._run(dataset.endpoint_name, params))
        fieldnames = list(endpoint.csv_columns) if endpoint.csv_columns else list(rows[0].keys()) if rows else []
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()


__all__ = [
    "TEAM_DATASETS",
    "TeamHubService",
]
