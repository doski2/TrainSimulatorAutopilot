# monitoreo_auto_tsc.py
# Monitoreo automático y ejecución de pruebas cuando TSC esté disponible

import os
import socket
import subprocess
import sys
import time


def verificar_conexion_tsc(max_intentos=60, intervalo=5):
    """Verifica conexión con TSC hasta que esté disponible."""
    print("🔍 Monitoreando conexión con TSC...")
    print(f"   Intentos máximos: {max_intentos} (cada {intervalo}s)")

    for intento in range(max_intentos):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(("localhost", 15678))  # Puerto Raildriver
            sock.close()

            if result == 0:
                print(f"\n✅ ¡TSC conectado exitosamente! (Intento {intento + 1})")
                return True

        except Exception:
            pass  # Ignorar errores temporales

        # Mostrar progreso cada 10 intentos
        if (intento + 1) % 10 == 0:
            tiempo_transcurrido = (intento + 1) * intervalo
            print(f"   Intento {intento + 1}/{max_intentos} - Tiempo: {tiempo_transcurrido}s")

        time.sleep(intervalo)

    print(f"\n⏰ Timeout agotado después de {max_intentos * intervalo} segundos")
    return False


def ejecutar_pruebas_automaticas():
    """Ejecuta las pruebas reales automáticamente."""
    print("\n🚀 Iniciando pruebas automáticas de conducción IA...")

    try:
        # Ejecutar script de pruebas reales
        result = subprocess.run(
            [sys.executable, "test_tsc_real.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            input="s\n",
        )

        print("📊 Resultados de las pruebas:")
        print(result.stdout)

        if result.stderr:
            print("⚠️ Errores durante las pruebas:")
            print(result.stderr)

        if result.returncode == 0:
            print("\n✅ ¡Pruebas completadas exitosamente!")
            return True
        else:
            print(f"\n❌ Pruebas fallaron con código {result.returncode}")
            return False

    except Exception as e:
        print(f"\n❌ Error ejecutando pruebas: {e}")
        return False


def mostrar_instrucciones():
    """Muestra instrucciones para el usuario."""
    print(
        """
🚂 MONITOREO AUTOMÁTICO DE TSC

Este script esperará automáticamente hasta que Train Simulator Classic esté disponible.

INSTRUCCIONES:
1. ✅ Steam ya debería estar ejecutándose TSC
2. ✅ Raildriver interface ya debería estar ejecutándose
3. ⏳ El script esperará hasta 5 minutos por la conexión
4. 🎯 Una vez conectado, ejecutará las pruebas automáticamente

Si TSC no se conecta automáticamente:
- Verifica que TSC esté completamente cargado (no en menú principal)
- Asegúrate de que Raildriver muestre "Connected to RailWorks"
- El script se detendrá automáticamente si no hay conexión

Presiona Ctrl+C para cancelar en cualquier momento.
    """
    )


def main():
    """Función principal del monitoreo automático."""
    print("🚂 TRAIN SIMULATOR AUTOPILOT - MONITOREO AUTOMÁTICO")
    print("=" * 60)

    mostrar_instrucciones()

    # Verificar si ya está conectado
    if verificar_conexion_tsc(max_intentos=1, intervalo=1):
        print("🎉 TSC ya está conectado. Ejecutando pruebas inmediatamente...")
        exito = ejecutar_pruebas_automaticas()
    else:
        print("\n⏳ Esperando conexión con TSC...")
        print("   (Asegúrate de que TSC esté ejecutándose y Raildriver esté conectado)")

        # Monitorear hasta que esté disponible
        if verificar_conexion_tsc():
            exito = ejecutar_pruebas_automaticas()
        else:
            print("\n❌ No se pudo establecer conexión con TSC")
            print("💡 Verifica que TSC esté ejecutándose correctamente")
            exito = False

    # Resultado final
    print("\n" + "=" * 60)
    if exito:
        print("🎉 ¡INTEGRACIÓN COMPLETA EXITOSA!")
        print("   El sistema IA está listo para uso productivo")
    else:
        print("⚠️ INTEGRACIÓN INCOMPLETA")
        print("   Revisa las instrucciones y vuelve a intentar")

    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoreo cancelado por usuario")
        print("Para ejecutar manualmente: python test_tsc_real.py")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("Para ejecutar manualmente: python verificar_conexion_tsc.py")
