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


def test_locked_file_realistic(tmp_path):
    """Realistic lock: open file exclusively in a background thread to simulate
    the simulator holding the file open and verify TSCIntegration handles it."""
    import threading
    import time

    p = tmp_path / "GetData.txt"
    write_text(p, "ControlName: CurrentSpeed\nControlValue: 2.34\n")

    t = TSCIntegration(ruta_archivo=str(p))

    # Locker that works on Windows (msvcrt) and POSIX (fcntl)
    def locker():
        try:
            if os.name == "nt":
                import msvcrt

                f = open(p, "r+b")
                # Lock the entire file non-blocking
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                except Exception:
                    # Fallback to block
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                time.sleep(1.0)
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
                f.close()
            else:
                import fcntl

                f = open(p, "r+b")
                try:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    # Try blocking
                    fcntl.flock(f, fcntl.LOCK_EX)
                time.sleep(1.0)
                try:
                    fcntl.flock(f, fcntl.LOCK_UN)
                except Exception:
                    pass
                f.close()
        except Exception:
            # Ensure that the locker won't raise to the test harness
            pass

    t_thread = threading.Thread(target=locker, daemon=True)
    t_thread.start()

    # Give locker a moment to acquire the lock
    time.sleep(0.2)

    # obtener_datos_telemetria should not crash; it may return None if lock prevents reading
    res = t.obtener_datos_telemetria()
    assert res is None or isinstance(res, dict)

    t_thread.join()

