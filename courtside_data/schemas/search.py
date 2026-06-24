"""Row schema for the player search endpoint.

Basketball-Reference's search results page is a div-based listing rather than a
table, so the fetcher is expected to normalize each result into a dict
with the stable keys ``name``, ``identifier``, and ``leagues`` before passing it
to :class:`SearchResultRow`.  No ``data-stat`` aliases are required.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator, TypeAdapter

from courtside_data.data import League
from courtside_data.schemas._base import BRRow
from courtside_data.schemas._fields import LeagueField
from courtside_data.schemas._registry import register

_LEAGUE_ADAPTER = TypeAdapter(LeagueField)


def _parse_leagues(value: object) -> set[League]:
    """Split a BR league string such as ``NBA/ABA`` into a set of leagues.

    Accepts single abbreviations, slash/comma/space separated strings, and
    collections of ``League`` values.
    """
    if value is None:
        return set()
    if isinstance(value, League):
        return {value}
    if isinstance(value, set | list | tuple):
        return {_LEAGUE_ADAPTER.validate_python(item) for item in value}
    s = str(value).strip()
    if s in {"", "\xa0"}:
        return set()
    result: set[League] = set()
    for token in s.replace(",", "/").replace(" ", "/").split("/"):
        token = token.strip()
        if not token:
            continue
        result.add(_LEAGUE_ADAPTER.validate_python(token))
    return result


LeaguesField = Annotated[set[League], BeforeValidator(_parse_leagues)]


class SearchResultRow(BRRow):
    """A single player search result.

    ``identifier`` is the player slug extracted from the result URL (e.g.
    ``bryanko01``).  ``leagues`` contains the league(s) the player appeared in.
    """

    name: str
    identifier: str
    leagues: LeaguesField


register("search", SearchResultRow)
