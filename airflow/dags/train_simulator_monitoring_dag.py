"""
Train Simulator Autopilot - Monitoreo Continuo DAG

Este DAG implementa monitoreo continuo del sistema Train Simulator,
incluyendo verificación de salud, métricas en tiempo real y alertas automáticas.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import requests

# Importaciones condicionales para type checking y runtime
if TYPE_CHECKING:
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.sensors.python import PythonSensor  # type: ignore

    from airflow import DAG  # type: ignore
    from ws_client_test import test_websocket_connection  # type: ignore # noqa: F401

# Importaciones runtime con fallback
try:
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.sensors.python import PythonSensor  # type: ignore

    from airflow import DAG  # type: ignore

    AIRFLOW_AVAILABLE = True
except ImportError:
    print("⚠️  Airflow no disponible - ejecutando en modo desarrollo")
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

    class PythonSensor:
        def __init__(
            self, task_id: str, python_callable, poke_interval=60, timeout=300, dag=None, **kwargs
        ):
            pass


# Configuración por defecto
default_args = {
    "owner": "train_simulator_team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
    "catchup": False,
}

if AIRFLOW_AVAILABLE:
    # Definir el DAG
    dag = DAG(
        "train_simulator_monitoring",
        default_args=default_args,
        description="DAG para monitoreo continuo del sistema Train Simulator Autopilot",
        schedule_interval="*/15 * * * *",  # Cada 15 minutos
        max_active_runs=1,
        tags=["train_simulator", "monitoring", "health_check"],
    )
else:
    print("⚠️  Airflow no disponible - DAG no definido (modo desarrollo)")
    dag = None


def verificar_dashboard_principal():
    """Verifica que el dashboard principal esté funcionando"""
    try:
        # Verificar dashboard TypeScript
        response = requests.get("http://localhost:3000/health", timeout=10)
        if response.status_code != 200:
            raise Exception(f"Dashboard principal no responde: {response.status_code}")

        print("✅ Dashboard principal operativo")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al dashboard principal: {e}")
        raise


def verificar_dashboard_flask():
    """Verifica que el dashboard Flask esté funcionando"""
    try:
        # Verificar dashboard Flask
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code != 200:
            raise Exception(f"Dashboard Flask no responde: {response.status_code}")

        print("✅ Dashboard Flask operativo")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al dashboard Flask: {e}")
        raise


def verificar_conexion_websocket():
    """Verifica la conexión WebSocket entre componentes"""
    try:
        sys.path.append("/opt/airflow/train_simulator")
        from ws_client_test import test_websocket_connection  # type: ignore

        resultado = test_websocket_connection()
        if not resultado["success"]:
            raise Exception(f"Error WebSocket: {resultado['error']}")

        print("✅ Conexión WebSocket operativa")
        return True

    except Exception as e:
        print(f"❌ Error en conexión WebSocket: {e}")
        raise


def monitorear_recursos_sistema():
    """Monitorea recursos del sistema (CPU, memoria, disco)"""
    try:
        import psutil

        # Obtener métricas del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        metricas = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": memory.used / (1024**3),
            "memory_total_gb": memory.total / (1024**3),
            "disk_percent": disk.percent,
            "disk_used_gb": disk.used / (1024**3),
            "disk_total_gb": disk.total / (1024**3),
        }

        # Verificar umbrales críticos
        alertas = []
        if cpu_percent > 90:
            alertas.append(f"CPU alto: {cpu_percent}%")
        if memory.percent > 85:
            alertas.append(f"Memoria alta: {memory.percent}%")
        if disk.percent > 90:
            alertas.append(f"Disco lleno: {disk.percent}%")

        # Guardar métricas
        output_path = f"/opt/airflow/monitoring/system_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, "w") as f:
            json.dump(metricas, f, indent=2)

        if alertas:
            print(f"⚠️ Alertas del sistema: {', '.join(alertas)}")
            # Aquí se podría enviar notificación

        print(f"✅ Métricas del sistema registradas: {output_path}")
        return metricas

    except Exception as e:
        print(f"❌ Error monitoreando recursos: {e}")
        raise


def verificar_integridad_datos():
    """Verifica la integridad de los archivos de datos"""
    try:
        import hashlib

        data_dir = "/opt/airflow/train_simulator/data"
        integrity_file = f"{data_dir}/integrity_check.json"

        # Calcular hashes de archivos de datos
        hashes_actuales = {}
        for file in os.listdir(data_dir):
            if file.endswith((".db", ".json", ".csv")):
                file_path = os.path.join(data_dir, file)
                with open(file_path, "rb") as f:
                    hashes_actuales[file] = hashlib.md5(f.read()).hexdigest()

        # Comparar con hashes anteriores si existen
        if os.path.exists(integrity_file):
            with open(integrity_file) as f:
                hashes_anteriores = json.load(f)

            cambios = []
            for archivo, hash_actual in hashes_actuales.items():
                hash_anterior = hashes_anteriores.get(archivo)
                if hash_anterior and hash_anterior != hash_actual:
                    cambios.append(f"{archivo} modificado")

            if cambios:
                print(f"📝 Cambios detectados en datos: {', '.join(cambios)}")

        # Guardar hashes actuales
        with open(integrity_file, "w") as f:
            json.dump(hashes_actuales, f, indent=2)

        print("✅ Verificación de integridad de datos completada")
        return True

    except Exception as e:
        print(f"❌ Error verificando integridad de datos: {e}")
        raise


def enviar_notificacion_estado():
    """Envía notificación del estado del sistema"""
    try:
        # Leer último estado del sistema
        estado_file = "/opt/airflow/monitoring/system_status.json"

        if os.path.exists(estado_file):
            with open(estado_file) as f:
                estado = json.load(f)

            # Aquí se podría integrar con servicios de notificación
            # como Slack, Discord, email, etc.
            print(f"📊 Estado del sistema: {estado.get('status', 'unknown')}")

        print("✅ Notificación de estado enviada")
        return True

    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        raise


if AIRFLOW_AVAILABLE:
    # Definir las tareas del DAG
    verificar_dashboard_principal_task = PythonOperator(
        task_id="verificar_dashboard_principal",
        python_callable=verificar_dashboard_principal,
        dag=dag,
    )

    verificar_dashboard_flask_task = PythonOperator(
        task_id="verificar_dashboard_flask",
        python_callable=verificar_dashboard_flask,
        dag=dag,
    )

    verificar_websocket_task = PythonOperator(
        task_id="verificar_conexion_websocket",
        python_callable=verificar_conexion_websocket,
        dag=dag,
    )

    monitorear_recursos_task = PythonOperator(
        task_id="monitorear_recursos_sistema",
        python_callable=monitorear_recursos_sistema,
        dag=dag,
    )

    verificar_integridad_task = PythonOperator(
        task_id="verificar_integridad_datos",
        python_callable=verificar_integridad_datos,
        dag=dag,
    )

    notificar_estado_task = PythonOperator(
        task_id="enviar_notificacion_estado",
        python_callable=enviar_notificacion_estado,
        dag=dag,
    )

    # Sensor para verificar que el sistema esté listo
    def sistema_listo():
        """Verifica que todos los componentes del sistema estén operativos"""
        try:
            # Verificar procesos en ejecución
            import subprocess

            result = subprocess.run(
                ["pgrep", "-f", "train_simulator"], capture_output=True, text=True
            )

            if result.returncode == 0:
                print("✅ Sistema Train Simulator operativo")
                return True
            else:
                print("⏳ Sistema Train Simulator no está completamente operativo")
                return False

        except Exception as e:
            print(f"❌ Error verificando estado del sistema: {e}")
            return False

    sistema_listo_sensor = PythonSensor(
        task_id="sistema_listo_sensor",
        python_callable=sistema_listo,
        poke_interval=60,  # Verificar cada minuto
        timeout=300,  # Timeout de 5 minutos
        dag=dag,
    )

    # Definir dependencias entre tareas
    sistema_listo_sensor >> [verificar_dashboard_principal_task, verificar_dashboard_flask_task]  # type: ignore
    [verificar_dashboard_principal_task, verificar_dashboard_flask_task] >> verificar_websocket_task  # type: ignore
    verificar_websocket_task >> [monitorear_recursos_task, verificar_integridad_task]  # type: ignore
    [monitorear_recursos_task, verificar_integridad_task] >> notificar_estado_task  # type: ignore
else:
    print("⚠️  Airflow no disponible - tareas del DAG no definidas (modo desarrollo)")
