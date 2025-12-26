
from tsc_integration import TSCIntegration
from web_dashboard import app


def test_api_status_includes_plugin_fields(tmp_path, monkeypatch):
    # Prepare fake plugins dir
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    send_cmd = plugins_dir / "SendCommand.txt"
    send_cmd.write_text("", encoding="utf-8")

    tsc = TSCIntegration()
    tsc.ruta_archivo_comandos = str(send_cmd)

    # Create ack files
    (plugins_dir / "autopilot_plugin_loaded.txt").write_text("loaded", encoding="utf-8")
    (plugins_dir / "autopilot_state.txt").write_text("on", encoding="utf-8")

    # Monkeypatch the global tsc_integration used by the app
    monkeypatch.setattr('web_dashboard.tsc_integration', tsc)

    with app.test_client() as client:
        resp = client.get('/api/status')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('autopilot_plugin_loaded') is True
        assert data.get('autopilot_plugin_state') == 'on'
