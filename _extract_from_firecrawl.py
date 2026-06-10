"""Extract all_standings div from firecrawl raw HTML output."""
import json
from lxml import html

with open(r'C:\Users\nicolas\.local\share\opencode\tool-output\tool_eb06c2d8a001ZphAnarVZUqbJZ', 'r', encoding='utf-8') as f:
    fc_output = f.read()

data = json.loads(fc_output)
print(f"Top-level keys: {list(data.keys())}")

raw_html_str = data.get('rawHtml', '')
print(f"rawHtml length: {len(raw_html_str)}")

tree = html.fromstring(raw_html_str)
standings = tree.xpath('.//div[@id="all_standings"]')
print(f"Standings divs found: {len(standings)}")

if standings:
    div_html = html.tostring(standings[0], encoding='unicode')
    print(f"Standings div: {len(div_html)} bytes")
    with open('_standings_2001.html', 'w', encoding='utf-8') as f:
        f.write(div_html)
    print("Saved to _standings_2001.html")
else:
    all_divs = tree.xpath('//div')
    for div in all_divs:
        div_id = div.get('id', '')
        if 'standings' in div_id.lower():
            print(f"Found div with id containing 'standings': {div_id}")
