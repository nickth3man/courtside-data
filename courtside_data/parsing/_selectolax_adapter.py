"""Adapter from parsel selectors to selectolax-backed generic tables."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from courtside_data.parsing._selectolax_tables import _SelectolaxGenericTable
from courtside_data.parsing._table_shared import selector_subtree_to_html

if TYPE_CHECKING:
    from selectolax.lexbor import LexborNode as _SLNode


def _empty_selectolax_table() -> _SelectolaxGenericTable:
    empty = object.__new__(_SelectolaxGenericTable)
    empty.rows = []
    return empty


def _find_table_node_in_html(html: str, table_id: str | None) -> _SLNode | None:
    """Parse ``html`` and return the first matching table node."""
    from selectolax.lexbor import LexborHTMLParser

    root = LexborHTMLParser(html)
    if table_id:
        node = root.css_first(f"table#{table_id}")
        if node is not None:
            return node
    return root.css_first("table")


def _row_container_node(html: str) -> _SLNode | None:
    """Return the selectolax node that corresponds to a parsel selector subtree."""
    from selectolax.lexbor import LexborHTMLParser

    root = LexborHTMLParser(html)
    body = root.body
    if body is None:
        return None
    for child in body.iter():
        if child is body:
            continue
        if child.tag in {"table", "thead", "tbody", "tfoot", "tr"}:
            return child
    return body


def _detect_root_tag(table_selector: Any) -> str | None:
    """Return the tag of ``table_selector``'s root element, or ``None``."""
    root = getattr(table_selector, "root", None)
    if root is None:
        return None
    return root.tag


def build_selectolax_table(
    table_selector: Any,
    *,
    use_header_fallback: bool = False,
    exclude_summary_rows: bool = False,
    value_column: bool = False,
) -> _SelectolaxGenericTable:
    """Build a selectolax-backed generic table from a parsel table selector."""
    table_id = table_selector.attrib.get("id")
    raw_html = selector_subtree_to_html(table_selector.root)
    root_tag = _detect_root_tag(table_selector)
    needs_unwrap = root_tag in {"thead", "tbody", "tfoot", "tr"}
    html = f"<table>{raw_html}</table>" if needs_unwrap else raw_html

    if needs_unwrap:
        from selectolax.lexbor import LexborHTMLParser

        wrapped = LexborHTMLParser(html).css_first("table")
        if wrapped is None:
            return _empty_selectolax_table()
        target = wrapped.css_first(root_tag)
        if target is None:
            target = wrapped
        return _SelectolaxGenericTable(
            target,
            use_header_fallback=use_header_fallback,
            exclude_summary_rows=exclude_summary_rows,
            value_column=value_column,
        )

    if table_id:
        named = _find_table_node_in_html(html, table_id)
        if named is not None:
            return _SelectolaxGenericTable(
                named,
                use_header_fallback=use_header_fallback,
                exclude_summary_rows=exclude_summary_rows,
                value_column=value_column,
            )

    container = _row_container_node(html)
    if container is None or container.tag not in {"table", "thead", "tbody", "tfoot"}:
        return _empty_selectolax_table()
    return _SelectolaxGenericTable(
        container,
        use_header_fallback=use_header_fallback,
        exclude_summary_rows=exclude_summary_rows,
        value_column=value_column,
    )
