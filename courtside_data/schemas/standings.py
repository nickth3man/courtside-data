"""Row schemas for standings Basketball-Reference endpoints.

Covers the conference-division standings and the day-by-day standings. The
``standings`` endpoint routes through a custom :class:`HTTPService` method that
yields typed values from the legacy parser, while ``standings_by_date`` flows
through the generic-table pipeline and produces raw ``data-stat``-keyed
string dicts.
"""

from __future__ import annotations

from pydantic import Field

from courtside_data.data import Conference, Division, Team
from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import BRFloatOrNone, BRInt, TeamField

# ---------------------------------------------------------------------------
# Standings (custom endpoint — typed values from the legacy parser)
# ---------------------------------------------------------------------------


class StandingsRow(BRRow):
    """Row from a conference-division standings table.

    The ``standings`` endpoint is custom and the bespoke HTTPService method
    routes the page through the legacy ``ConferenceDivisionStandingsParser``,
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
# Standings by date (custom endpoint — raw data-stat-keyed string dicts)
# ---------------------------------------------------------------------------


class StandingsByDateRow(BRRow):
    """Row from a day-by-day standings table.

    The ``standings_by_date`` endpoint is custom but routes through
    :func:`courtside_data.tables.GenericTable` for extraction, so the row
    dict is keyed by the raw ``data-stat`` keys the table emits
    (``team_name_abbr``, ``wins``, ``losses``, ``win_loss_pct``, ``gb``,
    ``pts_per_g``, ``opp_pts_per_g``, ``srs``). ``team`` uses
    :data:`TeamField` because the BR value is the team abbreviation
    (e.g. ``"BOS"``), not the full enum member.
    """

    team: TeamField = Field(validation_alias="team_name_abbr")
    wins: BRInt = Field(validation_alias="wins")
    losses: BRInt = Field(validation_alias="losses")
    win_loss_percentage: BRFloatOrNone = Field(default=None, validation_alias="win_loss_pct")
    games_back: BRFloatOrNone = Field(default=None, validation_alias="gb")
    points_per_game: BRFloatOrNone = Field(default=None, validation_alias="pts_per_g")
    opponent_points_per_game: BRFloatOrNone = Field(default=None, validation_alias="opp_pts_per_g")
    simple_rating_system: BRFloatOrNone = Field(default=None, validation_alias="srs")


register("standings_by_date", StandingsByDateRow)
