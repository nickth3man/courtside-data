"""Debug search CSV comparison."""
import hashlib
import requests_mock
from courtside_data import client
from courtside_data.data import OutputType

with open('tests/integration/files/search/kobe.html', 'r', encoding='utf-8') as f:
    html = f.read()

with requests_mock.Mocker() as m:
    m.get('https://www.basketball-reference.com/search/search.fcgi?search=kobe',
          text=html, status_code=200)
    client.search(
        term='kobe',
        output_type=OutputType.CSV,
        output_file_path='tests/integration/client/output/generated/search/kobe.csv',
        output_write_option=None,
    )

with open('tests/integration/client/output/generated/search/kobe.csv', 'rb') as f:
    gen = f.read()
with open('tests/integration/client/output/expected/search/kobe.csv', 'rb') as f:
    exp = f.read()

print(f'Generated: {len(gen)} bytes, MD5: {hashlib.md5(gen).hexdigest()}')
print(f'Expected: {len(exp)} bytes, MD5: {hashlib.md5(exp).hexdigest()}')
print(f'Generated CRLF count: {gen.count(b"\\r\\n")}')
print(f'Expected CRLF count: {exp.count(b"\\r\\n")}')

# Compare byte by byte
for i, (bg, be) in enumerate(zip(gen, exp)):
    if bg != be:
        print(f'First diff at byte {i}: gen={bg} exp={be}')
        print(f'Context gen: {gen[max(0,i-5):i+15]}')
        print(f'Context exp: {exp[max(0,i-5):i+15]}')
        break
else:
    if len(gen) != len(exp):
        print(f'Lengths differ: {len(gen)} vs {len(exp)}')
    else:
        print('IDENTICAL')

# Remove temp file
import os
os.remove('tests/integration/client/output/generated/search/kobe.csv')
