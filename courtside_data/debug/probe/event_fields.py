"""Low-level helpers that pull individual values out of debug events.

Each function reads a single field or derives a small value from a trace event,
header mapping, table selector, or stacktrace. They are shared by the event
summary walker and the trace enrichment helpers.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

_TRACEBACK_TAIL_LINES = 20

_HTTP_RESPONSE_EVENTS = frozenset({"attempt_response", "status_error", "request_complete"})


def _event_attributes(event: Mapping[str, Any]) -> dict[str, Any]:
    attributes = event.get("attributes")
    return dict(attributes) if isinstance(attributes, dict) else {}


def _event_label(event: Mapping[str, Any]) -> str:
    stage = event.get("stage")
    name = event.get("event")
    return f"{stage}/{name}" if stage and name else str(name or stage or "")


def _content_type_from_headers(headers: Any) -> str | None:
    if not isinstance(headers, dict):
        return None
    for key, value in headers.items():
        if str(key).lower() == "content-type":
            return str(value)
    return None


def _validation_error_paths(errors: Any) -> list[str]:
    if not isinstance(errors, list):
        return []
    paths: list[str] = []
    for error in errors:
        if not isinstance(error, dict):
            continue
        location = error.get("loc")
        if isinstance(location, (list, tuple)):
            paths.append(".".join(str(part) for part in location))
        elif location is not None:
            paths.append(str(location))
    return paths


def _traceback_tail(stacktrace: str | None) -> str | None:
    if not stacktrace:
        return None
    lines = stacktrace.splitlines()
    if not lines:
        return None
    tail = lines[-_TRACEBACK_TAIL_LINES:]
    return "\n".join(tail)


def _traceback_hash(stacktrace: str | None) -> str | None:
    if not stacktrace:
        return None
    return hashlib.sha256(stacktrace.encode("utf-8")).hexdigest()[:16]


def _table_id_from_selector(selector: Any) -> str | None:
    if not isinstance(selector, str):
        return None
    prefix = "table[@id="
    if selector.startswith(prefix) and selector.endswith("]"):
        rendered = selector[len(prefix) : -1]
        return rendered.strip("'\"")
    return None
