"""Runtime context, redaction, and severity helpers."""

from __future__ import annotations

import os
import platform
import socket
from collections.abc import Iterable
from importlib import metadata
from typing import Any

from courtside_data.debug.config import DebugConfig


def _runtime_context(config: DebugConfig) -> dict[str, Any]:
    """Build runtime-environment metadata dict (or empty if disabled)."""
    if not config.include_runtime:
        return {}
    try:
        package_version = metadata.version("courtside-data")
    except metadata.PackageNotFoundError:
        package_version = None
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "package_version": package_version,
        "service.name": "courtside-data",
        "service.version": package_version,
        "telemetry.sdk.name": "courtside_data.debug",
        "telemetry.sdk.language": "python",
        "telemetry.sdk.version": package_version,
        "instrumentation_scope.name": "courtside_data.debug",
        "instrumentation_scope.version": package_version,
        "process.pid": os.getpid(),
        "process.runtime.name": platform.python_implementation(),
        "process.runtime.version": platform.python_version(),
        "host.name": socket.gethostname(),
    }


def _should_redact(key: str, redact_keys: Iterable[str]) -> bool:
    """Check whether *key* should be redacted based on *redact_keys* patterns."""
    normalized = key.lower().replace("_", "-")
    return any(redact_key.lower().replace("_", "-") in normalized for redact_key in redact_keys)


def _severity_for_status(status: str) -> tuple[str, int]:
    """Map a status string to an OpenTelemetry-style (text, number) severity."""
    if status == "error":
        return "ERROR", 17
    if status == "cancelled":
        return "WARN", 13
    return "INFO", 9
