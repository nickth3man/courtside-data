"""Row schemas for standings Basketball-Reference endpoints.

Covers the conference-division standings and the day-by-day standings. Both
endpoints route through executable workflows. ``standings`` yields typed values
from the conference-division standings parser, while ``standings_by_date``
reuses ``GenericTable`` inside its workflow to parse conference-scoped source
pages before injecting the conference label.
"""

from __future__ import annotations

import re

from pydantic import Field, model_validator

from courtside_data.domain import Conference, Division, Team
from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import BRInt, ConferenceField, StrOrNone
from courtside_data.schemas._validators import _team_field

# ---------------------------------------------------------------------------
# Standings (workflow endpoint - typed values from the conference-division
# standings parser)
# ---------------------------------------------------------------------------


class StandingsRow(BRRow):
    """Row from a conference-division standings table.

    The ``standings`` workflow routes the page through the
    conference-division standings parser, which already produces typed values:
    :class:`Team`, :class:`Division`, and :class:`Conference` enums and
    ``int`` counts. The keys in the dict match the schema field names exactly,
    so no ``validation_alias`` is needed for the underlying data.
    """

    team: Team
    wins: BRInt
    losses: BRInt
    division: Division
    conference: Conference


register("standings", StandingsRow)


# ---------------------------------------------------------------------------
# Standings by date (workflow endpoint - date/rank snapshot rows)
# ---------------------------------------------------------------------------


class StandingsByDateRow(BRRow):
    """Row from a day-by-day standings table.

    Basketball-Reference publishes this as a pivot table: each row is a date,
    with ordinal rank columns (``1st`` through ``15th``) whose values contain
    team abbreviation and record snapshots, such as ``"BOS (1-0) T1"``.
    ``conference`` is injected by the workflow because the endpoint combines
    the conference-scoped source pages.
    """

    conference: ConferenceField = Field(validation_alias="conference")
    date: str = Field(validation_alias="date")
    first: StrOrNone = Field(default=None, validation_alias="1st")
    second: StrOrNone = Field(default=None, validation_alias="2nd")
    third: StrOrNone = Field(default=None, validation_alias="3rd")
    fourth: StrOrNone = Field(default=None, validation_alias="4th")
    fifth: StrOrNone = Field(default=None, validation_alias="5th")
    sixth: StrOrNone = Field(default=None, validation_alias="6th")
    seventh: StrOrNone = Field(default=None, validation_alias="7th")
    eighth: StrOrNone = Field(default=None, validation_alias="8th")
    ninth: StrOrNone = Field(default=None, validation_alias="9th")
    tenth: StrOrNone = Field(default=None, validation_alias="10th")
    eleventh: StrOrNone = Field(default=None, validation_alias="11th")
    twelfth: StrOrNone = Field(default=None, validation_alias="12th")
    thirteenth: StrOrNone = Field(default=None, validation_alias="13th")
    fourteenth: StrOrNone = Field(default=None, validation_alias="14th")
    fifteenth: StrOrNone = Field(default=None, validation_alias="15th")

    first_team: Team | None = None
    first_wins: int | None = None
    first_losses: int | None = None
    first_tie_rank: int | None = None
    second_team: Team | None = None
    second_wins: int | None = None
    second_losses: int | None = None
    second_tie_rank: int | None = None
    third_team: Team | None = None
    third_wins: int | None = None
    third_losses: int | None = None
    third_tie_rank: int | None = None
    fourth_team: Team | None = None
    fourth_wins: int | None = None
    fourth_losses: int | None = None
    fourth_tie_rank: int | None = None
    fifth_team: Team | None = None
    fifth_wins: int | None = None
    fifth_losses: int | None = None
    fifth_tie_rank: int | None = None
    sixth_team: Team | None = None
    sixth_wins: int | None = None
    sixth_losses: int | None = None
    sixth_tie_rank: int | None = None
    seventh_team: Team | None = None
    seventh_wins: int | None = None
    seventh_losses: int | None = None
    seventh_tie_rank: int | None = None
    eighth_team: Team | None = None
    eighth_wins: int | None = None
    eighth_losses: int | None = None
    eighth_tie_rank: int | None = None
    ninth_team: Team | None = None
    ninth_wins: int | None = None
    ninth_losses: int | None = None
    ninth_tie_rank: int | None = None
    tenth_team: Team | None = None
    tenth_wins: int | None = None
    tenth_losses: int | None = None
    tenth_tie_rank: int | None = None
    eleventh_team: Team | None = None
    eleventh_wins: int | None = None
    eleventh_losses: int | None = None
    eleventh_tie_rank: int | None = None
    twelfth_team: Team | None = None
    twelfth_wins: int | None = None
    twelfth_losses: int | None = None
    twelfth_tie_rank: int | None = None
    thirteenth_team: Team | None = None
    thirteenth_wins: int | None = None
    thirteenth_losses: int | None = None
    thirteenth_tie_rank: int | None = None
    fourteenth_team: Team | None = None
    fourteenth_wins: int | None = None
    fourteenth_losses: int | None = None
    fourteenth_tie_rank: int | None = None
    fifteenth_team: Team | None = None
    fifteenth_wins: int | None = None
    fifteenth_losses: int | None = None
    fifteenth_tie_rank: int | None = None

    @model_validator(mode="after")
    def parse_rank_cells(self) -> StandingsByDateRow:
        for field_name in _STANDINGS_BY_DATE_ORDINAL_FIELDS:
            parsed = _parse_standings_rank_cell(getattr(self, field_name))
            if parsed is None:
                continue
            team, wins, losses, tie_rank = parsed
            object.__setattr__(self, f"{field_name}_team", team)
            object.__setattr__(self, f"{field_name}_wins", wins)
            object.__setattr__(self, f"{field_name}_losses", losses)
            object.__setattr__(self, f"{field_name}_tie_rank", tie_rank)
        return self


_STANDINGS_BY_DATE_ORDINAL_FIELDS = (
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
)
_STANDINGS_RANK_CELL_RE = re.compile(r"^(?P<team>[A-Z]{2,3})\s+\((?P<wins>\d+)-(?P<losses>\d+)\)(?:\s+T(?P<tie>\d+))?$")


def _parse_standings_rank_cell(value: str | None) -> tuple[Team, int, int, int | None] | None:
    if value is None:
        return None
    match = _STANDINGS_RANK_CELL_RE.match(value.strip())
    if match is None:
        return None
    tie = match.group("tie")
    return (
        _team_field(match.group("team")),
        int(match.group("wins")),
        int(match.group("losses")),
        int(tie) if tie is not None else None,
    )


register("standings_by_date", StandingsByDateRow)
