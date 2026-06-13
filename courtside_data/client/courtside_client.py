"""A configurable client class that owns a single HTTP session."""

from __future__ import annotations

import functools
from typing import Any

import httpx

from courtside_data.client import _runner
from courtside_data.http_service import HTTPService


class CourtsideClient:
    """Basketball Reference client with one reusable HTTP session.

    Exposes every module-level endpoint function as a same-named method::

        client = CourtsideClient(cache=False)
        roster = client.team_roster(team_abbreviation="BOS", season_end_year=2024)

    Compared to the module-level convenience functions (which share one
    process-wide session), a ``CourtsideClient`` owns its session, so callers
    can control caching, headers, TLS impersonation, and timeouts.

    Rate limiting is intentionally not configurable: the library-wide pacing
    is tuned to stay safely under Basketball Reference's ban threshold, and
    it is enforced globally across all sessions in the process.
    """

    def __init__(
        self,
        *,
        cache: bool = True,
        headers: dict[str, str] | None = None,
        impersonate: str | None = "chrome124",
        timeout: httpx.Timeout | None = None,
    ) -> None:
        self._service = HTTPService(
            cache=cache,
            headers=headers,
            impersonate=impersonate,
            timeout=timeout,
        )

    def __getattr__(self, name: str) -> Any:
        from courtside_data import client as _client

        if name not in _client.ENDPOINT_FUNCTION_NAMES:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        func = getattr(_client, name)

        @functools.wraps(func)
        def bound(*args: Any, **kwargs: Any) -> Any:
            token = _runner._service_override.set(self._service)
            try:
                return func(*args, **kwargs)
            finally:
                _runner._service_override.reset(token)

        return bound

    def __dir__(self) -> list[str]:
        from courtside_data import client as _client

        return sorted(set(super().__dir__()) | set(_client.ENDPOINT_FUNCTION_NAMES))
