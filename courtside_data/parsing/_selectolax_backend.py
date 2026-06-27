"""Re-export facade for the selectolax parsing backend.

The backend is split into focused private modules:

* ``_selectolax_tables`` owns the row/table primitives.
* ``_selectolax_adapter`` adapts parsel selectors into selectolax tables.
* ``_selectolax_extractors`` owns commented-table and transaction-list parsing.

This module exposes the parser-backend selection helpers and selectolax
implementations used by :mod:`courtside_data.parsing.tables`.
"""

from __future__ import annotations

from courtside_data import config
from courtside_data.parsing._selectolax_adapter import (
    _detect_root_tag,
    _find_table_node_in_html,
    _row_container_node,
    build_selectolax_table,
)
from courtside_data.parsing._selectolax_extractors import (
    selectolax_extract_commented_table,
    selectolax_parse_transaction_list,
)
from courtside_data.parsing._selectolax_tables import (
    _node_all_attrs,
    _node_text,
    _SelectolaxGenericTable,
    _SelectolaxGenericTableRow,
)

__all__ = (
    "_PARSE_BACKEND_ENV_VAR",
    "_VALID_BACKENDS",
    "_SelectolaxGenericTable",
    "_SelectolaxGenericTableRow",
    "_detect_root_tag",
    "_find_table_node_in_html",
    "_node_all_attrs",
    "_node_text",
    "_row_container_node",
    "build_selectolax_table",
    "get_parse_backend",
    "is_parsel_backend",
    "is_selectolax_backend",
    "selectolax_extract_commented_table",
    "selectolax_parse_transaction_list",
)

_PARSE_BACKEND_ENV_VAR = config.COURTSIDE_DATA_PARSE_BACKEND_ENV
_VALID_BACKENDS: frozenset[str] = config._VALID_PARSE_BACKENDS


def get_parse_backend() -> str:
    """Return the active HTML-parsing backend (``'selectolax'`` or ``'parsel'``)."""
    return config.parse_backend()


def is_selectolax_backend() -> bool:
    """Return ``True`` when the selectolax backend is the active parser."""
    return get_parse_backend() == "selectolax"


def is_parsel_backend() -> bool:
    """Return ``True`` when the parsel/lxml backend is the active parser."""
    return get_parse_backend() == "parsel"
