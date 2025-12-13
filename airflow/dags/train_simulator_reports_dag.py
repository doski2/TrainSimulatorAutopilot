"""
Train Simulator Autopilot - Reportes Automatizados DAG

Este DAG automatiza la generación de reportes del sistema Train Simulator Autopilot,
incluyendo análisis de rendimiento, telemetría y estado del sistema.

NOTA: Este archivo está diseñado para ejecutarse dentro del contenedor Docker de Airflow.
Los errores de importación mostrados por Pylance son esperados cuando se edita fuera del entorno Docker.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

# Importaciones condicionales para type checking y runtime
if TYPE_CHECKING:
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.sensors.filesystem import FileSensor  # type: ignore

    from airflow import DAG  # type: ignore
    from alert_system import AlertSystem  # type: ignore # noqa: F401
    from performance_monitor import PerformanceMonitor  # type: ignore # noqa: F401
    from predictive_telemetry_analysis import TelemetryAnalyzer  # type: ignore # noqa: F401
    from verificar_tsc_conexion import verificar_conexion  # type: ignore # noqa: F401

# Importaciones runtime con fallback
try:
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.sensors.filesystem import FileSensor  # type: ignore

    from airflow import DAG  # type: ignore

    AIRFLOW_AVAILABLE = True
except ImportError:
    # Fallback para desarrollo local
    AIRFLOW_AVAILABLE = False

    # Clases dummy para desarrollo
    class DAG:
        def __init__(self, dag_id: str, **kwargs):
            self.dag_id = dag_id

    class PythonOperator:
        def __init__(self, task_id: str, python_callable, dag=None, **kwargs):
            pass

    class BashOperator:
        def __init__(self, task_id: str, bash_command: str, dag=None, **kwargs):
            pass

    class FileSensor:
        def __init__(self, task_id: str, filepath: str, dag=None, **kwargs):
            pass


# Configuración por defecto
default_args = {
    "owner": "train_simulator_team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "catchup": False,
}

# Definir el DAG solo si Airflow está disponible
if AIRFLOW_AVAILABLE:
    dag = DAG(
        "train_simulator_reports",
        default_args=default_args,
        description="DAG para generación automática de reportes del Train Simulator Autopilot",
        schedule_interval="0 */4 * * *",  # Cada 4 horas
        max_active_runs=1,
        tags=["train_simulator", "reports", "automation"],
    )
else:
    # DAG dummy para desarrollo
    dag = None
    print("ℹ️ Ejecutando en modo desarrollo - DAG de reportes no disponible")
    print("💡 Para usar este DAG, ejecuta en el entorno Docker de Airflow")


def verificar_conexion_tsc():
    """Verifica la conexión con el sistema TSC"""
    try:
        # Importar y ejecutar verificación de TSC
        sys.path.append("/opt/airflow/train_simulator")
        from verificar_tsc_conexion import verificar_conexion  # type: ignore

        resultado = verificar_conexion()
        if not resultado["success"]:
            raise Exception(f"Error de conexión TSC: {resultado['error']}")

        print("✅ Conexión TSC verificada exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error verificando conexión TSC: {e}")
        raise


def generar_reporte_rendimiento():
    """Genera reporte de rendimiento del sistema"""
    try:
        sys.path.append("/opt/airflow/train_simulator")
        from performance_monitor import PerformanceMonitor  # type: ignore

        monitor = PerformanceMonitor()
        reporte = monitor.generar_reporte_completo()  # type: ignore

        # Guardar reporte
        output_path = f"/opt/airflow/reports/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, "w") as f:
            import json

            json.dump(reporte, f, indent=2, default=str)

        print(f"✅ Reporte de rendimiento generado: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error generando reporte de rendimiento: {e}")
        raise


def procesar_telemetria():
    """Procesa datos de telemetría acumulados"""
    try:
        sys.path.append("/opt/airflow/train_simulator")
        from predictive_telemetry_analysis import TelemetryAnalyzer  # type: ignore

        analyzer = TelemetryAnalyzer()
        resultados = analyzer.analizar_telemetria_reciente()

        # Guardar resultados
        output_path = f"/opt/airflow/reports/telemetry_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, "w") as f:
            import json

            json.dump(resultados, f, indent=2, default=str)

        print(f"✅ Análisis de telemetría completado: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error procesando telemetría: {e}")
        raise


def generar_alertas_sistema():
    """Genera alertas del sistema basadas en métricas"""
    try:
        sys.path.append("/opt/airflow/train_simulator")
        from alert_system import AlertSystem  # type: ignore

        alert_system = AlertSystem()
        alertas = alert_system.verificar_todas_alertas()  # type: ignore

        # Guardar alertas
        output_path = (
            f"/opt/airflow/reports/system_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_path, "w") as f:
            import json

            json.dump(alertas, f, indent=2, default=str)

        print(f"✅ Alertas del sistema generadas: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error generando alertas: {e}")
        raise


def limpiar_archivos_antiguos():
    """Limpia archivos de log y reportes antiguos"""
    import glob
    from datetime import datetime, timedelta

    # Limpiar logs antiguos (más de 30 días)
    log_pattern = "/opt/airflow/logs/**/*.log"
    cutoff_date = datetime.now() - timedelta(days=30)

    for log_file in glob.glob(log_pattern, recursive=True):
        if os.path.getmtime(log_file) < cutoff_date.timestamp():
            os.remove(log_file)
            print(f"🗑️ Log antiguo eliminado: {log_file}")

    # Limpiar reportes antiguos (más de 7 días)
    report_pattern = "/opt/airflow/reports/*.json"
    cutoff_date = datetime.now() - timedelta(days=7)

    for report_file in glob.glob(report_pattern):
        if os.path.getmtime(report_file) < cutoff_date.timestamp():
            os.remove(report_file)
            print(f"🗑️ Reporte antiguo eliminado: {report_file}")

    print("✅ Limpieza de archivos antiguos completada")


if AIRFLOW_AVAILABLE:
    # Definir las tareas del DAG
    verificar_conexion_task = PythonOperator(
        task_id="verificar_conexion_tsc",
        python_callable=verificar_conexion_tsc,
        dag=dag,
    )

    generar_reporte_task = PythonOperator(
        task_id="generar_reporte_rendimiento",
        python_callable=generar_reporte_rendimiento,
        dag=dag,
    )

    procesar_telemetria_task = PythonOperator(
        task_id="procesar_telemetria",
        python_callable=procesar_telemetria,
        dag=dag,
    )

    generar_alertas_task = PythonOperator(
        task_id="generar_alertas_sistema",
        python_callable=generar_alertas_sistema,
        dag=dag,
    )

    limpiar_archivos_task = PythonOperator(
        task_id="limpiar_archivos_antiguos",
        python_callable=limpiar_archivos_antiguos,
        dag=dag,
    )

    backup_database_task = BashOperator(
        task_id="backup_database",
        bash_command='cp /opt/airflow/train_simulator/data/*.db /opt/airflow/backups/ 2>/dev/null || echo "No databases to backup"',
        dag=dag,
    )

    # Definir dependencias entre tareas
    verificar_conexion_task >> [generar_reporte_task, procesar_telemetria_task, generar_alertas_task]  # type: ignore
    [generar_reporte_task, procesar_telemetria_task, generar_alertas_task] >> backup_database_task  # type: ignore
    backup_database_task >> limpiar_archivos_task  # type: ignore
else:
    print("⚠️  Airflow no disponible - tareas del DAG no definidas (modo desarrollo)")
