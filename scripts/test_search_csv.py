"""
Verify leagues ARE included when data has them.
Tests a search that redirects to a player page vs search results page.
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from courtside_data.client import search, player_career_stats, players_season_totals, standings
from courtside_data.data import OutputType, OutputWriteOption

def test_csv(name, func, *args):
    tmp = os.path.join(tempfile.gettempdir(), f"test_{name}.csv")
    result = func(*args, output_type=OutputType.CSV, output_file_path=tmp, output_write_option=OutputWriteOption.WRITE)
    with open(tmp) as f:
        content = f.read()
        print(f"\n=== {name} ===")
        print(content)
    os.remove(tmp)

# Search (should NOT have empty leagues column)
test_csv("search", search, "LeBron James")

# Player career stats (should have many populated columns)
test_csv("player_career_stats", player_career_stats, "jamesle01")

# Standings (should have populated columns)
test_csv("standings", standings, 2024)
