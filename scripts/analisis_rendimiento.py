# analisis_rendimiento.py
# Análisis detallado del rendimiento de la IA

import json
from datetime import datetime

import numpy as np


def cargar_datos_pruebas():
    """Carga los datos de las pruebas de conducción."""
    try:
        with open("resultados_pruebas_conduccion.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de resultados de pruebas")
        return None


def cargar_historial_autonomo():
    """Carga el historial del modo autónomo."""
    try:
        with open("prueba_autonomo_historial.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de historial autónomo")
        return None


def analizar_aceleracion(datos):
    """Analiza el comportamiento de aceleración."""
    print("\n🚀 Análisis de Aceleración:")

    aceleraciones = datos["aceleracion"]
    velocidades = [r["velocidad_inicial"] for r in aceleraciones]
    aceleradores = [r["decision"]["acelerador"] for r in aceleraciones]

    # Calcular estadísticas
    prom_acelerador = np.mean(aceleradores)
    max_acelerador = max(aceleradores)
    min_acelerador = min(aceleradores)

    print(f"   - Promedio acelerador: {prom_acelerador:.3f}")
    print(f"   - Máximo acelerador: {max_acelerador:.3f}")
    print(f"   - Mínimo acelerador: {min_acelerador:.3f}")

    # Verificar lógica: acelerar cuando velocidad < objetivo (75 km/h)
    correctas = sum(
        1
        for v, a in zip(velocidades, aceleradores)
        if (v < 75 and a > 0.5) or (v >= 75 and a <= 0.5)
    )
    total = len(aceleraciones)
    precision = correctas / total * 100

    print(f"   - Decisiones correctas: {correctas}/{total} ({precision:.1f}%)")

    return {
        "promedio_acelerador": prom_acelerador,
        "precision_aceleracion": precision,
        "velocidades": velocidades,
        "aceleradores": aceleradores,
    }


def analizar_frenado(datos):
    """Analiza el comportamiento de frenado."""
    print("\n🛑 Análisis de Frenado:")

    frenados = datos["frenado"]
    distancias = [r["distancia_parada"] for r in frenados]
    frenos = [r["decision"]["freno"] for r in frenados]

    # Calcular estadísticas
    prom_freno = np.mean(frenos)
    max_freno = max(frenos)
    min_freno = min(frenos)

    print(f"   - Promedio freno: {prom_freno:.3f}")
    print(f"   - Máximo freno: {max_freno:.3f}")
    print(f"   - Mínimo freno: {min_freno:.3f}")

    # Verificar frenado anticipado: frenar cuando distancia < 15m
    correctas = sum(
        1 for d, f in zip(distancias, frenos) if (d < 15 and f > 0) or (d >= 15 and f == 0)
    )
    total = len(frenados)
    precision = correctas / total * 100

    print(f"   - Frenados anticipados correctos: {correctas}/{total} ({precision:.1f}%)")

    return {
        "promedio_freno": prom_freno,
        "precision_frenado": precision,
        "distancias": distancias,
        "frenos": frenos,
    }


def analizar_pendientes(datos):
    """Analiza el comportamiento en pendientes."""
    print("\n⛰️ Análisis de Pendientes:")

    pendientes_data = datos["pendientes"]
    pendientes = [r["pendiente"] for r in pendientes_data]
    ajustes = [r["decision"].get("ajuste_pendiente", 0) for r in pendientes_data]

    # Calcular estadísticas
    prom_ajuste = np.mean(ajustes)
    max_ajuste = max(ajustes)
    min_ajuste = min(ajustes)

    print(f"   - Promedio ajuste pendiente: {prom_ajuste:.3f}")
    print(f"   - Máximo ajuste pendiente: {max_ajuste:.3f}")
    print(f"   - Mínimo ajuste pendiente: {min_ajuste:.3f}")

    # Verificar ajustes por pendiente
    correctas = sum(
        1 for p, a in zip(pendientes, ajustes) if abs(a) > 0
    )  # Cualquier ajuste se considera correcto
    total = len(pendientes)
    precision = correctas / total * 100

    print(f"   - Ajustes aplicados: {correctas}/{total} ({precision:.1f}%)")

    return {
        "promedio_ajuste": prom_ajuste,
        "precision_pendientes": precision,
        "pendientes": pendientes,
        "ajustes": ajustes,
    }


def analizar_modo_autonomo(historial):
    """Analiza el rendimiento en modo autónomo."""
    print("\n🤖 Análisis de Modo Autónomo:")

    if not historial:
        print("   - No hay datos de historial autónomo")
        return None

    # Extraer datos de velocidad y decisiones
    velocidades = []
    aceleradores = []
    frenos = []
    timestamps = []

    for entrada in historial:
        if "datos" in entrada and "decision" in entrada:
            datos = entrada["datos"]
            decision = entrada["decision"]

            velocidades.append(datos.get("velocidad", 0))
            aceleradores.append(decision.get("acelerador", 0))
            frenos.append(decision.get("freno", 0))
            timestamps.append(entrada.get("timestamp", 0))

    if not velocidades:
        print("   - No hay datos válidos en el historial")
        return None

    # Estadísticas de velocidad
    vel_promedio = np.mean(velocidades)
    vel_max = max(velocidades)
    vel_min = min(velocidades)
    vel_std = np.std(velocidades)

    print(f"   - Velocidad promedio: {vel_promedio:.1f} km/h")
    print(f"   - Velocidad máxima: {vel_max:.1f} km/h")
    print(f"   - Velocidad mínima: {vel_min:.1f} km/h")
    print(f"   - Desviación estándar velocidad: {vel_std:.1f} km/h")

    # Analizar estabilidad (tiempo cerca del objetivo 80 km/h)
    objetivo = 80
    tolerancia = 5  # ±5 km/h
    cerca_objetivo = sum(
        1 for v in velocidades if objetivo - tolerancia <= v <= objetivo + tolerancia
    )
    estabilidad = cerca_objetivo / len(velocidades) * 100

    print(f"   - Estabilidad (±{tolerancia} km/h del objetivo): {estabilidad:.1f}%")

    # Analizar decisiones
    decisiones_acelerar = sum(1 for a in aceleradores if a > 0.1)
    decisiones_frenar = sum(1 for f in frenos if f > 0.1)
    total_decisiones = len(aceleradores)

    print(f"   - Decisiones de acelerar: {decisiones_acelerar}/{total_decisiones}")
    print(f"   - Decisiones de frenar: {decisiones_frenar}/{total_decisiones}")

    return {
        "velocidad_promedio": vel_promedio,
        "velocidad_max": vel_max,
        "velocidad_min": vel_min,
        "estabilidad": estabilidad,
        "decisiones_acelerar": decisiones_acelerar,
        "decisiones_frenar": decisiones_frenar,
        "total_ciclos": total_decisiones,
    }


def generar_reporte_completo():
    """Genera un reporte completo de rendimiento."""
    print("📊 Generando Análisis Completo de Rendimiento IA\n")

    # Cargar datos
    datos_pruebas = cargar_datos_pruebas()
    historial = cargar_historial_autonomo()

    if not datos_pruebas:
        print("❌ No se pudieron cargar los datos de pruebas")
        return

    # Análisis individuales
    analisis_acel = analizar_aceleracion(datos_pruebas)
    analisis_freno = analizar_frenado(datos_pruebas)
    analisis_pend = analizar_pendientes(datos_pruebas)
    analisis_auto = analizar_modo_autonomo(historial)

    # Resumen general
    print("\n" + "=" * 60)
    print("📈 RESUMEN GENERAL DE RENDIMIENTO")
    print("=" * 60)

    precision_total = (
        analisis_acel["precision_aceleracion"]
        + analisis_freno["precision_frenado"]
        + analisis_pend["precision_pendientes"]
    ) / 3

    print(f"🎯 Precisión general: {precision_total:.1f}%")

    if analisis_auto:
        print("🤖 Rendimiento autónomo:")
        print(f"   - Estabilidad: {analisis_auto['estabilidad']:.1f}%")
        print(f"   - Velocidad promedio: {analisis_auto['velocidad_promedio']:.1f} km/h")
        print(f"   - Total ciclos: {analisis_auto['total_ciclos']}")

    # Recomendaciones
    print("\n💡 Recomendaciones:")
    if analisis_freno["precision_frenado"] < 60:
        print("   - ⚠️ Calibrar parámetros de frenado anticipado")
    if analisis_acel["precision_aceleracion"] < 80:
        print("   - 📈 Optimizar lógica de aceleración")
    if analisis_auto and analisis_auto["estabilidad"] < 70:
        print("   - 🎛️ Ajustar control PID para mejor estabilidad")

    # Guardar análisis completo
    analisis_completo = {
        "timestamp": datetime.now().isoformat(),
        "aceleracion": analisis_acel,
        "frenado": analisis_freno,
        "pendientes": analisis_pend,
        "autonomo": analisis_auto,
        "precision_general": precision_total,
    }

    with open("analisis_rendimiento_completo.json", "w", encoding="utf-8") as f:
        json.dump(analisis_completo, f, indent=2, ensure_ascii=False)

    print("\n💾 Análisis guardado en 'analisis_rendimiento_completo.json'")
    print("✅ Análisis de rendimiento completado")

    return analisis_completo


if __name__ == "__main__":
    generar_reporte_completo()
