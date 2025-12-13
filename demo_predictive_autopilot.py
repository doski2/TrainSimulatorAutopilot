#!/usr/bin/env python3
"""
demo_predictive_autopilot.py
Demostración completa del sistema de análisis predictivo de telemetría
Muestra cómo el piloto automático usa machine learning para tomar decisiones inteligentes
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predictive_telemetry_analysis import (
    PredictiveAutopilotController,
    PredictiveTelemetryAnalyzer,
)
from tsc_integration import TSCIntegration


def demo_analisis_predictivo():
    """Demostración del análisis predictivo puro."""
    print("🧠 TRAIN SIMULATOR AUTOPILOT - DEMO ANÁLISIS PREDICTIVO")
    print("=" * 70)
    print("Esta demo muestra el sistema de machine learning para predicciones")
    print("Se generarán datos simulados y se entrenará un modelo predictivo")
    print("=" * 70)

    # Crear analizador predictivo
    analyzer = PredictiveTelemetryAnalyzer(lookback_steps=5)

    print("📊 GENERANDO DATOS DE ENTRENAMIENTO SIMULADOS...")
    print("-" * 50)

    # Generar datos simulados de conducción realista
    import numpy as np

    np.random.seed(42)

    velocidad_base = 40.0
    pendiente_actual = 0.0
    limite_velocidad = 160.0

    for i in range(100):
        # Simular conducción realista
        if i < 20:  # Aceleración inicial
            velocidad_base = min(velocidad_base + 2.0, limite_velocidad * 0.7)
            pendiente_actual = np.random.normal(0, 1)
        elif i < 60:  # Velocidad de crucero
            velocidad_base = limite_velocidad * 0.75 + np.random.normal(0, 2)
            pendiente_actual = np.random.normal(0, 0.5)
        elif i < 80:  # Subida pronunciada
            velocidad_base = max(velocidad_base - 1.5, 20)
            pendiente_actual = np.random.normal(3, 0.5)
        else:  # Bajada y frenado
            velocidad_base = max(velocidad_base - 2.0, 15)
            pendiente_actual = np.random.normal(-2, 0.5)

        # Crear muestra de telemetría
        sample = {
            "velocidad_actual": velocidad_base + np.random.normal(0, 1),
            "acelerador": max(0, min(1, 0.5 + pendiente_actual * 0.1 + np.random.normal(0, 0.1))),
            "freno_tren": max(0, min(1, np.random.normal(0, 0.05))),
            "freno_motor": 0.0,
            "pendiente": pendiente_actual,
            "limite_velocidad": limite_velocidad,
            "radio_curva": 800 + np.random.normal(0, 100),
            "senal_principal": 1,
            "senal_avanzada": np.random.choice([0, 1], p=[0.8, 0.2]),
        }

        analyzer.add_telemetry_sample(sample)

        if i % 20 == 0:
            print(f"✅ Muestra {i+1}/100 agregada - Vel: {sample['velocidad_actual']:.1f}")

    print("\n🏋️  ENTRENANDO MODELO PREDICTIVO...")
    print("-" * 50)

    # Entrenar modelo
    metrics = analyzer.train_model()

    if "error" in metrics:
        print(f"❌ Error entrenando modelo: {metrics['error']}")
        return

    print("✅ Modelo entrenado exitosamente")
    print(f"   MAE: {metrics['mae']:.3f}")
    print(f"   MSE: {metrics['mse']:.3f}")
    print(f"   RMSE: {metrics['rmse']:.3f}")
    print(f"   Muestras usadas: {metrics['samples_train'] + metrics['samples_test']}")

    print("\n🔮 GENERANDO PREDICCIONES EN TIEMPO REAL...")
    print("-" * 50)

    # Iniciar análisis predictivo
    analyzer.start_analysis()

    # Agregar algunas muestras más recientes para predicción
    print("📥 Agregando datos recientes para predicción...")

    for i in range(10):  # noqa: B007
        sample = {
            "velocidad_actual": 55.0 + np.random.normal(0, 2),
            "acelerador": 0.6 + np.random.normal(0, 0.1),
            "freno_tren": np.random.normal(0, 0.05),
            "freno_motor": 0.0,
            "pendiente": np.random.normal(0, 1),
            "limite_velocidad": 160.0,
            "radio_curva": 900 + np.random.normal(0, 50),
            "senal_principal": 1,
            "senal_avanzada": 0,
        }
        analyzer.add_telemetry_sample(sample)
        time.sleep(0.2)

    # Esperar a que se generen predicciones
    time.sleep(2)

    # Obtener predicciones
    predictions = analyzer.get_current_predictions()

    if predictions:
        print("🎯 PREDICCIONES GENERADAS:")
        print(f"   Velocidad: {predictions.get('velocidad_actual', 0):.3f}")
        print(f"   Acelerador: {predictions.get('acelerador', 0):.3f}")
        print(f"   Freno: {predictions.get('freno_tren', 0):.3f}")
        print(f"   Pendiente: {predictions.get('pendiente', 0):.3f}")
        print(f"   Límite vel: {predictions.get('limite_velocidad', 160):.3f}")
        print(f"   Radio curva: {predictions.get('radio_curva', 1000):.3f}")
        print(f"   Señal principal: {predictions.get('senal_principal', 0)}")
        print(f"   Señal avanzada: {predictions.get('senal_avanzada', 0)}")
    else:
        print("⚠️  No se generaron predicciones")

    # Detener análisis
    analyzer.stop_analysis()

    print("\n📈 ANÁLISIS DE RENDIMIENTO PREDICTIVO")
    print("-" * 50)

    # Mostrar estadísticas del sistema
    status = analyzer.get_system_status()
    print("📊 Estadísticas del sistema:")
    print(f"   Modelo entrenado: {status['model_trained']}")
    print(f"   Análisis activo: {status['is_running']}")
    print(f"   Muestras totales: {status['data_collector_stats']['total_samples']}")
    print(f"   Ventana de lookback: {status['lookback_steps']} pasos")
    print(f"   Horizonte predictivo: {status['prediction_horizon']} pasos")

    print("\n✅ DEMO DE ANÁLISIS PREDICTIVO COMPLETADA")
    print("El sistema puede predecir el comportamiento futuro del tren")
    print("usando machine learning basado en datos históricos.")


def demo_control_predictivo():
    """Demostración del control automático con predicciones."""
    print("🎮 DEMO CONTROL PREDICTIVO AUTOMÁTICO")
    print("=" * 50)
    print("Esta demo muestra cómo el piloto automático usa predicciones")
    print("para tomar decisiones más inteligentes de conducción.")
    print("=" * 50)

    # Crear componentes
    tsc = TSCIntegration()
    controller = PredictiveAutopilotController(tsc)

    print("🔧 CONFIGURACIÓN DEL CONTROLADOR:")
    print(f"   Peso de predicciones: {controller.prediction_weight}")
    print(f"   Margen de seguridad: {controller.safety_margin}")

    # Nota: El control completo requiere TSC ejecutándose
    print("\n⚠️  CONTROL PREDICTIVO AVANZADO")
    print("Para ver el control predictivo completo:")
    print("1. 🚂 Iniciar Train Simulator Classic")
    print("2. 🎮 Cargar un escenario con señales y límites")
    print("3. 🖥️  Ejecutar el piloto automático con predicciones")
    print("4. 👀 Observar cómo anticipa curvas y cambios de velocidad")

    print("\n🎯 VENTAJAS DEL CONTROL PREDICTIVO:")
    print("• Anticipa cambios en la vía antes de que ocurran")
    print("• Ajusta velocidad preventivamente en curvas")
    print("• Optimiza consumo de energía con predicciones")
    print("• Reduce frenados de emergencia")
    print("• Mejora seguridad y comodidad de conducción")

    print("\n✅ DEMO DE CONTROL PREDICTIVO COMPLETADA")
    print("El sistema está listo para control predictivo avanzado.")


def instrucciones_uso_predictivo():
    """Mostrar instrucciones completas de uso del sistema predictivo."""
    print("\n📖 GUÍA COMPLETA - SISTEMA DE ANÁLISIS PREDICTIVO")
    print("=" * 60)
    print("Para usar el análisis predictivo en producción:")
    print()
    print("1. 📊 RECOPILACIÓN DE DATOS:")
    print("   • Ejecutar TSC con escenarios variados")
    print("   • El sistema recopila automáticamente telemetría")
    print("   • Datos se guardan en data/telemetry_history.json")
    print()
    print("2. 🏋️  ENTRENAMIENTO DE MODELOS:")
    print("   • Ejecutar scripts/test_predictive_telemetry.py")
    print("   • Modelos se entrenan automáticamente")
    print("   • Se guardan en data/predictive_model.pkl")
    print()
    print("3. 🔮 PREDICCIONES EN TIEMPO REAL:")
    print("   • Iniciar PredictiveTelemetryAnalyzer()")
    print("   • Llamar start_analysis() para predicciones continuas")
    print("   • Obtener predicciones con get_current_predictions()")
    print()
    print("4. 🎮 CONTROL PREDICTIVO:")
    print("   • Usar PredictiveAutopilotController()")
    print("   • start_predictive_control() para control inteligente")
    print("   • Decisiones basadas en predicciones futuras")
    print()
    print("5. 📈 MONITOREO Y OPTIMIZACIÓN:")
    print("   • Revisar métricas MAE, MSE, RMSE")
    print("   • Reentrenar modelos periódicamente")
    print("   • Ajustar parámetros según rendimiento")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_analisis_predictivo()
        print("\n" + "=" * 70)
        demo_control_predictivo()
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        import traceback

        traceback.print_exc()

    instrucciones_uso_predictivo()
