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

    def _append_unique(values: list[str], value: str) -> None:
        if value and value not in values:
            values.append(value)

    def _node_text(node: _SLNode) -> str:
        return clean_text([(node.text(separator=" ", strip=True) or "")])

    def _is_trade(node: _SLNode) -> bool:
        return " traded " in f" {_node_text(node).lower()} "

    def _player_hrefs(node: _SLNode) -> set[str]:
        return {
            href for href in ((link.attributes.get("href") or "") for link in node.css('a[href^="/players/"]')) if href
        }

    def _transaction_groups(day: _SLNode) -> list[list[_SLNode]]:
        nodes = [node for node in day.css("p") if _node_text(node)]
        groups: list[list[_SLNode]] = []
        for transaction in nodes:
            if (
                groups
                and _is_trade(groups[-1][-1])
                and _is_trade(transaction)
                and _player_hrefs(groups[-1][-1]) & _player_hrefs(transaction)
            ):
                groups[-1].append(transaction)
            else:
                groups.append([transaction])
        return groups

    for day in root.css("ul.page_index > li"):
        first_span = day.css_first("span")
        date = (first_span.text(separator=" ", strip=True) if first_span is not None else "") or ""
        for transaction_group in _transaction_groups(day):
            linked_resources: list[dict[str, Any]] = []
            from_team_abbreviations: list[str] = []
            to_team_abbreviations: list[str] = []
            transaction_text: list[str] = []
            for transaction in transaction_group:
                transaction_text.append(_node_text(transaction))
                for link in transaction.css("a"):
                    attrs = link.attributes
                    from_team = attrs.get("data-attr-from") or ""
                    to_team = attrs.get("data-attr-to") or ""
                    _append_unique(from_team_abbreviations, from_team)
                    _append_unique(to_team_abbreviations, to_team)
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
                    "transaction": clean_text(transaction_text),
                    "from_team_abbreviations": from_team_abbreviations,
                    "to_team_abbreviations": to_team_abbreviations,
                    "linked_resources": linked_resources,
                }
            )
    return transactions
