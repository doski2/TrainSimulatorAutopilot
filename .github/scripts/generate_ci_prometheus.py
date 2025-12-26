#!/usr/bin/env python3
"""Generate a CI Prometheus config by replacing localhost targets with host.docker.internal

Defaults:
  src: prometheus/prometheus.yml
  dest: prometheus/ci_prometheus.yml

This script is small and intentionally deterministic for CI. It exits with
non-zero code on errors so it can be used directly from GitHub Actions.

Requires: Python 3.9+ (typing annotations use typing.Optional/typing.List for
backwards-compatible annotations).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Enforce a minimum Python version so CI failures are explicit and visible.
if sys.version_info < (3, 9):
    raise SystemExit("generate_ci_prometheus.py requires Python 3.9 or newer")


def generate(src: Path, dest: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"source file not found: {src}")
    s = src.read_text(encoding="utf-8")
    s = s.replace("localhost:5001", "host.docker.internal:5001")
    dest.write_text(s, encoding="utf-8")
    print(f"WROTE {dest}")



# Prefer built-in generics (e.g. `list`) on newer Python; ruff may suggest `list` or `X | None` when applicable.


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate CI Prometheus config")
    p.add_argument("--src", default="prometheus/prometheus.yml", help="source prometheus.yml")
    p.add_argument("--dest", default="prometheus/ci_prometheus.yml", help="destination file to write")
    args = p.parse_args(argv)

    try:
        generate(Path(args.src), Path(args.dest))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
