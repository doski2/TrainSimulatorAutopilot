from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration


def test_metrics_update_failure_does_not_raise(monkeypatch):
    # Prepare system and inject test telemetry
    tsci = TSCIntegration()
    ap = AutopilotSystem()
    ap.tsc = tsci

    # Simulate TSC returns telemetry
    monkeypatch.setattr(tsci, 'obtener_datos_telemetria', lambda: {'velocidad': 10.0, 'limite_velocidad_actual': 20.0})

    # Simulate broken metrics container (e.g., None or wrong type)
    ap.ia.metrics = None

    # Ensure session active so ejecutar_ciclo_control proceeds
    ap.sesion_activa = True

    # Should not raise even if metrics update fails internally
    result = ap.ejecutar_ciclo_control()
    assert result is not None
    # Restore a sane metrics object and run again to verify normal operation
    ap.ia.metrics = {'decision_total': 0, 'decision_total_time_ms': 0.0, 'decision_last_latency_ms': 0.0}
    result2 = ap.ejecutar_ciclo_control()
    assert result2 is not None
    assert ap.ia.metrics['decision_total'] >= 1