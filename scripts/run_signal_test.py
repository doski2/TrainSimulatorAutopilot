import os
import tempfile

from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration


def run_test(signal=0):
    tmpdir = tempfile.gettempdir()
    ruta = os.path.join(tmpdir, "GetData_test.txt")

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("ControlName:SignalAspect\n")
        f.write(f"ControlValue:{signal}\n")
        f.write("ControlName:KVB_SignalAspect\n")
        f.write("ControlValue:-1\n")

    system = AutopilotSystem()
    system.tsc = TSCIntegration(ruta_archivo=ruta)
    system.sesion_activa = True

    res = system.ejecutar_ciclo_control()
    if not res:
        print("No se obtuvo resultado de ejecutar_ciclo_control()")
        return 1

    comandos = res.get("comandos", {})
    print("RESULT:")
    print(comandos)

    ok = False
    if signal == 0:
        ok = (
            comandos.get("decision") == "SEÑAL_ROJA_STOP"
            and comandos.get("freno_tren", 0.0) >= 1.0
            and comandos.get("acelerador", 0.0) == 0.0
        )
    elif signal == 1:
        ok = (
            comandos.get("decision") == "SEÑAL_AMARILLA"
            and comandos.get("freno_tren", 0.0) >= 0.2
            and comandos.get("acelerador", 0.0) == 0.0
        )
    elif signal == 2:
        ok = not comandos.get("decision", "").startswith("SEÑAL_")

    if ok:
        print("✅ OK: test passed")
        return 0
    else:
        print("❌ NOT OK: unexpected behavior")
        return 2


if __name__ == "__main__":
    # Use 0 (ROJA) by default
    raise SystemExit(run_test(0))
