#!/usr/bin/env python3
"""
demo_multi_locomotive.py
Demostración completa del sistema multi-locomotora
Muestra cómo detectar, monitorear y controlar múltiples locomotoras
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_locomotive_integration import MultiLocomotiveIntegration


def demo_multi_locomotora():
    """Demostración completa del sistema multi-locomotora."""
    print("🚂 TRAIN SIMULATOR AUTOPILOT - DEMO MULTI-LOCOTORA")
    print("=" * 65)
    print("Esta demo muestra el soporte para múltiples locomotoras")
    print("Inicie Train Simulator Classic con múltiples locomotoras para ver")
    print("la funcionalidad completa.")
    print("=" * 65)

    # Crear sistema multi-locomotora
    multi_loco = MultiLocomotiveIntegration()

    if not multi_loco.conectar():
        print("❌ No se pudo conectar al sistema TSC")
        print("Asegúrese de que Train Simulator Classic esté ejecutándose")
        return

    print("✅ Sistema multi-locomotora conectado")
    print("\n🔍 ESCANEANDO LOCOMOTORAS...")
    print("-" * 40)

    # Escanear locomotoras durante 10 segundos
    tiempo_inicio = time.time()
    locomotoras_encontradas = set()

    while time.time() - tiempo_inicio < 10:
        datos = multi_loco.leer_datos_todas_locomotoras()

        for loco_id in datos.keys():
            if loco_id not in locomotoras_encontradas:
                locomotoras_encontradas.add(loco_id)
                estado = datos[loco_id]
                velocidad = estado.get("velocidad_actual", 0)
                limite = estado.get("limite_velocidad", 160)
                print(f"🆕 ¡Locomotora detectada: {loco_id}!")
                print(f"   Velocidad: {velocidad:.1f} mph")
                print(f"   Límite: {limite:.1f} mph")
                print("   Estado: Activa")
                print()

        time.sleep(0.5)

    if not locomotoras_encontradas:
        print("⚠️  No se detectaron locomotoras activas")
        print("   Asegúrese de que TSC esté ejecutándose y tenga locomotoras")
        print("   en el escenario actual.")
        multi_loco.desconectar()
        return

    print(f"✅ ESCANEO COMPLETADO - {len(locomotoras_encontradas)} locomotora(s) encontrada(s)")
    print("\n🎯 SELECCIÓN DE LOCOMOTORA ACTIVA")
    print("-" * 40)

    # Seleccionar la primera locomotora encontrada
    loco_activa = list(locomotoras_encontradas)[0]
    print(f"Seleccionando locomotora: {loco_activa}")

    if multi_loco.seleccionar_locomotora_activa(loco_activa):
        print(f"✅ Locomotora {loco_activa} seleccionada como activa")
        print("   Esta locomotora será controlada por el piloto automático")
    else:
        print(f"❌ Error seleccionando locomotora {loco_activa}")

    print("\n🚂 CONTROL AUTOMÁTICO MULTI-LOCOTORA")
    print("-" * 45)

    # Simular control automático durante 15 segundos
    print("Iniciando control automático por 15 segundos...")
    print("El sistema controlará la locomotora seleccionada")
    print()

    tiempo_inicio_control = time.time()
    comandos_enviados = 0

    while time.time() - tiempo_inicio_control < 15:
        # Leer estado de todas las locomotoras
        datos_todas = multi_loco.leer_datos_todas_locomotoras()

        if loco_activa in datos_todas:
            estado = datos_todas[loco_activa]
            velocidad = estado.get("velocidad_actual", 0)
            limite = estado.get("limite_velocidad", 160)

            # Lógica simple de control automático
            if velocidad < limite * 0.8:  # Si va por debajo del 80% del límite
                acelerador = 0.6  # Acelerar
                freno_tren = 0.0
                decision = "ACELERANDO"
            elif velocidad > limite * 0.95:  # Si está cerca del límite
                acelerador = 0.0  # Mantener velocidad
                freno_tren = 0.1  # Frenar ligeramente
                decision = "MANTENIENDO"
            else:
                acelerador = 0.3  # Velocidad de crucero
                freno_tren = 0.0
                decision = "CRUCERO"

            # Enviar comandos
            comandos = {
                "acelerador": acelerador,
                "freno_tren": freno_tren,
                "freno_motor": 0.0,
                "reverser": 1.0,
            }

            if multi_loco.enviar_comandos_locomotora(loco_activa, comandos):
                comandos_enviados += 1
                print(
                    f"📡 {loco_activa}: {decision} | "
                    f"Vel: {velocidad:.1f}/{limite:.1f} mph | "
                    f"Ac: {acelerador:.1f} | Fr: {freno_tren:.1f}"
                )
            else:
                print(f"❌ Error enviando comandos a {loco_activa}")
        else:
            print(f"⚠️  Locomotora {loco_activa} no disponible")

        time.sleep(1.0)  # Actualización cada segundo

    print("\n📊 RESUMEN DE LA DEMO MULTI-LOCOTORA")
    print("=" * 50)
    print(f"⏱️  Duración: {time.time() - tiempo_inicio:.1f} segundos")
    print(f"🚂 Locomotoras detectadas: {len(locomotoras_encontradas)}")
    print(f"🎯 Locomotora controlada: {loco_activa}")
    print(f"📡 Comandos enviados: {comandos_enviados}")

    # Estadísticas finales
    estadisticas = multi_loco.obtener_estadisticas_multi_locomotora()
    print("\n📈 ESTADÍSTICAS FINALES:")
    print(f"   Lecturas totales: {estadisticas['lecturas_totales']}")
    print(f"   Locomotoras activas: {estadisticas['locomotoras_activas']}")
    print(f"   Tiempo de conexión: {estadisticas['tiempo_total_segundos']:.1f}s")

    print("\n✅ DEMO MULTI-LOCOTORA COMPLETADA")
    print("El sistema puede detectar y controlar múltiples locomotoras")
    print("en escenarios complejos de Train Simulator Classic.")

    multi_loco.desconectar()


def instrucciones_uso():
    """Mostrar instrucciones de uso del sistema multi-locomotora."""
    print("\n📖 INSTRUCCIONES DE USO - SISTEMA MULTI-LOCOTORA")
    print("=" * 55)
    print("Para usar el sistema multi-locomotora:")
    print()
    print("1. 🚂 Iniciar Train Simulator Classic")
    print("2. 🎮 Cargar un escenario con múltiples locomotoras")
    print("3. 🖥️  Ejecutar: python demo_multi_locomotive.py")
    print("4. 👀 Observar cómo el sistema detecta locomotoras")
    print("5. 🎯 Ver cómo selecciona y controla una locomotora")
    print()
    print("Para desarrollo personalizado:")
    print("• Usar MultiLocomotiveIntegration() para instanciar")
    print("• Llamar conectar() para inicializar")
    print("• Usar leer_datos_todas_locomotoras() para obtener datos")
    print("• Usar seleccionar_locomotora_activa(id) para elegir control")
    print("• Usar enviar_comandos_locomotora(id, comandos) para controlar")
    print("=" * 55)


if __name__ == "__main__":
    try:
        demo_multi_locomotora()
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")

    instrucciones_uso()
