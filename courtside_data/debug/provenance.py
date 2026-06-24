"""Debug-only source/value provenance helpers.

The helpers in this module are intentionally internal to the debug/probe
surface. They collect evidence about the path from Basketball-Reference table
cells to parser rows to Pydantic row models, without changing the values the
public endpoint APIs return.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Literal
from weakref import WeakKeyDictionary

from parsel import Selector
from pydantic import AliasChoices, AliasPath
from pydantic_core import PydanticUndefined

from courtside_data.client._pipelines._drop_reasons import (
    EXPECTED_DROP_REASONS,
    UNRESOLVED_DROP_REASONS,
    row_drop_reason,
    validation_error_drop_reason,
)
from courtside_data.debug.trace import DebugTrace
from courtside_data.parsing._table_shared import clean_text, normalize_header

PROVENANCE_SOURCE_VALUE_PRESENT = "source_value_present"
PROVENANCE_SOURCE_COLUMN_ABSENT = "source_column_absent"
PROVENANCE_SOURCE_CELL_BLANK = "source_cell_blank"
PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL = "source_cell_dash_or_sentinel"
PROVENANCE_PARSER_EMITTED_VALUE = "parser_emitted_value"
PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN = "parser_omitted_present_column"
PROVENANCE_SCHEMA_DEFAULT_USED = "schema_default_used"
PROVENANCE_VALIDATOR_COERCED_TO_NONE = "validator_coerced_to_none"
PROVENANCE_VALIDATOR_TRANSFORMED_VALUE = "validator_transformed_value"
PROVENANCE_ROW_DROPPED_EXPECTED_REASON = "row_dropped_expected_reason"
PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR = "row_dropped_unresolved_validation_error"
PROVENANCE_CUSTOM_PARSER_VALUE = "custom_parser_value"
PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE = "custom_parser_metadata_unavailable"
PROVENANCE_DEBUG_UNAVAILABLE = "debug_provenance_unavailable"
PROVENANCE_UNKNOWN = "unknown"

ProvenanceReason = Literal[
    "source_value_present",
    "source_column_absent",
    "source_cell_blank",
    "source_cell_dash_or_sentinel",
    "parser_emitted_value",
    "parser_omitted_present_column",
    "schema_default_used",
    "validator_coerced_to_none",
    "validator_transformed_value",
    "row_dropped_expected_reason",
    "row_dropped_unresolved_validation_error",
    "custom_parser_value",
    "custom_parser_metadata_unavailable",
    "debug_provenance_unavailable",
    "unknown",
]

_DASH_OR_SENTINEL_VALUES = frozenset({"-", "\u2013", "\u2014", "n/a", "na", "none"})
_TRACE_CONTEXTS: WeakKeyDictionary[DebugTrace, ProvenanceContext] = WeakKeyDictionary()
_SAMPLE_LIMIT = 5


@dataclass(frozen=True, slots=True)
class SourceColumn:
    """One independently observed table column."""

    source_key: str
    data_stat: str | None
    header_text: str | None
    column_index: int


@dataclass(frozen=True, slots=True)
class SourceCell:
    """One independently observed table cell."""

    source_key: str
    data_stat: str | None
    header_text: str | None
    row_index: int
    column_index: int
    raw_text: str
    normalized_text: str


@dataclass(frozen=True, slots=True)
class SourceTableSnapshot:
    """Independent source-table evidence for one selected table."""

    endpoint_name: str
    params: dict[str, Any]
    source_table_id: str | None
    table_source: str | None
    source_columns: list[SourceColumn]
    raw_data_stat_columns: list[str]
    rows: list[dict[str, SourceCell]]
    row_count: int

    @property
    def source_keys(self) -> set[str]:
        return {column.source_key for column in self.source_columns}

    @property
    def columns_by_key(self) -> dict[str, SourceColumn]:
        return {column.source_key: column for column in self.source_columns}

    def cell(self, row_index: int, source_key: str) -> SourceCell | None:
        if row_index < 0 or row_index >= len(self.rows):
            return None
        return self.rows[row_index].get(source_key)

    def to_artifact(self) -> dict[str, Any]:
        return {
            "endpoint_name": self.endpoint_name,
            "params": self.params,
            "source_table_id": self.source_table_id,
            "table_source": self.table_source,
            "row_count": self.row_count,
            "raw_data_stat_columns": self.raw_data_stat_columns,
            "source_columns": [asdict(column) for column in self.source_columns],
            "rows": [
                {
                    key: {
                        "data_stat": cell.data_stat,
                        "header_text": cell.header_text,
                        "raw_text": cell.raw_text,
                        "normalized_text": cell.normalized_text,
                    }
                    for key, cell in row.items()
                }
                for row in self.rows
            ],
        }


@dataclass(slots=True)
class ProvenanceContext:
    """Live debug provenance context associated with a trace."""

    source_snapshot: SourceTableSnapshot | None = None
    parser_columns_before_projection: list[str] = field(default_factory=list)
    parser_columns_after_projection: list[str] = field(default_factory=list)
    expected_source_keys: list[str] = field(default_factory=list)
    parser_missed_columns: list[str] = field(default_factory=list)
    parser_extra_columns: list[str] = field(default_factory=list)
    schema_aliases_absent_from_parser: list[str] = field(default_factory=list)


def trace_context(trace: DebugTrace) -> ProvenanceContext:
    context = _TRACE_CONTEXTS.get(trace)
    if context is None:
        context = ProvenanceContext()
        _TRACE_CONTEXTS[trace] = context
    return context


def get_trace_context(trace: DebugTrace | None) -> ProvenanceContext | None:
    if trace is None:
        return None
    return _TRACE_CONTEXTS.get(trace)


def accepted_input_keys(field_name: str, field_info: Any, *, include_field_name: bool = True) -> list[str]:
    """Return the flat parser keys Pydantic will accept for a model field."""
    keys: list[str] = []

    def add(value: object) -> None:
        if isinstance(value, str) and value not in keys:
            keys.append(value)

    alias = getattr(field_info, "validation_alias", None)
    if isinstance(alias, str):
        add(alias)
    elif isinstance(alias, AliasChoices):
        for choice in alias.choices:
            if isinstance(choice, str):
                add(choice)
            elif isinstance(choice, AliasPath) and len(choice.path) == 1:
                add(str(choice.path[0]))
    elif isinstance(alias, AliasPath) and len(alias.path) == 1:
        add(str(alias.path[0]))

    if include_field_name:
        add(field_name)
    return keys


def expected_model_source_keys(row_model: Any) -> list[str]:
    keys: list[str] = []
    for field_name, field_info in row_model.model_fields.items():
        for key in accepted_input_keys(field_name, field_info, include_field_name=False) or [field_name]:
            if key not in keys:
                keys.append(key)
    return keys


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


def build_field_provenance_records(
    *,
    endpoint_name: str | None,
    endpoint_params: Mapping[str, Any] | None,
    row_model: Any,
    raw_rows: Sequence[Mapping[str, Any]],
    validated_rows: Sequence[Any],
    kept_row_indices: Sequence[int],
    context: ProvenanceContext | None,
    custom: bool,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    snapshot = context.source_snapshot if context is not None else None

    for validated, raw_index in zip(validated_rows, kept_row_indices, strict=False):
        parser_row = raw_rows[raw_index] if raw_index < len(raw_rows) else {}
        for field_name, field_info in row_model.model_fields.items():
            records.append(
                _field_record(
                    endpoint_name=endpoint_name,
                    endpoint_params=endpoint_params,
                    row_model=row_model,
                    field_name=field_name,
                    field_info=field_info,
                    parser_row=parser_row,
                    raw_row_index=raw_index,
                    validated=validated,
                    snapshot=snapshot,
                    custom=custom,
                )
            )
    return records


def build_dropped_row_provenance_records(
    *,
    endpoint_name: str | None,
    endpoint_params: Mapping[str, Any] | None,
    raw_rows: Sequence[Mapping[str, Any]],
    dropped: Sequence[Mapping[str, Any]],
    context: ProvenanceContext | None,
    custom: bool,
) -> list[dict[str, Any]]:
    snapshot = context.source_snapshot if context is not None else None
    records: list[dict[str, Any]] = []
    for drop in dropped:
        row_index = int(drop["row_index"])
        row = raw_rows[row_index] if 0 <= row_index < len(raw_rows) else {}
        reason = str(drop["reason"])
        errors = list(drop.get("errors") or [])
        fields = _validation_error_fields(errors)
        raw_values = {field_name: row.get(field_name) for field_name in fields if field_name in row}
        source_cells: dict[str, Any] = {}
        if snapshot is not None:
            for field_name in fields:
                cell = snapshot.cell(row_index, field_name)
                if cell is not None:
                    source_cells[field_name] = {
                        "source_data_stat": cell.data_stat,
                        "source_header_text": cell.header_text,
                        "source_cell_raw": cell.raw_text,
                    }
        unresolved = bool(drop.get("unresolved"))
        records.append(
            {
                "endpoint_name": endpoint_name,
                "params": dict(endpoint_params or {}),
                "row_index": row_index,
                "raw_row": dict(row),
                "validation_errors": errors,
                "row_drop_reason": row_drop_reason(dict(row)),
                "validation_error_drop_reason": reason,
                "expected_drop": not unresolved,
                "unresolved_drop": unresolved,
                "fields_involved": fields,
                "raw_values": raw_values,
                "source_cells": source_cells,
                "custom": custom,
                "provenance_reason": (
                    PROVENANCE_ROW_DROPPED_UNRESOLVED_VALIDATION_ERROR
                    if unresolved
                    else PROVENANCE_ROW_DROPPED_EXPECTED_REASON
                ),
            }
        )
    return records


def emit_field_provenance(
    trace: DebugTrace,
    *,
    field_records: Sequence[Mapping[str, Any]],
    dropped_records: Sequence[Mapping[str, Any]],
) -> None:
    summary = summarize_provenance(field_records=field_records, dropped_records=dropped_records)
    detail_records = list(field_records)
    detail_drops = list(dropped_records)
    if trace.config.detail_level != "full":
        detail_records = _sample_records_by_reason(detail_records)
        detail_drops = _sample_records_by_reason(detail_drops)

    trace.artifact("field_provenance", detail_records)
    if detail_drops:
        trace.artifact("dropped_row_provenance", detail_drops)
    trace.record("provenance", "field_provenance_summary", **summary)


def summarize_provenance(
    *,
    field_records: Sequence[Mapping[str, Any]],
    dropped_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    reason_counts: Counter[str] = Counter(
        str(record.get("provenance_reason") or PROVENANCE_UNKNOWN) for record in field_records
    )
    none_reason_counts: Counter[str] = Counter(
        str(record.get("provenance_reason") or PROVENANCE_UNKNOWN)
        for record in field_records
        if record.get("final_value") is None
    )
    dropped_reason_counts: Counter[str] = Counter(
        str(record.get("validation_error_drop_reason") or record.get("row_drop_reason") or PROVENANCE_UNKNOWN)
        for record in dropped_records
    )
    parser_missed = sum(
        1 for record in field_records if record.get("provenance_reason") == PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN
    )
    return {
        "provenance_field_count": len(field_records),
        "provenance_final_none_count": sum(1 for record in field_records if record.get("final_value") is None),
        "provenance_reason_counts": dict(sorted(reason_counts.items())),
        "provenance_none_reason_counts": dict(sorted(none_reason_counts.items())),
        "parser_missed_column_count": parser_missed,
        "schema_defaulted_field_count": sum(1 for record in field_records if record.get("schema_default_used") is True),
        "validator_coerced_field_count": sum(
            1 for record in field_records if record.get("validator_coerced_to_none") is True
        ),
        "validator_transformed_field_count": sum(
            1 for record in field_records if record.get("validator_transformed") is True
        ),
        "provenance_dropped_row_count": len(dropped_records),
        "provenance_dropped_row_reason_counts": dict(sorted(dropped_reason_counts.items())),
        "provenance_unresolved_drop_count": sum(
            1 for record in dropped_records if record.get("unresolved_drop") is True
        ),
        "custom_provenance_unavailable_count": sum(
            1
            for record in field_records
            if record.get("provenance_reason") == PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE
        ),
    }


def _field_record(
    *,
    endpoint_name: str | None,
    endpoint_params: Mapping[str, Any] | None,
    row_model: Any,
    field_name: str,
    field_info: Any,
    parser_row: Mapping[str, Any],
    raw_row_index: int,
    validated: Any,
    snapshot: SourceTableSnapshot | None,
    custom: bool,
) -> dict[str, Any]:
    aliases = accepted_input_keys(field_name, field_info)
    source_aliases = accepted_input_keys(field_name, field_info, include_field_name=False) or [field_name]
    matched_key = next((key for key in aliases if key in parser_row), None)
    pydantic_input_present = matched_key is not None
    pydantic_input_value = parser_row.get(matched_key) if matched_key is not None else None
    final_value = getattr(validated, field_name, None)
    schema_default_used = not pydantic_input_present and _field_has_default(field_info)
    source_key = _matched_source_key(source_aliases, snapshot)
    source_column_present: bool | None
    source_cell: SourceCell | None = None
    if snapshot is None:
        source_column_present = None
    elif source_key is None:
        source_column_present = False
    else:
        source_column_present = True
        source_cell = snapshot.cell(raw_row_index, source_key)

    validator_coerced_to_none = pydantic_input_present and final_value is None and not _is_blank(pydantic_input_value)
    validator_transformed = (
        pydantic_input_present and final_value is not None and _value_changed(pydantic_input_value, final_value)
    )
    provenance_reason = _classify_field_reason(
        custom=custom,
        source_column_present=source_column_present,
        source_cell=source_cell,
        pydantic_input_present=pydantic_input_present,
        pydantic_input_value=pydantic_input_value,
        final_value=final_value,
        schema_default_used=schema_default_used,
        validator_coerced_to_none=validator_coerced_to_none,
        validator_transformed=validator_transformed,
    )

    return {
        "endpoint_name": endpoint_name,
        "params": dict(endpoint_params or {}),
        "row_index": raw_row_index,
        "field_name": field_name,
        "model_field_name": field_name,
        "row_model": getattr(row_model, "__name__", None),
        "validation_alias": source_aliases,
        "accepted_input_keys": aliases,
        "matched_input_key": matched_key,
        "source_table_id": snapshot.source_table_id if snapshot is not None else None,
        "source_column_present": source_column_present,
        "source_data_stat": source_cell.data_stat if source_cell is not None else source_key,
        "source_header_text": source_cell.header_text if source_cell is not None else None,
        "source_cell_raw": source_cell.raw_text if source_cell is not None else None,
        "parsed_row_value": pydantic_input_value,
        "pydantic_input_present": pydantic_input_present,
        "pydantic_input_value": pydantic_input_value,
        "final_value": final_value,
        "schema_default_used": schema_default_used,
        "validator_coerced_to_none": validator_coerced_to_none,
        "validator_transformed": validator_transformed,
        "validator_transformation_reason": PROVENANCE_VALIDATOR_TRANSFORMED_VALUE if validator_transformed else None,
        "provenance_reason": provenance_reason,
    }


def _classify_field_reason(
    *,
    custom: bool,
    source_column_present: bool | None,
    source_cell: SourceCell | None,
    pydantic_input_present: bool,
    pydantic_input_value: Any,
    final_value: Any,
    schema_default_used: bool,
    validator_coerced_to_none: bool,
    validator_transformed: bool,
) -> ProvenanceReason:
    if custom:
        if pydantic_input_present:
            return PROVENANCE_CUSTOM_PARSER_VALUE
        if schema_default_used:
            return PROVENANCE_SCHEMA_DEFAULT_USED
        return PROVENANCE_CUSTOM_PARSER_METADATA_UNAVAILABLE

    if source_column_present is False:
        return PROVENANCE_SOURCE_COLUMN_ABSENT
    if source_column_present is True and not pydantic_input_present:
        return PROVENANCE_PARSER_OMITTED_PRESENT_COLUMN
    if not pydantic_input_present:
        if schema_default_used:
            return PROVENANCE_SCHEMA_DEFAULT_USED
        if source_column_present is None:
            return PROVENANCE_DEBUG_UNAVAILABLE
        return PROVENANCE_UNKNOWN

    if source_cell is not None and final_value is None:
        if _is_blank(source_cell.raw_text):
            return PROVENANCE_SOURCE_CELL_BLANK
        if _is_dash_or_sentinel(source_cell.raw_text):
            return PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL
    if final_value is None and _is_blank(pydantic_input_value):
        return PROVENANCE_SOURCE_CELL_BLANK
    if final_value is None and _is_dash_or_sentinel(pydantic_input_value):
        return PROVENANCE_SOURCE_CELL_DASH_OR_SENTINEL
    if validator_coerced_to_none:
        return PROVENANCE_VALIDATOR_COERCED_TO_NONE
    if validator_transformed:
        return PROVENANCE_VALIDATOR_TRANSFORMED_VALUE
    if source_column_present is None:
        return PROVENANCE_PARSER_EMITTED_VALUE
    return PROVENANCE_SOURCE_VALUE_PRESENT


def _field_has_default(field_info: Any) -> bool:
    if getattr(field_info, "default", PydanticUndefined) is not PydanticUndefined:
        return True
    return getattr(field_info, "default_factory", None) is not None


def _matched_source_key(source_aliases: Sequence[str], snapshot: SourceTableSnapshot | None) -> str | None:
    if snapshot is None:
        return None
    source_keys = snapshot.source_keys
    return next((key for key in source_aliases if key in source_keys), None)


def _sample_records_by_reason(records: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    by_reason: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        reason = str(record.get("provenance_reason") or PROVENANCE_UNKNOWN)
        if len(by_reason[reason]) < _SAMPLE_LIMIT:
            by_reason[reason].append(record)
    sampled: list[Mapping[str, Any]] = []
    for reason in sorted(by_reason):
        sampled.extend(by_reason[reason])
    return sampled


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


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    return str(value).replace("\xa0", " ").strip() == ""


def _is_dash_or_sentinel(value: Any) -> bool:
    return str(value).replace("\xa0", " ").strip().casefold() in _DASH_OR_SENTINEL_VALUES


def _value_changed(input_value: Any, final_value: Any) -> bool:
    if input_value == final_value:
        return False
    return str(input_value).strip() != str(final_value).strip()


def _validation_error_fields(errors: Iterable[Mapping[str, Any]]) -> list[str]:
    fields: list[str] = []
    for error in errors:
        loc = error.get("loc")
        parts: Iterable[Any]
        if isinstance(loc, tuple | list):
            parts = loc
        elif loc is None:
            parts = ()
        else:
            parts = (loc,)
        for part in parts:
            name = str(part)
            if name not in fields:
                fields.append(name)
    return fields


def classify_validation_drop(errors: Sequence[Mapping[str, Any]], row: Mapping[str, Any]) -> tuple[str, bool]:
    """Return ``(reason, unresolved)`` for a failed Pydantic row."""
    reason = validation_error_drop_reason(errors, row=row)
    unresolved = reason in UNRESOLVED_DROP_REASONS or reason not in EXPECTED_DROP_REASONS
    return reason, unresolved
