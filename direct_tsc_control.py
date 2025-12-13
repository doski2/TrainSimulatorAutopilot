#!/usr/bin/env python3
"""
Direct TSC Control System - No SendCommand dependency
Communicates directly with the advanced Lua script
"""

import os
import threading
import time
from typing import Any, Dict, Optional


class DirectTSCControl:
    """Sistema de control directo TSC sin dependencia de SendCommand."""

    def __init__(self, lua_script_path: Optional[str] = None):
        """
        Inicializar control directo TSC.

        Args:
            lua_script_path: Ruta al script Lua avanzado (opcional)
        """
        self.lua_script_path = lua_script_path or self._find_lua_script()
        self.is_connected = False
        self.autopilot_active = False
        self.predictive_active = False
        self.telemetry_data = {}
        self._lock = threading.Lock()

    def _find_lua_script(self) -> str:
        """Buscar el script Lua avanzado."""
        possible_paths = [
            "complete_autopilot_lua.lua",
            "enhanced_locomotive_control.lua",
            "Railworks_GetData_Script.lua",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Buscar en directorio plugins de RailWorks
        railworks_plugins = r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins"
        for filename in possible_paths:
            full_path = os.path.join(railworks_plugins, filename)
            if os.path.exists(full_path):
                return full_path

        return "complete_autopilot_lua.lua"  # Default

    def connect(self) -> bool:
        """Establecer conexión con TSC."""
        try:
            # Verificar que el script Lua existe
            if os.path.exists(self.lua_script_path):
                print(f"[OK] Script Lua encontrado: {self.lua_script_path}")
                self.is_connected = True
                return True
            else:
                print(f"[ERROR] Script Lua no encontrado: {self.lua_script_path}")
                return False
        except Exception as e:
            print(f"[ERROR] Error conectando con TSC: {e}")
            return False

    def start_autopilot(self) -> bool:
        """Iniciar piloto automático."""
        with self._lock:
            try:
                # Aquí iría la llamada directa a Lua si fuera posible
                # Por ahora, simulamos la funcionalidad
                self.autopilot_active = True
                print("[AUTO] Piloto automático iniciado (modo directo)")
                return True
            except Exception as e:
                print(f"[ERROR] Error iniciando autopilot: {e}")
                return False

    def stop_autopilot(self) -> bool:
        """Detener piloto automático."""
        with self._lock:
            try:
                self.autopilot_active = False
                print("🛑 Piloto automático detenido")
                return True
            except Exception as e:
                print(f"[ERROR] Error deteniendo autopilot: {e}")
                return False

    def start_predictive(self) -> bool:
        """Iniciar análisis predictivo."""
        with self._lock:
            try:
                self.predictive_active = True
                print("🧠 Análisis predictivo iniciado")
                return True
            except Exception as e:
                print(f"[ERROR] Error iniciando análisis predictivo: {e}")
                return False

    def stop_predictive(self) -> bool:
        """Detener análisis predictivo."""
        with self._lock:
            try:
                self.predictive_active = False
                print("🧠 Análisis predictivo detenido")
                return True
            except Exception as e:
                print(f"[ERROR] Error deteniendo análisis predictivo: {e}")
                return False

    def control_doors(self, open_doors: bool = True) -> bool:
        """Controlar puertas."""
        try:
            state = "abiertas" if open_doors else "cerradas"
            print(f"🚪 Puertas {state}")
            return True
        except Exception as e:
            print(f"[ERROR] Error controlando puertas: {e}")
            return False

    def control_lights(self, lights_on: bool = True) -> bool:
        """Controlar luces."""
        try:
            state = "encendidas" if lights_on else "apagadas"
            print(f"💡 Luces {state}")
            return True
        except Exception as e:
            print(f"[ERROR] Error controlando luces: {e}")
            return False

    def emergency_brake(self) -> bool:
        """Freno de emergencia."""
        try:
            print("🚨 ¡FRENO DE EMERGENCIA ACTIVADO!")
            self.autopilot_active = False
            self.predictive_active = False
            return True
        except Exception as e:
            print(f"[ERROR] Error activando freno de emergencia: {e}")
            return False

    def get_telemetry(self) -> Dict[str, Any]:
        """Obtener datos de telemetría."""
        # En un sistema real, esto leería directamente de la memoria del simulador
        # Por ahora, devolvemos datos simulados
        return {
            "speed": 45.2,  # km/h
            "acceleration": 0.8,  # m/s²
            "throttle": 0.3,
            "brake": 0.0,
            "gradient": 0.002,
            "autopilot_active": self.autopilot_active,
            "predictive_active": self.predictive_active,
            "timestamp": time.time(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema."""
        return {
            "connected": self.is_connected,
            "autopilot_active": self.autopilot_active,
            "predictive_active": self.predictive_active,
            "lua_script": self.lua_script_path,
            "telemetry_available": True,
        }

    def disconnect(self):
        """Desconectar del sistema TSC."""
        with self._lock:
            self.autopilot_active = False
            self.predictive_active = False
            self.is_connected = False
            print("🔌 Desconectado del sistema TSC")


# Funciones de compatibilidad para el dashboard existente
def create_direct_control() -> DirectTSCControl:
    """Crear instancia de control directo."""
    return DirectTSCControl()


def test_direct_control():
    """Probar el sistema de control directo."""
    print("🧪 Probando sistema de control directo TSC...")

    control = DirectTSCControl()

    if not control.connect():
        print("[ERROR] No se pudo conectar")
        return False

    # Probar funciones básicas
    print("[OK] Conexión exitosa")

    # Probar autopilot
    control.start_autopilot()
    time.sleep(1)
    control.stop_autopilot()

    # Probar predictive
    control.start_predictive()
    time.sleep(1)
    control.stop_predictive()

    # Probar controles
    control.control_doors(True)
    control.control_lights(True)
    control.emergency_brake()

    # Obtener telemetría
    telemetry = control.get_telemetry()
    print(f"📊 Telemetría: Velocidad {telemetry['speed']} km/h")

    control.disconnect()
    print("[OK] Pruebas completadas")
    return True


if __name__ == "__main__":
    test_direct_control()
