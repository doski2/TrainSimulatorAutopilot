import os

import pytest

from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration


def write_getdata_file(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


@pytest.mark.parametrize(
    "aspecto,expected_decision,expected_freno_min,expected_acelerador",
    [
        (0, "SEÑAL_ROJA_STOP", 1.0, 0.0),  # ROJA
        (1, "SEÑAL_AMARILLA", 0.2, 0.0),  # AMARILLA
    ],
)
def test_signals_override_red_yellow(
    aspecto, expected_decision, expected_freno_min, expected_acelerador, tmp_path
):
    """Test that SEÑAL_ROJA_STOP and SEÑAL_AMARILLA produce expected overrides."""
    file_path = tmp_path / "GetData_test.txt"

    # Compose simple GetData file with the needed controls
    lines = [
        "ControlName:CurrentSpeed",
        "ControlValue:0",
        "ControlName:CurrentSpeedLimit",
        "ControlValue:80",
        "ControlName:SignalAspect",
        f"ControlValue:{aspecto}",
        "ControlName:KVB_SignalAspect",
        "ControlValue:-1",
    ]
    write_getdata_file(str(file_path), lines)

    system = AutopilotSystem()
    system.tsc = TSCIntegration(ruta_archivo=str(file_path))
    system.sesion_activa = True

    res = system.ejecutar_ciclo_control()
    assert res is not None
    comandos = res["comandos"]

    assert comandos["decision"] == expected_decision
    assert comandos["freno_tren"] >= expected_freno_min
    assert comandos["acelerador"] == expected_acelerador


def test_signal_proceed_no_override(tmp_path):
    """Test that PROCEED (2) does not trigger special 'SEÑAL_*' override (no stop or caution)."""
    file_path = tmp_path / "GetData_test.txt"

    # Use a CurrentSpeed to make the IA choose a deterministic behavior
    lines = [
        "ControlName:CurrentSpeed",
        "ControlValue:10",  # small positive speed
        "ControlName:CurrentSpeedLimit",
        "ControlValue:80",
        "ControlName:SignalAspect",
        "ControlValue:2",  # PROCEED
        "ControlName:KVB_SignalAspect",
        "ControlValue:-1",
    ]
    write_getdata_file(str(file_path), lines)

    system = AutopilotSystem()
    system.tsc = TSCIntegration(ruta_archivo=str(file_path))
    system.sesion_activa = True

    res = system.ejecutar_ciclo_control()
    assert res is not None
    comandos = res["comandos"]

    # Ensure decision is not a SEÑAL_* override
    assert not comandos["decision"].startswith("SEÑAL_")
    # Ensure we did not apply maximum train brake
    assert comandos["freno_tren"] < 1.0


if __name__ == "__main__":
    pytest.main([__file__])
