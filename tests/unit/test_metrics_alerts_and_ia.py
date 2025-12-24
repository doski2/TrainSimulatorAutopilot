import os
import tempfile

from alert_system import AlertSystem
from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration
from web_dashboard import app


def test_alert_metrics_reflect_generated_alert(tmp_path, monkeypatch):
    # Prepare TSCIntegration with high speed to trigger speed violation
    temp_file = tmp_path / "GetData.txt"
    temp_file.write_text("ControlName:CurrentSpeed\nControlValue:200.0\n", encoding="utf-8")

    tsc = TSCIntegration(ruta_archivo=str(temp_file))
    alert = AlertSystem(alerts_file=str(tmp_path / ".alerts.json"), config_file=str(tmp_path / ".alerts_config.json"))
    # Inject TSC into alert system
    alert.tsc_integration = tsc

    # Run monitoring cycle to generate alerts
    new_alerts = alert.run_monitoring_cycle()
    assert len(new_alerts) >= 1

    # Expose via web_dashboard metrics
    import web_dashboard
    monkeypatch.setattr(web_dashboard, 'alert_system', alert, raising=False)

    with app.test_client() as client:
        resp = client.get('/metrics')
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        assert 'alerts_total_generated' in text
        assert 'alerts_last_cycle_count' in text
        # last_cycle_count should be >=1
        assert ('alerts_last_cycle_count 0' not in text)


def test_ia_metrics_update_and_exposed(monkeypatch):
    # Prepare autopilot system and mock tsc to return telemetry
    tsci = TSCIntegration()
    ap = AutopilotSystem()
    ap.tsc = tsci

    # Mock TSC to return deterministic telemetry
    def fake_leer():
        return {'CurrentSpeed': 5.0, 'CurrentSpeedLimit': 20.0}

    # Use the named fake_leer function instead of an inline lambda so the test can be
    # extended or inspected more easily.
    monkeypatch.setattr(tsci, 'leer_datos_archivo', fake_leer)
    monkeypatch.setattr(tsci, 'convertir_datos_ia', lambda x: {'velocidad_actual': 18.0, 'limite_velocidad': 20.0})

    # Ensure session active so ejecutar_ciclo_control proceeds
    ap.sesion_activa = True
    # Execute one control cycle
    res = ap.ejecutar_ciclo_control()
    assert res is not None
    # IA metrics should be updated
    assert ap.ia.metrics["decision_total"] >= 1

    # Inject into web_dashboard and check metrics
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    with app.test_client() as client:
        resp = client.get('/metrics')
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        assert 'autopilot_ia_decision_total' in text
        assert 'autopilot_ia_decision_last_latency_ms' in text
