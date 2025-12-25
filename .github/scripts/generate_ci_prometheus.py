#!/usr/bin/env python3
"""Generate a CI Prometheus config by replacing localhost targets with host.docker.internal

Defaults:
  src: prometheus/prometheus.yml
  dest: prometheus/ci_prometheus.yml

This script is small and intentionally deterministic for CI. It exits with
non-zero code on errors so it can be used directly from GitHub Actions.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def generate(src: Path, dest: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"source file not found: {src}")
    s = src.read_text(encoding="utf-8")
    s = s.replace("localhost:5001", "host.docker.internal:5001")
    dest.write_text(s, encoding="utf-8")
    print(f"WROTE {dest}")


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
