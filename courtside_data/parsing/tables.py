"""Schema-less table extraction for generic (beta) endpoints, parsel-based.

By default, :class:`GenericTable`, :class:`GenericTableRow`,
:func:`extract_commented_table`, and :func:`parse_transaction_list` all
operate on parsel ``Selector`` objects backed by lxml. When the
environment variable ``COURTSIDE_DATA_FAST_PARSE=1`` is set, the parsing
hot paths delegate to the selectolax-based equivalents in
:mod:`courtside_data.parsing._selectolax_backend` for faster table
extraction on large fixtures. The public function signatures and return
shapes are unchanged on either path.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Protocol

from parsel import Selector


def _is_fast_parse_enabled() -> bool:
    """Re-export the fast-parse predicate from the selectolax backend.

    Imported lazily inside the parser hot path so the default suite
    (flag off) never imports ``selectolax`` at all.
    """
    from courtside_data.parsing._selectolax_backend import is_fast_parse_enabled

    return is_fast_parse_enabled()


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


# Column keys on the leaders pages that are NEVER the rotating stat value.
# They are text/identity columns whose header does not rotate with the active
# stat category. Used by :attr:`GenericTable.value_column` to identify the
# rightmost non-text column and rename it to ``value``.
_LEADER_TEXT_COLUMN_KEYS: frozenset[str] = frozenset({"rank", "player", "season", "team", "team_id"})


class GenericTable:
    """Extracts rows from any basketball-reference table.

    Filters out header rows (.thead class) and returns GenericTableRow
    instances for each data row.

    When the environment variable ``COURTSIDE_DATA_FAST_PARSE=1`` is set,
    the constructor delegates to the selectolax-backed
    :class:`courtside_data.parsing._selectolax_backend._SelectolaxGenericTable`
    and stores its rows directly. The selectolax rows are duck-typed as
    :class:`GenericTableRow` (same ``to_dict`` / ``metadata`` surface) so
    callers don't need to know which backend produced them.
    """

    def __init__(
        self,
        table_selector: Selector,
        use_header_fallback: bool = False,
        exclude_summary_rows: bool = False,
        value_column: bool = False,
    ) -> None:
        if _is_fast_parse_enabled():
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

        Imported lazily so the default (parsel) path costs nothing at import
        time and the selectolax module is only loaded when the fast-parse
        flag is set.
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

        Two passes per row:

        1. **Rank period strip**: BR renders rank values as ``"1."``,
           ``"2."`` (trailing period). The shared ``_br_int`` validator
           rejects ``"1."`` as non-integer, so we strip the trailing
           period before the row reaches the schema.
        2. **Value column rename**: the leaders pages emit a column whose
           header rotates with the active stat category (``per``,
           ``pts``, ``ast``, ``blk`` …). A static ``validation_alias``
           cannot cover every category, so this pass renames the rotating
           column to a stable ``value`` key that downstream row models
           can match. The rename target is the rightmost key on each row
           that is NOT one of :data:`_LEADER_TEXT_COLUMN_KEYS`. Rows that
           already expose a ``value`` key are left untouched.
        """
        for row in self.rows:
            data = row._data
            # Pass 1: strip the trailing period from rank values.
            rank_value = data.get("rank")
            if isinstance(rank_value, str) and rank_value.endswith("."):
                data["rank"] = rank_value.rstrip(".")
            # Pass 2: rename the rotating stat column to a stable key.
            if "value" not in data:
                value_key = next(
                    (key for key in reversed(list(data)) if key not in _LEADER_TEXT_COLUMN_KEYS),
                    None,
                )
                if value_key is not None:
                    data["value"] = data.pop(value_key)

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

    When ``COURTSIDE_DATA_FAST_PARSE=1`` is set, the comment scan is
    delegated to the selectolax-based
    :func:`courtside_data.parsing._selectolax_backend.selectolax_extract_commented_table`,
    which regex-scans the page's HTML for ``<!-- ... -->`` blocks. The
    returned table is wrapped in a parsel ``Selector`` to preserve the
    public ``Selector | None`` return shape; the caller's eventual
    :class:`GenericTable` call will re-parse it through selectolax.

    Args:
        selector: The page-level Parsel Selector
        table_id: The id attribute of the table to find

    Returns:
        A Selector for the extracted table, or None if not found
    """
    if _is_fast_parse_enabled():
        from lxml.html import tostring

        from courtside_data.parsing._selectolax_backend import selectolax_extract_commented_table

        # Serialize the page Selector back to HTML so the selectolax
        # backend can scan the original source for comment blocks
        # (``<!-- ... -->``). lxml preserves comments in the serialized
        # output. ``lxml.html.tostring`` keeps empty elements like
        # ``<a data-attr-from=""></a>`` from being collapsed to
        # ``<a data-attr-from=""/>`` (the self-closing form changes how
        # selectolax's ``text()`` method sees following sibling text).
        page_html = tostring(selector.root, encoding="unicode")
        if isinstance(page_html, bytes):
            page_html = page_html.decode("utf-8")
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


def _clean_text(values: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(values)).strip()


def parse_transaction_list(selector: Selector) -> list[dict[str, Any]]:
    """Parse a Basketball Reference transaction-list page into dict rows.

    Transaction pages (league and team) are date-grouped ``<ul>`` lists
    rather than tables; this is the fallback used by ``fetch_table`` when an
    endpoint declares ``transaction_list_fallback``.

    When ``COURTSIDE_DATA_FAST_PARSE=1`` is set, the page is delegated to
    the selectolax-based
    :func:`courtside_data.parsing._selectolax_backend.selectolax_parse_transaction_list`,
    which scans ``<ul.page_index > li>`` date groups and the ``<p>``
    transactions inside each group. The output shape is identical to the
    parsel-based path.
    """
    if _is_fast_parse_enabled():
        from lxml.html import tostring

        from courtside_data.parsing._selectolax_backend import selectolax_parse_transaction_list

        # ``lxml.html.tostring`` preserves the explicit close tag on empty
        # elements like ``<a data-attr-from=""></a>`` so selectolax's
        # text-extraction on the link returns ``""`` rather than the
        # following sibling text.
        page_html = tostring(selector.root, encoding="unicode")
        if isinstance(page_html, bytes):
            page_html = page_html.decode("utf-8")
        return selectolax_parse_transaction_list(page_html)

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
