import types


class DummyResponse:
    def __init__(self, status=200, text="ok"):
        self.status_code = status
        self.text = text


def load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("wait_for_metrics", "./.github/scripts/wait_for_metrics.py")
    # Ensure spec is not None for type checkers
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_check_once_success(monkeypatch):
    mod = load_module()

    def fake_get(url, timeout):
        return DummyResponse(status=200, text="metric_line: 1\n")

    monkeypatch.setattr(mod, "requests", types.SimpleNamespace(get=fake_get))
    ok, info = mod.check_once("http://127.0.0.1:5001/metrics", timeout=0.1)
    assert ok is True
    assert info == "ok"


def test_check_once_failure_status(monkeypatch):
    mod = load_module()

    def fake_get(url, timeout):
        return DummyResponse(status=500, text="internal error\ntrace")

    monkeypatch.setattr(mod, "requests", types.SimpleNamespace(get=fake_get))
    ok, info = mod.check_once("http://127.0.0.1:5001/metrics", timeout=0.1)
    assert not ok
    assert "status=500" in info


def test_check_once_exception(monkeypatch):
    mod = load_module()

    def fake_get(url, timeout):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(mod, "requests", types.SimpleNamespace(get=fake_get))
    ok, info = mod.check_once("http://127.0.0.1:5001/metrics", timeout=0.1)
    assert not ok
    assert "request error" in info
