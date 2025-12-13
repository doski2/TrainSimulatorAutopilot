# performance_test.py
# Script para medir y optimizar rendimiento de la IA

import os
import time

import psutil
from ia_logic import decidir_accion


def medir_rendimiento(func, *args, iteraciones=1000):
    """
    Mide tiempo de ejecución y uso de memoria de una función.
    """
    tiempos = []
    memoria_inicial = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

    for _ in range(iteraciones):
        inicio = time.perf_counter()
        func(*args)
        fin = time.perf_counter()
        tiempos.append(fin - inicio)

    memoria_final = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
    uso_memoria = memoria_final - memoria_inicial

    tiempo_promedio = sum(tiempos) / len(tiempos)
    tiempo_total = sum(tiempos)

    return {
        "tiempo_promedio": tiempo_promedio,
        "tiempo_total": tiempo_total,
        "uso_memoria": uso_memoria,
        "iteraciones": iteraciones,
    }


def test_rendimiento_ia():
    """
    Prueba rendimiento de la lógica IA con datos simulados.
    """
    datos_telemetria = {
        "velocidad": 75,
        "acelerador": 0.5,
        "freno": 0.1,
        "presion": 120,
        "distancia_parada": 20,
        "fecha_hora": "2025-11-09T12:00:00",
    }

    print("Midiendo rendimiento de decidir_accion...")
    metricas = medir_rendimiento(decidir_accion, datos_telemetria, 80, 10, 5)

    print(f"Tiempo promedio por decisión: {metricas['tiempo_promedio']*1000:.2f} ms")
    print(f"Tiempo total ({metricas['iteraciones']} iteraciones): {metricas['tiempo_total']:.2f} s")
    print(f"Uso de memoria: {metricas['uso_memoria']:.2f} MB")

    # Verificar que las métricas son razonables
    assert metricas["tiempo_promedio"] >= 0
    assert metricas["tiempo_promedio"] < 1.0  # Debe ser menos de 1 segundo
    assert metricas["uso_memoria"] >= 0
    assert metricas["iteraciones"] == 1000  # Valor por defecto de la función


def procesar_decision(args):
    datos, objetivo, limite, pendiente = args
    return decidir_accion(datos, objetivo, limite, pendiente)


def optimizar_con_multiprocessing():
    """
    Implementa procesamiento paralelo para múltiples decisiones IA.
    """
    import concurrent.futures

    # Datos simulados para múltiples trenes/escenarios
    datos_multiples = [
        ({"velocidad": 70, "distancia_parada": 15}, 80, 10, 0),
        ({"velocidad": 90, "distancia_parada": 25}, 80, 10, 10),
        ({"velocidad": 60, "distancia_parada": 5}, 80, 10, -5),
    ]

    print("\nMidiendo rendimiento con threading...")
    inicio = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        resultados = list(executor.map(procesar_decision, datos_multiples))

    fin = time.time()
    tiempo_paralelo = fin - inicio

    print(f"Tiempo con threading: {tiempo_paralelo:.4f} s")
    print(f"Resultados: {len(resultados)} decisiones procesadas")

    return tiempo_paralelo


if __name__ == "__main__":
    # Instalar psutil si no está
    try:
        import psutil
    except ImportError:
        print("Instalando psutil...")
        # Nota: Instalar manualmente psutil antes de ejecutar
        print("Ejecutar: pip install psutil")
        import psutil

    metricas = test_rendimiento_ia()
    tiempo_paralelo = optimizar_con_multiprocessing()

    print("\nOptimización completada.")
    print("Mejora potencial: Procesamiento paralelo reduce tiempo para múltiples decisiones.")
