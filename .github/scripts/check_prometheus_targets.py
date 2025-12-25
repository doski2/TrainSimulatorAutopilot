#!/usr/bin/env python3
"""Check that Prometheus has discovered the target and it's healthy.

By default this checks http://localhost:9090/api/v1/targets and looks for any
active target whose discoveredLabels['__address__'] is one of the allowed
addresses and whose 'health' == 'up'.

The script exits with 0 when such a target is found, and 1 otherwise.
It supports retrying (default 30 attempts with 1s delay) to wait for Prometheus.
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Iterable

import requests


DEFAULT_URL = "http://localhost:9090/api/v1/targets"
DEFAULT_ALLOWED = {"host.docker.internal:5001", "127.0.0.1:5001", "localhost:5001"}


def check_once(url: str, allowed: Iterable[str], timeout: float = 5.0) -> bool:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    for t in data.get("data", {}).get("activeTargets", []):
        addr = t.get("discoveredLabels", {}).get("__address__")
        if addr in allowed and t.get("health") == "up":
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Check Prometheus discovered targets")
    p.add_argument("--url", default=DEFAULT_URL, help="Prometheus targets API URL")
    p.add_argument("--retries", type=int, default=30, help="Number of retries")
    p.add_argument("--sleep", type=float, default=1.0, help="Seconds to sleep between retries")
    p.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout seconds")
    p.add_argument("--allowed", nargs="*", default=list(DEFAULT_ALLOWED), help="Allowed target addresses")
    args = p.parse_args(argv)

    allowed = set(args.allowed)
    for _ in range(args.retries):
        try:
            if check_once(args.url, allowed, timeout=args.timeout):
                print("Prometheus sees a healthy target")
                return 0
        except Exception as e:
            # Keep trying on transient errors
            print(f"check error: {e}", file=sys.stderr)
        time.sleep(args.sleep)
    print("Prometheus did not see a healthy target", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
