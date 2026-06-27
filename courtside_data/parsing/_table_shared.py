"""Shared pure helpers for the parsel and selectolax parsing backends.

These operate on plain Python types (``str``, ``list[str]``,
``dict[str, str]``, sequence-of-row-objects with ``._data``) and
contain no backend-specific node-type references.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

# ─── Leaderboard column keys ────────────────────────────────────────────────

# Column keys on the leaders pages that are NEVER the rotating stat value.
# They are text/identity columns whose header does not rotate with the active
# stat category. Used by :func:`normalize_value_column` to identify the
# rightmost non-text column and rename it to ``value``.
_LEADER_TEXT_COLUMN_KEYS: frozenset[str] = frozenset({"rank", "player", "season", "team", "team_id"})

_CSK_VALUE_KEYS: frozenset[str] = frozenset(
    {
        "birth_date",
        "date_update",
        "salary",
        "age_today",
        "y1",
        "y2",
        "y3",
        "y4",
        "y5",
        "y6",
        "remain_gtd",
    }
)
_FLAG_CLASS_RE = re.compile(r"(?:^|\s)f-([a-z]{2})(?:\s|$)", re.IGNORECASE)


# ─── Text helpers ───────────────────────────────────────────────────────────


def clean_text(values: list[str]) -> str:
    """Collapse runs of whitespace and strip."""
    return re.sub(r"\s+", " ", " ".join(values)).strip()


def normalize_header(value: str) -> str:
    """Slugify a header value to a safe key."""
    header = re.sub(r"[^0-9A-Za-z]+", "_", value.strip().lower()).strip("_")
    return header or "col"


def canonical_cell_value(stat: str, text: str, attrs: dict[str, str]) -> str:
    """Return the stable machine value for BR cells that expose one.

    Basketball-Reference often renders a display value (``"$4,171,200"``,
    ``"November 7, 1999"``, ``"ca CA"``) alongside a better machine value
    in either ``csk`` or the flag span class. This helper is deliberately
    stat-key scoped: many unrelated cells also carry ``csk`` sort values
    (player names, positions, heights) whose display value is the public API
    contract.
    """
    if stat == "flag":
        return _canonical_flag_value(text, attrs)
    csk = attrs.get("csk")
    if stat in _CSK_VALUE_KEYS and csk:
        return csk.strip()
    return text


def _canonical_flag_value(text: str, attrs: dict[str, str]) -> str:
    class_value = attrs.get("class", "")
    match = _FLAG_CLASS_RE.search(class_value)
    if match is not None:
        return match.group(1).upper()

    parts = text.split()
    if parts:
        return parts[-1].upper()
    return text


# ─── Value-column normalization (leaderboard tables) ────────────────────────


def normalize_value_column(rows: Sequence[Any]) -> None:
    """Apply the leaderboard ``value``-column rename and ``rank`` trailing-dot
    strip in place.

    Operates on any sequence of row objects exposing a ``_data: dict[str, str]``
    attribute, so it is shared by the parsel and selectolax backends.

    Two passes per row:

    1. **Rank period strip**: BR renders rank values as ``"1."``, ``"2."``
       (trailing period). The shared ``_br_int`` validator rejects ``"1."``
       as non-integer, so we strip the trailing period before the row reaches
       the schema.
    2. **Value column rename**: the leaders pages emit a column whose header
       rotates with the active stat category (``per``, ``pts``, ``ast``,
       ``blk`` …). A static ``validation_alias`` cannot cover every category,
       so this pass renames the rotating column to a stable ``value`` key
       that downstream row models can match. The rename target is the
       rightmost key on each row that is NOT one of
       :data:`_LEADER_TEXT_COLUMN_KEYS`. Rows that already expose a ``value``
       key are left untouched.
    """
    for row in rows:
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


# ─── HTML serialization ─────────────────────────────────────────────────────


def selector_subtree_to_html(root) -> str:
    """Serialize an lxml element subtree to a UTF-8 HTML string.

    ``method="html"`` is required to keep lxml from collapsing empty
    elements like ``<a data-attr-from=""></a>`` into the self-closing form
    ``<a data-attr-from=""/>`` — the self-closing form changes the meaning
    of ``node.text()`` in selectolax, which (incorrectly) hoists the
    following sibling text into the link.

    We use :func:`lxml.html.tostring` (a pure-Python helper around the
    same machinery) so the import is resolvable by the ``ty`` type checker;
    it produces the same output as
    ``lxml.etree.tostring(..., method="html")``.
    """
    from lxml.html import tostring

    result = tostring(root, encoding="unicode")
    return result if isinstance(result, str) else result.decode("utf-8")
