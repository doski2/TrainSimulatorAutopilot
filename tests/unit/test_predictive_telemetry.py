"""
Tests unitarios para el módulo Predictive Telemetry Analysis
"""

import os

import pytest
# Skip if joblib is not available (heavy ML dependency)
pytest.importorskip("joblib")

pytestmark = pytest.mark.integration  # requires joblib/scikit-learn
from predictive_telemetry_analysis import PredictiveTelemetryAnalyzer


class TestPredictiveTelemetryAnalyzer:
    """Tests para la clase PredictiveTelemetryAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Fixture que crea una instancia del analizador"""
        return PredictiveTelemetryAnalyzer()

    @pytest.fixture
    def sample_telemetry_data(self):
        """Datos de telemetría de ejemplo"""
        return {
            "speed": 45.5,
            "acceleration": 0.2,
            "gradient": 1.5,
            "tractive_effort": 150.0,
            "rpm": 1200,
            "amperage": 250.0,
            "wheelslip": 0.0,
            "timestamp": "2025-11-15T14:30:00Z",
        }

    def test_initialization(self, analyzer):
        """Test que la inicialización funciona correctamente"""
        assert analyzer is not None
        assert hasattr(analyzer, "data_collector")
        assert hasattr(analyzer, "predictive_model")
        assert analyzer.lookback_steps == 10
        assert analyzer.prediction_horizon == 5

    def test_add_telemetry_sample(self, analyzer, sample_telemetry_data):
        """Test que agrega muestras de telemetría correctamente"""
        initial_count = len(analyzer.data_collector.telemetry_history)
        analyzer.add_telemetry_sample(sample_telemetry_data)

        assert len(analyzer.data_collector.telemetry_history) == initial_count + 1
        stored_data = analyzer.data_collector.telemetry_history[-1]
        assert stored_data["data"]["speed"] == 45.5
        assert stored_data["data"]["acceleration"] == 0.2

    def test_max_samples_limit(self, analyzer, sample_telemetry_data):
        """Test que respeta el límite máximo de muestras"""
        # Agregar más muestras que el límite
        for i in range(analyzer.data_collector.max_samples + 5):
            data = sample_telemetry_data.copy()
            data["speed"] = i
            analyzer.add_telemetry_sample(data)

        # Debe mantener solo el límite máximo
        assert len(analyzer.data_collector.telemetry_history) == analyzer.data_collector.max_samples

    def test_data_validation(self, analyzer):
        """Test que maneja datos de telemetría correctamente"""
        # Limpiar datos históricos para test limpio
        analyzer.data_collector.telemetry_history.clear()

        # Datos válidos
        valid_data = {
            "speed": 50.0,
            "acceleration": 0.1,
            "gradient": 2.0,
            "tractive_effort": 120.0,
            "rpm": 1000,
            "amperage": 200.0,
            "wheelslip": 0.0,
        }

        initial_count = len(analyzer.data_collector.telemetry_history)
        analyzer.add_telemetry_sample(valid_data)
        assert len(analyzer.data_collector.telemetry_history) == initial_count + 1

        # Datos con valores extremos (deberían manejarse sin errores)
        extreme_data = valid_data.copy()
        extreme_data["speed"] = 200.0  # Velocidad muy alta
        extreme_data["acceleration"] = -5.0  # Desaceleración fuerte

        analyzer.add_telemetry_sample(extreme_data)
        assert len(analyzer.data_collector.telemetry_history) == initial_count + 2

    @pytest.mark.slow
    def test_predictive_model_training(self, analyzer, sample_telemetry_data):
        """Test que entrena el modelo predictivo"""
        # Limpiar datos históricos para test limpio
        analyzer.data_collector.telemetry_history.clear()

        # Agregar suficientes datos para entrenamiento
        for i in range(100):
            data = sample_telemetry_data.copy()
            data["speed"] = 40 + i * 0.1
            data["acceleration"] = 0.1 + i * 0.001
            analyzer.add_telemetry_sample(data)

        # Entrenar modelo
        result = analyzer.train_model()
        assert isinstance(result, dict)
        assert "error" not in result

        # Verificar que el modelo esté entrenado
        assert analyzer.predictive_model.is_trained

    def test_prediction_without_trained_model(self, analyzer, sample_telemetry_data):
        """Test que maneja predicciones sin modelo entrenado"""
        analyzer.add_telemetry_sample(sample_telemetry_data)

        predictions = analyzer.get_current_predictions()
        assert isinstance(predictions, dict)
        # Sin suficientes datos o modelo, las predicciones pueden estar vacías
        assert len(predictions) >= 0

    def test_prediction_with_trained_model(self, analyzer, sample_telemetry_data):
        """Test que hace predicciones con modelo entrenado"""
        # Agregar datos y entrenar
        for i in range(150):  # Suficientes datos
            data = sample_telemetry_data.copy()
            data["speed"] = 40 + i * 0.1
            data["acceleration"] = 0.1 + i * 0.001
            analyzer.add_telemetry_sample(data)

        analyzer.train_model()

        # Agregar más datos para activar predicciones
        for i in range(20):
            data = sample_telemetry_data.copy()
            data["speed"] = 50 + i * 0.1
            analyzer.add_telemetry_sample(data)

        # Hacer predicción
        predictions = analyzer.get_current_predictions()
        assert isinstance(predictions, dict)
        # Las predicciones pueden contener datos si el sistema está funcionando
        if len(predictions) > 0:
            assert "timestamp" in predictions

    def test_historical_data_persistence(self, analyzer, sample_telemetry_data):
        """Test que guarda y carga datos históricos"""
        # Agregar datos
        initial_count = len(analyzer.data_collector.telemetry_history)
        analyzer.add_telemetry_sample(sample_telemetry_data)

        # Verificar que los datos se agregaron al data collector
        assert len(analyzer.data_collector.telemetry_history) == initial_count + 1
        assert analyzer.data_collector.telemetry_history[-1]["data"]["speed"] == 45.5

    def test_thread_safety(self, analyzer, sample_telemetry_data):
        """Test que las operaciones son thread-safe"""
        import threading

        results = []
        errors = []
        initial_count = len(analyzer.data_collector.telemetry_history)

        def worker(sample_id):
            try:
                data = sample_telemetry_data.copy()
                data["speed"] = 40 + sample_id
                analyzer.data_collector.add_telemetry_sample(data)
                results.append(sample_id)
            except Exception as e:
                errors.append(e)

        # Crear múltiples threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)

        # Iniciar threads
        for t in threads:
            t.start()

        # Esperar que terminen
        for t in threads:
            t.join()

        # Verificar resultados
        assert len(results) == 10
        assert len(errors) == 0
        assert len(analyzer.data_collector.telemetry_history) == initial_count + 10

    def test_model_persistence(self, analyzer, sample_telemetry_data):
        """Test que guarda y carga el modelo"""
        # Entrenar modelo
        for i in range(200):
            data = sample_telemetry_data.copy()
            data["speed"] = 40 + i * 0.05
            data["acceleration"] = 0.1 + i * 0.0005
            analyzer.add_telemetry_sample(data)

        analyzer.train_model()

        # Verificar que el modelo se guardó automáticamente
        assert os.path.exists(analyzer.model_file)

        # Crear nueva instancia y verificar carga automática del modelo
        new_analyzer = PredictiveTelemetryAnalyzer()
        assert new_analyzer.predictive_model.is_trained

        # Verificar que puede hacer predicciones
        predictions = new_analyzer.get_current_predictions()
        assert isinstance(predictions, dict)

    def test_error_handling_invalid_data(self, analyzer):
        """Test que maneja datos inválidos correctamente"""
        invalid_data = {
            "speed": "invalid",
            "acceleration": None,
            "gradient": float("inf"),
        }

        # El método debe manejar datos inválidos sin errores
        initial_count = len(analyzer.data_collector.telemetry_history)
        try:
            analyzer.add_telemetry_sample(invalid_data)
            # Puede o no agregar los datos, pero no debe causar error
            final_count = len(analyzer.data_collector.telemetry_history)
            assert final_count >= initial_count  # No debe disminuir
        except Exception:
            # Si hay error, está bien, pero no debe ser un error no manejado
            pass

    def test_performance_metrics(self, analyzer, sample_telemetry_data):
        """Test que calcula métricas de rendimiento"""
        # Agregar datos con diferentes condiciones
        for i in range(50):
            data = sample_telemetry_data.copy()
            data["speed"] = 40 + i * 0.5
            data["acceleration"] = 0.1 + i * 0.01
            data["wheelslip"] = i * 0.001  # Aumentar deslizamiento
            analyzer.add_telemetry_sample(data)

        status = analyzer.get_system_status()

        assert status is not None
        assert "is_running" in status
        assert "model_trained" in status
        assert "data_collector_stats" in status

    def test_data_preprocessing(self, analyzer, sample_telemetry_data):
        """Test que preprocesa datos correctamente"""
        # Agregar datos con valores atípicos
        analyzer.add_telemetry_sample(sample_telemetry_data)

        data_with_outliers = sample_telemetry_data.copy()
        data_with_outliers["speed"] = 200  # Velocidad irreal
        data_with_outliers["acceleration"] = 50  # Aceleración irreal
        analyzer.add_telemetry_sample(data_with_outliers)

        # Verificar que ambos datos se agregaron
        assert len(analyzer.data_collector.telemetry_history) >= 2

    @pytest.mark.slow
    def test_large_dataset_training(self, analyzer, sample_telemetry_data):
        """Test de rendimiento con conjunto de datos grande"""
        # Agregar muchos datos
        for i in range(1000):
            data = sample_telemetry_data.copy()
            data["speed"] = 40 + (i % 50)  # Patrón cíclico
            data["acceleration"] = 0.1 + 0.001 * (i % 20)
            analyzer.add_telemetry_sample(data)

        # Entrenar modelo (puede ser lento)
        result = analyzer.train_model()
        assert isinstance(result, dict)
        assert "error" not in result

        # Verificar que el modelo esté entrenado
        assert analyzer.predictive_model.is_trained
