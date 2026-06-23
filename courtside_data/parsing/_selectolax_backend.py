"""Selectolax (Lexbor) backend for the generic table extraction hot path.

This module is a parallel implementation of the surface exposed by
:mod:`courtside_data.parsing.tables` — :class:`GenericTable`, :class:`GenericTableRow`,
:func:`extract_commented_table`, and :func:`parse_transaction_list` — but
backed by ``selectolax.lexbor.LexborHTMLParser`` instead of ``lxml`` + ``parsel``.

Activation
----------
The selectolax backend is the **default**. The parsel backend is opt-in
via the ``COURTSIDE_DATA_PARSE_BACKEND=parsel`` environment variable.
Set ``COURTSIDE_DATA_PARSE_BACKEND=selectolax`` explicitly to lock in
the default (useful in deployment manifests).

For backward compatibility, the legacy ``COURTSIDE_DATA_FAST_PARSE=1``
flag is still honored and treated as ``selectolax``;
``COURTSIDE_DATA_FAST_PARSE=0`` is treated as ``parsel``. When both
env vars are set, ``COURTSIDE_DATA_PARSE_BACKEND`` wins.

The :func:`is_selectolax_backend` and :func:`is_parsel_backend` predicates
read the env via :func:`courtside_data.config.parse_backend` on every
call so tests can flip the dispatch via ``monkeypatch.setenv`` without
reloading modules. The parsing hot paths in
:mod:`courtside_data.parsing.tables` and
:mod:`courtside_data.parsing.generic` consult those helpers and dispatch
to :func:`build_selectolax_table`, :func:`selectolax_extract_commented_table`,
or :func:`selectolax_parse_transaction_list` when selectolax is active.

When the parsel backend is selected, this module is not consulted at all
and the existing parsel-based code paths run unchanged.

Module shape
------------
* :class:`_SelectolaxGenericTableRow` and :class:`_SelectolaxGenericTable`
  mirror the parsel versions row-for-row, including the leaderboard
  ``value``-column rename and header-row filtering.
* :func:`selectolax_extract_commented_table` works on **raw HTML text** (not a
  parsel ``Selector``) so the caller can feed it either the document source
  string or a serialized subtree. selectolax's parser does not expose HTML
  comments, so a small regex over the original source string is used to
  locate the comment block; the inner HTML is then parsed and the table
  returned as a selectolax node.
* :func:`selectolax_parse_transaction_list` is the selectolax analogue of
  :func:`parse_transaction_list`. It takes raw HTML text.

Importing this module is side-effect-free: ``selectolax`` is imported lazily
inside the public helpers so importing the module costs nothing when the
parsel backend is selected.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from courtside_data import config
from courtside_data.parsing._table_shared import (
    clean_text,
    normalize_header,
    normalize_value_column,
    selector_subtree_to_html,
)

if TYPE_CHECKING:
    from selectolax.lexbor import LexborNode as _SLNode

# Re-exports for backward compatibility — the env-var names and the
# set of valid backend identifiers live in :mod:`courtside_data.config`
# (the single source of truth for env-var access). External code that
# imported these from ``_selectolax_backend`` still gets the same values.
_PARSE_BACKEND_ENV_VAR = config.COURTSIDE_DATA_PARSE_BACKEND_ENV
_FAST_PARSE_ENV_VAR = config.COURTSIDE_DATA_FAST_PARSE_ENV  # legacy alias
_VALID_BACKENDS: frozenset[str] = config._VALID_PARSE_BACKENDS


def get_parse_backend() -> str:
    """Return the active HTML-parsing backend (``'selectolax'`` or ``'parsel'``).

    Thin wrapper around :func:`courtside_data.config.parse_backend`; the
    check is performed against ``os.environ`` on every call so tests can
    flip the backend via ``monkeypatch.setenv`` without reloading modules.
    """
    return config.parse_backend()


def is_selectolax_backend() -> bool:
    """Return ``True`` when the selectolax (Lexbor) backend is the active parser."""
    return get_parse_backend() == "selectolax"


def is_parsel_backend() -> bool:
    """Return ``True`` when the parsel/lxml backend is the active parser."""
    return get_parse_backend() == "parsel"


def is_fast_parse_enabled() -> bool:
    """Return ``True`` when the selectolax (fast-parse) backend is the active parser.

    Deprecated alias for :func:`is_selectolax_backend`. Retained for
    backward compatibility with code/tests that probe the legacy
    ``COURTSIDE_DATA_FAST_PARSE`` flag. New code should call
    :func:`is_selectolax_backend` or :func:`is_parsel_backend` instead.
    """
    return is_selectolax_backend()


# ─── Selectolax node helpers ────────────────────────────────────────────────


def _node_all_attrs(node: _SLNode) -> dict[str, str]:
    """Collect attributes from a selectolax node and all its descendants.

    Mirrors parsel's ::

        for element in [cell, *cell.css("*")]:
            for key, value in element.attrib.items():
                ...

    ``node.attributes`` already returns a mutable dict, but we copy it
    so callers can't mutate the live tree by accident. selectolax stores
    attribute values as ``str | None``; we normalize ``None`` to ``""`` so
    the returned dict matches the parsel ``cell.attrib`` shape.
    """
    collected: dict[str, str] = {key: (value or "") for key, value in node.attributes.items()}
    for descendant in node.iter():
        for key, value in descendant.attributes.items():
            collected[key] = value or ""
    return collected


def _node_text(node: _SLNode) -> str:
    """Extract text from a selectolax node the way the parsel extractor does.

    Parsel does::

        " ".join(value.strip() for value in cell.css("::text").getall() if value.strip())

    which joins the cell's text fragments with a single space. selectolax's
    ``text(separator=" ", strip=True)`` produces an equivalent string for
    the HTML Basketball-Reference emits (text nodes only; no entity-mangled
    whitespace). We additionally strip the ``*`` annotation that BR uses
    for things like All-Star selections, matching the parsel behavior.
    """
    text = node.text(separator=" ", strip=True) or ""
    return text.replace("*", "").strip()


# ─── GenericTableRow / GenericTable equivalents ─────────────────────────────


class _SelectolaxGenericTableRow:
    """Selectolax-backed row with the same interface as :class:`GenericTableRow`.

    The public attributes (``get``, ``to_dict``, ``metadata``) match the
    parsel version exactly so the two can be used interchangeably by callers
    that only need the extracted data.
    """

    def __init__(self, node: _SLNode, fallback_headers: list[str] | None = None) -> None:
        self._data: dict[str, str] = {}
        self._metadata: dict[str, dict[str, str]] = {}
        for index, cell in enumerate(node.css("td, th")):
            stat: str | None = cell.attributes.get("data-stat")
            if not stat and fallback_headers is not None:
                stat = fallback_headers[index] if index < len(fallback_headers) else f"col_{index + 1}"
            if stat:
                self._data[stat] = _node_text(cell)
                attrs = _node_all_attrs(cell)
                attrs.pop("data-stat", None)
                self._metadata[stat] = attrs

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


class _SelectolaxGenericTable:
    """Selectolax-backed table with the same interface as :class:`GenericTable`.

    Construction is identical to the parsel version: pass a selectolax
    ``Node`` for the table element plus the same keyword toggles. The
    produced :attr:`rows` list contains :class:`_SelectolaxGenericTableRow`
    instances; downstream consumers call ``.to_dict()`` and read
    ``.metadata`` exactly as they would for the parsel variant.
    """

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
        """Two-pass normalization for leaderboard rows.

        Delegates to the shared
        :func:`courtside_data.parsing._table_shared.normalize_value_column`
        helper.
        """
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


# ─── parsel → selectolax table adapter ─────────────────────────────────────


def _find_table_node_in_html(html: str, table_id: str | None) -> _SLNode | None:
    """Parse ``html`` and return the first matching row-container node.

    Prefers the explicit ``table_id`` when present (which matches the
    parsel selector's ``attrib['id']``) and falls back to the first
    ``<table>`` element. Returns ``None`` if nothing matches.

    Note: callers may pass selectors wrapping *any* row container — e.g.
    a ``<tfoot>`` from :func:`courtside_data.parsing.rows.parse_team_box_score`.
    The selectolax :class:`_SelectolaxGenericTable` walks ``tr`` elements
    inside the node it's given, so the node just needs to be a row
    container (table / thead / tbody / tfoot), not specifically a
    ``<table>``.
    """
    from selectolax.lexbor import LexborHTMLParser

    root = LexborHTMLParser(html)
    if table_id:
        node = root.css_first(f"table#{table_id}")
        if node is not None:
            return node
    return root.css_first("table")


def _row_container_node(html: str) -> _SLNode | None:
    """Return the selectolax node that corresponds to the parsel selector's subtree.

    Selectolax always wraps the input in an ``<html><body>`` shell, so the
    re-parsed tree's root is the ``<body>`` element when the input is a
    full document, or the first child of ``<body>`` when the input is a
    fragment. This helper finds the topmost meaningful row container
    (``<table>`` or any ``<thead>``/``<tbody>``/``<tfoot>``) inside the
    re-parsed tree.

    Returns the ``<body>`` itself when nothing matching is found, which
    :class:`_SelectolaxGenericTable` handles as a no-op (no ``tr`` rows
    inside ``<body>`` unless there happen to be loose ones, in which
    case those are extracted — matching parsel's behavior).
    """
    from selectolax.lexbor import LexborHTMLParser

    root = LexborHTMLParser(html)
    # The first child of <body> is the user's fragment (e.g. <table> or <tfoot>).
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
    """Build a :class:`_SelectolaxGenericTable` from a parsel table ``Selector``.

    The parsel ``Selector`` is re-serialized to HTML and re-parsed with
    selectolax so the selectolax backend operates on its native tree.
    The output rows are equivalent to those produced by the parsel
    :class:`GenericTable` for the same input.

    Supports any row container the parsel path accepts (``<table>``,
    ``<tfoot>``, ``<tbody>``, ``<thead>``): bare row containers are
    wrapped in a synthetic ``<table>`` so selectolax preserves them.

    When the re-parsed HTML does not contain a matching container, the
    returned table has an empty ``rows`` list — mirroring the parsel
    ``GenericTable`` behavior for the same input.
    """
    table_id = table_selector.attrib.get("id")
    raw_html = selector_subtree_to_html(table_selector.root)
    root_tag = _detect_root_tag(table_selector)
    needs_unwrap = root_tag in {"thead", "tbody", "tfoot", "tr"}
    html = f"<table>{raw_html}</table>" if needs_unwrap else raw_html

    if needs_unwrap:
        # Re-locate the wrapped container after the synthetic <table>.
        from selectolax.lexbor import LexborHTMLParser

        wrapped = LexborHTMLParser(html).css_first("table")
        if wrapped is None:
            empty = object.__new__(_SelectolaxGenericTable)
            empty.rows = []
            return empty
        # Drill into the original container so ``_fallback_headers`` and
        # other methods that target the original row container see it.
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
    # The parsel selector may be a non-<table> row container (e.g. a
    # <tfoot> passed in by parse_team_box_score). Locate the fragment
    # that corresponds to it inside selectolax's <body> wrapper.
    container = _row_container_node(html)
    if container is None or container.tag not in {"table", "thead", "tbody", "tfoot"}:
        empty = object.__new__(_SelectolaxGenericTable)
        empty.rows = []
        return empty
    return _SelectolaxGenericTable(
        container,
        use_header_fallback=use_header_fallback,
        exclude_summary_rows=exclude_summary_rows,
        value_column=value_column,
    )


# ─── Commented-table extraction ────────────────────────────────────────────


def selectolax_extract_commented_table(html_text: str, table_id: str) -> str | None:
    """Find a table inside an HTML comment and return its inner HTML.

    selectolax's ``LexborHTMLParser`` does not expose HTML comments in its
    tree (it drops them), so we scan the original HTML text with a regex.
    When a comment contains the target ``id="<table_id>"`` (or
    ``id='<table_id>'``) attribute, the comment tags are stripped and the
    resulting HTML is parsed with selectolax; if it contains the desired
    ``<table id="...">`` element, the table's HTML is returned for the
    caller to wrap in whatever tree representation the public surface
    requires.
    """
    for comment in re.findall(r"<!--.*?-->", html_text, flags=re.DOTALL):
        if f'id="{table_id}"' in comment or f"id='{table_id}'" in comment:
            clean_html = comment.replace("<!--", "").replace("-->", "").strip()
            table_node = _find_table_node_in_html(clean_html, table_id)
            if table_node is not None:
                return table_node.html
    return None


# ─── Transaction-list parsing ──────────────────────────────────────────────


def selectolax_parse_transaction_list(html_text: str) -> list[dict[str, Any]]:
    """Selectolax equivalent of :func:`parse_transaction_list`.

    Mirrors the parsel version's behavior:

    * Group entries by day (``<ul.page_index > li>``), using the first
      ``<span>`` inside the ``<li>`` as the date label.
    * Within each day, iterate over ``<p>`` elements that contain a
      ``class="... transaction ..."`` attribute; if none exist, fall back
      to every ``<p>`` that has non-whitespace text content.
    * For each ``<p>`` transaction, collect all ``<a>`` children, recording
      ``data-attr-from`` / ``data-attr-to`` shorthand and the rendered
      text/href.

    Returns the same ``list[dict[str, Any]]`` shape as the parsel version.
    """
    from selectolax.lexbor import LexborHTMLParser

    root = LexborHTMLParser(html_text)
    transactions: list[dict[str, Any]] = []

    def _is_transaction_p(node: _SLNode) -> bool:
        cls = node.attributes.get("class") or ""
        if "transaction" in cls.split():
            return True
        # Fallback: non-empty text (matches the parsel ``p[normalize-space()]`` branch).
        return bool(node.text(separator=" ", strip=True) or "")

    for day in root.css("ul.page_index > li"):
        # date: text of the first <span> descendant of the <li>
        first_span = day.css_first("span")
        date = (first_span.text(separator=" ", strip=True) if first_span is not None else "") or ""
        # transaction nodes: prefer p.transaction, fall back to p with text
        transaction_nodes = [n for n in day.css("p.transaction") if _is_transaction_p(n)]
        if not transaction_nodes:
            transaction_nodes = [n for n in day.css("p") if _is_transaction_p(n)]
        for transaction in transaction_nodes:
            linked_resources: list[dict[str, Any]] = []
            from_team_abbreviations: list[str] = []
            to_team_abbreviations: list[str] = []
            for link in transaction.css("a"):
                attrs = link.attributes
                # selectolax's ``dict.get`` returns ``None`` for missing keys;
                # normalize to ``""`` to match the parsel ``link.attrib.get(...)`` shape.
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
