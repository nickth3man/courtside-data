"""Row schema for the play-by-play endpoint.

The play-by-play table is structural rather than ``data-stat`` driven, so the
Wave-4 custom fetcher is responsible for producing rows with stable keys.  In
particular, ``relevant_team`` must be resolved from the event description and
the away/home team context before the row reaches this model.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import BeforeValidator

from courtside_data.data import PeriodType
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import BRFloat, BRInt, TeamField
from courtside_data.schemas._registry import register

_SCORE_REGEX = re.compile(r"^(?P<away>[0-9]+)\s*-\s*(?P<home>[0-9]+)$")


def _parse_score(side: str):
    """Return a BeforeValidator that extracts one side of an ``AWAY-HOME`` score."""

    def validator(value: object) -> int | None:
        if value is None:
            return None
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        s = str(value).strip()
        if s in {"", "\xa0"}:
            return None
        match = _SCORE_REGEX.match(s)
        if match is not None:
            return int(match.group("away" if side == "away" else "home"))
        return int(s)

    return validator


AwayScore = Annotated[int | None, BeforeValidator(_parse_score("away"))]
HomeScore = Annotated[int | None, BeforeValidator(_parse_score("home"))]


class PlayByPlayRow(BRRow):
    """A single play-by-play event."""

    period: BRInt
    period_type: PeriodType
    remaining_seconds_in_period: BRFloat
    relevant_team: TeamField
    away_team: TeamField
    home_team: TeamField
    away_score: AwayScore
    home_score: HomeScore
    description: str


register("play_by_play", PlayByPlayRow)
