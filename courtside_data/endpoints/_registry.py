"""``ENDPOINTS`` dict assembled from domain-specific endpoint groups."""

from __future__ import annotations

from courtside_data.endpoints._custom import CUSTOM_ENDPOINTS
from courtside_data.endpoints._draft_awards_leaders import DRAFT_AWARDS_LEADERS_ENDPOINTS
from courtside_data.endpoints._league import LEAGUE_ENDPOINTS
from courtside_data.endpoints._players import PLAYER_ENDPOINTS
from courtside_data.endpoints._playoffs import PLAYOFF_ENDPOINTS
from courtside_data.endpoints._table import TableEndpoint
from courtside_data.endpoints._teams import TEAM_ENDPOINTS

ENDPOINTS: dict[str, TableEndpoint] = {
    **LEAGUE_ENDPOINTS,
    **PLAYOFF_ENDPOINTS,
    **DRAFT_AWARDS_LEADERS_ENDPOINTS,
    **PLAYER_ENDPOINTS,
    **TEAM_ENDPOINTS,
    **CUSTOM_ENDPOINTS,
}
