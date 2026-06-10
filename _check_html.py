"""Check if the league page has schedule table."""
import sys
from lxml import html

for year in [2000, 2001]:
    fname = f'tests/integration/files/schedule/{year}/{year}.html'
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = html.fromstring(content)
    
    schedule_table = tree.xpath('//table[@id="schedule"]')
    standings_div = tree.xpath('.//div[@id="all_standings"]')
    filter_divs = tree.xpath('//div[@id="content"]/div[@class="filter"]')
    
    print(f'{year}: schedule_table={len(schedule_table)}, standings_div={len(standings_div)}, filter_divs={len(filter_divs)}')
    
    if filter_divs:
        filter_links = tree.xpath('//div[@id="content"]/div[@class="filter"]/div[not(contains(@class, "current"))]/a')
        print(f'  Filter links: {len(filter_links)}')
        for link in filter_links[:3]:
            print(f'    {link.attrib.get("href", "N/A")}')
