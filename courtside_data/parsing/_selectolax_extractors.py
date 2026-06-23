"""Selectolax helpers for irregular HTML extraction."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from courtside_data.parsing._selectolax_adapter import _find_table_node_in_html
from courtside_data.parsing._table_shared import clean_text

if TYPE_CHECKING:
    from selectolax.lexbor import LexborNode as _SLNode


def selectolax_extract_commented_table(html_text: str, table_id: str) -> str | None:
    """Find a table inside an HTML comment and return its HTML."""
    for comment in re.findall(r"<!--.*?-->", html_text, flags=re.DOTALL):
        if f'id="{table_id}"' in comment or f"id='{table_id}'" in comment:
            clean_html = comment.replace("<!--", "").replace("-->", "").strip()
            table_node = _find_table_node_in_html(clean_html, table_id)
            if table_node is not None:
                return table_node.html
    return None


def selectolax_parse_transaction_list(html_text: str) -> list[dict[str, Any]]:
    """Selectolax equivalent of ``parse_transaction_list``."""
    from selectolax.lexbor import LexborHTMLParser

    root = LexborHTMLParser(html_text)
    transactions: list[dict[str, Any]] = []

    def _is_transaction_p(node: _SLNode) -> bool:
        cls = node.attributes.get("class") or ""
        if "transaction" in cls.split():
            return True
        return bool(node.text(separator=" ", strip=True) or "")

    for day in root.css("ul.page_index > li"):
        first_span = day.css_first("span")
        date = (first_span.text(separator=" ", strip=True) if first_span is not None else "") or ""
        transaction_nodes = [node for node in day.css("p.transaction") if _is_transaction_p(node)]
        if not transaction_nodes:
            transaction_nodes = [node for node in day.css("p") if _is_transaction_p(node)]
        for transaction in transaction_nodes:
            linked_resources: list[dict[str, Any]] = []
            from_team_abbreviations: list[str] = []
            to_team_abbreviations: list[str] = []
            for link in transaction.css("a"):
                attrs = link.attributes
                from_team = attrs.get("data-attr-from") or ""
                to_team = attrs.get("data-attr-to") or ""
                if from_team:
                    from_team_abbreviations.append(from_team)
                if to_team:
                    to_team_abbreviations.append(to_team)
                linked_resources.append(
                    {
                        "text": clean_text([(link.text(separator=" ", strip=True) or "")]),
                        "href": attrs.get("href") or "",
                        "from_team_abbreviation": from_team,
                        "to_team_abbreviation": to_team,
                    }
                )
            transactions.append(
                {
                    "date": date,
                    "transaction": clean_text([(transaction.text(separator=" ", strip=True) or "")]),
                    "from_team_abbreviations": from_team_abbreviations,
                    "to_team_abbreviations": to_team_abbreviations,
                    "linked_resources": linked_resources,
                }
            )
    return transactions
