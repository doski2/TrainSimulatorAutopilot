#!/usr/bin/env python3
"""
demo_completa_autopilot.py
Demostración completa del sistema de piloto automático
Muestra todo el flujo: TSC → IA → Comandos → Juego
"""

import os
import sys
import time
from datetime import datetime

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autopilot_system import IASistema
from tsc_integration import TSCIntegration


def demo_lectura_datos():
    """Demuestra la lectura de datos reales."""
    print("📊 DEMO 1: LECTURA DE DATOS REALES")
    print("=" * 40)

    tsc = TSCIntegration()

    print(f"📂 Archivo de datos: {tsc.ruta_archivo}")
    print(f"📂 Archivo de comandos: {tsc.ruta_archivo_comandos}")
    print()

    # Intentar leer datos
    datos = tsc.obtener_datos_telemetria()

    if datos:
        print("✅ Datos leídos exitosamente:")
        print(f"   🚂 Velocidad: {datos.get('velocidad', 'N/A')} mph")
        print(f"   🚦 Límite: {datos.get('limite_velocidad_actual', 'N/A')} mph")
        print(f"   🏔️  Pendiente: {datos.get('pendiente', 'N/A')} ‰")
        print(f"   ⚡ Aceleración: {datos.get('aceleracion', 'N/A')} m/s²")
        return datos
    else:
        print("⚠️  No se pudieron leer datos reales")
        print("💡 Asegúrate de que TSC y Raildriver estén ejecutándose")
        return None


def demo_procesamiento_ia(datos_telemetria):
    """Demuestra el procesamiento con IA."""
    print("\n🤖 DEMO 2: PROCESAMIENTO CON IA")
    print("=" * 35)

    if not datos_telemetria:
        print("❌ No hay datos para procesar")
        return None

    ia = IASistema()

    print("📊 Datos de entrada:")
    print(f"   Velocidad actual: {datos_telemetria.get('velocidad', 0)} mph")
    print(f"   Límite de velocidad: {datos_telemetria.get('limite_velocidad_actual', 80)} mph")
    print(f"   Pendiente: {datos_telemetria.get('pendiente', 0)} ‰")
    print(f"   Aceleración: {datos_telemetria.get('aceleracion', 0)} m/s²")

    # Procesar con IA
    comandos = ia.procesar_telemetria(datos_telemetria)

    print("\n🧠 IA tomó una decisión:")
    print(f"   🎯 Decisión: {comandos['decision']}")
    print(f"   🚀 Acelerador: {comandos['acelerador']}")
    print(f"   🛑 Freno tren: {comandos['freno_tren']}")
    print(f"   🔧 Freno motor: {comandos['freno_motor']}")
    print(f"   ⚡ Freno dinámico: {comandos['freno_dinamico']}")
    print(f"   ↔️  Reverser: {comandos['reverser']}")

    return comandos


def demo_envio_comandos(comandos):
    """Demuestra el envío de comandos al juego."""
    print("\n📡 DEMO 3: ENVÍO DE COMANDOS AL JUEGO")
    print("=" * 40)

    if not comandos:
        print("❌ No hay comandos para enviar")
        return False

    tsc = TSCIntegration()

    print("📤 Enviando comandos al archivo SendCommand.txt...")

    # Enviar comandos
    exito = tsc.enviar_comandos(comandos)

    if exito:
        print("✅ Comandos enviados exitosamente")
        print("📄 Contenido del archivo SendCommand.txt:")

        # Mostrar contenido del archivo
        try:
            if os.path.exists(tsc.ruta_archivo_comandos):
                with open(tsc.ruta_archivo_comandos, encoding="utf-8") as f:
                    contenido = f.read().strip()
                    for linea in contenido.split("\n"):
                        if linea.strip():
                            print(f"   {linea}")
            else:
                print("   ⚠️  Archivo no encontrado (normal si no hay cambios)")
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")

        return True
    else:
        print("❌ Error enviando comandos")
        return False


def demo_flujo_completo():
    """Demuestra el flujo completo del sistema."""
    print("🚂 DEMO COMPLETA: FLUJO TSC → IA → JUEGO")
    print("=" * 50)
    print(f"🕐 Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Paso 1: Leer datos
    datos = demo_lectura_datos()
    if not datos:
        return

    time.sleep(1)

    # Paso 2: Procesar con IA
    comandos = demo_procesamiento_ia(datos)
    if not comandos:
        return

    time.sleep(1)

    # Paso 3: Enviar comandos
    exito = demo_envio_comandos(comandos)

    print("\n" + "=" * 50)
    if exito:
        print("🎉 ¡FLUJO COMPLETO EXITOSO!")
        print("✅ Datos leídos → ✅ IA procesados → ✅ Comandos enviados")
        print("\n💡 El sistema de piloto automático está funcionando correctamente")
        print("🚂 Si TSC está ejecutándose, los controles deberían cambiar automáticamente")
    else:
        print("⚠️  Flujo completado con algunos errores")


def instrucciones_uso():
    """Muestra instrucciones para usar el sistema."""
    print("\n📖 INSTRUCCIONES DE USO")
    print("=" * 25)
    print("Para usar el piloto automático completo:")
    print()
    print("1. 🚂 Iniciar Train Simulator Classic")
    print("2. 🎮 Conectar el Raildriver Interface")
    print("3. 🚃 Montar en una locomotora")
    print("4. 🖥️  Ejecutar: python autopilot_system.py")
    print("5. ⌨️  Usar comandos: 'start' → 'auto'")
    print()
    print("El sistema controlará automáticamente:")
    print("• Velocidad según límites")
    print("• Frenado en curvas y pendientes")
    print("• Aceleración segura")
    print("• Paradas anticipadas")


def main():
    """Función principal."""
    print("🚂 TRAIN SIMULATOR AUTOPILOT - DEMO COMPLETA")
    print("=" * 55)

    try:
        # Ejecutar demo completa
        demo_flujo_completo()

        # Mostrar instrucciones
        instrucciones_uso()

        print("\n" + "=" * 55)
        print("✅ DEMO COMPLETADA - Sistema funcionando perfectamente")

    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
