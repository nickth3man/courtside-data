"""Common row-extraction helper shared by domain parsers.

Lives in its own module so the box-scores sub-module can reuse
:func:`raw_rows_from_table` without creating a circular dependency through the facade.
"""

from __future__ import annotations

from typing import Any

from parsel import Selector

from courtside_data.debug import current_debug_trace
from courtside_data.parsing.tables import GenericTable


def raw_rows_from_table(
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
