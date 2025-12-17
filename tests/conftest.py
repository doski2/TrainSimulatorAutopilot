"""Test configuration for pytest.

This centralizes test-time path setup so individual test modules don't need to
mutate sys.path. In CI or developer environments it is still recommended to
install the package in editable mode (e.g. `pip install -e .`) or configure
pyproject/pytest config to expose project modules, but this keeps the test suite
self-contained for running locally and in CI where installing editable deps
isn't always done.
"""

import sys
from pathlib import Path

# Ensure repository root is on sys.path for tests so tests can import project modules
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
