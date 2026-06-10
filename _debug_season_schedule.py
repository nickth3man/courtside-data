"""Debug season schedule test."""
from lxml import html
from courtside_data.html import SchedulePage

# Check 2018.html fixture
paths = [
    'tests/integration/files/schedule/2018/2018.html',
    'tests/integration/files/schedule/2001/2001.html',
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    page = SchedulePage(html=html.fromstring(content))
    urls = page.other_months_schedule_urls
    rows = page.rows
    has_standings = 'all_standings' in content
    
    print(f'{p}:')
    print(f'  Rows: {len(rows)}, Other months URLs: {len(urls)}, Has standings: {has_standings}')
    if rows:
        print(f'  First: {rows[0]}')
        print(f'  Last: {rows[-1]}')
