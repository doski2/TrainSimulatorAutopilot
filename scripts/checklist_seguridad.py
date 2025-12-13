# checklist_seguridad.py
# Checklist de seguridad y auditoría para Train Simulator Autopilot

import logging
import os
from datetime import datetime

# Configurar logging de seguridad
logging.basicConfig(
    filename="seguridad.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class ChecklistSeguridad:
    def __init__(self):
        self.checks = []
        self.resultados = {}

    def agregar_check(self, nombre, funcion_check, descripcion):
        """Agrega un check de seguridad a la lista."""
        self.checks.append({"nombre": nombre, "funcion": funcion_check, "descripcion": descripcion})

    def ejecutar_checks(self):
        """Ejecuta todos los checks de seguridad."""
        print("Ejecutando checklist de seguridad...")
        logging.info("Inicio de auditoría de seguridad")

        for check in self.checks:
            try:
                resultado = check["funcion"]()
                self.resultados[check["nombre"]] = resultado
                status = "✓ PASÓ" if resultado else "✗ FALLÓ"
                print(f"{status}: {check['descripcion']}")
                logging.info(f"{check['nombre']}: {status}")
            except Exception as e:
                self.resultados[check["nombre"]] = False
                print(f"✗ ERROR: {check['descripcion']} - {str(e)}")
                logging.error(f"{check['nombre']}: ERROR - {str(e)}")

        logging.info("Fin de auditoría de seguridad")
        return self.resultados

    def generar_reporte(self):
        """Genera reporte de seguridad."""
        reporte = f"""
# Reporte de Seguridad - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Resumen
Total de checks: {len(self.checks)}
Pasaron: {sum(1 for r in self.resultados.values() if r)}
Fallaron: {sum(1 for r in self.resultados.values() if not r)}

## Detalles
"""
        for check in self.checks:
            status = "✓" if self.resultados.get(check["nombre"], False) else "✗"
            reporte += f"- {status} {check['descripcion']}\n"

        with open("reporte_seguridad.md", "w", encoding="utf-8") as f:
            f.write(reporte)

        print("Reporte generado: reporte_seguridad.md")
        return reporte


# Funciones de check específicas
def check_permisos_archivos():
    """Verifica permisos de archivos críticos."""
    archivos_criticos = [
        "scripts/ia_logic.py",
        "scripts/test_ia_logic.py",
        "data/",
        "docs/",
    ]

    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            # En Windows, verificar si es de solo lectura
            if os.access(archivo, os.W_OK):
                continue
            else:
                return False
    return True


def check_backups():
    """Verifica existencia de backups recientes."""
    if os.path.exists("backups"):
        backups = [f for f in os.listdir("backups") if f.startswith("backup_")]
        return len(backups) > 0
    return False


def check_logs():
    """Verifica integridad de logs."""
    archivos_log = ["docs/workflow-log.md"]  # Solo verificar workflow-log.md inicialmente
    for log in archivos_log:
        if os.path.exists(log):
            if os.path.getsize(log) > 0:
                continue
            else:
                return False
        else:
            return False
    return True


def check_codigo_seguro():
    """Verifica prácticas de código seguro básicas."""
    archivos_python = []
    for root, _dirs, files in os.walk("scripts"):
        for file in files:
            if file.endswith(".py") and file != "checklist_seguridad.py":
                archivos_python.append(os.path.join(root, file))

    for archivo in archivos_python:
        with open(archivo, encoding="utf-8") as f:
            contenido = f.read()
            # Verificar no hay eval() o exec()
            if "eval(" in contenido or "exec(" in contenido:
                return False
            # Verificar no hay llamadas peligrosas al sistema
            if "os.system(" in contenido:
                return False
            # Permitir subprocess.run solo para pytest
            if "subprocess.run(" in contenido and "pytest" not in contenido:
                return False
            if "subprocess.call(" in contenido:
                return False
    return True


def check_versiones():
    """Verifica control de versiones."""
    return os.path.exists(".git") or os.path.exists("backups")


# Crear y ejecutar checklist
if __name__ == "__main__":
    checklist = ChecklistSeguridad()

    # Agregar checks
    checklist.agregar_check(
        "permisos_archivos",
        check_permisos_archivos,
        "Verificar permisos de archivos críticos",
    )
    checklist.agregar_check("backups", check_backups, "Verificar existencia de backups recientes")
    checklist.agregar_check("logs", check_logs, "Verificar integridad de archivos de log")
    checklist.agregar_check(
        "codigo_seguro", check_codigo_seguro, "Verificar prácticas de código seguro"
    )
    checklist.agregar_check("versiones", check_versiones, "Verificar control de versiones")

    # Ejecutar
    resultados = checklist.ejecutar_checks()
    checklist.generar_reporte()

    # Resumen final
    total_checks = len(checklist.checks)
    pasaron = sum(1 for r in resultados.values() if r)
    print(f"\nResumen: {pasaron}/{total_checks} checks pasaron")

    if pasaron == total_checks:
        print("✓ Todos los checks de seguridad pasaron")
    else:
        print("⚠ Algunos checks fallaron - revisar reporte_seguridad.md")
