#!/usr/bin/env python3
import yaml, pathlib, sys
files=list(pathlib.Path('.').glob('**/*.[yY][mM][lL]'))
print(f"Found {len(files)} YAML files")
any_err=False
for f in files:
    try:
        s=f.read_text(encoding='utf-8')
    except Exception as e:
        print(f"DECODE_ERR\t{f}\t{e}")
        any_err=True
        continue
    if '\x00' in s:
        print(f"NUL_CHAR\t{f}")
        any_err=True
    try:
        yaml.safe_load(s)
        print(f"OK\t{f}")
    except Exception as e:
        print(f"PARSE_ERR\t{f}\t{e}")
        any_err=True
sys.exit(1 if any_err else 0)
