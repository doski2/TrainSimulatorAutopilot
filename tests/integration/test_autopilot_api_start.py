import os

from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration
from web_dashboard import app


def test_start_autopilot_writes_commands_and_reports_plugin_state_when_plugin_reports_on(tmp_path, monkeypatch):
    # Prepare GetData.txt (so autopilot_system.start() succeeds)
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    # Prepare TSCIntegration pointing to tmp files
    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    # Simulate plugin state file present (plugin reports 'on')
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    state_file = os.path.join(plugins_dir, "autopilot_state.txt")
    open(state_file, "w", encoding="utf-8").write("on")

    # Prepare autopilot system and inject TSC
    ap = AutopilotSystem()
    ap.tsc = tsci

    # Inject into dashboard module
    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    # Call endpoint
    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        # The API should report plugin_state 'on' as we created the plugin state file
        assert data.get('autopilot_plugin_state') == 'on'

    # Check that commands files include 'start_autopilot'
    main_content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in main_content
    lua_file = os.path.join(os.path.dirname(tsci.ruta_archivo_comandos), 'autopilot_commands.txt')
    assert os.path.exists(lua_file)
    assert 'start_autopilot' in open(lua_file, encoding='utf-8').read()


def test_start_autopilot_succeeds_by_default_when_plugin_unresponsive(tmp_path, monkeypatch):
    # Prepare GetData.txt
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    ap = AutopilotSystem()
    ap.tsc = tsci

    # Ensure no plugin state file exists
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    state_file = os.path.join(plugins_dir, "autopilot_state.txt")
    if os.path.exists(state_file):
        os.remove(state_file)

    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot')
        # New behaviour: by default the API does NOT wait for plugin confirmation and returns success immediately
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    # Commands file should still have the start_autopilot command
    content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in content

    # Commands file should still have the start_autopilot command
    content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in content

    # Client request (payload ignored) — should still return success
    with app.test_client() as client:
        resp2 = client.post('/api/control/start_autopilot', json={'timeout': 2.0})
        assert resp2.status_code == 200
        assert resp2.get_json().get('success') is True


def test_start_autopilot_ignores_legacy_env_flag_and_returns_success(tmp_path, monkeypatch):
    # Prepare GetData.txt
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    ap = AutopilotSystem()
    ap.tsc = tsci

    # Ensure no plugin state file exists
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    state_file = os.path.join(plugins_dir, "autopilot_state.txt")
    if os.path.exists(state_file):
        os.remove(state_file)

    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    # Legacy env flags are ignored by the current implementation

    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot')
        # After removing file-based confirmation support, API returns success regardless of env
        assert resp.status_code == 200
        assert resp.get_json().get('success') is True



def test_start_autopilot_env_flag_ignored(tmp_path, monkeypatch):
    # Prepare GetData.txt
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    ap = AutopilotSystem()
    ap.tsc = tsci

    # Ensure no plugin state file exists
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    state_file = os.path.join(plugins_dir, "autopilot_state.txt")
    if os.path.exists(state_file):
        os.remove(state_file)

    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    # Legacy env flags are ignored by the current implementation

    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot')
        # Now the API should return success (200) despite missing plugin state file
        assert resp.status_code == 200
        assert resp.get_json().get('success') is True

    # Commands file should still have the start_autopilot command
    content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in content
