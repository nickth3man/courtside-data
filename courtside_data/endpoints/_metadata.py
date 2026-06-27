"""Typed taxonomy for :class:`~courtside_data.endpoints.EndpointSpec` specs.

These enums describe *what* an endpoint is (domain, shape, features) and provide
the canonical runtime dispatch kind. All values are ``StrEnum`` so they
serialise to plain strings and compare equal to their string representations.

Usage::

    from courtside_data.endpoints._metadata import (
        EndpointDomain,
        EndpointFeature,
        EndpointKind,
        EndpointMetadata,
        EndpointScope,
        ParserShape,
        RequestShape,
    )

    meta = EndpointMetadata(
        domain=EndpointDomain.TEAMS,
        kind=EndpointKind.GENERIC_TABLE,
        scope=EndpointScope.TEAM_SEASON,
        request_shape=RequestShape.SINGLE_REQUEST,
        parser_shape=ParserShape.TABLE,
    )
"""

from __future__ import annotations

from dataclasses import field
from enum import StrEnum

from courtside_data._frozen import frozen_slot


class EndpointKind(StrEnum):
    """Top-level classification of how an endpoint is implemented."""

    GENERIC_TABLE = "generic_table"
    """Standard ``GenericEndpointHandler.fetch_table`` pipeline."""

    WORKFLOW = "workflow"
    """Bespoke multi-step request handled by the workflow executor."""


class EndpointDomain(StrEnum):
    """Logical Basketball-Reference domain that an endpoint belongs to."""

    LEAGUE = "league"
    PLAYOFFS = "playoffs"
    DRAFT_AWARDS_LEADERS = "draft_awards_leaders"
    PLAYERS = "players"
    TEAMS = "teams"
    GAMES = "games"


class EndpointScope(StrEnum):
    """Granularity / key space of the endpoint's primary parameter set."""

    SEASON = "season"
    """League-wide season aggregate (``season_end_year``)."""

    TEAM_SEASON = "team_season"
    """One team x one season (``team_abbreviation`` + ``season_end_year``)."""

    TEAM = "team"
    """Team-only, season-independent (e.g. franchise history)."""

    PLAYER = "player"
    """Player career stats, season-independent (``player_identifier``)."""

    PLAYER_SEASON = "player_season"
    """One player x one season (``player_identifier`` + ``season_end_year``)."""

    DATE = "date"
    """Single calendar date (``day``, ``month``, ``year``)."""

    DATE_TEAM = "date_team"
    """Date x team combination."""

    GAME = "game"
    """Single game id (``YYYYMMDD0XXX``)."""

    SEARCH = "search"
    """Free-text search query."""

    STATIC = "static"
    """No parameters; content is fixed (e.g. all-time franchise list)."""


class RequestShape(StrEnum):
    """How many HTTP requests the endpoint issues."""

    SINGLE_REQUEST = "single_request"
    """One GET → one HTML page."""

    MULTI_REQUEST = "multi_request"
    """Multiple GETs fanned out (e.g. per-team box-score aggregation)."""

    REDIRECTING = "redirecting"
    """Follows one or more redirects to resolve the final URL."""

    PAGINATED = "paginated"
    """Issues one request per page until no next-page link is found."""

    STATIC = "static"
    """No network request; data is generated locally."""


class ParserShape(StrEnum):
    """How the response HTML is parsed into rows."""

    TABLE = "table"
    """Standard ``<table id="…">`` extraction."""

    COMMENTED_TABLE = "commented_table"
    """Table hidden inside an HTML comment (``extract_commented_table``)."""

    TRANSACTION_LIST = "transaction_list"
    """``<ul>``-based transaction list (``parse_transaction_list``)."""

    MULTI_TABLE = "multi_table"
    """Multiple tables merged into one row stream."""

    PAGE_BLOCKS = "page_blocks"
    """Structured blocks assembled from multiple page sections."""

    STANDINGS_BLOCKS = "standings_blocks"
    """Conference/division standings blocks (``ConferenceDivisionStandingsParser``)."""

    SEARCH_RESULTS = "search_results"
    """Search-result page (non-tabular HTML list)."""

    PLAY_BY_PLAY = "play_by_play"
    """Play-by-play event rows assembled from score-differential cells."""

    BRACKET = "bracket"
    """Playoff bracket grid (manually-laid-out table, header-fallback required)."""


class EndpointFeature(StrEnum):
    """Optional behavioural flags present on an endpoint.

    Values mirror the boolean / non-None fields of :class:`~courtside_data.endpoints.EndpointSpec`
    so that the metadata set can be compared programmatically without
    inspecting the low-level dataclass fields.
    """

    COMMENTED_TABLE = "commented_table"
    """Uses ``commented_table_id`` (table hidden inside HTML comment)."""

    FALLBACK_TABLE_IDS = "fallback_table_ids"
    """Has one or more ``fallback_table_ids``."""

    TRANSACTION_LIST_FALLBACK = "transaction_list_fallback"
    """Routes through ``parse_transaction_list`` as the last-resort extractor."""

    EXCLUDE_SUMMARY_ROWS = "exclude_summary_rows"
    """Strips league-average / summary rows appended by Basketball Reference."""

    HEADER_FALLBACK = "header_fallback"
    """Uses normalised header text as the row key when ``data-stat`` is absent."""

    VALUE_COLUMN = "value_column"
    """Renames the rotating stat-column header to the stable key ``value``."""

    PROJECTION = "projection"
    """Projects extracted rows down to a declared subset of keys."""

    FANOUT_LINKS = "fanout_links"
    """Fetches multiple linked sub-pages and merges the results."""

    PAGINATED = "paginated"
    """Issues requests across multiple pages."""

    REDIRECTS = "redirects"
    """Follows one or more redirects before parsing."""

    AGGREGATES_ROWS = "aggregates_rows"
    """Combines rows from multiple tables or requests into one output."""

    DERIVED_FIELDS = "derived_fields"
    """Adds computed fields not present in the raw HTML."""

    REQUIRES_NON_EMPTY = "requires_non_empty"
    """Raises an error when the extracted row set is empty."""

    WORKFLOW_DIAGNOSTICS = "workflow_diagnostics"
    """Emits non-standard debug telemetry beyond the default trace envelope."""

    INTERNAL_TEMPLATE_PARAMS = "internal_template_params"
    """Has URL-template placeholders that are *not* in ``params``
    (i.e. resolved internally by the bespoke handler)."""

    ENUM_PARAM_COERCION = "enum_param_coercion"
    """Accepts domain enum values (e.g. ``Team``) in addition to raw strings."""


@frozen_slot
class EndpointMetadata:
    """Immutable taxonomy descriptor for one :class:`~courtside_data.endpoints.EndpointSpec`.

    Attach via the ``metadata=`` kwarg when registering an endpoint.  All
    fields except ``features`` are required so that every annotated endpoint
    carries a complete description.

    Example::

        EndpointMetadata(
            domain=EndpointDomain.TEAMS,
            kind=EndpointKind.GENERIC_TABLE,
            scope=EndpointScope.TEAM_SEASON,
            request_shape=RequestShape.SINGLE_REQUEST,
            parser_shape=ParserShape.TABLE,
            features=frozenset({EndpointFeature.EXCLUDE_SUMMARY_ROWS}),
        )
    """

    domain: EndpointDomain
    kind: EndpointKind
    scope: EndpointScope
    request_shape: RequestShape
    parser_shape: ParserShape
    features: frozenset[EndpointFeature] = field(default_factory=frozenset)
