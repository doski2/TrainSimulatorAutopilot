#!/usr/bin/env python3
"""
benchmark_rendimiento.py
Script de benchmark para comparar rendimiento de versiones optimizada vs original
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tsc_integration_optimized import TSCIntegrationOptimized


def benchmark_version_optimizada():
    """Benchmark de la versión optimizada."""
    print("🔬 BENCHMARK VERSIÓN OPTIMIZADA")
    print("-" * 40)

    tsc = TSCIntegrationOptimized()

    if not tsc.conectar():
        print("❌ No se pudo conectar")
        return None

    # Benchmark de lecturas
    tiempo_inicio = time.time()
    lecturas_totales = 0
    lecturas_exitosas = 0

    while time.time() - tiempo_inicio < 3:  # 3 segundos
        lecturas_totales += 1
        if tsc.leer_datos():
            lecturas_exitosas += 1
        time.sleep(0.005)  # 200 Hz máximo

    tiempo_total = time.time() - tiempo_inicio
    stats = tsc.obtener_estadisticas_rendimiento()

    tsc.desconectar()

    return {
        "version": "optimizada",
        "tiempo_total": tiempo_total,
        "lecturas_totales": lecturas_totales,
        "lecturas_exitosas": lecturas_exitosas,
        "frecuencia_real": lecturas_totales / tiempo_total,
        "eficiencia": (lecturas_exitosas / lecturas_totales * 100 if lecturas_totales > 0 else 0),
        "tiempo_promedio_lectura": stats["tiempo_promedio_lectura_ms"],
        "ratio_eficiencia": stats["ratio_eficiencia"],
    }


def benchmark_version_original():
    """Benchmark de la versión original."""
    print("📊 BENCHMARK VERSIÓN ORIGINAL")
    print("-" * 40)

    try:
        from tsc_integration import TSCIntegration
    except ImportError:
        print("❌ No se pudo importar versión original")
        return None

    tsc = TSCIntegration()

    # Verificar que el archivo existe
    if not tsc.archivo_existe():
        print("❌ Archivo de datos no encontrado")
        return None

    print("✅ Archivo encontrado")

    # Benchmark de lecturas
    tiempo_inicio = time.time()
    lecturas_totales = 0
    lecturas_exitosas = 0

    while time.time() - tiempo_inicio < 3:  # 3 segundos
        lecturas_totales += 1
        datos = tsc.obtener_datos_telemetria()
        if datos:
            lecturas_exitosas += 1
        time.sleep(0.1)  # 10 Hz como la versión original

    tiempo_total = time.time() - tiempo_inicio

    return {
        "version": "original",
        "tiempo_total": tiempo_total,
        "lecturas_totales": lecturas_totales,
        "lecturas_exitosas": lecturas_exitosas,
        "frecuencia_real": lecturas_totales / tiempo_total,
        "eficiencia": (lecturas_exitosas / lecturas_totales * 100 if lecturas_totales > 0 else 0),
        "tiempo_promedio_lectura": 0,  # No disponible en versión original
        "ratio_eficiencia": 0,  # No disponible en versión original
    }


def mostrar_resultados(resultados_original, resultados_optimizada):
    """Mostrar comparación de resultados."""
    print("\n" + "=" * 80)
    print("📊 COMPARACIÓN DE RENDIMIENTO")
    print("=" * 80)

    if not resultados_original or not resultados_optimizada:
        print("❌ No hay suficientes datos para comparar")
        return

    print(f"{'Versión':<12}{'Original':<12}{'Optimizada':<12}{'Unidad'}")
    print("-" * 80)

    # Función auxiliar para mostrar fila
    def mostrar_fila(label, orig, opt, unidad="", mostrar_mejora=True):
        if mostrar_mejora and orig > 0:
            mejora = ((opt - orig) / orig) * 100
            print(f"{label:<12}{orig:<12.1f}{opt:<12.1f}{mejora:+.1f}%{unidad}")
        else:
            print(f"{label:<12}{orig:<12.1f}{opt:<12.1f}{unidad}")

    mostrar_fila(
        "Frecuencia (Hz)",
        resultados_original["frecuencia_real"],
        resultados_optimizada["frecuencia_real"],
        "Hz",
    )

    mostrar_fila(
        "Eficiencia (%)",
        resultados_original["eficiencia"],
        resultados_optimizada["eficiencia"],
        "%",
    )

    mostrar_fila(
        "Lecturas exitosas",
        resultados_original["lecturas_exitosas"],
        resultados_optimizada["lecturas_exitosas"],
        "",
    )

    if resultados_optimizada["tiempo_promedio_lectura"] > 0:
        print("<12")

    if resultados_optimizada["ratio_eficiencia"] > 0:
        print("<12")

    print("\n" + "=" * 80)

    # Resumen
    mejora_freq = (
        (resultados_optimizada["frecuencia_real"] - resultados_original["frecuencia_real"])
        / resultados_original["frecuencia_real"]
    ) * 100

    print("🎯 RESUMEN DE MEJORAS:")
    print(f"   • Frecuencia de lectura: {mejora_freq:+.1f}%")
    print(
        f"   • Eficiencia: {resultados_optimizada['eficiencia']:.1f}% vs {resultados_original['eficiencia']:.1f}%"
    )
    print(
        f"   • Lecturas efectivas: {resultados_optimizada['lecturas_exitosas']} vs {resultados_original['lecturas_exitosas']}"
    )

    if mejora_freq > 50:
        print("   ✅ Optimización altamente efectiva")
    elif mejora_freq > 20:
        print("   ✅ Optimización efectiva")
    else:
        print("   ⚠️  Mejora moderada")


def main():
    """Función principal del benchmark."""
    print("🚂 TRAIN SIMULATOR AUTOPILOT - BENCHMARK DE RENDIMIENTO")
    print("=" * 80)
    print("Comparando versiones: Original vs Optimizada")
    print("Duración de prueba: 3 segundos por versión")
    print("=" * 80)

    # Ejecutar benchmarks
    resultados_original = benchmark_version_original()
    print()
    resultados_optimizada = benchmark_version_optimizada()

    # Mostrar resultados
    if resultados_original and resultados_optimizada:
        mostrar_resultados(resultados_original, resultados_optimizada)
    else:
        print("❌ Error en los benchmarks")

    print("\n" + "=" * 80)
    print("✅ BENCHMARK COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    main()
