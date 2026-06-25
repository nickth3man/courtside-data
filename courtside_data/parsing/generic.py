"""Generic table endpoint extraction via the declarative ENDPOINTS registry."""

from __future__ import annotations

import hashlib
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any

from parsel import Selector

from courtside_data.debug import current_debug_trace
from courtside_data.debug._pipeline_events import record_parsed_rows_summary
from courtside_data.debug.provenance import (
    build_source_table_snapshot,
    record_table_provenance,
    record_unavailable_table_provenance,
)
from courtside_data.endpoints import EndpointKind, EndpointSpec
from courtside_data.parsing.tables import GenericTable, extract_commented_table, parse_transaction_list

if TYPE_CHECKING:
    from courtside_data.http_service import HTTPService


def xpath_literal(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"


def find_table_by_id(selector: Selector, table_id: str) -> list[Selector]:
    return list(selector.xpath(f"//table[@id={xpath_literal(table_id)}]"))


def find_table(selector: Selector, table_id: str) -> Selector | None:
    table = selector.css(f"table#{table_id}")
    if table:
        return table[0]
    return extract_commented_table(selector, table_id)


class GenericEndpointHandler:
    """Fetch and parse generic table endpoints declared in ENDPOINTS."""

    def __init__(self, http: HTTPService) -> None:
        self._http = http

    def _resolve_table_selector(
        self, selector: Selector, endpoint: EndpointSpec, params: dict[str, Any]
    ) -> tuple[Selector | None, str | None]:
        trace = current_debug_trace()
        if endpoint.table_id is not None:
            rendered_table_id = endpoint.table_id.format(**params)
            found = find_table_by_id(selector, rendered_table_id)
            if trace is not None:
                trace.record(
                    "table_resolution",
                    "table_id_lookup",
                    selector=f"table[@id={rendered_table_id!r}]",
                    matched=bool(found),
                    match_count=len(found),
                )
            if found:
                return found[0], "table_id"

        if endpoint.fallback_table_ids:
            for fallback_id in endpoint.fallback_table_ids:
                rendered_fallback_id = fallback_id.format(**params)
                found = find_table_by_id(selector, rendered_fallback_id)
                if trace is not None:
                    trace.record(
                        "table_resolution",
                        "fallback_table_id_lookup",
                        selector=f"table[@id={rendered_fallback_id!r}]",
                        fallback_id=fallback_id,
                        matched=bool(found),
                        match_count=len(found),
                    )
                if found:
                    return found[0], "fallback_table_id"

        if endpoint.commented_table_id is not None:
            table_selector = extract_commented_table(selector, endpoint.commented_table_id)
            if trace is not None:
                trace.record(
                    "table_resolution",
                    "commented_table_lookup",
                    table_id=endpoint.commented_table_id,
                    matched=table_selector is not None,
                )
            if table_selector is not None:
                return table_selector, "commented_table_id"

        if endpoint.table_id is None and endpoint.commented_table_id is None:
            found = selector.css("table")
            if found:
                return found[0], "first_table"

        return None, None

    def fetch_table(
        self,
        endpoint: EndpointSpec,
        *,
        endpoint_name: str | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """Fetch and parse a generic table endpoint described by ``endpoint``.

        Resolution order: CSS ``table#<table_id>``, then a comment-wrapped
        table with ``commented_table_id``, then the transaction-list fallback,
        then an empty list.
        """
        if endpoint.kind is EndpointKind.WORKFLOW:
            raise ValueError("Workflow endpoints require the workflow executor, not fetch_table()")
        trace = current_debug_trace()
        url = self._http._url(endpoint.path.format(**params))
        if trace is not None:
            trace.record(
                "endpoint",
                "generic_fetch_table_start",
                url=url,
                path_template=endpoint.path,
                table_id=endpoint.table_id,
                commented_table_id=endpoint.commented_table_id,
                transaction_list_fallback=endpoint.transaction_list_fallback,
                use_header_fallback=endpoint.use_header_fallback,
                exclude_summary_rows=endpoint.exclude_summary_rows,
            )
        selector = self._http._get_selector(url=url)

        resolve_context = trace.span("table_resolve", stage="table_resolution") if trace is not None else nullcontext()
        with resolve_context:
            table_selector, table_source = self._resolve_table_selector(selector, endpoint, params)

        if table_selector is None:
            if endpoint.transaction_list_fallback:
                rows = parse_transaction_list(selector)
                if trace is not None:
                    record_unavailable_table_provenance(trace, reason="transaction_list_fallback")
                    trace.record("table_resolution", "transaction_list_fallback", row_count=len(rows))
                    trace.artifact("raw_rows", rows)
                    record_parsed_rows_summary(trace, parser_name="transaction_list", rows=rows)
                return rows
            if trace is not None:
                record_unavailable_table_provenance(trace, reason="no_selected_table")
                trace.record("table_resolution", "no_table_found", returned_row_count=0)
            return []

        parse_rows_context = trace.span("row_parse", stage="parse") if trace is not None else nullcontext()
        with parse_rows_context:
            table = GenericTable(
                table_selector,
                use_header_fallback=endpoint.use_header_fallback,
                exclude_summary_rows=endpoint.exclude_summary_rows,
                value_column=endpoint.value_column,
            )
            parser_rows_before_projection = [row.to_dict() for row in table.rows]
            rows = parser_rows_before_projection
            if endpoint.projection is not None:
                rows = [{key: row.get(key, "") for key in endpoint.projection} for row in rows]
        if trace is not None:
            try:
                snapshot = build_source_table_snapshot(
                    table_selector,
                    endpoint_name=endpoint_name or "<unknown>",
                    params=params,
                    table_source=table_source,
                    use_header_fallback=endpoint.use_header_fallback,
                    exclude_summary_rows=endpoint.exclude_summary_rows,
                )
                record_table_provenance(
                    trace,
                    snapshot=snapshot,
                    row_model=endpoint.row_model,
                    parser_rows_before_projection=parser_rows_before_projection,
                    parser_rows_after_projection=rows,
                )
            except Exception as error:
                trace.record(
                    "provenance",
                    "source_table_provenance_unavailable",
                    status="warn",
                    reason="source_table_snapshot_failed",
                    error_type=type(error).__name__,
                    error_message=str(error),
                )
            include_html_meta = trace.config.detail_level != "summary"
            raw_table_html = table_selector.get() or "" if include_html_meta else ""
            row_class_counts: dict[str, int] = {}
            for row_selector in table_selector.css("tr"):
                classes = row_selector.attrib.get("class", "").split()
                if not classes:
                    row_class_counts["<none>"] = row_class_counts.get("<none>", 0) + 1
                for class_name in classes:
                    row_class_counts[class_name] = row_class_counts.get(class_name, 0) + 1
            trace.record(
                "parse",
                "generic_table_parsed",
                source=table_source,
                source_sections=[table_source],
                row_count=len(rows),
                column_names=list(rows[0].keys()) if rows else [],
                table_attributes=dict(table_selector.attrib),
                table_html_length=len(raw_table_html),
                table_html_sha256=hashlib.sha256(raw_table_html.encode("utf-8", errors="replace")).hexdigest(),
                row_class_counts=row_class_counts,
            )
            trace.artifact("raw_rows", rows)
            trace.artifact(
                "row_metadata",
                [{"row_index": index, "metadata": row.metadata} for index, row in enumerate(table.rows)],
            )
            record_parsed_rows_summary(trace, parser_name="generic_table", rows=rows)
        return rows
