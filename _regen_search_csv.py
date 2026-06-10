"""Regenerate search expected CSV through actual client path."""
import os
import requests_mock
from courtside_data import client
from courtside_data.data import OutputType, OutputWriteOption

fixture_path = 'tests/integration/files/search/kobe.html'
with open(fixture_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

expected_path = 'tests/integration/client/output/expected/search/kobe.csv'

with requests_mock.Mocker() as m:
    m.get('https://www.basketball-reference.com/search/search.fcgi?search=kobe',
          text=html_content, status_code=200)
    
    # Run through actual client path to get the exact same output
    result = client.search(
        term="kobe",
        output_type=OutputType.CSV,
        output_file_path=expected_path,
        output_write_option=OutputWriteOption.WRITE,
    )
    print(f"CSV regenerated to {expected_path}")
    print(f"Result type: {type(result)}")
