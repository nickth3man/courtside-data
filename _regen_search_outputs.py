"""Regenerate expected output files for search tests."""
import os
import json
import csv
import io
import requests_mock

from courtside_data import client
from courtside_data.data import OutputType
from courtside_data.output.fields import format_value, BasketballReferenceJSONEncoder
from courtside_data.output.writers import CSVWriter, JSONWriter, FileOptions, OutputOptions

fixture_path = 'tests/integration/files/search/kobe.html'
with open(fixture_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

base_dir = 'tests/integration/client/output/expected/search'

with requests_mock.Mocker() as m:
    m.get('https://www.basketball-reference.com/search/search.fcgi?search=kobe',
          text=html_content, status_code=200)
    
    # Get the data
    results = client.search(term="kobe")
    
    print(f"Results type: {type(results)}")
    print(f"Players count: {len(results['players'])}")
    
    # Generate CSV
    csv_path = os.path.join(base_dir, 'kobe.csv')
    csv_options = OutputOptions.of(
        file_options=FileOptions.of(path=csv_path),
        output_type=OutputType.CSV,
        csv_options={"column_names": None}
    )
    csv_writer = CSVWriter(value_formatter=format_value)
    csv_writer.write(data=results, options=csv_options)
    print(f"Generated CSV: {csv_path}")
    
    # Generate JSON
    json_path = os.path.join(base_dir, 'kobe.json')
    json_options = OutputOptions.of(
        file_options=FileOptions.of(path=json_path),
        output_type=OutputType.JSON,
        json_options={"sort_keys": True, "indent": 4}
    )
    json_writer = JSONWriter(value_formatter=BasketballReferenceJSONEncoder)
    json_writer.write(data=results, options=json_options)
    print(f"Generated JSON: {json_path}")
