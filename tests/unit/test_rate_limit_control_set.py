import time

from web_dashboard import app


class DummyTSC:
    def __init__(self):
        self.last = None

    def enviar_comandos(self, comandos):
        self.last = comandos
        return True


def test_control_set_rate_limit(monkeypatch):
    import web_dashboard as wd

    if wd.limiter is None:
        import pytest

        pytest.skip("Flask-Limiter not installed in test environment; skipping rate limit test")

    # Set a tight rate: 1 per second
    app.config["CONTROL_RATE_LIMIT"] = "1 per second"

    dummy = DummyTSC()

    monkeypatch.setattr(wd, "tsc_integration", dummy)
    client = app.test_client()

    payload = {"control": "Regulator", "value": 0.5}

    # First request should succeed
    r1 = client.post("/api/control/set", json=payload)
    assert r1.status_code == 200

    # Immediate second request should be rate limited (1 per second)
    r2 = client.post("/api/control/set", json=payload)
    assert r2.status_code == 429

    # After a short sleep, requests should succeed again
    time.sleep(1)
    r3 = client.post("/api/control/set", json=payload)
    assert r3.status_code == 200
    assert dummy.last == {"Regulator": 0.5}
