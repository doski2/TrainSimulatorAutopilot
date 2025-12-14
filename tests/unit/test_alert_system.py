import os
import sys
import pytest

# Ensure project root is importable when running from pytest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from alert_system import AlertSystem, AlertType


def test_check_wheelslip_triggered_above_threshold():
    system = AlertSystem(alerts_file=".test_alerts.json", config_file=".test_alerts_config.json")
    # Set threshold low to make test simpler
    system.config["wheelslip"]["threshold"] = 0.5
    data = {"deslizamiento_ruedas_intensidad": 0.6}
    alert = system.check_wheelslip(data)
    assert alert is not None
    assert alert.alert_type == AlertType.WHEELSLIP


def test_check_wheelslip_no_alert_below_threshold():
    system = AlertSystem(alerts_file=".test_alerts.json", config_file=".test_alerts_config.json")
    system.config["wheelslip"]["threshold"] = 0.5
    data = {"deslizamiento_ruedas_intensidad": 0.4}
    alert = system.check_wheelslip(data)
    assert alert is None


def test_auto_resolve_speed_violation():
    # Verifica que una alerta de velocidad se resuelve automáticamente cuando la velocidad vuelve por debajo del límite
    system = AlertSystem(alerts_file=".test_alerts.json", config_file=".test_alerts_config.json")
    system.config["speed_violation"]["max_speed"] = 120
    # Crear alerta de velocidad activa
    from alert_system import Alert, AlertSeverity
    alert = Alert(
        alert_id="speed_test_1",
        alert_type=AlertType.SPEED_VIOLATION,
        severity=AlertSeverity.HIGH,
        title="Violación de Velocidad Detectada",
        message="Velocidad actual: 145.0 km/h (límite: 120 km/h)",
        timestamp=__import__('datetime').datetime.now(),
        data={"current_speed": 145.0, "max_speed": 120},
    )
    system.alerts.append(alert)
    # Simular telemetría actual por debajo del límite
    system.last_telemetry = {"velocidad_actual": 100.0}
    system._resolve_transient_alerts(system.last_telemetry)
    # Se espera que la alerta haya sido marcada como reconocida (resuelta)
    resolved = any(a.alert_id == "speed_test_1" and a.acknowledged for a in system.alerts)
    assert resolved


def test_auto_resolve_wheelslip():
    system = AlertSystem(alerts_file=".test_alerts.json", config_file=".test_alerts_config.json")
    system.config["wheelslip"]["threshold"] = 0.5
    from alert_system import Alert, AlertSeverity
    alert = Alert(
        alert_id="wheelslip_test_1",
        alert_type=AlertType.WHEELSLIP,
        severity=AlertSeverity.HIGH,
        title="Deslizamiento de Ruedas Detectado",
        message="Deslizamiento: 1.00 (umbral: 0.5)",
        timestamp=__import__('datetime').datetime.now(),
        data={"wheelslip": 1.0, "threshold": 0.5},
    )
    system.alerts.append(alert)
    system.last_telemetry = {"deslizamiento_ruedas_intensidad": 0.2}
    system._resolve_transient_alerts(system.last_telemetry)
    resolved = any(a.alert_id == "wheelslip_test_1" and a.acknowledged for a in system.alerts)
    assert resolved
