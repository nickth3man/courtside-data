"""Schema-less table extraction for generic (beta) endpoints, parsel-based."""

from __future__ import annotations

import re
from typing import Any

from parsel import Selector


class GenericTableRow:
    """Extracts data from any table row using data-stat attributes.

    This replaces per-endpoint Row classes for new endpoints.
    Each cell's data-stat attribute becomes a key in the output dict.
    Cell attributes (except data-stat) are exposed via the metadata property.
    """

    def __init__(self, selector: Selector, fallback_headers: list[str] | None = None) -> None:
        self._data: dict[str, str] = {}
        self._metadata: dict[str, dict[str, str]] = {}
        for index, cell in enumerate(selector.css("td, th")):
            stat: str | None = cell.attrib.get("data-stat")
            if not stat and fallback_headers is not None:
                stat = fallback_headers[index] if index < len(fallback_headers) else f"col_{index + 1}"
            if stat:
                text: str = " ".join(value.strip() for value in cell.css("::text").getall() if value.strip())
                # Remove asterisks (used for player notes like All-Star)
                self._data[stat] = text.replace("*", "").strip()
                # Collect all attributes from the cell and its descendants
                # (e.g., data-append-csv is sometimes on child <a> tags)
                all_attrs: dict[str, str] = {}
                for element in [cell, *cell.css("*")]:
                    for key, value in element.attrib.items():
                        if key != "data-stat":
                            all_attrs[key] = value
                self._metadata[stat] = all_attrs

    def get(self, stat_name: str, default: str = "") -> str:
        """Get a value by data-stat attribute name."""
        return self._data.get(stat_name, default)

    def to_dict(self) -> dict[str, str]:
        """Return all extracted data as a dictionary."""
        return self._data.copy()

    @property
    def metadata(self) -> dict[str, dict[str, str]]:
        """Return all cell attributes (except data-stat) keyed by stat name."""
        return dict(self._metadata)


class GenericTable:
    """Extracts rows from any basketball-reference table.

    Filters out header rows (.thead class) and returns GenericTableRow
    instances for each data row.
    """

    def __init__(
        self,
        table_selector: Selector,
        use_header_fallback: bool = False,
        exclude_summary_rows: bool = False,
    ) -> None:
        self.rows: list[GenericTableRow] = []
        row_filter = "tbody tr:not(.thead)"
        if exclude_summary_rows:
            row_filter += ":not(.norank)"
        row_selectors = table_selector.css(row_filter)
        if not row_selectors:
            row_filter = "tr:not(.thead)"
            if exclude_summary_rows:
                row_filter += ":not(.norank)"
            row_selectors = table_selector.css(row_filter)
        fallback_headers = self._fallback_headers(table_selector) if use_header_fallback else None

        for row in row_selectors:
            if self._is_header_row(row):
                continue
            generic_row = GenericTableRow(row, fallback_headers=fallback_headers)
            if generic_row._data:
                self.rows.append(generic_row)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> GenericTableRow:
        return self.rows[index]

    @staticmethod
    def _is_header_row(row: Selector) -> bool:
        cells = row.css("td, th")
        return bool(cells) and not row.css("td") and bool(row.css("th"))

    @classmethod
    def _fallback_headers(cls, table_selector: Selector) -> list[str]:
        for row in table_selector.css("tr"):
            cells = row.css("td, th")
            if cells and not row.css("td") and row.css("th"):
                return [
                    cls._normalize_header(cell.attrib.get("data-stat") or cell.css("::text").get("")) for cell in cells
                ]
        return []

    @staticmethod
    def _normalize_header(value: str) -> str:
        header = re.sub(r"[^0-9A-Za-z]+", "_", value.strip().lower()).strip("_")
        return header or "col"


def extract_commented_table(selector: Selector, table_id: str) -> Selector | None:
    """
    Finds a table inside HTML comments and returns it as a Selector.

    Basketball-reference wraps some tables in HTML comments to speed up
    page load. This function finds and extracts those hidden tables.

    Args:
        selector: The page-level Parsel Selector
        table_id: The id attribute of the table to find

    Returns:
        A Selector for the extracted table, or None if not found
    """
    for comment in selector.xpath("//comment()").getall():
        if f'id="{table_id}"' in comment or f"id='{table_id}'" in comment:
            # Strip comment tags to get raw HTML
            clean_html: str = comment.replace("<!--", "").replace("-->", "").strip()
            fragment: Selector = Selector(text=clean_html)
            table = fragment.css(f"table#{table_id}")
            if table:
                return table[0]
    return None


def _clean_text(values: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(values)).strip()


def parse_transaction_list(selector: Selector) -> list[dict[str, Any]]:
    """Parse a Basketball Reference transaction-list page into dict rows.

    Transaction pages (league and team) are date-grouped ``<ul>`` lists
    rather than tables; this is the fallback used by ``fetch_table`` when an
    endpoint declares ``transaction_list_fallback``.
    """
    transactions = []
    for day in selector.css("ul.page_index > li"):
        date = _clean_text(day.xpath("./span//text()").getall())
        transaction_nodes = day.xpath('./p[contains(concat(" ", normalize-space(@class), " "), " transaction ")]')
        if not transaction_nodes:
            transaction_nodes = day.xpath("./p[normalize-space()]")
        for transaction in transaction_nodes:
            linked_resources = []
            from_team_abbreviations = []
            to_team_abbreviations = []
            for link in transaction.css("a"):
                from_team = link.attrib.get("data-attr-from")
                to_team = link.attrib.get("data-attr-to")
                if from_team:
                    from_team_abbreviations.append(from_team)
                if to_team:
                    to_team_abbreviations.append(to_team)
                linked_resources.append(
                    {
                        "text": _clean_text(link.css("::text").getall()),
                        "href": link.attrib.get("href", ""),
                        "from_team_abbreviation": from_team or "",
                        "to_team_abbreviation": to_team or "",
                    }
                )

            transactions.append(
                {
                    "date": date,
                    "transaction": _clean_text(transaction.css("::text").getall()),
                    "from_team_abbreviations": from_team_abbreviations,
                    "to_team_abbreviations": to_team_abbreviations,
                    "linked_resources": linked_resources,
                }
            )
    return transactions
