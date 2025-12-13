import os

from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration


def write_getdata(path: str, signal_aspect: int):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("ControlName:SignalAspect\n")
        f.write(f"ControlValue:{signal_aspect}\n")
        f.write("ControlName:KVB_SignalAspect\n")
        f.write("ControlValue:-1\n")


def test_signal_roja_script(tmp_path):
    """Recreated the standalone script `test_signal_roja.py` as a pytest test that validates ROJA behavior."""
    ruta = tmp_path / "GetData_test.txt"

    write_getdata(str(ruta), 0)  # SignalAspect 0 => ROJA

    system = AutopilotSystem()
    system.tsc = TSCIntegration(ruta_archivo=str(ruta))
    system.sesion_activa = True

    res = system.ejecutar_ciclo_control()
    assert res is not None
    comandos = res["comandos"]

    assert comandos["decision"] == "SEÑAL_ROJA_STOP"
    assert comandos["freno_tren"] >= 1.0
    assert comandos["acelerador"] == 0.0
