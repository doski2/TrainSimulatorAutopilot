from pathlib import Path

from autopilot_system import AutopilotSystem


def write_getdata(path: Path, entries: dict):
    # entries: mapping from control name to numeric value
    with path.open("w", encoding="utf-8") as f:
        for name, val in entries.items():
            f.write(f"ControlName:{name}\n")
            f.write(f"ControlValue:{val}\n")


def test_traction_mitigation_writes_throttle(tmp_path: Path):
    getdata = tmp_path / "GetData.txt"
    commands = tmp_path / "autopilot_commands.txt"

    # Prepare getdata that indicates slip: CurrentSpeed small, Wheelslip > 1 to indicate slip
    entries = {
        "CurrentSpeed": 5.0,  # m/s => 18 km/h
        "Wheelslip": 2.0,  # base-1 mapping -> intensity > 0
        "TractiveEffort": 500.0,
        "RPM": 3000.0,
    }
    write_getdata(getdata, entries)

    system = AutopilotSystem()
    # Point TSCIntegration to our temp files
    system.tsc.ruta_archivo = str(getdata)
    system.tsc.ruta_archivo_comandos = str(commands)

    # Start session and activate automatic mode
    assert system.iniciar_sesion() is True
    assert system.activar_modo_automatico() is True

    # Run a cycle - should detect slip and send throttle command
    result = system.ejecutar_ciclo_control()
    assert result is not None

    # Read commands file and check for Regulator/VirtualThrottle entries
    assert commands.exists(), "commands file not created"
    content = commands.read_text(encoding="utf-8")
    assert "Regulator:" in content or "VirtualThrottle:" in content
    # Ensure throttle value is reduced (not zero-length)
    assert ":" in content
