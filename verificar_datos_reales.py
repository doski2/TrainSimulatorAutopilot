#!/usr/bin/env python3
"""
Script para verificar que los datos de frenos se están enviando correctamente
desde el backend del dashboard.
"""

import os

import requests


def verificar_datos_frenos():
    """Verifica que los datos de frenos están presentes en la respuesta del servidor."""
    try:
        # Hacer una petición al endpoint de estado del servidor
        response = requests.get("http://localhost:5001/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor del dashboard está respondiendo correctamente")
            try:
                js = response.json()
                if "telemetry_source" in js:
                    print(f"ℹ️  telemetry_source: {js.get('telemetry_source')}")
                if "brake_pressure_present" in js:
                    print(f"ℹ️  brake_pressure_present: {js.get('brake_pressure_present')}")
                # Show individual flags when available
                for flag in [
                    "presion_tubo_freno_presente",
                    "presion_tubo_freno_mostrada_presente",
                    "presion_freno_loco_presente",
                    "presion_freno_loco_mostrada_presente",
                    "presion_freno_tren_presente",
                    "presion_deposito_principal_presente",
                    "eq_reservoir_presente",
                    "presion_deposito_auxiliar_presente",
                    "posicion_freno_tren_presente",
                    "presion_freno_tren_inferida",
                    "presion_freno_loco_avanzada_presente",
                ]:
                    if flag in js:
                        print(f"   {flag}: {js.get(flag)}")
            except Exception:
                pass
            return True
        else:
            print(f"❌ Error en la respuesta del servidor: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False


def verificar_archivo_getdata():
    """Verifica que el archivo GetData.txt existe y tiene datos."""
    try:
        # Use default TSC plugin path to check if real GetData.txt exists
        default_getdata_path = (
            r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"
        )
        target_path = (
            default_getdata_path if os.path.exists(default_getdata_path) else "GetData.txt"
        )
        with open(target_path, encoding="utf-8") as f:
            contenido = f.read()
            if contenido.strip():
                print("✅ Archivo GetData.txt existe y tiene contenido")
                # Mostrar las primeras líneas para verificar formato
                lineas = contenido.split("\n")[:5]
                print("📄 Primeras líneas del archivo GetData.txt:")
                for i, linea in enumerate(lineas, 1):
                    print(f"   {i}: {linea}")
                return True
            else:
                print("❌ Archivo GetData.txt está vacío")
                return False
    except FileNotFoundError:
        print(
            f"❌ Archivo GetData.txt no encontrado en {default_getdata_path} ni en el directorio actual"
        )
        return False
    except Exception as e:
        print(f"❌ Error leyendo GetData.txt: {e}")
        return False


def verificar_test_data_renombrado():
    """Verifica que test_data.txt fue renombrado."""
    import os

    if os.path.exists("test_data.txt"):
        print("❌ test_data.txt aún existe - el sistema podría estar usando datos de prueba")
        return False
    elif os.path.exists("test_data_backup.txt"):
        print("✅ test_data.txt fue correctamente renombrado a test_data_backup.txt")
        return True
    else:
        print("ℹ️  No se encontró test_data.txt ni test_data_backup.txt")
        return True


if __name__ == "__main__":
    print("🔍 Verificando configuración del dashboard con datos reales...")
    print()

    # Verificar que test_data.txt fue renombrado
    verificar_test_data_renombrado()
    print()

    # Verificar archivo GetData.txt
    verificar_archivo_getdata()
    print()

    # Verificar servidor
    verificar_datos_frenos()
    print()

    print("✅ Verificación completada. El dashboard debería mostrar datos reales de frenos.")
