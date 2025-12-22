import os

from web_dashboard import app
from tsc_integration import TSCIntegration


def test_api_metrics_io_writes_and_reads(tmp_path, monkeypatch):
    # Preparar un TSCIntegration con rutas en tmp
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    send_cmd = plugins / "SendCommand.txt"

    tsc = TSCIntegration()
    tsc.ruta_archivo_comandos = str(send_cmd)

    # Simular PermissionError en la primera escritura al archivo temporal
    orig_open = open
    calls = {"count": 0}

    def fake_open(path, mode="r", *args, **kwargs):
        tmp_path_str = os.path.abspath(str(tsc.ruta_archivo_comandos) + ".tmp")
        if os.path.abspath(path) == tmp_path_str and "w" in mode and calls["count"] == 0:
            calls["count"] += 1
            raise PermissionError("file locked")
        return orig_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    # Ejecutar acción para que haya métricas de escritura
    assert tsc.enviar_comandos({"acelerador": 0.5}) is True

    # Registrar la instancia global usada por el app
    monkeypatch.setattr('web_dashboard.tsc_integration', tsc)

    with app.test_client() as client:
        resp = client.get('/api/metrics/io')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'tsc_io_metrics' in data
        metrics = data['tsc_io_metrics']
        assert 'write_total_retries' in metrics
        assert metrics['write_total_retries'] >= 1
        assert 'read_total_retries' in metrics
        assert metrics['write_last_latency_ms'] >= 0.0