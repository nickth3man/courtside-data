"""Extract the all_standings div from a basketball-reference league page."""
import sys
from lxml import html

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

tree = html.fromstring(content)
standings = tree.xpath('.//div[@id="all_standings"]')
if len(standings) == 1:
    div_html = html.tostring(standings[0], encoding='unicode')
    print(f'Found all_standings div, length: {len(div_html)}')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(div_html)
    print(f'Saved to {output_file}')
else:
    print(f'Did not find all_standings div, found {len(standings)}')
    sys.exit(1)
