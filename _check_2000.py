from lxml import html
with open('tests/integration/files/schedule/2000/2000.html', 'r', encoding='utf-8') as f:
    content = f.read()
tree = html.fromstring(content)

# Check for standings
standings = tree.xpath('.//div[@id="all_standings"]')
print(f'Standings divs found: {len(standings)}')
if standings:
    east = standings[0].xpath('.//table[@id="divs_standings_E"]')
    west = standings[0].xpath('.//table[@id="divs_standings_W"]')
    print(f'Eastern table: {len(east)}, Western table: {len(west)}')
    if east:
        rows = east[0].xpath('.//tbody/tr')
        print(f'Eastern conference rows: {len(rows)}')
        for r in rows[:3]:
            print(f'  class={r.attrib.get("class")}, team={r.xpath(".//th[@data-stat=\"team_name\"]")}')
else:
    # Try to find what's happening
    all_ids = tree.xpath('//div/@id')
    standings_ids = [i for i in all_ids if i and 'standing' in i.lower()]
    print(f'Divs with standing in id: {standings_ids}')
    
    # Check if the parsing issue is related to HTML structure
    divs = tree.xpath('//div')
    print(f'Total divs: {len(divs)}')
    for d in divs[:5]:
        print(f'  id={d.get("id")}, class={d.get("class")}')
