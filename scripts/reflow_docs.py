#!/usr/bin/env python3
"""Reflow markdown files under docs/ and .github/PR_BODIES to 80 cols.
Preserves code fences and does simple handling for lists and blockquotes.
"""
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "docs", ROOT / ".github" / "PR_BODIES"]
WIDTH = 80

def reflow_text(text: str, width: int, initial_indent: str = "", subsequent_indent: str = "") -> str:
    return textwrap.fill(text, width=width, initial_indent=initial_indent, subsequent_indent=subsequent_indent)


def process_file(path: Path) -> bool:
    content = path.read_text(encoding='utf-8')
    lines = content.splitlines()
    out_lines = []
    i = 0
    changed = False
    in_code = False

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            # code fence; copy until closing fence
            in_code = not in_code
            fence = line.strip()
            out_lines.append(line)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                out_lines.append(lines[i])
                i += 1
            if i < len(lines):
                out_lines.append(lines[i])
                i += 1
            continue

        if in_code:
            out_lines.append(line)
            i += 1
            continue

        # Handle blank lines
        if not line.strip():
            out_lines.append(line)
            i += 1
            continue

        # Collect a block until next blank line or code fence
        block_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('```'):
            block_lines.append(lines[i])
            i += 1

        # If it's a list (starts with - or * or numbered), handle items separately
        trimmed = [ln.lstrip() for ln in block_lines]
        first = trimmed[0]
        if first.startswith(('-', '*')) or (first and first[0].isdigit() and '.' in first[:3]):
            # process each list item independently
            j = 0
            while j < len(block_lines):
                item = block_lines[j]
                stripped = item.lstrip()
                indent_len = len(item) - len(stripped)
                indent = ' ' * indent_len
                if stripped.startswith(('- ', '* ')):
                    marker, rest = stripped.split(' ', 1)
                    text = rest.strip()
                    wrapped = reflow_text(text, width=WIDTH - indent_len - 2, initial_indent='', subsequent_indent='')
                    for k, wrapped_line in enumerate(wrapped.splitlines()):
                        prefix = indent + marker + ' ' if k == 0 else indent + '  '
                        out_lines.append(prefix + wrapped_line)
                    j += 1
                elif stripped and stripped[0].isdigit() and '.' in stripped[:3]:
                    # numbered list like '1. '
                    parts = stripped.split(' ', 1)
                    marker = parts[0]
                    rest = parts[1] if len(parts) > 1 else ''
                    text = rest.strip()
                    wrapped = reflow_text(text, width=WIDTH - indent_len - len(marker) - 1)
                    for k, wrapped_line in enumerate(wrapped.splitlines()):
                        prefix = indent + marker + ' ' if k == 0 else indent + ' ' * (len(marker) + 1)
                        out_lines.append(prefix + wrapped_line)
                    j += 1
                else:
                    # fallback: reflow the whole line
                    w = reflow_text(stripped, width=WIDTH - indent_len)
                    for wline in w.splitlines():
                        out_lines.append(indent + wline)
                    j += 1
        else:
            # It's a paragraph or heading or blockquote
            if block_lines[0].lstrip().startswith('>'):
                # handle blockquote lines preserving '>'
                joined = ' '.join(ln.strip()[1:].strip() for ln in block_lines)
                wrapped = reflow_text(joined, width=WIDTH - 2)
                for wrapped_line in wrapped.splitlines():
                    out_lines.append('> ' + wrapped_line)
            elif block_lines[0].startswith('#'):
                # heading: preserve as-is
                out_lines.extend(block_lines)
            else:
                # normal paragraph
                joined = ' '.join(ln.strip() for ln in block_lines)
                wrapped = reflow_text(joined, width=WIDTH)
                out_lines.extend(wrapped.splitlines())

        # continue main loop
    new_content = '\n'.join(out_lines) + '\n'
    if new_content != content:
        path.write_text(new_content, encoding='utf-8')
        changed = True
    return changed


def main():
    changed_files = []
    for t in TARGETS:
        if not t.exists():
            continue
        for p in sorted(t.rglob('*.md')):
            try:
                if process_file(p):
                    changed_files.append(str(p.relative_to(ROOT)))
            except Exception as e:
                print(f"Failed to process {p}: {e}")
    if changed_files:
        print("Reflowed files:")
        for f in changed_files:
            print(f" - {f}")
    else:
        print("No changes required")

if __name__ == '__main__':
    main()
