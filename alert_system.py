# alert_system.py
# Sistema de alertas basado en análisis estadístico para Train Simulator Autopilot

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from seaborn_analysis import SeabornAnalysis

# Importar módulos del proyecto
from tsc_integration import TSCIntegration


class AlertSeverity(Enum):
    """Niveles de severidad para alertas"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Tipos de alertas disponibles"""

    SPEED_VIOLATION = "speed_violation"
    ANOMALY_DETECTED = "anomaly_detected"
    EFFICIENCY_DROP = "efficiency_drop"
    SYSTEM_ERROR = "system_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    FUEL_LOW = "fuel_low"
    OVERHEATING = "overheating"
    WHEELSLIP = "wheelslip"
    BRAKE_PRESSURE_DISCREPANCY = "brake_pressure_discrepancy"


@dataclass
class Alert:
    """Clase para representar una alerta"""

    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    data: Dict
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convertir alerta a diccionario para serialización"""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Alert":
        """Crear alerta desde diccionario"""
        return cls(
            alert_id=data["alert_id"],
            alert_type=AlertType(data["alert_type"]),
            severity=AlertSeverity(data["severity"]),
            title=data["title"],
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            acknowledged=data.get("acknowledged", False),
            acknowledged_at=(
                datetime.fromisoformat(data["acknowledged_at"])
                if data.get("acknowledged_at")
                else None
            ),
        )


class AlertSystem:
    """Sistema de alertas basado en análisis estadístico"""

    def __init__(self, alerts_file="alerts.json", config_file="alert_config.json"):
        self.alerts_file = alerts_file
        self.config_file = config_file
        self.tsc_integration = TSCIntegration()
        self.analyzer = SeabornAnalysis(use_tsc_integration=False)  # No inicializar TSC aquí

        # Configuración por defecto de umbrales
        self.default_config = {
            "speed_violation": {"max_speed": 120, "enabled": True, "severity": "high"},  # km/h
            "anomaly_detection": {
                "z_score_threshold": 3.0,
                "min_samples": 10,
                "enabled": True,
                "severity": "medium",
            },
            "efficiency_drop": {
                "drop_percentage": 20,  # 20% drop
                "time_window_minutes": 5,
                "enabled": True,
                "severity": "medium",
            },
            "overheating": {
                "temperature_threshold": 90,  # °C
                "enabled": True,
                "severity": "critical",
            },
            "performance_degradation": {
                "response_time_threshold_ms": 1000,
                "enabled": True,
                "severity": "low",
            },
            "wheelslip": {
                "threshold": 0.5,  # 0.5 = 50% wheelslip
                "enabled": True,
                "severity": "high",
            },
            "brake_pipe_discrepancy": {
                "threshold_psi": 20.0,  # PSI difference between front and tail
                "enabled": True,
                "severity": "high",
            },
        }

        # Cargar configuración
        self.config = self.load_config()

        # Cargar alertas existentes
        self.alerts: List[Alert] = self.load_alerts()

        # Estado para monitoreo continuo
        self.monitoring_active = False
        self.last_check_time = None
        self.last_telemetry: Optional[Dict] = None
        self.baseline_data = {}  # Datos baseline para comparación

        print("Sistema de alertas inicializado")

    def load_config(self) -> Dict:
        """Cargar configuración de alertas"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, default_value in self.default_config.items():
                        if key not in config:
                            config[key] = default_value
                    return config
            except Exception as e:
                print(f"Error cargando configuración: {e}")

        return self.default_config.copy()

    def save_config(self):
        """Guardar configuración de alertas"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Configuración guardada en {self.config_file}")
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def load_alerts(self) -> List[Alert]:
        """Cargar alertas desde archivo"""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, encoding="utf-8") as f:
                    alerts_data = json.load(f)
                    # Filter out deprecated fuel_low alerts
                    filtered = [a for a in alerts_data if a.get("alert_type") != "fuel_low"]
                    if len(filtered) != len(alerts_data):
                        try:
                            with open(self.alerts_file, "w", encoding="utf-8") as wf:
                                json.dump(filtered, wf, indent=2, ensure_ascii=False)
                            print("[INFO] Removed legacy fuel_low alerts from alerts.json")
                        except Exception as e:
                            print(f"[ERROR] Could not update alerts file after pruning legacy fuel_low alerts: {e}")
                    return [Alert.from_dict(alert_data) for alert_data in filtered]
            except Exception as e:
                print(f"Error cargando alertas: {e}")

        return []

    def save_alerts(self):
        """Guardar alertas en archivo"""
        try:
            alerts_data = [alert.to_dict() for alert in self.alerts]
            with open(self.alerts_file, "w", encoding="utf-8") as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)
            print(f"Alertas guardadas en {self.alerts_file}")
        except Exception as e:
            print(f"Error guardando alertas: {e}")

    def _to_float(self, x: Any) -> Optional[float]:
        """Convertir de forma segura a float, devolviendo None si no es posible."""
        try:
            if x is None:
                return None
            return float(x)
        except Exception:
            return None
    def check_speed_violation(self, current_data: Dict) -> Optional[Alert]:
        """Verificar violación de velocidad"""
        if not self.config["speed_violation"]["enabled"]:
            return None

        current_speed = current_data.get("velocidad_actual", 0)
        max_speed = self.config["speed_violation"].get("max_speed")

        try:
            # Asegurarse de que existan valores numéricos válidos
            if max_speed is None:
                return None
            current_speed = float(current_speed)
            max_speed = float(max_speed)
        except Exception:
            return None

        if current_speed > max_speed:
            severity = AlertSeverity(self.config["speed_violation"]["severity"])
            return Alert(
                alert_id=f"speed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type=AlertType.SPEED_VIOLATION,
                severity=severity,
                title="Violación de Velocidad Detectada",
                message=f"Velocidad actual: {current_speed:.1f} km/h (límite: {max_speed} km/h)",
                timestamp=datetime.now(),
                data={
                    "current_speed": current_speed,
                    "max_speed": max_speed,
                    "violation_amount": current_speed - max_speed,
                },
            )

        return None

    def check_anomalies(self, recent_data: pd.DataFrame) -> List[Alert]:
        """Verificar anomalías en datos recientes usando análisis estadístico"""
        if (
            not self.config["anomaly_detection"]["enabled"]
            or recent_data is None
            or len(recent_data) < 10
        ):
            return []

        alerts = []
        z_threshold = self.config["anomaly_detection"]["z_score_threshold"]

        # Verificar anomalías en variables clave
        variables_to_check = ["velocidad", "aceleracion", "rpm", "presion_freno"]

        for var in variables_to_check:
            if var in recent_data.columns:
                data_clean = recent_data[var].dropna()
                if len(data_clean) >= self.config["anomaly_detection"]["min_samples"]:
                    # Calcular z-score manualmente
                    data_array = np.asarray(data_clean, dtype=float)
                    mean_val = np.mean(data_array)
                    std_val = np.std(data_array, ddof=1)

                    if std_val > 0:
                        z_scores = np.abs((data_array - mean_val) / std_val)
                        max_z = float(np.max(z_scores))
                        max_z_idx = np.argmax(z_scores)

                        if max_z > z_threshold:
                            severity = AlertSeverity(self.config["anomaly_detection"]["severity"])
                            if max_z > 4.0:
                                severity = AlertSeverity.CRITICAL
                            elif max_z > 3.5:
                                severity = AlertSeverity.HIGH

                            alerts.append(
                                Alert(
                                    alert_id=f"anomaly_{var}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                    alert_type=AlertType.ANOMALY_DETECTED,
                                    severity=severity,
                                    title=f"Anomalía Detectada en {var.title()}",
                                    message=f"Valor anómalo detectado (Z-score: {max_z:.2f}) en variable {var}",
                                    timestamp=datetime.now(),
                                    data={
                                        "variable": var,
                                        "z_score": max_z,
                                        "threshold": z_threshold,
                                        "anomalous_value": float(data_array[max_z_idx]),
                                        "mean": mean_val,
                                        "std": std_val,
                                    },
                                )
                            )

        return alerts

    def check_efficiency_drop(self, recent_data: pd.DataFrame) -> Optional[Alert]:
        """Verificar caída en eficiencia"""
        if not self.config["efficiency_drop"]["enabled"] or recent_data is None:
            return None

        # Calcular eficiencia aproximada (velocidad / (RPM + corriente))
        if (
            "velocidad" in recent_data.columns
            and "rpm" in recent_data.columns
            and "corriente" in recent_data.columns
        ):
            efficiency = recent_data["velocidad"] / (
                recent_data["rpm"] + recent_data["corriente"] + 1
            )

            # Comparar con baseline si existe
            if "efficiency_baseline" in self.baseline_data:
                baseline_eff = self.baseline_data["efficiency_baseline"]
                current_avg_eff = efficiency.mean()
                drop_percentage = ((baseline_eff - current_avg_eff) / baseline_eff) * 100

                if drop_percentage > self.config["efficiency_drop"]["drop_percentage"]:
                    severity = AlertSeverity(self.config["efficiency_drop"]["severity"])
                    return Alert(
                        alert_id=f"efficiency_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        alert_type=AlertType.EFFICIENCY_DROP,
                        severity=severity,
                        title="Caída en Eficiencia Detectada",
                        message=f"Eficiencia reducida en {drop_percentage:.1f}% (baseline: {baseline_eff:.2f})",
                        timestamp=datetime.now(),
                        data={
                            "current_efficiency": current_avg_eff,
                            "baseline_efficiency": baseline_eff,
                            "drop_percentage": drop_percentage,
                            "threshold": self.config["efficiency_drop"]["drop_percentage"],
                        },
                    )

            # Actualizar baseline
            self.baseline_data["efficiency_baseline"] = efficiency.mean()

        return None

    # Fuel monitoring removed; method deleted

    def check_overheating(self, current_data: Dict) -> Optional[Alert]:
        """Verificar sobrecalentamiento"""
        if not self.config["overheating"]["enabled"]:
            return None

        temperature = current_data.get("temperatura", 0)
        threshold = self.config["overheating"].get("temperature_threshold")

        try:
            if threshold is None:
                return None
            temperature = float(temperature)
            threshold = float(threshold)
        except Exception:
            return None

        if temperature > threshold:
            severity = AlertSeverity(self.config["overheating"]["severity"])
            return Alert(
                alert_id=f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type=AlertType.OVERHEATING,
                severity=severity,
                title="Sobrecalentamiento Detectado",
                message=f"Temperatura: {temperature:.1f}°C (umbral: {threshold}°C)",
                timestamp=datetime.now(),
                data={
                    "temperature": temperature,
                    "threshold": threshold,
                    "overheat_amount": temperature - threshold,
                },
            )

        return None

    def check_wheelslip(self, current_data: Dict) -> Optional[Alert]:
        """Verificar deslizamiento de ruedas"""
        if not self.config["wheelslip"]["enabled"]:
            return None

        # Prefer normalized intensity if present
        wheelslip = current_data.get(
            "deslizamiento_ruedas_intensidad", current_data.get("deslizamiento_ruedas", 0)
        )
        threshold = self.config["wheelslip"].get("threshold")

        try:
            if threshold is None:
                return None
            wheelslip = float(wheelslip)
            threshold = float(threshold)
        except Exception:
            return None

        if wheelslip > threshold:
            severity = AlertSeverity(self.config["wheelslip"]["severity"])
            return Alert(
                alert_id=f"wheelslip_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type=AlertType.WHEELSLIP,
                severity=severity,
                title="Deslizamiento de Ruedas Detectado",
                message=f"Deslizamiento: {wheelslip:.2f} (umbral: {threshold})",
                timestamp=datetime.now(),
                data={
                    "wheelslip": wheelslip,
                    "threshold": threshold,
                    "slip_amount": wheelslip - threshold,
                },
            )

        return None

    def check_brake_pipe_discrepancy(self, current_data: Dict) -> Optional[Alert]:
        """Detectar discrepancia significativa entre presión tubo de freno delantera y cola"""
        if not self.config.get("brake_pipe_discrepancy", {}).get("enabled", False):
            return None

        # Revisar que ambos valores estén presentes
        present_front = current_data.get("presion_tubo_freno_presente", False)
        present_tail = current_data.get("presion_tubo_freno_cola_presente", False)
        if not (present_front and present_tail):
            return None

        front = current_data.get("presion_tubo_freno", None)
        tail = current_data.get("presion_tubo_freno_cola", None)
        if front is None or tail is None:
            return None

        try:
            diff = abs(float(front) - float(tail))
        except Exception:
            return None

        threshold = self.config.get("brake_pipe_discrepancy", {}).get("threshold_psi", 20.0)
        if diff > threshold:
            severity = AlertSeverity(self.config.get("brake_pipe_discrepancy", {}).get("severity", "high"))
            return Alert(
                alert_id=f"brake_pipe_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type=AlertType.BRAKE_PRESSURE_DISCREPANCY,
                severity=severity,
                title="Discrepancia Presión Tubo de Freno (Frente/Cola)",
                message=f"Diferencia de presión del tubo de freno entre frente ({front} PSI) y cola ({tail} PSI): {diff:.1f} PSI",
                timestamp=datetime.now(),
                data={"front": front, "tail": tail, "diff": diff, "threshold": threshold},
            )

        return None

    def check_performance_degradation(self) -> Optional[Alert]:
        """Verificar degradación de rendimiento del sistema"""
        if not self.config["performance_degradation"]["enabled"]:
            return None

        # Medir tiempo de respuesta del sistema TSC
        import time

        start_time = time.time()

        try:
            self.tsc_integration.leer_datos_archivo()
            response_time = (time.time() - start_time) * 1000  # ms

            threshold = self.config["performance_degradation"]["response_time_threshold_ms"]

            if response_time > threshold:
                severity = AlertSeverity(self.config["performance_degradation"]["severity"])
                return Alert(
                    alert_id=f"perf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type=AlertType.PERFORMANCE_DEGRADATION,
                    severity=severity,
                    title="Degradación de Rendimiento",
                    message=f"Tiempo de respuesta: {response_time:.0f}ms (umbral: {threshold}ms)",
                    timestamp=datetime.now(),
                    data={"response_time_ms": response_time, "threshold_ms": threshold},
                )

        except Exception as e:
            # Si hay error de conexión, generar alerta crítica
            return Alert(
                alert_id=f"system_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type=AlertType.SYSTEM_ERROR,
                severity=AlertSeverity.CRITICAL,
                title="Error de Sistema Crítico",
                message=f"Error accediendo a TSC: {str(e)}",
                timestamp=datetime.now(),
                data={"error": str(e)},
            )

        return None

    def perform_health_check(self) -> List[Alert]:
        """Realizar verificación completa de salud del sistema"""
        alerts = []

        try:
            # Obtener datos actuales
            raw_data = self.tsc_integration.leer_datos_archivo()

            if raw_data:
                # Convertir datos al formato IA
                current_data = self.tsc_integration.convertir_datos_ia(raw_data)
                # Guardar últimas lecturas para re-resolución automática
                self.last_telemetry = current_data

                # Verificar alertas basadas en datos actuales
                # Verificar alertas basadas en datos actuales
                speed_alert = self.check_speed_violation(current_data)
                if speed_alert:
                    alerts.append(speed_alert)

                # Fuel alerts removed per request - trains are always fueled

                temp_alert = self.check_overheating(current_data)
                if temp_alert:
                    alerts.append(temp_alert)

                wheelslip_alert = self.check_wheelslip(current_data)
                if wheelslip_alert:
                    alerts.append(wheelslip_alert)

                # Verificar discrepancia de presión de tubo de freno (frente vs cola)
                brake_diff_alert = self.check_brake_pipe_discrepancy(current_data)
                if brake_diff_alert:
                    alerts.append(brake_diff_alert)

            # Verificar rendimiento del sistema
            perf_alert = self.check_performance_degradation()
            if perf_alert:
                alerts.append(perf_alert)

        except Exception as e:
            print(f"Error en health check: {e}")
            alerts.append(
                Alert(
                    alert_id=f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type=AlertType.SYSTEM_ERROR,
                    severity=AlertSeverity.CRITICAL,
                    title="Error en Health Check",
                    message=f"Fallo en verificación de salud: {str(e)}",
                    timestamp=datetime.now(),
                    data={"error": str(e)},
                )
            )

        return alerts

    def analyze_recent_data(self, time_window_minutes: int = 10) -> List[Alert]:
        """Analizar datos recientes para detectar anomalías y tendencias"""
        alerts = []

        try:
            # Recopilar datos recientes
            if self.analyzer.load_data_from_tsc(
                max_records=100, collection_time=time_window_minutes
            ):
                # Verificar que tenemos datos antes de analizar
                if self.analyzer.df is not None:
                    # Verificar anomalías
                    anomaly_alerts = self.check_anomalies(self.analyzer.df)
                    alerts.extend(anomaly_alerts)

                    # Verificar caída en eficiencia
                    efficiency_alert = self.check_efficiency_drop(self.analyzer.df)
                    if efficiency_alert:
                        alerts.append(efficiency_alert)
                else:
                    print("No se pudieron cargar datos para análisis")

        except Exception as e:
            print(f"Error analizando datos recientes: {e}")

        return alerts

    def run_monitoring_cycle(self) -> List[Alert]:
        """Ejecutar un ciclo completo de monitoreo"""
        new_alerts = []

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ejecutando ciclo de monitoreo...")

        # Health check básico
        health_alerts = self.perform_health_check()
        new_alerts.extend(health_alerts)

        # Análisis de datos recientes (cada 5 minutos)
        if (
            self.last_check_time is None
            or (datetime.now() - self.last_check_time).total_seconds() > 300
        ):  # 5 minutos

            analysis_alerts = self.analyze_recent_data(time_window_minutes=5)
            new_alerts.extend(analysis_alerts)
            self.last_check_time = datetime.now()

        # Filtrar alertas duplicadas recientes (evitar spam)
        filtered_alerts = self._filter_duplicate_alerts(new_alerts)

        # Agregar alertas nuevas
        for alert in filtered_alerts:
            self.alerts.append(alert)
            print(f"[ALERTA] Nueva alerta: {alert.title} ({alert.severity.value})")

        # Guardar alertas
        if filtered_alerts:
            self.save_alerts()

        # Intentar resolver alertas transitorias basadas en última telemetría
        try:
            self._resolve_transient_alerts(self.last_telemetry)
        except Exception as e:
            print(f"[WARN] Error al intentar resolver alertas transitorias: {e}")

        return filtered_alerts

    def _filter_duplicate_alerts(
        self, new_alerts: List[Alert], time_window_minutes: int = 5
    ) -> List[Alert]:
        """Filtrar alertas duplicadas dentro de una ventana de tiempo"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_alerts = [a for a in self.alerts if a.timestamp > cutoff_time]

        filtered = []
        for new_alert in new_alerts:
            # Verificar si ya existe una alerta similar reciente
            duplicate = False
            for recent_alert in recent_alerts:
                if (
                    recent_alert.alert_type == new_alert.alert_type
                    and abs((recent_alert.timestamp - new_alert.timestamp).total_seconds()) < 60
                ):  # 1 minuto
                    duplicate = True
                    break

            if not duplicate:
                filtered.append(new_alert)

        return filtered

    def _resolve_transient_alerts(self, current_data: Optional[Dict] = None) -> None:
        """Marcar como reconocidas las alertas transitorias cuya condición ya se ha resuelto.

        Actualmente aplica a: speed_violation, wheelslip, overheating.
        """
        if current_data is None:
            current_data = self.last_telemetry
        if not current_data:
            return

        changed = False
        try:
            # Speed violations
            current_speed = self._to_float(current_data.get("velocidad_actual"))

            wheelslip_current = None
            # Prefer intensity normalized
            if current_data.get("deslizamiento_ruedas_intensidad") is not None:
                wheelslip_current = self._to_float(current_data.get("deslizamiento_ruedas_intensidad"))
            else:
                wheelslip_current = self._to_float(current_data.get("deslizamiento_ruedas"))

            temp_current = self._to_float(current_data.get("temperatura_motor"))

            for alert in self.alerts:
                if alert.acknowledged:
                    continue
                # Resolvemos solo tipo speed_violation / wheelslip / overheating
                try:
                    if alert.alert_type == AlertType.SPEED_VIOLATION:
                        # Obtener umbral del dato de la alerta o del config
                        max_speed_candidate = alert.data.get("max_speed", self.config["speed_violation"]["max_speed"])
                        max_speed_val = self._to_float(max_speed_candidate)
                        max_speed = max_speed_val if max_speed_val is not None else self.config["speed_violation"]["max_speed"]
                        if current_speed is not None and max_speed is not None and current_speed <= float(max_speed):
                            alert.acknowledged = True
                            alert.acknowledged_at = datetime.now()
                            print(f"[OK] Alerta resuelta automáticamente: {alert.alert_id} (speed)")
                            changed = True
                    elif alert.alert_type == AlertType.WHEELSLIP:
                        thr_candidate = alert.data.get("threshold", self.config["wheelslip"]["threshold"])
                        thr_val = self._to_float(thr_candidate)
                        threshold = thr_val if thr_val is not None else self.config["wheelslip"]["threshold"]
                        if wheelslip_current is not None and threshold is not None and wheelslip_current <= float(threshold):
                            alert.acknowledged = True
                            alert.acknowledged_at = datetime.now()
                            print(f"[OK] Alerta resuelta automáticamente: {alert.alert_id} (wheelslip)")
                            changed = True
                    elif alert.alert_type == AlertType.OVERHEATING:
                        th_candidate = alert.data.get("temperature_threshold", self.config["overheating"]["temperature_threshold"])
                        th_val = self._to_float(th_candidate)
                        threshold = th_val if th_val is not None else self.config["overheating"]["temperature_threshold"]
                        if temp_current is not None and threshold is not None and temp_current <= float(threshold):
                            alert.acknowledged = True
                            alert.acknowledged_at = datetime.now()
                            print(f"[OK] Alerta resuelta automáticamente: {alert.alert_id} (overheating)")
                            changed = True
                except Exception as e:
                    # No romper si hay error en evaluación de una alerta
                    print(f"[WARN] Error al evaluar resolución para {alert.alert_id}: {e}")
        except Exception as e:
            print(f"[WARN] Error evaluando alertas a resolver: {e}")

        if changed:
            self.save_alerts()

    def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[Alert]:
        """Obtener alertas activas (no reconocidas)"""
        active_alerts = [a for a in self.alerts if not a.acknowledged]

        if severity_filter:
            active_alerts = [a for a in active_alerts if a.severity == severity_filter]

        # Ordenar por severidad y timestamp (más recientes primero)
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3,
        }

        active_alerts.sort(key=lambda x: (severity_order[x.severity], -x.timestamp.timestamp()))
        return active_alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Marcar alerta como reconocida"""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.acknowledged:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                self.save_alerts()
                print(f"[OK] Alerta {alert_id} reconocida")
                return True

        return False

    def get_alerts_summary(self) -> Dict:
        """Obtener resumen de alertas"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        acknowledged_alerts = total_alerts - active_alerts

        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(self.get_active_alerts(severity))

        type_counts = {}
        for alert_type in AlertType:
            type_counts[alert_type.value] = len(
                [a for a in self.get_active_alerts() if a.alert_type == alert_type]
            )

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
        }

    def start_monitoring(self, interval_seconds: int = 30):
        """Iniciar monitoreo continuo"""
        import threading
        import time

        if self.monitoring_active:
            print("Monitoreo ya está activo")
            return

        self.monitoring_active = True
        print(f"Iniciando monitoreo continuo (intervalo: {interval_seconds}s)")

        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self.run_monitoring_cycle()
                except Exception as e:
                    print(f"Error en ciclo de monitoreo: {e}")

                time.sleep(interval_seconds)

        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()

    def stop_monitoring(self):
        """Detener monitoreo continuo"""
        self.monitoring_active = False
        print("Monitoreo detenido")


# Funciones de utilidad para integración con web dashboard
def get_alert_system() -> AlertSystem:
    """Obtener instancia singleton del sistema de alertas"""
    if not hasattr(get_alert_system, "_instance"):
        get_alert_system._instance = AlertSystem()
    return get_alert_system._instance


def check_alerts() -> Dict:
    """Función para verificar alertas (llamada desde web dashboard)"""
    system = get_alert_system()
    alerts = system.run_monitoring_cycle()
    active_list = system.get_active_alerts()

    return {
        "new_alerts": len(alerts),
        "active_alerts": len(active_list),
        "alerts": [alert.to_dict() for alert in alerts],
        "active_alerts_list": [a.to_dict() for a in active_list],
    }


if __name__ == "__main__":
    print("Sistema de Alertas - Train Simulator Autopilot")
    print("=" * 50)

    # Crear sistema de alertas
    alert_system = AlertSystem()

    # Ejecutar health check
    print("\n[HEALTH] Ejecutando health check...")
    alerts = alert_system.perform_health_check()

    if alerts:
        print(f"[ALERTA] {len(alerts)} alertas detectadas:")
        for alert in alerts:
            print(f"  {alert.severity.value.upper()}: {alert.title}")
    else:
        print("[OK] No se detectaron alertas en health check")

    # Ejecutar análisis de datos recientes
    print("\n[ANALISIS] Analizando datos recientes...")
    analysis_alerts = alert_system.analyze_recent_data(time_window_minutes=2)

    if analysis_alerts:
        print(f"[ALERTA] {len(analysis_alerts)} alertas de análisis detectadas:")
        for alert in analysis_alerts:
            print(f"  {alert.severity.value.upper()}: {alert.title}")
    else:
        print("[OK] No se detectaron anomalías en análisis reciente")

    # Mostrar resumen
    summary = alert_system.get_alerts_summary()
    print("\n[RESUMEN] Resumen de alertas:")
    print(f"  Total: {summary['total_alerts']}")
    print(f"  Activas: {summary['active_alerts']}")
    print(f"  Reconocidas: {summary['acknowledged_alerts']}")

    print("\n[TIP] Para iniciar monitoreo continuo, usar: alert_system.start_monitoring()")
