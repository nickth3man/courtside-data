"""Extract div#all_standings from a raw HTML file and inject into a fixture."""
import os
import re
import sys

# Check the firecrawl output file for raw HTML
firecrawl_file = r'C:\Users\nicolas\.local\share\opencode\tool-output\tool_eb06c2d8a001ZphAnarVZUqbJZ'

with open(firecrawl_file, 'r', encoding='utf-8') as f:
    content = f.read()

# The rawHtml in firecrawl response is in the JSON data field
# Let me find it with regex
match = re.search(r'"rawHtml"\s*:\s*"([^"]+)"', content)
if match:
    # Unescape JSON string
    import json
    raw_html = json.loads('"' + match.group(1) + '"')
    print(f'Found rawHtml, length: {len(raw_html)}')
    
    # Extract div#all_standings
    from lxml import html
    tree = html.fromstring(raw_html)
    standings = tree.xpath('.//div[@id="all_standings"]')
    if len(standings) == 1:
        div_html = html.tostring(standings[0], encoding='unicode')
        print(f'Found all_standings div, length: {len(div_html)} bytes')
        
        # Save the standings div
        with open('_standings_2001.html', 'w', encoding='utf-8') as f:
            f.write(div_html)
        print('Saved to _standings_2001.html')
    else:
        print(f'Did not find all_standings div, found {len(standings)}')
else:
    print('No rawHtml found in firecrawl output')
    # Let me look at the file structure
    print(f'File starts with: {content[:200]}')
