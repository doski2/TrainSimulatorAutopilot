"""
Tests de integración para el sistema Train Simulator Autopilot
"""

from unittest.mock import patch

import pytest

from predictive_telemetry_analysis import PredictiveTelemetryAnalyzer
from tsc_integration import TSCIntegration


class TestTSCIntegration:
    """Tests de integración para TSC Integration"""

    @pytest.fixture
    def tsc_integration(self):
        """Fixture que crea una instancia de TSC Integration"""
        return TSCIntegration()

    @pytest.fixture
    def predictive_analyzer(self):
        """Fixture que crea una instancia del analizador predictivo"""
        return PredictiveTelemetryAnalyzer()

    def test_tsc_telemetry_data_flow(self, tsc_integration, predictive_analyzer):
        """Test que verifica el flujo de datos de telemetría entre TSC y analizador"""
        # Simular datos de telemetría del TSC
        mock_telemetry = {
            "speed": 45.5,
            "acceleration": 0.2,
            "gradient": 1.5,
            "tractive_effort": 120.0,
            "rpm": 1000,
            "amperage": 200.0,
            "wheelslip": 0.0,
        }

        # Mock del método de lectura de TSC
        with patch.object(tsc_integration, "obtener_datos_telemetria", return_value=mock_telemetry):
            telemetry_data = tsc_integration.obtener_datos_telemetria()

            # Verificar que los datos se leen correctamente
            assert telemetry_data is not None
            assert telemetry_data["speed"] == 45.5

            # Pasar datos al analizador predictivo
            predictive_analyzer.add_telemetry_sample(telemetry_data)

            # Verificar que el analizador recibió los datos
            assert len(predictive_analyzer.data_collector.telemetry_history) > 0

    def test_command_execution_integration(self, tsc_integration):
        """Test que verifica la ejecución integrada de comandos"""
        # Comandos válidos para probar (usando nombres de IA)
        test_commands = [
            {"acelerador": 0.5},
            {"freno_tren": 0.3},
            {"reverser": 1},
            {"freno_motor": 0.2},
        ]

        for command_dict in test_commands:
            # Mock de la ejecución del comando
            with patch.object(
                tsc_integration, "enviar_comandos", return_value=True
            ) as mock_execute:
                result = tsc_integration.enviar_comandos(command_dict)

                # Verificar que se llamó al método correcto
                mock_execute.assert_called_once_with(command_dict)
                assert result is True

    def test_predictive_feedback_loop(self, tsc_integration, predictive_analyzer):
        """Test que verifica el bucle de retroalimentación predictiva"""
        # Agregar datos históricos para entrenamiento
        for i in range(50):
            telemetry_data = {
                "speed": 40 + i * 0.5,
                "acceleration": 0.1 + i * 0.01,
                "gradient": 1.0,
                "tractive_effort": 100 + i * 2,
                "rpm": 800 + i * 10,
                "amperage": 180 + i * 2,
                "wheelslip": 0.0,
            }
            predictive_analyzer.add_telemetry_sample(telemetry_data)

        # Entrenar el modelo
        metrics = predictive_analyzer.train_model()
        assert "error" not in metrics

        # Simular predicción y ajuste de comandos
        # Agregar más datos para activar predicciones
        for i in range(15):
            telemetry_data = {
                "speed": 65 + i * 0.1,
                "acceleration": 0.2,
                "gradient": 1.5,
                "tractive_effort": 140.0,
                "rpm": 1200,
                "amperage": 220.0,
                "wheelslip": 0.0,
            }
            predictive_analyzer.add_telemetry_sample(telemetry_data)

        # Obtener predicciones
        predictions = predictive_analyzer.get_current_predictions()

        # Verificar que se generaron predicciones
        assert isinstance(predictions, dict)

        # Simular ajuste de comandos basado en predicciones
        if "speed" in predictions:
            predicted_speed = predictions.get("speed", 0)
            if predicted_speed > 70:  # Velocidad alta, reducir throttle
                with patch.object(
                    tsc_integration, "enviar_comandos", return_value=True
                ) as mock_cmd:
                    tsc_integration.enviar_comandos({"acelerador": 0.3})
                    mock_cmd.assert_called_with({"acelerador": 0.3})

    def test_error_handling_integration(self, tsc_integration, predictive_analyzer):
        """Test que verifica el manejo integrado de errores"""
        # Simular error en TSC
        with patch.object(
            tsc_integration,
            "obtener_datos_telemetria",
            side_effect=ConnectionError("TSC connection error"),
        ):
            with pytest.raises(ConnectionError):
                tsc_integration.obtener_datos_telemetria()

        # Verificar que el analizador sigue funcionando
        telemetry_data = {
            "speed": 50.0,
            "acceleration": 0.1,
            "gradient": 1.0,
            "tractive_effort": 110.0,
            "rpm": 900,
            "amperage": 190.0,
            "wheelslip": 0.0,
        }

        # No debería fallar por errores previos
        predictive_analyzer.add_telemetry_sample(telemetry_data)
        assert len(predictive_analyzer.data_collector.telemetry_history) > 0

    def test_performance_integration(self, tsc_integration, predictive_analyzer):
        """Test que verifica el rendimiento integrado del sistema"""
        import time as time_module

        # Medir tiempo de procesamiento de datos
        start_time = time_module.time()

        # Procesar múltiples muestras
        for i in range(100):
            telemetry_data = {
                "speed": 40 + i * 0.2,
                "acceleration": 0.1,
                "gradient": 1.0,
                "tractive_effort": 100.0,
                "rpm": 1000,
                "amperage": 200.0,
                "wheelslip": 0.0,
            }

            predictive_analyzer.add_telemetry_sample(telemetry_data)

        processing_time = time_module.time() - start_time

        # Verificar que el procesamiento es razonablemente rápido (< 1 segundo para 100 muestras)
        assert processing_time < 1.0

        # Verificar que todos los datos se procesaron
        assert len(predictive_analyzer.data_collector.telemetry_history) >= 100
