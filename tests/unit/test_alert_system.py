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
