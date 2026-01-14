import pytest

from tsc_integration import TSCIntegration


def test_enviar_comandos_returns_false_on_main_write_failure(monkeypatch, tmp_path):
    t = TSCIntegration()

    def raise_on_write(file_path, lines, retries=3, wait=0.1):
        raise OSError("disk full")

    monkeypatch.setattr(t, "_atomic_write_lines", raise_on_write)

    # emergency_brake is a critical control that should fail if we cannot write
    assert t.enviar_comandos({"command": "emergency_brake"}) is False


def test_enviar_comandos_success_when_writes_ok(monkeypatch):
    t = TSCIntegration()

    def noop_write(file_path, lines, retries=3, wait=0.1):
        return None

    monkeypatch.setattr(t, "_atomic_write_lines", noop_write)

    assert t.enviar_comandos({"command": "emergency_brake"}) is True
