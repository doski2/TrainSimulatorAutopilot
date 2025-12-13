"""
Train Simulator Autopilot - Plugin Personalizado para Airflow

Este plugin extiende Airflow con operadores y sensores específicos
para el sistema Train Simulator Autopilot.
"""

from typing import TYPE_CHECKING

# Importaciones condicionales para type checking y runtime
if TYPE_CHECKING:
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.plugins_manager import AirflowPlugin  # type: ignore
    from airflow.sensors.base import BaseSensorOperator  # type: ignore
    from airflow.utils.decorators import apply_defaults  # type: ignore

# Importaciones runtime con fallback
try:
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.plugins_manager import AirflowPlugin  # type: ignore
    from airflow.sensors.base import BaseSensorOperator  # type: ignore
    from airflow.utils.decorators import apply_defaults  # type: ignore

    AIRFLOW_AVAILABLE = True
except ImportError:
    # Fallback para desarrollo local
    AIRFLOW_AVAILABLE = False

    # Clases dummy para desarrollo
    class AirflowPlugin:  # type: ignore
        pass

    class PythonOperator:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    class BaseSensorOperator:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    def apply_defaults(func):  # type: ignore
        return func


import json
import os
import time  # noqa: F401
from datetime import datetime
from typing import Any, Dict, Optional  # noqa: F401

import requests


class TrainSimulatorHealthOperator(PythonOperator if AIRFLOW_AVAILABLE else object):  # type: ignore
    """
    Operador personalizado para verificar la salud del sistema Train Simulator.

    Verifica múltiples componentes del sistema:
    - Dashboard principal (TypeScript)
    - Dashboard secundario (Flask)
    - Conexión TSC
    - Base de datos
    - WebSocket connections
    """

    @apply_defaults
    def __init__(
        self,
        check_dashboard_main: bool = True,
        check_dashboard_flask: bool = True,
        check_tsc_connection: bool = True,
        check_database: bool = True,
        check_websocket: bool = True,
        timeout: int = 30,
        *args,
        **kwargs,
    ):
        self.check_dashboard_main = check_dashboard_main
        self.check_dashboard_flask = check_dashboard_flask
        self.check_tsc_connection = check_tsc_connection
        self.check_database = check_database
        self.check_websocket = check_websocket
        self.timeout = timeout

        super().__init__(*args, python_callable=self._execute_health_check, **kwargs)

    def _execute_health_check(self):
        """Ejecuta verificación completa de salud del sistema"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "HEALTHY",
        }

        # Verificar dashboard principal
        if self.check_dashboard_main:
            try:
                response = requests.get("http://localhost:3000/health", timeout=self.timeout)
                results["checks"]["dashboard_main"] = {
                    "status": "HEALTHY" if response.status_code == 200 else "UNHEALTHY",
                    "response_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                }
            except Exception as e:
                results["checks"]["dashboard_main"] = {"status": "UNHEALTHY", "error": str(e)}
                results["overall_status"] = "UNHEALTHY"

        # Verificar dashboard Flask
        if self.check_dashboard_flask:
            try:
                response = requests.get("http://localhost:5000/health", timeout=self.timeout)
                results["checks"]["dashboard_flask"] = {
                    "status": "HEALTHY" if response.status_code == 200 else "UNHEALTHY",
                    "response_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                }
            except Exception as e:
                results["checks"]["dashboard_flask"] = {"status": "UNHEALTHY", "error": str(e)}
                results["overall_status"] = "UNHEALTHY"

        # Verificar conexión TSC
        if self.check_tsc_connection:
            try:
                # Importar función de verificación TSC
                import sys

                sys.path.append("/opt/airflow/train_simulator")
                from verificar_tsc_conexion import verificar_conexion  # type: ignore

                tsc_result = verificar_conexion()
                results["checks"]["tsc_connection"] = {
                    "status": "HEALTHY" if tsc_result["success"] else "UNHEALTHY",
                    "details": tsc_result,
                }
                if not tsc_result["success"]:
                    results["overall_status"] = "UNHEALTHY"

            except Exception as e:
                results["checks"]["tsc_connection"] = {"status": "UNHEALTHY", "error": str(e)}
                results["overall_status"] = "UNHEALTHY"

        # Verificar base de datos
        if self.check_database:
            try:
                import os
                import sqlite3

                db_path = "/opt/airflow/train_simulator/data/train_simulator.db"
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    conn.close()

                    results["checks"]["database"] = {
                        "status": "HEALTHY",
                        "tables_count": table_count,
                    }
                else:
                    results["checks"]["database"] = {
                        "status": "UNHEALTHY",
                        "error": "Database file not found",
                    }
                    results["overall_status"] = "UNHEALTHY"

            except Exception as e:
                results["checks"]["database"] = {"status": "UNHEALTHY", "error": str(e)}
                results["overall_status"] = "UNHEALTHY"

        # Verificar WebSocket
        if self.check_websocket:
            try:
                # Importar función de verificación WebSocket
                import sys

                sys.path.append("/opt/airflow/train_simulator")
                from ws_client_test import test_websocket_connection  # type: ignore

                ws_result = test_websocket_connection()
                results["checks"]["websocket"] = {
                    "status": "HEALTHY" if ws_result["success"] else "UNHEALTHY",
                    "details": ws_result,
                }
                if not ws_result["success"]:
                    results["overall_status"] = "UNHEALTHY"

            except Exception as e:
                results["checks"]["websocket"] = {"status": "UNHEALTHY", "error": str(e)}
                results["overall_status"] = "UNHEALTHY"

        # Guardar resultados
        output_path = f"/opt/airflow/health_checks/health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"✅ Health check completado. Status: {results['overall_status']}")
        print(f"📊 Resultados guardados en: {output_path}")

        # Lanzar excepción si el sistema no está saludable
        if results["overall_status"] != "HEALTHY":
            unhealthy_checks = [
                k for k, v in results["checks"].items() if v.get("status") == "UNHEALTHY"
            ]
            raise Exception(
                f"Sistema no saludable. Componentes con problemas: {', '.join(unhealthy_checks)}"
            )

        return results


class TelemetryDataSensor(BaseSensorOperator if AIRFLOW_AVAILABLE else object):  # type: ignore
    """
    Sensor que espera a que haya suficientes datos de telemetría
    para procesar antes de continuar con el workflow.
    """

    @apply_defaults
    def __init__(
        self,
        telemetry_dir: str = "/opt/airflow/train_simulator/data/telemetry",
        min_records: int = 100,
        max_wait_time: int = 3600,  # 1 hora
        *args,
        **kwargs,
    ):
        self.telemetry_dir = telemetry_dir
        self.min_records = min_records
        self.max_wait_time = max_wait_time

        super().__init__(
            *args,
            mode="poke",
            timeout=max_wait_time,
            poke_interval=300,  # Verificar cada 5 minutos
            **kwargs,
        )

    def poke(self, context):
        """Verifica si hay suficientes datos de telemetría"""
        try:
            import json
            import os

            if not os.path.exists(self.telemetry_dir):
                print(f"📁 Directorio de telemetría no existe: {self.telemetry_dir}")
                return False

            total_records = 0

            # Contar registros en archivos de telemetría
            for filename in os.listdir(self.telemetry_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.telemetry_dir, filename)
                    try:
                        with open(filepath) as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                total_records += len(data)
                            elif isinstance(data, dict):
                                total_records += 1
                    except Exception:
                        continue

            print(
                f"📊 Registros de telemetría encontrados: {total_records} (mínimo requerido: {self.min_records})"
            )

            return total_records >= self.min_records

        except Exception as e:
            print(f"❌ Error verificando datos de telemetría: {e}")
            return False


class PerformanceAlertOperator(PythonOperator if AIRFLOW_AVAILABLE else object):  # type: ignore
    """
    Operador que verifica métricas de rendimiento y genera alertas
    si se detectan anomalías.
    """

    @apply_defaults
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 85.0,
        response_time_threshold: float = 2.0,
        *args,
        **kwargs,
    ):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.response_time_threshold = response_time_threshold

        super().__init__(*args, python_callable=self._check_performance_alerts, **kwargs)

    def _check_performance_alerts(self):
        """Verifica métricas de rendimiento y genera alertas"""
        try:
            from datetime import datetime

            import psutil
            import requests

            alerts = []

            # Verificar CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                alerts.append(
                    {
                        "type": "CPU_HIGH",
                        "metric": "cpu_percent",
                        "value": cpu_percent,
                        "threshold": self.cpu_threshold,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Verificar memoria
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                alerts.append(
                    {
                        "type": "MEMORY_HIGH",
                        "metric": "memory_percent",
                        "value": memory.percent,
                        "threshold": self.memory_threshold,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Verificar tiempo de respuesta de dashboards
            try:
                response = requests.get("http://localhost:3000/health", timeout=5)
                response_time = response.elapsed.total_seconds()
                if response_time > self.response_time_threshold:
                    alerts.append(
                        {
                            "type": "RESPONSE_TIME_HIGH",
                            "metric": "dashboard_response_time",
                            "value": response_time,
                            "threshold": self.response_time_threshold,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            except Exception:
                alerts.append(
                    {
                        "type": "DASHBOARD_UNREACHABLE",
                        "metric": "dashboard_main",
                        "value": "unreachable",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Guardar alertas si existen
            if alerts:
                output_path = f"/opt/airflow/alerts/performance_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                with open(output_path, "w") as f:
                    json.dump(alerts, f, indent=2)

                print(f"🚨 Alertas de rendimiento generadas: {len(alerts)}")
                for alert in alerts:
                    print(f"  - {alert['type']}: {alert['metric']} = {alert['value']}")

                # Aquí se podría integrar con servicios de notificación
                # (Slack, email, PagerDuty, etc.)

            else:
                print("✅ No se detectaron alertas de rendimiento")

            return alerts

        except Exception as e:
            print(f"❌ Error verificando alertas de rendimiento: {e}")
            raise


# Definir el plugin
class TrainSimulatorPlugin(AirflowPlugin if AIRFLOW_AVAILABLE else object):  # type: ignore
    name = "train_simulator_plugin"

    if AIRFLOW_AVAILABLE:
        operators = [TrainSimulatorHealthOperator, PerformanceAlertOperator]
        sensors = [TelemetryDataSensor]
    else:
        operators = []
        sensors = []
        print("ℹ️ Ejecutando plugin en modo desarrollo - componentes Airflow no disponibles")
        print("💡 Para usar el plugin completo, ejecuta en el entorno Docker de Airflow")
