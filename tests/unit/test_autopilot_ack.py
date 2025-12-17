import os

from tsc_integration import TSCIntegration


def test_autopilot_plugin_ack(tmp_path, monkeypatch):
    # Setup a fake plugins directory
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    send_cmd = plugins_dir / "SendCommand.txt"
    # Create dummy SendCommand file
    send_cmd.write_text("", encoding="utf-8")

    tsc = TSCIntegration()
    # Override the commands path to point to our temp plugins dir
    tsc.ruta_archivo_comandos = str(send_cmd)

    # Initially, no ack files
    assert tsc.get_autopilot_plugin_state() is None
    assert tsc.is_autopilot_plugin_loaded() is False

    # Create loaded file
    loaded = plugins_dir / "autopilot_plugin_loaded.txt"
    loaded.write_text("loaded", encoding="utf-8")
    assert tsc.is_autopilot_plugin_loaded() is True

    # Create state file
    state = plugins_dir / "autopilot_state.txt"
    state.write_text("on", encoding="utf-8")
    assert tsc.get_autopilot_plugin_state() == "on"
