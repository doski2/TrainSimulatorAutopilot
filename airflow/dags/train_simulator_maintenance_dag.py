"""
Train Simulator Autopilot - Mantenimiento y Backup DAG

Este DAG automatiza tareas de mantenimiento, backup y limpieza del sistema
Train Simulator Autopilot para asegurar estabilidad y recuperación de datos.

NOTA: Este archivo está diseñado para ejecutarse dentro del contenedor Docker de Airflow.
Los errores de importación mostrados por Pylance son esperados cuando se edita fuera del entorno Docker.
"""

import json
import os
import shutil
import sys
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

# Importaciones condicionales para type checking y runtime
if TYPE_CHECKING:
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.dummy import DummyOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore

    from airflow import DAG  # type: ignore

# Importaciones runtime con fallback
try:
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.dummy import DummyOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore

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

    class DummyOperator:
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
    "retry_delay": timedelta(minutes=10),
    "catchup": False,
}

# Definir el DAG solo si Airflow está disponible
if AIRFLOW_AVAILABLE:
    dag = DAG(
        "train_simulator_maintenance",
        default_args=default_args,
        description="DAG para mantenimiento y backup del sistema Train Simulator Autopilot",
        schedule_interval="0 2 * * *",  # Todos los días a las 2 AM
        max_active_runs=1,
        tags=["train_simulator", "maintenance", "backup"],
    )
else:
    # DAG dummy para desarrollo
    dag = None
    print("ℹ️ Ejecutando en modo desarrollo - DAG de mantenimiento no disponible")
    print("💡 Para usar este DAG, ejecuta en el entorno Docker de Airflow")


def crear_backup_completo():
    """Crea un backup completo del sistema"""
    try:
        # Definir rutas
        base_dir = "/opt/airflow/train_simulator"
        backup_dir = "/opt/airflow/backups"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"train_simulator_backup_{timestamp}"

        # Crear directorio de backup
        backup_path = os.path.join(backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)

        # Archivos y directorios a respaldar
        items_to_backup = [
            "data/",
            "config.ini",
            "config.ini.production",
            "reports/",
            "logs/",
        ]

        total_size = 0
        backed_up_files = []

        for item in items_to_backup:
            src_path = os.path.join(base_dir, item)
            dst_path = os.path.join(backup_path, item)

            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    # Calcular tamaño del directorio
                    for dirpath, _, filenames in os.walk(dst_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            total_size += os.path.getsize(filepath)
                    backed_up_files.append(f"DIR: {item}")
                else:
                    shutil.copy2(src_path, dst_path)
                    total_size += os.path.getsize(dst_path)
                    backed_up_files.append(f"FILE: {item}")

        # Crear archivo de metadatos del backup
        metadata = {
            "timestamp": timestamp,
            "backup_name": backup_name,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files_backed_up": backed_up_files,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
            },
        }

        metadata_path = os.path.join(backup_path, "backup_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        # Comprimir el backup
        compressed_backup = f"{backup_path}.tar.gz"
        shutil.make_archive(backup_path, "gztar", backup_path)

        # Limpiar directorio descomprimido
        shutil.rmtree(backup_path)

        print(f"✅ Backup completo creado: {compressed_backup}")
        print(f"📊 Tamaño del backup: {metadata['total_size_mb']} MB")
        print(f"📁 Archivos respaldados: {len(backed_up_files)}")

        return compressed_backup

    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        raise


def limpiar_backups_antiguos():
    """Limpia backups antiguos (mantener últimos 30 días)"""
    try:
        backup_dir = "/opt/airflow/backups"
        cutoff_date = datetime.now() - timedelta(days=30)

        if not os.path.exists(backup_dir):
            print("⚠️ Directorio de backups no existe")
            return

        backups_eliminados = []
        espacio_liberado = 0

        for filename in os.listdir(backup_dir):
            if filename.startswith("train_simulator_backup_") and filename.endswith(".tar.gz"):
                filepath = os.path.join(backup_dir, filename)

                # Extraer timestamp del nombre del archivo
                try:
                    timestamp_str = filename.replace("train_simulator_backup_", "").replace(
                        ".tar.gz", ""
                    )
                    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                    if file_date < cutoff_date:
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        backups_eliminados.append(filename)
                        espacio_liberado += file_size

                except ValueError:
                    print(f"⚠️ Nombre de archivo inválido: {filename}")
                    continue

        if backups_eliminados:
            print(f"🗑️ Backups antiguos eliminados: {len(backups_eliminados)}")
            print(f"💾 Espacio liberado: {round(espacio_liberado / (1024*1024), 2)} MB")
            print(f"📝 Archivos eliminados: {', '.join(backups_eliminados)}")
        else:
            print("✅ No hay backups antiguos para eliminar")

    except Exception as e:
        print(f"❌ Error limpiando backups antiguos: {e}")
        raise


def optimizar_base_datos():
    """Optimiza y repara bases de datos"""
    try:
        import sqlite3

        data_dir = "/opt/airflow/train_simulator/data"
        optimized_dbs = []

        if not os.path.exists(data_dir):
            print("⚠️ Directorio de datos no existe")
            return

        for filename in os.listdir(data_dir):
            if filename.endswith(".db"):
                db_path = os.path.join(data_dir, filename)

                try:
                    # Conectar y optimizar
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    # Ejecutar comandos de optimización
                    cursor.execute("VACUUM")
                    cursor.execute("ANALYZE")

                    # Obtener estadísticas
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()

                    conn.commit()
                    conn.close()

                    optimized_dbs.append(filename)
                    print(f"✅ Base de datos optimizada: {filename} ({len(tables)} tablas)")

                except Exception as db_error:
                    print(f"❌ Error optimizando {filename}: {db_error}")
                    continue

        if optimized_dbs:
            print(f"📊 Bases de datos optimizadas: {len(optimized_dbs)}")
        else:
            print("ℹ️ No se encontraron bases de datos para optimizar")

    except Exception as e:
        print(f"❌ Error en optimización de base de datos: {e}")
        raise


def verificar_espacio_disco():
    """Verifica el espacio disponible en disco y alerta si es bajo"""
    try:
        import psutil

        disk = psutil.disk_usage("/")
        espacio_libre_gb = disk.free / (1024**3)
        porcentaje_libre = 100 - disk.percent

        print(f"💾 Espacio en disco: {espacio_libre_gb:.2f} GB libres ({porcentaje_libre:.1f}%)")

        if espacio_libre_gb < 5:  # Menos de 5GB libres
            print("🚨 ALERTA: Espacio en disco muy bajo!")
            # Aquí se podría enviar notificación crítica
            raise Exception(f"Espacio en disco crítico: {espacio_libre_gb:.2f} GB libres")

        elif espacio_libre_gb < 10:  # Menos de 10GB libres
            print("⚠️ ADVERTENCIA: Espacio en disco bajo")

        else:
            print("✅ Espacio en disco adecuado")

        return {
            "espacio_libre_gb": espacio_libre_gb,
            "porcentaje_libre": porcentaje_libre,
            "status": (
                "OK"
                if espacio_libre_gb >= 10
                else "WARNING" if espacio_libre_gb >= 5 else "CRITICAL"
            ),
        }

    except Exception as e:
        print(f"❌ Error verificando espacio en disco: {e}")
        raise


def actualizar_estadisticas_sistema():
    """Actualiza estadísticas y métricas del sistema"""
    try:
        stats_file = "/opt/airflow/maintenance/system_stats.json"

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(stats_file), exist_ok=True)

        # Recopilar estadísticas
        stats = {
            "timestamp": datetime.now().isoformat(),
            "uptime_days": None,  # Se podría calcular con psutil
            "total_backups": (
                len(
                    [
                        f
                        for f in os.listdir("/opt/airflow/backups")
                        if f.startswith("train_simulator_backup_")
                    ]
                )
                if os.path.exists("/opt/airflow/backups")
                else 0
            ),
            "total_reports": (
                len([f for f in os.listdir("/opt/airflow/reports") if f.endswith(".json")])
                if os.path.exists("/opt/airflow/reports")
                else 0
            ),
            "database_size_mb": None,
            "log_size_mb": None,
        }

        # Calcular tamaños
        try:
            data_dir = "/opt/airflow/train_simulator/data"
            if os.path.exists(data_dir):
                total_size = 0
                for dirpath, _, filenames in os.walk(data_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(filepath)
                stats["database_size_mb"] = round(total_size / (1024 * 1024), 2)
        except Exception:
            pass

        try:
            logs_dir = "/opt/airflow/logs"
            if os.path.exists(logs_dir):
                total_size = 0
                for dirpath, _, filenames in os.walk(logs_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(filepath)
                stats["log_size_mb"] = round(total_size / (1024 * 1024), 2)
        except Exception:
            pass

        # Guardar estadísticas
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

        print("✅ Estadísticas del sistema actualizadas")
        print(f"📊 Backups totales: {stats['total_backups']}")
        print(f"📊 Reportes totales: {stats['total_reports']}")
        if stats["database_size_mb"]:
            print(f"💾 Tamaño base de datos: {stats['database_size_mb']} MB")
        if stats["log_size_mb"]:
            print(f"📝 Tamaño logs: {stats['log_size_mb']} MB")

        return stats
        if stats["log_size_mb"]:
            print(f"📝 Tamaño logs: {stats['log_size_mb']} MB")

        return stats

    except Exception as e:
        print(f"❌ Error actualizando estadísticas: {e}")
        raise


# Definir las tareas del DAG
# Definir las tareas del DAG solo si Airflow está disponible
if AIRFLOW_AVAILABLE:
    inicio_mantenimiento = DummyOperator(
        task_id="inicio_mantenimiento",
        dag=dag,
    )

    verificar_espacio_task = PythonOperator(
        task_id="verificar_espacio_disco",
        python_callable=verificar_espacio_disco,
        dag=dag,
    )

    crear_backup_task = PythonOperator(
        task_id="crear_backup_completo",
        python_callable=crear_backup_completo,
        dag=dag,
    )

    optimizar_db_task = PythonOperator(
        task_id="optimizar_base_datos",
        python_callable=optimizar_base_datos,
        dag=dag,
    )

    limpiar_backups_task = PythonOperator(
        task_id="limpiar_backups_antiguos",
        python_callable=limpiar_backups_antiguos,
        dag=dag,
    )

    actualizar_stats_task = PythonOperator(
        task_id="actualizar_estadisticas_sistema",
        python_callable=actualizar_estadisticas_sistema,
        dag=dag,
    )

    fin_mantenimiento = DummyOperator(
        task_id="fin_mantenimiento",
        dag=dag,
    )

    # Definir dependencias entre tareas
    inicio_mantenimiento >> verificar_espacio_task  # type: ignore
    verificar_espacio_task >> crear_backup_task  # type: ignore
    crear_backup_task >> [optimizar_db_task, limpiar_backups_task]  # type: ignore
    [optimizar_db_task, limpiar_backups_task] >> actualizar_stats_task  # type: ignore
    actualizar_stats_task >> fin_mantenimiento  # type: ignore
else:
    # Variables dummy para desarrollo
    inicio_mantenimiento = verificar_espacio_task = crear_backup_task = None
    optimizar_db_task = limpiar_backups_task = actualizar_stats_task = None
    fin_mantenimiento = None
