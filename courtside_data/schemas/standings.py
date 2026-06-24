"""Row schemas for standings Basketball-Reference endpoints.

Covers the conference-division standings and the day-by-day standings. The
``standings`` endpoint routes through a custom :class:`HTTPService` method that
yields typed values from the conference-division standings parser, while
``standings_by_date`` flows through the generic-table pipeline and produces raw
``data-stat``-keyed string dicts.
"""

from __future__ import annotations

from pydantic import Field

from courtside_data.data import Conference, Division, Team
from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import BRInt, ConferenceField, StrOrNone

# ---------------------------------------------------------------------------
# Standings (custom endpoint — typed values from the conference-division
# standings parser)
# ---------------------------------------------------------------------------


class StandingsRow(BRRow):
    """Row from a conference-division standings table.

    The ``standings`` endpoint is custom and the bespoke HTTPService method
    routes the page through the ``ConferenceDivisionStandingsParser``,
    which already produces typed values: :class:`Team`,
    :class:`Division`, and :class:`Conference` enums and ``int`` counts. The
    keys in the dict match the schema field names exactly, so no
    ``validation_alias`` is needed for the underlying data.
    """

    team: Team
    wins: BRInt
    losses: BRInt
    division: Division
    conference: Conference


register("standings", StandingsRow)


# ---------------------------------------------------------------------------
# Standings by date (custom endpoint — date/rank snapshot rows)
# ---------------------------------------------------------------------------


class StandingsByDateRow(BRRow):
    """Row from a day-by-day standings table.

    Basketball-Reference publishes this as a pivot table: each row is a date,
    with ordinal rank columns (``1st`` through ``15th``) whose values contain
    team abbreviation and record snapshots, such as ``"BOS (1-0) T1"``.
    ``conference`` is injected by the custom fetcher because the endpoint
    combines the conference-scoped source pages.
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


register("standings_by_date", StandingsByDateRow)
