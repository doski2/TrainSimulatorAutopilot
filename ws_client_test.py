#!/usr/bin/env python3
"""
ws_client_test.py
Cliente de prueba que se conecta al servidor Socket.IO local y muestra events `telemetry_update`.
"""
import argparse
import os
import time
from typing import Optional

import socketio

# Default server URL - changed to 5001 (dashboard default uses 5001)
SERVER_URL = os.environ.get("TSA_SERVER_URL", "http://localhost:5001")

sio: Optional[socketio.Client] = None


def connect():
    print("[CLIENT] Connected to server")
    # solicitar telemetría inmediata
    try:
        if sio:
            sio.emit("request_telemetry")
            print("[CLIENT] Emitted request_telemetry")
        else:
            print("[CLIENT] Socket.IO client not available")
    except Exception as e:
        print("[CLIENT] Error emitting request_telemetry:", e)


def disconnect():
    print("[CLIENT] Disconnected from server")


def on_telemetry_update(data):
    print("\n[CLIENT] telemetry_update received:")
    try:
        # Mostrar resumen: keys y velocidad
        telemetry = data.get("telemetry") if isinstance(data, dict) else None
        if telemetry and isinstance(telemetry, dict):
            # Compressed data may include fields; print velocidad_actual if present
            vel = telemetry.get("velocidad_actual")
            print("  velocidad_actual (from telemetry):", vel)
            # print full telemetry small subset
            subset_keys = [
                "velocidad_actual",
                "aceleracion",
                "rpm",
                "presion_tubo_freno",
                "presion_tubo_freno_presente",
                "presion_tubo_freno_mostrada_presente",
                "presion_freno_loco_mostrada_presente",
                "presion_deposito_auxiliar_presente",
                "senal_principal",
                "senal_avanzada",
                "senal_procesada",
            ]
            for k in subset_keys:
                print(f"   {k}:", telemetry.get(k))
        else:
            print("  telemetry payload not dict; raw:", data)
        # Además de la telemetría, algunos servidores incluyen listas de alertas activas
        try:
            alerts_list = data.get("active_alerts_list") if isinstance(data, dict) else None
            if alerts_list:
                print(f"  active_alerts_list: {len(alerts_list)} alerts (showing up to 3):")
                for a in alerts_list[:3]:
                    # a debería ser un dict con id, severity, name, message
                    aid = a.get("id") if isinstance(a, dict) else a
                    sev = a.get("severity") if isinstance(a, dict) else None
                    name = a.get("name") if isinstance(a, dict) else None
                    msg = a.get("message") if isinstance(a, dict) else None
                    print(f"    - {aid} | {sev} | {name} | {msg}")
            else:
                # Fallback a la lista corta de nuevas alertas si existe
                alerts_short = data.get("alerts") if isinstance(data, dict) else None
                if alerts_short:
                    print(f"  new alerts this cycle: {len(alerts_short)}")
        except Exception as e:
            print("[CLIENT] Error processing active_alerts_list:", e)
    except Exception as e:
        print("[CLIENT] Error processing telemetry_update:", e)


def on_system_message(msg):
    print("[CLIENT] system_message:", msg)


def main(listen_seconds: float = 10.0):
    print("[CLIENT] Starting Socket.IO test client")

    global sio
    try:
        sio = socketio.Client(logger=False, engineio_logger=False)
    except Exception as e:
        print(f"[CLIENT] Error creating Socket.IO client: {e}")
        return

    # Configurar event handlers
    sio.on("connect", connect)
    sio.on("disconnect", disconnect)
    sio.on("telemetry_update", on_telemetry_update)
    sio.on("system_message", on_system_message)

    try:
        sio.connect(SERVER_URL, wait=True, wait_timeout=5)
    except Exception as e:
        print("[CLIENT] Could not connect to server:", e)
        return

    # Escuchar durante `listen_seconds`
    try:
        time_to_listen = listen_seconds or 10.0
        print(f"[CLIENT] Listening for {time_to_listen} seconds...")
        t0 = time.time()
        while time.time() - t0 < time_to_listen:
            time.sleep(0.1)
    finally:
        try:
            sio.disconnect()
        except Exception as e:
            print(f"[CLIENT] Error disconnecting: {e}")
        print("[CLIENT] Exiting")


if __name__ == "__main__":
    # Add CLI parsing to make it easier to override the default server URL
    parser = argparse.ArgumentParser(
        description="Socket.IO demo client for Train Simulator Autopilot"
    )
    parser.add_argument(
        "--server",
        "-s",
        dest="server_url",
        default=None,
        help="Socket.IO server URL (e.g. http://localhost:5001)",
    )
    parser.add_argument(
        "--listen",
        "-l",
        dest="listen",
        type=float,
        default=10.0,
        help="Seconds to listen for telemetry updates",
    )
    args = parser.parse_args()

    if args.server_url:
        SERVER_URL = args.server_url

    # Allow environment variable to override as well
    SERVER_URL = os.environ.get("TSA_SERVER_URL", SERVER_URL)
    print(f"[CLIENT] Connecting to {SERVER_URL}")
    # Pass listen duration to the client
    time_to_listen = args.listen
    main(listen_seconds=time_to_listen)
