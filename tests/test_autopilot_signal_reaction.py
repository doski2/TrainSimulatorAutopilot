import os
import sys

# Ensure project root is in sys.path so tests can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autopilot_system import AutopilotSystem


def test_autopilot_reacts_to_red_signal(monkeypatch):
    system = AutopilotSystem()
    system.sesion_activa = True

    # Setup fake telemetry where signal is RED (0)
    fake_telemetry = {"velocidad": 50.0, "limite_velocidad": 80.0, "senal_procesada": 0}

    # Monkeypatch tsc.obtener_datos_telemetria to return our fake telemetry
    monkeypatch.setattr(system.tsc, "obtener_datos_telemetria", lambda: fake_telemetry)

    # Run a control cycle
    result = system.ejecutar_ciclo_control()
    assert result is not None
    comandos = result["comandos"]
    assert comandos["decision"] == "SEÑAL_ROJA_STOP"
    assert comandos["freno_tren"] >= 1.0
    assert comandos["acelerador"] == 0.0


def test_autopilot_ignores_red_signal_when_autobrake_disabled(monkeypatch):
    system = AutopilotSystem()
    system.sesion_activa = True
    # Desactivar autobrake_by_signal
    system.autobrake_by_signal = False

    # Setup fake telemetry where signal is RED (0)
    fake_telemetry = {"velocidad": 50.0, "limite_velocidad": 80.0, "senal_procesada": 0}

    monkeypatch.setattr(system.tsc, "obtener_datos_telemetria", lambda: fake_telemetry)

    result = system.ejecutar_ciclo_control()
    assert result is not None
    comandos = result["comandos"]
    # Cuando la opción está desactivada, no debe aplicarse la regla SEÑAL_ROJA_STOP
    assert comandos["decision"] != "SEÑAL_ROJA_STOP"
