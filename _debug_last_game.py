"""Debug last game of 2018 season schedule."""
import os
from lxml import html
from courtside_data.html import SchedulePage
from courtside_data.parsers import ScheduledGamesParser, TeamNameParser, ScheduledStartTimeParser
from courtside_data.data import TEAM_NAME_TO_TEAM

base = 'tests/integration/files/schedule/2018'

with open(os.path.join(base, '2018.html'), 'r', encoding='utf-8') as f:
    main_content = f.read()

main_page = SchedulePage(html=html.fromstring(main_content))
urls = main_page.other_months_schedule_urls
main_rows = main_page.rows

parser = ScheduledGamesParser(
    start_time_parser=ScheduledStartTimeParser(),
    team_name_parser=TeamNameParser(team_names_to_teams=TEAM_NAME_TO_TEAM),
)

all_games = list(parser.parse_games(main_rows))

for url in urls:
    month = url.split('-')[-1].replace('.html', '')
    month_file = os.path.join(base, f'{month}.html')
    if os.path.exists(month_file):
        with open(month_file, 'r', encoding='utf-8') as f:
            content = f.read()
        page = SchedulePage(html=html.fromstring(content))
        month_rows = page.rows
        month_games = parser.parse_games(month_rows)
        all_games.extend(month_games)

print(f"Total games: {len(all_games)}")
print(f"First game: {all_games[0]}")
print(f"Last game (index -1): {all_games[-1]}")
print(f"Last game (index {len(all_games)-1}): {all_games[len(all_games)-1]}")

# The test expects index 1415. If total is less, find what's at the last few positions
for i in range(max(0, len(all_games)-10), len(all_games)):
    print(f"  [{i}]: {all_games[i]}")
