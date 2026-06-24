"""Declarative registry for generic ("beta") Basketball Reference endpoints.

Each :class:`TableEndpoint` captures everything that distinguishes one
table-scraping endpoint from another: the URL path template, how to locate the
table on the page, which CSV columns the output contract promises, and which
domain error a failed lookup maps to. ``HTTPService.fetch_table`` and the
generated client functions consume these specs, so adding a new endpoint is a
single registry entry.

Path and table-id templates are ``str.format`` templates over the endpoint's
call parameters, e.g. ``"/players/{player_identifier[0]}/{player_identifier}.html"``.

The package layout:

* :mod:`courtside_data.endpoints._error_mapping` — HTTP status-code tuples
  shared by the registry and ``TableEndpoint`` defaults.
* :mod:`courtside_data.endpoints._table` — ``TableEndpoint`` dataclass and
  the ``_endpoint`` / ``_season`` / ``_team`` / ``_player`` factory helpers.
* :mod:`courtside_data.endpoints._registry` — the ``ENDPOINTS`` dict literal
  plus the per-domain ``output.columns`` / ``schemas`` imports it needs.
"""

from __future__ import annotations

from courtside_data.endpoints._error_mapping import NOT_FOUND, NOT_FOUND_OR_SERVER_ERROR
from courtside_data.endpoints._metadata import (
    EndpointDomain,
    EndpointFeature,
    EndpointKind,
    EndpointMetadata,
    EndpointScope,
    ParserShape,
    RequestShape,
)
from courtside_data.endpoints._registry import ENDPOINTS
from courtside_data.endpoints._table import (
    _DEFAULT_SEASON_MIN_YEAR,
    TableEndpoint,
    _endpoint,
    _player,
    _season,
    _team,
)

__all__ = [
    "ENDPOINTS",
    "NOT_FOUND",
    "NOT_FOUND_OR_SERVER_ERROR",
    "_DEFAULT_SEASON_MIN_YEAR",
    "EndpointDomain",
    "EndpointFeature",
    "EndpointKind",
    "EndpointMetadata",
    "EndpointScope",
    "ParserShape",
    "RequestShape",
    "TableEndpoint",
    "_endpoint",
    "_player",
    "_season",
    "_team",
]
