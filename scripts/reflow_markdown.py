#!/usr/bin/env python3
"""
Simple Markdown reflow script that preserves code fences, list markers,
blockquotes and avoids wrapping inline URLs.
"""
import argparse
import re
import textwrap

URL_RE = re.compile(r"https?://\S+")


def should_skip_line(line):
    line_strip = line.strip()
    if line_strip.startswith("```)") or line_strip.startswith("~~~"):
        return True
    if line_strip.startswith("-") or line_strip.startswith("*") or line_strip.startswith("+"):
        return False
    if re.match(r"^\d+\. ", line_strip):
        return False
    if line_strip.startswith(">"):
        return False
    if URL_RE.search(line_strip):
        return True
    return False


def reflow_text(text, width=80):
    # Detect paragraphs separated by blank lines
    lines = text.splitlines()
    out_lines = []
    buffer = []

    def flush_buffer(indent=""):
        if not buffer:
            return
        paragraph = " ".join(line.strip() for line in buffer)
        # Keep it as is if contains URL
        if URL_RE.search(paragraph):
            for line in buffer:
                out_lines.append(indent + line.strip())
        else:
            wrapped = textwrap.wrap(paragraph, width=width - len(indent))
            for w in wrapped:
                out_lines.append(indent + w)
        buffer.clear()

    for ln in lines:
        if ln.strip() == "":
            flush_buffer("")
            out_lines.append("")
            continue
        # list items
        m = re.match(r"^(?P<indent>\s*)(?P<marker>[-*+]|\d+\.)\s+(?P<rest>.+)$", ln)
        if m:
            flush_buffer("")
            indent = m.group("indent") + "  "
            marker = m.group("marker")
            rest = m.group("rest")
            wrapped = textwrap.wrap(rest, width=width - len(indent))
            if wrapped:
                out_lines.append(f"{indent[:-2]}{marker} {wrapped[0]}")
                for w in wrapped[1:]:
                    out_lines.append(indent + w)
            else:
                out_lines.append(ln)
            continue
        # blockquote
        m2 = re.match(r"^(?P<indent>\s*>\s?)(?P<rest>.+)$", ln)
        if m2:
            flush_buffer("")
            indent = m2.group("indent")
            rest = m2.group("rest")
            wrapped = textwrap.wrap(rest, width=width - len(indent))
            if wrapped:
                out_lines.append(indent + wrapped[0])
                for w in wrapped[1:]:
                    out_lines.append(indent + w)
            else:
                out_lines.append(ln)
            continue
        # code fence detection not handled here; upper level handles code fences
        # normal paragraph
        buffer.append(ln)
    flush_buffer("")
    return "\n".join(out_lines)


def reflow_file(path, width=80):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    new_lines = []
    in_code_block = False
    code_block_re = re.compile(r"^\s*(```|~~~)\S*")
    paragraph_block = []

    def flush_paragraph():
        nonlocal paragraph_block
        if paragraph_block:
            text = "\n".join(paragraph_block)
            new_lines.append(reflow_text(text, width))
            paragraph_block = []

    lines = content.splitlines()
    for ln in lines:
        if code_block_re.match(ln):
            # entering or leaving code block
            flush_paragraph()
            new_lines.append(ln)
            in_code_block = not in_code_block
            continue
        if in_code_block:
            new_lines.append(ln)
            continue
        if ln.strip() == "":
            flush_paragraph()
            new_lines.append(ln)
            continue
        # If line is starting a list or blockquote, include in paragraph buffer and reflow later
        paragraph_block.append(ln)
    flush_paragraph()
    new_content = "\n".join(new_lines) + "\n"
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Reflowed: {path}")
    else:
        print(f"Unchanged: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Files or directories to reflow")
    parser.add_argument("--width", type=int, default=80)
    args = parser.parse_args()
    import os

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            for root, _dirs, filenames in os.walk(p):
                for fn in filenames:
                    if fn.lower().endswith(".md"):
                        files.append(os.path.join(root, fn))
        else:
            files.append(p)
    for f in files:
        reflow_file(f, width=args.width)
