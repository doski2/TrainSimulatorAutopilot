"""
Train Simulator Autopilot - DAG de Ejemplo con Plugins Personalizados

Este DAG demuestra el uso de los operadores y sensores personalizados
desarrollados específicamente para Train Simulator Autopilot.

IMPORTANTE - Modo de Uso:
========================
Este archivo está diseñado para ejecutarse dentro del contenedor Docker de Airflow.
Cuando se edita localmente, Pylance mostrará errores de importación porque:

1. Apache Airflow no está instalado en el entorno local
2. Los plugins personalizados (train_simulator_plugin) no están en PYTHONPATH
3. Los módulos del proyecto no están disponibles fuera del contenedor

El código usa importaciones condicionales para manejar estos casos:
- Si Airflow está disponible: importa los módulos reales
- Si no está disponible: usa clases dummy para evitar errores de linting

Para usar este DAG:
1. Asegúrate de que Airflow esté ejecutándose: ./init_airflow.sh
2. El DAG aparecerá en la UI de Airflow como 'train_simulator_custom_operators_demo'
3. Puede ejecutarse manualmente desde la interfaz web
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

# Importaciones condicionales para type checking y runtime
if TYPE_CHECKING:
    from airflow.operators.dummy import DummyOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from train_simulator_plugin import (  # type: ignore
        PerformanceAlertOperator,
        TelemetryDataSensor,
        TrainSimulatorHealthOperator,
    )

    from airflow import DAG  # type: ignore
    from predictive_telemetry_analysis import TelemetryAnalyzer  # type: ignore # noqa: F401

# Importaciones runtime con fallback
try:
    from airflow.operators.dummy import DummyOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from train_simulator_plugin import (  # type: ignore
        PerformanceAlertOperator,
        TelemetryDataSensor,
        TrainSimulatorHealthOperator,
    )

    from airflow import DAG  # type: ignore

    AIRFLOW_AVAILABLE = True
except ImportError:
    # Fallback para desarrollo local
    AIRFLOW_AVAILABLE = False

    # Clases dummy para desarrollo - Pylance las verá gracias a TYPE_CHECKING arriba
    class DAG:
        def __init__(self, dag_id: str, **kwargs):
            self.dag_id = dag_id

    class PythonOperator:
        def __init__(self, task_id: str, python_callable, dag=None, **kwargs):
            pass

    class DummyOperator:
        def __init__(self, task_id: str, dag=None, **kwargs):
            pass

    class TrainSimulatorHealthOperator:
        def __init__(self, task_id: str, dag=None, **kwargs):
            pass

    class TelemetryDataSensor:
        def __init__(self, task_id: str, dag=None, **kwargs):
            pass

    class PerformanceAlertOperator:
        def __init__(self, task_id: str, dag=None, **kwargs):
            pass


# Configuración por defecto
default_args = {
    "owner": "train_simulator_team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "catchup": False,
}

# Definir el DAG solo si Airflow está disponible
if AIRFLOW_AVAILABLE:
    dag = DAG(
        "train_simulator_custom_operators_demo",
        default_args=default_args,
        description="DAG de demostración usando operadores personalizados de Train Simulator",
        schedule_interval=None,  # Solo ejecución manual
        max_active_runs=1,
        tags=["train_simulator", "demo", "custom_operators"],
    )
else:
    # DAG dummy para desarrollo
    dag = None
    print("ℹ️ Ejecutando en modo desarrollo - DAG no disponible")
    print("💡 Para usar este DAG, ejecuta en el entorno Docker de Airflow")


def procesar_datos_telemetria():
    """Procesa datos de telemetría usando el sistema existente"""
    try:
        import sys

        sys.path.append("/opt/airflow/train_simulator")

        # Importación condicional para evitar errores en desarrollo
        try:
            from predictive_telemetry_analysis import TelemetryAnalyzer  # type: ignore
        except ImportError:
            print("⚠️ TelemetryAnalyzer no disponible - simulando procesamiento")
            return {"status": "simulated", "insights": []}

        analyzer = TelemetryAnalyzer()
        resultados = analyzer.analizar_telemetria_reciente()

        print(f"✅ Procesamiento completado. {len(resultados)} insights generados")

        # Aquí se podrían enviar resultados a un dashboard
        # o almacenar en una base de datos externa

        return resultados

    except Exception as e:
        print(f"❌ Error procesando telemetría: {e}")
        raise


def generar_reporte_integrado():
    """Genera un reporte integrado con datos de health check y rendimiento"""
    try:
        import json
        import os
        from datetime import datetime

        # Recopilar datos de diferentes fuentes
        reporte_integrado = {
            "timestamp": datetime.now().isoformat(),
            "tipo": "reporte_integrado",
            "componentes": {},
        }

        # Buscar archivos recientes de health checks
        health_dir = "/opt/airflow/health_checks"
        if os.path.exists(health_dir):
            health_files = [
                f
                for f in os.listdir(health_dir)
                if f.startswith("health_check_") and f.endswith(".json")
            ]
            if health_files:
                latest_health = max(health_files)
                with open(os.path.join(health_dir, latest_health)) as f:
                    reporte_integrado["componentes"]["health_check"] = json.load(f)

        # Buscar métricas de rendimiento recientes
        monitoring_dir = "/opt/airflow/monitoring"
        if os.path.exists(monitoring_dir):
            metric_files = [
                f
                for f in os.listdir(monitoring_dir)
                if f.startswith("system_metrics_") and f.endswith(".json")
            ]
            if metric_files:
                latest_metrics = max(metric_files)
                with open(os.path.join(monitoring_dir, latest_metrics)) as f:
                    reporte_integrado["componentes"]["system_metrics"] = json.load(f)

        # Buscar alertas recientes
        alerts_dir = "/opt/airflow/alerts"
        if os.path.exists(alerts_dir):
            alert_files = [
                f
                for f in os.listdir(alerts_dir)
                if f.startswith("performance_alerts_") and f.endswith(".json")
            ]
            if alert_files:
                latest_alerts = max(alert_files)
                with open(os.path.join(alerts_dir, latest_alerts)) as f:
                    reporte_integrado["componentes"]["alerts"] = json.load(f)

        # Guardar reporte integrado
        output_path = f"/opt/airflow/reports/integrated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(reporte_integrado, f, indent=2, default=str)

        print(f"✅ Reporte integrado generado: {output_path}")
        return reporte_integrado

    except Exception as e:
        print(f"❌ Error generando reporte integrado: {e}")
        raise


# Definir las tareas del DAG solo si Airflow está disponible
if AIRFLOW_AVAILABLE:
    # Tarea inicial
    inicio_demo = DummyOperator(
        task_id="inicio_demo",
        dag=dag,
    )

    # Health check completo usando operador personalizado
    health_check_completo = TrainSimulatorHealthOperator(
        task_id="health_check_completo",
        check_dashboard_main=True,
        check_dashboard_flask=True,
        check_tsc_connection=True,
        check_database=True,
        check_websocket=True,
        timeout=30,
        dag=dag,
    )

    # Sensor que espera datos de telemetría suficientes
    esperar_telemetria = TelemetryDataSensor(
        task_id="esperar_telemetria",
        telemetry_dir="/opt/airflow/train_simulator/data/telemetry",
        min_records=50,  # Menos registros para demo
        max_wait_time=1800,  # 30 minutos máximo
        dag=dag,
    )

    # Procesar telemetría después de tener suficientes datos
    procesar_telemetria_task = PythonOperator(
        task_id="procesar_telemetria",
        python_callable=procesar_datos_telemetria,
        dag=dag,
    )

    # Verificar rendimiento y generar alertas
    performance_alert_task = PerformanceAlertOperator(
        task_id="verificar_performance_alerts",
        cpu_threshold=70.0,  # Umbrales más bajos para demo
        memory_threshold=75.0,
        response_time_threshold=1.5,
        dag=dag,
    )

    # Generar reporte integrado
    reporte_integrado_task = PythonOperator(
        task_id="generar_reporte_integrado",
        python_callable=generar_reporte_integrado,
        dag=dag,
    )

    # Tarea final
    fin_demo = DummyOperator(
        task_id="fin_demo",
        dag=dag,
    )

    # Definir dependencias entre tareas
    inicio_demo >> health_check_completo  # type: ignore
    health_check_completo >> esperar_telemetria  # type: ignore
    esperar_telemetria >> procesar_telemetria_task  # type: ignore
    procesar_telemetria_task >> performance_alert_task  # type: ignore
    performance_alert_task >> reporte_integrado_task  # type: ignore
    reporte_integrado_task >> fin_demo  # type: ignore
else:
    # En modo desarrollo, solo mostrar información
    print("ℹ️ DAG definido para desarrollo local - ejecutar en entorno Airflow")
    print("📋 Tareas definidas:")
    print("  - inicio_demo")
    print("  - health_check_completo")
    print("  - esperar_telemetria")
    print("  - procesar_telemetria_task")
    print("  - performance_alert_task")
    print("  - reporte_integrado_task")
    print("  - fin_demo")

# Nota: En un escenario real, algunas tareas podrían ejecutarse en paralelo
# pero para esta demo las mantenemos secuenciales para claridad
