"""Box-score row parsers (team totals, player rows, and game metadata)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from parsel import Selector

from courtside_data.parsing._rows_common import raw_rows_from_table
from courtside_data.parsing.cells import (
    cell_text,
    require_slug,
    score_outcome,
    slug_from_metadata,
    team_name_from_abbreviation,
)
from courtside_data.parsing.generic import find_table
from courtside_data.parsing.tables import GenericTable, GenericTableRow
from courtside_data.parsing.workflow_parsers._diagnostics import (
    IGNORE_EMPTY_TABLE,
    IGNORE_MISSING_FOOTER,
    increment_ignored,
)

_TEAM_HREF_RE = re.compile(r"/teams/([A-Z]{2,3})/\d{4}\.html")
_TIP_OFF_DATE_RE = re.compile(r"^(?P<tip_off>\d{1,2}:\d{2}\s*[AP]M),\s*(?P<game_date>.+)$")
_ATTENDANCE_RE = re.compile(r"Attendance:\s*([\d,]+)")
_DURATION_RE = re.compile(r"(?:Time of Game|Duration):\s*([0-9:]+)")


def _game_date_to_iso(value: str) -> str:
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return value.strip()


def _scorebox_teams(selector: Selector) -> list[dict[str, Any]]:
    teams: list[dict[str, Any]] = []
    for team_box in selector.css("div.scorebox div.scorebox_team"):
        href = team_box.css("strong a::attr(href)").get("")
        match = _TEAM_HREF_RE.search(href)
        if match is None:
            continue
        score_text = team_box.css("div.scores div.score::text").get("")
        teams.append(
            {
                "team_id": match.group(1),
                "score": int(score_text.strip()) if score_text.strip().isdigit() else None,
            }
        )
    if len(teams) < 2:
        raise ValueError(f"Expected away/home teams in scorebox, got {len(teams)}")
    return teams[:2]


def _team_context(selector: Selector) -> dict[str, dict[str, Any]]:
    away, home = _scorebox_teams(selector)
    away_score = away["score"]
    home_score = home["score"]
    if away_score is None or home_score is None:
        raise ValueError("Expected away/home scores in scorebox")
    return {
        away["team_id"]: {
            "opponent": home["team_id"],
            "location": "@",
            "outcome": score_outcome(away_score, home_score),
            "score": away_score,
        },
        home["team_id"]: {
            "opponent": away["team_id"],
            "location": "",
            "outcome": score_outcome(home_score, away_score),
            "score": home_score,
        },
    }


def _table_team_abbreviation(table: Selector, suffix: str) -> str | None:
    table_id = table.attrib.get("id", "")
    if not table_id.startswith("box-") or not table_id.endswith(suffix):
        return None
    return table_id.removeprefix("box-").removesuffix(suffix)


def parse_team_box_score_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return team totals for one game page plus parser diagnostics."""
    ignored_row_reason_counts: dict[str, int] = {}
    combined_team_totals: list[dict[str, Any]] = []
    basic_table_count = 0
    advanced_table_count = 0
    empty_table_count = 0

    for table in selector.css('table.stats_table[id^="box-"]'):
        table_id = table.attrib.get("id", "")
        if table_id.endswith("-game-advanced"):
            advanced_table_count += 1
        elif table_id.endswith("-game-basic"):
            basic_table_count += 1

    stat_table_count = basic_table_count + advanced_table_count

    for table in selector.css('table.stats_table[id$="-game-basic"]'):
        table_id = table.attrib.get("id", "")
        if not table_id.startswith("box-"):
            continue
        team_abbreviation = table_id.removeprefix("box-").removesuffix("-game-basic")
        footer = table.css("tfoot")
        if not footer:
            increment_ignored(ignored_row_reason_counts, IGNORE_MISSING_FOOTER)
            continue
        footer_rows = raw_rows_from_table(footer[0])
        if not footer_rows:
            empty_table_count += 1
            increment_ignored(ignored_row_reason_counts, IGNORE_EMPTY_TABLE)
            continue
        row = footer_rows[0][0]
        row["team_name_abbr"] = team_name_from_abbreviation(team_abbreviation)
        combined_team_totals.append(row)

    if len(combined_team_totals) < 2:
        raise ValueError(f"Expected 2 team totals in box score page, got {len(combined_team_totals)}")

    first_team_totals, second_team_totals = combined_team_totals[:2]
    first_team_totals["outcome"] = score_outcome(first_team_totals["pts"], second_team_totals["pts"])
    second_team_totals["outcome"] = score_outcome(second_team_totals["pts"], first_team_totals["pts"])
    parsed_rows = [first_team_totals, second_team_totals]

    stats = {
        "game_count": 1,
        "team_count": len(parsed_rows),
        "stat_table_count": stat_table_count,
        "basic_table_count": basic_table_count,
        "advanced_table_count": advanced_table_count,
        "empty_table_count": empty_table_count,
        "ignored_row_reason_counts": ignored_row_reason_counts,
    }
    return parsed_rows, stats


def parse_team_box_score(selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_team_box_score_with_stats(selector)
    return rows


def parse_player_box_scores_from_table_with_stats(
    table_selector: Selector,
    *,
    endpoint_name: str = "player_box_scores",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return daily-leader player rows and parser diagnostics from ``table#stats``."""
    raw_rows = list(raw_rows_from_table(table_selector))
    parsed_rows: list[dict[str, Any]] = []
    for row_index, (row, metadata) in enumerate(raw_rows):
        row["slug"] = slug_from_metadata(metadata, "player")
        require_slug(endpoint_name, row, row_index)
        parsed_rows.append(row)

    raw_column_count = len(raw_rows[0][0]) if raw_rows else 0
    stats = {
        "player_count": len(parsed_rows),
        "raw_row_count": len(raw_rows),
        "raw_column_count": raw_column_count,
        "stat_table_count": 1,
        "basic_table_count": 1,
        "advanced_table_count": 0,
        "selected_table_id": "stats",
    }
    return parsed_rows, stats


def parse_player_box_scores_from_table(table_selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_player_box_scores_from_table_with_stats(table_selector)
    return rows


def parse_box_score_player_basic_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return per-player basic rows from one game box-score page."""
    context_by_team = _team_context(selector)
    parsed_rows: list[dict[str, Any]] = []
    ignored_row_reason_counts: dict[str, int] = {}
    basic_table_count = 0

    for table in selector.css('table.stats_table[id$="-game-basic"]'):
        team_id = _table_team_abbreviation(table, "-game-basic")
        if team_id is None:
            continue
        basic_table_count += 1
        team_context = context_by_team.get(team_id)
        if team_context is None:
            increment_ignored(ignored_row_reason_counts, "unknown_team")
            continue

        is_starter = True
        for row_index, row_selector in enumerate(table.css("tbody tr")):
            row_class = row_selector.attrib.get("class", "")
            if "thead" in row_class.split():
                is_starter = False
                continue

            generic_row = GenericTableRow(row_selector)
            row: dict[str, Any] = dict(generic_row.to_dict())
            if not row:
                continue

            row["slug"] = slug_from_metadata(generic_row.metadata, "player")
            require_slug("box_score_player_basic", row, row_index)
            row["team_id"] = team_id
            row["opp_id"] = team_context["opponent"]
            row["game_location"] = team_context["location"]
            row["game_result"] = team_context["outcome"]
            row["is_starter"] = is_starter and "reason" not in row
            row["status"] = row.pop("reason", None)
            parsed_rows.append(row)

    stats = {
        "game_count": 1,
        "player_count": len(parsed_rows),
        "active_player_count": sum(1 for row in parsed_rows if row.get("status") is None),
        "inactive_player_count": sum(1 for row in parsed_rows if row.get("status") is not None),
        "team_count": len(context_by_team),
        "stat_table_count": basic_table_count,
        "basic_table_count": basic_table_count,
        "advanced_table_count": len(selector.css('table.stats_table[id$="-game-advanced"]')),
        "ignored_row_reason_counts": dict(ignored_row_reason_counts),
    }
    return parsed_rows, stats


def parse_box_score_player_basic(selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_box_score_player_basic_with_stats(selector)
    return rows


def parse_box_score_team_four_factors_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return per-team Four Factors rows from one game box-score page."""
    table = find_table(selector, "four_factors")
    if table is None:
        raise ValueError("Expected four_factors table in box score page")

    raw_rows = [row.to_dict() for row in GenericTable(table).rows]
    raw_column_count = len(raw_rows[0]) if raw_rows else 0
    parsed_rows: list[dict[str, Any]] = []
    for row in raw_rows:
        team_abbreviation = str(row.get("team_id", "")).strip()
        if not team_abbreviation:
            continue
        row["team_name_abbr"] = team_name_from_abbreviation(team_abbreviation)
        parsed_rows.append(row)

    if len(parsed_rows) != 2:
        raise ValueError(f"Expected 2 team four factor rows in box score page, got {len(parsed_rows)}")

    stats = {
        "game_count": 1,
        "team_count": len(parsed_rows),
        "raw_row_count": len(raw_rows),
        "raw_column_count": raw_column_count,
        "stat_table_count": 1,
        "selected_table_id": "four_factors",
        "ignored_row_reason_counts": {},
    }
    return parsed_rows, stats


def parse_box_score_team_four_factors(selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_box_score_team_four_factors_with_stats(selector)
    return rows


def _scorebox_meta(selector: Selector) -> dict[str, str | None]:
    metadata_divs = [cell_text(div) for div in selector.css("div.scorebox_meta > div")]
    result: dict[str, str | None] = {"game_date": None, "tip_off": None, "arena": None}
    if metadata_divs:
        first = metadata_divs[0]
        match = _TIP_OFF_DATE_RE.match(first)
        if match is not None:
            result["tip_off"] = match.group("tip_off")
            result["game_date"] = _game_date_to_iso(match.group("game_date"))
        else:
            result["game_date"] = _game_date_to_iso(first)
    if len(metadata_divs) > 1:
        result["arena"] = metadata_divs[1]
    return result


def _div_with_label(selector: Selector, label: str) -> Selector | None:
    for div in selector.css("#content div"):
        strong_text = "".join(div.xpath("./strong/text()").getall()).replace("\xa0", " ").strip()
        if strong_text.startswith(label):
            return div
    return None


def _inactive_players(selector: Selector) -> dict[str, list[str]]:
    inactive_div = _div_with_label(selector, "Inactive:")
    if inactive_div is None:
        return {}

    inactive_by_team: dict[str, list[str]] = {}
    current_team: str | None = None
    for child in inactive_div.root.iterchildren():
        tag = str(child.tag).lower()
        if tag == "span":
            team_text = " ".join(child.itertext()).replace("\xa0", " ").strip()
            current_team = team_text or None
            if current_team is not None:
                inactive_by_team.setdefault(current_team, [])
        elif tag == "a" and current_team is not None:
            name = " ".join(child.itertext()).strip()
            if name:
                inactive_by_team.setdefault(current_team, []).append(name)
    return inactive_by_team


def _officials(selector: Selector) -> list[str]:
    officials_div = _div_with_label(selector, "Officials:")
    if officials_div is None:
        return []
    return [cell_text(link) for link in officials_div.css("a") if cell_text(link)]


def _attendance(selector: Selector) -> str | None:
    attendance_div = _div_with_label(selector, "Attendance:")
    if attendance_div is None:
        return None
    match = _ATTENDANCE_RE.search(cell_text(attendance_div))
    return match.group(1) if match is not None else None


def _duration(selector: Selector) -> str | None:
    for div in selector.css("#content > div"):
        match = _DURATION_RE.search(cell_text(div))
        if match is not None:
            return match.group(1)
    return None


def parse_box_score_game_info_with_stats(selector: Selector) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return one game-level metadata row from a box-score page."""
    away, home = _scorebox_teams(selector)
    metadata = _scorebox_meta(selector)
    inactive_by_team = _inactive_players(selector)
    row = {
        "game_date": metadata["game_date"],
        "home_team": home["team_id"],
        "away_team": away["team_id"],
        "home_team_score": home["score"],
        "away_team_score": away["score"],
        "arena": metadata["arena"],
        "attendance": _attendance(selector),
        "duration": _duration(selector),
        "tip_off": metadata["tip_off"],
        "officials": _officials(selector),
        "inactive_home": inactive_by_team.get(home["team_id"], []),
        "inactive_away": inactive_by_team.get(away["team_id"], []),
    }
    stats = {
        "game_count": 1,
        "team_count": 2,
        "official_count": len(row["officials"]),
        "inactive_player_count": len(row["inactive_home"]) + len(row["inactive_away"]),
        "scorebox_meta_count": len(selector.css("div.scorebox_meta > div")),
    }
    return [row], stats


def parse_box_score_game_info(selector: Selector) -> list[dict[str, Any]]:
    rows, _ = parse_box_score_game_info_with_stats(selector)
    return rows
