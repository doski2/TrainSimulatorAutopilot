import os
import sys

import pytest

# Ensure project root is importable for tests when run from pytest runner
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tsc_integration import TSCIntegration  # noqa: E402


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
    assert pytest.approx(datos_ia["freno_tren"], 0.01) == 0.5


def test_infer_presion_freno_tren_from_train_brake_control():
    integ = TSCIntegration(ruta_archivo=None)
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


def test_posicion_freno_tren_presence():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"TrainBrakeControl": 0.4}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("posicion_freno_tren_presente") is True


def test_brake_pipe_tail_presence_flag():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"BrakePipePressureTailEnd": 90.0}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("presion_tubo_freno_cola_presente") is True
    assert datos_ia.get("presion_tubo_freno_cola") == 90.0


def test_fuel_conversion_with_capacity():
    integ = TSCIntegration(ruta_archivo=None, fuel_capacity_gallons=300.0)
    datos_archivo = {"FuelLevel": 0.5}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("combustible_porcentaje") == 50.0
    assert datos_ia.get("combustible_galones") == 150.0


def test_fuel_raw_gallons_with_capacity():
    integ = TSCIntegration(ruta_archivo=None, fuel_capacity_gallons=300.0)
    datos_archivo = {"FuelLevel": 50.0}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("combustible_galones") == 50.0
    assert pytest.approx((50.0 / 300.0) * 100.0, abs=0.1) == float(datos_ia.get("combustible_porcentaje", 0.0))


def test_fuel_raw_gallons_without_capacity():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"FuelLevel": 4000.0}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("combustible_galones") == 4000.0


def test_tractive_effort_presence_flag():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"TractiveEffort": 123.0}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia.get("esfuerzo_traccion") == 123.0


def test_rpm_inferred_from_regulator():
    integ = TSCIntegration(ruta_archivo=None)
    datos_archivo = {"Regulator": 0.5}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    # Default max_engine_rpm is 5000.0, so expected inferred RPM is 2500
    assert datos_ia.get("rpm_inferida") is True
    assert pytest.approx(datos_ia.get("rpm", 0), abs=1.0) == 2500.0


def test_wheelslip_normalization_cases():
    integ = TSCIntegration(ruta_archivo=None)
    # Normalized 0..1
    datos_archivo = {"Wheelslip": 0.5}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert pytest.approx(datos_ia["deslizamiento_ruedas_intensidad"], abs=0.001) == 0.5

    # Base-1 asset (1..2) mapping
    datos_archivo = {"Wheelslip": 1.5}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert pytest.approx(datos_ia["deslizamiento_ruedas_intensidad"], abs=0.001) == 0.5

    # Max values map to 1.0
    datos_archivo = {"Wheelslip": 2.0}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia["deslizamiento_ruedas_intensidad"] == 1.0


def test_wheelslip_inference_from_tractive():
    integ = TSCIntegration(ruta_archivo=None)
    # Asset doesn't provide Wheelslip, but provides high tractive effort and low speed
    datos_archivo = {
        "TractiveEffort": 800.0,  # high effort
        "CurrentSpeed": 0.5,  # m/s -> 1.8 km/h (low)
        "RPM": 1200,
    }
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    # Expect inference to set intensity > 0
    assert datos_ia["deslizamiento_ruedas_intensidad"] > 0.0
    assert datos_ia.get("deslizamiento_ruedas_inferida") is True

    datos_archivo = {"Wheelslip": 3.0}
    datos_ia = integ.convertir_datos_ia(datos_archivo)
    assert datos_ia["deslizamiento_ruedas_intensidad"] == 1.0
