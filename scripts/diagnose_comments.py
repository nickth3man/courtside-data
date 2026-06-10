"""Diagnostic script to check what's inside HTML comments on basketball-reference pages.

Scans both live pages (with proper browser headers) and local fixture files.
"""

import re
import time
from pathlib import Path

import requests
from parsel import Selector

SEASON = 2024
PLAYER_ID = "jamesle01"
TEAM = "LAL"

# Better browser headers to avoid 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

# All table IDs used in http_service.py via extract_commented_table
EXPECTED_TABLE_IDS = [
    "per_poss_stats",  # league_per_100_possessions
    "shooting_stats",  # league_shooting
    "playoffs_per_game",  # playoff_per_game
    "playoffs_totals",  # playoff_totals
    "adj_shooting",  # player_adj_shooting
    "pbp",  # player_pbp
    "highs_totals",  # player_highs_totals
    "all_star_g_stats",  # player_all_star_game_stats
    "sim_career",  # player_similar_career
    "salaries",  # player_salaries
    "team_and_opponent",  # team_and_opponent
    "team_misc",  # team_misc
    "opp_stats",  # opponent_stats
]


def diagnose_html(html_text, source_name):
    """Analyze HTML text for comments containing tables."""
    print(f"\n{'=' * 60}")
    print(f"Source: {source_name}")
    print("=" * 60)

    selector = Selector(text=html_text)

    # Find all direct table IDs
    direct_tables = selector.css("table[id]")
    print(f"\nDirect tables ({len(direct_tables)}):")
    for t in direct_tables:
        print(f"  - {t.attrib.get('id')}")

    # Find all comments
    comments = selector.xpath("//comment()").getall()
    print(f"\nHTML comments: {len(comments)}")

    # Check each comment for tables
    commented_tables = []
    for i, comment in enumerate(comments):
        if "<table" in comment.lower():
            # Find table IDs in this comment
            ids = re.findall(r'id="([^"]*)"', comment)
            if not ids:
                ids = re.findall(r"id='([^']*)'", comment)
            if ids:
                commented_tables.extend(ids)
                print(f"\nComment #{i} contains tables with IDs: {ids}")
                # Show first 200 chars of the comment
                preview = comment[:200].replace("\n", " ")
                print(f"  Preview: {preview}...")
            else:
                print(f"\nComment #{i} has <table> but no id found")
                preview = comment[:200].replace("\n", " ")
                print(f"  Preview: {preview}...")

    if not commented_tables:
        print("\nNo table IDs found in comments!")
    else:
        print(f"\nAll commented table IDs: {commented_tables}")

    # Check which expected IDs were found
    found_expected = [tid for tid in EXPECTED_TABLE_IDS if tid in commented_tables]
    missing_expected = [
        tid
        for tid in EXPECTED_TABLE_IDS
        if tid not in commented_tables and tid not in [t.attrib.get("id") for t in direct_tables]
    ]

    if found_expected:
        print(f"\nExpected IDs found in comments: {found_expected}")
    if missing_expected:
        print(f"\nExpected IDs NOT found anywhere: {missing_expected}")

    return commented_tables, [t.attrib.get("id") for t in direct_tables]


def diagnose_url(url, page_name):
    """Fetch a live page and diagnose it."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Skipping - got {response.status_code}")
            return None, None
        return diagnose_html(response.text, page_name)
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def diagnose_local_file(file_path, file_name):
    """Diagnose a local HTML fixture file."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            html_text = f.read()
        return diagnose_html(html_text, f"{file_name} ({file_path})")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None, None


# Live pages to test
live_pages = [
    (f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_per_poss.html", "league_per_100_possessions"),
    (f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_shooting.html", "league_shooting"),
    (f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_per_game.html", "league_per_game"),
    (f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_totals.html", "league_totals"),
    (f"https://www.basketball-reference.com/players/{PLAYER_ID[0]}/{PLAYER_ID}.html", "player_page"),
    (f"https://www.basketball-reference.com/teams/{TEAM}/{SEASON}.html", "team_page"),
    (f"https://www.basketball-reference.com/draft/NBA_{SEASON}.html", "draft"),
    ("https://www.basketball-reference.com/leaders/", "career_leaders"),
    ("https://www.basketball-reference.com/leaders/per_season.html", "season_leaders"),
    (f"https://www.basketball-reference.com/contracts/{TEAM}.html", "contracts"),
]

# Phase 1: Analyze local fixture files
print("\n" + "#" * 60)
print("# PHASE 1: Analyzing local fixture HTML files")
print("#" * 60)

fixture_dir = Path(__file__).parent.parent / "tests" / "integration" / "files"
local_results = {}

if fixture_dir.exists():
    html_files = list(fixture_dir.rglob("*.html"))
    print(f"\nFound {len(html_files)} HTML fixture files")

    # Scan each file for comments with tables
    for fpath in sorted(html_files):
        rel = fpath.relative_to(fixture_dir)
        with open(fpath, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        selector = Selector(text=content)
        comments = selector.xpath("//comment()").getall()
        has_commented_tables = False

        for comment in comments:
            if "<table" in comment.lower():
                ids = re.findall(r'id="([^"]*)"', comment)
                if not ids:
                    ids = re.findall(r"id='([^']*)'", comment)
                if ids:
                    has_commented_tables = True
                    direct_tables = selector.css("table[id]")
                    direct_ids = [t.attrib.get("id") for t in direct_tables]
                    print(f"\n  {rel}:")
                    print(f"    Commented table IDs: {ids}")
                    print(f"    Direct table IDs:    {direct_ids[:10]}{'...' if len(direct_ids) > 10 else ''}")
                    local_results[str(rel)] = {"commented": ids, "direct": direct_ids}
                    break  # Only report once per file

        if not has_commented_tables:
            # Still check direct tables
            direct_tables = selector.css("table[id]")
            if direct_tables:
                direct_ids = [t.attrib.get("id") for t in direct_tables]
                local_results[str(rel)] = {"commented": [], "direct": direct_ids}
else:
    print(f"Fixture directory not found: {fixture_dir}")

# Phase 2: Try live pages
print("\n\n" + "#" * 60)
print("# PHASE 2: Testing live basketball-reference pages")
print("#" * 60)

live_results = {}
for url, name in live_pages:
    try:
        commented, direct = diagnose_url(url, name)
        live_results[name] = {"commented": commented or [], "direct": direct or []}
    except Exception as e:
        print(f"Error: {e}")
        live_results[name] = {"commented": [], "direct": [], "error": str(e)}
    time.sleep(4)  # Rate limiting

# Summary
print("\n\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

print("\n--- Expected table IDs used in http_service.py ---")
for tid in EXPECTED_TABLE_IDS:
    print(f"  {tid}")

print("\n--- Local fixture files with commented tables ---")
found_in_fixtures = set()
for fname, data in local_results.items():
    if data["commented"]:
        print(f"  {fname}: {data['commented']}")
        found_in_fixtures.update(data["commented"])

not_in_fixtures = [tid for tid in EXPECTED_TABLE_IDS if tid not in found_in_fixtures]
if not_in_fixtures:
    print(f"\n  Expected IDs NOT found in any fixture: {not_in_fixtures}")

print("\n--- Live page results ---")
for name, data in live_results.items():
    if "error" in data:
        print(f"  {name}: ERROR - {data['error']}")
    elif data["commented"]:
        print(f"  {name}: commented={data['commented']}, direct={data['direct']}")
    else:
        print(f"  {name}: NO COMMENTED TABLES, direct={data['direct']}")
