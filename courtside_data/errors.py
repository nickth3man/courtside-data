from __future__ import annotations

from typing import Any


class CourtsideDataError(Exception):
    """Base class for every domain error raised by courtside-data.

    Catch this to handle any library-specific failure (invalid lookups,
    rate-limit jail) without also swallowing httpx transport errors.
    """


class _DomainError(CourtsideDataError):
    """Internal base for the concrete domain errors in this module.

    This is private — public callers should catch :class:`CourtsideDataError`
    instead.
    """


class InvalidDate(_DomainError):
    def __init__(self, day: int, month: int, year: int) -> None:
        super().__init__(f"Date with year set to {year}, month set to {month}, and day set to {day} is invalid")


class InvalidSeason(_DomainError):
    def __init__(self, season_end_year: int) -> None:
        super().__init__(f"Season end year of {season_end_year} is invalid")


class InvalidPlayerAndSeason(_DomainError):
    def __init__(self, player_identifier: str, season_end_year: int) -> None:
        super().__init__(
            f'Player with identifier "{player_identifier}" in season ending in {season_end_year} is invalid'
        )


class InvalidSearch(_DomainError):
    def __init__(self, term: str) -> None:
        super().__init__(f'Search term "{term}" returned no results')


class InvalidPlayer(_DomainError):
    def __init__(self, player_identifier: str) -> None:
        self.player_identifier = player_identifier
        super().__init__(f"Invalid player: {player_identifier}")


class InvalidTeam(_DomainError):
    def __init__(self, team_abbreviation: str) -> None:
        self.team_abbreviation = team_abbreviation
        super().__init__(f"Invalid team: {team_abbreviation}")


class RateLimitJailed(_DomainError):
    """Raised when Basketball-Reference has jailed the session (Retry-After > 5 minutes)."""

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"Session jailed by Basketball-Reference. "
            f"Retry-After: {retry_after:.0f}s ({retry_after / 60:.1f} minutes). "
            f"Back off and retry later."
        )


class MissingPlayerSlug(_DomainError):
    """Raised when a custom player parser fails to inject the required player slug."""

    def __init__(self, endpoint_name: str, row_index: int, player: str) -> None:
        self.endpoint_name = endpoint_name
        self.row_index = row_index
        self.player = player
        super().__init__(
            f"Missing player slug while parsing endpoint '{endpoint_name}' at row {row_index} for player {player!r}"
        )


def _format_loc(loc: tuple[Any, ...]) -> str:
    """Render a Pydantic ``loc`` tuple as a dotted path.

    Identifier-like segments are joined with ``.``; anything else (integers,
    strings with spaces, etc.) is bracketed, e.g. ``('scores', 0, 'points')``
    becomes ``scores.[0].points``. An empty tuple renders as ``<root>``.
    """
    parts: list[str] = []
    for part in loc:
        s = str(part)
        parts.append(s if s.isidentifier() else f"[{s}]")
    return ".".join(parts) if parts else "<root>"


def _summarize_pydantic_errors(pydantic_errors: list[dict]) -> str:
    """Render a one-line summary of a Pydantic v2 ``ValidationError.errors()`` payload.

    Preserves the legacy ``missing field/alias '<loc>'`` shape for the common
    "row no longer matches the schema" canary case, but degrades gracefully for
    other error types by surfacing the first error's type/loc/msg, and notes
    when additional errors are present.
    """
    if not pydantic_errors:
        return "no errors"
    first = pydantic_errors[0]
    err_type = str(first.get("type", "unknown"))
    raw_loc = first.get("loc") or ()
    loc_str = _format_loc(tuple(raw_loc)) if raw_loc else "<root>"
    msg = str(first.get("msg", "")).strip() or "(no message)"
    if err_type == "missing":
        base = f"missing field/alias '{loc_str}'"
    else:
        short_msg = msg if len(msg) <= 80 else f"{msg[:77]}..."
        base = f"first error \u2014 {err_type} at '{loc_str}': {short_msg}"
    extras = len(pydantic_errors) - 1
    if extras > 0:
        base = f"{base} (+{extras} more)"
    return base


class SchemaDriftError(_DomainError):
    """Raised when a generic endpoint row no longer matches the registered schema.

    Carries the Pydantic validation errors so callers can inspect exactly which
    fields/aliases are missing or malformed.
    """

    def __init__(self, endpoint_name: str, url: str, pydantic_errors: list[dict]) -> None:
        self.endpoint_name = endpoint_name
        self.url = url
        self.pydantic_errors = pydantic_errors
        detail = _summarize_pydantic_errors(pydantic_errors)
        super().__init__(f"Schema drift detected for endpoint '{endpoint_name}' ({url}): {detail}")
