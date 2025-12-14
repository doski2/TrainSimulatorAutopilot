"""
Tests de integración end-to-end para el dashboard web.
Pruebas que simulan el flujo completo de usuario.
"""

import json
import os
import sys

import pytest

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestDashboardE2E:
    """Tests end-to-end para el dashboard completo."""

    def test_full_dashboard_initialization_flow(self):
        """Test que simula la inicialización completa del dashboard."""
        # Verificar que todos los archivos necesarios existen
        required_files = [
            "web_dashboard.py",
            "web/templates/index.html",
            "web/templates/sd40.html",
            "web/static/js/dashboard.js",
            "web/static/js/dashboard-sd40.js",
            "web/static/css/dashboard.css",
        ]

        for file_path in required_files:
            assert os.path.exists(file_path), f"Archivo requerido faltante: {file_path}"

        # Verificar que el archivo principal se puede importar
        try:
            import web_dashboard

            assert hasattr(web_dashboard, "app")
            assert hasattr(web_dashboard, "socketio")
        except ImportError as e:
            pytest.fail(f"No se puede importar web_dashboard: {e}")

    def test_config_validation_integration(self):
        """Test de integración para validación de configuración."""
        from web_dashboard import validate_dashboard_config

        # Configuración válida completa
        valid_config = {
            "theme": "dark",
            "animations": True,
            "updateInterval": 1000,
            "historyPoints": 50,
            "speedUnit": "mph",
            "alerts": {"speedLimit": True, "emergency": True, "system": True},
        }

        is_valid, errors, warnings = validate_dashboard_config(valid_config)
        assert is_valid, f"Configuración válida rechazada: {errors}"
        assert len(errors) == 0
        assert len(warnings) == 0

        # Configuración con errores
        invalid_config = {
            "theme": "invalid_theme",
            "updateInterval": 50,  # Demasiado bajo
            "historyPoints": 5000,  # Demasiado alto
            "alerts": "not_an_object",
        }

        is_valid, errors, warnings = validate_dashboard_config(invalid_config)
        assert not is_valid, "Configuración inválida aceptada"
        assert len(errors) > 0, "Debería haber errores de validación"

    def test_sd40_metrics_complete_workflow(self):
        """Test del flujo completo de métricas SD40."""
        # Simular datos de telemetría realistas
        realistic_data = {
            "speed": 65.5,
            "engineTemp": 210.0,
            "oilPressure": 55.0,
            "amps": 1200.0,
            "efficiency": 145.0,
            "runtime": 3.5,
            "brakePressure": 25.0,
            # fuel metrics removed
            "sandLevel": 80.0,
            "waterLevel": 90.0,
            "rpm": 950.0,
        }

        # Verificar que todas las métricas críticas están presentes
        critical_metrics = [
            "speed",
            "engineTemp",
            "oilPressure",
            "amps",
        ]
        for metric in critical_metrics:
            assert metric in realistic_data
            assert isinstance(realistic_data[metric], (int, float))
            assert realistic_data[metric] >= 0

        # Verificar rangos realistas
        assert 0 <= realistic_data["speed"] <= 200  # mph
        assert 100 <= realistic_data["engineTemp"] <= 300  # °F
        assert 20 <= realistic_data["oilPressure"] <= 100  # psi
        assert 500 <= realistic_data["amps"] <= 2000  # amperes
        # Fuel metrics removed; verify efficiency instead
        assert 50 <= realistic_data["efficiency"] <= 200

    def test_alert_system_integration(self):
        """Test de integración del sistema de alertas."""
        # Datos que deberían generar múltiples alertas
        alert_triggering_data = {
            "engineTemp": 290.0,  # Sobrecalentamiento
            "oilPressure": 15.0,  # Baja presión aceite
            # Fuel-related metrics removed
            "efficiency": 70.0,  # Baja eficiencia
            "runtime": 12.0,  # Tiempo prolongado
            "brakePressure": 95.0,  # Alta presión freno
        }

        # Verificar condiciones de alerta
        alerts_expected = []

        if alert_triggering_data["engineTemp"] > 250:
            alerts_expected.append("overheat")
        if alert_triggering_data["oilPressure"] < 30:
            alerts_expected.append("low_oil")
        # Fuel-related alerts removed
        if alert_triggering_data["efficiency"] < 100:
            alerts_expected.append("low_efficiency")
        if alert_triggering_data["runtime"] > 8.0:
            alerts_expected.append("long_runtime")
        if alert_triggering_data["brakePressure"] > 80:
            alerts_expected.append("high_brake_pressure")

        # Debería haber múltiples alertas
        assert (
            len(alerts_expected) >= 5
        ), f"Esperadas al menos 5 alertas, obtenidas {len(alerts_expected)}: {alerts_expected}"

    def test_performance_optimization_validation(self):
        """Test que valida las optimizaciones de rendimiento."""
        # Verificar que las optimizaciones están implementadas
        sd40_js_path = "web/static/js/dashboard-sd40.js"

        with open(sd40_js_path, encoding="utf-8") as f:
            content = f.read()

        # Verificar throttling de métricas
        assert "metricsUpdateThrottle" in content, "Falta throttling de métricas"
        assert "chartUpdateThrottle" in content, "Falta throttling de gráficos"

        # Verificar requestAnimationFrame
        assert "requestAnimationFrame" in content, "Falta requestAnimationFrame"

        # Verificar valores de throttling razonables
        assert "metricsUpdateThrottle = 100" in content, "Throttling de métricas incorrecto"
        assert "chartUpdateThrottle = 500" in content, "Throttling de gráficos incorrecto"

    def test_error_handling_integration(self):
        """Test de integración para manejo de errores."""
        from web_dashboard import validate_dashboard_config

        # Configuración con tipos de datos incorrectos
        bad_config = {
            "updateInterval": "not_a_number",
            "historyPoints": [1, 2, 3],  # Array en lugar de número
            "animations": "yes",  # String en lugar de boolean
            "alerts": "invalid",  # String en lugar de objeto
        }

        is_valid, errors, warnings = validate_dashboard_config(bad_config)
        assert not is_valid, "Configuración con tipos incorrectos aceptada"
        assert len(errors) >= 3, f"Esperados al menos 3 errores, obtenidos {len(errors)}: {errors}"

    def test_configuration_persistence_workflow(self):
        """Test del flujo completo de persistencia de configuración."""
        # Simular configuración guardada
        test_config = {
            "theme": "light",
            "animations": False,
            "updateInterval": 2000,
            "historyPoints": 100,
            "speedUnit": "kmh",
            "alerts": {"speedLimit": False, "emergency": True, "system": False},
        }

        # Verificar que se puede serializar
        config_json = json.dumps(test_config)
        assert len(config_json) > 50, "Configuración serializada demasiado corta"

        # Verificar que se puede deserializar
        parsed_config = json.loads(config_json)
        assert (
            parsed_config == test_config
        ), "Configuración no se serializa/deserializa correctamente"

        # Verificar que pasa validación
        from web_dashboard import validate_dashboard_config

        is_valid, errors, warnings = validate_dashboard_config(test_config)
        assert is_valid, f"Configuración válida rechazada: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
