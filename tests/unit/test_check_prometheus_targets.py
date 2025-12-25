import types


class DummyResponse:
    def __init__(self, json_data, status=200):
        self._json = json_data
        self.status_code = status

    def json(self):
        return self._json

    def raise_for_status(self):
        return None


def load_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_prometheus_targets", "./.github/scripts/check_prometheus_targets.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_check_once_found(monkeypatch):
    mod = load_module()

    sample = {
        "data": {
            "activeTargets": [
                {"discoveredLabels": {"__address__": "127.0.0.1:5001"}, "health": "up"}
            ]
        }
    }

    def fake_get(url, timeout):
        return DummyResponse(sample)

    monkeypatch.setattr(mod, "requests", types.SimpleNamespace(get=fake_get))
    assert mod.check_once("http://localhost:9090/api/v1/targets", {"127.0.0.1:5001"}, timeout=1.0)


def test_check_once_not_found(monkeypatch):
    mod = load_module()

    sample = {"data": {"activeTargets": []}}

    def fake_get(url, timeout):
        return DummyResponse(sample)

    monkeypatch.setattr(mod, "requests", types.SimpleNamespace(get=fake_get))
    assert not mod.check_once("http://localhost:9090/api/v1/targets", {"127.0.0.1:5001"}, timeout=1.0)
