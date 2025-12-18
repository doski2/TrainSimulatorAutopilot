import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from tsc_integration import TSCIntegration  # noqa: E402

integ = TSCIntegration()
raw = integ.leer_datos_archivo()
print("Leidos del archivo:", list(raw.keys()) if raw else raw)
datos_ia = integ.convertir_datos_ia(raw if raw else {})
print("deslizamiento_ruedas_raw:", datos_ia.get("deslizamiento_ruedas_raw"))
print("deslizamiento_ruedas_intensidad:", datos_ia.get("deslizamiento_ruedas_intensidad"))
print("deslizamiento_ruedas_interpretacion:", datos_ia.get("deslizamiento_ruedas_interpretacion"))
print("deslizamiento_ruedas_inferida:", datos_ia.get("deslizamiento_ruedas_inferida"))
print(
    "datos_ia snippet:",
    {
        k: datos_ia.get(k)
        for k in [
            "deslizamiento_ruedas",
            "deslizamiento_ruedas_raw",
            "deslizamiento_ruedas_intensidad",
        ]
    },
)
