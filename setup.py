#!/usr/bin/env python3
"""
setup.py - Script de instalación mejorado para Train Simulator Autopilot
Actualizado: 30 de noviembre de 2025
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"\n🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Verifica la versión de Python."""
    print(f"🐍 Versión de Python: {sys.version}")
    return True


def install_dependencies(requirements_file, description):
    """Instala dependencias desde un archivo requirements."""
    if os.path.exists(requirements_file):
        return run_command(f"pip install -r {requirements_file}", f"Instalando {description}")
    else:
        print(f"⚠️  Archivo {requirements_file} no encontrado, omitiendo...")
        return True


def setup_environment():
    """Configura el entorno de desarrollo."""
    print("\n🚀 Configurando entorno de Train Simulator Autopilot...")

    # Verificar Python
    if not check_python_version():
        return False

    # Actualizar pip
    if not run_command("python -m pip install --upgrade pip", "Actualizando pip"):
        return False

    # Instalar dependencias principales
    if not install_dependencies("requirements.txt", "dependencias principales"):
        return False

    # Instalar dependencias de desarrollo (opcional)
    dev_choice = input("\n¿Instalar dependencias de desarrollo? (y/N): ").lower().strip()
    if dev_choice == "y":
        install_dependencies("requirements-dev.txt", "dependencias de desarrollo")

    # Verificar instalación
    print("\n🔍 Verificando instalación...")
    try:
        import flask  # noqa: F401
        import numpy  # noqa: F401
        import pandas  # noqa: F401
        import websockets  # noqa: F401

        print("✅ Dependencias principales verificadas")
    except ImportError as e:
        print(f"❌ Error importando dependencias: {e}")
        return False

    # Crear directorios necesarios
    dirs_to_create = ["logs", "data", "reports", "backups"]
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Directorio '{dir_name}' creado/verificado")

    print("\n🎉 ¡Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Configurar variables de entorno en .env")
    print("2. Ejecutar 'python web_dashboard.py' para iniciar el dashboard")
    print("3. Ejecutar 'docker-compose up -d' para iniciar Airflow")
    print("4. Ver documentación en docs/ para más información")

    return True


def main():
    parser = argparse.ArgumentParser(description="Instalador de Train Simulator Autopilot")
    parser.add_argument("--dev", action="store_true", help="Instalar dependencias de desarrollo")
    parser.add_argument(
        "--skip-checks", action="store_true", help="Omitir verificación de versión de Python"
    )

    args = parser.parse_args()

    if not args.skip_checks and not check_python_version():
        sys.exit(1)

    if not setup_environment():
        print("\n❌ La instalación falló. Revisa los errores arriba.")
        sys.exit(1)

    print("\n✨ ¡Listo para usar Train Simulator Autopilot!")


if __name__ == "__main__":
    main()
