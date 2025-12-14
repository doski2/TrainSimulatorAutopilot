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
            "EqReservoirPressurePSIAdvanced": "presion_deposito_equalizacion",
            "MainReservoirPressurePSIDisplayed": "presion_deposito_principal",
            "AirBrakePipePressurePSIDisplayed": "presion_tubo_freno_mostrada",
            "AuxReservoirPressure": "presion_deposito_auxiliar",
            "BrakePipePressureTailEnd": "presion_tubo_freno_cola",
            "LocoBrakeCylinderPressurePSIDisplayed": "presion_freno_loco_mostrada",
            "LocoBrakeCylinderPressurePSIAdvanced": "presion_freno_loco_avanzada",
            # Engine Control Mappings
            "EngineBrakeControl": "freno_motor_control",
            "Regulator": "acelerador",
            "Reverser": "reverser",
            "TrainBrakeControl": "posicion_freno_tren",
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
            "freno_motor": "EngineBrakeControl",
            "freno_dinamico": "DynamicBrake",
            "reverser": "Reverser",  # Changed to Reverser
            # Nuevos controles de locomotora
            "puertas": "DoorSwitch",  # May not exist
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

    def archivo_existe(self) -> bool:
        """Verificar si el archivo GetData.txt existe."""
        return os.path.exists(self.ruta_archivo)

    def leer_datos_archivo(self) -> Optional[Dict[str, Any]]:
        """
        Leer datos del archivo GetData.txt.

        Returns:
            Dict con los datos leídos o None si hay error
        """
        if not self.archivo_existe():
            return None

        try:
            with open(self.ruta_archivo, encoding="utf-8") as f:
                lineas = f.readlines()

            # Normalizar y remover BOM UTF-8 si existe en la primera línea
            if lineas:
                # ".lstrip('\ufeff')" remueve el carácter BOM (si está presente)
                if lineas[0].startswith("\ufeff"):
                    lineas[0] = lineas[0].lstrip("\ufeff")

            datos = {}
            i = 0
            while i < len(lineas):
                linea = lineas[i].strip()
                if linea.startswith("ControlName:"):
                    nombre_control = linea.split(":", 1)[1].strip()
                    # Buscar el valor correspondiente
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

                i += 1

            return datos

        except Exception as e:
            print(f"Error leyendo archivo GetData.txt: {e}")
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
                except Exception:
                    pass

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
                except Exception:
                    pass

            # Mapear RPMSource (depuración) si existe en el archivo
            if "RPMSource" in datos_archivo:
                datos_ia["rpm_fuente"] = datos_archivo.get("RPMSource")

        # Priorizar control de freno real (TrainBrakeControl/VirtualBrake) si está disponible
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
                except Exception:
                    pass
        except Exception:
            # No bloquear si hay error
            pass

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
                pass
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
            if raw_ws <= 1.0:
                intensity = raw_ws
                interpretation = "0-1"
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
            pass
            datos_ia["deslizamiento_ruedas_interpretacion"] = interpretation
        except Exception:
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
        # RPM inference flags and source
        datos_ia.setdefault("rpm_inferida", False)
        datos_ia.setdefault("rpm_fuente", None)
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
        except Exception:
            pass

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
                    "EngineBrakeControl": ["EngineBrakeControl", "VirtualEngineBrakeControl"],
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

            # Escribir al archivo autopilot_commands.txt
            with open(self.ruta_archivo_comandos, "w", encoding="utf-8") as f:
                for linea in comandos_texto:
                    f.write(linea + "\n")

            print(f"[TSC] Comandos enviados al Lua: {len(comandos_texto)} comandos")
            for linea in comandos_texto:
                print(f"   {linea}")

            return True

        except Exception as e:
            print(f"[ERROR] Error enviando comandos: {e}")
            return False

    def estado_conexion(self) -> Dict[str, Any]:
        """
        Obtener el estado actual de la conexión.

        Returns:
            Dict con información del estado
        """
        return {
            "archivo_existe": self.archivo_existe(),
            "ultima_lectura": (
                datetime.fromtimestamp(self.timestamp_ultima_lectura).isoformat()
                if self.timestamp_ultima_lectura > 0
                else None
            ),
            "datos_disponibles": len(self.datos_anteriores) > 0,
            "controles_leidos": len(self.datos_anteriores),
        }

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
