"""Schema-less table extraction for generic (beta) endpoints.

:class:`GenericTable`, :class:`GenericTableRow`,
:func:`extract_commented_table`, and :func:`parse_transaction_list` all
operate on the **selectolax (Lexbor)** backend by default — set the
environment variable ``COURTSIDE_DATA_PARSE_BACKEND=parsel`` to switch to
the parsel + lxml backend. The public function signatures and return
shapes are unchanged on either path.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from parsel import Selector

from courtside_data.parsing._table_shared import (
    canonical_cell_value,
    clean_text,
    normalize_header,
    normalize_value_column,
    selector_subtree_to_html,
)


def _is_parsel_backend() -> bool:
    """Re-export the parsel predicate from the selectolax backend.

    Imported lazily inside the parser hot path so the default suite
    (selectolax backend) never imports ``selectolax`` at all.
    """
    from courtside_data.parsing._selectolax_backend import is_parsel_backend

    return is_parsel_backend()


class _GenericRowLike(Protocol):
    """Minimal row interface consumed by :class:`GenericTable` callers.

    Both :class:`GenericTableRow` (parsel) and
    ``_SelectolaxGenericTableRow`` (selectolax) satisfy this protocol; the
    fast-parse path stores instances of the latter in :attr:`GenericTable.rows`
    so they need to be duck-typed as :class:`GenericTableRow` from a caller's
    perspective. ``_data`` is the internal cell-data dict used by the
    parsel extractor to filter out empty rows; both implementations expose
    it as an implementation detail of the row class.
    """

    _data: dict[str, str]

    def get(self, stat_name: str, default: str = ...) -> str: ...
    def to_dict(self) -> dict[str, str]: ...
    @property
    def metadata(self) -> dict[str, dict[str, str]]: ...


if TYPE_CHECKING:
    from courtside_data.parsing._selectolax_backend import (
        _SelectolaxGenericTableRow as _SelectolaxGenericTableRow,
    )


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
                text = text.replace("*", "").strip()
                # Collect all attributes from the cell and its descendants
                # (e.g., data-append-csv is sometimes on child <a> tags)
                all_attrs: dict[str, str] = {}
                for element in [cell, *cell.css("*")]:
                    for key, value in element.attrib.items():
                        if key != "data-stat":
                            all_attrs[key] = value
                self._data[stat] = canonical_cell_value(stat, text, all_attrs)
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

    By default the constructor delegates to the selectolax (Lexbor)-backed
    :class:`courtside_data.parsing._selectolax_backend._SelectolaxGenericTable`
    and stores its rows directly. The selectolax rows are duck-typed as
    :class:`GenericTableRow` (same ``to_dict`` / ``metadata`` surface) so
    callers don't need to know which backend produced them. Set the
    environment variable ``COURTSIDE_DATA_PARSE_BACKEND=parsel`` to fall
    back to the parsel + lxml implementation.
    """

    def __init__(
        self,
        table_selector: Selector,
        use_header_fallback: bool = False,
        exclude_summary_rows: bool = False,
        value_column: bool = False,
    ) -> None:
        if not _is_parsel_backend():
            self.rows: list[_GenericRowLike] = self._build_selectolax_rows(
                table_selector,
                use_header_fallback=use_header_fallback,
                exclude_summary_rows=exclude_summary_rows,
                value_column=value_column,
            )
            return

        self.rows: list[_GenericRowLike] = []
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
        if value_column:
            self._normalize_value_column()

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> _GenericRowLike:
        return self.rows[index]

    @staticmethod
    def _build_selectolax_rows(
        table_selector: Selector,
        *,
        use_header_fallback: bool,
        exclude_summary_rows: bool,
        value_column: bool,
    ) -> list[_GenericRowLike]:
        """Build rows via the selectolax backend.

        Imported lazily so the parsel path costs nothing at import time.
        """
        from typing import cast

        from courtside_data.parsing._selectolax_backend import build_selectolax_table

        # ``_SelectolaxGenericTableRow`` is structurally a ``_GenericRowLike``
        # (it exposes ``get``/``to_dict``/``metadata``/``_data``); the cast is
        # the only safe way to bridge an invariant ``list`` parameterization
        # in the type checker.
        return cast(
            "list[_GenericRowLike]",
            build_selectolax_table(
                table_selector,
                use_header_fallback=use_header_fallback,
                exclude_summary_rows=exclude_summary_rows,
                value_column=value_column,
            ).rows,
        )

    @staticmethod
    def _is_header_row(row: Selector) -> bool:
        cells = row.css("td, th")
        return bool(cells) and not row.css("td") and bool(row.css("th"))

    def _normalize_value_column(self) -> None:
        """Normalize leaderboard rows for downstream row-model validation.

        Two passes per row — delegates to the shared
        :func:`courtside_data.parsing._table_shared.normalize_value_column`
        helper.
        """
        normalize_value_column(self.rows)

    @classmethod
    def _fallback_headers(cls, table_selector: Selector) -> list[str]:
        for row in table_selector.css("tr"):
            cells = row.css("td, th")
            if cells and not row.css("td") and row.css("th"):
                return [normalize_header(cell.attrib.get("data-stat") or cell.css("::text").get("")) for cell in cells]
        return []


def extract_commented_table(selector: Selector, table_id: str) -> Selector | None:
    """
    Finds a table inside HTML comments and returns it as a Selector.

    Basketball-reference wraps some tables in HTML comments to speed up
    page load. This function finds and extracts those hidden tables.

    By default the comment scan is delegated to the selectolax-based
    :func:`courtside_data.parsing._selectolax_backend.selectolax_extract_commented_table`,
    which regex-scans the page's HTML for ``<!-- ... -->`` blocks. The
    returned table is wrapped in a parsel ``Selector`` to preserve the
    public ``Selector | None`` return shape; the caller's eventual
    :class:`GenericTable` call will re-parse it through selectolax. Set
    the environment variable ``COURTSIDE_DATA_PARSE_BACKEND=parsel`` to
    fall back to the parsel + lxml implementation.

    Args:
        selector: The page-level Parsel Selector
        table_id: The id attribute of the table to find

    Returns:
        A Selector for the extracted table, or None if not found
    """
    if not _is_parsel_backend():
        from courtside_data.parsing._selectolax_backend import selectolax_extract_commented_table

        # Serialize the page Selector back to HTML so the selectolax
        # backend can scan the original source for comment blocks
        # (``<!-- ... -->``). lxml preserves comments in the serialized
        # output. ``lxml.html.tostring`` keeps empty elements like
        # ``<a data-attr-from=""></a>`` from being collapsed to
        # ``<a data-attr-from=""/>`` (the self-closing form changes how
        # selectolax's ``text()`` method sees following sibling text).
        page_html = selector_subtree_to_html(selector.root)
        table_html = selectolax_extract_commented_table(page_html, table_id)
        if table_html is None:
            return None
        fragment = Selector(text=table_html)
        matches = fragment.css(f"table#{table_id}")
        return matches[0] if matches else None

    for comment in selector.xpath("//comment()").getall():
        if f'id="{table_id}"' in comment or f"id='{table_id}'" in comment:
            # Strip comment tags to get raw HTML
            clean_html: str = comment.replace("<!--", "").replace("-->", "").strip()
            fragment: Selector = Selector(text=clean_html)
            table = fragment.css(f"table#{table_id}")
            if table:
                return table[0]
    return None


def parse_transaction_list(selector: Selector) -> list[dict[str, Any]]:
    """Parse a Basketball Reference transaction-list page into dict rows.

    Transaction pages (league and team) are date-grouped ``<ul>`` lists
    rather than tables; this is the fallback used by ``fetch_table`` when an
    endpoint declares ``transaction_list_fallback``.

    By default the page is delegated to the selectolax-based
    :func:`courtside_data.parsing._selectolax_backend.selectolax_parse_transaction_list`,
    which scans ``<ul.page_index > li>`` date groups and the ``<p>``
    transactions inside each group. The output shape is identical to the
    parsel-based path. Set the environment variable
    ``COURTSIDE_DATA_PARSE_BACKEND=parsel`` to fall back to the parsel +
    lxml implementation.
    """
    if not _is_parsel_backend():
        from courtside_data.parsing._selectolax_backend import selectolax_parse_transaction_list

        # ``lxml.html.tostring`` preserves the explicit close tag on empty
        # elements like ``<a data-attr-from=""></a>`` so selectolax's
        # text-extraction on the link returns ``""`` rather than the
        # following sibling text.
        page_html = selector_subtree_to_html(selector.root)
        return selectolax_parse_transaction_list(page_html)

    def _append_unique(values: list[str], value: str | None) -> None:
        if value and value not in values:
            values.append(value)

    def _player_hrefs(transaction: Selector) -> set[str]:
        return {
            href for href in (link.attrib.get("href", "") for link in transaction.css('a[href^="/players/"]')) if href
        }

    def _is_trade(transaction: Selector) -> bool:
        return " traded " in f" {clean_text(transaction.css('::text').getall()).lower()} "

    def _transaction_groups(day: Selector) -> list[list[Selector]]:
        nodes = day.xpath("./p[normalize-space()]")
        groups: list[list[Selector]] = []
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

    transactions = []
    for day in selector.css("ul.page_index > li"):
        date = clean_text(day.xpath("./span//text()").getall())
        for transaction_group in _transaction_groups(day):
            linked_resources = []
            from_team_abbreviations = []
            to_team_abbreviations = []
            transaction_text: list[str] = []
            for transaction in transaction_group:
                transaction_text.append(clean_text(transaction.css("::text").getall()))
                for link in transaction.css("a"):
                    from_team = link.attrib.get("data-attr-from")
                    to_team = link.attrib.get("data-attr-to")
                    _append_unique(from_team_abbreviations, from_team)
                    _append_unique(to_team_abbreviations, to_team)
                    linked_resources.append(
                        {
                            "text": clean_text(link.css("::text").getall()),
                            "href": link.attrib.get("href", ""),
                            "from_team_abbreviation": from_team or "",
                            "to_team_abbreviation": to_team or "",
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
