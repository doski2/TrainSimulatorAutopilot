#!/usr/bin/env python3
"""
Script de ejemplo para interactuar con Apache Airflow
desde el sistema Train Simulator Autopilot

Este script demuestra cómo:
1. Ejecutar DAGs manualmente
2. Verificar estado de DAGs
3. Obtener información de tareas
4. Integrar con el sistema existente
"""

import shlex
import subprocess
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def ejecutar_comando_airflow(comando, descripcion):
    """Ejecuta un comando de Airflow y maneja errores

    Security: Commands are parsed with shlex.split() to prevent shell injection (CWE-78)
    """
    try:
        print(f"🔄 {descripcion}...")
        # Security: Use shlex.split() to safely parse command string without shell=True
        cmd_list = shlex.split(comando)
        result = subprocess.run(
            cmd_list, shell=False, capture_output=True, text=True, cwd=str(project_root)
        )

        if result.returncode == 0:
            print(f"✅ {descripcion} completado")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Error en {descripcion}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Excepción ejecutando {descripcion}: {e}")
        return False


def verificar_estado_dag(dag_id):
    """Verifica el estado de un DAG específico"""
    comando = f"docker-compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags show {dag_id}"
    return ejecutar_comando_airflow(comando, f"Verificando estado del DAG {dag_id}")


def ejecutar_dag_manualmente(dag_id):
    """Ejecuta un DAG manualmente"""
    comandos = [
        f"docker-compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags unpause {dag_id}",
        f"docker-compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags trigger {dag_id}",
    ]

    for comando in comandos:
        if not ejecutar_comando_airflow(comando, f"Ejecutando DAG {dag_id}"):
            return False

    return True


def listar_dags_disponibles():
    """Lista todos los DAGs disponibles"""
    comando = (
        "docker-compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags list"
    )
    return ejecutar_comando_airflow(comando, "Listando DAGs disponibles")


def verificar_conexion_airflow():
    """Verifica que Airflow esté ejecutándose correctamente"""
    try:
        import requests

        # Verificar webserver
        response = requests.get("http://localhost:8080/health", timeout=10)
        if response.status_code == 200:
            print("✅ Airflow webserver operativo")
            return True
        else:
            print(f"❌ Airflow webserver respondió con código: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando a Airflow: {e}")
        print("💡 Asegúrate de que Airflow esté ejecutándose con: ./init_airflow.sh")
        return False


def mostrar_menu():
    """Muestra el menú de opciones disponibles"""
    print("\n" + "=" * 60)
    print("🚂 TRAIN SIMULATOR AUTOPILOT - AIRFLOW INTEGRATION")
    print("=" * 60)
    print("1. Verificar estado de Airflow")
    print("2. Listar DAGs disponibles")
    print("3. Ejecutar DAG de reportes")
    print("4. Ejecutar DAG de monitoreo")
    print("5. Ejecutar DAG de mantenimiento")
    print("6. Ejecutar DAG de demostración")
    print("7. Ver estado detallado de un DAG")
    print("8. Salir")
    print("=" * 60)


def ejecutar_dag_interactivo(dag_id, nombre):
    """Ejecuta un DAG y muestra feedback al usuario"""
    print(f"\n🔄 Ejecutando {nombre}...")

    if ejecutar_dag_manualmente(dag_id):
        print(f"✅ {nombre} ejecutado exitosamente")
        print("📊 Puedes ver el progreso en: http://localhost:8080")
    else:
        print(f"❌ Error ejecutando {nombre}")


def main():
    """Función principal del script"""
    while True:
        mostrar_menu()

        try:
            opcion = input("Selecciona una opción (1-8): ").strip()

            if opcion == "1":
                if verificar_conexion_airflow():
                    print("🎉 Airflow está listo para usar!")
                else:
                    print("⚠️ Airflow no está disponible")

            elif opcion == "2":
                listar_dags_disponibles()

            elif opcion == "3":
                ejecutar_dag_interactivo(
                    "train_simulator_reports_dag", "DAG de Reportes del Sistema"
                )

            elif opcion == "4":
                ejecutar_dag_interactivo(
                    "train_simulator_monitoring_dag", "DAG de Monitoreo Continuo"
                )

            elif opcion == "5":
                ejecutar_dag_interactivo("train_simulator_maintenance_dag", "DAG de Mantenimiento")

            elif opcion == "6":
                ejecutar_dag_interactivo(
                    "train_simulator_custom_operators_demo_dag",
                    "DAG de Demostración con Operadores Personalizados",
                )

            elif opcion == "7":
                dag_id = input("Ingresa el ID del DAG: ").strip()
                if dag_id:
                    verificar_estado_dag(dag_id)
                else:
                    print("❌ ID de DAG no válido")

            elif opcion == "8":
                print("👋 ¡Hasta luego!")
                break

            else:
                print("❌ Opción no válida. Por favor selecciona 1-8.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()
