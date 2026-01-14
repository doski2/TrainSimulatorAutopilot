import os

import pytest

import web_dashboard as wd


@pytest.fixture(autouse=True)
def disable_auth_env(monkeypatch):
    # Default to enabled unless test explicitly sets API_KEYS
    monkeypatch.delenv("AUTH_DISABLED", raising=False)


def test_api_commands_requires_api_key(monkeypatch):
    # ensure no keys configured -> request will be allowed but warn; set key to enforce
    monkeypatch.setenv("API_KEYS", "testkey")

    # replace atomic_write_cmd to avoid file IO
    monkeypatch.setattr(wd, "atomic_write_cmd", lambda dirpath, payload: "id-123")

    client = wd.app.test_client()

    # Missing key -> 401
    resp = client.post("/api/commands", json={"type": "set_regulator", "value": 0.4})
    assert resp.status_code == 401

    # Invalid key -> 403
    resp = client.post("/api/commands", json={"type": "set_regulator", "value": 0.4}, headers={"X-API-KEY": "bad"})
    assert resp.status_code == 403

    # Valid key -> accepted (202)
    resp = client.post(
        "/api/commands",
        json={"type": "set_regulator", "value": 0.4},
        headers={"X-API-KEY": "testkey"},
    )
    assert resp.status_code == 202


def test_control_action_requires_api_key(monkeypatch):
    monkeypatch.setenv("API_KEYS", "ctrlkey")

    class DummyTSC:
        def enviar_comandos(self, comandos):
            return True

    monkeypatch.setattr(wd, "tsc_integration", DummyTSC())

    client = wd.app.test_client()

    # Missing key
    r = client.post("/api/control/emergency_brake")
    assert r.status_code == 401

    # Invalid key
    r = client.post("/api/control/emergency_brake", headers={"X-API-KEY": "no"})
    assert r.status_code == 403

    # Valid key should return 200 as dummy enviar_comandos returns True
    r = client.post("/api/control/emergency_brake", headers={"X-API-KEY": "ctrlkey"})
    assert r.status_code == 200
