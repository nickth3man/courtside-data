"""Typed API models for the optional Player Hub server."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

TransportMode = Literal["fixture", "live"]
DatasetScope = Literal["player", "season"]


class ApiError(BaseModel):
    """Stable error response returned by the Player Hub API."""

    code: str
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)


class ColumnMeta(BaseModel):
    """Presentation metadata for one response column."""

    key: str
    label: str
    default_visible: bool = True
    numeric: bool = False


class PlayerSearchResult(BaseModel):
    """Player result shown in the UI search control."""

    name: str
    identifier: str
    leagues: list[str] = Field(default_factory=list)


class PlayerHubTab(BaseModel):
    """A tab and its backing datasets in the Player Hub."""

    id: str
    label: str
    description: str
    scope: DatasetScope
    datasets: list[str]
    default_dataset: str


class DatasetCatalogEntry(BaseModel):
    """HTTP-facing metadata for one Player Hub dataset."""

    id: str
    label: str
    endpoint_name: str
    scope: DatasetScope
    description: str
    columns: list[ColumnMeta]
    default_visible_columns: list[str]
    supports_export: bool = True


class EndpointRowsResponse(BaseModel):
    """Rows returned by one endpoint-backed dataset."""

    dataset: str
    endpoint_name: str
    params: dict[str, Any]
    row_count: int
    columns: list[ColumnMeta]
    default_visible_columns: list[str]
    rows: list[dict[str, Any]]
    transport: TransportMode


class PlayerHubSummary(BaseModel):
    """Aggregated overview payload for the Player Hub landing state."""

    model_config = ConfigDict(extra="forbid")

    identifier: str
    display_name: str
    leagues: list[str] = Field(default_factory=list)
    default_season: int | None = None
    available_seasons: list[int] = Field(default_factory=list)
    hero_stats: dict[str, Any] = Field(default_factory=dict)
    career: EndpointRowsResponse
    season_dataset_availability: dict[str, list[int]] = Field(default_factory=dict)
    transport: TransportMode


class StatusResponse(BaseModel):
    """Health and runtime metadata for the UI shell."""

    ok: bool
    transport: TransportMode
    endpoint_count: int
    fixture_root: str | None = None
    fixture_root_exists: bool | None = None
