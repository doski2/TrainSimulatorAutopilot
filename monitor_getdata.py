#!/usr/bin/env python3
"""
monitor_getdata.py
Monitorea en tiempo real el archivo GetData.txt y muestra los valores clave cada vez que cambian.
"""

import os
import time
from datetime import datetime

RUTA_ARCHIVO = r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"

CAMPOS_CLAVE = [
    "CurrentSpeed",
    "Acceleration",
    "Gradient",
    "RPM",
    "Ammeter",
    "AirBrakePipePressurePSI",
    "LocoBrakeCylinderPressurePSI",
    "TrainBrakeCylinderPressurePSI",
]


def leer_datos_archivo(ruta):
    if not os.path.exists(ruta):
        return None
    try:
        with open(ruta, encoding="utf-8") as f:
            lineas = f.readlines()
        datos = {}
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            if linea.startswith("ControlName:"):
                nombre_control = linea.split(":", 1)[1]
                j = i + 1
                while j < len(lineas) and not lineas[j].strip().startswith("ControlValue:"):
                    j += 1
                if j < len(lineas):
                    valor_str = lineas[j].strip().split(":", 1)[1]
                    try:
                        valor = float(valor_str)
                        datos[nombre_control] = valor
                    except ValueError:
                        datos[nombre_control] = valor_str
            i += 1
        return datos
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return None


def main():
    print("\n🚦 Monitoreando GetData.txt en tiempo real...")
    print(f"Ubicación: {RUTA_ARCHIVO}")
    if not os.path.exists(RUTA_ARCHIVO):
        print(
            "❌ El archivo no existe. Ejecuta el simulador y asegúrate de que Raildriver Interface está activo."
        )
        return
    last_data = None
    try:
        while True:
            datos = leer_datos_archivo(RUTA_ARCHIVO)
            if datos and datos != last_data:
                print("\n" + "=" * 60)
                print(
                    f"🕒 {datetime.now().strftime('%H:%M:%S')} - Cambios detectados en GetData.txt:"
                )
                for campo in CAMPOS_CLAVE:
                    valor = datos.get(campo, "--")
                    print(f"   {campo:30}: {valor}")
                last_data = datos
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido por el usuario.")


if __name__ == "__main__":
    main()
