"""Tests for the search schema and parser.

Two pieces here:

1. The :class:`SearchResultRow` schema gains a ``type`` discriminator
   field. Defaults to ``"player"`` for player-hub back-compat and
   accepts the six canonical BR entity types: ``player``, ``team``,
   ``coach``, ``executive``, ``referee``, and ``other``.

2. The row parser in :mod:`courtside_data.parsing._rows_search` walks
   every sub-`div` of ``div#searches`` and stamps each card with the
   ``type`` that matches its parent sub-`div` id. Unknown sub-`div`
   ids are stamped ``"other"`` (forward-compat for new BR indexes).

3. The :class:`SearchResultRow` parser preserves the **case** of the
   identifier, so a team href ``/teams/BOS/`` resolves to ``"BOS"``
   (uppercase) — the deep-link ``/teams/{identifier}/summary`` will
   404 if the identifier is lowercased.
"""

from __future__ import annotations

import pytest
from courtside_data.parsing.rows import parse_search_rows
from courtside_data.schemas.search import SearchResultRow
from parsel import Selector
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# Schema: ``type`` discriminator
# ---------------------------------------------------------------------------


def test_search_result_row_default_type_is_player() -> None:
    """Default is ``player`` for back-compat with player-hub callers."""
    # The Pydantic ``BeforeValidator`` for ``leagues`` accepts strings and
    # coerces to ``set[League]``; the static type still says
    # ``set[League]`` though, so the runtime-valid set is intentionally
    # cast through the boundary.
    row = SearchResultRow(name="Kobe Bryant", identifier="bryanko01", leagues={"NBA"})  # ty: ignore[invalid-argument-type]
    assert row.type == "player"


@pytest.mark.parametrize("type_value", ["player", "team", "coach", "executive", "referee", "other"])
def test_search_result_row_accepts_canonical_type_values(type_value: str) -> None:
    """All six canonical entity types round-trip through the model."""
    row = SearchResultRow(
        name="Boston Celtics",
        identifier="BOS",
        leagues={"NBA"},  # ty: ignore[invalid-argument-type]
        type=type_value,  # ty: ignore[invalid-argument-type]
    )
    assert row.type == type_value


def test_search_result_row_rejects_unknown_type() -> None:
    """Closed Literal: any value outside the canonical set is rejected."""
    with pytest.raises(ValidationError):
        SearchResultRow(
            name="X",
            identifier="x",
            leagues=set(),
            type="galaxy",  # ty: ignore[invalid-argument-type]
        )


# ---------------------------------------------------------------------------
# Parser: ``type`` comes from the parent sub-`div` id
# ---------------------------------------------------------------------------


def _make_html(cards: list[tuple[str, str, str]]) -> str:
    """Synthesize a minimal ``div#searches`` page with one card per
    (sub_div_id, name, href) triple.

    Mirrors the BR markup shape documented in
    ``ideas/br-search-idx-research-2026-06-28.md`` §2.
    """
    sub_divs: dict[str, list[tuple[str, str]]] = {}
    for sub_div_id, name, href in cards:
        sub_divs.setdefault(sub_div_id, []).append((name, href))
    parts = ['<div id="searches" class="switcher_content">']
    for sub_div_id, items in sub_divs.items():
        parts.append(f'<div id="{sub_div_id}">')
        for name, href in items:
            parts.append(
                '<div class="search-item">'
                '<div class="search-item-name">'
                f'<a href="{href}">{name}</a>'
                "</div>"
                f'<div class="search-item-url">{href}</div>'
                "</div>"
            )
        parts.append("</div>")
    parts.append("</div>")
    return "".join(parts)


def test_parse_search_rows_stamps_type_from_sub_div() -> None:
    """One card per sub-div: each row's ``type`` matches its parent id."""
    html = _make_html(
        [
            ("players", "LeBron James", "/players/j/jamesle01.html"),
            ("coaches", "Gregg Popovich", "/coaches/popovgr99c.html"),
            ("executives", "Danny Ainge", "/executives/aingeda01x.html"),
            ("referees", "Jack Madden", "/referees/maddeja99r.html"),
            ("teams", "Boston Celtics", "/teams/BOS/"),
            ("team_seasons", "1975 New Orleans Jazz", "/teams/NOJ/1975.html"),
        ]
    )
    rows = parse_search_rows(Selector(text=html))
    type_by_id = {r["identifier"]: r["type"] for r in rows}
    assert type_by_id["jamesle01"] == "player"
    assert type_by_id["popovgr99c"] == "coach"
    assert type_by_id["aingeda01x"] == "executive"
    assert type_by_id["maddeja99r"] == "referee"
    # The franchise card (``teams`` sub-`div`) carries the team
    # abbreviation as its identifier. ``team_seasons`` hrefs end in
    # the year segment (e.g. ``/teams/NOJ/1975.html`` → ``"1975"``),
    # so the dedupe-by-identifier strategy in the team-search service
    # uses the franchise card's identifier and discards the per-season
    # row. Both sub-`div`s nonetheless stamp ``"team"`` as the type
    # so callers can filter on the discriminator.
    assert type_by_id["BOS"] == "team"
    team_seasons_rows = [r for r in rows if r["type"] == "team"]
    # ``team_seasons`` hrefs are ``/teams/{ABBR}/{YEAR}.html``; the
    # parser extracts the team abbreviation (not the year) as the
    # identifier, so the team-search dedupe-by-identifier can
    # collapse the per-season card into the franchise card. See
    # ``ideas/br-search-idx-research-2026-06-28.md`` §1 (the
    # ``teams`` vs ``team_seasons`` footnote).
    assert any(r["identifier"] == "NOJ" for r in team_seasons_rows)


def test_parse_search_rows_team_seasons_identifier_is_abbr_not_year() -> None:
    """A ``team_seasons`` card href ``/teams/{ABBR}/{YEAR}.html`` must
    resolve to ``{ABBR}`` as the identifier, **not** ``{YEAR}``.

    The team-search service dedupes by identifier: the per-season
    card from the ``team_seasons`` sub-`div` and the franchise card
    from the ``teams`` sub-`div` (href ``/teams/UTA/``) both point
    at the same franchise. If the per-season card's identifier were
    ``"1997"`` instead of ``"UTA"``, the dedupe would miss it and the
    per-season row would leak into the team-search results — and
    clicking it would 404 (the deep-link is
    ``/teams/{identifier}/summary``).

    This test feeds three cards (one ``teams``, two ``team_seasons``
    for different years) and asserts every card's identifier is the
    team abbreviation.
    """
    html = _make_html(
        [
            ("teams", "Utah Jazz", "/teams/UTA/"),
            ("team_seasons", "1997 Utah Jazz (1997)", "/teams/UTA/1997.html"),
            ("team_seasons", "2024 Utah Jazz (2024)", "/teams/UTA/2024.html"),
        ]
    )
    rows = parse_search_rows(Selector(text=html))
    assert len(rows) == 3
    identifiers = {r["identifier"] for r in rows}
    assert identifiers == {"UTA"}
    # Sanity: the year-as-identifier bug is gone.
    assert "1997" not in identifiers
    assert "2024" not in identifiers


def test_parse_search_rows_unknown_sub_div_defaults_to_other() -> None:
    """Forward-compat: an unknown sub-div id (e.g. a new BR index) is
    stamped ``"other"`` instead of being dropped.
    """
    html = _make_html([("future_index", "Mystery Entity", "/future/x/")])
    rows = parse_search_rows(Selector(text=html))
    assert len(rows) == 1
    assert rows[0]["type"] == "other"


def test_parse_search_rows_preserves_team_identifier_case() -> None:
    """Team hrefs are ``/teams/BOS/`` — the parser must NOT lowercase.

    The deep-link ``/teams/{identifier}/summary`` will 404 if
    identifier is lowercased; only player hrefs are case-insensitive.
    """
    html = _make_html(
        [
            ("teams", "Boston Celtics", "/teams/BOS/"),
            ("players", "Larry Bird", "/players/b/birdla01.html"),
        ]
    )
    rows = parse_search_rows(Selector(text=html))
    ids = {r["identifier"] for r in rows}
    assert "BOS" in ids
    assert "birdla01" in ids
    assert "bos" not in ids
