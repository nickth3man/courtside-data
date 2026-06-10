"""Debug the search test to see actual output."""
import os
import json
import requests_mock
from courtside_data import client

# Load the fixture HTML
fixture_path = 'tests/integration/files/search/kobe.html'
with open(fixture_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

with requests_mock.Mocker() as m:
    m.get('https://www.basketball-reference.com/search/search.fcgi?search=kobe',
          text=html_content, status_code=200)
    results = client.search(term="kobe")
    
    print("=== ACTUAL RESULTS ===")
    for i, player in enumerate(results['players']):
        print(f"  [{i}] name={player['name']!r}, identifier={player['identifier']!r}")
    
    print("\n=== EXPECTED (from test) ===")
    expected = [
        {"name": "Kobe Bryant", "identifier": "bryanko01"},
        {"name": "Ruben Patterson", "identifier": "patteru01"},
        {"name": "Dion Waiters", "identifier": "waitedi01"},
        {"name": "Austin Reaves", "identifier": "reaveau01"},
        {"name": "Kobe Bufkin", "identifier": "bufkiko01"},
        {"name": "Kobe Brown", "identifier": "brownko01"},
        {"name": "Oleksandr Kobets", "identifier": "kobetol01"},
    ]
    for i, p in enumerate(expected):
        print(f"  [{i}] name={p['name']!r}, identifier={p['identifier']!r}")
