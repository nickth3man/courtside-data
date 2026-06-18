"""Configuration and constants for structured debug traces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DEFAULT_REDACT_KEYS = frozenset(
    {
        "api-key",
        "api_key",
        "apikey",
        "authorization",
        "cookie",
        "password",
        "proxy-authorization",
        "secret",
        "set-cookie",
        "token",
    }
)

SAFE_RESPONSE_HEADERS = frozenset(
    {
        "cache-control",
        "content-encoding",
        "content-language",
        "content-length",
        "content-type",
        "date",
        "etag",
        "expires",
        "last-modified",
        "retry-after",
        "server",
        "vary",
    }
)


@dataclass(frozen=True)
class DebugConfig:
    """Controls trace size, redaction, and artifact sampling."""

    max_events: int | None = 500
    max_artifact_items: int | None = 50
    max_string_length: int | None = 4000
    max_depth: int | None = 8
    include_artifacts: bool = True
    include_stacktraces: bool = True
    include_runtime: bool = True
    include_row_diagnostics: bool = True
    artifact_sample: Literal["head", "tail", "head_tail"] = "head_tail"
    max_column_examples: int = 5
    redact_keys: frozenset[str] = DEFAULT_REDACT_KEYS
    safe_response_headers: frozenset[str] = SAFE_RESPONSE_HEADERS
    profile: bool = False
    profile_interval: float = 0.001
