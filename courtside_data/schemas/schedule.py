"""Row schemas for schedule Basketball-Reference endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, Field, model_validator

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRDate,
    BRDatetime,
    BRInt,
    BRIntOrNone,
    OutcomeField,
    TeamNameField,
)


def _combine_start_time(data: Any) -> Any:
    """Populate ``start_time`` from separate ``date_game`` and ``game_start_time`` cells."""
    if not isinstance(data, dict) or "start_time" in data:
        return data
    date_game = data.get("date_game")
    if date_game is None:
        return data
    data["start_time"] = (date_game, data.get("game_start_time"))
    return data


class TeamScheduleRow(BRRow):
    """Row from a team schedule table (``table#games`` on ``/teams/{team}/{season}_games.html``)."""

    game_number: BRInt = Field(validation_alias=AliasChoices("game_number", "g"))
    date: BRDate = Field(validation_alias="date_game")
    start_time: BRDatetime = Field(validation_alias="start_time")
    away_team: TeamNameField = Field(validation_alias=AliasChoices("away_team_name", "visitor_team_name", "opp_name"))
    away_team_score: BRIntOrNone = Field(
        default=None,
        validation_alias=AliasChoices("away_team_score", "visitor_pts", "opp_pts"),
    )
    home_team: TeamNameField = Field(validation_alias=AliasChoices("home_team_name", "team_name"))
    home_team_score: BRIntOrNone = Field(
        default=None,
        validation_alias=AliasChoices("home_team_score", "home_pts", "tm_pts"),
    )
    result: OutcomeField = Field(validation_alias=AliasChoices("result", "game_result"))
    overtimes: str | None = Field(default=None, validation_alias="overtimes")
    wins: BRInt = Field(validation_alias="wins")
    losses: BRInt = Field(validation_alias="losses")
    streak: str = Field(validation_alias="streak")

    @model_validator(mode="before")
    @classmethod
    def _combine_start_time_validator(cls, data: Any) -> Any:
        return _combine_start_time(data)


register("team_schedule", TeamScheduleRow)


class SeasonScheduleRow(BRRow):
    """Row from the league season schedule (``table#schedule`` on ``/leagues/NBA_{season_end_year}_games.html``)."""

    start_time: BRDatetime = Field(validation_alias="start_time")
    away_team: TeamNameField = Field(validation_alias=AliasChoices("away_team_name", "visitor_team_name"))
    away_team_score: BRIntOrNone = Field(default=None, validation_alias=AliasChoices("away_team_score", "visitor_pts"))
    home_team: TeamNameField = Field(validation_alias=AliasChoices("home_team_name", "home_team"))
    home_team_score: BRIntOrNone = Field(default=None, validation_alias=AliasChoices("home_team_score", "home_pts"))

    @model_validator(mode="before")
    @classmethod
    def _combine_start_time_validator(cls, data: Any) -> Any:
        return _combine_start_time(data)


register("season_schedule", SeasonScheduleRow)
