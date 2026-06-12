"""Row schemas for the draft Basketball-Reference endpoint.

Covers the ``draft_picks`` table (``/draft/NBA_{year}.html``) — pick overall,
player, college, drafting team, career totals, and per-game averages.

The ``season_awards``, ``season_leaders``, and ``career_leaders`` row
models live in :mod:`courtside_data.schemas.league` because the awards
table reuses the league-level awards column layout and the leaders
indexes are scoped at the league level (they aggregate across all teams).
"""

from __future__ import annotations

from pydantic import Field

from courtside_data.schemas import register
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import (
    BRFloatOrNone,
    BRInt,
    BRIntOrNone,
    BRPercentage,
    TeamField,
)


class DraftPicksRow(BRRow):
    """Row from a draft picks table (``/draft/NBA_{year}.html``).

    The draft table carries both career totals (``g``, ``mp``, ``pts``,
    ``trb``, ``ast``) and per-game averages (``mp_per_g``, ``pts_per_g``,
    ``trb_per_g``, ``ast_per_g``) plus career-aggregate advanced stats
    (``ws``, ``ws_per_48``, ``bpm``, ``vorp``) and shooting percentages
    (``fg_pct``, ``fg3_pct``, ``ft_pct``). ``player`` and ``pick_overall``
    are required — they uniquely identify a draft selection; every other
    stat cell is optional (some players never logged an NBA minute,
    leaving their career cells empty).
    """

    pick_overall: BRInt = Field(validation_alias="pick_overall")
    player: str = Field(validation_alias="player")
    college_name: str | None = Field(default=None, validation_alias="college_name")
    team: TeamField | None = Field(default=None, validation_alias="team_id")
    seasons: BRIntOrNone = Field(default=None, validation_alias="seasons")
    games: BRIntOrNone = Field(default=None, validation_alias="g")
    minutes_played: BRIntOrNone = Field(default=None, validation_alias="mp")
    points: BRIntOrNone = Field(default=None, validation_alias="pts")
    total_rebounds: BRIntOrNone = Field(default=None, validation_alias="trb")
    assists: BRIntOrNone = Field(default=None, validation_alias="ast")
    field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg_pct")
    three_point_field_goal_percentage: BRPercentage = Field(default=None, validation_alias="fg3_pct")
    free_throw_percentage: BRPercentage = Field(default=None, validation_alias="ft_pct")
    minutes_played_per_game: BRFloatOrNone = Field(default=None, validation_alias="mp_per_g")
    points_per_game: BRFloatOrNone = Field(default=None, validation_alias="pts_per_g")
    total_rebounds_per_game: BRFloatOrNone = Field(default=None, validation_alias="trb_per_g")
    assists_per_game: BRFloatOrNone = Field(default=None, validation_alias="ast_per_g")
    win_shares: BRFloatOrNone = Field(default=None, validation_alias="ws")
    win_shares_per_48: BRFloatOrNone = Field(default=None, validation_alias="ws_per_48")
    box_plus_minus: BRFloatOrNone = Field(default=None, validation_alias="bpm")
    value_over_replacement_player: BRFloatOrNone = Field(default=None, validation_alias="vorp")


register("draft_picks", DraftPicksRow)
