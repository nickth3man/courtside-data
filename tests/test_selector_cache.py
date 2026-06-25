"""Regression tests for the parsed-selector cache freshness contract."""

from __future__ import annotations

import httpx
from courtside_data.http import HTTPService


class SequencedTransport(httpx.BaseTransport):
    """Return response bodies in order while counting transport hits."""

    def __init__(self, bodies: list[str]) -> None:
        self._bodies = bodies
        self.calls = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        index = min(self.calls, len(self._bodies) - 1)
        self.calls += 1
        return httpx.Response(200, text=self._bodies[index], request=request)


def _service_for(transport: SequencedTransport) -> HTTPService:
    return HTTPService(
        session=httpx.Client(transport=transport),
        rate_limit_interval=0.0,
        rate_limit_jitter=0.0,
        random_func=lambda _start, _end: 0.0,
    )


def test_selector_cache_rechecks_transport_before_reusing_parse() -> None:
    transport = SequencedTransport(["<html><h1>same</h1></html>", "<html><h1>same</h1></html>"])
    service = _service_for(transport)
    url = service._url("/leagues/NBA_2024.html")

    first = service._get_selector(url)
    second = service._get_selector(url)

    assert transport.calls == 2
    assert second is first


def test_selector_cache_replaces_parse_when_same_url_body_changes() -> None:
    transport = SequencedTransport(["<html><h1>old</h1></html>", "<html><h1>new</h1></html>"])
    service = _service_for(transport)
    url = service._url("/leagues/NBA_2024.html")

    first = service._get_selector(url)
    second = service._get_selector(url)

    assert transport.calls == 2
    assert first.css("h1::text").get() == "old"
    assert second.css("h1::text").get() == "new"
    assert second is not first
