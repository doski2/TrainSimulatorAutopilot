import json

import pytest

from web_dashboard import app


class DummyTSC:
    def __init__(self):
        self.last = None

    def enviar_comandos(self, comandos):
        self.last = comandos
        return True


def test_control_set_success(monkeypatch):
    dummy = DummyTSC()
    import web_dashboard as wd

    monkeypatch.setattr(wd, "tsc_integration", dummy)
    client = app.test_client()

    payload = {"control": "Regulator", "value": 0.45}
    resp = client.post("/api/control/set", json=payload)
    assert resp.status_code == 200
    j = resp.get_json()
    assert j["success"] is True
    assert dummy.last == {"Regulator": 0.45}


def test_control_set_invalid_payload():
    client = app.test_client()
    resp = client.post("/api/control/set", json={})
    assert resp.status_code == 400
    j = resp.get_json()
    assert j["success"] is False


def test_control_set_tsc_unavailable(monkeypatch):
    import web_dashboard as wd

    monkeypatch.setattr(wd, "tsc_integration", None)
    client = app.test_client()

    payload = {"control": "Regulator", "value": 0.5}
    resp = client.post("/api/control/set", json=payload)
    assert resp.status_code == 500
    j = resp.get_json()
    assert j["success"] is False