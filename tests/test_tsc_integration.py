import pytest
from tsc_integration import TSCIntegration


def test_train_brake_control_sets_freno_tren():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"TrainBrakeControl": 0.8}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert "posicion_freno_tren" in datos_ia
    assert pytest.approx(datos_ia["posicion_freno_tren"], 0.01) == 0.8
    assert pytest.approx(datos_ia["freno_tren"], 0.01) == 0.8


def test_virtual_brake_sets_freno_tren():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"VirtualBrake": 0.5}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert "posicion_freno_tren" in datos_ia
    # VirtualBrake mapped to posicion_freno_tren
    assert pytest.approx(datos_ia["freno_tren"], 0.01) == 0.5


def test_infer_presion_freno_tren_from_train_brake_control():
    integ = TSCIntegration(ruta_archivo=None)
    # No TrainBrakeCylinderPressurePSI present
    datos_archivo = {"TrainBrakeControl": 1.0}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("presion_freno_tren_inferida", False) is True
    assert datos_ia.get("presion_freno_tren", 0) > 0


def test_presion_tubo_freno_presence_flag():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"AirBrakePipePressurePSI": 66.8}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("presion_tubo_freno_presente") is True
    assert datos_ia.get("presion_tubo_freno") == 66.8
