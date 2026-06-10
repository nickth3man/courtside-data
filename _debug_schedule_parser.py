"""Debug schedule parser test."""
import os
from lxml import html
from courtside_data.html import SchedulePage

# Test loading 2001/2001.html
path = 'tests/integration/files/schedule/2001/2001.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

page = SchedulePage(html=html.fromstring(content))
urls = page.other_months_schedule_urls
rows = page.rows

print(f'URLs found: {len(urls)}')
for u in urls:
    print(f'  {u}')

print(f'\nRows found: {len(rows)}')

# Test upcoming-games.html
upcoming_path = 'tests/integration/files/schedule/upcoming-games.html'
with open(upcoming_path, 'r', encoding='utf-8') as f:
    upcoming_content = f.read()

upcoming_page = SchedulePage(html=html.fromstring(upcoming_content))
upcoming_rows = upcoming_page.rows
upcoming_urls = upcoming_page.other_months_schedule_urls

print(f'\nUpcoming games rows: {len(upcoming_rows)}')
print(f'Upcoming URLs: {upcoming_urls}')
