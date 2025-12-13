import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tsc_integration import TSCIntegration

if __name__ == "__main__":
    tsc = TSCIntegration(ruta_archivo=r"C:\temp\GetData_test.txt")
    datos_archivo = tsc.leer_datos_archivo()
    print("raw file parsed as:", datos_archivo)
    datos = tsc.obtener_datos_telemetria()
    if not datos:
        print("No telemetry parsed or empty telemetry snapshot")
    else:
        print("senal_principal:", datos.get("senal_principal"))
        print("senal_avanzada :", datos.get("senal_avanzada"))
        print("senal_procesada:", datos.get("senal_procesada"))
