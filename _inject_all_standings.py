"""Extract standings from firecrawl outputs and inject into all fixture files."""
import json
import os
from lxml import html

# Map: firecrawl output file → year → fixture fixture
FILES = {
    r'C:\Users\nicolas\.local\share\opencode\tool-output\tool_eb06e221a001Y452sF0DCU9C1I': 2002,
    r'C:\Users\nicolas\.local\share\opencode\tool-output\tool_eb06e26ee001d6Dxldvl1pCjvN': 2005,
    r'C:\Users\nicolas\.local\share\opencode\tool-output\tool_eb06e223b001XbvZpH6SCQ7UvD': 2019,
    r'C:\Users\nicolas\.local\share\opencode\tool-output\tool_eb06e273c001lN2eifoLQKMs0i': 2020,
}

for fc_file, year in FILES.items():
    print(f"\nProcessing year {year}...")

    # Read firecrawl output
    with open(fc_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    raw_html_str = data.get('rawHtml', '')
    print(f"  rawHtml length: {len(raw_html_str)}")

    # Extract standings div
    tree = html.fromstring(raw_html_str)
    standings = tree.xpath('.//div[@id="all_standings"]')

    if not standings:
        print(f"  No div#all_standings found!")
        continue

    div_html = html.tostring(standings[0], encoding='unicode')
    print(f"  Standings div: {len(div_html)} bytes")

    # Inject into fixture
    fixture_path = f'tests/integration/files/schedule/{year}/{year}.html'
    if not os.path.exists(fixture_path):
        print(f"  Fixture not found: {fixture_path}")
        continue

    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixture = f.read()

    if 'all_standings' in fixture:
        print(f"  Filings already have all_standings - skip")
        continue

    if '</body>' in fixture:
        fixture = fixture.replace('</body>', div_html + '\n</body>')
        with open(fixture_path, 'w', encoding='utf-8') as f:
            f.write(fixture)
        print(f"  Injected into {fixture_path}")
    else:
        print(f"  No </body> in fixture")
