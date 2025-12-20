#!/usr/bin/env python3
"""
Script para preparar el entorno del simulador copiando archivos necesarios.
"""

import os
import shutil
import argparse

def prepare_simulator(railworks_path, script_source):
    """
    Copia los scripts Lua al directorio plugins de RailWorks.
    """
    plugins_dir = os.path.join(railworks_path, "plugins")
    os.makedirs(plugins_dir, exist_ok=True)

    # Copiar script Lua
    script_dest = os.path.join(plugins_dir, "engineScript.lua")
    shutil.copy2(script_source, script_dest)
    print(f"Script copiado a: {script_dest}")

    # Crear archivo de estado inicial si no existe
    state_file = os.path.join(plugins_dir, "autopilot_state.txt")
    if not os.path.exists(state_file):
        with open(state_file, 'w') as f:
            f.write("autopilot=inactive\n")
        print(f"Archivo de estado creado: {state_file}")

    print("Preparación completada. Reinicia el simulador si está corriendo.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preparar entorno del simulador")
    parser.add_argument("--railworks", default=r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks",
                        help="Ruta a RailWorks")
    parser.add_argument("--script", default="complete_autopilot_lua.lua",
                        help="Script Lua a copiar")

    args = parser.parse_args()

    if not os.path.exists(args.railworks):
        print(f"Error: Ruta RailWorks no existe: {args.railworks}")
        exit(1)

    script_path = os.path.join(os.getcwd(), args.script)
    if not os.path.exists(script_path):
        print(f"Error: Script no encontrado: {script_path}")
        exit(1)

    prepare_simulator(args.railworks, script_path)