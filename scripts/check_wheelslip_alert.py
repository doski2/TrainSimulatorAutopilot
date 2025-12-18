import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from alert_system import AlertSystem  # noqa: E402
from tsc_integration import TSCIntegration  # noqa: E402

integ = TSCIntegration()
raw = integ.leer_datos_archivo()
datos_ia = integ.convertir_datos_ia(raw if raw else {})
print("Intensity:", datos_ia.get("deslizamiento_ruedas_intensidad"))
alert_sys = AlertSystem(alerts_file=".test_alerts.json", config_file=".test_alerts_config.json")
alert = alert_sys.check_wheelslip(datos_ia)
print("Alert returned:", alert is not None)
if alert:
    print("Alert data:", alert.to_dict())
