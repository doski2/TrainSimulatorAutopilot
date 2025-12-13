# demo_senalizacion_europea.py
# Demostración del sistema de señalización europea

import json

from sistemas_senalizacion_europea import GestorSenalizacionEuropea


def main():
    print("=== DEMO: SISTEMAS DE SEÑALIZACIÓN EUROPEA ===")
    print()

    # Crear gestor
    gestor = GestorSenalizacionEuropea()

    print("1. Configuración para ruta alemana (PZB + LZB):")
    gestor.configurar_ruta("alemania", ["pzb", "lzb"])
    print(f"Sistemas activos: {list(gestor.sistemas_activos.keys())}")
    print()

    print("2. Simulación de baliza PZB FAHRT (velocidad máxima 100 km/h):")
    datos_via = {
        "baliza_pzb": {"tipo": "FAHRT", "velocidad_maxima": 100},
        "datos_lzb": {"velocidad_maxima": 120},
    }
    gestor.actualizar_datos_via(datos_via)

    # Procesar con velocidad normal
    datos_tren = {"velocidad": 90}
    comandos = gestor.procesar_datos_tren(datos_tren)
    print(f'Velocidad: {datos_tren["velocidad"]} km/h')
    print(
        f'Comandos: Velocidad máxima={comandos["velocidad_maxima"]}, Advertencia sonora={comandos["advertencia_sonora"]}'
    )
    print()

    print("3. Simulación de exceso de velocidad (110 km/h):")
    datos_tren = {"velocidad": 110}
    comandos = gestor.procesar_datos_tren(datos_tren)
    print(f'Velocidad: {datos_tren["velocidad"]} km/h')
    print(
        f'Comandos: Ajuste velocidad={comandos["ajuste_velocidad"]}, Advertencia visual={comandos["advertencia_visual"]}'
    )
    print()

    print("4. Cambio a ruta británica (AWS + TPWS):")
    gestor.reset_sistemas()
    gestor.configurar_ruta("reino_unido", ["aws", "tpws"])
    print(f"Sistemas activos: {[k for k, v in gestor.sistemas_activos.items() if v]}")
    print()

    print("5. Simulación de señal AWS amarilla:")
    datos_via = {
        "senal_aws": "amarillo",
        "restriccion_tpws": {"velocidad_maxima": 50, "distancia": 500},
    }
    gestor.actualizar_datos_via(datos_via)

    datos_tren = {"velocidad": 60}
    comandos = gestor.procesar_datos_tren(datos_tren)
    print(f'Velocidad: {datos_tren["velocidad"]} km/h')
    print(
        f'Comandos: Velocidad máxima={comandos["velocidad_maxima"]}, Advertencia sonora={comandos["advertencia_sonora"]}'
    )
    print()

    print("6. Confirmación del conductor:")
    gestor.confirmar_conductor()
    comandos = gestor.procesar_datos_tren(datos_tren)
    print(f'Después de confirmación: Advertencia sonora={comandos["advertencia_sonora"]}')
    print()

    print("=== ESTADO FINAL DE SISTEMAS ===")
    estado = gestor.obtener_estado_completo()
    print(
        json.dumps(
            {
                "normativa": estado["normativa_actual"],
                "sistemas_activos": estado["sistemas_activos"],
                "aws_estado": estado["aws"]["estado"] if estado["aws"] else None,
                "tpws_estado": estado["tpws"]["estado"] if estado["tpws"] else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
