from pathlib import Path

from autopilot_system import AutopilotSystem


def write_getdata(path: Path):
    with path.open("w", encoding="utf-8") as f:
        f.write("ControlName:CurrentSpeed\n")
        f.write("ControlValue:20.0\n")


def test_ia_sends_accelerator(tmp_path: Path):
    getdata = tmp_path / "GetData.txt"
    commands = tmp_path / "autopilot_commands.txt"
    write_getdata(getdata)

    system = AutopilotSystem()
    system.tsc.ruta_archivo = str(getdata)
    system.tsc.ruta_archivo_comandos = str(commands)

    assert system.iniciar_sesion() is True
    assert system.activar_modo_automatico() is True

    # Monkeypatch IA to return an ACELERAR decision with high throttle
    def fake_procesar_telemetria(_datos):
        return {"decision": "ACELERAR", "acelerador": 0.8}

    system.ia.procesar_telemetria = fake_procesar_telemetria

    # Run one control cycle
    res = system.ejecutar_ciclo_control()
    assert res is not None

    # Check that commands file was written and contains Regulator/VirtualThrottle
    assert commands.exists()
    content = commands.read_text(encoding="utf-8")
    assert "Regulator:" in content or "VirtualThrottle:" in content
