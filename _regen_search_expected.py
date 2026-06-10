"""Regenerate ALL search expected output files through actual client path."""
import os
import requests_mock
from courtside_data import client
from courtside_data.data import OutputType, OutputWriteOption

fixture_path = 'tests/integration/files/search/kobe.html'
with open(fixture_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

base_dir = 'tests/integration/client/output/expected/search'

with requests_mock.Mocker() as m:
    m.get('https://www.basketball-reference.com/search/search.fcgi?search=kobe',
          text=html_content, status_code=200)
    
    # Regenerate CSV expected
    csv_path = os.path.join(base_dir, 'kobe.csv')
    client.search(
        term="kobe",
        output_type=OutputType.CSV,
        output_file_path=csv_path,
        output_write_option=OutputWriteOption.WRITE,
    )
    print(f"CSV regenerated: {csv_path}")
    
    # Regenerate JSON expected
    json_path = os.path.join(base_dir, 'kobe.json')
    client.search(
        term="kobe",
        output_type=OutputType.JSON,
        output_file_path=json_path,
        output_write_option=OutputWriteOption.WRITE,
    )
    print(f"JSON regenerated: {json_path}")
