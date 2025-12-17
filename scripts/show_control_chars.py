#!/usr/bin/env python3
from pathlib import Path
p=Path('mkdocs_clean.yml')
s=p.read_text(encoding='utf-8')
problems=[]
for i,ch in enumerate(s):
    o=ord(ch)
    if (o<32 and ch not in '\t\n\r') or (0x80<=o<=0x9F):
        problems.append((i,o,ch))
print(f'Found {len(problems)} control chars in {p}')
for i,o,ch in problems:
    ctx=s[max(0,i-20):min(len(s),i+20)]
    print(f'index={i} 0x{o:02x} {repr(ch)}')
    print('context:',repr(ctx))
    print('---')
