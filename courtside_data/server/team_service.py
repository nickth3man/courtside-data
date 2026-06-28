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
from courtside_data.endpoints import ENDPOINTS
from courtside_data.server.catalog import columns_for_dataset
from courtside_data.server.fixtures import MissingFixtureError, build_fixture_service
from courtside_data.server.models import EndpointRowsResponse, TransportMode
from courtside_data.server.team_catalog import (
    TEAM_DATASETS,
    team_columns_for_dataset,
    team_dataset_by_id,
)
from courtside_data.server.team_models import TeamHubSummary, TeamSearchResult

# Team endpoints are parametrised by ``team_abbreviation`` (and, for most,
# ``season_end_year``) per ``courtside_data.endpoints._table._team``. The
# public API uses ``team_identifier`` as the user-facing path param to
# mirror the player hub's ``player_identifier``; the service maps it onto
# the endpoint's actual param names at call time.
_TEAM_ABBREVIATION_PARAM = "team_abbreviation"
_TEAM_SEASON_PARAM = "season_end_year"
_TEAM_INCLUDE_INACTIVE_PARAM = "include_inactive_games"

# Default season used by the summary endpoint when no explicit season is
# provided by the caller. Mirrors the hard-coded ``_default_season`` policy
# in :mod:`courtside_data.server.service` (which also pins 2024 as the
# "default unless the data tells us otherwise"). ``_default_season`` there
# operates on a list of discovered seasons; for teams we don't yet have a
# season-discovery path (see TODO on :meth:`TeamHubService.summary`) so
# we ship a single hard-coded anchor for now.
#
# TODO(team-hub): replace the hard-coded ``_TEAM_DEFAULT_SEASON`` with a
# data-driven resolver.
#
# What: pick the "current NBA season" (an integer ``season_end_year``)
# from the current calendar date so the summary lands on the most
# recently completed season instead of a stale 2024.
# Where:
#   - courtside_data/server/service.py:157  (_default_season — the player
#     hub's existing resolver; it takes a list of available seasons and
#     returns the max, so it is NOT a drop-in replacement — it still
#     needs an upstream season-discovery step to populate that list).
#   - courtside_data/server/team_service.py:323  (where this constant
#     is consumed by :meth:`TeamHubService.summary`).
# How:
#   1. Define a ``_current_nba_season(today: date) -> int`` helper: the
#      NBA regular season that starts in fall of year ``Y-1`` ends in
#      spring of year ``Y`` (``season_end_year == Y``). The cutoff is
#      October 1 of ``Y-1`` (training-camp start): for a ``today`` on
#      or after that date, return ``today.year + 1``; otherwise return
#      ``today.year``. Example: 2026-06-27 -> 2026 (the 2025-26 season
#      ended in spring 2026); 2026-09-15 -> 2027 (the 2026-27 season
#      has just started training camp).
#   2. Optionally union it with the per-dataset seasons returned by
#      ``fixture_seasons_for_team`` (see the TODO on
#      :meth:`TeamHubService.summary`'s ``available_seasons`` block) and
#      fall back to the constant if the walker returns no data.
# Decision needed: whether to use the calendar helper in ``live``
# transport and the fixture walker in ``fixture`` transport, or always
# prefer the more-specific source. The existing player hub uses
# "fixtures-or-data" union; mirroring that is the lowest-risk path.
# Verify: ``uv run python -c "from datetime import date; from
#   courtside_data.server.team_service import _current_nba_season; print(
#   _current_nba_season(date(2026, 6, 27)), _current_nba_season(date(
#   2026, 9, 15)), _current_nba_season(date(2026, 1, 5)))"`` -> 2026
#   2027 2026.
_TEAM_DEFAULT_SEASON = 2024

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
                    # TODO(team-hub): this branch is reachable only from
                    # callers that omitted a season for a
                    # ``team_season``-scope endpoint. After the scope
                    # reclassification in :mod:`courtside_data.server.
                    # team_catalog`, the only team-scope (no-season)
                    # datasets are ``contracts`` and ``franchise_history``;
                    # the season_dataset route and the CSV export route
                    # both pass ``season_end_year`` explicitly, so this
                    # raise is the safety net for direct service calls
                    # that bypass the route layer.
                    #
                    # What: wire a single shared default-season resolver
                    # so the summary() embedded roster call (and any
                    # other direct caller) can fall back to
                    # :data:`_TEAM_DEFAULT_SEASON` (or its data-driven
                    # replacement) without each call site re-deriving
                    # it.
                    # Where:
                    #   - courtside_data/server/team_service.py:323
                    #     (the :meth:`TeamHubService.summary` default
                    #     season — already passes the constant).
                    #   - courtside_data/server/team_service.py:470
                    #     (the :meth:`TeamHubService.csv` call site
                    #     that currently raises when season is None).
                    # How:
                    #   1. Change this branch to assign
                    #     ``params[name] = _resolve_default_season()``
                    #     instead of raising.
                    #   2. Make :meth:`TeamHubService.csv` pass
                    #     ``season_end_year=`` directly (or
                    #     ``_resolve_default_season()``) instead of
                    #     relying on this raise to flag a bad request.
                    # Decision needed: the team CSV export route
                    # (``/api/teams/{id}/export?dataset=roster`` without
                    # a ``season_end_year``) currently maps this
                    # ``ValueError`` to ``400 bad_request``; if the
                    # default-season resolver silently fills in a
                    # season, the export will succeed for any dataset,
                    # which may surprise users. Keep the raise for the
                    # route layer; resolve only inside the service when
                    # the caller is summary().
                    # Verify: ``TestClient(create_app(transport=
                    #   'fixture')).get('/api/teams/BOS/summary').
                    #   status_code == 200`` and the same call's
                    #   ``.json()['default_season']`` matches the
                    #   resolver's output.
                    raise ValueError(
                        f"Endpoint {endpoint_name!r} requires season_end_year; "
                        "team_service._build_params has no default-season resolver yet"
                    )
                params[name] = season_end_year
            elif name == _TEAM_INCLUDE_INACTIVE_PARAM:
                params[name] = bool(include_inactive_games) if include_inactive_games is not None else False
            else:
                # TODO(team-hub): extend the param-name mapping when
                # wiring a team endpoint that declares a custom param
                # not covered by ``_TEAM_ABBREVIATION_PARAM`` /
                # ``_TEAM_SEASON_PARAM`` / ``_TEAM_INCLUDE_INACTIVE_PARAM``.
                #
                # What: teach :meth:`TeamHubService._build_params` about
                # the new param. Today every team endpoint in
                # ``courtside_data.endpoints._teams`` uses the default
                # ``_team(...)`` param tuple
                # ``("team_abbreviation", "season_end_year")`` except
                # ``team_contracts`` and ``franchise_history`` which
                # override to ``("team_abbreviation",)``. No current
                # team endpoint declares ``include_inactive_games`` in
                # its spec — that branch exists for forward-compat with
                # future team-box-score endpoints.
                # Where:
                #   - courtside_data/endpoints/_teams.py  (the 13
                #     ``TEAM_ENDPOINTS`` specs; check ``spec.params``
                #     before adding a new branch here).
                #   - courtside_data/endpoints/_table.py:170
                #     (the ``_team`` helper that defines the default
                #     param tuple).
                # How:
                #   1. Inspect ``ENDPOINTS[endpoint_name].params`` and
                #     add a new ``elif name == "<param>":`` branch
                #     that pulls the value from a new public kwarg on
                #     :meth:`TeamHubService._build_params`.
                #   2. If the param is read-only or transport-side
                #     (e.g. a per-call ``include_inactive_games``-style
                #     flag), wire it through the ``_fetch`` /
                #     ``_run`` private helpers and the public
                #     ``dataset`` / ``season_dataset`` / ``csv``
                #     methods that already accept such flags.
                # Decision needed: should the service auto-derive
                # unknown params from a fixed set of public kwargs, or
                # should :meth:`_build_params` take a ``**extra_params``
                # bag that gets forwarded verbatim? The former keeps
                # the public surface narrow; the latter is faster to
                # extend.
                # Verify: add a new team endpoint with a custom param
                #   to ``_teams.py``, register a fixture, and confirm
                #   ``TeamHubService(...).dataset(team_id,
                #   new_dataset_id)`` returns the expected rows.
                raise NotImplementedError(
                    f"team_service._build_params: endpoint {endpoint_name!r} has unhandled param {name!r}; "
                    f"see courtside_data.endpoints.ENDPOINTS[{endpoint_name!r}].params"
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

    def _team_hero_stats(self, team_identifier: str, season_end_year: int) -> dict[str, Any]:
        """Extract team hero stats from the ``team_misc_four_factors`` row.

        Mirrors :func:`_hero_stats` in
        :mod:`courtside_data.server.service` but pulls from the
        ``TeamMiscFourFactorsRow`` schema (wins / losses / MOV / SRS /
        ratings / pace) instead of the player career row. Returns ``{}``
        on any failure (including :class:`MissingFixtureError`) so the
        summary can still render.
        """
        # TODO(team-hub): confirm and stabilise the hero-stats source
        # and the contract with the team-hub UI.
        #
        # What: the team-hub UI ``overview`` component consumes
        # ``wins``, ``losses``, and ``win_pct`` from ``hero_stats``
        # (the three keys the player-hub UI surfaces in its
        # overview). The current implementation already emits those
        # three, plus a basket of secondary keys (``wins_pyth``,
        # ``losses_pyth``, ``mov``, ``srs``, ``off_rtg``, ``def_rtg``,
        # ``pace``, ``season``, ``team``) that the player hub's hero
        # strip doesn't carry. This implementation may be over-emitting;
        # the field set needs product sign-off.
        # Where:
        #   - courtside_data/schemas/teams.py:62
        #     (``TeamMiscFourFactorsRow``; the source row model that
        #     supplies ``wins`` / ``losses`` / ``srs`` / ``mov`` /
        #     ``off_rtg`` / ``def_rtg`` / ``pace``).
        #   - courtside_data/endpoints/_teams.py:75 (the
        #     ``team_misc_four_factors`` EndpointSpec — the ``path``
        #     is the same ``/teams/{abbr}/{season}.html`` page the
        #     ``and-opponent`` and ``opponent-stats`` endpoints hit,
        #     only the parsed table differs).
        #   - ui/src/features/team-hub/components/overview.tsx (the UI
        #     consumer; cannot be read from this lane but is the source
        #     of truth for which keys are required).
        # How:
        #   1. Read the team-hub overview component and reconcile its
        #     ``heroStats`` / ``hero_stats`` access pattern with the
        #     keys emitted here. Trim the secondary keys if the UI
        #     doesn't render them.
        #   2. If the UI needs a "franchise totals" or "playoff
        #     record" key, source it from ``franchise_history``
        #     (``FranchiseHistoryRow`` at
        #     ``courtside_data/schemas/teams.py:286``) or
        #     ``team_schedule`` (which exposes ``wins`` / ``losses``
        #     in ``courtside_data/schemas/schedule.py:44-45``) and
        #     merge the keys into the dict returned here.
        # Decision needed: (a) keep the graceful-empty ``{}`` fallback
        # (current behaviour) so a missing fixture is a no-op for the
        # UI, or (b) raise so the UI surfaces a clear "data
        # unavailable" state. (a) is the current behaviour and
        # matches the player hub's empty-row fallback in
        # :func:`courtside_data.server.service._hero_stats`; (b) is
        # more honest but breaks the summary in fixture mode.
        # Verify: with a captured
        # ``raw/team_misc_four_factors/BOS_2024.html`` fixture,
        # ``TeamHubService(transport='fixture').summary('BOS')[
        # 'hero_stats']`` should contain ``wins``, ``losses``,
        # ``win_pct``, plus the secondary keys documented above; the
        # values should match what the raw HTML's ``#team_misc``
        # table renders (sanity-check against the page in a browser).
        try:
            rows = self._run(
                "team_misc_four_factors",
                {
                    _TEAM_ABBREVIATION_PARAM: team_identifier,
                    _TEAM_SEASON_PARAM: season_end_year,
                },
            )
        except MissingFixtureError:
            return {}
        for row in reversed(rows):
            payload = row.model_dump(mode="json") if hasattr(row, "model_dump") else dict(row)
            wins_raw = payload.get("wins")
            losses_raw = payload.get("losses")
            wins = int(wins_raw) if isinstance(wins_raw, (int, float)) and wins_raw is not None else None
            losses = int(losses_raw) if isinstance(losses_raw, (int, float)) and losses_raw is not None else None
            win_pct: float | None = None
            if wins is not None and losses is not None:
                total = wins + losses
                if total > 0:
                    win_pct = wins / total
            return {
                "season": payload.get("season"),
                "team": team_identifier,
                "wins": wins,
                "losses": losses,
                "win_pct": win_pct,
                "wins_pyth": payload.get("wins_pyth"),
                "losses_pyth": payload.get("losses_pyth"),
                "mov": payload.get("mov"),
                "srs": payload.get("srs"),
                "off_rtg": payload.get("off_rtg"),
                "def_rtg": payload.get("def_rtg"),
                "pace": payload.get("pace"),
            }
        return {}

    @staticmethod
    def _serialize_rows(rows: list[Any]) -> list[dict[str, Any]]:
        return [row.model_dump(mode="json") if hasattr(row, "model_dump") else dict(row) for row in rows]

    # ------------------------------------------------------------ public API
    def search(self, term: str) -> list[TeamSearchResult]:
        # TODO(team-hub): wire team search end-to-end.
        #
        # What: implement :meth:`TeamHubService.search` so that
        # ``GET /api/teams/search?term=…`` returns a list of
        # :class:`TeamSearchResult` (``name`` / ``identifier`` /
        # ``leagues``) for matching team abbreviations. The current
        # search :class:`EndpointSpec` in
        # ``courtside_data/endpoints/_workflows.py:794`` is the
        # Basketball-Reference ``/search/search.fcgi?search=…`` endpoint
        # but its ``row_model`` is :class:`SearchResultRow` at
        # ``courtside_data/schemas/search.py:50`` whose fields are
        # ``name`` (``str``), ``identifier`` (``str``), ``leagues``
        # (``LeaguesField``) — there is **no** ``type`` or ``kind``
        # discriminator, so we cannot filter to team rows from the
        # existing data alone.
        # Where:
        #   - courtside_data/endpoints/_workflows.py:794  (the
        #     ``search`` EndpointSpec; ``path=``/search/search.fcgi
        #     ?search={term}``, ``params=("term",)``,
        #     ``row_model=SearchResultRow``,
        #     ``metadata.scope=EndpointScope.SEARCH``,
        #     ``metadata.kind=EndpointKind.WORKFLOW``,
        #     ``workflow=_SEARCH_WORKFLOW``).
        #   - courtside_data/schemas/search.py:50  (``SearchResultRow``
        #     fields ``name`` / ``identifier`` / ``leagues``).
        #   - courtside_data/endpoints/_workflows.py:_SEARCH_WORKFLOW
        #     (the workflow executor that normalises the
        #     div-based search listing into ``SearchResultRow``; this
        #     is what strips the team results today).
        #   - courtside_data/server/team_service.py:287  (this method).
        # How (two viable options — see Decision needed):
        #
        #   Option A — discriminator on SearchResultRow (cheapest):
        #     1. Add ``type: Literal["player", "team", "coach", ...]``
        #        to :class:`SearchResultRow` in
        #        ``courtside_data/schemas/search.py`` (default
        #        ``"player"`` for back-compat).
        #     2. Populate ``type`` in the workflow's
        #        ``_SEARCH_WORKFLOW`` result-mapping step (look at the
        #        result container's CSS class — basketball-reference
        #        wraps each result card in a div with a
        #        ``"search-item"`` + ``"search-item-N"`` block whose
        #        first anchor's ``/teams/`` vs ``/players/`` prefix
        #        disambiguates).
        #     3. Implement this method by calling ``self._run(
        #        "search", {"term": term})`` and filtering the rows
        #        to only those with ``r.get("type") == "team"``,
        #        mapping each remaining row to a
        #        :class:`TeamSearchResult` (name / identifier /
        #        leagues).
        #     4. If the workflow doesn't yet emit ``type``, the filter
        #        returns ``[]`` and the route degrades to "no results"
        #        (not an error), which is the safe default.
        #
        #   Option B — dedicated team_search EndpointSpec (purest):
        #     1. Add a new entry to ``TEAM_ENDPOINTS`` in
        #        ``courtside_data/endpoints/_teams.py`` with a
        #        team-only path. Basketball-Reference's team search
        #        lives at the same ``/search/search.fcgi?search=…``
        #        URL but the workflow currently only paginates
        #        ``players`` / ``wnba_players`` / ``intl_players`` /
        #        ``nbdl_players`` / ``sup_players`` (see the
        #        ``_search_map`` helper in
        #        ``courtside_data/server/fixtures.py:168``). The team
        #        search would need either a new workflow step that
        #        paginates a ``teams`` index, or a separate request
        #        URL like ``/search/search.fcgi?search=…&idx=teams``
        #        (verify the actual parameter against a live capture;
        #        basketball-reference has shipped several search-index
        #        names over the years).
        #     2. Add a corresponding ``TeamSearchResultRow` schema in
        #        a new ``courtside_data/schemas/teams.py` block and
        #        ``register("team_search", …)``.
        #     3. Implement this method as
        #        ``rows = self._run("team_search", {"term": term});
        #        return [TeamSearchResult(...) for row in rows]``.
        #     4. Add a ``_search_team_map`` helper to
        #        ``courtside_data/server/fixtures.py` mirroring
        #        ``_search_map`` but pointing at
        #        ``raw/team_search/{term}.html``.
        # Decision needed: Option A is one-line schema change + one
        # workflow tweak; Option B is a new spec end-to-end. The
        # player hub will also benefit from Option A (the
        # coach/manager search results are silently dropped today),
        # so Option A is the recommended path unless a separate
        # team-search URL is a product requirement.
        # Verify (Option A): capture a ``raw/search/celtics.html``
        # fixture containing the team results, then
        # ``TestClient(create_app(transport='fixture')).get(
        # '/api/teams/search', params={'term': 'celtics'}).json()``
        # returns ``[{"name": "Boston Celtics", "identifier": "BOS",
        # "leagues": ["NBA"]}, ...]``.
        # Verify (Option B): same as Option A but assert
        # ``/api/teams/search`` hits the new spec and not the player
        # ``search`` spec (check the trace envelope's
        # ``endpoint_name`` is ``"team_search"``).
        raise NotImplementedError(
            "TODO(team-hub): team search is not wired — `search` EndpointSpec "
            "is player-only (see courtside_data/schemas/search.py:50). Need "
            "a team_search spec or a `type` discriminator on SearchResultRow."
        )

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
        # (TODO below), so we fall back to a single hard-coded anchor.
        default_season = _TEAM_DEFAULT_SEASON

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
            default_season=default_season,
            available_seasons=available_seasons,
            hero_stats=hero_stats,
            roster=roster,
            season_dataset_availability=season_dataset_availability,
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
        # TODO(team-hub): stabilise the CSV column-ordering contract.
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
        # Verify: snapshot the current CSV output of
        #   ``TestClient(create_app(transport='fixture')).get(
        #   '/api/teams/BOS/seasons/2024/roster.csv')`` (after
        #   capturing ``raw/team_roster/BOS_2024.html``) and
        #   confirm the header row matches
        #   ``TEAM_ROSTER_COLUMN_NAMES`` byte-for-byte; the row
        #   order should also match.
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


# Re-export ``columns_for_dataset`` under a team-friendly name so callers
# who only depend on ``team_service`` can reach the player-hub column helper
# for shared column shapes (currently unused, but kept for symmetry with
# future cross-hub column work).
team_columns = columns_for_dataset


__all__ = [
    "TEAM_DATASETS",
    "TeamHubService",
]
