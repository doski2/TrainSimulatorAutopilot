"""Simple validators for web API payloads.

The implementation uses jsonschema if available; tests skip when jsonschema
is not installed to keep test environments flexible.
"""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schemas" / "control_set_schema.json"

try:
    import jsonschema
    from jsonschema import ValidationError

    HAS_JSONSCHEMA = True
except Exception:
    jsonschema = None  # type: ignore
    ValidationError = Exception
    HAS_JSONSCHEMA = False

# Forbidden characters that should not appear in control names
FORBIDDEN_CONTROL_CHARS = {":", "\n", "\r", "\x00"}


def validate_control_set(payload: dict) -> tuple[bool, str | None]:
    """Validate `/api/control/set` payload.

    Returns (True, None) on success, or (False, error_message) on failure.
    If jsonschema is not available, the test will skip higher-level tests.
    """
    if not HAS_JSONSCHEMA:
        return False, "jsonschema not available"

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(instance=payload, schema=schema)
    except ValidationError as e:
        return False, f"schema validation error: {e.message}"
    except Exception as e:
        return False, f"failed to validate payload: {e}"

    control = payload.get("control")
    # Additional checks not easily expressed in schema: forbidden characters and printable
    if any(ch in control for ch in FORBIDDEN_CONTROL_CHARS):
        return False, "control contains forbidden characters"
    if not isinstance(control, str) or not control.strip():
        return False, "control must be a non-empty string"
    if not control.isprintable():
        return False, "control contains non-printable characters"

    # value types validated by schema (bool / number / string), no extra checks here
    return True, None
