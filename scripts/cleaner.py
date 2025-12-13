"""
cleaner.py
Limpia y valida los datos extraídos antes de almacenarlos para la IA.
"""

import pandas as pd


def cargar_datos(ruta_csv):
    """Carga los datos desde un archivo CSV."""
    return pd.read_csv(ruta_csv)


def limpiar_datos(df):
    """Aplica reglas de limpieza y validación sobre el DataFrame."""
    # Filtrar registros con valores nulos en variables clave
    df = df.dropna(subset=["velocidad", "posición", "acelerador", "freno"])

    # Filtrar velocidad fuera de rango
    df = df[(df["velocidad"] >= 0) & (df["velocidad"] <= 350)]

    # Marcar como error si la posición no cambia en más de 60 segundos
    if "tiempo_sin_cambio_posicion" in df.columns:
        df["error_posicion"] = df["tiempo_sin_cambio_posicion"] > 60

    # Filtrar presión fuera de rango físico
    if "presión" in df.columns:
        df = df[(df["presión"] >= 0) & (df["presión"] <= 200)]

    # Validar formato de fecha/hora
    if "fecha_hora" in df.columns:
        df["fecha_valida"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
        df = df.dropna(subset=["fecha_valida"])

    return df


def guardar_datos(df, ruta_salida):
    """Guarda el DataFrame limpio en un archivo CSV."""
    df.to_csv(ruta_salida, index=False)


if __name__ == "__main__":
    # Ejemplo de uso
    df = cargar_datos("datos_tren.csv")
    df_limpio = limpiar_datos(df)
    guardar_datos(df_limpio, "datos_tren_filtrados.csv")
