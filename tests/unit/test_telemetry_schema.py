import json
from jsonschema import validate, ValidationError

SCHEMA_PATH = "docs/schemas/telemetry_update.schema.json"


def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_valid_telemetry_payload():
    schema = load_schema()
    payload = {
        "fecha_hora": "2026-01-14T12:34:56Z",
        "velocidad_actual": 72.5,
        "acelerador": 0.5,
        "freno_tren": 0.0,
        "rpm": 1200.0,
        "senal_procesada": 2,
        "autopilot_active": False,
    }
    # should not raise
    validate(payload, schema)


def test_invalid_telemetry_payload_missing_fecha():
    schema = load_schema()
    payload = {
        "velocidad_actual": 72.5,
        "acelerador": 0.5,
    }
    try:
        validate(payload, schema)
        raise AssertionError("Expected ValidationError")
    except ValidationError:
        pass


def test_invalid_type_payload():
    schema = load_schema()
    payload = {
        "fecha_hora": "2026-01-14T12:34:56Z",
        "velocidad_actual": "fast",
    }
    try:
        validate(payload, schema)
        raise AssertionError("Expected ValidationError")
    except ValidationError:
        pass
