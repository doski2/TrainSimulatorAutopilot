import os
import sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from alert_system import AlertSystem, AlertType


def test_brake_pipe_discrepancy_alert():
    # Use a fresh AlertSystem instance
    alert_system = AlertSystem(alerts_file='test_alerts.json', config_file='test_alert_config.json')

    # Ensure threshold is small for test
    alert_system.config['brake_pipe_discrepancy']['threshold_psi'] = 10.0
    alert_system.config['brake_pipe_discrepancy']['enabled'] = True

    # Monkeypatch TSCIntegration reader to return a raw data with front/tail mismatch
    def fake_leer():
        return {'AirBrakePipePressurePSI': 90.0, 'BrakePipePressureTailEnd': 60.0}

    alert_system.tsc_integration.leer_datos_archivo = fake_leer

    alerts = alert_system.perform_health_check()
    # We expect one brake pipe discrepancy alert
    found = any(a.alert_type == AlertType.BRAKE_PRESSURE_DISCREPANCY for a in alerts)
    assert found
