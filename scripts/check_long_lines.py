import sys

path = sys.argv[1] if len(sys.argv) > 1 else "DOCUMENTATION.md"
width = int(sys.argv[2]) if len(sys.argv) > 2 else 80
in_code = False
with open(path, encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code and len(line.rstrip("\n")) > width:
            print(f"Line:{i} Length:{len(line.rstrip())} {line.rstrip()}")
