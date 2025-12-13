"""
Script de prueba para GetData.txt y normalización de señales usando TSCIntegration
Genera varios archivos GetData_test.txt y verifica que `senal_procesada` y campos
sean los esperados.

Ejecutar:
    python .\\scripts\test_getdata_suite.py
"""

import os
import sys
from pathlib import Path

# Permitir importar desde el root del repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tsc_integration import TSCIntegration

GETDATA_PATH = r"C:\temp\GetData_test.txt"

TEST_CASES = [
    # (SignalAspect, KVB_SignalAspect, expected_principal, expected_avanzada, expected_procesada)
    (0, -1, 0, -1, 0),
    (1, -1, 1, -1, 1),
    (2, -1, 2, -1, 2),
    (0, 2, 0, 2, 2),
    (-1, -1, -1, -1, -1),
]


def write_getdata(signal_aspect, kvb_aspect, path=GETDATA_PATH):
    # Escribir archivo ASCII sin BOM para evitar parse issues
    content = f"ControlName:SignalAspect\nControlValue:{signal_aspect}\nControlName:KVB_SignalAspect\nControlValue:{kvb_aspect}\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="ascii")


def run_case(signal_aspect, kvb_aspect, expected_principal, expected_avanzada, expected_procesada):
    write_getdata(signal_aspect, kvb_aspect)
    tsc = TSCIntegration(ruta_archivo=GETDATA_PATH)
    parsed = tsc.leer_datos_archivo()  # raw dictionary parsed from file
    datos = tsc.obtener_datos_telemetria()

    result = {
        "parsed": parsed,
        "senal_principal": datos.get("senal_principal") if datos is not None else None,
        "senal_avanzada": datos.get("senal_avanzada") if datos is not None else None,
        "senal_procesada": datos.get("senal_procesada") if datos is not None else None,
    }

    ok = True
    if result["senal_principal"] != expected_principal:
        ok = False
    if result["senal_avanzada"] != expected_avanzada:
        ok = False
    if result["senal_procesada"] != expected_procesada:
        ok = False

    return ok, result


def main():
    all_ok = True
    print("Running GetData test suite...")
    for idx, case in enumerate(TEST_CASES, 1):
        sa, kvb, exp_pr, exp_av, exp_pro = case
        ok, res = run_case(sa, kvb, exp_pr, exp_av, exp_pro)
        print("\nTest case", idx, f"(SignalAspect={sa}, KVB_SignalAspect={kvb})")
        print("  parsed raw:", res["parsed"])
        print(f"  expected -> principal:{exp_pr}, avanzada:{exp_av}, procesada:{exp_pro}")
        print(
            "  got      -> principal:",
            res["senal_principal"],
            ", avanzada:",
            res["senal_avanzada"],
            ", procesada:",
            res["senal_procesada"],
        )
        print("  PASS" if ok else "  FAIL")
        all_ok = all_ok and ok

    print("\nSummary:")
    if all_ok:
        print("All tests passed ✅")
        return 0
    else:
        print("Some tests failed ⚠️")
        return 2


if __name__ == "__main__":
    exit(main())
