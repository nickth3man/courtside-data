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


def _service_from_app(request: Request) -> PlayerHubService:
    return request.app.state.player_hub_service


ServiceDep = Annotated[PlayerHubService, Depends(_service_from_app)]


def _api_error(status_code: int, code: str, message: str, **detail: Any) -> HTTPException:
    payload = ApiError(code=code, message=message, detail=detail)
    return HTTPException(status_code=status_code, detail=payload.model_dump())


def _map_exception(error: Exception) -> HTTPException:
    if isinstance(error, MissingFixtureError):
        return _api_error(404, "missing_fixture", str(error))
    if isinstance(error, InvalidSearch):
        return _api_error(404, "invalid_search", str(error))
    if isinstance(error, (InvalidPlayer, InvalidPlayerAndSeason)):
        return _api_error(404, "invalid_player", str(error))
    if isinstance(error, InvalidSeason):
        return _api_error(400, "invalid_season", str(error))
    if isinstance(error, RateLimitJailed):
        return _api_error(429, "rate_limit_jailed", str(error), retry_after=error.retry_after)
    if isinstance(error, SchemaDriftError):
        return _api_error(
            502,
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
        term: Annotated[str, Query(min_length=2)],
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
