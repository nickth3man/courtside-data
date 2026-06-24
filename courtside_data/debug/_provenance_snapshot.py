"""Source table snapshot building and recording.

Extracts a :class:`SourceTableSnapshot` directly from a parsel
:class:`Selector` (independent of ``GenericTable``) and records the
table-level provenance onto the active :class:`DebugTrace`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from parsel import Selector

from courtside_data.debug._provenance_constants import PROVENANCE_DEBUG_UNAVAILABLE
from courtside_data.debug._provenance_context import trace_context
from courtside_data.debug._provenance_field import expected_model_source_keys
from courtside_data.debug._provenance_types import (
    SourceCell,
    SourceColumn,
    SourceTableSnapshot,
)
from courtside_data.debug.trace import DebugTrace
from courtside_data.parsing._table_shared import clean_text, normalize_header


def build_source_table_snapshot(
    table_selector: Selector,
    *,
    endpoint_name: str,
    params: Mapping[str, Any],
    table_source: str | None,
    use_header_fallback: bool,
    exclude_summary_rows: bool,
) -> SourceTableSnapshot:
    """Inspect a selected table directly, independent of ``GenericTable``."""
    fallback_headers = _fallback_headers(table_selector) if use_header_fallback else []
    columns_by_key: dict[str, SourceColumn] = {}
    raw_data_stats: list[str] = []

    for index, cell in enumerate(_header_cells(table_selector)):
        data_stat = cell.attrib.get("data-stat")
        header_text = _cell_raw_text(cell).strip() or None
        source_key = data_stat or (fallback_headers[index] if index < len(fallback_headers) else None)
        if data_stat and data_stat not in raw_data_stats:
            raw_data_stats.append(data_stat)
        if source_key and source_key not in columns_by_key:
            columns_by_key[source_key] = SourceColumn(
                source_key=source_key,
                data_stat=data_stat,
                header_text=header_text,
                column_index=index,
            )

    source_rows: list[dict[str, SourceCell]] = []
    for row_index, row in enumerate(_data_rows(table_selector, exclude_summary_rows=exclude_summary_rows)):
        row_cells: dict[str, SourceCell] = {}
        for column_index, cell in enumerate(row.css("td, th")):
            data_stat = cell.attrib.get("data-stat")
            if data_stat and data_stat not in raw_data_stats:
                raw_data_stats.append(data_stat)
            source_key = data_stat
            if source_key is None and use_header_fallback:
                source_key = (
                    fallback_headers[column_index]
                    if column_index < len(fallback_headers)
                    else f"col_{column_index + 1}"
                )
            if source_key is None:
                continue
            raw_text = _cell_raw_text(cell)
            source_column = columns_by_key.get(source_key)
            header_text = source_column.header_text if source_column is not None else None
            if source_key not in columns_by_key:
                columns_by_key[source_key] = SourceColumn(
                    source_key=source_key,
                    data_stat=data_stat,
                    header_text=header_text,
                    column_index=column_index,
                )
            row_cells[source_key] = SourceCell(
                source_key=source_key,
                data_stat=data_stat,
                header_text=header_text,
                row_index=row_index,
                column_index=column_index,
                raw_text=raw_text,
                normalized_text=clean_text([raw_text]).replace("*", "").strip(),
            )
        if row_cells:
            source_rows.append(row_cells)

    return SourceTableSnapshot(
        endpoint_name=endpoint_name,
        params=dict(params),
        source_table_id=table_selector.attrib.get("id"),
        table_source=table_source,
        source_columns=sorted(columns_by_key.values(), key=lambda item: item.column_index),
        raw_data_stat_columns=raw_data_stats,
        rows=source_rows,
        row_count=len(source_rows),
    )


def record_table_provenance(
    trace: DebugTrace,
    *,
    snapshot: SourceTableSnapshot,
    row_model: Any | None,
    parser_rows_before_projection: Sequence[Mapping[str, Any]],
    parser_rows_after_projection: Sequence[Mapping[str, Any]],
) -> None:
    parser_before = _columns_from_rows(parser_rows_before_projection)
    parser_after = _columns_from_rows(parser_rows_after_projection)
    expected = expected_model_source_keys(row_model) if row_model is not None else []
    source_keys = sorted(snapshot.source_keys)
    parser_missed = sorted(key for key in source_keys if key not in parser_before)
    parser_extra = sorted(key for key in parser_after if expected and key not in expected)
    schema_absent = sorted(key for key in expected if key not in parser_after)

    context = trace_context(trace)
    context.source_snapshot = snapshot
    context.parser_columns_before_projection = parser_before
    context.parser_columns_after_projection = parser_after
    context.expected_source_keys = expected
    context.parser_missed_columns = parser_missed
    context.parser_extra_columns = parser_extra
    context.schema_aliases_absent_from_parser = schema_absent

    trace.artifact("source_table_provenance", snapshot.to_artifact())
    trace.record(
        "provenance",
        "source_table_provenance",
        selected_table_id=snapshot.source_table_id,
        table_source=snapshot.table_source,
        source_row_count=snapshot.row_count,
        source_column_count=len(source_keys),
        source_data_stat_columns=snapshot.raw_data_stat_columns,
        parser_columns_before_projection=parser_before,
        parser_columns_after_projection=parser_after,
        expected_source_keys=expected,
        parser_extra_columns=parser_extra,
        schema_aliases_absent_from_parser=schema_absent,
        parser_missed_columns=parser_missed,
        parser_missed_column_count=len(parser_missed),
    )


def record_unavailable_table_provenance(trace: DebugTrace, *, reason: str) -> None:
    trace.record(
        "provenance",
        "source_table_provenance_unavailable",
        reason=reason,
        provenance_reason=PROVENANCE_DEBUG_UNAVAILABLE,
    )


def _columns_from_rows(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    return sorted({str(key) for row in rows for key in row})


def _fallback_headers(table_selector: Selector) -> list[str]:
    for row in table_selector.css("tr"):
        cells = row.css("td, th")
        if cells and not row.css("td") and row.css("th"):
            return [
                normalize_header(cell.attrib.get("data-stat") or cell.css("::text").get("") or "") for cell in cells
            ]
    return []


def _header_cells(table_selector: Selector) -> list[Selector]:
    cells: list[Selector] = []
    for row in table_selector.css("thead tr"):
        row_cells = list(row.css("td, th"))
        if row_cells:
            cells = row_cells
    if cells:
        return cells
    for row in table_selector.css("tr"):
        row_cells = list(row.css("td, th"))
        if row_cells and (not row.css("td") or any(cell.attrib.get("data-stat") for cell in row_cells)):
            return row_cells
    return []


def _data_rows(table_selector: Selector, *, exclude_summary_rows: bool) -> list[Selector]:
    row_filter = "tbody tr:not(.thead)"
    if exclude_summary_rows:
        row_filter += ":not(.norank)"
    rows = list(table_selector.css(row_filter))
    if not rows:
        row_filter = "tr:not(.thead)"
        if exclude_summary_rows:
            row_filter += ":not(.norank)"
        rows = list(table_selector.css(row_filter))
    return [row for row in rows if not _is_header_row(row)]


def _is_header_row(row: Selector) -> bool:
    cells = row.css("td, th")
    return bool(cells) and not row.css("td") and bool(row.css("th"))


def _cell_raw_text(cell: Selector) -> str:
    return "".join(cell.xpath(".//text()").getall()).replace("*", "")
