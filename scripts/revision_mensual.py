# revision_mensual.py
# Script para revisión mensual automática del proyecto Train Simulator Autopilot

import os
import subprocess
from datetime import datetime


def ejecutar_pruebas():
    """Ejecuta pruebas automáticas."""
    try:
        result = subprocess.run(
            [
                "C:/Users/doski/TrainSimulatorAutopilot/.venv/Scripts/python.exe",
                "-m",
                "pytest",
                "scripts/test_ia_logic.py",
                "-v",
            ],
            capture_output=True,
            text=True,
        )
        return "PASSED" in result.stdout
    except Exception:
        return False


def verificar_backups():
    """Verifica que backups existen."""
    backup_dir = "backups"
    if os.path.exists(backup_dir):
        backups = [f for f in os.listdir(backup_dir) if f.startswith("backup_")]
        return len(backups) > 0
    return False


def generar_reporte_revision():
    """Genera reporte de revisión mensual."""
    fecha = datetime.now().strftime("%Y-%m-%d")

    pruebas_ok = ejecutar_pruebas()
    backups_ok = verificar_backups()

    reporte = f"""
# Revisión Mensual - {fecha}

## Estado de módulos:
- Pruebas automáticas: {'PASSED' if pruebas_ok else 'FAILED'}
- Backups: {'OK' if backups_ok else 'MISSING'}

## Recomendaciones:
- Revisar documentación en docs/
- Ejecutar backup manual si automático falló
- Actualizar dependencias si es necesario

## Próxima revisión: {datetime.now().replace(month=datetime.now().month+1).strftime('%Y-%m-%d')}
"""

    with open(f"docs/revision_{fecha}.md", "w") as f:
        f.write(reporte)

    print(f"Reporte de revisión generado: docs/revision_{fecha}.md")
    return reporte


if __name__ == "__main__":
    generar_reporte_revision()
