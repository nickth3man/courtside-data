"""Selectolax-backed row and table primitives."""

from __future__ import annotations

from typing import TYPE_CHECKING

from courtside_data.parsing._table_shared import canonical_cell_value, normalize_header, normalize_value_column

if TYPE_CHECKING:
    from selectolax.lexbor import LexborNode as _SLNode


def _node_all_attrs(node: _SLNode) -> dict[str, str]:
    """Collect attributes from a selectolax node and all its descendants."""
    collected: dict[str, str] = {key: (value or "") for key, value in node.attributes.items()}
    for descendant in node.iter():
        for key, value in descendant.attributes.items():
            collected[key] = value or ""
    return collected


def _node_text(node: _SLNode) -> str:
    """Extract text from a selectolax node the way the parsel extractor does."""
    text = node.text(separator=" ", strip=True) or ""
    return text.replace("*", "").strip()


class _SelectolaxGenericTableRow:
    """Selectolax-backed row with the same interface as ``GenericTableRow``."""

    def __init__(self, node: _SLNode, fallback_headers: list[str] | None = None) -> None:
        self._data: dict[str, str] = {}
        self._metadata: dict[str, dict[str, str]] = {}
        for index, cell in enumerate(node.css("td, th")):
            stat: str | None = cell.attributes.get("data-stat")
            if not stat and fallback_headers is not None:
                stat = fallback_headers[index] if index < len(fallback_headers) else f"col_{index + 1}"
            if stat:
                text = _node_text(cell)
                attrs = _node_all_attrs(cell)
                attrs.pop("data-stat", None)
                self._data[stat] = canonical_cell_value(stat, text, attrs)
                self._metadata[stat] = attrs

    def get(self, stat_name: str, default: str = "") -> str:
        """Get a value by data-stat attribute name."""
        return self._data.get(stat_name, default)

    def to_dict(self) -> dict[str, str]:
        """Return all extracted data as a dictionary."""
        return self._data.copy()

    @property
    def metadata(self) -> dict[str, dict[str, str]]:
        """Return all cell attributes except data-stat, keyed by stat name."""
        return dict(self._metadata)


class _SelectolaxGenericTable:
    """Selectolax-backed table with the same interface as ``GenericTable``."""

    def __init__(
        self,
        table_node: _SLNode,
        *,
        use_header_fallback: bool = False,
        exclude_summary_rows: bool = False,
        value_column: bool = False,
    ) -> None:
        self.rows: list[_SelectolaxGenericTableRow] = []
        row_filter = "tbody tr:not(.thead)"
        if exclude_summary_rows:
            row_filter += ":not(.norank)"
        row_selectors = table_node.css(row_filter)
        if not row_selectors:
            row_filter = "tr:not(.thead)"
            if exclude_summary_rows:
                row_filter += ":not(.norank)"
            row_selectors = table_node.css(row_filter)
        fallback_headers = self._fallback_headers(table_node) if use_header_fallback else None

        for row in row_selectors:
            if self._is_header_row(row):
                continue
            generic_row = _SelectolaxGenericTableRow(row, fallback_headers=fallback_headers)
            if generic_row._data:
                self.rows.append(generic_row)
        if value_column:
            self._normalize_value_column()

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> _SelectolaxGenericTableRow:
        return self.rows[index]

    @staticmethod
    def _is_header_row(row: _SLNode) -> bool:
        cells = row.css("td, th")
        if not cells:
            return False
        tds = row.css("td")
        ths = row.css("th")
        return not tds and bool(ths)

    def _normalize_value_column(self) -> None:
        normalize_value_column(self.rows)

    @classmethod
    def _fallback_headers(cls, table_node: _SLNode) -> list[str]:
        for row in table_node.css("tr"):
            cells = row.css("td, th")
            if cells and not row.css("td") and row.css("th"):
                return [
                    normalize_header(cell.attributes.get("data-stat") or (cell.text(separator=" ", strip=True) or ""))
                    for cell in cells
                ]
        return []
