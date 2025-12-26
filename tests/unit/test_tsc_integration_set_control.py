
from tsc_integration import TSCIntegration


def test_enviar_comandos_escribe_control_numerico(tmp_path):
    """Verificar que enviar_comandos escribe un control numérico al archivo Lua"""
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    lua_cmd = plugins / "autopilot_commands.txt"

    tsc = TSCIntegration()
    # point the send commands path to tmp directory's SendCommand.txt
    tsc.ruta_archivo_comandos = str(plugins / "SendCommand.txt")
    tsc.write_lua_commands = True

    ok = tsc.enviar_comandos({"Regulator": 0.45})
    assert ok is True

    assert lua_cmd.exists()
    content = lua_cmd.read_text(encoding="utf-8").strip()
    assert "Regulator:0.450" in content
