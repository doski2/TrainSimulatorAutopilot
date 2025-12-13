"""
extractor.py
Extrae datos en tiempo real del juego Train Simulator Classic desde GetData.txt.
Documenta cada fuente y formato de dato extraído.
"""

import logging
import os
import time
from typing import Dict, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ruta al archivo GetData.txt
GETDATA_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"


def leer_getdata() -> Optional[Dict[str, float]]:
    """
    Lee los datos de telemetría desde GetData.txt.

    Returns:
        Dict con los datos parseados o None si hay error.
    """
    if not os.path.exists(GETDATA_PATH):
        logging.warning(f"Archivo GetData.txt no encontrado en {GETDATA_PATH}")
        return None

    try:
        with open(GETDATA_PATH, encoding="utf-8") as f:
            contenido = f.read().strip()

        if not contenido:
            logging.warning("Archivo GetData.txt está vacío")
            return None

        # Parsear el contenido (asumiendo formato clave=valor por línea)
        datos = {}
        for linea in contenido.split("\n"):
            if "=" in linea:
                clave, valor = linea.split("=", 1)
                clave = clave.strip()
                try:
                    datos[clave] = float(valor.strip())
                except ValueError:
                    logging.warning(f"No se pudo convertir a float: {linea}")
                    continue

        logging.info(f"Datos extraídos: {len(datos)} variables")
        return datos

    except Exception as e:
        logging.error(f"Error al leer GetData.txt: {e}")
        return None


def extraer_datos_en_tiempo_real(intervalo: float = 1.0):
    """
    Extrae datos continuamente cada intervalo de segundos.

    Args:
        intervalo: Segundos entre lecturas.
    """
    logging.info("Iniciando extracción de datos en tiempo real...")
    while True:
        datos = leer_getdata()
        if datos:
            # Aquí se pueden procesar o enviar los datos
            print(f"Datos actuales: {datos}")
        time.sleep(intervalo)


# Ejemplo de uso
if __name__ == "__main__":
    # Prueba de lectura única
    datos = leer_getdata()
    if datos:
        print("Datos leídos:")
        for clave, valor in datos.items():
            print(f"  {clave}: {valor}")
    else:
        print("No se pudieron leer los datos")

    # Para extracción continua (descomentar si se desea)
    # extraer_datos_en_tiempo_real()
