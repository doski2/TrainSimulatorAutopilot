import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tsc_integration import TSCIntegration


def write_getdata_bom(path: str, signal_aspect: int = 0, kvb_aspect: int = -1):
    # Escribir archivo con BOM UTF-8
    content = f"\ufeffControlName:SignalAspect\nControlValue:{signal_aspect}\nControlName:KVB_SignalAspect\nControlValue:{kvb_aspect}\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def test_bom_is_stripped_and_parsed():
    path = r"C:\temp\GetData_test_bom.txt"
    write_getdata_bom(path, 2, -1)
    tsc = TSCIntegration(ruta_archivo=path)
    parsed = tsc.leer_datos_archivo()
    datos = tsc.obtener_datos_telemetria()

    assert parsed is not None
    assert isinstance(parsed, dict)
    assert parsed.get("SignalAspect") == 2.0
    assert datos is not None
    assert isinstance(datos, dict)
    assert datos.get("senal_principal") == 2.0
    assert datos.get("senal_procesada") == 2
