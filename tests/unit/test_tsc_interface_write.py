from tsc_integration import TSCIntegration


def test_write_to_tsc_interface_file(tmp_path):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    send_file = plugins / "SendCommand.txt"

    tsc = TSCIntegration()
    # Configure paths to point to tmp plugins folder
    tsc.ruta_archivo_comandos = str(plugins / "SendCommand.txt")
    tsc.write_lua_commands = False

    # Set explicit interface file path
    tsc.tsc_interface_file = str(send_file)

    # Send numeric control commands
    ok = tsc.enviar_comandos({"Regulator": 0.125, "VirtualThrottle": 0.125, "VirtualBrake": 0.37})
    assert ok is True

    assert send_file.exists()
    content = send_file.read_text(encoding="utf-8").strip().splitlines()
    assert "Regulator:0.125" in content
    assert "VirtualThrottle:0.125" in content
    assert "VirtualBrake:0.370" in content


def test_acelerador_writes_both_regulator_and_virtualthrottle(tmp_path):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    send_file = plugins / "SendCommand.txt"

    tsc = TSCIntegration()
    tsc.ruta_archivo_comandos = str(plugins / "SendCommand.txt")
    tsc.write_lua_commands = False
    tsc.tsc_interface_file = str(send_file)

    # Send 'acelerador' command from AI (Spanish name mapped to Regulator)
    ok = tsc.enviar_comandos({"acelerador": 0.375})
    assert ok is True

    assert send_file.exists()
    content = send_file.read_text(encoding="utf-8").strip().splitlines()
    # Both controls should be present so that either asset type responds
    assert "Regulator:0.375" in content
    assert "VirtualThrottle:0.375" in content


def test_start_autopilot_fallback_when_plugin_not_loaded(tmp_path, monkeypatch):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    send_file = plugins / "SendCommand.txt"

    tsc = TSCIntegration()
    tsc.ruta_archivo_comandos = str(plugins / "SendCommand.txt")
    tsc.write_lua_commands = False
    tsc.tsc_interface_file = str(send_file)

    # Simulate plugin not loaded
    monkeypatch.setattr(tsc, "is_autopilot_plugin_loaded", lambda: False)

    # Send the boolean autopilot command that normally yields 'start_autopilot'
    ok = tsc.enviar_comandos({"autopilot": True})
    assert ok is True

    assert send_file.exists()
    content = send_file.read_text(encoding="utf-8").strip().splitlines()

    # The fallback regulator/virtual throttle lines should be present so the train reacts
    assert "Regulator:0.125" in content
    assert "VirtualThrottle:0.125" in content


def test_acelerador_snaps_to_nearest_notch(tmp_path):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    send_file = plugins / "SendCommand.txt"

    tsc = TSCIntegration()
    tsc.ruta_archivo_comandos = str(plugins / "SendCommand.txt")
    tsc.write_lua_commands = False
    tsc.tsc_interface_file = str(send_file)

    # Value 0.18 is closer to 0.125 than to 0.25 -> should snap to 0.125
    ok = tsc.enviar_comandos({"acelerador": 0.18})
    assert ok is True
    content = send_file.read_text(encoding="utf-8").strip().splitlines()
    assert "Regulator:0.125" in content
    assert "VirtualThrottle:0.125" in content

    # Value 0.19 is closer to 0.25 than to 0.125 -> should snap to 0.250
    ok = tsc.enviar_comandos({"acelerador": 0.19})
    assert ok is True
    content = send_file.read_text(encoding="utf-8").strip().splitlines()
    assert "Regulator:0.250" in content
    assert "VirtualThrottle:0.250" in content
