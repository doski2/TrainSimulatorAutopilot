import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
# Skip tests that depend on seaborn/matplotlib
pytest.importorskip("matplotlib")
from alert_system import AlertSystem, AlertType  # noqa: E402

pytestmark = pytest.mark.integration  # requires seaborn/matplotlib


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


def test_health_check_handles_none_values():
    alert_system = AlertSystem(alerts_file='test_alerts.json', config_file='test_alert_config.json')

    # Set some config thresholds to None to simulate misconfiguration
    alert_system.config['performance_degradation']['response_time_threshold_ms'] = None

    # Fake leer_datos_archivo to return None values for numeric fields
    def fake_leer_none():
        return {
            'velocidad_actual': None,
            'deslizamiento_ruedas_intensidad': None,
            'temperatura': None,
        }

    alert_system.tsc_integration.leer_datos_archivo = fake_leer_none

    # Should not raise; should return a list (possibly empty or with safe alerts)
    alerts = alert_system.perform_health_check()
    assert isinstance(alerts, list)
