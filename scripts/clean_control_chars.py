#!/usr/bin/env python3
from pathlib import Path

p = Path("mkdocs_clean.yml")
text = p.read_text(encoding="utf-8")
problems = []
for i, ch in enumerate(text):
    o = ord(ch)
    if (o < 32 and ch not in "\t\n\r") or (0x80 <= o <= 0x9F):
        problems.append((i, o, ch))
if not problems:
    print("No control characters found")
else:
    print(f"Found {len(problems)} control chars; making backup to mkdocs_clean.yml.bak")
    p.with_suffix(".yml.bak").write_bytes(p.read_bytes())
    cleaned = "".join(
        ch
        for ch in text
        if not ((ord(ch) < 32 and ch not in "\t\n\r") or (0x80 <= ord(ch) <= 0x9F))
    )
    p.write_text(cleaned, encoding="utf-8")
    print("Cleaned file written")
    # show summary of removed codepoints
    for i, o, ch in problems[:10]:
        print(f"removed index={i} 0x{o:02x} {repr(ch)}")
    if len(problems) > 10:
        print("...")
