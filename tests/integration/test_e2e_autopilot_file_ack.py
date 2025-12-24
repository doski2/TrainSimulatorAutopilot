import os
import time

from tsc_integration import TSCIntegration


def test_e2e_file_ack(tmp_path):
    """E2E: Python writes start_autopilot, simulated plugin reads it and writes ACK, and TSCIntegration.wait_for_autopilot_state detects it."""
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    tsc = TSCIntegration()
    tsc.ruta_archivo_comandos = str(plugins / "SendCommand.txt")
    tsc.write_lua_commands = True

    # Send start_autopilot
    ok = tsc.enviar_comandos({"autopilot": True})
    assert ok is True

    lua_file = plugins / "autopilot_commands.txt"
    assert lua_file.exists()

    # Simulate plugin processing after short delay
    time.sleep(0.1)
    # Read lines, ensure start_autopilot present
    lines = lua_file.read_text(encoding="utf-8").splitlines()
    assert "start_autopilot" in lines

    # Simulate plugin writing ACK
    ack_file = plugins / "autopilot_state.txt"
    ack_file.write_text("on", encoding="utf-8")

    # Now TSCIntegration should detect ack via wait_for_autopilot_state
    detected = tsc.wait_for_autopilot_state("on", timeout=1.0)
    assert detected is True