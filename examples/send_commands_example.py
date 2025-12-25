#!/usr/bin/env python3
"""
Ejemplo: enviar comandos al simulador usando TSCIntegration.enviar_comandos

Uso:
  python examples/send_commands_example.py --regulator 0.6 --autopilot start

Este script escribe en SendCommand.txt / autopilot_commands.txt (según configuración)
que es lo que lee el plugin Lua y el RailDriver interface.
"""

import argparse
import logging
import os
import time

from tsc_integration import TSCIntegration


def main():
    p = argparse.ArgumentParser(description="Ejemplo enviar comandos al Train Simulator (TSC)")
    p.add_argument("--regulator", type=float, help="Valor de acelerador (0.0-1.0)")
    p.add_argument("--train-brake", type=float, help="Valor freno de tren (0.0-1.0)")
    p.add_argument("--autopilot", choices=("start", "stop"), help="Arrancar/parar autopilot")
    p.add_argument("--plugins-dir", type=str, help="Anular carpeta plugins (ej: C:\\...\\RailWorks\\plugins)")
    p.add_argument("--dry-run", action="store_true", help="No escribir archivos, sólo mostrar lo que se enviaría")
    p.add_argument("--wait-plugin", action="store_true", help="Esperar a que el plugin autopilot reporte 'on' antes de enviar")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("send_commands_example")

    t = TSCIntegration()

    # Opción para anular donde escribir (útil en pruebas)
    if args.plugins_dir:
        sendpath = os.path.join(args.plugins_dir, "SendCommand.txt")
        logger.info("Anulando ruta de archivo de comandos: %s", sendpath)
        t.ruta_archivo_comandos = sendpath
        t.write_lua_commands = True

    # Verificar conexión básica
    if not t.conectar():
        logger.warning("No se detectó SendCommand.txt o no existe GetData.txt; asegúrate que RailWorks y el plugin estén activos")
    else:
        logger.info("Usando archivo de comandos: %s", t.ruta_archivo_comandos)

    # Opcional: esperar a que el plugin autopilot esté 'on'
    if args.wait_plugin:
        logger.info("Esperando a que el plugin autopilot reporte 'on' (timeout 5s)")
        ok = t.wait_for_autopilot_state('on', timeout=5.0)
        if not ok:
            logger.warning("Plugin autopilot no respondió 'on' dentro del timeout; continuando de todos modos")

    # Construir diccionario de comandos (usamos las claves en español que mapea la clase)
    comandos = {}
    if args.regulator is not None:
        comandos['acelerador'] = max(0.0, min(1.0, float(args.regulator)))
    if args.train_brake is not None:
        comandos['freno_tren'] = max(0.0, min(1.0, float(args.train_brake)))
    if args.autopilot:
        comandos['autopilot'] = True if args.autopilot == 'start' else False

    if not comandos:
        logger.info("No hay comandos a enviar. Usa --regulator, --train-brake o --autopilot")
        return

    logger.info("Comandos a enviar: %s", comandos)

    if args.dry_run:
        logger.info("Dry-run: no se escribirán archivos")
        return

    ok = t.enviar_comandos(comandos)
    if ok:
        logger.info("Comandos escritos correctamente. Verifica archivos:")
        logger.info("  - %s", t.ruta_archivo_comandos)
        logger.info("  - %s", os.path.join(os.path.dirname(t.ruta_archivo_comandos), "autopilot_commands.txt"))
    else:
        logger.error("Fallo al enviar comandos")

    # Pequeña espera para que el plugin lea el archivo (si está activo)
    time.sleep(0.2)


if __name__ == '__main__':
    main()
