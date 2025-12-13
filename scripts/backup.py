# backup.py
# Script para automatizar backups de datos y configuración

import os
import shutil
from datetime import datetime


def crear_backup(origen, destino_base):
    """
    Crea un backup con timestamp de la carpeta origen a destino_base.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(destino_base, f"backup_{timestamp}")

    try:
        if os.path.exists(destino):
            shutil.rmtree(destino)
        shutil.copytree(origen, destino)
        print(f"Backup creado: {destino}")
        return destino
    except Exception as e:
        print(f"Error al crear backup: {e}")
        return None


def limpiar_backups_antiguos(destino_base, max_backups=5):
    """
    Elimina backups antiguos, manteniendo solo los más recientes.
    """
    backups = [d for d in os.listdir(destino_base) if d.startswith("backup_")]
    backups.sort(reverse=True)

    if len(backups) > max_backups:
        for backup in backups[max_backups:]:
            shutil.rmtree(os.path.join(destino_base, backup))
            print(f"Backup antiguo eliminado: {backup}")


# Configuración
carpeta_datos = "data"
carpeta_scripts = "scripts"
carpeta_docs = "docs"
carpeta_backups = "backups"

# Crear carpeta de backups si no existe
os.makedirs(carpeta_backups, exist_ok=True)

# Crear backups
crear_backup(carpeta_datos, carpeta_backups)
crear_backup(carpeta_scripts, carpeta_backups)
crear_backup(carpeta_docs, carpeta_backups)

# Limpiar backups antiguos
limpiar_backups_antiguos(carpeta_backups)

# Limpiar backups antiguos
limpiar_backups_antiguos(carpeta_backups)

print("Proceso de backup completado.")
