"""Compare generated vs expected CSV."""
import hashlib

with open('tests/integration/client/output/generated/search/kobe.csv', 'rb') as f:
    gen = f.read()
with open('tests/integration/client/output/expected/search/kobe.csv', 'rb') as f:
    exp = f.read()

print(f'Generated: {len(gen)} bytes')
print(f'Expected: {len(exp)} bytes')
print(f'Generated has CRLF: {b"\\r\\n" in gen}')
print(f'Expected has CRLF: {b"\\r\\n" in exp}')
print(f'Generated CRLF count: {gen.count(b"\\r\\n")}')
print(f'Expected CRLF count: {exp.count(b"\\r\\n")}')

gen_hash = hashlib.md5(gen).hexdigest()
exp_hash = hashlib.md5(exp).hexdigest()
print(f'Generated MD5: {gen_hash}')
print(f'Expected MD5: {exp_hash}')

# Find first difference
for i, (bg, be) in enumerate(zip(gen, exp)):
    if bg != be:
        print(f'First diff at byte {i}: gen={bg} exp={be}')
        context_start = max(0, i - 10)
        print(f'Context gen: {gen[context_start:i+10]}')
        print(f'Context exp: {exp[context_start:i+10]}')
        break
else:
    if len(gen) != len(exp):
        print(f'Lengths differ: {len(gen)} vs {len(exp)}')
        # Show the extra bytes
        if len(gen) > len(exp):
            print(f'Extra bytes in gen: {gen[len(exp):]}')
        else:
            print(f'Extra bytes in exp: {exp[len(gen):]}')
    else:
        print('Files are identical!')
