"""One-off audit: unique team abbreviations in raw fixtures vs lookup dict."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from courtside_data.domain.lookups import TEAM_ABBREVIATIONS_TO_TEAM

RAW = Path("raw")
KNOWN = set(TEAM_ABBREVIATIONS_TO_TEAM.keys())
AGGREGATE = {"TOT", "2TM", "3TM", "4TM", "LG", "NBA"}

TEAM_STATS = (
    "team_id",
    "team_name_abbr",
    "team",
    "visitor_team_name",
    "home_team_name",
    "opp_name_abbr",
    "opp",
)


def extract_abbrs(html: str) -> dict[str, set[str]]:
    found: dict[str, set[str]] = defaultdict(set)
    for stat in TEAM_STATS:
        # Prefer anchor text inside team cells (e.g. draft ``team_id`` links).
        link_pattern = re.compile(
            rf'data-stat="{re.escape(stat)}"[^>]*>[^<]*<a[^>]*>([A-Z0-9]{{2,4}})</a>',
            re.I,
        )
        for match in link_pattern.finditer(html):
            found[stat].add(match.group(1).strip())

        pattern = re.compile(rf'data-stat="{re.escape(stat)}"[^>]*>([^<]*)</', re.I)
        for match in pattern.finditer(html):
            val = match.group(1).strip()
            if val and val not in AGGREGATE and len(val) <= 5 and val.isascii() and " " not in val:
                found[stat].add(val)
    return found


def main() -> None:
    by_file: dict[str, set[str]] = {}
    all_abbrs: set[str] = set()
    for path in sorted(RAW.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        stats = extract_abbrs(text)
        abbrs = set().union(*stats.values()) if stats else set()
        if abbrs:
            rel = str(path.relative_to(RAW))
            by_file[rel] = abbrs
            all_abbrs |= abbrs

    missing = sorted(all_abbrs - KNOWN - AGGREGATE)
    print(f"Total unique abbrs in fixtures: {len(all_abbrs)}")
    print(f"Missing from TEAM_ABBREVIATIONS_TO_TEAM: {missing}")
    print()
    for abbr in missing:
        files = sorted(rel for rel, abbrs in by_file.items() if abbr in abbrs)
        print(f"  {abbr}: {files[:8]}{'...' if len(files) > 8 else ''}")


if __name__ == "__main__":
    main()
