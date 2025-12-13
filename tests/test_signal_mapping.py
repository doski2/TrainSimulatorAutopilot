import os
import sys

# Ensure project root is in sys.path so tests can import tsc_integration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tsc_integration import TSCIntegration


def test_signal_principal_only():
    tsc = TSCIntegration(ruta_archivo=None)
    # Datos de archivo con solo SignalAspect
    datos_archivo = {"SignalAspect": 0}
    datos = tsc.convertir_datos_ia(datos_archivo)
    assert datos.get("senal_principal") == 0
    assert datos.get("senal_procesada") == 0

    datos_archivo = {"SignalAspect": 1}
    datos = tsc.convertir_datos_ia(datos_archivo)
    assert datos.get("senal_procesada") == 1

    datos_archivo = {"SignalAspect": 2}
    datos = tsc.convertir_datos_ia(datos_archivo)
    assert datos.get("senal_procesada") == 2


def test_signal_avanzada_prefiere_kvb():
    tsc = TSCIntegration(ruta_archivo=None)
    # Si KVB_SignalAspect está presente (senal_avanzada), se usa preferentemente
    datos_archivo = {"SignalAspect": 0, "KVB_SignalAspect": 2}
    datos = tsc.convertir_datos_ia(datos_archivo)
    assert datos.get("senal_principal") == 0
    assert datos.get("senal_avanzada") == 2
    assert datos.get("senal_procesada") == 2


def test_signal_unknown_defaults():
    tsc = TSCIntegration(ruta_archivo=None)
    datos_archivo = {}
    datos = tsc.convertir_datos_ia(datos_archivo)
    # Defaults should exist and se_procesada should be present
    assert "senal_principal" in datos
    assert "senal_procesada" in datos
