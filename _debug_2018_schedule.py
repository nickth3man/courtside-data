"""Debug 2018 season schedule data."""
import os
from lxml import html
from courtside_data.html import SchedulePage
from courtside_data.parsers import ScheduledGamesParser, TeamNameParser, ScheduledStartTimeParser
from courtside_data.data import TEAM_NAME_TO_TEAM

# The schedule mocker maps files in schedule/2018/ 
base = 'tests/integration/files/schedule/2018'

# Load the main page (2018.html) to get other months URLs
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
print(f"Main page rows: {len(main_rows)}, URLs: {len(urls)}")

for url in urls:
    # URL is like /leagues/NBA_2018_games-october.html
    # Extract month from URL
    month = url.split('-')[-1].replace('.html', '')
    month_file = os.path.join(base, f'{month}.html')
    
    if os.path.exists(month_file):
        with open(month_file, 'r', encoding='utf-8') as f:
            content = f.read()
        page = SchedulePage(html=html.fromstring(content))
        month_rows = page.rows
        month_games = parser.parse_games(month_rows)
        all_games.extend(month_games)
        print(f"  {month}: {len(month_rows)} rows")
    else:
        print(f"  {month}: FILE NOT FOUND: {month_file}")

print(f"\nTotal games: {len(all_games)}")
if len(all_games) > 1415:
    print(f"Game 1415: {all_games[1415]}")
