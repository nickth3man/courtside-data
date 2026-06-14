"""Row schemas for schedule Basketball-Reference endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, Field, model_validator

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRDatetime,
    BRIntOrNone,
    StrOrNone,
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

    g: BRIntOrNone = Field(default=None, validation_alias="g")
    date_game: StrOrNone = Field(default=None, validation_alias="date_game")
    game_start_time: StrOrNone = Field(default=None, validation_alias="game_start_time")
    network: StrOrNone = Field(default=None, validation_alias="network")
    box_score_text: StrOrNone = Field(default=None, validation_alias="box_score_text")
    game_location: StrOrNone = Field(default=None, validation_alias="game_location")
    opp_name: StrOrNone = Field(default=None, validation_alias="opp_name")
    game_result: StrOrNone = Field(default=None, validation_alias="game_result")
    overtimes: StrOrNone = Field(default=None, validation_alias="overtimes")
    pts: BRIntOrNone = Field(default=None, validation_alias="pts")
    opp_pts: BRIntOrNone = Field(default=None, validation_alias="opp_pts")
    wins: BRIntOrNone = Field(default=None, validation_alias="wins")
    losses: BRIntOrNone = Field(default=None, validation_alias="losses")
    game_streak: StrOrNone = Field(default=None, validation_alias="game_streak")
    attendance: BRIntOrNone = Field(default=None, validation_alias="attendance")
    game_duration: StrOrNone = Field(default=None, validation_alias="game_duration")
    game_remarks: StrOrNone = Field(default=None, validation_alias="game_remarks")


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
