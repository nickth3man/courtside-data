"""HTTP layer: rate-limited, retried requests plus per-endpoint fetch methods.

Legacy endpoints (standings, box scores, schedule, play-by-play, season
totals, search) have bespoke methods using dedicated page classes from
raw table extraction. Generic endpoints are declared in
``courtside_data.endpoints`` and served by :meth:`HTTPService.fetch_table`,
which the generated client functions call directly.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from datetime import UTC
from pathlib import Path
from typing import Any, ClassVar

import httpx
import stamina
from curl_cffi.const import CurlOpt  # type: ignore[import-untyped]
from hishel.httpx import SyncCacheTransport
from lxml import html
from parsel import Selector

from courtside_data.data import (
    DIVISIONS_TO_CONFERENCES,
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
    Division,
    Team,
)
from courtside_data.debug import current_debug_trace
from courtside_data.endpoints import ENDPOINTS, TableEndpoint
from courtside_data.errors import InvalidDate, InvalidPlayerAndSeason, RateLimitJailed
from courtside_data.tables import GenericTable, extract_commented_table, parse_transaction_list

logger = logging.getLogger(__name__)

_DEFAULT_RATE_LIMIT_INTERVAL = 6.0  # 10 req/min ceiling — matches pybaseball's proven safe rate
_DEFAULT_RATE_LIMIT_JITTER = 1.0  # uniform(0, 1.0) — average ~8.6 req/min with comfortable headroom
_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
_RETRY_ATTEMPTS = 3

# Pages like the 7-game playoff series outcomes matrix host multiple tables
# that are exposed as separate endpoints. Cache parsed selectors per URL so
# fetching several tables from the same page only makes one HTTP request and
# only parses the HTML once. The cache is per-instance and bounded to avoid
# unbounded growth for long-lived clients.
_SELECTOR_CACHE_SIZE = 16
# Basketball-Reference can send Retry-After values of an hour or more when a
# session is jailed. stamina uses a hook-returned float verbatim (wait_max
# does not apply to it), so cap it to keep a single request from sleeping
# for the full jail duration.
_MAX_RETRY_AFTER_WAIT = float(os.environ.get("BASKETBALL_REF_MAX_RETRY_AFTER", "60.0"))

# If Retry-After exceeds this threshold, the session is considered jailed
# and further retries are suppressed to avoid wasting requests.
_JAIL_THRESHOLD_SECONDS = 300.0  # 5 minutes

# Jail state is persisted to disk so a process that crashes (or is restarted)
# while jailed does not immediately re-offend — Basketball-Reference
# escalates bans for repeat offenders. Set the env var to an empty string to
# disable persistence (the test suite does this to stay hermetic).
_JAIL_STATE_PATH_ENV = "BASKETBALL_REF_JAIL_STATE_PATH"
_DEFAULT_JAIL_STATE_PATH = Path(".cache") / "courtside" / "jail.json"

# Browser-like headers proven to avoid bot-flagging.
# Tells Cloudflare this looks like a real browser navigation event.
_DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}


def _xpath_literal(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"


def _find_table_by_id(selector: Selector, table_id: str) -> list[Selector]:
    return list(selector.xpath(f"//table[@id={_xpath_literal(table_id)}]"))


class _SafeCurlTransport(httpx.BaseTransport):
    """Wraps :class:`httpx_curl_cffi.CurlTransport` with two workarounds for
    correct caching behavior with hishel:

    1. **Timeout extension**: A hishel 1.x regression drops the ``timeout``
       extension when revalidating cached responses, causing
       ``CurlTransport._create_request_params`` to fail with an
       ``AssertionError``. The ``handle_request`` method ensures every
       request has a ``timeout`` extension before handing off to the real
       transport.

    2. **Content decoding**: ``curl-cffi`` decompresses gzip responses by
       default but leaves the ``Content-Encoding: gzip`` header in place.
       When hishel stores/retrieves the response, ``httpx`` sees the header
       and tries to decompress already-plaintext content, raising
       ``httpx.DecodingError``. Passing
       ``curl_options={CurlOpt.HTTP_CONTENT_DECODING: 0}`` tells libcurl
       not to decode content, so ``httpx`` handles decompression
       consistently.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        from httpx_curl_cffi import CurlTransport  # type: ignore[import-untyped]

        curl_options = kwargs.pop("curl_options", {})
        curl_options = {CurlOpt.HTTP_CONTENT_DECODING: 0, **curl_options}
        self._impl = CurlTransport(*args, curl_options=curl_options, **kwargs)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if "timeout" not in request.extensions:
            request.extensions["timeout"] = {
                "connect": _DEFAULT_TIMEOUT.connect,
                "read": _DEFAULT_TIMEOUT.read,
                "write": _DEFAULT_TIMEOUT.write,
                "pool": _DEFAULT_TIMEOUT.pool,
            }
        return self._impl.handle_request(request)

    def close(self) -> None:
        self._impl.close()


def _parse_retry_after(value: str) -> float:
    """Parse Retry-After header value, returning seconds to wait.

    Handles both integer seconds and HTTP-date formats per RFC 9110.
    """
    try:
        return float(value)
    except ValueError:
        pass
    # HTTP-date format: parse RFC 2822 date
    import email.utils as eutils
    from datetime import datetime

    parsed = eutils.parsedate_tz(value)
    if parsed is not None:
        retry_time = datetime(*parsed[:6], tzinfo=UTC)
        now = datetime.now(UTC)
        wait = (retry_time - now).total_seconds()
        return max(wait, 1.0)
    return 5.0


def _should_retry(exc: Exception) -> bool | float:
    """Custom stamina retry predicate.

    Returns True to retry with default backoff, a float to retry after
    that many seconds (honors Retry-After, capped at _MAX_RETRY_AFTER_WAIT),
    or False to abort. If the Retry-After value exceeds the jail threshold
    (5 minutes), returns False to skip retries — the caller handles jail
    detection.
    """
    if isinstance(exc, httpx.TransportError):
        logger.debug("Retrying after transport error: %s", exc)
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in (429, 502, 503, 504):
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after is not None:
                parsed = _parse_retry_after(retry_after)
                if parsed > _JAIL_THRESHOLD_SECONDS:
                    logger.warning("Retry-After of %.0fs exceeds jail threshold; not retrying", parsed)
                    return False  # We're jailed — don't burn retries
                wait = min(parsed, _MAX_RETRY_AFTER_WAIT)
                logger.debug("HTTP %d with Retry-After %s; retrying in %.1fs", code, retry_after, wait)
                return wait
            logger.debug("HTTP %d; retrying with default backoff", code)
            return True
        # Do NOT retry other 4xx (400, 401, 403, 404, etc.)
        return False
    return False


def _jail_state_path() -> Path | None:
    value = os.environ.get(_JAIL_STATE_PATH_ENV)
    if value is None:
        return _DEFAULT_JAIL_STATE_PATH
    return Path(value) if value else None


def _read_persisted_jail() -> float | None:
    """Return the persisted jailed-until UNIX timestamp if it is still active.

    Stale or unreadable state files are removed/ignored (best effort).
    """
    path = _jail_state_path()
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        jailed_until_epoch = float(payload["jailed_until_epoch"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if jailed_until_epoch <= time.time():
        try:
            path.unlink()
        except OSError:
            pass
        return None
    return jailed_until_epoch


def _persist_jail(jailed_until_epoch: float) -> None:
    path = _jail_state_path()
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"jailed_until_epoch": jailed_until_epoch}), encoding="utf-8")
    except OSError:
        logger.warning("Could not persist rate-limit jail state to %s", path)


def build_client(
    cache: bool = False,
    timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
    headers: dict[str, str] | None = None,
    impersonate: str | None = "chrome124",
) -> httpx.Client:
    """Build the httpx client used by HTTPService.

    With cache=True, responses are cached per RFC 9111 via hishel's
    SQLite-backed storage. Headers default to browser-like values that
    reduce bot-flagging; pass ``headers`` to override or extend.

    TLS impersonation is enabled by default (``impersonate="chrome124"``)
    via the ``httpx-curl-cffi`` package. Set ``impersonate=None`` to use
    standard httpx TLS instead.
    """
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    transport: httpx.BaseTransport = httpx.HTTPTransport()

    if impersonate is not None:
        transport = _SafeCurlTransport(impersonate=impersonate)

    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(transport=transport, follow_redirects=True, timeout=timeout, headers=merged)


class HTTPService:
    BASE_URL = "https://www.basketball-reference.com"
    _last_request_time: ClassVar[float] = float("-inf")
    _jailed_until: ClassVar[float] = 0.0  # monotonic timestamp; 0 = not jailed
    _jail_state_loaded: ClassVar[bool] = False  # persisted jail state is read at most once per process
    _rate_limit_lock: ClassVar[threading.RLock] = threading.RLock()

    def __init__(
        self,
        parser: Any = None,
        rate_limit_interval: float | None = None,
        rate_limit_jitter: float | None = None,
        session: httpx.Client | None = None,
        time_func: Callable[[], float] | None = None,
        sleep: Callable[[float], None] | None = None,
        random_func: Callable[[float, float], float] | None = None,
        timeout: httpx.Timeout | None = None,
        cache: bool = True,
        headers: dict[str, str] | None = None,
        impersonate: str | None = "chrome124",
    ) -> None:
        self.parser = parser
        # Constructor param > env var > default
        if rate_limit_interval is not None:
            self._rate_limit_interval = rate_limit_interval
        else:
            self._rate_limit_interval = float(
                os.environ.get("BASKETBALL_REF_RATE_LIMIT_INTERVAL", _DEFAULT_RATE_LIMIT_INTERVAL)
            )

        if rate_limit_jitter is not None:
            self._rate_limit_jitter = rate_limit_jitter
        else:
            self._rate_limit_jitter = float(
                os.environ.get("BASKETBALL_REF_RATE_LIMIT_JITTER", _DEFAULT_RATE_LIMIT_JITTER)
            )

        self._timeout = timeout if timeout is not None else _DEFAULT_TIMEOUT
        self._session = (
            session
            if session is not None
            else build_client(
                cache=cache,
                timeout=self._timeout,
                headers=headers,
                impersonate=impersonate,
            )
        )

        # Injectable dependencies for testing
        self._time = time_func if time_func is not None else time.monotonic
        self._sleep = sleep if sleep is not None else time.sleep
        self._random = random_func if random_func is not None else random.uniform

        # Bounded per-instance selector cache so multiple endpoints that scrape
        # the same URL share one fetch and one parse.
        self._selector_cache: OrderedDict[str, Selector] = OrderedDict()

    def _apply_rate_limiting(self) -> None:
        with self._rate_limit_lock:
            trace = current_debug_trace()
            # A jail set by a previous process (persisted to disk) carries over
            if not self.__class__._jail_state_loaded:
                self.__class__._jail_state_loaded = True
                jailed_until_epoch = _read_persisted_jail()
                if jailed_until_epoch is not None:
                    remaining = jailed_until_epoch - time.time()
                    self.__class__._jailed_until = self._time() + remaining
                    logger.warning("Loaded persisted jail state: %.0fs remaining", remaining)
                    if trace is not None:
                        trace.record("rate_limit", "persisted_jail_loaded", remaining_seconds=remaining)

            # Circuit breaker: if jailed, refuse all requests immediately
            current_time = self._time()
            if current_time < self.__class__._jailed_until:
                remaining = self.__class__._jailed_until - current_time
                if trace is not None:
                    trace.record("rate_limit", "jailed_request_rejected", remaining_seconds=remaining)
                raise RateLimitJailed(retry_after=remaining)

            time_since_last = current_time - self.__class__._last_request_time
            if self._rate_limit_interval > 0 and time_since_last < self._rate_limit_interval:
                jitter = self._random(0.0, self._rate_limit_jitter)
                wait = (self._rate_limit_interval - time_since_last) + jitter
                logger.debug("Rate-limit pacing: sleeping %.2fs", wait)
                if trace is not None:
                    trace.record(
                        "rate_limit",
                        "sleep",
                        interval_seconds=self._rate_limit_interval,
                        jitter_seconds=jitter,
                        wait_seconds=wait,
                        seconds_since_last_request=time_since_last,
                    )
                self._sleep(wait)
            elif trace is not None:
                trace.record(
                    "rate_limit",
                    "no_sleep",
                    interval_seconds=self._rate_limit_interval,
                    seconds_since_last_request=time_since_last,
                )
            self.__class__._last_request_time = self._time()

    def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        trace = current_debug_trace()
        if trace is not None:
            trace.record("http", "request_prepare", url=url, kwargs=sorted(kwargs))
        self._apply_rate_limiting()
        response = None
        attempt_count = 0
        try:
            for attempt in stamina.retry_context(
                on=_should_retry,
                attempts=_RETRY_ATTEMPTS,
                wait_initial=1.0,
                wait_max=10.0,
                wait_jitter=0.5,
            ):
                with attempt:
                    attempt_count += 1
                    if trace is not None:
                        trace.record("http", "attempt_start", attempt=attempt_count, url=url)
                    response = self._session.get(url=url, **kwargs)
                    if trace is not None:
                        trace.record(
                            "http",
                            "attempt_response",
                            attempt=attempt_count,
                            status_code=response.status_code,
                            url=str(response.url),
                            headers=trace.sanitize_headers(response.headers),
                            extensions={key: repr(value) for key, value in response.extensions.items()},
                        )
                    response.raise_for_status()
            assert response is not None  # retry_context either yields a response or raises
        except httpx.HTTPStatusError as e:
            if trace is not None:
                trace.record(
                    "http",
                    "status_error",
                    status_code=e.response.status_code,
                    url=str(e.response.url),
                    attempts=attempt_count,
                )
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                if retry_after is not None:
                    parsed = _parse_retry_after(retry_after)
                    if parsed > _JAIL_THRESHOLD_SECONDS:
                        # Set the circuit breaker so future calls fail fast,
                        # and persist it so restarted processes honor it too
                        self.__class__._jailed_until = self._time() + parsed
                        _persist_jail(time.time() + parsed)
                        logger.warning("Session jailed by Basketball-Reference for %.0fs", parsed)
                        if trace is not None:
                            trace.record("rate_limit", "jail_detected", retry_after_seconds=parsed)
                        raise RateLimitJailed(retry_after=parsed) from e
            raise
        else:
            # Reset pacing — retries consumed time, so measure from now
            with self._rate_limit_lock:
                self.__class__._last_request_time = self._time()
            if trace is not None:
                trace.record(
                    "http",
                    "request_complete",
                    status_code=response.status_code,
                    final_url=str(response.url),
                    attempts=attempt_count,
                )
        return response

    def _get_selector(self, url: str) -> Selector:
        """Fetch a page (no redirects) and wrap the body in a parsel Selector.

        Parsed selectors are cached per URL on this instance, so callers that
        extract several tables from the same page (e.g. the three 7-game
        playoff series outcome matrices) reuse one request and one parse.
        """
        if url in self._selector_cache:
            self._selector_cache.move_to_end(url)
            trace = current_debug_trace()
            if trace is not None:
                trace.record("http", "selector_cache_hit", url=url)
            return self._selector_cache[url]

        response = self._get(url=url, follow_redirects=False)
        response.raise_for_status()
        trace = current_debug_trace()
        if trace is not None:
            trace.record(
                "http",
                "selector_created",
                url=str(response.url),
                response_text_length=len(response.text),
                response_text_sha256=hashlib.sha256(response.text.encode("utf-8", errors="replace")).hexdigest(),
            )
        selector = Selector(text=response.text)
        self._selector_cache[url] = selector
        if len(self._selector_cache) > _SELECTOR_CACHE_SIZE:
            self._selector_cache.popitem(last=False)
        return selector

    def _get_html(self, url: str, **kwargs: Any) -> html.HtmlElement:
        """Fetch a page, raise on HTTP errors, and parse the body with lxml."""
        response = self._get(url=url, **kwargs)
        response.raise_for_status()
        trace = current_debug_trace()
        if trace is not None:
            trace.record(
                "http",
                "html_created",
                url=str(response.url),
                response_content_length=len(response.content),
                response_content_sha256=hashlib.sha256(response.content).hexdigest(),
            )
        return html.fromstring(response.content)

    # ── Generic endpoint plumbing ───────────────────────────────────────

    def fetch_table(self, endpoint: TableEndpoint, **params: Any) -> list[dict[str, Any]]:
        """Fetch and parse a generic table endpoint described by ``endpoint``.

        Resolution order: CSS ``table#<table_id>``, then a comment-wrapped
        table with ``commented_table_id``, then the transaction-list fallback,
        then an empty list.
        """
        if endpoint.custom:
            raise ValueError("Endpoint requires its bespoke HTTPService method, not fetch_table()")
        trace = current_debug_trace()
        url = f"{HTTPService.BASE_URL}{endpoint.path.format(**params)}"
        if trace is not None:
            trace.record(
                "endpoint",
                "generic_fetch_table_start",
                url=url,
                path_template=endpoint.path,
                table_id=endpoint.table_id,
                commented_table_id=endpoint.commented_table_id,
                transaction_list_fallback=endpoint.transaction_list_fallback,
                use_header_fallback=endpoint.use_header_fallback,
            )
        selector = self._get_selector(url=url)

        table_selector: Selector | None = None
        table_source: str | None = None
        if endpoint.table_id is not None:
            rendered_table_id = endpoint.table_id.format(**params)
            found = _find_table_by_id(selector, rendered_table_id)
            if trace is not None:
                trace.record(
                    "table_resolution",
                    "table_id_lookup",
                    selector=f"table[@id={rendered_table_id!r}]",
                    matched=bool(found),
                    match_count=len(found),
                )
            if found:
                table_selector = found[0]
                table_source = "table_id"
        if table_selector is None and endpoint.fallback_table_ids:
            for fallback_id in endpoint.fallback_table_ids:
                rendered_fallback_id = fallback_id.format(**params)
                found = _find_table_by_id(selector, rendered_fallback_id)
                if trace is not None:
                    trace.record(
                        "table_resolution",
                        "fallback_table_id_lookup",
                        selector=f"table[@id={rendered_fallback_id!r}]",
                        fallback_id=fallback_id,
                        matched=bool(found),
                        match_count=len(found),
                    )
                if found:
                    table_selector = found[0]
                    table_source = "fallback_table_id"
                    break
        if table_selector is None and endpoint.commented_table_id is not None:
            table_selector = extract_commented_table(selector, endpoint.commented_table_id)
            if trace is not None:
                trace.record(
                    "table_resolution",
                    "commented_table_lookup",
                    table_id=endpoint.commented_table_id,
                    matched=table_selector is not None,
                )
            if table_selector is not None:
                table_source = "commented_table_id"

        if table_selector is None and endpoint.table_id is None and endpoint.commented_table_id is None:
            found = selector.css("table")
            if found:
                table_selector = found[0]
                table_source = "first_table"

        if table_selector is None:
            if endpoint.transaction_list_fallback:
                rows = parse_transaction_list(selector)
                if trace is not None:
                    trace.record("table_resolution", "transaction_list_fallback", row_count=len(rows))
                    trace.artifact("raw_rows", rows)
                return rows
            if trace is not None:
                trace.record("table_resolution", "no_table_found", returned_row_count=0)
            return []

        table = GenericTable(table_selector, use_header_fallback=endpoint.use_header_fallback)
        rows = [row.to_dict() for row in table.rows]
        if trace is not None:
            raw_table_html = table_selector.get() or ""
            row_class_counts: dict[str, int] = {}
            for row_selector in table_selector.css("tr"):
                classes = row_selector.attrib.get("class", "").split()
                if not classes:
                    row_class_counts["<none>"] = row_class_counts.get("<none>", 0) + 1
                for class_name in classes:
                    row_class_counts[class_name] = row_class_counts.get(class_name, 0) + 1
            trace.record(
                "parse",
                "generic_table_parsed",
                source=table_source,
                row_count=len(rows),
                column_names=list(rows[0].keys()) if rows else [],
                table_attributes=dict(table_selector.attrib),
                table_html_length=len(raw_table_html),
                table_html_sha256=hashlib.sha256(raw_table_html.encode("utf-8", errors="replace")).hexdigest(),
                row_class_counts=row_class_counts,
            )
            trace.artifact("raw_rows", rows)
            trace.artifact(
                "row_metadata",
                [{"row_index": index, "metadata": row.metadata} for index, row in enumerate(table.rows)],
            )
        return rows

    # ── Legacy endpoints (dedicated page classes and parser chains) ─────

    @staticmethod
    def _find_table(selector: Selector, table_id: str) -> Selector | None:
        table = selector.css(f"table#{table_id}")
        if table:
            return table[0]
        return extract_commented_table(selector, table_id)

    @staticmethod
    def _raw_rows_from_table(
        table_selector: Selector,
        *,
        use_header_fallback: bool = False,
    ) -> list[tuple[dict[str, Any], dict[str, dict[str, str]]]]:
        table = GenericTable(table_selector, use_header_fallback=use_header_fallback)
        rows = [(row.to_dict(), row.metadata) for row in table.rows]
        trace = current_debug_trace()
        if trace is not None:
            trace.record(
                "parse",
                "raw_rows_from_table",
                row_count=len(rows),
                use_header_fallback=use_header_fallback,
                column_names=list(rows[0][0].keys()) if rows else [],
            )
            trace.append_artifact(
                "raw_table_extracts",
                {
                    "rows": [row for row, _ in rows],
                    "row_metadata": [
                        {"row_index": index, "metadata": metadata} for index, (_, metadata) in enumerate(rows)
                    ],
                },
            )
        return rows

    @staticmethod
    def _cell_text(selector: Any) -> str:
        text = (
            " ".join(value.strip() for value in selector.css("::text").getall() if value.strip())
            .replace("*", "")
            .strip()
        )
        return re.sub(r"\s+([),.;:])", r"\1", text)

    @staticmethod
    def _slug_from_metadata(metadata: dict[str, dict[str, str]], stat_name: str) -> str:
        return metadata.get(stat_name, {}).get("data-append-csv", "")

    @staticmethod
    def _is_combined_team(row: dict[str, Any]) -> bool:
        return str(row.get("team_name_abbr", "")).endswith("TM")

    @staticmethod
    def _team_abbreviation_from_name(team_name: str) -> str:
        team = TEAM_NAME_TO_TEAM[team_name.strip().upper()]
        return TEAM_TO_TEAM_ABBREVIATION[team]

    @staticmethod
    def _team_name_from_abbreviation(team_abbreviation: str) -> str:
        return TEAM_ABBREVIATIONS_TO_TEAM[team_abbreviation].value.title()

    @staticmethod
    def _score_outcome(points: str, opponent_points: str) -> str | None:
        team_points = int(points)
        opposing_points = int(opponent_points)
        if team_points > opposing_points:
            return "W"
        if team_points < opposing_points:
            return "L"
        return None

    @staticmethod
    def _period_number(period_count: int) -> int:
        return period_count if period_count <= 4 else period_count - 4

    @staticmethod
    def _period_type(period_count: int) -> str:
        return "QUARTER" if period_count <= 4 else "OVERTIME"

    @staticmethod
    def _remaining_seconds(timestamp: str) -> float:
        minutes, seconds = timestamp.split(":", maxsplit=1)
        return (int(minutes) * 60) + float(seconds)

    @classmethod
    def _standings_team_value(cls, formatted_name: str) -> str:
        cleaned = formatted_name.upper().strip()
        for team in Team:
            if cleaned.startswith(team.value):
                return team.value
        return cleaned

    @staticmethod
    def _division_value(formatted_name: str) -> str | None:
        cleaned = formatted_name.upper().strip()
        for division in Division:
            if cleaned == f"{division.value} DIVISION":
                return division.value
        return None

    @staticmethod
    def _resource_identifier(resource_location: str | None) -> str:
        if not resource_location:
            return ""
        return resource_location.rstrip("/").rsplit("/", maxsplit=1)[-1].removesuffix(".html")

    @staticmethod
    def _search_result_name(resource_name: str | None) -> str:
        if resource_name is None:
            return ""
        return resource_name.split("(", maxsplit=1)[0].strip()

    def _generic_table_rows(self, selector: Selector, table_id: str) -> list[dict[str, Any]]:
        table_selector = self._find_table(selector, table_id)
        if table_selector is None:
            return []
        return [row for row, _ in self._raw_rows_from_table(table_selector)]

    def _player_totals_rows(self, selector: Selector, table_id: str, *, include_combined: bool) -> list[dict[str, Any]]:
        table_selector = self._find_table(selector, table_id)
        if table_selector is None:
            return []

        rows: list[dict[str, Any]] = []
        for row, metadata in self._raw_rows_from_table(table_selector):
            if not row.get("name_display") or not row.get("team_name_abbr"):
                continue
            if not include_combined and self._is_combined_team(row):
                continue
            row["slug"] = self._slug_from_metadata(metadata, "name_display")
            if table_id == "advanced":
                row["is_combined_totals"] = self._is_combined_team(row)
            rows.append(row)
        return rows

    def _player_season_box_score_rows(
        self,
        table_selector: Selector,
        *,
        include_inactive_games: bool,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row, metadata in self._raw_rows_from_table(table_selector):
            if not row.get("date") and not row.get("date_game"):
                continue

            active = "colspan" not in metadata.get("is_starter", {})
            if not active and not include_inactive_games:
                continue

            row["active"] = active
            rows.append(row)
        return rows

    def _schedule_rows(self, selector: Selector) -> list[dict[str, Any]]:
        return [
            row
            for row in self._generic_table_rows(selector, "schedule")
            if row.get("visitor_team_name") and row.get("home_team_name")
        ]

    def _search_rows(self, selector: Selector) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for result in selector.css("div#searches div#players div.search-item"):
            link = result.css("div.search-item-name a")
            if not link:
                continue
            rows.append(
                {
                    "name": self._search_result_name(self._cell_text(link[0])),
                    "identifier": self._resource_identifier(link[0].attrib.get("href")),
                    "leagues": self._cell_text(result.css("div.search-item-league")),
                }
            )
        return rows

    def _search_pagination_url(self, selector: Selector) -> str | None:
        links = selector.css("div#searches div#players div.search-pagination a")
        if not links:
            return None
        if len(links) == 1:
            if self._cell_text(links[0]) == "Previous 100 Results":
                return None
            return links[0].attrib["href"]
        return links[1].attrib["href"]

    def standings(self, season_end_year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}.html"

        selector = self._get_selector(url=url)
        standings: list[dict[str, Any]] = []
        for table_id in ("divs_standings_E", "divs_standings_W"):
            current_division: Division | None = None
            table = selector.css(f"table#{table_id}")
            if not table:
                continue
            for row in table[0].css("tbody tr"):
                classes = row.attrib.get("class", "").split()
                if "thead" in classes:
                    division_value = self._division_value(self._cell_text(row.css("th")))
                    current_division = Division(division_value) if division_value is not None else None
                    continue
                team = self._cell_text(row.css('[data-stat="team_name"]'))
                if not team:
                    continue
                standings.append(
                    {
                        "team": self._standings_team_value(team),
                        "wins": self._cell_text(row.css('[data-stat="wins"]')),
                        "losses": self._cell_text(row.css('[data-stat="losses"]')),
                        "division": current_division.value if current_division is not None else None,
                        "conference": (
                            DIVISIONS_TO_CONFERENCES[current_division].value if current_division is not None else None
                        ),
                    }
                )

        return standings

    def player_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/friv/dailyleaders.cgi?month={month}&day={day}&year={year}"

        response = self._get(url=url, follow_redirects=False)

        response.raise_for_status()

        if response.status_code == httpx.codes.OK:
            selector = Selector(text=response.text)
            table = self._find_table(selector, "stats")
            if table is None:
                raise InvalidDate(day=day, month=month, year=year)
            rows = []
            for row, metadata in self._raw_rows_from_table(table):
                row["slug"] = self._slug_from_metadata(metadata, "player")
                rows.append(row)
            if not rows:
                raise InvalidDate(day=day, month=month, year=year)
            return rows

        raise InvalidDate(day=day, month=month, year=year)

    def _player_season_box_scores_selector(self, player_identifier: str, season_end_year: int) -> Selector:
        # Makes assumption that basketball reference pattern of breaking out player pathing using first character of
        # surname can be derived from the fact that basketball reference also has a pattern of player identifiers
        # starting with first few characters of player's surname
        url = f"{HTTPService.BASE_URL}/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}"

        return self._get_selector(url=url)

    def regular_season_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        selector = self._player_season_box_scores_selector(player_identifier, season_end_year)
        table = self._find_table(selector, "player_game_log_reg")
        if table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self._player_season_box_score_rows(table, include_inactive_games=include_inactive_games)

    def playoff_player_box_scores(
        self, player_identifier: str, season_end_year: int, include_inactive_games: bool = False
    ) -> list[dict[str, Any]]:
        selector = self._player_season_box_scores_selector(player_identifier, season_end_year)
        table = self._find_table(selector, "player_game_log_post")
        if table is None:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)

        return self._player_season_box_score_rows(table, include_inactive_games=include_inactive_games)

    def play_by_play(self, home_team: Team, day: int, month: int, year: int) -> list[dict[str, Any]]:
        # Look up the actual game URL from the daily boxscores page
        # instead of hardcoding the game index (handles doubleheaders).
        boxscores_selector = self._get_selector(
            url=f"{HTTPService.BASE_URL}/boxscores/?day={day}&month={month}&year={year}",
        )
        abbr = TEAM_TO_TEAM_ABBREVIATION[home_team]
        game_url_path = None
        for path in [link.attrib["href"] for link in boxscores_selector.css("td.gamelink a")]:
            if path.endswith(f"0{abbr}.html") or path.endswith(f"1{abbr}.html"):
                game_url_path = path
                break
        if game_url_path is None:
            raise InvalidDate(day=day, month=month, year=year)
        url = f"{HTTPService.BASE_URL}/boxscores/pbp/{game_url_path.split('/')[-1]}"
        selector = self._get_selector(url=url)
        team_names = [self._cell_text(team_name) for team_name in selector.css("#content div.scorebox strong a")]
        away_team = self._team_abbreviation_from_name(team_names[0])
        home_team_abbreviation = self._team_abbreviation_from_name(team_names[1])

        current_period = 0
        rows: list[dict[str, Any]] = []
        for row in selector.css("table#pbp tr"):
            cells = row.css("td, th")
            if not cells:
                continue
            timestamp_cell = cells[0]
            if timestamp_cell.attrib.get("colspan") == "6":
                current_period += 1
                continue
            if (
                len(cells) < 2
                or cells[1].attrib.get("colspan") == "5"
                or timestamp_cell.attrib.get("aria-label") == "Time"
            ):
                continue

            timestamp = self._cell_text(timestamp_cell)
            away_description = self._cell_text(cells[1]) if len(cells) == 6 else ""
            home_description = self._cell_text(cells[5]) if len(cells) == 6 else ""
            scores = self._cell_text(cells[3]) if len(cells) == 6 else ""
            is_away_play = away_description != ""
            rows.append(
                {
                    "period": self._period_number(current_period),
                    "period_type": self._period_type(current_period),
                    "remaining_seconds_in_period": self._remaining_seconds(timestamp),
                    "relevant_team": away_team if is_away_play else home_team_abbreviation,
                    "away_team": away_team,
                    "home_team": home_team_abbreviation,
                    "away_score": scores,
                    "home_score": scores,
                    "description": away_description if is_away_play else home_description,
                }
            )
        return rows

    def players_advanced_season_totals(
        self, season_end_year: int, include_combined_values: bool = False
    ) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}_advanced.html"

        selector = self._get_selector(url=url)
        return self._player_totals_rows(selector, "advanced", include_combined=include_combined_values)

    def players_season_totals(self, season_end_year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}_totals.html"

        selector = self._get_selector(url=url)
        return self._player_totals_rows(selector, "totals_stats", include_combined=False)

    def schedule_for_month(self, url: str) -> list[dict[str, Any]]:
        return self._schedule_rows(self._get_selector(url=url))

    def season_schedule(self, season_end_year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/leagues/NBA_{season_end_year}_games.html"

        selector = self._get_selector(url=url)
        season_schedule_values = self._schedule_rows(selector)

        for month_url_path in [
            link.attrib["href"] for link in selector.css('div#content div.filter div:not([class*="current"]) a')
        ]:
            url = f"{HTTPService.BASE_URL}{month_url_path}"
            monthly_schedule = self.schedule_for_month(url=url)
            season_schedule_values.extend(monthly_schedule)

        return season_schedule_values

    def team_box_score(self, game_url_path: str) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/{game_url_path.lstrip('/')}"

        selector = self._get_selector(url=url)
        combined_team_totals: list[dict[str, Any]] = []
        for table in selector.css('table.stats_table[id$="-game-basic"]'):
            table_id = table.attrib.get("id", "")
            if not table_id.startswith("box-"):
                continue
            team_abbreviation = table_id.removeprefix("box-").removesuffix("-game-basic")
            footer = table.css("tfoot")
            if not footer:
                continue
            rows = self._raw_rows_from_table(footer[0])
            if not rows:
                continue
            row = rows[0][0]
            row["team_name_abbr"] = self._team_name_from_abbreviation(team_abbreviation)
            combined_team_totals.append(row)

        if len(combined_team_totals) < 2:
            raise ValueError(f"Expected 2 team totals in box score page, got {len(combined_team_totals)}")

        first_team_totals, second_team_totals = combined_team_totals[:2]
        first_team_totals["outcome"] = self._score_outcome(first_team_totals["pts"], second_team_totals["pts"])
        second_team_totals["outcome"] = self._score_outcome(second_team_totals["pts"], first_team_totals["pts"])
        return [first_team_totals, second_team_totals]

    def team_box_scores(self, day: int, month: int, year: int) -> list[dict[str, Any]]:
        url = f"{HTTPService.BASE_URL}/boxscores/?day={day}&month={month}&year={year}"

        selector = self._get_selector(url=url)
        game_url_paths = [link.attrib["href"] for link in selector.css("td.gamelink a")]
        if not game_url_paths:
            raise InvalidDate(day=day, month=month, year=year)

        return [
            box_score
            for game_url_path in game_url_paths
            for box_score in self.team_box_score(game_url_path=game_url_path)
        ]

    def search(self, term: str) -> dict[str, list[dict[str, Any]]]:
        response = self._get(url=f"{HTTPService.BASE_URL}/search/search.fcgi", params={"search": term})

        response.raise_for_status()

        player_results: list[dict[str, Any]] = []

        if str(response.url).startswith(f"{HTTPService.BASE_URL}/search/search.fcgi"):
            selector = Selector(text=response.text)
            player_results += self._search_rows(selector)

            # Guard against pagination loops where the next-page URL doesn't
            # advance (e.g., when a page points back to itself). Without this,
            # a malformed or stale "Next" link can cause an infinite loop.
            seen_pagination_urls: set[str] = set()
            while self._search_pagination_url(selector) is not None:
                pagination_url = self._search_pagination_url(selector)
                assert pagination_url is not None
                if pagination_url in seen_pagination_urls:
                    break
                seen_pagination_urls.add(pagination_url)

                response = self._get(url=f"{HTTPService.BASE_URL}/search/{pagination_url}")

                response.raise_for_status()

                selector = Selector(text=response.text)
                player_results += self._search_rows(selector)

        elif str(response.url).startswith(f"{HTTPService.BASE_URL}/players"):
            selector = Selector(text=response.text)
            league_abbreviations = {
                self._cell_text(league)
                for league in selector.css('table#per_game tbody tr td[data-stat="lg_id"]')
                if self._cell_text(league)
            }
            player_results += [
                {
                    "name": self._cell_text(selector.css('h1[itemprop="name"]')),
                    "identifier": self._resource_identifier(str(response.url)),
                    "leagues": league_abbreviations,
                }
            ]

        return {"players": player_results}

    # ── Generic endpoints with bespoke behavior ─────────────────────────

    def standings_by_date(self, season_end_year: int) -> list[dict[str, Any]]:
        endpoint = ENDPOINTS["standings_by_date"]
        standings: list[dict[str, Any]] = []
        for conference in ["eastern_conference", "western_conference"]:
            url = (
                f"{HTTPService.BASE_URL}{endpoint.path.format(season_end_year=season_end_year, conference=conference)}"
            )
            selector = self._get_selector(url=url)
            table_selector = selector.css(f"table#{endpoint.table_id}")
            if table_selector:
                table = GenericTable(table_selector[0])
                standings.extend(row.to_dict() for row in table.rows)
        return standings
