"""FastAPI application for the optional Courtside Data Player Hub."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from courtside_data.errors import (
    InvalidPlayer,
    InvalidPlayerAndSeason,
    InvalidSearch,
    InvalidSeason,
    RateLimitJailed,
    SchemaDriftError,
)
from courtside_data.server.catalog import DATASETS, dataset_by_id, player_hub_catalog
from courtside_data.server.fixtures import MissingFixtureError, default_raw_root
from courtside_data.server.models import (
    ApiError,
    EndpointRowsResponse,
    PlayerHubSummary,
    PlayerSearchResult,
    StatusResponse,
    TransportMode,
)
from courtside_data.server.service import PlayerHubService, endpoint_count
from courtside_data.server.team_catalog import (
    team_dataset_by_id,
    team_hub_catalog,
)
from courtside_data.server.team_models import TeamHubSummary, TeamSearchResult
from courtside_data.server.team_service import TeamHubService


def _service_from_app(request: Request) -> PlayerHubService:
    return request.app.state.player_hub_service


def _team_service_from_app(request: Request) -> TeamHubService:
    return request.app.state.team_hub_service


ServiceDep = Annotated[PlayerHubService, Depends(_service_from_app)]
TeamServiceDep = Annotated[TeamHubService, Depends(_team_service_from_app)]


def _api_error(status_code: int, code: str, message: str, **detail: Any) -> HTTPException:
    payload = ApiError(code=code, message=message, detail=detail)
    return HTTPException(status_code=status_code, detail=payload.model_dump())


def _map_exception(error: Exception) -> HTTPException:
    if isinstance(error, MissingFixtureError):
        return _api_error(404, "missing_fixture", str(error))
    if isinstance(error, InvalidSearch):
        return _api_error(400, "invalid_search", str(error))
    if isinstance(error, (InvalidPlayer, InvalidPlayerAndSeason)):
        return _api_error(404, "invalid_player", str(error))
    if isinstance(error, InvalidSeason):
        return _api_error(404, "invalid_season", str(error))
    if isinstance(error, RateLimitJailed):
        return _api_error(429, "rate_limit_jailed", str(error), retry_after=error.retry_after)
    if isinstance(error, SchemaDriftError):
        return _api_error(
            500,
            "schema_drift",
            str(error),
            endpoint_name=error.endpoint_name,
            url=error.url,
            pydantic_errors=error.pydantic_errors,
        )
    if isinstance(error, (ValueError, ValidationError)):
        return _api_error(400, "bad_request", str(error))
    return _api_error(500, "internal_error", str(error), error_type=type(error).__name__)


def create_app(*, transport: TransportMode = "fixture", raw_root: Path | None = None) -> FastAPI:
    """Create the Player Hub FastAPI application."""

    app = FastAPI(
        title="Courtside Data Player Hub API",
        version="0.1.0",
        responses={
            400: {"model": ApiError},
            404: {"model": ApiError},
            429: {"model": ApiError},
            500: {"model": ApiError},
        },
    )
    app.state.player_hub_service = PlayerHubService(transport=transport, raw_root=raw_root)
    app.state.team_hub_service = TeamHubService(transport=transport, raw_root=raw_root)
    app.state.transport = transport
    app.state.raw_root = raw_root or default_raw_root()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/api/status", response_model=StatusResponse)
    def status(request: Request) -> StatusResponse:
        fixture_root: Path = request.app.state.raw_root
        return StatusResponse(
            ok=True,
            transport=request.app.state.transport,
            endpoint_count=endpoint_count(),
            fixture_root=str(fixture_root),
            fixture_root_exists=fixture_root.exists(),
        )

    @app.get("/api/endpoints/player-hub")
    def catalog() -> dict[str, object]:
        return player_hub_catalog()

    @app.get("/api/players/search", response_model=list[PlayerSearchResult])
    def player_search(
        term: Annotated[str, Query()],
        service: ServiceDep,
    ) -> list[PlayerSearchResult]:
        try:
            return service.search_players(term)
        except Exception as error:
            raise _map_exception(error) from error

    @app.get("/api/players/{player_identifier}/summary", response_model=PlayerHubSummary)
    def player_summary(
        player_identifier: str,
        service: ServiceDep,
    ) -> PlayerHubSummary:
        try:
            return service.summary(player_identifier)
        except Exception as error:
            raise _map_exception(error) from error

    @app.get("/api/players/{player_identifier}/export")
    def export_dataset(
        player_identifier: str,
        dataset: str,
        service: ServiceDep,
        season_end_year: int | None = None,
        include_inactive_games: bool = False,
    ) -> Response:
        try:
            params = _params_for_dataset(dataset, player_identifier, season_end_year, include_inactive_games)
            csv_text = service.csv_for_dataset(dataset, params)
        except Exception as error:
            raise _map_exception(error) from error
        filename = f"{player_identifier}-{dataset}.csv"
        return Response(
            csv_text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.get(
        "/api/players/{player_identifier}/seasons/{season_end_year}/{dataset}",
        response_model=EndpointRowsResponse,
    )
    def season_dataset(
        player_identifier: str,
        season_end_year: int,
        dataset: str,
        service: ServiceDep,
        include_inactive_games: bool = False,
    ) -> EndpointRowsResponse:
        try:
            dataset_meta = dataset_by_id(dataset)
            if dataset_meta.scope != "season":
                raise ValueError(f"Dataset {dataset!r} does not require a season")
            return service.rows_for_dataset(
                dataset,
                _params_for_dataset(dataset, player_identifier, season_end_year, include_inactive_games),
            )
        except Exception as error:
            raise _map_exception(error) from error

    @app.get("/api/players/{player_identifier}/{dataset}", response_model=EndpointRowsResponse)
    def player_dataset(
        player_identifier: str,
        dataset: str,
        service: ServiceDep,
    ) -> EndpointRowsResponse:
        try:
            dataset_meta = dataset_by_id(dataset)
            if dataset_meta.scope != "player":
                raise ValueError(f"Dataset {dataset!r} requires /seasons/{{season_end_year}}")
            return service.rows_for_dataset(dataset, {"player_identifier": player_identifier})
        except Exception as error:
            raise _map_exception(error) from error

    # --------------------------------------------------------------- Team Hub

    # Shared error-response map for the Team Hub routes. Mirrors the
    # FastAPI app-level ``responses={400, 404, 429, 500: ApiError}`` block
    # declared on the app instance, but exposed per-route so the OpenAPI
    # spec for each team endpoint advertises the same error contract as
    # the player hub.
    _TEAM_ERROR_RESPONSES: dict[int | str, dict[str, type[ApiError]]] = {
        400: {"model": ApiError},
        404: {"model": ApiError},
        429: {"model": ApiError},
        500: {"model": ApiError},
    }

    @app.get("/api/endpoints/team-hub", responses=_TEAM_ERROR_RESPONSES)
    def team_catalog() -> dict[str, object]:
        """Static Team Hub catalog: tabs and dataset metadata."""
        return team_hub_catalog()

    @app.get(
        "/api/teams/search",
        response_model=list[TeamSearchResult],
        responses=_TEAM_ERROR_RESPONSES,
    )
    def team_search(
        term: Annotated[str, Query()],
        service: TeamServiceDep,
    ) -> list[TeamSearchResult]:
        """Search teams by name/abbreviation.

        Mirrors ``/api/players/search`` but for the team hub. Currently a
        NotImplementedError stub pending the team-search wiring decision
        (see ``TeamHubService.search``).
        """
        try:
            return service.search(term)
        except Exception as error:
            raise _map_exception(error) from error

    @app.get(
        "/api/teams/{team_identifier}/summary",
        response_model=TeamHubSummary,
        responses=_TEAM_ERROR_RESPONSES,
    )
    def team_summary(
        team_identifier: str,
        service: TeamServiceDep,
    ) -> TeamHubSummary:
        """Aggregated Team Hub overview payload.

        Mirrors ``/api/players/{player_identifier}/summary``. Currently a
        NotImplementedError stub pending the team-summary wiring decision
        (see ``TeamHubService.summary``).
        """
        try:
            return service.summary(team_identifier)
        except Exception as error:
            raise _map_exception(error) from error

    @app.get("/api/teams/{team_identifier}/export", responses=_TEAM_ERROR_RESPONSES)
    def team_export(
        team_identifier: str,
        dataset: str,
        service: TeamServiceDep,
        season_end_year: int | None = None,
        include_inactive_games: bool = False,
    ) -> Response:
        """Stream a Team Hub dataset as a CSV download.

        Mirrors ``/api/players/{player_identifier}/export``. Currently a
        NotImplementedError stub pending the team-CSV wiring decision
        (see ``TeamHubService.csv``).
        """
        try:
            csv_text = service.csv(team_identifier, dataset, season_end_year, include_inactive_games)
        except Exception as error:
            raise _map_exception(error) from error
        season_suffix = f"-{season_end_year}" if season_end_year is not None else ""
        filename = f"{team_identifier}{season_suffix}-{dataset}.csv"
        return Response(
            csv_text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.get(
        "/api/teams/{team_identifier}/seasons/{season_end_year}/{dataset}",
        response_model=EndpointRowsResponse,
        responses=_TEAM_ERROR_RESPONSES,
    )
    def team_season_dataset(
        team_identifier: str,
        season_end_year: int,
        dataset: str,
        service: TeamServiceDep,
        include_inactive_games: bool = False,
    ) -> EndpointRowsResponse:
        """Team-season-scoped dataset (requires ``season_end_year`` in the URL)."""
        try:
            dataset_meta = team_dataset_by_id(dataset)
            if dataset_meta.scope != "team_season":
                raise ValueError(f"Dataset {dataset!r} does not require a season")
            return service.season_dataset(
                team_identifier,
                season_end_year,
                dataset,
                include_inactive_games,
            )
        except Exception as error:
            raise _map_exception(error) from error

    @app.get(
        "/api/teams/{team_identifier}/{dataset}",
        response_model=EndpointRowsResponse,
        responses=_TEAM_ERROR_RESPONSES,
    )
    def team_dataset(
        team_identifier: str,
        dataset: str,
        service: TeamServiceDep,
    ) -> EndpointRowsResponse:
        """Team-scoped dataset (no season in the URL)."""
        try:
            dataset_meta = team_dataset_by_id(dataset)
            if dataset_meta.scope != "team":
                raise ValueError(f"Dataset {dataset!r} requires /seasons/{{season_end_year}}")
            return service.dataset(team_identifier, dataset)
        except Exception as error:
            raise _map_exception(error) from error

    return app


def _params_for_dataset(
    dataset: str,
    player_identifier: str,
    season_end_year: int | None,
    include_inactive_games: bool,
) -> dict[str, object]:
    dataset_meta = DATASETS.get(dataset)
    if dataset_meta is None:
        raise ValueError(f"Unknown Player Hub dataset: {dataset}")
    params: dict[str, object] = {"player_identifier": player_identifier}
    if dataset_meta.scope == "season":
        if season_end_year is None:
            raise ValueError(f"Dataset {dataset!r} requires season_end_year")
        params["season_end_year"] = season_end_year
        if dataset in {"regular-games", "playoff-games"}:
            params["include_inactive_games"] = include_inactive_games
    return params


def app_from_env() -> FastAPI:
    raw_root = os.getenv("COURTSIDE_DATA_FIXTURE_ROOT")
    transport = os.getenv("COURTSIDE_SERVER_TRANSPORT", "fixture")
    if transport not in {"fixture", "live"}:
        raise RuntimeError("COURTSIDE_SERVER_TRANSPORT must be 'fixture' or 'live'")
    transport_mode: TransportMode = "live" if transport == "live" else "fixture"
    return create_app(transport=transport_mode, raw_root=Path(raw_root) if raw_root else None)


app = app_from_env()


# TODO(endpoint-roadmap): Remaining HTTP routes for 34 unreachable endpoints.
#
# See docs/architecture/endpoint-roadmap.md for the master plan. This block
# is documentation-only; it does NOT register any routes. The four
# domain lanes below mirror the existing Team Hub pattern (catalog stub +
# 1-2 services + 6 routes) except for Games/Browser which is a fundamentally
# different UX model.
#
# Status by domain (per the master matrix in endpoint-roadmap.md §1):
#   LEAGUE (11 endpoints): 0/11 reachable -> see docs/architecture/league-hub.md
#     Routes needed: /api/endpoints/league-hub (static catalog),
#       /api/league/seasons/{year}/{dataset} (11 routes mirroring the team
#       season-dataset pattern; 1 of them is standings_by_date which adds a
#       date path param, and 1 is attendance which is a projection).
#     Catalog stub (future): courtside_data/server/league_catalog.py
#     Service stub (future): courtside_data/server/league_service.py
#   PLAYOFFS (6 endpoints): 0/6 reachable -> see docs/architecture/playoffs-hub.md
#     Routes needed: /api/endpoints/playoffs-hub (static catalog),
#       /api/playoffs/seasons/{year}/{dataset} (3 season-scoped routes for
#       playoff_per_game, playoff_totals, playoff_bracket),
#       /api/playoffs/static/{table} (3 STATIC routes for the friv
#       team-is-down / team-is-tied / team-is-up endpoints, distinguished by
#       the table_id path param).
#     Catalog stub (future): courtside_data/server/playoffs_catalog.py
#     Service stub (future): courtside_data/server/playoffs_service.py
#   DRAFT_AWARDS_LEADERS (5 endpoints): 0/5 reachable
#     -> see docs/architecture/draft-awards-hub.md
#     Routes needed: /api/endpoints/draft-awards-hub (static catalog),
#       /api/draft/seasons/{year}/{dataset} (2 season-scoped routes for
#       draft_picks, season_awards, season_awards_voting),
#       /api/awards/static/{dataset} (2 STATIC routes for season_leaders,
#       career_leaders). season_awards_voting has a free-form `award` query
#       param that maps to 10 fallback table ids.
#     Catalog stub (future): courtside_data/server/draft_awards_catalog.py
#     Service stub (future): courtside_data/server/draft_awards_service.py
#   GAMES (12 endpoints, 0/12 reachable via a games-specific route;
#     3 of the 15 GAMES-domain endpoints are already reachable via the
#     Player Hub: regular_season_player_box_scores, playoff_player_box_scores,
#     search).
#     -> see docs/architecture/games-browser-hub.md
#     Routes needed: /api/endpoints/games-hub (static catalog),
#       /api/games/{game_id}/{dataset} (6 per-game box-score routes; the
#       game_id format is {YYYYMMDD}0{HOMETEAM_ABBR} -- see
#       games-browser-hub.md §3 for the load-bearing design decision),
#       /api/games/box-scores?date=YYYY-MM-DD&dataset=player|team (2
#       daily-leaders routes),
#       /api/games/play-by-play?date=YYYY-MM-DD&home_team=BOS (1 PBP route).
#     NOTE: Games/Browser is the HARDEST domain -- it does not fit the
#     entity-Hub pattern and spans 4 different interaction models
#     (per-game box scores, daily leaders, play-by-play, league-season
#     tables). The 3 season-scoped endpoints (season_schedule,
#     players_season_totals, players_advanced_season_totals) are
#     RECOMMENDED TO MOVE to the League Hub; see games-browser-hub.md §9.2.
#     Catalog stub: courtside_data/server/games_catalog.py (already
#     created with a TODO; the GAMES domain's catalog does not follow the
#     Team Hub shape).
#     Service stub (future): courtside_data/server/games_service.py
#
# What (per lane): Add a {league,playoffs,draft_awards,games}_catalog.py
#   module (1-2 services + 1 catalog function), then add a route group at
#   the end of create_app() (before the `return app` line on app.py:334)
#   mirroring the Team Hub routes at app.py:204-332. The Games Hub is the
#   exception: it does NOT have an entity search / summary / export route
#   triple; it has 6 per-game box-score routes + 2 daily-leaders routes +
#   1 PBP route (see games-browser-hub.md §4).
# Where:
#   - Pattern to mirror: app.py:204-332 (Team Hub routes)
#   - Service pattern: courtside_data/server/team_service.py (510+ lines)
#   - Catalog pattern: courtside_data/server/team_catalog.py (315+ lines)
#   - Fixtures whitelist: courtside_data/server/fixtures.py (the
#     TEAM_ENDPOINTS / TEAM_SEASON_ENDPOINTS sets are the template; the
#     four new lanes need LEAGUE_ENDPOINTS, PLAYOFFS_ENDPOINTS,
#     DRAFT_ENDPOINTS, GAMES_ENDPOINTS -- see the expanded TODO at the
#     bottom of fixtures.py).
# Decision needed:
#   - Should season_schedule + players_season_totals +
#     players_advanced_season_totals move to League Hub? (recommended yes;
#     see games-browser-hub.md §9.2)
#   - Game-identifier scheme for box scores (resolved: single game_id path
#     param matching BR format verbatim; see games-browser-hub.md §3.4)
#   - Route naming convention: /api/{domain}/seasons/{year}/... vs
#     /api/{domain}/... (Team Hub uses the seasons/ infix; LEAGUE/PLAYOFFS
#     should follow the same convention for consistency).
#   - Should daily-leaders use a `?dataset=...` discriminator or two
#     separate routes? (recommended `?dataset=...`; see
#     games-browser-hub.md §4.2)
# Verify: each new route group should pass TestClient smoke tests (200 on
#   catalog, 404 on missing-fixture datasets) mirroring the Team Hub test
#   pattern in tests/server/test_player_hub_api.py. The full
#   post-implementation check is `uv run task audit` (lint + format + type
#   + test) per AGENTS.md.
