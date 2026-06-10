"""Download league page for each standings test year, extract div#all_standings,
and inject it into the existing schedule fixture."""
import os
import sys
import requests
from lxml import html

YEARS = [2001, 2002, 2005, 2019, 2020]
FIXTURE_DIR = 'tests/integration/files/schedule'

def download_league_page(year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}.html'
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp.raise_for_status()
    return resp.text

def extract_standings_div(content):
    tree = html.fromstring(content)
    standings = tree.xpath('.//div[@id="all_standings"]')
    if len(standings) == 1:
        return html.tostring(standings[0], encoding='unicode')
    return None

def inject_standings_into_fixture(fixture_path, standings_html):
    with open(fixture_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the closing </body> tag and insert standings before it
    if '</body>' in content:
        # But first, check if all_standings already exists
        if 'all_standings' in content:
            print(f'  all_standings already in {fixture_path}')
            return True
        
        content = content.replace('</body>', standings_html + '\n</body>')
        with open(fixture_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  Injected standings into {fixture_path}')
        return True
    else:
        print(f'  No </body> found in {fixture_path}')
        return False

for year in YEARS:
    fixture_file = os.path.join(FIXTURE_DIR, str(year), f'{year}.html')
    if not os.path.exists(fixture_file):
        print(f'Fixture {fixture_file} not found, skipping')
        continue
    
    print(f'Processing year {year}...')
    
    # Download league page
    print(f'  Downloading NBA_{year}.html...')
    try:
        league_content = download_league_page(year)
    except Exception as e:
        print(f'  Failed to download: {e}')
        continue
    
    # Extract standings div
    standings_html = extract_standings_div(league_content)
    if not standings_html:
        print(f'  No div#all_standings found in NBA_{year}.html')
        continue
    print(f'  Extracted standings div ({len(standings_html)} bytes)')
    
    # Inject into fixture
    success = inject_standings_into_fixture(fixture_file, standings_html)
    if success:
        print(f'  Year {year}: SUCCESS')
    else:
        print(f'  Year {year}: FAILED')
