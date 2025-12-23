import os


def test_portalocker_is_used_when_available(tmp_path, monkeypatch):
    """Simular que portalocker está disponible y verificar que se intenta usarlo

    Este test parchea `tsc_integration.HAS_PORTALOCKER` a True y reemplaza
    `portalocker.Lock` por un Dummy que registra las llamadas.
    """
    import tsc_integration

    # Crear archivos temporales
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:30.0\n", encoding="utf-8")
    sendfile = tmp_path / "SendCommand.txt"

    tsci = tsc_integration.TSCIntegration(ruta_archivo=str(getdata))
    tsci.ruta_archivo_comandos = str(sendfile)

    # Dummy lock para registrar llamadas
    class DummyLock:
        calls = []

        def __init__(self, path, mode, timeout=0.1):
            DummyLock.calls.append((path, mode, timeout))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    # Forzar uso de portalocker y parchear Lock
    monkeypatch.setattr(tsc_integration, "HAS_PORTALOCKER", True)
    monkeypatch.setattr(tsc_integration, "portalocker", type("p", (), {"Lock": DummyLock}))

    # Ejecutar una lectura para invocar el lock en lectura
    lines = tsci._robust_read_lines()
    assert DummyLock.calls, "Expected portalocker.Lock to be called during read"

    # Limpiar registros y ejecutar escritura para invocar lock en escritura
    DummyLock.calls.clear()
    ok = tsci.enviar_comandos({"freno_tren": 0.5})
    assert ok is True
    assert DummyLock.calls, "Expected portalocker.Lock to be called during atomic write"
