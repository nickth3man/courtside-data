"""Provenance data models.

Frozen dataclasses that describe the independently-observed source-table
evidence collected by the debug/probe surface. These types are the
canonical shared vocabulary for the rest of the provenance sub-modules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


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
