"""
Archivo de compatibilidad: `test_signal_roja.py` fue transformado en un test pytest y se dejó
un script independiente bajo `scripts/run_signal_test.py`.

Ejecuta la versión de pytest:
  python -m pytest -q tests/test_signal_roja_script.py

O ejecuta la versión standalone:
  python scripts/run_signal_test.py
"""

from scripts.run_signal_test import run_test

if __name__ == "__main__":
    # Ejecuta el script standalone con señal ROJA por defecto
    raise SystemExit(run_test(0))
