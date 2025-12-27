import os

from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration
from web_dashboard import app, autopilot_metrics


def test_start_autopilot_writes_commands_and_returns_ack_when_plugin_reports_on(tmp_path, monkeypatch):
    # Prepare GetData.txt (so autopilot_system.start() succeeds)
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    # Prepare TSCIntegration pointing to tmp files
    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    # Simulate plugin ACK file present (plugin reports 'on')
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    ack_file = os.path.join(plugins_dir, "autopilot_state.txt")
    open(ack_file, "w", encoding="utf-8").write("on")

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
        # The API should report plugin_state 'on' as we created the ACK
        assert data.get('autopilot_plugin_state') == 'on'

    # Check that commands files include 'start_autopilot'
    main_content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in main_content
    lua_file = os.path.join(os.path.dirname(tsci.ruta_archivo_comandos), 'autopilot_commands.txt')
    assert os.path.exists(lua_file)
    assert 'start_autopilot' in open(lua_file, encoding='utf-8').read()


def test_start_autopilot_skips_ack_by_default_and_returns_success_when_plugin_unresponsive(tmp_path, monkeypatch):
    # Prepare GetData.txt
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    ap = AutopilotSystem()
    ap.tsc = tsci

    # Ensure no ACK file exists
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    ack_file = os.path.join(plugins_dir, "autopilot_state.txt")
    if os.path.exists(ack_file):
        os.remove(ack_file)

    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot')
        # New behaviour: by default the API does NOT wait for ACK and returns success immediately
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    # Commands file should still have the start_autopilot command
    content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in content

    # Commands file should still have the start_autopilot command
    content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in content

    # Client can explicitly request no-wait; should still return success
    with app.test_client() as client:
        resp2 = client.post('/api/control/start_autopilot', json={'wait_for_ack': False})
        assert resp2.status_code == 200
        assert resp2.get_json().get('success') is True


def test_start_autopilot_ignores_ack_config_and_returns_success(tmp_path, monkeypatch):
    # Prepare GetData.txt
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    ap = AutopilotSystem()
    ap.tsc = tsci

    # Ensure no ACK file exists
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    ack_file = os.path.join(plugins_dir, "autopilot_state.txt")
    if os.path.exists(ack_file):
        os.remove(ack_file)

    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    # Set env to true (legacy) — should be ignored and API should still return success
    monkeypatch.setenv("AUTOPILOT_REQUIRE_ACK", "true")

    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot')
        # After removing ACK support, API returns success regardless of env
        assert resp.status_code == 200
        assert resp.get_json().get('success') is True



def test_start_autopilot_env_disables_ack_and_skips_wait(tmp_path, monkeypatch):
    # Prepare GetData.txt
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    ap = AutopilotSystem()
    ap.tsc = tsci

    # Ensure no ACK file exists
    plugins_dir = os.path.dirname(tsci.ruta_archivo_comandos)
    ack_file = os.path.join(plugins_dir, "autopilot_state.txt")
    if os.path.exists(ack_file):
        os.remove(ack_file)

    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    # Set environment to disable ACK requirement globally (legacy flag; now ignored)
    monkeypatch.setenv("AUTOPILOT_REQUIRE_ACK", "false")

    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot')
        # Now the API should return success (200) despite no ACK
        assert resp.status_code == 200
        assert resp.get_json().get('success') is True

    # Commands file should still have the start_autopilot command
    content = open(tsci.ruta_archivo_comandos, encoding='utf-8').read()
    assert 'start_autopilot' in content
