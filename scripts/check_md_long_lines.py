from pathlib import Path

p = Path('CHANGELOG.md')
longs = []
for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), start=1):
    if len(line) > 80:
        longs.append((i, len(line), line))
if not longs:
    print('No long lines found')
else:
    for i, length, text in longs:
        print(f'{i}: {length} chars')
        print('  ', text[:200])
