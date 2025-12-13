#!/usr/bin/env python3
"""
inspeccionar_datos_dashboard.py
Script para inspeccionar qué datos está recibiendo el dashboard en tiempo real
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime

import requests


def obtener_datos_debug():
    """Obtener datos desde el endpoint de debug del dashboard."""
    try:
        # Try common ports (5000 is default dev, 5001 used by our dashboard)
        tried_urls = ["http://localhost:5000/debug_data", "http://localhost:5001/debug_data"]
        response = None
        for url in tried_urls:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    break
            except Exception:
                response = None
        if response is None:
            raise requests.exceptions.ConnectionError("No se pudo conectar a /debug_data en puerto 5000/5001")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose web_dashboard.py?")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def mostrar_datos(datos):
    """Mostrar los datos de forma legible."""
    if not datos:
        return

    print("\n" + "=" * 80)
    print(f"🕐 DATOS RECIBIDOS - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)

    # Telemetría
    if "telemetry" in datos:
        telem = datos["telemetry"]
        print("\n📊 TELEMETRÍA:")
        print(f"   Velocidad actual:      {telem.get('velocidad_actual', 0):.2f} km/h")
        print(f"   Aceleración:           {telem.get('aceleracion', 0):.3f} m/s²")
        print(f"   RPM:                   {telem.get('rpm', 0):.0f}")
        print(f"   Amperaje:              {telem.get('amperaje', 0):.1f} A")
        print(f"   Presión tubo freno:    {telem.get('presion_tubo_freno', 0):.1f} PSI")
        print(f"   Presión freno loco:    {telem.get('presion_freno_loco', 0):.1f} PSI")
        print(f"   Esfuerzo tracción:     {telem.get('esfuerzo_traccion', 0):.0f} N")
        print(f"   Pendiente:             {telem.get('pendiente', 0):.2f}%")
        print(f"   Deslizamiento:         {telem.get('deslizamiento_ruedas', 0):.3f}")

        # Mostrar timestamp
        if "timestamp" in telem:
            print(f"   Timestamp:             {telem['timestamp']}")
        # Mostrar flags de presencia de campos en GetData
        print("\n   📌 Flags de presencia de presiones de freno:")
        print(f"      presion_tubo_freno_presente: {telem.get('presion_tubo_freno_presente', False)}")
        print(f"      presion_freno_loco_presente: {telem.get('presion_freno_loco_presente', False)}")
        print(f"      presion_freno_tren_presente: {telem.get('presion_freno_tren_presente', False)}")
        print(f"      presion_deposito_principal_presente: {telem.get('presion_deposito_principal_presente', False)}")
        print(f"      eq_reservoir_presente: {telem.get('eq_reservoir_presente', False)}")
        print(f"      presion_tubo_freno_mostrada_presente: {telem.get('presion_tubo_freno_mostrada_presente', False)}")
        print(f"      presion_freno_loco_mostrada_presente: {telem.get('presion_freno_loco_mostrada_presente', False)}")
        print(f"      presion_deposito_auxiliar_presente: {telem.get('presion_deposito_auxiliar_presente', False)}")
        print(f"      posicion_freno_tren_presente: {telem.get('posicion_freno_tren_presente', False)}")
        print(f"      presion_freno_tren_inferida: {telem.get('presion_freno_tren_inferida', False)}")
        print(f"      presion_freno_loco_avanzada_presente: {telem.get('presion_freno_loco_avanzada_presente', False)}")

    # Estado del sistema
    if "system_status" in datos:
        status = datos["system_status"]
        print("\n⚙️ ESTADO DEL SISTEMA:")
        print(
            f"   Simulador activo:      {'✅ SÍ' if status.get('simulator_active', False) else '❌ NO'}"
        )
        print(
            f"   TSC conectado:         {'✅ SÍ' if status.get('tsc_connected', False) else '❌ NO'}"
        )
        print(f"   Actualizaciones:       {status.get('telemetry_updates', 0)}")

    # Alertas activas
    if "active_alerts" in datos:
        alerts = datos["active_alerts"]
        print(f"\n🚨 ALERTAS ACTIVAS:      {len(alerts) if isinstance(alerts, list) else 'N/A'}")
        if isinstance(alerts, list) and len(alerts) > 0:
            for alert in alerts[:3]:  # Mostrar solo las primeras 3
                print(f"   - {alert.get('title', 'Sin título')}")


def inspeccionar_archivo_getdata():
    """Inspeccionar directamente el archivo GetData.txt."""
    ruta = r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"

    if not os.path.exists(ruta):
        print(f"\n⚠️ GetData.txt no encontrado en: {ruta}")
        return

    try:
        # Verificar última modificación
        mtime = os.path.getmtime(ruta)
        fecha_mod = datetime.fromtimestamp(mtime)
        ahora = datetime.now()
        diferencia = (ahora - fecha_mod).total_seconds()

        print("\n📄 ARCHIVO GetData.txt:")
        print(f"   Última modificación: {fecha_mod.strftime('%H:%M:%S')}")
        print(f"   Hace:                {diferencia:.1f} segundos")

        if diferencia < 1:
            print("   Estado:              ✅ ACTUALIZÁNDOSE (simulador activo)")
        elif diferencia < 5:
            print("   Estado:              ⚠️ Pausado o inactivo")
        else:
            print("   Estado:              ❌ NO se está actualizando")

        # Leer y parsear algunas líneas clave
        with open(ruta, encoding="utf-8", errors="ignore") as f:
            contenido = f.read()

        # Buscar valores clave
        valores_clave = {}
        for linea in contenido.split("\n"):
            if ":" in linea:
                partes = linea.split(":")
                if len(partes) >= 2:
                    nombre = partes[0].strip()
                    if nombre == "ControlName":
                        control_actual = partes[1].strip()
                    elif nombre == "ControlValue":
                        try:
                            valor = float(partes[1].strip())
                            if "control_actual" in locals():
                                valores_clave[control_actual] = valor
                        except:  # noqa: E722
                            pass

        print("\n   📊 Valores leídos del archivo:")
        controles_importantes = [
            "CurrentSpeed",
            "Acceleration",
            "RPM",
            "Ammeter",
            "AirBrakePipePressurePSI",
            "TractiveEffort",
        ]

        for control in controles_importantes:
            if control in valores_clave:
                print(f"      {control}: {valores_clave[control]}")

    except Exception as e:
        print(f"\n❌ Error leyendo GetData.txt: {e}")


def monitorear_continuo(intervalo=2, duracion=20):
    """Monitorear datos continuamente."""
    print("\n" + "=" * 80)
    print("🔍 MONITOREO EN TIEMPO REAL DEL DASHBOARD")
    print("=" * 80)
    print(f"\nMonitoreando cada {intervalo} segundos durante {duracion} segundos...")
    print("Presiona Ctrl+C para detener antes\n")

    tiempo_inicio = time.time()
    contador = 0

    try:
        while time.time() - tiempo_inicio < duracion:
            contador += 1
            print(f"\n--- Lectura #{contador} ---")

            # Obtener datos del dashboard
            datos = obtener_datos_debug()
            if datos:
                mostrar_datos(datos)
            else:
                print("❌ No se pudieron obtener datos del dashboard")

            # Inspeccionar archivo GetData.txt
            inspeccionar_archivo_getdata()

            print(f"\n{'='*80}")
            time.sleep(intervalo)

    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoreo detenido por el usuario")

    print(f"\n✅ Monitoreo completado. Total de lecturas: {contador}")


def main():
    """Función principal."""
    print("=" * 80)
    print("🔍 INSPECTOR DE DATOS DEL DASHBOARD")
    print("=" * 80)

    # Verificar conexión inicial
    print("\n1. Verificando conexión con el servidor...")
    datos = obtener_datos_debug()

    if datos:
        print("   ✅ Servidor respondiendo")
        mostrar_datos(datos)
    else:
        print("   ❌ No se puede conectar al servidor")
        print("\n💡 Asegúrate de que:")
        print("   1. El servidor está ejecutándose (ejecuto.bat)")
        print("   2. El servidor está en http://localhost:5000")
        input("\nPresiona Enter para salir...")
        return

    # Inspeccionar archivo GetData.txt
    print("\n2. Inspeccionando archivo GetData.txt...")
    inspeccionar_archivo_getdata()

    # Ofrecer monitoreo continuo
    print("\n" + "=" * 80)
    respuesta = input("\n¿Quieres monitorear datos en tiempo real? (s/n): ")

    if respuesta.lower() in ["s", "si", "sí", "y", "yes"]:
        monitorear_continuo(intervalo=2, duracion=20)

    print("\n" + "=" * 80)
    print("✅ Inspección completada")
    print("=" * 80)
    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
