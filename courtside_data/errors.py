from __future__ import annotations


class CourtsideDataError(Exception):
    """Base class for every domain error raised by courtside-data.

    Catch this to handle any library-specific failure (invalid lookups,
    rate-limit jail) without also swallowing httpx transport errors.
    """


class InvalidDate(CourtsideDataError):
    def __init__(self, day: int, month: int, year: int) -> None:
        message = f"Date with year set to {year}, month set to {month}, and day set to {day} is invalid"
        super().__init__(message)


class InvalidSeason(CourtsideDataError):
    def __init__(self, season_end_year: int) -> None:
        message = f"Season end year of {season_end_year} is invalid"
        super().__init__(message)


class InvalidPlayerAndSeason(CourtsideDataError):
    def __init__(self, player_identifier: str, season_end_year: int) -> None:
        message = f'Player with identifier "{player_identifier}" in season ending in {season_end_year} is invalid'
        super().__init__(message)


class InvalidSearch(CourtsideDataError):
    def __init__(self, term: str) -> None:
        message = f'Search term "{term}" returned no results'
        super().__init__(message)


class InvalidPlayer(CourtsideDataError):
    def __init__(self, player_identifier: str) -> None:
        self.player_identifier = player_identifier
        message = f"Invalid player: {player_identifier}"
        super().__init__(message)


class InvalidTeam(CourtsideDataError):
    def __init__(self, team_abbreviation: str) -> None:
        self.team_abbreviation = team_abbreviation
        message = f"Invalid team: {team_abbreviation}"
        super().__init__(message)


class RateLimitJailed(CourtsideDataError):
    """Raised when Basketball-Reference has jailed the session (Retry-After > 5 minutes)."""

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        message = (
            f"Session jailed by Basketball-Reference. "
            f"Retry-After: {retry_after:.0f}s ({retry_after / 60:.1f} minutes). "
            f"Back off and retry later."
        )
        super().__init__(message)


class MissingPlayerSlug(CourtsideDataError):
    """Raised when a custom player parser fails to inject the required player slug."""

    def __init__(self, endpoint_name: str, row_index: int, player: str) -> None:
        self.endpoint_name = endpoint_name
        self.row_index = row_index
        self.player = player
        message = (
            f"Missing player slug while parsing endpoint '{endpoint_name}' at row {row_index} for player {player!r}"
        )
        super().__init__(message)


def _extract_missing_field(pydantic_errors: list[dict]) -> str:
    """Return the location of the first missing field/alias, or 'unknown'."""
    for error in pydantic_errors:
        if error.get("type") == "missing":
            loc = error.get("loc")
            if loc:
                return ".".join(str(part) for part in loc)
    return "unknown"


class SchemaDriftError(CourtsideDataError):
    """Raised when a generic endpoint row no longer matches the registered schema.

    Carries the Pydantic validation errors so callers can inspect exactly which
    fields/aliases are missing or malformed.
    """

    def __init__(self, endpoint_name: str, url: str, pydantic_errors: list[dict]) -> None:
        self.endpoint_name = endpoint_name
        self.url = url
        self.pydantic_errors = pydantic_errors
        field_or_alias = _extract_missing_field(pydantic_errors)
        message = f"Schema drift detected for endpoint '{endpoint_name}' ({url}): missing field/alias: {field_or_alias}"
        super().__init__(message)
