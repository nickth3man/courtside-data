# Rate Limiting Optimization Plan for courtside-data

## Context

Basketball-Reference enforces rate limits via Cloudflare:
- **Official limit:** 20 requests/minute (all Sports-Reference sites except FBref/Stathead, which are 10/min)
- **Effective safe rate:** ~10 req/min based on `pybaseball` production experience
- **Penalty:** Session jailed for 1 hour (bots) to 24 hours (severe/repeat)
- **robots.txt:** `Crawl-delay: 3`
- **Rate-limiting provider:** Cloudflare (Error 1015)
- **Jail trigger:** Exceeding 20 req/min OR sending bot-like TLS fingerprints/headers

### Current State of `courtside_data/http_service.py`

| Feature | Current Value | Status |
|---|---|---|
| Rate limit interval | `3.5s` + `1.2s` jitter (~14 req/min) | Safe but conservative |
| Retry logic | `stamina` with 3 attempts, exponential backoff | Good |
| Retry-After handling | Parses both integer + HTTP-date, capped at 60s | Good but cap is wasteful on long jails |
| Thread safety | `ClassVar[threading.Lock]` + `_last_request_time` | Has a race condition |
| Caching | Optional via `hishel` (`SyncCacheTransport`) | Good but not default |
| User-Agent | **None** (defaults to `python-httpx/0.XX`) | Critical gap |
| Browser headers | **None** | Critical gap |
| TLS fingerprint | `python-httpx` default (easily flagged) | Gap |
| Circuit breaker | **None** (no memory between `_get` calls) | Gap |
| Cloudflare 403 handling | **Not retried** (only 429/502/503/504) | Gap |

### Inconsistency: Scripts vs. Library

| Component | User-Agent | Extra Headers |
|---|---|---|
| `scripts/diagnose_comments.py:19` | Full Chrome 120 UA | `Accept`, `Accept-Language`, `Accept-Encoding`, `Sec-Fetch-*`, `DNT`, `Connection`, `Upgrade-Insecure-Requests` |
| `scripts/refresh_fixtures.py:22` | Full Chrome 124 UA | None |
| `scripts/diagnose_failing.py:17` | Partial Chrome UA | None |
| **`courtside_data/http_service.py`** | **None** | **None** |

The production library sends the most suspicious headers. The diagnostic scripts send the most benign ones. This is backwards.

---

## Research Sources

### Libraries Analyzed

| Library | Stars | Rate Limiting | Notable Technique |
|---|---|---|---|
| `vishaalagartha/basketball_reference_scraper` | 291 | 3s delay, Retry-After sleep loop | Bare `requests.get()` — zero headers |
| `jaebradley/basketball_reference_web_scraper` | 546 | **None** | No rate limiting at all |
| `roclark/sportsipy` | 558 | **None** (abandoned 2021) | Cross-sport (NBA/MLB/NFL/NHL) |
| `jldbc/pybaseball` | 1,700 | **10 req/min** singleton `BRefSession` | `requests.Session` — conservative rate, no TLS impersonation |
| `swar/nba_api` | 1,900 | Internal (stats.nba.com, not b-ref) | Chrome UA + session reuse |

### Key Findings

1. **`pybaseball` is the gold standard for rate limiting.** It conservatively caps at 10 req/min (half the official limit) because community testing showed 20 req/min still triggers blocks. **Correction:** `pybaseball` uses plain `requests.Session` — NOT `curl_cffi` for TLS impersonation. The TLS fingerprinting claim applies to `yfinance` and `yt-dlp`, not `pybaseball`.

2. **TLS fingerprinting is the silent killer.** Cloudflare identifies `python-httpx` and `requests` by their JA3/JA4 TLS signatures before headers are even sent. `curl_cffi` (used by `yfinance`, `yt-dlp`) impersonates Chrome's TLS handshake at the C library level. **`pybaseball` survives without TLS impersonation** by being extremely conservative with request rate (10 req/min).

3. **No existing library sends `Sec-Fetch-*` or `Sec-CH-UA` headers.** This is an untapped optimization. `diagnose_comments.py` already has a working header set that includes these.

4. **Community consensus on delay:** 3-5 seconds between requests. The 3.5s default is within range.

5. **No data mirrors exist.** Sports-Reference's data use policy explicitly prohibits redistribution. Alternative sources (nba_api for stats.nba.com, balldontlie.io) cover different data.

6. **Jail recovery:** No library has a sophisticated recovery mechanism. The universal pattern is: read `Retry-After`, sleep, retry. `pybaseball` simply prevents hitting the limit in the first place.

7. **No library handles Cloudflare 403.** All existing scrapers only handle 429. Cloudflare challenge pages return 403, which is currently classified as "do not retry" in `_should_retry`.

---

## Phase 1: Headers and Timing Fixes (High Priority, Low Effort)

### 1A. Add Default Headers to `build_client()`

**File:** `courtside_data/http_service.py` lines 99-108

**Current:**
```python
def build_client(cache: bool = False, timeout: httpx.Timeout = _DEFAULT_TIMEOUT) -> httpx.Client:
    transport: httpx.BaseTransport = httpx.HTTPTransport()
    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(transport=transport, follow_redirects=True, timeout=timeout)
```

**Proposed:** Add a `_DEFAULT_HEADERS` constant and pass it to `httpx.Client`:
```python
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

def build_client(
    cache: bool = False,
    timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
    headers: dict[str, str] | None = None,
) -> httpx.Client:
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    transport: httpx.BaseTransport = httpx.HTTPTransport()
    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(
        transport=transport,
        follow_redirects=True,
        timeout=timeout,
        headers=merged,
    )
```

**Rationale:**
- Matches the header set already proven to work in `diagnose_comments.py:18-30`
- `Sec-Fetch-*` headers tell Cloudflare this looks like a real navigation event
- `Referer` is omitted (real browsers send no `Referer` on initial navigation)
- `Accept-Encoding` is omitted (`httpx`'s transport layer sets it automatically)
- `DNT: 1` matches the proven `diagnose_comments.py` header set
- `Sec-Fetch-Site: none` is correct for initial navigation (matching `diagnose_comments.py`)
- `headers` parameter allows users to override or extend defaults
- Updates `__init__` constructor to pass `headers` through to `build_client`

**Note:** `_get_html()`, `_get_selector()`, `player_box_scores()`, and `search()` all call `raise_for_status()` redundantly since `_get()` already raises inside the retry loop. These can be cleaned up as part of Phase 1 work.

**Tests to update:**
- `tests/unit/test_http_service.py:TestHTTPServiceSessionReuse` — verify default session has correct headers
- New test: `test_default_headers_include_user_agent` — assert `User-Agent` is set
- New test: `test_custom_headers_override_defaults` — assert user-provided headers win

### 1B. Fix Concurrency Race in `_apply_rate_limiting()`

**File:** `courtside_data/http_service.py` lines 152-159

**Current:**
```python
def _apply_rate_limiting(self) -> None:
    current_time = self._time()               # OUTSIDE lock — race condition
    with self._rate_limit_lock:
        time_since_last = current_time - self.__class__._last_request_time
        if self._rate_limit_interval > 0 and time_since_last < self._rate_limit_interval:
            jitter = self._random(0.0, self._rate_limit_jitter)
            self._sleep((self._rate_limit_interval - time_since_last) + jitter)
        self.__class__._last_request_time = self._time()
```

**Problem:** Two threads calling `_apply_rate_limiting` concurrently both read `current_time` before either acquires the lock. Both compute the same `time_since_last` and both sleep for the same duration. The second thread's sleep is wasted — it should have measured from when the first thread actually fired.

**Proposed:**
```python
def _apply_rate_limiting(self) -> None:
    with self._rate_limit_lock:
        current_time = self._time()           # INSIDE lock — no race
        time_since_last = current_time - self.__class__._last_request_time
        if self._rate_limit_interval > 0 and time_since_last < self._rate_limit_interval:
            jitter = self._random(0.0, self._rate_limit_jitter)
            self._sleep((self._rate_limit_interval - time_since_last) + jitter)
        self.__class__._last_request_time = self._time()
```

**Note:** Setting `_last_request_time` after the sleep (not before) is intentional — this ensures the next request waits a full interval from when the current one completed, not from when it started. The existing test mock expectations at `tests/unit/test_http_service.py:100-102` already use 4 `mock_time` values for 2 `_get` calls (2 per `_apply_rate_limiting`), so the fix does not require test mock changes.

**Tests to update:**
- `tests/unit/test_http_service.py:TestHTTPServiceRateLimiting` — time mock now expects 2 calls per `_apply_rate_limiting` (both inside lock), not 1 outside + 1 inside
- `test_second_request_sleeps_when_interval_requires` (line 96): `mock_time` side_effect changes from `[0.0, 0.0, 1.0, 1.0]` to `[0.0, 0.0, 1.0, 1.0]` (same values, but both are now inside the lock)
- `test_jitter_is_added_to_sleep_time` (line 139): same adjustment

### 1C. Switch to `time.monotonic`

**File:** `courtside_data/http_service.py` line 148

**Current:** `self._time = time_func if time_func is not None else time.time`

**Proposed:** `self._time = time_func if time_func is not None else time.monotonic`

**Rationale:** `time.time()` is wall-clock and can jump backward from NTP adjustments. `time.monotonic()` only moves forward and is correct for measuring intervals. Tests inject their own `time_func` so this doesn't break any tests.

**No test changes needed** — tests inject `mock_time` which replaces the default.

---

## Phase 2: Tiered Retry-After and Circuit Breaker (Medium Priority)

### 2A. Tiered Retry-After Handling

**File:** `courtside_data/http_service.py` lines 79-96

**Current behavior:** All `Retry-After` values are capped at 60s, then retried up to 3 times. A 3600s jail results in: 60s sleep → retry → 429 again → backoff → retry → 429 again → raise. Total waste: ~90s for a doomed request.

**Proposed:**

```python
_JAIL_THRESHOLD_SECONDS = 300.0  # 5 minutes — if Retry-After > this, we're jailed

def _should_retry(exc: Exception) -> bool | float:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in (429, 502, 503, 504):
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after is not None:
                parsed = _parse_retry_after(retry_after)
                if parsed > _JAIL_THRESHOLD_SECONDS:
                    return False  # We're jailed — don't burn retries, let caller handle
                return min(parsed, _MAX_RETRY_AFTER_WAIT)
            return True
        return False
    return False
```

**New error class in `courtside_data/errors.py`:**
```python
class RateLimitJailed(Exception):
    """Raised when Basketball-Reference has jailed the session (Retry-After > 5 minutes)."""
    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        message = (
            f"Session jailed by Basketball-Reference. "
            f"Retry-After: {retry_after:.0f}s ({retry_after / 60:.1f} minutes). "
            f"Back off and retry later."
        )
        super().__init__(message)
```

**Note:** `RateLimitJailed` must be caught in `_call_with_error_mapping` at `client.py:37`, which currently only catches `httpx.HTTPStatusError`. Add `except RateLimitJailed` handling before the existing `except httpx.HTTPStatusError` clause to ensure jail errors are properly mapped rather than surfacing as unhandled exceptions.

**Note:** stamina's `on`-predicate float return is used verbatim as the retry delay (confirmed by stamina source code, `stamina._core` lines 618-641). The `_should_retry` → `float` → stamina pipeline is correct as proposed.

**In `_get()`:** Catch `stamina`'s final exception after retries exhausted. If the last error was a 429 with a large `Retry-After`, raise `RateLimitJailed` instead of the raw `HTTPStatusError`.

**Tests to update:**
- `TestShouldRetryRetryAfterCap` — add `test_huge_retry_after_returns_false` (previously returned `_MAX_RETRY_AFTER_WAIT`, now returns `False`)
- New test: `test_jail_threshold_boundary` — assert `_should_retry` returns `False` at exactly 300s
- New test: `test_retry_after_below_threshold_honored` — assert 60s Retry-After still works

### 2B. Lightweight Circuit Breaker

**File:** `courtside_data/http_service.py`

**Add class-level state:**
```python
class HTTPService:
    _last_request_time: ClassVar[float] = float("-inf")
    _jailed_until: ClassVar[float] = 0.0  # monotonic timestamp; 0 = not jailed
    _rate_limit_lock: ClassVar[threading.RLock] = threading.RLock()
```

**Modify `_apply_rate_limiting()`:**
```python
def _apply_rate_limiting(self) -> None:
    with self._rate_limit_lock:
        # Circuit breaker: if jailed, refuse all requests
        current_time = self._time()
        if current_time < self.__class__._jailed_until:
            remaining = self.__class__._jailed_until - current_time
            raise RateLimitJailed(retry_after=remaining)

        time_since_last = current_time - self.__class__._last_request_time
        if self._rate_limit_interval > 0 and time_since_last < self._rate_limit_interval:
            jitter = self._random(0.0, self._rate_limit_jitter)
            self._sleep((self._rate_limit_interval - time_since_last) + jitter)
        self.__class__._last_request_time = self._time()
```

**Modify `_get()` to set jail on 429 with large Retry-After:**
```python
def _get(self, url: str, **kwargs: Any) -> httpx.Response:
    self._apply_rate_limiting()
    response = None
    for attempt in stamina.retry_context(
        on=_should_retry,
        attempts=_RETRY_ATTEMPTS,
        wait_initial=1.0,
        wait_max=10.0,
        wait_jitter=0.5,
    ):
        with attempt:
            response = self._session.get(url=url, **kwargs)
            response.raise_for_status()
    assert response is not None
    return response
```

**Note:** The `_get()` method must include an `except httpx.HTTPStatusError` block that inspects 429 responses and sets `_jailed_until` when `Retry-After` exceeds the jail threshold. The circuit breaker cannot rely on the caller (`client.py`) because `HTTPService` is instantiated per-call in `client.py:121-125`. Also note that `_jailed_until` is a `ClassVar`, so test isolation requires resetting it in `setUp` (similar to how `TestHTTPServiceRateLimiting.setUp` resets `_last_request_time`).

The jail is set via `_should_retry` returning `False` for large `Retry-After`, which causes `stamina` to raise the original `HTTPStatusError`. The `_get()` method catches this `HTTPStatusError` and inspects the response to set `_jailed_until`.

**Alternative approach (simpler):** Add a `_consecutive_429s` counter. If 3 consecutive requests return 429, set `_jailed_until = now + 300`. Reset on any successful response.

**Tests to update:**
- New test class `TestHTTPServiceCircuitBreaker`:
  - `test_jailed_requests_raise_immediately`
  - `test_jail_expires_after_duration`
  - `test_successful_request_clears_jail`
  - `test_jail_is_shared_across_instances` (class-level state)

### 2C. Reset Pacing After Retry-After Sleep

**Problem:** When a request gets a 429 and sleeps for 60s (via stamina's retry), `_last_request_time` was set before the sleep. The next request might skip its pre-request pause because it thinks 60s have elapsed since the last request — but the "last request" was a failed one, not a successful one.

**Proposed:** After a successful response in `_get()`, update `_last_request_time`:
```python
def _get(self, url: str, **kwargs: Any) -> httpx.Response:
    self._apply_rate_limiting()
    response = None
    for attempt in stamina.retry_context(...):
        with attempt:
            response = self._session.get(url=url, **kwargs)
            response.raise_for_status()
    assert response is not None
    # Reset pacing — the retries consumed time, so the next request
    # should measure from now, not from the original attempt.
    with self._rate_limit_lock:
        self.__class__._last_request_time = self._time()
    return response
```

**Note:** `_rate_limit_lock` has been changed from `threading.Lock` to `threading.RLock` (see Phase 2B) to future-proof against reentrant access patterns (e.g., if `search()` pagination is ever parallelized). The pacing reset itself is correct: after a 429 → 60s sleep → retry → success, `_last_request_time` should reset to "now" so the next request waits a full interval rather than skipping its pause due to elapsed time.

---

## Phase 3: TLS Impersonation (High Impact, Higher Effort)

### 3A. Optional `curl_cffi` Integration

**Dependency:** Add `curl_cffi` as an optional dependency (not replacing `httpx`).

**In `pyproject.toml`:**
```toml
[project.optional-dependencies]
stealth = ["curl_cffi>=0.7.0"]
```

**In `http_service.py`:**
```python
def build_client(
    cache: bool = False,
    timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
    headers: dict[str, str] | None = None,
    impersonate: str | None = None,
) -> httpx.Client:
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    transport: httpx.BaseTransport = httpx.HTTPTransport()

    if impersonate:
        try:
            from curl_cffi.requests import Session as CurlSession
            # Wrap curl_cffi session to match httpx.Client interface
            # OR: provide a separate transport that uses curl_cffi under the hood
        except ImportError:
            pass  # Fall back to standard httpx

    if cache:
        transport = SyncCacheTransport(next_transport=transport)
    return httpx.Client(transport=transport, follow_redirects=True, timeout=timeout, headers=merged)
```

**Alternative (simpler integration):** Use `curl_cffi` as a standalone session and wrap it behind the same interface as `httpx.Client`. This avoids the transport-layer complexity but requires a thin adapter.

**Note:** The `curl_cffi` session wrapping approach is complex because `curl_cffi` exposes a `requests`-compatible API, not an `httpx`-compatible one. A simpler approach is to use the third-party [`httpx-curl-cffi`](https://github.com/misuzu-dev/httpx-curl-cffi) package, which provides `CurlTransport(impersonate="chrome")` as a drop-in httpx transport. This avoids rewriting code that depends on `httpx.Response` types and keeps the `_should_retry` and `client.py` interfaces unchanged. Add `httpx-curl-cffi` to `pyproject.toml` as the optional dependency instead of raw `curl_cffi`.

**Research basis:**
- `yfinance` and `yt-dlp` use `curl_cffi` in production
- `curl_cffi` handles JA3/JA4 fingerprints, HTTP/2 settings frames, and header order matching automatically
- `curl_cffi` is actively maintained (v0.15.1b2, June 2026), 5.8k stars, pre-compiled wheels for all platforms

### 3B. `niquests` as Alternative

**If `curl_cffi` is too heavy**, `niquests` is a drop-in `requests` replacement with built-in TLS impersonation:
```python
import niquests as requests  # HTTP/2 + HTTP/3 + TLS impersonation
```

This would require refactoring away from `httpx`, so it's a larger change.

**Note:** `niquests` is actively maintained (v3.19.1, June 2026) and supports TLS impersonation via `utls`/BoringSSL since v3.19.0. However, it requires `pip install niquests[utls]` and is a `requests` replacement, not an `httpx` replacement — switching would mean losing `hishel` cache integration, `httpx.Timeout`, and the transport layer abstraction. The entire test suite would also need rewriting. Given the `hishel` dependency and test infrastructure, `httpx-curl-cffi` (Option 3A) is the lower-friction path.

---

## Phase 4: Advanced Features (Future)

### 4A. Request-Level Budget

Track requests per minute and dynamically tighten the interval if responses show soft rate-limit signals (increased latency, missing data):
```python
class HTTPService:
    _requests_this_minute: ClassVar[int] = 0
    _minute_start: ClassVar[float] = 0.0

    def _check_budget(self) -> None:
        now = self._time()
        if now - self.__class__._minute_start > 60:
            self.__class__._requests_this_minute = 0
            self.__class__._minute_start = now
        if self.__class__._requests_this_minute >= 15:  # 75% of 20 limit
            # Dynamically double the interval
            ...
```

### 4B. Cloudflare 403 Handling

Add 403 to the retryable status codes (at least once) since Cloudflare challenge pages can return 403:
```python
if code in (403, 429, 502, 503, 504):
    if code == 403:
        # Only retry 403 once — it might be a Cloudflare challenge
        return True
    ...
```

**Note:** Blind 403 retry is risky. A 403 can mean: (1) Cloudflare bot challenge (retryable), (2) legitimate access denied (not retryable), or (3) Cloudflare "I'm Under Attack" mode. Only retry 403 if the response body contains Cloudflare challenge markers (`cf-challenge`, `cf-browser-verification`). Even then, a single retry won't solve a JS challenge — TLS impersonation (Phase 3) is the real solution to avoid triggering challenges.

### 4C. Aggressive Caching

Make caching the default for production use. Currently `build_client(cache=True)` is opt-in:
```python
def __init__(self, ..., cache: bool = True) -> None:  # Default to True
```

### 4D. Configurable Retry-After Cap

Make `_MAX_RETRY_AFTER_WAIT` configurable via env var:
```python
_MAX_RETRY_AFTER_WAIT = float(os.environ.get("BASKETBALL_REF_MAX_RETRY_AFTER", "60.0"))
```

---

## Implementation Order and Effort Estimates

**Note:** Phase 3A effort estimate corrected: use `httpx-curl-cffi` adapter (~10 lines) instead of raw `curl_cffi` session wrapping (~50 lines). Phase 2A/2B require additional `client.py` changes not originally estimated.

| Phase | Item | Files Changed | Effort | Impact | Notes |
|---|---|---|---|---|---|
| **1C** | `time.monotonic` | `http_service.py` | 1 line | Low — prevents clock-drift bugs | Zero risk — tests inject mock |
| **1B** | Fix concurrency race | `http_service.py`, `test_http_service.py` | ~5 lines + test fixes | Medium — eliminates wasted sleeps | Low risk — verified test expectations |
| **1A** | Default headers in `build_client` | `http_service.py`, `http_service.py.__init__` | ~20 lines | High — reduces bot-flagging | **R5**: `Referer` on first request; **R10**: missing headers |
| **2A** | Tiered Retry-After | `http_service.py`, `errors.py`, `client.py`, `test_http_service.py` | ~25 lines | Medium — avoids wasting retries on jails | **R2**: must update `client.py` error mapping |
| **2C** | Pacing reset after retry | `http_service.py` | ~5 lines | Low — prevents pacing gap | **R7**: use `RLock` to future-proof |
| **2B** | Circuit breaker | `http_service.py`, `client.py`, `test_http_service.py` | ~40 lines | Medium — stops cascading failures | **R1**: must set `_jailed_until` inside `_get()`; update `client.py` |
| **3A** | `httpx-curl-cffi` TLS impersonation | `pyproject.toml`, `http_service.py` | ~15 lines + new dep | High — evades TLS fingerprinting | **R3/R4**: use adapter, not raw `curl_cffi` |
| **4D** | Configurable cap | `http_service.py` | ~3 lines | Low — flexibility | Env var already established pattern |
| **4C** | Default caching | `http_service.py` | 1 line | Low — fewer re-fetches | May change existing behavior for users |
| **4B** | 403 retry | `http_service.py`, `test_http_service.py` | ~10 lines | Low — handles Cloudflare challenges | **R8**: must inspect body for CF markers |
| **4A** | Request budget | `http_service.py` | ~25 lines | Low — adaptive throttling | Same `ClassVar` problem as R1; low value |

---

## Key Files Reference

| File | Role | Changes Needed |
|---|---|---|
| `courtside_data/http_service.py` | HTTP client, rate limiting, retry logic | Headers, race fix, monotonic, tiered retry, circuit breaker, pacing reset, TLS transport |
| `courtside_data/errors.py` | Custom exceptions | Add `RateLimitJailed` |
| `courtside_data/client.py` | Public API that instantiates `HTTPService` | **Must** add `RateLimitJailed` to error mapping; consider `headers` pass-through |
| `tests/unit/test_http_service.py` | Unit tests for rate limiting, retries, env vars | New tests for headers, circuit breaker, jail detection |
| `tests/e2e/live_policy.py` | Live e2e test policy (already has `LiveRateLimitExceeded`) | May need `RateLimitJailed` handling |
| `scripts/diagnose_comments.py` | Proven browser-like header set (lines 18-30) | Reference only |
| `scripts/refresh_fixtures.py` | Proven Chrome UA (line 22-24) | Reference only |
| `pyproject.toml` | Dependencies | Add `httpx-curl-cffi` optional dep |

## External References

| Source | URL |
|---|---|
| Sports-Reference bot-traffic policy | https://www.sports-reference.com/bot-traffic.html |
| Sports-Reference 429 page | https://www.sports-reference.com/429.html |
| Sports-Reference data use policy | https://www.sports-reference.com/data_use.html |
| Basketball-Reference robots.txt | https://www.basketball-reference.com/robots.txt |
| `pybaseball` BRefSession (best reference implementation) | https://github.com/jldbc/pybaseball/blob/master/pybaseball/datasources/bref.py |
| `curl_cffi` (TLS impersonation library) | https://github.com/lexiforest/curl_cffi |
| `httpx-curl-cffi` (httpx transport adapter) | https://github.com/misuzu-dev/httpx-curl-cffi |
| `vishaalagartha/basketball_reference_scraper` rate limiting | https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper/request_utils.py |
| `Scrapling` stealth headers pattern | https://github.com/D4Vinci/Scrapling |
| pipeshub-ai stealth headers pattern | https://github.com/pipeshub-ai/pipeshub-ai |
