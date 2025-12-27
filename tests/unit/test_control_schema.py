import pytest

pytest.importorskip("jsonschema", reason="jsonschema not installed; skipping schema tests")

from web_validators import validate_control_set


def test_schema_valid_payload():
    payload = {"control": "Regulator", "value": 0.5}
    ok, reason = validate_control_set(payload)
    assert ok is True
    assert reason is None


def test_schema_invalid_value_type():
    payload = {"control": "Regulator", "value": [1,2,3]}
    ok, reason = validate_control_set(payload)
    assert ok is False
    assert reason is not None and ("schema validation" in reason or "Invalid value type" in reason)


def test_schema_reject_colon_in_control():
    payload = {"control": "Reg:Bad", "value": 0.5}
    ok, reason = validate_control_set(payload)
    assert ok is False
    assert reason is not None and "forbidden" in reason.lower()


def test_schema_reject_too_long():
    payload = {"control": "x" * 200, "value": 0.5}
    ok, reason = validate_control_set(payload)
    assert ok is False
    assert reason is not None and "schema" in reason.lower()
