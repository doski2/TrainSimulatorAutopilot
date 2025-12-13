# visualization.py
# Script para visualización de datos de Train Simulator Autopilot

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)


def cargar_datos_limpios(ruta_archivo):
    """
    Carga los datos limpios desde el archivo CSV.
    """
    try:
        df = pd.read_csv(ruta_archivo)
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
        return df
    except FileNotFoundError:
        logger.error(f"Archivo {ruta_archivo} no encontrado.")
        return None


def graficar_velocidad(df):
    """
    Grafica la velocidad a lo largo del tiempo.
    """
    if df is None or "velocidad" not in df.columns:
        logger.warning("Datos insuficientes para graficar velocidad.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["fecha_hora"], df["velocidad"], label="Velocidad (km/h)", color="blue")
    plt.xlabel("Tiempo")
    plt.ylabel("Velocidad (km/h)")
    plt.title("Velocidad del Tren a lo Largo del Tiempo")
    plt.legend()
    plt.grid(True)
    plt.savefig("velocidad_chart.png")
    plt.close()
    logger.info("Gráfico de velocidad guardado como velocidad_chart.png")


def graficar_acelerador_freno(df):
    """
    Grafica acelerador y freno.
    """
    if df is None or "acelerador" not in df.columns or "freno" not in df.columns:
        logger.warning("Datos insuficientes para graficar controles.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["fecha_hora"], df["acelerador"], label="Acelerador", color="green")
    plt.plot(df["fecha_hora"], df["freno"], label="Freno", color="red")
    plt.xlabel("Tiempo")
    plt.ylabel("Valor")
    plt.title("Controles de Acelerador y Freno")
    plt.legend()
    plt.grid(True)
    plt.savefig("controles_chart.png")
    plt.close()
    logger.info("Gráfico de controles guardado como controles_chart.png")


# Ejemplo de uso
if __name__ == "__main__":
    ruta = os.path.join(os.path.dirname(__file__), "datos_tren_filtrados.csv")
    df = cargar_datos_limpios(ruta)
    if df is not None:
        graficar_velocidad(df)
        graficar_acelerador_freno(df)
    else:
        logger.error("No se pudieron cargar los datos.")
