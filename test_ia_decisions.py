#!/usr/bin/env python3
"""
test_ia_decisions.py
Probar decisiones de IA con diferentes situaciones
"""

from autopilot_system import IASistema


def main():
    ia = IASistema()

    # Simular diferentes situaciones
    situaciones = [
        {
            "velocidad": 0,
            "limite_velocidad_actual": 50,
            "pendiente": -0.01,
            "aceleracion": 0,
            "distancia_parada": 1000,
        },
        {
            "velocidad": 60,
            "limite_velocidad_actual": 50,
            "pendiente": 0.02,
            "aceleracion": 0.5,
            "distancia_parada": 500,
        },
        {
            "velocidad": 45,
            "limite_velocidad_actual": 50,
            "pendiente": 0.02,
            "aceleracion": -0.2,
            "distancia_parada": 200,
        },
        {
            "velocidad": 25,
            "limite_velocidad_actual": 30,
            "pendiente": 0.05,
            "aceleracion": 0.1,
            "distancia_parada": 100,
        },
    ]

    print("🧠 PRUEBA DE DECISIONES DE IA")
    print("=" * 50)

    for i, datos in enumerate(situaciones, 1):
        print(f"\n🎯 Situación {i}:")
        print(
            f'   🚗 Velocidad: {datos["velocidad"]} mph, Límite: {datos["limite_velocidad_actual"]} mph'
        )
        print(f'   🏔️  Pendiente: {datos["pendiente"]}, Aceleración: {datos["aceleracion"]}')
        print(f'   📍 Distancia parada: {datos["distancia_parada"]}m')

        decision = ia.procesar_telemetria(datos)
        print(f'   🤖 Decisión IA: {decision["decision"]}')
        print(f'   ⚡ Acelerador: {decision["acelerador"]:.1f}')
        print(f'   🛑 Freno tren: {decision["freno_tren"]:.1f}')
        print(f'   🔧 Freno motor: {decision["freno_motor"]:.1f}')
        print(f'   ⚡ Freno dinámico: {decision["freno_dinamico"]:.1f}')

        # Mostrar comandos que se enviarían
        comandos_enviados = []
        if decision["acelerador"] > 0:
            comandos_enviados.append(f"VirtualThrottle:{decision['acelerador']:.1f}")
        if decision["freno_tren"] > 0:
            comandos_enviados.append(f"TrainBrakeControl:{decision['freno_tren']:.1f}")
        if decision["freno_motor"] > 0:
            comandos_enviados.append(f"EngineBrakeControl:{decision['freno_motor']:.1f}")
        if decision["freno_dinamico"] > 0:
            comandos_enviados.append(f"VirtualEngineBrakeControl:{decision['freno_dinamico']:.1f}")

        if comandos_enviados:
            print(f'   📡 Comandos: {", ".join(comandos_enviados)}')
        else:
            print("   📡 Comandos: Mantener estado actual")


if __name__ == "__main__":
    main()
