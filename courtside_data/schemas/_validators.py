"""Pydantic ``BeforeValidator`` functions for Basketball-Reference cell coercion.

These validators transform the raw string cells BR emits into typed Python
values (``int``, ``float``, ``date``, enums, etc.). They are consumed by the
``Annotated[...]`` type aliases in ``_fields.py``.

All names remain importable from ``courtside_data.schemas._fields`` for
backward compatibility.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from courtside_data.data import (
    LEAGUE_ABBREVIATIONS_TO_LEAGUE,
    LOCATION_ABBREVIATIONS_TO_LOCATION,
    OUTCOME_ABBREVIATIONS_TO_OUTCOME,
    POSITION_ABBREVIATIONS_TO_POSITION,
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    Conference,
    Division,
    League,
    Location,
    Outcome,
    Position,
    Team,
)

_EMPTY_VALUES = frozenset({"", "\xa0"})


def _is_empty(value: object) -> bool:
    """Return True for empty strings, non-breaking spaces, and None."""
    if value is None:
        return True
    s = str(value).strip()
    return s in _EMPTY_VALUES or s == ""


def _str_or_none(value: object) -> str | None:
    """Free-form text cell coerced to ``None`` when empty (e.g. ``awards``)."""
    if _is_empty(value):
        return None
    return str(value).strip()


def _br_int(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    s = str(value).strip()
    if s in _EMPTY_VALUES:
        raise ValueError(f"Invalid integer value: {value!r}")
    s = s.replace(",", "")
    try:
        return int(s)
    except ValueError as exc:
        raise ValueError(f"Invalid integer value: {value!r}") from exc


def _br_int_or_none(value: object) -> int | None:
    if _is_empty(value):
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    s = str(value).strip()
    s = s.replace(",", "")
    try:
        return int(s)
    except ValueError as exc:
        raise ValueError(f"Invalid integer value: {value!r}") from exc


_RANK_TIE_SUFFIX = "T"


def _br_award_rank(value: object) -> int | None:
    """Parse an award-voting rank cell, tolerating BR's tied-rank suffix.

    Basketball Reference renders tied award-voting ranks as ``"7T"`` /
    ``"10T"``. This validator strips the trailing ``T`` and returns the
    integer rank (``7``, ``10``). Blank cells become ``None``. The tie
    information itself is surfaced separately via the companion
    :func:`_rank_tied` validator / :data:`RankTied` field rather than being
    silently dropped.

    This is intentionally narrow: it is only applied to award ``rank``
    fields, never to the general-purpose :data:`BRInt` / :data:`BRIntOrNone`.
    """
    if _is_empty(value):
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    s = str(value).strip()
    if s.upper().endswith(_RANK_TIE_SUFFIX):
        s = s[:-1].strip()
    s = s.replace(",", "")
    try:
        return int(s)
    except ValueError as exc:
        raise ValueError(f"Invalid rank value: {value!r}") from exc


def _rank_tied(value: object) -> bool:
    """Return ``True`` when a rank cell carries BR's tied-rank suffix (``7T``)."""
    if _is_empty(value):
        return False
    return str(value).strip().upper().endswith(_RANK_TIE_SUFFIX)


def _br_float(value: object) -> float:
    if isinstance(value, float):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return float(value)
    s = str(value).strip()
    if s in _EMPTY_VALUES:
        raise ValueError(f"Invalid float value: {value!r}")
    try:
        return float(s)
    except ValueError as exc:
        raise ValueError(f"Invalid float value: {value!r}") from exc


def _br_float_or_none(value: object) -> float | None:
    if _is_empty(value):
        return None
    if isinstance(value, float):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return float(value)
    s = str(value).strip()
    try:
        return float(s)
    except ValueError as exc:
        raise ValueError(f"Invalid float value: {value!r}") from exc


def _seconds_played(value: object) -> int:
    if value is None:
        return 0
    s = str(value).strip()
    if s in _EMPTY_VALUES:
        return 0
    parts = s.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid playing time format: {value!r}")
    try:
        minutes = int(parts[0])
        seconds = int(parts[1])
    except ValueError as exc:
        raise ValueError(f"Invalid playing time format: {value!r}") from exc
    return 60 * minutes + seconds


def _seconds_played_or_none(value: object) -> int | None:
    if _is_empty(value):
        return None
    return _seconds_played(value)


def _team_field(value: object) -> Team:
    if isinstance(value, Team):
        return value
    s = str(value).strip()
    team = TEAM_ABBREVIATIONS_TO_TEAM.get(s)
    if team is None:
        raise ValueError(f"Unknown team abbreviation: {value!r}")
    return team


def _team_name_field(value: object) -> Team:
    if isinstance(value, Team):
        return value
    s = str(value).strip().upper()
    team = TEAM_NAME_TO_TEAM.get(s)
    if team is None:
        normalized = " ".join(s.replace(".", "").split())
        for name, mapped in TEAM_NAME_TO_TEAM.items():
            if normalized == " ".join(name.replace(".", "").split()):
                return mapped
        raise ValueError(f"Unknown team name: {value!r}")
    return team


def _location_field(value: object) -> Location:
    if isinstance(value, Location):
        return value
    s = str(value).strip()
    location = LOCATION_ABBREVIATIONS_TO_LOCATION.get(s)
    if location is None:
        raise ValueError(f"Unknown location symbol: {value!r}")
    return location


_OUTCOME_REGEX = re.compile(r"^(W|L)")


def _outcome_field(value: object) -> Outcome:
    if isinstance(value, Outcome):
        return value
    s = str(value).strip()
    match = _OUTCOME_REGEX.match(s)
    if match is None:
        raise ValueError(f"Unknown outcome symbol: {value!r}")
    outcome = OUTCOME_ABBREVIATIONS_TO_OUTCOME.get(match.group(1))
    if outcome is None:
        raise ValueError(f"Unknown outcome symbol: {value!r}")
    return outcome


def _positions_field(value: object) -> list[Position]:
    if value is None:
        return []
    if isinstance(value, list):
        parsed_values: list[Position] = []
        for item in value:
            if isinstance(item, Position):
                parsed_values.append(item)
            else:
                parsed_values.extend(_positions_field(item))
        return parsed_values
    s = str(value).strip()
    if s in _EMPTY_VALUES:
        return []
    parsed: list[Position] = []
    for abbreviation in s.split("-"):
        position = POSITION_ABBREVIATIONS_TO_POSITION.get(abbreviation.strip())
        if position is None:
            raise ValueError(f"Unknown position abbreviation: {value!r}")
        parsed.append(position)
    return parsed


def _division_field(value: object) -> Division:
    if isinstance(value, Division):
        return value
    s = str(value).strip().upper()
    if s.endswith(" DIVISION"):
        s = s[:-9].strip()
    for division in Division:
        if division.value == s:
            return division
    raise ValueError(f"Unknown division: {value!r}")


def _conference_field(value: object) -> Conference:
    if isinstance(value, Conference):
        return value
    s = str(value).strip().upper()
    if s.endswith(" CONFERENCE"):
        s = s[:-11].strip()
    for conference in Conference:
        if conference.value == s:
            return conference
    raise ValueError(f"Unknown conference: {value!r}")


def _league_field(value: object) -> League:
    if isinstance(value, League):
        return value
    s = str(value).strip()
    league = LEAGUE_ABBREVIATIONS_TO_LEAGUE.get(s)
    if league is None:
        raise ValueError(f"Unknown league abbreviation: {value!r}")
    return league


_BR_STRICT_DATE_FORMATS = ("%a, %b %d, %Y", "%Y-%m-%d")
_BR_STRICT_DATETIME_FORMATS = (
    "%a, %b %d, %Y %I:%M %p",  # "Mon, Jan 01, 2024 8:30 PM"
    "%a, %b %d, %Y %I:%M%p",  # "Mon, Jan 01, 2024 8:30p" (m appended for %p)
)
# dateparser parser set: skip the heavier relative-time/timestamp parsers so
# the fallback stays cheap. ``absolute-time`` covers natural-language dates,
# ``custom-formats`` re-tries the strict strptime formats, and ``no-spaces-time``
# handles "8:30PM" style inputs.
_BR_DATEPARSER_PARSERS = ("absolute-time", "custom-formats", "no-spaces-time")


def _dateparser_parse(s: str) -> datetime | None:
    """Tolerant parse via :mod:`dateparser` — fallback only.

    Returns a **naive** :class:`datetime` on success, ``None`` on failure.
    ``dateparser`` is imported lazily so the strict path stays import-free.
    """
    try:
        import dateparser
    except ImportError:
        return None
    return dateparser.parse(
        s,
        languages=["en"],
        date_formats=[*_BR_STRICT_DATE_FORMATS, *_BR_STRICT_DATETIME_FORMATS],
        settings={"PARSERS": list(_BR_DATEPARSER_PARSERS)},
    )


def _br_date(value: object) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    # Strict first — try the known strptime formats with no extra cost.
    for fmt in _BR_STRICT_DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # Tolerant fallback: dateparser handles drifted/renamed BR date strings.
    parsed = _dateparser_parse(s)
    if parsed is None:
        raise ValueError(f"Invalid date value: {value!r}")
    return parsed.date()


def _br_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC)

    # Accept a tuple/list of (date_string, time_string) so callers can combine
    # separate BR columns (date + start_time) into one UTC datetime.
    if isinstance(value, tuple | list):
        if len(value) != 2:
            raise ValueError(f"Invalid datetime value: {value!r}")
        formatted_date, formatted_time_of_day = value
    else:
        formatted_date = value
        formatted_time_of_day = None

    date_s = str(formatted_date).strip()
    time_s = "" if formatted_time_of_day is None else str(formatted_time_of_day).strip()

    # Strict first — try the existing strptime path verbatim. The whole branch
    # is wrapped so any failure (new date format, new time format, both) routes
    # uniformly through the tolerant fallback below.
    try:
        if time_s in ("", " "):
            dt = datetime.strptime(date_s, "%a, %b %d, %Y")
        elif time_s[-2:].lower() in ("am", "pm"):
            dt = datetime.strptime(f"{date_s} {time_s}", "%a, %b %d, %Y %I:%M %p")
        else:
            # Newer BR format uses "p" or "a" suffix; add "m" for strptime's %p.
            dt = datetime.strptime(f"{date_s} {time_s}m", "%a, %b %d, %Y %I:%M%p")
    except ValueError:
        combined = f"{date_s} {time_s}".strip() if time_s else date_s
        dt = _dateparser_parse(combined)
        if dt is None:
            raise ValueError(f"Invalid datetime value: {value!r}") from None

    return dt.replace(tzinfo=ZoneInfo("US/Eastern")).astimezone(UTC)


def _br_salary(value: object) -> int | None:
    if value is None:
        return None
    s = str(value).strip()
    if s in _EMPTY_VALUES:
        return None
    cleaned = s.replace("$", "").replace(",", "").replace(" ", "")
    try:
        return int(cleaned)
    except ValueError as exc:
        raise ValueError(f"Invalid salary value: {value!r}") from exc


def _br_percentage(value: object) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if s in _EMPTY_VALUES:
        return None
    is_percentage = s.endswith("%")
    if is_percentage:
        s = s[:-1].strip()
    try:
        parsed = float(s)
    except ValueError as exc:
        raise ValueError(f"Invalid percentage value: {value!r}") from exc
    if is_percentage:
        parsed = parsed / 100.0
    return parsed


def _br_decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    s = str(value).strip()
    if s in _EMPTY_VALUES:
        raise ValueError(f"Invalid decimal value: {value!r}")
    try:
        return Decimal(s)
    except Exception as exc:
        raise ValueError(f"Invalid decimal value: {value!r}") from exc
