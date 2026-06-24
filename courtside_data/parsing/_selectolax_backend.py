"""Re-export facade for the selectolax parsing backend.

The backend is split into focused private modules:

* ``_selectolax_tables`` owns the row/table primitives.
* ``_selectolax_adapter`` adapts parsel selectors into selectolax tables.
* ``_selectolax_extractors`` owns commented-table and transaction-list parsing.

This module re-exports those names so existing imports from
``courtside_data.parsing._selectolax_backend`` keep working.
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
    "_FAST_PARSE_ENV_VAR",
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
    "is_fast_parse_enabled",
    "is_parsel_backend",
    "is_selectolax_backend",
    "selectolax_extract_commented_table",
    "selectolax_parse_transaction_list",
)

# Re-exports for backward compatibility. The env-var names and the set of valid
# backend identifiers live in courtside_data.config as the single source of truth.
_PARSE_BACKEND_ENV_VAR = config.COURTSIDE_DATA_PARSE_BACKEND_ENV
_FAST_PARSE_ENV_VAR = config.COURTSIDE_DATA_FAST_PARSE_ENV
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


def is_fast_parse_enabled() -> bool:
    """Return ``True`` when the selectolax backend is active.

    Deprecated alias for :func:`is_selectolax_backend`, retained for callers
    that still probe the ``COURTSIDE_DATA_FAST_PARSE`` compatibility flag.
    """
    return is_selectolax_backend()
