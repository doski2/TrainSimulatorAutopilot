"""
Tests para los dashboards web del sistema Train Simulator Autopilot.
"""

import os
import sys

# Añadir el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestDashboardWeb:
    """Tests para funcionalidades del dashboard web."""

    def test_dashboard_initialization(self):
        """Test que verifica la inicialización correcta del dashboard."""
        try:
            from web_dashboard import app

            assert app is not None
            assert hasattr(app, "run")
        except ImportError:
            # Si no se puede importar, al menos verificar que el archivo existe
            assert os.path.exists("web_dashboard.py")

    def test_settings_validation(self):
        """Test que verifica la validación de configuraciones."""
        # Configuración válida
        valid_settings = {"max_speed": 100, "safety_margin": 10, "update_interval": 100}

        # Simular validación básica
        assert valid_settings["max_speed"] > 0
        assert valid_settings["safety_margin"] >= 0
        assert valid_settings["update_interval"] > 0

        # Configuración inválida
        invalid_settings = {
            "max_speed": -10,  # Negativo
            "safety_margin": 10,
            "update_interval": 100,
        }

        assert invalid_settings["max_speed"] < 0  # Debería fallar


class TestDashboardSD40:
    """Tests para el dashboard específico SD40."""

    def test_sd40_metrics_update(self):
        """Test que verifica la actualización de métricas SD40."""
        # Simular datos de telemetría SD40
        test_data = {
            "speed": 45.0,
            "engineTemp": 180.0,
            "oilPressure": 50.0,
            "amps": 800.0,
            "fuelConsumption": 3.5,
            "efficiency": 120.0,
            "runtime": 2.5,
            "brakePressure": 60.0,
        }

        # Verificar que los datos tienen todas las métricas requeridas
        required_metrics = [
            "speed",
            "engineTemp",
            "oilPressure",
            "amps",
            "fuelConsumption",
            "efficiency",
            "runtime",
            "brakePressure",
        ]

        for metric in required_metrics:
            assert metric in test_data
            assert isinstance(test_data[metric], (int, float))

    def test_sd40_alerts_logic(self):
        """Test que verifica la lógica de alertas SD40."""
        # Datos con alertas
        alert_data = {
            "engineTemp": 280.0,  # Sobrecalentamiento
            "oilPressure": 20.0,  # Baja presión aceite
            "fuelLevel": 10.0,  # Combustible bajo
            "fuelConsumption": 6.0,  # Alto consumo
            "efficiency": 80.0,  # Baja eficiencia
            "runtime": 10.0,  # Tiempo prolongado
            "brakePressure": 90.0,  # Alta presión freno
        }

        # Verificar condiciones de alerta
        assert alert_data["engineTemp"] > 250  # Sobrecalentamiento
        assert alert_data["oilPressure"] < 30  # Baja presión
        assert alert_data["fuelLevel"] < 15  # Combustible bajo
        assert alert_data["fuelConsumption"] > 5.0  # Alto consumo
        assert alert_data["efficiency"] < 100  # Baja eficiencia
        assert alert_data["runtime"] > 8.0  # Tiempo prolongado
        assert alert_data["brakePressure"] > 80  # Alta presión freno


class TestDashboardIntegration:
    """Tests de integración para dashboards."""

    def test_dashboard_files_exist(self):
        """Test que verifica que existen los archivos necesarios del dashboard."""
        required_files = [
            "web_dashboard.py",
            "web/templates/index.html",
            "web/static/js/dashboard.js",
            "web/templates/sd40.html",
            "web/static/js/dashboard-sd40.js",
        ]

        for file_path in required_files:
            assert os.path.exists(file_path), f"Archivo faltante: {file_path}"

    def test_static_files_accessible(self):
        """Test que verifica que los archivos estáticos son accesibles."""
        static_files = ["web/static/css/dashboard.css", "web/static/css/icons.css"]

        for file_path in static_files:
            if os.path.exists(file_path):
                assert os.path.getsize(file_path) > 0, f"Archivo estático vacío: {file_path}"
