"""Typed API models for the optional Team Hub server."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from courtside_data.server.models import EndpointRowsResponse, TransportMode

TeamDatasetScope = Literal["team", "team_season"]


class TeamSearchResult(BaseModel):
    """Team result shown in the UI search control."""

    name: str
    identifier: str
    leagues: list[str] = Field(default_factory=list)


class TeamHubTab(BaseModel):
    """A tab and its backing datasets in the Team Hub."""

    id: str
    label: str
    description: str
    scope: TeamDatasetScope
    datasets: list[str]
    default_dataset: str


class TeamDatasetCatalogEntry(BaseModel):
    """HTTP-facing metadata for one Team Hub dataset.

    Mirrors :class:`DatasetCatalogEntry` but uses the team-scope literal
    (``"team"`` / ``"team_season"``) instead of the player-scope literal.
    """

    id: str
    label: str
    endpoint_name: str
    scope: TeamDatasetScope
    description: str
    columns: list[Any] = Field(default_factory=list)
    default_visible_columns: list[str] = Field(default_factory=list)
    supports_export: bool = True


class TeamHubCatalog(BaseModel):
    """Top-level Team Hub catalog response.

    Shape mirrors :class:`PlayerHubSummary` in spirit (hub landing payload)
    but exposes the static tab/dataset metadata that the UI uses to render
    the hub shell.
    """

    tabs: list[TeamHubTab]
    datasets: dict[str, TeamDatasetCatalogEntry]


class TeamHubSummary(BaseModel):
    """Aggregated overview payload for the Team Hub landing state.

    Mirrors :class:`PlayerHubSummary`; the embedded ``roster`` field plays
    the same structural role as the player hub's ``career`` field.
    """

    model_config = ConfigDict(extra="forbid")

    identifier: str
    display_name: str
    leagues: list[str] = Field(default_factory=list)
    default_season: int | None = None
    available_seasons: list[int] = Field(default_factory=list)
    hero_stats: dict[str, Any] = Field(default_factory=dict)
    roster: EndpointRowsResponse
    season_dataset_availability: dict[str, list[int]] = Field(default_factory=dict)
    transport: TransportMode
