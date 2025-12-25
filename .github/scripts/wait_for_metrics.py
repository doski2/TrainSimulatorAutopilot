#!/usr/bin/env python3
"""Wait for the dashboard /metrics endpoint to be available.

This script performs configurable retries with simple logging on failures and
prints a small snippet of the response body when non-2xx responses are returned
so CI logs are more useful when debugging flakiness.
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Tuple

import requests


DEFAULT_URL = "http://127.0.0.1:5001/metrics"


def check_once(url: str, timeout: float = 5.0) -> Tuple[bool, str]:
    try:
        r = requests.get(url, timeout=timeout)
    except Exception as e:
        return False, f"request error: {e}"

    if 200 <= r.status_code < 300:
        return True, "ok"

    # return a short snippet of body for debugging
    try:
        body = r.text[:400].replace("\n", "\\n")
    except Exception:
        body = "<unreadable body>"
    return False, f"status={r.status_code} body={body}"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Wait for a metrics endpoint to respond 2xx")
    p.add_argument("--url", default=DEFAULT_URL, help="URL to poll")
    p.add_argument("--retries", type=int, default=120, help="number of retries")
    p.add_argument("--sleep", type=float, default=1.0, help="sleep seconds between retries")
    p.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout per request in seconds")
    args = p.parse_args(argv)

    for attempt in range(1, args.retries + 1):
        ok, info = check_once(args.url, timeout=args.timeout)
        if ok:
            print(f"metrics ready (attempt {attempt})")
            return 0
        print(f"metrics not ready (attempt {attempt}/{args.retries}): {info}")
        time.sleep(args.sleep)

    print("ERROR: /metrics not responding after configured retries", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
