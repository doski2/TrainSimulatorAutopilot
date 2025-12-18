"""
Tests unitarios actualizados para el módulo TSCIntegration real
"""

import os
import tempfile

import pytest

from tsc_integration import TSCIntegration


@pytest.fixture
def tsc_integration():
    return TSCIntegration()


def test_archivo_no_existe(tsc_integration):
    """Debe devolver None si el archivo no existe."""
    tsc_integration.ruta_archivo = "ruta/inexistente/GetData.txt"
    assert tsc_integration.leer_datos_archivo() is None


def test_leer_datos_archivo_valido(tsc_integration):
    """Debe leer correctamente un archivo con datos simulados."""
    contenido = """
ControlName:CurrentSpeed
ControlValue:10.0
ControlName:Acceleration
ControlValue:0.5
ControlName:RPM
ControlValue:400
ControlName:Ammeter
ControlValue:250.5
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
        f.write(contenido)
        temp_path = f.name
    tsc_integration.ruta_archivo = temp_path
    datos = tsc_integration.leer_datos_archivo()
    os.remove(temp_path)
    assert datos["CurrentSpeed"] == 10.0
    assert datos["Acceleration"] == 0.5
    assert datos["RPM"] == 400
    assert datos["Ammeter"] == 250.5


def test_convertir_datos_ia(tsc_integration):
    """Debe mapear y convertir correctamente los datos de entrada."""
    datos_archivo = {
        "CurrentSpeed": 10.0,  # m/s
        "Acceleration": 0.5,
        "RPM": 400,
        "Ammeter": 250.5,
    }
    datos_ia = tsc_integration.convertir_datos_ia(datos_archivo)
    assert datos_ia["velocidad_actual"] == 36.0  # 10 m/s * 3.6
    assert datos_ia["aceleracion"] == 0.5
    assert datos_ia["rpm"] == 400
    assert datos_ia["amperaje"] == 250.5


def test_obtener_datos_telemetria_sin_archivo(tsc_integration):
    """Debe devolver None si el archivo no existe."""
    tsc_integration.ruta_archivo = "ruta/inexistente/GetData.txt"
    assert tsc_integration.obtener_datos_telemetria() is None


def test_threading_commands(tsc_integration):
    """Debe manejar comandos concurrentes correctamente."""
    import threading

    results = []
    errors = []

    def worker(command, value):
        try:
            tsc_integration.enviar_comandos({command: value})
            results.append((command, value))
        except Exception as e:
            errors.append(e)

    # Crear múltiples threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(f"THROTTLE_{i}", i * 0.1))
        threads.append(t)

    # Iniciar threads
    for t in threads:
        t.start()

    # Esperar que terminen
    for t in threads:
        t.join()

    # Verificar resultados
    assert len(results) == 5
    assert len(errors) == 0


def test_enviar_comandos_mapea_nombres(tsc_integration, tmp_path):
    """Verificar que enviar_comandos mapea comandos en español a nombres RailDriver."""
    # Crear archivo temporal para SendCommand
    send_cmd_file = tmp_path / "SendCommand.txt"
    tsc_integration.ruta_archivo_comandos = str(send_cmd_file)

    # Enviar comando en español 'freno_tren' y verificar el contenido escrito
    tsc_integration.enviar_comandos({"freno_tren": 0.0, "acelerador": 0.5})
    with open(tsc_integration.ruta_archivo_comandos, encoding="utf-8") as f:
        contenido = f.read().strip()

    assert "TrainBrakeControl:0.000" in contenido
    assert "VirtualThrottle:0.500" in contenido or "Regulator:0.500" in contenido


def test_enviar_comandos_fallback_dinamico(tsc_integration, tmp_path):
    """Si el asset no tiene DynamicBrake presente, enviar freno_dinamico debe usar VirtualEngineBrakeControl."""
    # Simular datos anteriores indicando que solo existe VirtualEngineBrakeControl
    tsc_integration.datos_anteriores = {"VirtualEngineBrakeControl": 0.2}
    tsc_integration.ruta_archivo_comandos = str(tmp_path / "SendCommandFallback.txt")
    tsc_integration.enviar_comandos({"freno_dinamico": 0.5})
    contenido = open(tsc_integration.ruta_archivo_comandos, encoding="utf-8").read()
    assert "VirtualEngineBrakeControl:0.500" in contenido


def test_enviar_comandos_escribe_archivo_lua(tsc_integration, tmp_path):
    """Verificar que enviar_comandos escriba también plugins/autopilot_commands.txt"""
    # Preparar ruta de SendCommand en tmp dir
    cmd_file = tmp_path / "SendCommand.txt"
    tsc_integration.ruta_archivo_comandos = str(cmd_file)

    # Enviar comando para iniciar autopilot
    tsc_integration.enviar_comandos({"autopilot": True})

    lua_file = tmp_path / "autopilot_commands.txt"
    assert lua_file.exists()
    contenido = lua_file.read_text(encoding="utf-8").strip()
    assert "start_autopilot" in contenido


def test_enviar_comandos_no_duplicate_when_same_file(tsc_integration, tmp_path):
    """If `ruta_archivo_comandos` already points to the Lua commands file, only that file should be written once."""
    lua_cmd = tmp_path / "autopilot_commands.txt"
    # Configure ruta_archivo_comandos to point to the same filename Lua reads
    tsc_integration.ruta_archivo_comandos = str(lua_cmd)

    # Ensure the flag to write lua commands is enabled (default)
    tsc_integration.write_lua_commands = True

    tsc_integration.enviar_comandos({"autopilot": True})

    # The alamacenado file should exist and contain the command
    assert lua_cmd.exists()
    contenido = lua_cmd.read_text(encoding="utf-8")
    assert "start_autopilot" in contenido

    def test_sendcommand_lowercase_written(tmp_path, monkeypatch):
        # Ensure that enviar_comandos writes sendcommand.txt (lowercase) when numeric commands present
        plugins = tmp_path / "plugins"
        plugins.mkdir()
        send_cmd = plugins / "SendCommand.txt"
        send_cmd.write_text("", encoding="utf-8")

        from tsc_integration import TSCIntegration

        tsc = TSCIntegration()
        tsc.ruta_archivo_comandos = str(send_cmd)

        assert tsc.enviar_comandos({"acelerador": 0.5}) is True

        lower = plugins / "sendcommand.txt"
        assert lower.exists()
        txt = lower.read_text(encoding="utf-8")
        assert "Regulator:0.500" in txt
