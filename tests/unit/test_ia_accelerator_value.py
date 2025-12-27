from autopilot_system import IASistema


def test_ia_computes_acceleration_value():
    ia = IASistema()
    # Provide telemetry where velocidad_actual=50 km/h and limit=80 km/h
    datos = {"velocidad_actual": 50.0, "limite_velocidad": 80.0}
    comandos = ia.procesar_telemetria(datos)
    # deficit = 30 => acelerador = min(0.8, 30/20=1.5) => 0.8
    assert comandos["decision"] == "ACELERAR"
    assert abs(comandos["acelerador"] - 0.8) < 1e-6
