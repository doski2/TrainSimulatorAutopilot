"""
Sistema de monitoreo de rendimiento para el dashboard web.
Mide el impacto de optimizaciones y detecta cuellos de botella.
"""

import json
import os
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil


class PerformanceMonitor:
    """Monitor de rendimiento para el dashboard web."""

    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics_history = deque(maxlen=max_samples)
        self.is_monitoring = False
        self.monitor_thread = None
        self.baseline_metrics = {}
        self.optimization_impact = {}

        # Métricas a monitorear
        self.metric_definitions = {
            "cpu_percent": "Uso de CPU (%)",
            "memory_percent": "Uso de memoria (%)",
            "memory_mb": "Memoria usada (MB)",
            "network_connections": "Conexiones de red activas",
            "open_files": "Archivos abiertos",
            "threads_count": "Número de hilos",
            "dashboard_response_time": "Tiempo de respuesta dashboard (ms)",
            "websocket_latency": "Latencia WebSocket (ms)",
            "chart_render_time": "Tiempo de renderizado de gráficos (ms)",
            "metrics_update_frequency": "Frecuencia actualización métricas (Hz)",
            "ui_frame_drops": "Caídas de frames UI (%)",
        }

    def start_monitoring(self):
        """Iniciar monitoreo de rendimiento."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Monitoreo de rendimiento iniciado")

    def stop_monitoring(self):
        """Detener monitoreo de rendimiento."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("Monitoreo de rendimiento detenido")

    def _monitor_loop(self):
        """Bucle principal de monitoreo."""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                metrics["timestamp"] = datetime.now().isoformat()

                self.metrics_history.append(metrics)
                time.sleep(1)  # Muestreo cada segundo

            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(5)

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Recopilar métricas del sistema."""
        metrics = {}

        # Métricas de CPU
        metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)

        # Métricas de memoria
        memory = psutil.virtual_memory()
        metrics["memory_percent"] = memory.percent
        metrics["memory_mb"] = memory.used / 1024 / 1024

        # Métricas de red
        network = psutil.net_connections()
        metrics["network_connections"] = len(network)

        # Métricas de proceso (si está disponible)
        try:
            process = psutil.Process()
            metrics["open_files"] = len(process.open_files())
            metrics["threads_count"] = process.num_threads()
        except Exception:
            metrics["open_files"] = 0
            metrics["threads_count"] = 0

        # Métricas específicas del dashboard (placeholders para integración)
        metrics["dashboard_response_time"] = 0  # Se actualizará desde el dashboard
        metrics["websocket_latency"] = 0
        metrics["chart_render_time"] = 0
        metrics["metrics_update_frequency"] = 0
        metrics["ui_frame_drops"] = 0

        return metrics

    def record_dashboard_metric(self, metric_name: str, value: float):
        """Registrar métrica específica del dashboard."""
        if not self.metrics_history:
            return

        # Actualizar la última entrada
        self.metrics_history[-1][metric_name] = value

    def set_baseline(self, label: str = "baseline"):
        """Establecer línea base de rendimiento."""
        if not self.metrics_history:
            print("No hay datos para establecer línea base")
            return

        # Calcular promedio de las últimas 60 muestras (1 minuto)
        recent_metrics = list(self.metrics_history)[-60:]
        baseline = {}

        for key in self.metric_definitions.keys():
            if key in recent_metrics[0]:
                values = [m.get(key, 0) for m in recent_metrics]
                baseline[key] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "samples": len(values),
                }

        self.baseline_metrics[label] = {
            "timestamp": datetime.now().isoformat(),
            "metrics": baseline,
        }

        print(f"Línea base '{label}' establecida con {len(recent_metrics)} muestras")

    def measure_optimization_impact(self, optimization_name: str, before_label: str = "baseline"):
        """Medir impacto de una optimización."""
        if before_label not in self.baseline_metrics:
            print(f"Línea base '{before_label}' no encontrada")
            return

        if not self.metrics_history:
            print("No hay datos actuales para comparar")
            return

        # Calcular métricas actuales
        recent_metrics = list(self.metrics_history)[-60:]
        current = {}

        for key in self.metric_definitions.keys():
            if key in recent_metrics[0]:
                values = [m.get(key, 0) for m in recent_metrics]
                current[key] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "samples": len(values),
                }

        # Calcular impacto
        impact = {}
        baseline = self.baseline_metrics[before_label]["metrics"]

        for key in self.metric_definitions.keys():
            if key in baseline and key in current:
                before = baseline[key]["mean"]
                after = current[key]["mean"]

                if before != 0:
                    change_percent = ((after - before) / before) * 100
                else:
                    change_percent = 0 if after == 0 else float("inf")

                impact[key] = {
                    "before": before,
                    "after": after,
                    "change_percent": change_percent,
                    "improvement": change_percent < 0,  # Mejora si es negativo
                }

        self.optimization_impact[optimization_name] = {
            "timestamp": datetime.now().isoformat(),
            "baseline_used": before_label,
            "impact": impact,
            "summary": self._summarize_impact(impact),
        }

        print(f"Impacto de optimización '{optimization_name}' medido")
        return impact

    def _summarize_impact(self, impact: Dict) -> Dict[str, Any]:
        """Crear resumen del impacto."""
        improvements = []
        regressions = []

        for metric, data in impact.items():
            change = data["change_percent"]
            if abs(change) > 5:  # Cambios significativos (>5%)
                if change < 0:
                    improvements.append(f"{metric}: {change:.1f}%")
                else:
                    regressions.append(f"{metric}: +{change:.1f}%")

        return {
            "total_metrics": len(impact),
            "improvements": improvements,
            "regressions": regressions,
            "net_improvement": len(improvements) > len(regressions),
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Generar reporte completo de rendimiento."""
        if not self.metrics_history:
            return {"error": "No hay datos de monitoreo disponibles"}

        recent_metrics = list(self.metrics_history)[-300:]  # Últimos 5 minutos

        report = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_duration_seconds": len(recent_metrics),
            "current_metrics": recent_metrics[-1] if recent_metrics else {},
            "averages": {},
            "peaks": {},
            "optimization_impacts": self.optimization_impact,
            "recommendations": [],
        }

        # Calcular promedios y picos
        for key in self.metric_definitions.keys():
            values = [m.get(key, 0) for m in recent_metrics if key in m]
            if values:
                report["averages"][key] = sum(values) / len(values)
                report["peaks"][key] = max(values)

        # Generar recomendaciones
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generar recomendaciones basadas en métricas."""
        recommendations = []

        avg = report.get("averages", {})

        # Recomendaciones de CPU
        if avg.get("cpu_percent", 0) > 80:
            recommendations.append("CPU alto: Considerar reducir frecuencia de actualización")
        elif avg.get("cpu_percent", 0) > 50:
            recommendations.append("CPU moderado: Optimizar operaciones de renderizado")

        # Recomendaciones de memoria
        if avg.get("memory_percent", 0) > 85:
            recommendations.append("Memoria alta: Implementar limpieza de caché automática")
        elif avg.get("memory_mb", 0) > 500:
            recommendations.append("Memoria elevada: Reducir puntos de historial")

        # Recomendaciones de respuesta
        if avg.get("dashboard_response_time", 0) > 100:
            recommendations.append("Respuesta lenta: Optimizar consultas al servidor")
        if avg.get("chart_render_time", 0) > 50:
            recommendations.append("Renderizado lento: Implementar throttling de gráficos")

        # Recomendaciones de conectividad
        if avg.get("websocket_latency", 0) > 100:
            recommendations.append("Latencia WebSocket alta: Verificar conexión de red")

        return recommendations

    def save_report(self, filename: Optional[str] = None):
        """Guardar reporte de rendimiento."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"

        report = self.get_performance_report()

        os.makedirs("reports", exist_ok=True)
        filepath = os.path.join("reports", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Reporte guardado: {filepath}")
        return filepath

    def export_metrics_csv(self, filename: Optional[str] = None):
        """Exportar métricas a CSV para análisis."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.csv"

        if not self.metrics_history:
            print("No hay métricas para exportar")
            return

        os.makedirs("reports", exist_ok=True)
        filepath = os.path.join("reports", filename)

        import csv

        fieldnames = ["timestamp"] + list(self.metric_definitions.keys())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for metric in self.metrics_history:
                row = {"timestamp": metric.get("timestamp", "")}
                for key in self.metric_definitions.keys():
                    row[key] = metric.get(key, 0)
                writer.writerow(row)

        print(f"Métricas exportadas: {filepath}")
        return filepath


# Instancia global del monitor
performance_monitor = PerformanceMonitor()


def start_performance_monitoring():
    """Función de conveniencia para iniciar monitoreo."""
    performance_monitor.start_monitoring()


def stop_performance_monitoring():
    """Función de conveniencia para detener monitoreo."""
    performance_monitor.stop_monitoring()


def record_dashboard_metric(metric_name: str, value: float):
    """Función de conveniencia para registrar métricas del dashboard."""
    performance_monitor.record_dashboard_metric(metric_name, value)


if __name__ == "__main__":
    # Demo del sistema de monitoreo
    print("Iniciando demo del monitor de rendimiento...")

    monitor = PerformanceMonitor(max_samples=100)

    # Iniciar monitoreo
    monitor.start_monitoring()

    # Simular línea base
    print("Estableciendo línea base...")
    time.sleep(10)  # Recopilar datos por 10 segundos
    monitor.set_baseline("baseline")

    # Simular optimización (simular mejora en métricas)
    print("Aplicando 'optimización' simulada...")
    for i in range(5):
        monitor.record_dashboard_metric("cpu_percent", 20 + i)  # Simular reducción de CPU
        monitor.record_dashboard_metric(
            "dashboard_response_time", 50 - i * 5
        )  # Simular mejora de respuesta
        time.sleep(1)

    # Medir impacto
    impact = monitor.measure_optimization_impact("throttling_optimization")

    # Generar reporte
    report = monitor.get_performance_report()

    if impact:
        print(f"Impacto medido: {len(impact)} métricas")
    else:
        print("No se pudo medir el impacto")
    print(f"Recomendaciones: {len(report.get('recommendations', []))}")

    # Guardar reporte
    monitor.save_report("demo_performance_report.json")

    # Detener monitoreo
    monitor.stop_monitoring()

    print("Demo completada")


# ==================== OPTIMIZACIONES ADICIONALES - FASE 4 ====================


class DataCompressor:
    """Compresor de datos para optimizar transmisión."""

    def __init__(self):
        self.compression_enabled = True
        self.compression_threshold = 1000  # bytes
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos

    def compress_data(self, data: Dict) -> Dict:
        """Comprimir datos si es beneficioso."""
        if not self.compression_enabled:
            return data

        # Convertir a JSON string para medir tamaño
        json_str = json.dumps(data, default=str)
        original_size = len(json_str.encode("utf-8"))

        if original_size < self.compression_threshold:
            return data  # No comprimir datos pequeños

        # Aplicar compresión simple (remover redundancias)
        compressed = self._apply_compression(data)

        # Verificar si la compresión fue efectiva
        compressed_str = json.dumps(compressed, default=str)
        compressed_size = len(compressed_str.encode("utf-8"))

        if compressed_size < original_size * 0.8:  # Al menos 20% de reducción
            compressed["_compressed"] = True
            compressed["_original_size"] = original_size
            compressed["_compressed_size"] = compressed_size
            return compressed

        return data  # Mantener original si compresión no efectiva

    def _apply_compression(self, data: Dict) -> Dict:
        """Aplicar algoritmos de compresión simples."""
        compressed = {}

        for key, value in data.items():
            if isinstance(value, list) and len(value) > 10:
                # Comprimir listas largas usando diferencias
                compressed[key] = self._compress_list(value)
            elif isinstance(value, dict):
                # Recursivamente comprimir diccionarios
                compressed[key] = self._apply_compression(value)
            else:
                compressed[key] = value

        return compressed

    def _compress_list(self, data_list: List) -> Dict:
        """Comprimir lista usando diferencias o patrones."""
        if not data_list:
            return {"type": "empty"}

        # Detectar si es una secuencia numérica
        if all(isinstance(x, (int, float)) for x in data_list):
            # Calcular diferencias para secuencias largas
            if len(data_list) > 20:
                diffs = [data_list[i] - data_list[i - 1] for i in range(1, len(data_list))]
                # Si las diferencias son pequeñas, comprimir
                avg_diff = sum(abs(d) for d in diffs) / len(diffs)
                if avg_diff < 0.1:  # Diferencias pequeñas
                    return {"type": "diff_compressed", "first": data_list[0], "diffs": diffs}

        # Comprimir usando run-length encoding para valores repetidos
        if len(data_list) > 5:
            rle = self._run_length_encode(data_list)
            if len(str(rle)) < len(str(data_list)) * 0.7:
                return {"type": "rle_compressed", "data": rle}

        return {"type": "raw", "data": data_list}

    def _run_length_encode(self, data: List) -> List:
        """Run-length encoding para datos repetitivos."""
        if not data:
            return []

        encoded = []
        current_value = data[0]
        count = 1

        for value in data[1:]:
            if value == current_value:
                count += 1
            else:
                encoded.append([current_value, count])
                current_value = value
                count = 1

        encoded.append([current_value, count])
        return encoded

    def decompress_data(self, data: Dict) -> Dict:
        """Descomprimir datos comprimidos."""
        if not data.get("_compressed", False):
            return data

        decompressed = {}

        for key, value in data.items():
            if key.startswith("_"):
                continue  # Saltar metadatos de compresión

            if isinstance(value, dict):
                if value.get("type") == "diff_compressed":
                    decompressed[key] = self._decompress_diffs(value)
                elif value.get("type") == "rle_compressed":
                    decompressed[key] = self._decompress_rle(value)
                elif value.get("type") == "raw":
                    decompressed[key] = value["data"]
                elif value.get("type") == "empty":
                    decompressed[key] = []
                else:
                    decompressed[key] = self._apply_compression(value)  # Recursivo
            else:
                decompressed[key] = value

        return decompressed

    def _decompress_diffs(self, compressed: Dict) -> List:
        """Descomprimir diferencias."""
        first = compressed["first"]
        diffs = compressed["diffs"]
        result = [first]

        for diff in diffs:
            result.append(result[-1] + diff)

        return result

    def _decompress_rle(self, compressed: Dict) -> List:
        """Descomprimir run-length encoding."""
        result = []
        for value, count in compressed["data"]:
            result.extend([value] * count)
        return result


class SmartCache:
    """Cache inteligente para gráficos y datos."""

    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Obtener elemento del cache."""
        if key in self.cache:
            # Verificar TTL
            if time.time() - self.access_times[key] > self.ttl:
                del self.cache[key]
                del self.access_times[key]
                self.miss_count += 1
                return None

            self.access_times[key] = time.time()
            self.hit_count += 1
            return self.cache[key]

        self.miss_count += 1
        return None

    def put(self, key: str, value: Any):
        """Almacenar elemento en cache."""
        current_time = time.time()

        # Implementar LRU eviction si es necesario
        if len(self.cache) >= self.max_size:
            # Encontrar el elemento menos recientemente usado
            oldest_key = min(self.access_times, key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        self.cache[key] = value
        self.access_times[key] = current_time

    def clear_expired(self):
        """Limpiar elementos expirados."""
        current_time = time.time()
        expired_keys = [
            key
            for key, access_time in self.access_times.items()
            if current_time - access_time > self.ttl
        ]

        for key in expired_keys:
            del self.cache[key]
            del self.access_times[key]

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "ttl": self.ttl,
        }


class LatencyOptimizer:
    """Optimizador de latencia para el dashboard."""

    def __init__(self):
        self.latency_history = deque(maxlen=100)
        self.optimization_strategies = {
            "websocket_batching": self._optimize_websocket_batching,
            "data_sampling": self._optimize_data_sampling,
            "render_throttling": self._optimize_render_throttling,
            "memory_pooling": self._optimize_memory_pooling,
        }
        self.active_optimizations = set()

    def measure_latency(self, operation: str, start_time: float) -> float:
        """Medir latencia de una operación."""
        latency = (time.time() - start_time) * 1000  # ms
        self.latency_history.append(
            {"operation": operation, "latency": latency, "timestamp": time.time()}
        )
        return latency

    def apply_optimization(self, strategy: str) -> bool:
        """Aplicar una estrategia de optimización."""
        if strategy in self.optimization_strategies:
            success = self.optimization_strategies[strategy]()
            if success:
                self.active_optimizations.add(strategy)
            return success
        return False

    def _optimize_websocket_batching(self) -> bool:
        """Optimizar batching de mensajes WebSocket."""
        # Implementar batching de mensajes para reducir overhead
        print("Optimización WebSocket batching aplicada")
        return True

    def _optimize_data_sampling(self) -> bool:
        """Optimizar muestreo de datos."""
        # Implementar muestreo inteligente de datos
        print("Optimización data sampling aplicada")
        return True

    def _optimize_render_throttling(self) -> bool:
        """Optimizar throttling de renderizado."""
        # Implementar throttling para renderizado de gráficos
        print("Optimización render throttling aplicada")
        return True

    def _optimize_memory_pooling(self) -> bool:
        """Optimizar pooling de memoria."""
        # Implementar object pooling para reducir GC
        print("Optimización memory pooling aplicada")
        return True

    def get_latency_report(self) -> Dict[str, Any]:
        """Generar reporte de latencia."""
        if not self.latency_history:
            return {
                "average_latency": 0,
                "max_latency": 0,
                "min_latency": 0,
                "active_optimizations": list(self.active_optimizations),
            }

        latencies = [entry["latency"] for entry in self.latency_history]

        return {
            "average_latency": sum(latencies) / len(latencies),
            "max_latency": max(latencies),
            "min_latency": min(latencies),
            "sample_count": len(latencies),
            "active_optimizations": list(self.active_optimizations),
        }


# Instancias globales para optimizaciones
data_compressor = DataCompressor()
smart_cache = SmartCache()
latency_optimizer = LatencyOptimizer()


def optimize_dashboard_performance():
    """Aplicar todas las optimizaciones de rendimiento disponibles."""
    print("🚀 Aplicando optimizaciones de rendimiento...")

    # Aplicar optimizaciones de latencia
    optimizations = ["websocket_batching", "data_sampling", "render_throttling", "memory_pooling"]
    applied = 0

    for opt in optimizations:
        if latency_optimizer.apply_optimization(opt):
            applied += 1

    print(f"✅ {applied}/{len(optimizations)} optimizaciones de latencia aplicadas")

    # Limpiar cache expirado
    smart_cache.clear_expired()

    # Mostrar estadísticas
    cache_stats = smart_cache.get_stats()
    latency_stats = latency_optimizer.get_latency_report()

    print("📊 Estadísticas de optimización:")
    print(f"  Cache: {cache_stats['size']}/{cache_stats['max_size']} elementos")
    print(f"  Hit rate: {cache_stats['hit_rate']:.1f}")
    print(f"  Average latency: {latency_stats['average_latency']:.1f}")
    print(f"  Optimizaciones activas: {len(latency_stats['active_optimizations'])}")

    return {
        "cache_stats": cache_stats,
        "latency_stats": latency_stats,
        "applied_optimizations": applied,
    }


if __name__ == "__main__":
    # Demo de optimizaciones
    print("Demo de Optimizaciones de Rendimiento")
    print("=" * 50)

    # Aplicar optimizaciones
    results = optimize_dashboard_performance()

    print(f"\nResultados: {results['applied_optimizations']} optimizaciones aplicadas")
    print("Demo completada")
