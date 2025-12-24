#!/usr/bin/env python3
"""
tsc_integration.py
Módulo principal de integración con Train Simulator Classic
Lee datos del archivo GetData.txt generado por el Raildriver Interface
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

# Importar sistema de logging centralizado
try:
    from logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

# Intentar usar portalocker para bloqueo de archivo cuando esté disponible.
# Si no está instalado, el código cae en el comportamiento de reintentos existente.
try:
    import portalocker

    HAS_PORTALOCKER = True
except Exception:
    portalocker = None
    HAS_PORTALOCKER = False


class TSCIntegration:
    """Clase principal para la integración con Train Simulator Classic."""

    def __init__(self, ruta_archivo=None, fuel_capacity_gallons: Optional[float] = None):
        """Inicializar la integración."""
        logger.info("Inicializando integración con Train Simulator Classic")

        # Permitir ruta personalizada para pruebas
        if ruta_archivo:
            self.ruta_archivo = ruta_archivo
        else:
            self.ruta_archivo = (
                r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"
            )
        # Use absolute path for commands file (Python runs from project directory)
        self.ruta_archivo_comandos = (
            r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt"
        )
        # If True, also write the file that the Lua plugin reads (autopilot_commands.txt).
        # Can be disabled for environments where only the SendCommand file is desired.
        self.write_lua_commands = True
        self.datos_anteriores = {}
        self.timestamp_ultima_lectura = 0
        self.intervalo_lectura = 0.1  # 100ms entre lecturas
        self.simulador_activo = False  # Estado del simulador
        self.timestamp_ultimo_cambio = 0  # Timestamp del último cambio significativo

        # Signal aspect constants
        SIGNAL_UNKNOWN = -1
        SIGNAL_STOP = 0
        SIGNAL_CAUTION = 1
        SIGNAL_PROCEED = 2

        # expose constants for potential external use
        self.SIGNAL_UNKNOWN = SIGNAL_UNKNOWN
        self.SIGNAL_STOP = SIGNAL_STOP
        self.SIGNAL_CAUTION = SIGNAL_CAUTION
        self.SIGNAL_PROCEED = SIGNAL_PROCEED

        # Mapeo de nombres de control a nombres de IA
        self.mapeo_controles = {
            "CurrentSpeed": "velocidad_actual",
            "SpeedometerMPH": "velocimetro_mph",
            "SpeedoType": "tipo_velocimetro",
            "Acceleration": "aceleracion",
            "Gradient": "pendiente",
            # FuelLevel removed from mapping (TSC uses infinite fuel in scenarios)
            "CurrentSpeedLimit": "limite_velocidad",
            "NextSpeedLimitSpeed": "limite_velocidad_siguiente",
            "NextSpeedLimitDistance": "distancia_limite_siguiente",
            "SimulationTime": "tiempo_simulacion",
            "DistanceTravelled": "distancia_recorrida",
            "TractiveEffort": "esfuerzo_traccion",
            "RPM": "rpm",
            "RPMDelta": "rpm",
            "Ammeter": "amperaje",
            "Wheelslip": "deslizamiento_ruedas",
            # Brake Pressure Controls
            "AirBrakePipePressurePSI": "presion_tubo_freno",
            "LocoBrakeCylinderPressurePSI": "presion_freno_loco",
            "TrainBrakeCylinderPressurePSI": "presion_freno_tren",
            # Brake pipe tail end (some mods report this separately)
            "BrakePipePressureTailEnd": "presion_tubo_freno_cola",
            # Engine Control Mappings
            "Regulator": "acelerador",
            "Reverser": "reverser",
            "VirtualBrake": "posicion_freno_tren",
            "DynamicBrake": "freno_dinamico",
            "HandBrake": "freno_mano",
            "EmergencyBrake": "freno_emergencia",
            "CompressorState": "estado_compresor",
            # Signal and Light Mappings
            "SignalAspect": "senal_principal",
            "KVB_SignalAspect": "senal_avanzada",
            "Headlights": "luces",
        }

        # Mapeo de comandos IA a nombres de control Raildriver
        self.mapeo_comandos = {
            "acelerador": "Regulator",  # Para SD40
            "freno_tren": "TrainBrakeControl",
            "freno_dinamico": "DynamicBrake",
            "reverser": "Reverser",  # Changed to Reverser
            # Nuevos controles de locomotora
            # Doors handled by AI in future; remove direct DoorSwitch mapping
            "luces": "Headlights",  # Changed to Headlights
            "freno_emergencia": "EmergencyBrake",  # Changed to EmergencyBrake,
        }

        # Valores anteriores de comandos para evitar envíos innecesarios
        self.comandos_anteriores = {}
        # Fuel capacity handling removed; keep placeholder for compatibility
        self.fuel_capacity_gallons = None
        # Maximum RPM used for inferring RPM when direct RPM control isn't provided
        # Default matches common locomotive max RPM (configurable via API/back-end)
        self.max_engine_rpm = 5000.0
        # Fuel capacity option ignored by integration; configuration removed

        # I/O metrics for monitoring and diagnostics
        # - read_total_retries/write_total_retries: cumulative retry counts
        # - read_last_latency_ms/write_last_latency_ms: latency of last successful op in ms
        # - read_attempts_last/write_attempts_last: attempts used in last call
        self.io_metrics = {
            "read_total_retries": 0,
            "read_last_latency_ms": 0.0,
            "read_attempts_last": 0,
            "write_total_retries": 0,
            "write_last_latency_ms": 0.0,
            "write_attempts_last": 0,
        }

    def _to_float(self, val: Any, default: float = 0.0) -> float:
        """Safely convert a value to float, returning default on failure."""
        try:
            if val is None:
                return default
            return float(val)
        except Exception:
            return default

    def _parse_optional_float(self, val: Any) -> Optional[float]:
        """Parse float and return None if it cannot be parsed."""
        try:
            if val is None:
                return None
            return float(val)
        except Exception:
            return None

    def _snap_to_notch(self, val: float) -> float:
        """Snap a throttle value to the nearest notch (discrete throttle steps).

        Rounds to the closest notch defined in `self.throttle_notches`. On a tie,
        the higher notch is chosen to favour positive movement.
        """
        # Default throttle notches (muescas) if not configured
        if not hasattr(self, "throttle_notches") or not self.throttle_notches:
            # Common 8-step increments plus 0 and 1
            self.throttle_notches = [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]

        try:
            v = float(val)
        except Exception:
            return val

        # Clamp into 0..1
        v = max(0.0, min(1.0, v))

        best = self.throttle_notches[0]
        best_diff = abs(v - best)
        for n in self.throttle_notches[1:]:
            d = abs(v - n)
            # Prefer the closer notch; on exact tie, prefer the higher notch
            if d < best_diff or (d == best_diff and n > best):
                best = n
                best_diff = d
        return best

    def archivo_existe(self) -> bool:
        """Verificar si el archivo GetData.txt existe."""
        return os.path.exists(self.ruta_archivo)

    def get_autopilot_plugin_state(self) -> Optional[str]:
        """Leer el archivo de estado escrito por el plugin Lua (on/off).

        Returns:
            'on'|'off' si el plugin informó estado, None si no hay información.
        """
        try:
            plugins_dir = os.path.dirname(self.ruta_archivo_comandos)
            state_file = os.path.join(plugins_dir, "autopilot_state.txt")
            if os.path.exists(state_file):
                with open(state_file, "r", encoding="utf-8") as f:
                    val = f.read().strip().lower()
                    if val in ("on", "off"):
                        return val
            return None
        except Exception:
            return None

    def is_autopilot_plugin_loaded(self) -> bool:
        """Comprobar si el plugin Lua ha marcado que está cargado."""
        try:
            plugins_dir = os.path.dirname(self.ruta_archivo_comandos)
            loaded_file = os.path.join(plugins_dir, "autopilot_plugin_loaded.txt")
            return os.path.exists(loaded_file)
        except Exception:
            return False

    def wait_for_autopilot_state(self, expected: str, timeout: float = 2.0) -> bool:
        """Esperar hasta que el plugin reporte el estado esperado o timeout.

        Args:
            expected: 'on' or 'off'
            timeout: segundos a esperar

        Returns:
            True si se alcanza el estado esperado, False si timeout.
        """
        import time

        start = time.time()
        while time.time() - start < timeout:
            cur = self.get_autopilot_plugin_state()
            if cur == expected:
                return True
            time.sleep(0.1)
        return False

    def _robust_read_lines(self, retries: int = 3, wait: float = 0.05) -> list[str]:
        """Leer líneas del archivo GetData.txt con reintentos y saneamiento.

        - Reintenta ante errores de E/S (ej. PermissionError por bloqueo del simulador)
        - Normaliza BOM UTF-8 en la primera línea
        - Retorna la lista de líneas leídas (puede estar incompleta; el parser
          ignorará entradas parciales)
        """
        last_exc = None
        start = time.time()
        for attempt in range(1, retries + 1):
            try:
                # Try to use portalocker to obtain a short shared/read lock when available
                if HAS_PORTALOCKER:
                    try:
                        with portalocker.Lock(self.ruta_archivo, 'r', timeout=0.1) as f:
                            lines = f.readlines()
                    except Exception as _e:
                        # Fallback to plain open if lock acquisition fails quickly
                        with open(self.ruta_archivo, encoding="utf-8") as f:
                            lines = f.readlines()
                else:
                    with open(self.ruta_archivo, encoding="utf-8") as f:
                        lines = f.readlines()
                if lines:
                    # Normalizar BOM si existe
                    if lines[0].startswith("\ufeff"):
                        lines[0] = lines[0].lstrip("\ufeff")
                elapsed_ms = (time.time() - start) * 1000.0
                # update metrics
                self.io_metrics["read_attempts_last"] = attempt
                if attempt > 1:
                    self.io_metrics["read_total_retries"] += (attempt - 1)
                self.io_metrics["read_last_latency_ms"] = round(elapsed_ms, 3)
                return lines
            except Exception as e:
                last_exc = e
                logger.warning(
                    "Attempt %d to read %s failed: %s", attempt, self.ruta_archivo, e
                )
                try:
                    time.sleep(wait * attempt)
                except Exception:
                    pass
        # All attempts failed: record attempts and total retries
        elapsed_ms = (time.time() - start) * 1000.0
        self.io_metrics["read_attempts_last"] = retries
        self.io_metrics["read_total_retries"] += retries
        self.io_metrics["read_last_latency_ms"] = round(elapsed_ms, 3)
        logger.exception("Failed to read file %s after %d attempts", self.ruta_archivo, retries)
        raise last_exc

    def leer_datos_archivo(self) -> Optional[Dict[str, Any]]:
        """
        Leer datos del archivo GetData.txt.

        Returns:
            Dict con los datos leídos o None si hay error
        """
        if not self.archivo_existe():
            return None

        try:
            lineas = self._robust_read_lines()

            datos = {}
            i = 0
            while i < len(lineas):
                linea = lineas[i].strip()
                if linea.startswith("ControlName:"):
                    nombre_control = linea.split(":", 1)[1].strip()
                    # Buscar el valor correspondiente (si falta, ignorar la entrada)
                    j = i + 1
                    while j < len(lineas) and not lineas[j].strip().startswith("ControlValue:"):
                        j += 1
                    if j < len(lineas):
                        valor_str = lineas[j].strip().split(":", 1)[1].strip()
                        try:
                            valor = float(valor_str)
                            datos[nombre_control] = valor
                        except ValueError:
                            datos[nombre_control] = valor_str
                    else:
                        # Valor faltante: registrar y continuar (evita crash por escrituras parciales)
                        logger.debug("Ignoring ControlName '%s' without ControlValue (partial write)", nombre_control)
                i += 1

            return datos

        except Exception as e:
            logger.exception("Error leyendo archivo GetData.txt: %s", e)
            return None

    def convertir_datos_ia(self, datos_archivo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertir datos del archivo al formato que espera la IA.

        Args:
            datos_archivo: Datos leídos del archivo

        Returns:
            Datos en formato IA
        """
        datos_ia = {}

        # Mapear controles conocidos
        for nombre_archivo, nombre_ia in self.mapeo_controles.items():
            if nombre_archivo in datos_archivo:
                datos_ia[nombre_ia] = datos_archivo[nombre_archivo]

        # CurrentSpeed del RailDriver viene en m/s (metros por segundo)
        # Convertir de m/s a km/h para mostrar en el dashboard
        if "velocidad_actual" in datos_ia:
            velocidad_ms = abs(datos_ia["velocidad_actual"])  # En m/s
            velocidad_kmh = velocidad_ms * 3.6  # Convertir m/s a km/h (1 m/s = 3.6 km/h)
            datos_ia["velocidad_actual"] = round(velocidad_kmh, 2)

        # Procesar aceleración para separar acelerador y freno
        if "aceleracion" in datos_ia:
            accel = datos_ia["aceleracion"]
            print(f"[DEBUG] Aceleración cruda: {accel}")

            # TEMPORAL: Mostrar valores sin filtro para debugging
            if accel > 0:
                datos_ia["acelerador"] = accel
                datos_ia["freno_tren"] = 0.0
                print(f"[DEBUG] Acelerador: {accel}, Freno: 0.0")
            elif accel < 0:
                datos_ia["acelerador"] = 0.0
                datos_ia["freno_tren"] = -accel  # Convertir a positivo para freno
                print(f"[DEBUG] Acelerador: 0.0, Freno: {-accel}")
            else:
                datos_ia["acelerador"] = 0.0
                datos_ia["freno_tren"] = 0.0
                print("[DEBUG] Acelerador: 0.0, Freno: 0.0")
            # Si rpm es 0, intentar usar RPMDelta (alias) del archivo
            if datos_ia.get("rpm", 0.0) == 0.0 and "RPMDelta" in datos_archivo:
                try:
                    rpm_alt = self._to_float(datos_archivo.get("RPMDelta", 0.0))
                    if rpm_alt != 0.0:
                        datos_ia["rpm"] = rpm_alt
                except Exception as e:
                    print(f"[WARN] Failed to parse RPMDelta for rpm inference: {e}")
                    import traceback

                    traceback.print_exc()

            # Si RPM aún es 0, inferir desde Regulator o VirtualThrottle (si están presentes)
            if datos_ia.get("rpm", 0.0) == 0.0:
                try:
                    if "Regulator" in datos_archivo and datos_archivo.get("Regulator", None) is not None:
                        reg_val = self._to_float(datos_archivo.get("Regulator", 0.0))
                        if reg_val > 0.0:
                            datos_ia["rpm"] = reg_val * self.max_engine_rpm
                            datos_ia["rpm_inferida"] = True
                    elif "VirtualThrottle" in datos_archivo and datos_archivo.get("VirtualThrottle", None) is not None:
                        vt = self._to_float(datos_archivo.get("VirtualThrottle", 0.0))
                        if vt > 0.0:
                            datos_ia["rpm"] = vt * self.max_engine_rpm
                            datos_ia["rpm_inferida"] = True
                except Exception as e:
                    print(f"[WARN] RPM inference failed: {e}")
                    import traceback

                    traceback.print_exc()

            # Mapear RPMSource (depuración) si existe en el archivo
            if "RPMSource" in datos_archivo:
                datos_ia["rpm_fuente"] = datos_archivo.get("RPMSource")

        # Si se proporciona TrainBrakeControl directamente, mapearlo a posicion_freno_tren
        # para unificar el manejo con VirtualBrake y permitir inferencias posteriores.
        try:
            if "TrainBrakeControl" in datos_archivo and "posicion_freno_tren" not in datos_ia:
                try:
                    datos_ia["posicion_freno_tren"] = self._to_float(datos_archivo.get("TrainBrakeControl", 0.0))
                except Exception:
                    datos_ia["posicion_freno_tren"] = 0.0
        except Exception:
            # No bloquear si falla el mapeo; continuar
            pass

        # Priorizar control de freno real (posicion_freno_tren/VirtualBrake) si está disponible
        try:
            if datos_ia.get("posicion_freno_tren") is not None:
                val = datos_ia.get("posicion_freno_tren")
                try:
                    val = self._to_float(val)
                except Exception:
                    val = 0.0
                # Clamp entre 0 y 1
                val = max(0.0, min(1.0, val))
                datos_ia["freno_tren"] = val
            elif "VirtualBrake" in datos_archivo:
                try:
                    vb = self._to_float(datos_archivo.get("VirtualBrake", 0.0))
                    datos_ia["freno_tren"] = max(0.0, min(1.0, vb))
                except Exception as e:
                    print(f"[WARN] VirtualBrake parsing failed: {e}")
                    import traceback

                    traceback.print_exc()
        except Exception as e:
            # No bloquear si hay error; registrar para diagnóstico
            print(f"[WARN] Error processing brake/virtual brake fields: {e}")
            import traceback

            traceback.print_exc()

        # Agregar campos que la IA necesita pero que pueden no estar en el archivo
        datos_ia.setdefault("acelerador", 0.0)
        datos_ia.setdefault("freno_tren", 0.0)
        datos_ia.setdefault("freno_motor", 0.0)
        datos_ia.setdefault("freno_motor_control", 0.0)
        datos_ia.setdefault("freno_dinamico", 0.0)
        datos_ia.setdefault("reverser", 1)
        datos_ia.setdefault("presion_aire", 90.0)
        datos_ia.setdefault("rpm", 0.0)
        datos_ia.setdefault("distancia_parada", 1000.0)
        datos_ia.setdefault("senal_principal", int(self.SIGNAL_UNKNOWN))
        datos_ia.setdefault("senal_avanzada", int(self.SIGNAL_UNKNOWN))
        # Normalizar y procesar la señal que vamos a usar en IA/UI: preferimos la señal avanzada si está disponible
        try:
            se_av = datos_ia.get("senal_avanzada", None)
            se_pr = datos_ia.get("senal_principal", None)
            # Preferir la avanzada si no es UNKNOWN (-1). Si ambas no están, usar UNKNOWN
            if se_av is not None and se_av != self.SIGNAL_UNKNOWN:
                datos_ia["senal_procesada"] = int(se_av)
            elif se_pr is not None and se_pr != self.SIGNAL_UNKNOWN:
                datos_ia["senal_procesada"] = int(se_pr)
            else:
                datos_ia["senal_procesada"] = int(self.SIGNAL_UNKNOWN)
        except Exception:
            datos_ia["senal_procesada"] = int(self.SIGNAL_UNKNOWN)
        # Debug log for signal values (useful to diagnose why signals are -1)
        try:
            logger.debug(
                f"[TSC] SignalAspect={se_pr}, KVB_SignalAspect={se_av}, senal_procesada={datos_ia.get('senal_procesada')}"
            )
        except Exception:
            # Don't crash on logging error
            pass
        datos_ia.setdefault("velocimetro_mph", 0.0)
        datos_ia.setdefault("tipo_velocimetro", 1)
        # If RPM still zero here, try inferring from Regulator or VirtualThrottle and set flags
        if datos_ia.get("rpm", 0.0) == 0.0:
            try:
                if "Regulator" in datos_archivo and datos_archivo.get("Regulator", 0) is not None:
                    reg_val = self._to_float(datos_archivo.get("Regulator", 0.0))
                    if reg_val > 0.0:
                        datos_ia["rpm"] = reg_val * self.max_engine_rpm
                        datos_ia["rpm_inferida"] = True
                elif "VirtualThrottle" in datos_archivo and datos_archivo.get("VirtualThrottle", 0) is not None:
                    vt = self._to_float(datos_archivo.get("VirtualThrottle", 0.0))
                    if vt > 0.0:
                        datos_ia["rpm"] = vt * self.max_engine_rpm
                        datos_ia["rpm_inferida"] = True
            except Exception:
                print("[WARN] RPM inference failed (secondary block): unknown error")
                import traceback

                traceback.print_exc()
        # Mapear RPMSource (depuración) si existe en el archivo
        if "RPMSource" in datos_archivo:
            datos_ia["rpm_fuente"] = datos_archivo.get("RPMSource")
        datos_ia.setdefault("distancia_recorrida", 0.0)
        datos_ia.setdefault("esfuerzo_traccion", 0.0)
        # Amperaje (A) is the primary metric name; keep 'corriente' and 'amps' as aliases
        datos_ia.setdefault("amperaje", 0.0)
        datos_ia.setdefault("corriente", datos_ia.get("amperaje", 0.0))
        # Normalizar y validar RPM y corriente
        try:
            datos_ia["rpm"] = self._to_float(datos_ia.get("rpm", 0.0))
            if datos_ia["rpm"] < 0:
                datos_ia["rpm"] = 0.0
            if datos_ia["rpm"] > 5000:
                datos_ia["rpm"] = 5000.0
        except Exception:
            datos_ia["rpm"] = 0.0

        # Infer RPM from regulator (Regulator -> acelerador) when RPM not provided
        try:
            if datos_ia.get("rpm", 0.0) == 0.0:
                reg = self._to_float(datos_ia.get("acelerador", 0.0))
                if reg and reg > 0.0:
                    datos_ia["rpm"] = reg * float(self.max_engine_rpm)
                    datos_ia["rpm_inferida"] = True
                else:
                    datos_ia.setdefault("rpm_inferida", False)
        except Exception:
            datos_ia.setdefault("rpm_inferida", False)

        try:
            datos_ia["amperaje"] = self._to_float(datos_ia.get("amperaje", 0.0))
            # keep legacy alias
            datos_ia["corriente"] = datos_ia["amperaje"]
        except Exception:
            datos_ia["corriente"] = 0.0
        # Alias para compatibilidad con front-end y pruebas (amps -> corriente)
        datos_ia.setdefault("amps", datos_ia.get("amperaje", 0.0))
        datos_ia.setdefault("deslizamiento_ruedas", 0.0)
        # Normalizar wheelslip a una intensidad 0..1 compatible entre assets
        try:
            raw_ws = self._to_float(datos_ia.get("deslizamiento_ruedas", 0.0))
            datos_ia["deslizamiento_ruedas_raw"] = raw_ws
            # Heurística de normalización:
            # - Si el valor está en 0..1 => es normalizado por asset (0=bueno, 1=máx deslizamiento)
            # - Si el valor tiene base 1 (1 = normal, >1 = deslizamiento) mapear 1..2 -> 0..1 y 1..3 -> 0..1
            # - El valor EXACTO 1.0 es ambiguo (puede ser "normal" en assets base-1 o "máx" en assets normalizados)
            #   Si el valor es exactamente 1.0, se considera ambiguo y la presencia de
            #   deslizamiento (intensidad = 1.0) se infiere usando heurísticas basadas
            #   en otros indicadores de telemetría (esfuerzo de tracción, RPM, velocidad).
            #   Solo si estas heurísticas no sugieren patinamiento, se asume
            #   conservadoramente "no deslizamiento" (0.0) por defecto.
            if raw_ws is None:
                intensity = 0.0
                interpretation = "missing"
            elif raw_ws < 1.0:
                intensity = raw_ws
                interpretation = "0-1"
            elif raw_ws == 1.0:
                # Ambiguo: inferir a partir de otros indicadores conservadores
                tractive = self._to_float(datos_ia.get("esfuerzo_traccion", 0.0))
                speed_kmh = self._to_float(datos_ia.get("velocidad_actual", 0.0))
                rpm_val = self._to_float(datos_ia.get("rpm", 0.0))
                # Heurísticas que indican posible patinamiento
                if (speed_kmh < 5.0 and tractive > 300.0) or (
                    rpm_val > 2000.0 and speed_kmh < 10.0 and tractive > 300.0
                ):
                    intensity = 1.0
                    interpretation = "1.0-inferred-slip"
                else:
                    intensity = 0.0
                    interpretation = "1.0-assumed-normal"
            elif raw_ws <= 2.0:
                # Base 1, max 2
                intensity = max(0.0, min(1.0, raw_ws - 1.0))
                interpretation = "base-1-max-2"
            elif raw_ws <= 3.0:
                # Base 1, max 3 => mapear 1..3 -> 0..1
                intensity = max(0.0, min(1.0, (raw_ws - 1.0) / 2.0))
                interpretation = "base-1-max-3"
            else:
                # Valores extremos: escalar conservadoramente
                intensity = max(0.0, min(1.0, (raw_ws - 1.0) / max(1.0, raw_ws)))
                interpretation = "unknown-large-scale"
            datos_ia["deslizamiento_ruedas_intensidad"] = round(float(intensity), 3)
        except Exception:
            datos_ia.setdefault("deslizamiento_ruedas_intensidad", 0.0)
            datos_ia.setdefault("deslizamiento_ruedas_raw", datos_ia.get("deslizamiento_ruedas", 0.0))

        # If wheelslip control not present or raw is zero, try to infer from other telemetry
        try:
            if datos_ia.get("deslizamiento_ruedas_raw", 0.0) == 0.0:
                tractive = self._to_float(datos_ia.get("esfuerzo_traccion", 0.0))
                speed_kmh = self._to_float(datos_ia.get("velocidad_actual", 0.0))
                rpm_val = self._to_float(datos_ia.get("rpm", 0.0))
                inferred = 0.0
                # Heurística simple y conservadora:
                # - Si la velocidad es baja (<5 km/h) y el esfuerzo de tracción es alto, hay probabilidad de patinamiento.
                if speed_kmh < 5.0 and tractive > 300.0:
                    inferred = min(1.0, (tractive - 300.0) / 1000.0)
                # - Si RPM es alto y la velocidad baja, también puede indicar patinamiento
                elif rpm_val > 2000.0 and speed_kmh < 10.0 and tractive > 300.0:
                    inferred = min(1.0, (tractive - 300.0) / 1000.0)
                if inferred > 0.0:
                    # Keep higher of observed intensity and inferred
                    current_int = datos_ia.get("deslizamiento_ruedas_intensidad", 0.0)
                    datos_ia["deslizamiento_ruedas_intensidad"] = round(max(float(current_int), inferred), 3)
                    datos_ia["deslizamiento_ruedas_interpretacion"] = (
                        datos_ia.get("deslizamiento_ruedas_interpretacion", "") + ",inferred_from_tractive".lstrip(',')
                    )
                    datos_ia.setdefault("deslizamiento_ruedas_inferida", True)
        except Exception:
            # On any error during wheelslip inference, record interpretation if available
            try:
                datos_ia["deslizamiento_ruedas_interpretacion"] = interpretation
            except NameError:
                datos_ia.setdefault("deslizamiento_ruedas_interpretacion", "unknown")
            datos_ia.setdefault("deslizamiento_ruedas_intensidad", 0.0)
            datos_ia.setdefault("deslizamiento_ruedas_raw", datos_ia.get("deslizamiento_ruedas", 0.0))
        # Brake Pressure Defaults
        datos_ia.setdefault("presion_tubo_freno", 0.0)
        datos_ia.setdefault("presion_freno_loco", 0.0)
        datos_ia.setdefault("presion_freno_tren", 0.0)
        datos_ia.setdefault("presion_deposito_equalizacion", 0.0)
        datos_ia.setdefault("presion_deposito_principal", 0.0)
        datos_ia.setdefault("presion_tubo_freno_mostrada", 0.0)
        datos_ia.setdefault("presion_deposito_auxiliar", 0.0)
        datos_ia.setdefault("presion_tubo_freno_cola", 0.0)
        datos_ia.setdefault("presion_tubo_freno_cola_presente", False)
        datos_ia.setdefault("presion_freno_loco_mostrada", 0.0)
        datos_ia.setdefault("presion_freno_loco_avanzada", 0.0)
        datos_ia.setdefault("presion_freno_tren_inferida", False)
        # Engine Control Defaults
        datos_ia.setdefault("freno_mano", 0.0)
        datos_ia.setdefault("freno_emergencia", 0.0)
        datos_ia.setdefault("estado_compresor", 0.0)
        datos_ia.setdefault("posicion_freno_tren", 0.0)
        datos_ia.setdefault("fecha_hora", datetime.now().isoformat())

        # Fuel telemetry removed: keep compatibility keys but filled with None
        datos_ia.setdefault("combustible_porcentaje", None)
        datos_ia.setdefault("combustible_galones", None)
        datos_ia.setdefault("combustible", None)

        # Presencia de campos: indicar si el archivo GetData.txt contenía ciertos controles
        datos_ia["presion_tubo_freno_presente"] = "AirBrakePipePressurePSI" in datos_archivo
        datos_ia["presion_freno_loco_presente"] = "LocoBrakeCylinderPressurePSI" in datos_archivo
        datos_ia["presion_freno_tren_presente"] = "TrainBrakeCylinderPressurePSI" in datos_archivo
        datos_ia["presion_deposito_principal_presente"] = "MainReservoirPressurePSIDisplayed" in datos_archivo
        datos_ia["eq_reservoir_presente"] = "EqReservoirPressurePSIAdvanced" in datos_archivo
        # Presencia de control TrainBrakeControl o VirtualBrake (control de freno de tren)
        datos_ia["posicion_freno_tren_presente"] = (
            "TrainBrakeControl" in datos_archivo or "VirtualBrake" in datos_archivo
        )
        datos_ia["presion_freno_loco_avanzada_presente"] = (
            "LocoBrakeCylinderPressurePSIAdvanced" in datos_archivo
        )
        # Flags para valores "mostrados" (display). Algunos mods/locos reportan solo la versión mostrada.
        datos_ia["presion_tubo_freno_mostrada_presente"] = (
            "AirBrakePipePressurePSIDisplayed" in datos_archivo
        )
        datos_ia["presion_freno_loco_mostrada_presente"] = (
            "LocoBrakeCylinderPressurePSIDisplayed" in datos_archivo
        )
        datos_ia["presion_deposito_auxiliar_presente"] = "AuxReservoirPressure" in datos_archivo
        datos_ia["presion_tubo_freno_cola_presente"] = "BrakePipePressureTailEnd" in datos_archivo

        # Fallback: algunos mods solo reportan la versión "mostrada" (displayed), usar como backup
        try:
            if (
                datos_ia.get("presion_tubo_freno", 0.0) == 0.0
                and datos_ia.get("presion_tubo_freno_mostrada", 0.0) != 0.0
            ):
                datos_ia["presion_tubo_freno"] = datos_ia.get("presion_tubo_freno_mostrada", 0.0)
            if (
                datos_ia.get("presion_freno_loco", 0.0) == 0.0
                and datos_ia.get("presion_freno_loco_mostrada", 0.0) != 0.0
            ):
                datos_ia["presion_freno_loco"] = datos_ia.get("presion_freno_loco_mostrada", 0.0)
        except Exception:
            # No fallbacks on exception
            pass

        # Inferencias si faltan sensores de presión de freno
        try:
            # Inferir presion_tubo_freno si no está presente
            if not datos_ia.get("presion_tubo_freno_presente"):
                # Basarse en el control de freno (TrainBrakeControl) cuando exista
                train_brake_cmd = datos_archivo.get("TrainBrakeControl") or datos_archivo.get("VirtualBrake") or 0.0
                try:
                    train_brake_cmd = self._to_float(train_brake_cmd)
                except Exception:
                    train_brake_cmd = 0.0
                if train_brake_cmd > 0.5:
                    datos_ia["presion_tubo_freno"] = 0.0
                else:
                    # Suponer valor normal si no frena (conservador)
                    datos_ia["presion_tubo_freno"] = datos_ia.get("presion_tubo_freno_mostrada", 80.0)
                datos_ia["presion_tubo_freno_inferida"] = True
            else:
                datos_ia.setdefault("presion_tubo_freno_inferida", False)

            # Inferir presion_freno_loco si no está presente
            if not datos_ia.get("presion_freno_loco_presente"):
                loco_display = datos_ia.get("presion_freno_loco_mostrada", 0.0)
                if loco_display != 0.0:
                    datos_ia["presion_freno_loco"] = loco_display
                else:
                    datos_ia["presion_freno_loco"] = 0.0
                datos_ia["presion_freno_loco_inferida"] = True
            else:
                datos_ia.setdefault("presion_freno_loco_inferida", False)

            # Inferir presion_freno_tren si no está presente, en función del TrainBrakeControl / VirtualBrake
            if not datos_ia.get("presion_freno_tren_presente"):
                train_brake_val = datos_ia.get("posicion_freno_tren") or datos_archivo.get("TrainBrakeControl") or datos_archivo.get("VirtualBrake") or 0.0
                try:
                    train_brake_val = self._to_float(train_brake_val)
                except Exception:
                    train_brake_val = 0.0
                # Heurística conservadora: si el control de freno está parcialmente aplicado,
                # inferimos una presión de cilindro proporcional a la posición del control.
                if train_brake_val > 0.0:
                    datos_ia["presion_freno_tren"] = 30.0 + (train_brake_val * 60.0)  # 30..90 PSI promedio
                else:
                    datos_ia["presion_freno_tren"] = datos_ia.get("presion_freno_tren", 0.0)
                datos_ia["presion_freno_tren_inferida"] = True
            else:
                datos_ia.setdefault("presion_freno_tren_inferida", False)
        except Exception as e:
            print(f"[WARN] Error inferring brake pressure: {e}")
            import traceback

            traceback.print_exc()

        return datos_ia

    def datos_cambiaron(self, datos_nuevos: Dict[str, Any]) -> bool:
        """
        Verificar si los datos han cambiado significativamente.

        Args:
            datos_nuevos: Nuevos datos leídos

        Returns:
            True si los datos cambiaron
        """
        if not self.datos_anteriores:
            return True

        # Verificar cambios en valores clave
        claves_importantes = [
            "CurrentSpeed",
            "Acceleration",
            "Gradient",
            "CurrentSpeedLimit",
        ]

        for clave in claves_importantes:
            if clave in datos_nuevos and clave in self.datos_anteriores:
                diferencia = abs(datos_nuevos[clave] - self.datos_anteriores[clave])
                if diferencia > 0.01:  # Umbral mínimo de cambio
                    return True

        return False

    def obtener_datos_telemetria(self) -> Optional[Dict[str, Any]]:
        """
        Obtener datos de telemetría del juego.

        Returns:
            Datos de telemetría en formato IA o None si no hay datos disponibles
        """
        tiempo_actual = time.time()

        # Controlar frecuencia de lectura
        if tiempo_actual - self.timestamp_ultima_lectura < self.intervalo_lectura:
            return None

        self.timestamp_ultima_lectura = tiempo_actual

        # Leer datos del archivo
        datos_archivo = self.leer_datos_archivo()

        if not datos_archivo:
            self.simulador_activo = False
            return None

        # Verificar si los datos cambiaron para detectar si el simulador está activo
        if self.datos_cambiaron(datos_archivo):
            # Datos cambiaron - simulador definitivamente activo
            self.simulador_activo = True
            self.timestamp_ultimo_cambio = tiempo_actual
        else:
            # Si no cambiaron, verificar si el simulador sigue activo
            tiempo_sin_cambio = tiempo_actual - self.timestamp_ultimo_cambio
            if tiempo_sin_cambio > 5.0:  # 5 segundos sin cambios = simulador inactivo
                self.simulador_activo = False

        # Actualizar datos anteriores
        self.datos_anteriores = datos_archivo.copy()

        # SIEMPRE convertir y devolver los datos actuales, incluso si no cambiaron
        # Esto asegura que el dashboard muestre los valores reales en todo momento
        datos_ia = self.convertir_datos_ia(datos_archivo)

        return datos_ia

    def _atomic_write_lines(self, file_path: str, lines: list[str], retries: int = 3, wait: float = 0.1) -> None:
        """Escribir una lista de líneas en `file_path` de forma atómica.

        Implementa escritura a fichero temporal en el mismo directorio y `os.replace`
        para minimizar ventanas de inconsistencia y reintenta en caso de errores de
        E/S (por ejemplo, PermissionError por bloqueo del archivo por el simulador).
        """
        dirname = os.path.dirname(file_path) or os.getcwd()
        tmp = os.path.join(dirname, os.path.basename(file_path) + ".tmp")
        last_exc = None
        start = time.time()
        for attempt in range(1, retries + 1):
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    for linea in lines:
                        f.write(linea + "\n")
                # If portalocker is available, try to acquire a short exclusive lock on the
                # destination file before replacing it, to reduce the window where a reader
                # might see an inconsistent state on platforms with strong locking semantics.
                if HAS_PORTALOCKER:
                    try:
                        # Acquire an exclusive append-mode lock on the destination file
                        # (this will create the file if it does not exist) and then replace.
                        with portalocker.Lock(file_path, 'a', timeout=0.25):
                            os.replace(tmp, file_path)
                    except Exception:
                        # If locking fails, fall back to a direct replace
                        os.replace(tmp, file_path)
                else:
                    os.replace(tmp, file_path)

                elapsed_ms = (time.time() - start) * 1000.0
                # update metrics
                self.io_metrics["write_attempts_last"] = attempt
                if attempt > 1:
                    self.io_metrics["write_total_retries"] += (attempt - 1)
                self.io_metrics["write_last_latency_ms"] = round(elapsed_ms, 3)
                return
            except Exception as e:
                last_exc = e
                logger.warning("Attempt %d to write %s failed: %s", attempt, file_path, e)
                try:
                    time.sleep(wait * attempt)
                except Exception:
                    pass
        # All attempts failed: record attempts and total retries
        elapsed_ms = (time.time() - start) * 1000.0
        self.io_metrics["write_attempts_last"] = retries
        self.io_metrics["write_total_retries"] += retries
        self.io_metrics["write_last_latency_ms"] = round(elapsed_ms, 3)
        logger.exception("Failed to write file %s after %d attempts", file_path, retries)
        raise last_exc

    def enviar_comandos(self, comandos: Dict[str, Any]) -> bool:
        """
        Enviar comandos de control al juego escribiendo al archivo autopilot_commands.txt.

        Args:
            comandos: Diccionario con comandos a enviar (comandos de texto simples)

        Returns:
            True si se enviaron correctamente
        """
        try:
            # Los comandos ahora son simples strings de texto
            comandos_texto = []
            for comando, valor in comandos.items():
                # Mapear comando en español a nombre RailDriver si está en mapeo
                comando_raildriver = self.mapeo_comandos.get(comando, comando)
                # Fallback heuristics: if sending DynamicBrake but it doesn't exist in latest read, try VirtualEngineBrakeControl
                if comando_raildriver == "DynamicBrake":
                    # if we have recent data, prefer the control that exists
                    if self.datos_anteriores:
                        if (
                            "DynamicBrake" not in self.datos_anteriores
                            and "VirtualEngineBrakeControl" in self.datos_anteriores
                        ):
                            comando_raildriver = "VirtualEngineBrakeControl"
                            logger.info(
                                "[TSC] Fallback using VirtualEngineBrakeControl because DynamicBrake not present in GetData.txt"
                            )
                # Generic fallback map for a few critical controls
                fallback_map = {
                    "Regulator": ["Regulator", "VirtualThrottle", "SimpleThrottle"],
                    "TrainBrakeControl": ["TrainBrakeControl", "VirtualBrake"],
                    "DynamicBrake": ["DynamicBrake", "VirtualEngineBrakeControl"],
                }
                if self.datos_anteriores and comando_raildriver in fallback_map:
                    candidates = fallback_map[comando_raildriver]
                    if candidates:
                        # Use the first available control present in datos_anteriores
                        found = None
                        for c in candidates:
                            if c in self.datos_anteriores:
                                found = c
                                break
                        if found and found != comando_raildriver:
                            logger.info(
                                f"[TSC] Fallback mapped '{comando_raildriver}' to '{found}' based on available controls"
                            )
                            comando_raildriver = found
                if isinstance(valor, str):
                    # Permitir cadenas de texto crudas (start/stop autopilot)
                    comandos_texto.append(valor)
                elif isinstance(valor, bool):
                    if comando == "autopilot":
                        if valor:
                            comandos_texto.append("start_autopilot")
                        else:
                            comandos_texto.append("stop_autopilot")
                    elif comando == "predictive":
                        if valor:
                            comandos_texto.append("start_predictive")
                        else:
                            comandos_texto.append("stop_predictive")
                    else:
                        # Valores booleanos no mapeados como autopilot/predictive se envían con mapeo si existe
                        comandos_texto.append(f"{comando_raildriver}:{valor}")
                else:
                    # Para valores numéricos, mapear nombre de comando si es necesario
                    try:
                        val_f = float(valor)
                    except Exception:
                        val_f = None

                    # Special-case: when AI sends 'acelerador' we write both Regulator and VirtualThrottle
                    # to support assets that consume one or the other (notches/virtual throttle).
                    if comando == "acelerador":
                        try:
                            if val_f is not None:
                                # Snap to nearest notch for physical/virtual throttle compatibility
                                snapped = self._snap_to_notch(val_f)
                                reg_line = f"Regulator:{snapped:.3f}"
                                vt_line = f"VirtualThrottle:{snapped:.3f}"
                                comandos_texto.append(reg_line)
                                comandos_texto.append(vt_line)
                                commands_line = f"Regulator/VirtualThrottle:{snapped:.3f}"
                            else:
                                comandos_texto.append(f"Regulator:{valor}")
                                comandos_texto.append(f"VirtualThrottle:{valor}")
                                commands_line = f"Regulator/VirtualThrottle:{valor}"
                        except Exception:
                            # Fallback to single mapped command
                            try:
                                commands_line = f"{comando_raildriver}:{float(valor):.3f}"
                                comandos_texto.append(commands_line)
                            except Exception:
                                commands_line = f"{comando_raildriver}:{valor}"
                                comandos_texto.append(commands_line)
                    else:
                        try:
                            commands_line = f"{comando_raildriver}:{float(valor):.3f}"
                            comandos_texto.append(commands_line)
                        except Exception:
                            commands_line = f"{comando_raildriver}:{valor}"
                            comandos_texto.append(commands_line)

                    # Debug print if we remapped the command
                    if comando_raildriver != comando:
                        logger.info(
                            f"[TSC] Remapped command '{comando}' -> '{comando_raildriver}': {commands_line}"
                        )

            if not comandos_texto:
                return True

            # If 'start_autopilot' exists but the Lua plugin is not loaded, append fallback control lines
            try:
                lower_cmds = [c.lower() for c in comandos_texto]
                if any("start_autopilot" in c for c in lower_cmds):
                    # Prefer explicit plugin state file (autopilot_state.txt) to determine whether
                    # the plugin has acknowledged 'on'. Only apply fallback if plugin_state != 'on'.
                    try:
                        plugin_state = self.get_autopilot_plugin_state()
                    except Exception:
                        plugin_state = None

                    if plugin_state != "on":
                        fallback_notch = 0.125
                        fallback_lines = [f"Regulator:{fallback_notch:.3f}", f"VirtualThrottle:{fallback_notch:.3f}"]
                        for fl in fallback_lines:
                            if fl not in comandos_texto:
                                comandos_texto.append(fl)
                        logger.warning(
                            "[TSC] 'start_autopilot' issued but plugin state not 'on'; applying fallback controls: %s",
                            fallback_lines,
                        )
            except Exception:
                logger.exception("[TSC] Error evaluating start_autopilot fallback logic")

            # Escribir al archivo autopilot_commands.txt de forma atómica con reintentos
            try:
                self._atomic_write_lines(self.ruta_archivo_comandos, comandos_texto)
            except Exception as e:
                logger.warning("[TSC] No se pudo escribir %s: %s", self.ruta_archivo_comandos, e)
                # No abortar inmediatamente; seguir intentando escribir archivos auxiliares

            print(f"[TSC] Comandos enviados al Lua: {len(comandos_texto)} comandos")
            for linea in comandos_texto:
                print(f"   {linea}")

            # Además, escribir un archivo que el script Lua realmente lee (autopilot_commands.txt).
            # Evitar escribir dos veces en el mismo archivo cuando `ruta_archivo_comandos`
            # ya apunta al archivo que Lua consume.
            try:
                if self.write_lua_commands:
                    directorio = os.path.dirname(self.ruta_archivo_comandos)
                    lua_commands_file = os.path.join(directorio, "autopilot_commands.txt")
                    # If the configured commands file and the Lua file are the same path,
                    # skip the second write to avoid duplicate writes.
                    if os.path.abspath(lua_commands_file) != os.path.abspath(self.ruta_archivo_comandos):
                        try:
                            self._atomic_write_lines(lua_commands_file, comandos_texto)
                            logger.info(f"[TSC] También escrito archivo de comandos Lua: {lua_commands_file}")
                        except Exception as e:
                            logger.warning(f"[TSC] No se pudo escribir archivo de comandos Lua: {e}")
                    else:
                        logger.debug(
                            f"[TSC] Ruta de comandos configurada ya es el archivo Lua ({lua_commands_file}); omitida escritura duplicada"
                        )
            except Exception as e:
                logger.warning(f"[TSC] No se pudo escribir archivo de comandos Lua: {e}")

            # Also write the lowercase 'sendcommand.txt' to mirror what some controllers (RailDriver)
            # and third-party tools use. Some systems observe this exact filename.
            try:
                directorio = os.path.dirname(self.ruta_archivo_comandos)
                lower_send_file = os.path.join(directorio, "sendcommand.txt")
                try:
                    # If legacy lowercase path resolves to the same file as the configured
                    # commands file on case-insensitive filesystems, skip the filtered write
                    # to avoid overwriting directives that must be preserved.
                    if os.path.normcase(os.path.abspath(lower_send_file)) == os.path.normcase(os.path.abspath(self.ruta_archivo_comandos)):
                        logger.debug(
                            f"[TSC] Legacy sendcommand path {lower_send_file} equals configured commands file; skipping filtered legacy write"
                        )
                    else:
                        # Filter only control:value lines
                        filtered = [l for l in comandos_texto if ":" in l]
                        if filtered:
                            self._atomic_write_lines(lower_send_file, filtered)
                        logger.info(f"[TSC] También escrito archivo legacy sendcommand: {lower_send_file}")
                except Exception as e:
                    logger.warning(f"[TSC] No se pudo escribir archivo legacy sendcommand: {e}")
            except Exception as e:
                logger.warning(f"[TSC] No se pudo preparar archivo legacy sendcommand: {e}")

            # Also write to TSClassic Interface file (configurable). Default points to SendCommand.txt
            try:
                tsc_file = getattr(self, "tsc_interface_file", None)
                if not tsc_file:
                    tsc_file = os.path.join(os.path.dirname(self.ruta_archivo_comandos), "SendCommand.txt")
                    # store for future
                    self.tsc_interface_file = tsc_file
                # If TSClassic interface file is the same path as configured commands file,
                # do not overwrite it with filtered colon-only lines (this would remove
                # directive tokens like 'start_autopilot'); skip the extra write instead.
                if os.path.normcase(os.path.abspath(tsc_file)) == os.path.normcase(os.path.abspath(self.ruta_archivo_comandos)):
                    logger.debug(
                        f"[TSC] TSClassic interface file {tsc_file} matches configured commands file; skipping filtered write to avoid overwriting full commands"
                    )
                else:
                    # Write only control:value lines (TSClassic Interface expects that format)
                    filtered_interface = [l for l in comandos_texto if ":" in l]
                    if filtered_interface:
                        try:
                            self._atomic_write_lines(tsc_file, filtered_interface)
                            logger.info(f"[TSC] Also written TSClassic Interface file: {tsc_file}")
                        except Exception as e:
                            logger.warning(f"[TSC] Could not write TSClassic Interface file {tsc_file}: {e}")
            except Exception as e:
                logger.warning(f"[TSC] Error handling TSClassic Interface file write: {e}")

            # If we've reached here, consider the send successful
            return True
        except Exception as e:
            logger.exception("[TSC] Error sending commands: %s", e)
            return False
    def estado_conexion(self) -> Dict[str, Any]:
        """Retornar estado de conexión y métricas básicas para monitoreo."""
        state = {
            "archivo_existe": self.archivo_existe(),
            "ultima_lectura": (
                datetime.fromtimestamp(self.timestamp_ultima_lectura).isoformat()
                if self.timestamp_ultima_lectura > 0
                else None
            ),
            "datos_disponibles": len(self.datos_anteriores) > 0,
            "controles_leidos": len(self.datos_anteriores),
        }
        # Añadir métricas I/O al estado para fácil acceso desde endpoints/monitoreo
        state.setdefault("io_metrics", {})
        state["io_metrics"].update(self.io_metrics)
        return state

    def get_io_metrics(self) -> Dict[str, Any]:
        """Retornar una copia de las métricas I/O actuales."""
        return dict(self.io_metrics)

    def conectar(self) -> bool:
        """
        Conectar con TSC (verificar que el archivo existe).

        Returns:
            True si la conexión es exitosa
        """
        return self.archivo_existe()

    def ejecutar_ciclo_ia(self) -> Dict[str, Any]:
        """
        Ejecutar un ciclo completo de IA: leer datos, tomar decisión, enviar comandos.

        Returns:
            Dict con datos leídos y decisión tomada
        """
        datos = self.obtener_datos_telemetria()
        if datos:
            # Aquí se podría integrar con ia_logic para tomar decisiones
            # Por ahora, devolver datos simulados
            decision = {"acelerador": 0.5, "freno": 0.0}
            return {"datos": datos, "decision": decision}
        return {"datos": {}, "decision": {}}

    def desconectar(self) -> None:
        """
        Desconectar de TSC (no hace nada específico en esta implementación).
        """
        pass

    def guardar_historial(self, archivo: str) -> None:
        """
        Guardar historial de operaciones a un archivo JSON.

        Args:
            archivo: Ruta del archivo donde guardar
        """
        # Implementación básica: guardar datos anteriores
        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "datos_anteriores": self.datos_anteriores,
                        "comandos_anteriores": self.comandos_anteriores,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"[SAVE] Historial guardado en {archivo}")
        except Exception as e:
            print(f"[ERROR] Error guardando historial: {e}")


def main():
    """Función principal para pruebas."""
    print("[TEST] TSC Integration - Modo de Prueba")
    print("=" * 40)

    integration = TSCIntegration()

    print(f"[FILE] Archivo de datos: {integration.ruta_archivo}")
    print(f"[STATUS] Archivo existe: {integration.archivo_existe()}")

    if not integration.archivo_existe():
        print("\n[ERROR] El archivo GetData.txt no existe")
        print("[INFO] Asegúrate de que:")
        print("   1. TSClassic Raildriver Interface esté ejecutándose")
        print("   2. Train Simulator Classic esté ejecutándose")
        print("   3. Estés conduciendo un tren")
        return

    print("\n[MONITOR] Monitoreando datos en tiempo real...")
    print("Presiona Ctrl+C para detener")

    try:
        contador_lecturas = 0
        while True:
            datos = integration.obtener_datos_telemetria()

            if datos:
                contador_lecturas += 1
                print(f"\n📈 Lectura #{contador_lecturas} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"[DATA] Velocidad: {datos.get('velocidad', 0)} mph")
                print(f"🚦 Límite: {datos.get('limite_velocidad_actual', 0)} mph")
                print(f"🏔️  Pendiente: {datos.get('pendiente', 0)} ‰")
                print(f"⚡ Aceleración: {datos.get('aceleracion', 0)} m/s²")

            time.sleep(0.5)  # Pequeña pausa para no saturar la consola

    except KeyboardInterrupt:
        print("\n\n🛑 Monitoreo detenido por el usuario")

        # Mostrar estado final
        estado = integration.estado_conexion()
        print("\n[FINAL] ESTADO FINAL:")
        print(f"   Archivo existe: {estado['archivo_existe']}")
        print(f"   Última lectura: {estado['ultima_lectura']}")
        print(f"   Datos disponibles: {estado['datos_disponibles']}")
        print(f"   Controles leídos: {estado['controles_leidos']}")

        print("\n✅ ¡Integración TSC completada exitosamente!")


if __name__ == "__main__":
    main()
