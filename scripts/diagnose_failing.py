"""Diagnose table IDs for the 17 failing endpoints."""
import requests
from parsel import Selector
import re
import time

def diagnose(url, expected_id, page_name):
    print(f"\n{'='*50}")
    print(f"{page_name}: {url}")
    print(f"Expected table ID: {expected_id}")
    
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=30)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")
        return
    
    if response.status_code != 200:
        print(f"Non-200 status, skipping content analysis")
        return
    
    selector = Selector(text=response.text)
    
    # Direct tables
    direct = [t.attrib.get('id') for t in selector.css('table[id]')]
    print(f"Direct table IDs ({len(direct)}): {direct[:30]}{'...' if len(direct) > 30 else ''}")
    
    # Commented tables
    commented = []
    for comment in selector.xpath('//comment()').getall():
        if '<table' in comment.lower():
            ids = re.findall(r'id="([^"]*)"', comment)
            commented.extend(ids)
    print(f"Commented table IDs ({len(commented)}): {commented[:30]}{'...' if len(commented) > 30 else ''}")
    
    # Check if expected ID exists
    if expected_id in direct:
        print(f"[FOUND] '{expected_id}' found as DIRECT table")
    elif expected_id in commented:
        print(f"[FOUND] '{expected_id}' found in COMMENTS")
    else:
        print(f"[NOT FOUND] '{expected_id}' NOT FOUND - need different ID")
    
    # Suggest closest matches
    all_ids = direct + commented
    if expected_id and '_' in expected_id:
        prefix = expected_id.split('_')[0]
        matches = [i for i in all_ids if prefix in i]
        if matches:
            print(f"  Partial matches for prefix '{prefix}': {matches[:15]}")
    # Also try full expected_id
    if expected_id not in direct and expected_id not in commented:
        close = [i for i in all_ids if expected_id in i or i in expected_id]
        if close:
            print(f"  Close matches: {close[:15]}")

# Test pages for failing endpoints
tests = [
    # League admin
    ("https://www.basketball-reference.com/leagues/NBA_2024_standings_by_date.html", "standings", "standings_by_date"),
    ("https://www.basketball-reference.com/leagues/NBA_2024_attendance.html", "attendance", "attendance"),
    ("https://www.basketball-reference.com/leagues/NBA_2024_transactions.html", "transactions", "league_transactions"),
    
    # Leaders/Awards
    ("https://www.basketball-reference.com/leaders/per_season.html", "leaders", "season_leaders"),
    ("https://www.basketball-reference.com/leaders/", "leaders", "career_leaders"),
    ("https://www.basketball-reference.com/playoffs/NBA_2024.html", "bracket", "playoff_bracket"),
    ("https://www.basketball-reference.com/awards/awards_2024.html", "awards", "season_awards"),
    
    # Player pages
    ("https://www.basketball-reference.com/players/j/jamesle01.html", "per_game", "player_career_stats"),
    ("https://www.basketball-reference.com/players/j/jamesle01.html", "playoffs_per_game", "player_playoff_series"),
    ("https://www.basketball-reference.com/players/j/jamesle01/shooting/2024.html", "shot_charts", "player_shot_charts"),
    
    # Team pages
    ("https://www.basketball-reference.com/teams/LAL/2024.html", "injuries", "team_injury_report"),
    ("https://www.basketball-reference.com/teams/LAL/2024_transactions.html", "transactions", "team_transactions"),
    ("https://www.basketball-reference.com/teams/LAL/2024/splits/", "team_splits", "team_splits"),
    ("https://www.basketball-reference.com/teams/LAL/2024/lineups/", "lineups", "team_lineups"),
    ("https://www.basketball-reference.com/teams/LAL/2024_start.html", "starting_lineups", "team_starting_lineups"),
    ("https://www.basketball-reference.com/teams/LAL/2024/on-off/", "on-off", "team_on_off"),
    ("https://www.basketball-reference.com/teams/LAL/2024.html", "opp_stats", "team_opponent_stats"),
]

for url, expected_id, name in tests:
    try:
        diagnose(url, expected_id, name)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)
