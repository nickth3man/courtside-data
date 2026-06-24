"""Pydantic ``Annotated`` field types for Basketball-Reference schemas.

Every ``Annotated[..., BeforeValidator(fn)]`` alias you see in row models
originates here. The actual validation functions live in
:mod:`courtside_data.schemas._validators` and are re-exported from this
module for backward compatibility. All names that were importable from
``_fields`` remain importable here.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BeforeValidator

from courtside_data.data import (
    Conference,
    Division,
    League,
    Location,
    Outcome,
    Position,
    Team,
)
from courtside_data.schemas._validators import (
    _br_award_rank,
    _br_date,
    _br_datetime,
    _br_decimal,
    _br_float,
    _br_float_or_none,
    _br_int,
    _br_int_or_none,
    _br_percentage,
    _br_salary,
    _conference_field,
    _division_field,
    _is_empty,  # noqa: F401  # re-exported for backward compat
    _league_field,
    _location_field,
    _outcome_field,
    _positions_field,
    _rank_tied,
    _seconds_played,
    _seconds_played_or_none,
    _str_or_none,
    _team_field,
    _team_name_field,
)

# ── Annotated field-type aliases ───────────────────────────────────────

StrOrNone = Annotated[str | None, BeforeValidator(_str_or_none)]
BRInt = Annotated[int, BeforeValidator(_br_int)]
BRIntOrNone = Annotated[int | None, BeforeValidator(_br_int_or_none)]
# Award-voting rank: tolerates BR's tied-rank suffix (``"7T"`` -> ``7``); the
# tie flag is exposed via the companion :data:`RankTied` field.
BRAwardRank = Annotated[int | None, BeforeValidator(_br_award_rank)]
RankTied = Annotated[bool, BeforeValidator(_rank_tied)]
BRFloat = Annotated[float, BeforeValidator(_br_float)]
BRFloatOrNone = Annotated[float | None, BeforeValidator(_br_float_or_none)]
SecondsPlayed = Annotated[int, BeforeValidator(_seconds_played)]
SecondsPlayedOrNone = Annotated[int | None, BeforeValidator(_seconds_played_or_none)]
TeamField = Annotated[Team, BeforeValidator(_team_field)]
TeamNameField = Annotated[Team, BeforeValidator(_team_name_field)]
LocationField = Annotated[Location, BeforeValidator(_location_field)]
OutcomeField = Annotated[Outcome, BeforeValidator(_outcome_field)]
PositionsField = Annotated[list[Position], BeforeValidator(_positions_field)]
DivisionField = Annotated[Division, BeforeValidator(_division_field)]
ConferenceField = Annotated[Conference, BeforeValidator(_conference_field)]
LeagueField = Annotated[League, BeforeValidator(_league_field)]
BRDate = Annotated[date, BeforeValidator(_br_date)]
BRDatetime = Annotated[datetime, BeforeValidator(_br_datetime)]
BRSalary = Annotated[int | None, BeforeValidator(_br_salary)]
BRPercentage = Annotated[float | None, BeforeValidator(_br_percentage)]
BRDecimal = Annotated[Decimal, BeforeValidator(_br_decimal)]
