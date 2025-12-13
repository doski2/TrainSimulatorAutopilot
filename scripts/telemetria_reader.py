# telemetria_reader.py
# Script para leer y procesar telemetría desde el simulador

import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


def leer_telemetria(ruta_archivo):
    """
    Lee el archivo de telemetría y lo convierte en un diccionario.
    """
    datos = {}
    try:
        with open(ruta_archivo) as f:
            for linea in f:
                if ":" in linea:
                    clave, valor = linea.split(":", 1)
                    clave = clave.strip()
                    valor = valor.strip()
                    try:
                        # Intentar convertir a float si es numérico
                        datos[clave] = float(valor)
                    except ValueError:
                        datos[clave] = valor
    except FileNotFoundError:
        logger.error(f"Archivo {ruta_archivo} no encontrado.")
        return None
    return datos


def procesar_telemetria(datos):
    """
    Procesa los datos de telemetría: validación básica y extracción de variables clave.
    """
    if not datos:
        return None

    # Variables clave para la IA
    velocidad = datos.get("SpeedometerMPH", 0) * 1.60934  # Convertir a km/h
    acelerador = datos.get("SimpleThrottle", 0)
    freno = datos.get("TrainBrakeControl", 0)
    presion = datos.get("AirBrakePipePressurePSI", 0)

    # Validación básica
    if velocidad < 0 or velocidad > 500:
        print("Velocidad fuera de rango.")
        return None

    return {
        "velocidad": velocidad,
        "acelerador": acelerador,
        "freno": freno,
        "presion": presion,
        "fecha_hora": pd.Timestamp.now().isoformat(),
    }


# Ejemplo de uso
if __name__ == "__main__":
    ruta = os.path.join(os.path.dirname(__file__), "..", "docs", "data-received-from-railworks.md")
    datos_crudo = leer_telemetria(ruta)
    if datos_crudo:
        datos_procesados = procesar_telemetria(datos_crudo)
        if datos_procesados:
            print("Datos procesados:", datos_procesados)
        else:
            print("Error en procesamiento.")
    else:
        print("No se pudieron leer los datos.")
