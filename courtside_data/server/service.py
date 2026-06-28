"""Application service for Player Hub API routes."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from courtside_data.client import CourtsideClient
from courtside_data.domain.seasons import season_end_year
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import InvalidSearch
from courtside_data.server.catalog import columns_for_dataset, dataset_by_id
from courtside_data.server.fixtures import build_fixture_service, fixture_seasons_for_player
from courtside_data.server.models import EndpointRowsResponse, PlayerHubSummary, PlayerSearchResult, TransportMode

PLAYER_DISPLAY_NAMES = {
    "abdulka01": "Kareem Abdul-Jabbar",
    "antetgi01": "Giannis Antetokounmpo",
    "birdla01": "Larry Bird",
    "bradlav01": "Avery Bradley",
    "brownja01": "Jaylen Brown",
    "bryanko01": "Kobe Bryant",
    "chambwi01": "Wilt Chamberlain",
    "curryst01": "Stephen Curry",
    "doncilu01": "Luka Doncic",
    "duncati01": "Tim Duncan",
    "duranke01": "Kevin Durant",
    "jamesle01": "LeBron James",
    "jokicni01": "Nikola Jokic",
    "jordami01": "Michael Jordan",
    "paulch01": "Chris Paul",
    "russebi01": "Bill Russell",
    "westbru01": "Russell Westbrook",
}


class PlayerHubService:
    """Runs existing Courtside Data endpoints for the Player Hub API."""

    def __init__(self, *, transport: TransportMode = "fixture", raw_root: Path | None = None) -> None:
        self.transport = transport
        self.raw_root = raw_root
        self._live_client = CourtsideClient(cache=True) if transport == "live" else None

    def _client_for(self, endpoint_name: str, params: dict[str, object]) -> CourtsideClient:
        if self.transport == "live":
            if self._live_client is None:
                self._live_client = CourtsideClient(cache=True)
            return self._live_client
        service = build_fixture_service(endpoint_name, params, raw_root=self.raw_root)
        return CourtsideClient(service=service)

    def _run(self, endpoint_name: str, params: dict[str, object]) -> list[Any]:
        endpoint_client = self._client_for(endpoint_name, params)
        endpoint_func = getattr(endpoint_client, endpoint_name)
        values = endpoint_func(**params, output_type=None)
        return list(values)

    @staticmethod
    def _serialize_rows(rows: list[Any]) -> list[dict[str, Any]]:
        return [row.model_dump(mode="json") if hasattr(row, "model_dump") else dict(row) for row in rows]

    def rows_for_dataset(self, dataset_id: str, params: dict[str, object]) -> EndpointRowsResponse:
        dataset = dataset_by_id(dataset_id)
        rows = self._serialize_rows(self._run(dataset.endpoint_name, params))
        columns = columns_for_dataset(dataset, rows[0] if rows else None)
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

    def search_players(self, term: str) -> list[PlayerSearchResult]:
        term = term.strip()
        if len(term) < 2:
            raise InvalidSearch(term)
        try:
            rows = self._serialize_rows(self._run("search", {"term": term}))
        except InvalidSearch:
            return []
        results: list[PlayerSearchResult] = []
        for row in rows:
            leagues = row.get("leagues", [])
            if isinstance(leagues, str):
                leagues = [leagues]
            results.append(
                PlayerSearchResult(
                    name=str(row["name"]),
                    identifier=str(row["identifier"]),
                    leagues=sorted(str(league) for league in leagues),
                )
            )
        return results

    def summary(self, player_identifier: str) -> PlayerHubSummary:
        career = self.rows_for_dataset("career", {"player_identifier": player_identifier})
        available_from_career = _season_end_years(career.rows)
        fixture_availability = (
            fixture_seasons_for_player(player_identifier, raw_root=self.raw_root) if self.transport == "fixture" else {}
        )
        available_from_fixtures = sorted(
            {season for seasons in fixture_availability.values() for season in seasons},
            reverse=True,
        )
        available_seasons = sorted(set(available_from_career) | set(available_from_fixtures), reverse=True)
        default_season = _default_season(available_from_fixtures or available_from_career)
        return PlayerHubSummary(
            identifier=player_identifier,
            display_name=PLAYER_DISPLAY_NAMES.get(player_identifier, player_identifier),
            default_season=default_season,
            available_seasons=available_seasons,
            hero_stats=_hero_stats(career.rows),
            career=career,
            season_dataset_availability=_dataset_availability_by_dataset_id(fixture_availability),
            transport=self.transport,
        )

    def csv_for_dataset(self, dataset_id: str, params: dict[str, object]) -> str:
        response = self.rows_for_dataset(dataset_id, params)
        fieldnames = [column.key for column in response.columns]
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(response.rows)
        return output.getvalue()


def _season_end_year(season: object) -> int | None:
    # Thin shim over :func:`courtside_data.domain.seasons.season_end_year`
    # so any internal callers in the player hub keep working without an
    # import-path change. The hoisted helper also accepts the
    # four-digit end-year spelling (``"1999-2000"``), which the local
    # copy did not — that gain is intentional.
    return season_end_year(season)


def _season_end_years(rows: list[dict[str, Any]]) -> list[int]:
    seasons = {_season_end_year(row.get("season")) for row in rows}
    return sorted((season for season in seasons if season is not None), reverse=True)


def _default_season(seasons: list[int]) -> int | None:
    if not seasons:
        return None
    if 2024 in seasons:
        return 2024
    return max(seasons)


def _hero_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    for row in reversed(rows):
        if _season_end_year(row.get("season")) is None:
            continue
        return {
            "season": row.get("season"),
            "team": row.get("team_name_abbr"),
            "positions": row.get("positions"),
            "games_played": row.get("games_played"),
            "points_per_game": row.get("points_per_game"),
            "total_rebounds_per_game": row.get("total_rebounds_per_game"),
            "assists_per_game": row.get("assists_per_game"),
            "field_goal_percentage": row.get("field_goal_percentage"),
        }
    return {}


def _dataset_availability_by_dataset_id(endpoint_availability: dict[str, list[int]]) -> dict[str, list[int]]:
    by_dataset: dict[str, list[int]] = {}
    for dataset_id in (
        "splits",
        "on-off",
        "shooting-breakdown",
        "regular-games",
        "playoff-games",
    ):
        endpoint_name = dataset_by_id(dataset_id).endpoint_name
        by_dataset[dataset_id] = endpoint_availability.get(endpoint_name, [])
    return by_dataset


def endpoint_count() -> int:
    return len(ENDPOINTS)
