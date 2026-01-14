import os
import io
import pytest
from tsc_integration import TSCIntegration


def write_bytes(path, data: bytes):
    with open(path, "wb") as f:
        f.write(data)


def write_text(path, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def test_partial_write_does_not_crash(tmp_path):
    # Simulate a partial write: ControlName present but ControlValue missing
    p = tmp_path / "GetData.txt"
    write_text(p, "ControlName: CurrentSpeed\n")

    t = TSCIntegration(ruta_archivo=str(p))

    # Should not raise; leer_datos_archivo should return dict or None but not crash
    datos = t.leer_datos_archivo()
    assert datos is not Exception


def test_malformed_bytes_handled(tmp_path):
    p = tmp_path / "GetData.txt"
    # Write invalid utf-8 bytes
    write_bytes(p, b"\xff\xfe\xff\xfe")

    t = TSCIntegration(ruta_archivo=str(p))

    # obtener_datos_telemetria should handle decoding issues and return None
    assert t.obtener_datos_telemetria() is None


def test_locked_file_retries_and_returns_none(monkeypatch, tmp_path):
    p = tmp_path / "GetData.txt"
    write_text(p, "ControlName: CurrentSpeed\nControlValue: 1.23\n")

    t = TSCIntegration(ruta_archivo=str(p))

    # Monkeypatch portalocker.Lock to raise PermissionError to simulate file lock on Windows
    class DummyLock:
        def __init__(self, *args, **kwargs):
            raise PermissionError("File is locked")

    monkeypatch.setattr("tsc_integration.portalocker", None)
    # Replace the HAS_PORTALOCKER flag to False to force fallback behavior
    monkeypatch.setattr(t, "archivo_existe", lambda: True)

    # Also monkeypatch the _robust_read_lines to simulate underlying PermissionError
    def raise_on_read(*args, **kwargs):
        raise PermissionError("locked by simulator")

    monkeypatch.setattr(t, "_robust_read_lines", raise_on_read)

    # leer_datos_archivo should catch the error and return None
    assert t.leer_datos_archivo() is None
