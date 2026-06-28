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
    datasets: list[TeamDatasetCatalogEntry]


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
    hero_stats: TeamHeroStats = Field(default_factory=lambda: TeamHeroStats(team=""))
    roster: EndpointRowsResponse
    season_dataset_availability: dict[str, list[int]] = Field(default_factory=dict)
    franchise_arc: list[FranchiseArcPoint] = Field(default_factory=list)
    transport: TransportMode


class TeamHeroStats(BaseModel):
    """Closed-type hero-stats payload for the Team Hub landing state.

    Mirrors the player-hub's :class:`PlayerHubSummary` ``hero_stats``
    payload but typed: ``team`` is the only required field (always
    populated with the requested team identifier so a missing-fixture
    path still tells the UI which team the empty stats are for); every
    other field is ``Optional`` and defaults to ``None``. This is the
    graceful-empty contract — the UI can render "no data" without
    guarding on shape.
    """

    model_config = ConfigDict(extra="forbid")

    team: str
    season: int | str | None = None
    wins: int | None = None
    losses: int | None = None
    win_pct: float | None = None
    wins_pyth: int | None = None
    losses_pyth: int | None = None
    mov: float | None = None
    srs: float | None = None
    off_rtg: float | None = None
    def_rtg: float | None = None
    pace: float | None = None


class FranchiseArcPoint(BaseModel):
    """A single point on the franchise-level season arc.

    Sourced from the ``franchise_history`` endpoint's
    :class:`~courtside_data.schemas.teams.FranchiseHistoryRow`. The
    point carries the season-end-year, the team name (which can
    differ across the arc for relocated / renamed franchises, e.g.
    the Seattle SuperSonics -> OKC Thunder), and the win-loss
    summary. ``win_pct`` is computed by the service
    (``wins / (wins + losses)`` when both are positive; ``None``
    otherwise).
    """

    model_config = ConfigDict(extra="forbid")

    season_end_year: int
    team_name: str | None = None
    wins: int | None = None
    losses: int | None = None
    win_pct: float | None = None
