"""Row diagnostics mixin for observing and sanitizing data."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from courtside_data.debug._jsonish import _jsonish, _row_diagnostics, _rows_as_dicts


class RowDiagnosticsMixin:
    """Mixin that adds row observation and header sanitization.

    Requires ``DebugTraceCore`` (or equivalent) in the MRO so that
    ``self.config``, ``self.artifact()``, and ``self.record()`` are
    available.
    """

    def observe_rows(
        self,
        name: str,
        rows: Any,
        *,
        expected_columns: Iterable[str] | None = None,
    ) -> None:
        """Capture row-shape, column, nullness, and type diagnostics."""
        if not self.config.include_row_diagnostics:  # ty: ignore
            return
        row_list = _rows_as_dicts(rows)
        diagnostics = _row_diagnostics(
            row_list,
            expected_columns=tuple(expected_columns) if expected_columns is not None else None,
            max_examples=self.config.max_column_examples,  # ty: ignore
        )
        self.artifact(f"{name}_diagnostics", diagnostics)  # ty: ignore
        self.record(  # ty: ignore
            "diagnostics",
            "rows_observed",
            name=name,
            row_count=diagnostics["row_count"],
            column_count=len(diagnostics["columns"]),
            missing_expected_columns=diagnostics["missing_expected_columns"],
            extra_columns=diagnostics["extra_columns"],
        )

    def sanitize_headers(self, headers: Mapping[str, Any]) -> dict[str, Any]:
        """Return lower-cased, redacted response headers allowed by DebugConfig."""
        result: dict[str, Any] = {}
        for key, value in headers.items():
            normalized = str(key).lower()
            if normalized in self.config.safe_response_headers:  # ty: ignore
                result[normalized] = _jsonish(value, config=self.config, key=normalized)  # ty: ignore
        return result
