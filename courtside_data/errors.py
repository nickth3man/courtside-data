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
