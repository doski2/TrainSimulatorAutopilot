#!/usr/bin/env python3
"""
predictive_telemetry_analysis.py
Sistema de análisis predictivo de telemetría usando machine learning
para anticipar el comportamiento del tren en Train Simulator Classic
"""

import json
import os
import sys
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tsc_integration import TSCIntegration


class TelemetryDataCollector:
    """Recopila y almacena datos históricos de telemetría para análisis predictivo."""

    def __init__(self, max_samples: int = 10000, data_file: str = "data/telemetry_history.json"):
        self.max_samples = max_samples
        self.data_file = data_file
        self.telemetry_history = deque(maxlen=max_samples)
        self.lock = threading.Lock()

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(data_file), exist_ok=True)

        # Cargar datos históricos si existen
        self._load_historical_data()

    def _load_historical_data(self):
        """Carga datos históricos desde archivo."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, encoding="utf-8-sig") as f:
                    data = json.load(f)
                    # Convertir a deque manteniendo el límite
                    for entry in data[-self.max_samples :]:
                        self.telemetry_history.append(entry)
                print(f"✅ Cargados {len(self.telemetry_history)} muestras históricas")
        except json.JSONDecodeError as e:
            print(f"⚠️  Archivo de datos históricos corrupto ({self.data_file}): {e}")
            print("   Creando archivo nuevo con datos vacíos...")
            # Crear archivo vacío válido
            self._save_historical_data()
        except Exception as e:
            print(f"⚠️  Error cargando datos históricos: {e}")
            print("   Continuando sin datos históricos...")

    def _save_historical_data(self):
        """Guarda datos históricos en archivo."""
        try:
            with self.lock:
                data_to_save = list(self.telemetry_history)
            with open(self.data_file, "w", encoding="utf-8-sig") as f:
                json.dump(data_to_save, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error guardando datos históricos: {e}")

    def add_telemetry_sample(self, telemetry_data: Dict[str, Any]):
        """Agrega una nueva muestra de telemetría al historial."""
        sample = {"timestamp": datetime.now().isoformat(), "data": telemetry_data}

        with self.lock:
            self.telemetry_history.append(sample)

        # Guardar periódicamente (cada 100 muestras)
        if len(self.telemetry_history) % 100 == 0:
            threading.Thread(target=self._save_historical_data, daemon=True).start()

    def get_recent_samples(self, n_samples: int = 100) -> List[Dict]:
        """Obtiene las n muestras más recientes."""
        with self.lock:
            return list(self.telemetry_history)[-n_samples:]

    def get_training_data(self, lookback_steps: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara datos para entrenamiento de modelos predictivos."""
        if len(self.telemetry_history) < lookback_steps + 1:
            return np.array([]), np.array([])

        samples = []
        targets = []

        with self.lock:
            history_list = list(self.telemetry_history)

        for i in range(len(history_list) - lookback_steps):
            # Crear secuencia de entrada (últimos lookback_steps)
            sequence = []
            for j in range(lookback_steps):
                data = history_list[i + j]["data"]
                features = self._extract_features(data)
                sequence.extend(features)

            # Target: valores en el siguiente paso
            target_data = history_list[i + lookback_steps]["data"]
            target_features = self._extract_features(target_data)

            samples.append(sequence)
            targets.append(target_features)

        return np.array(samples), np.array(targets)

    def _extract_features(self, telemetry_data: Dict[str, Any]) -> List[float]:
        """Extrae características relevantes de los datos de telemetría."""
        features = []

        # Características principales
        features.append(telemetry_data.get("velocidad_actual", 0))
        features.append(telemetry_data.get("acelerador", 0))
        features.append(telemetry_data.get("freno_tren", 0))
        features.append(telemetry_data.get("freno_motor", 0))
        features.append(telemetry_data.get("pendiente", 0))
        features.append(telemetry_data.get("limite_velocidad", 160))
        features.append(telemetry_data.get("radio_curva", 1000))

        # Señales y aspectos
        features.append(telemetry_data.get("senal_principal", 0))
        features.append(telemetry_data.get("senal_avanzada", 0))

        return features

    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del conjunto de datos."""
        with self.lock:
            total_samples = len(self.telemetry_history)

        if total_samples == 0:
            return {"total_samples": 0}

        return {
            "total_samples": total_samples,
            "max_samples": self.max_samples,
            "data_file": self.data_file,
        }


class PredictiveModel:
    """Modelo predictivo para telemetría usando machine learning."""

    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            "velocidad_actual",
            "acelerador",
            "freno_tren",
            "freno_motor",
            "pendiente",
            "limite_velocidad",
            "radio_curva",
            "senal_principal",
            "senal_avanzada",
        ]
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Entrena el modelo con datos históricos."""
        if len(X) == 0 or len(y) == 0:
            return {"error": "No hay suficientes datos para entrenar"}

        # Dividir datos en entrenamiento y validación
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Escalar características
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Crear modelo
        if self.model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        else:
            return {"error": f"Tipo de modelo no soportado: {self.model_type}"}

        # Entrenar modelo
        self.model.fit(X_train_scaled, y_train)

        # Evaluar modelo
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        self.is_trained = True

        return {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "samples_train": len(X_train),
            "samples_test": len(X_test),
        }

    def predict(self, current_sequence: np.ndarray) -> Optional[np.ndarray]:
        """Realiza predicción para la próxima muestra."""
        if not self.is_trained or self.model is None:
            return None

        # Escalar secuencia de entrada
        sequence_scaled = self.scaler.transform(current_sequence.reshape(1, -1))

        # Realizar predicción
        prediction = self.model.predict(sequence_scaled)

        return prediction[0]

    def save_model(self, filepath: str):
        """Guarda el modelo entrenado."""
        if not self.is_trained:
            return False

        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "model_type": self.model_type,
            "is_trained": self.is_trained,
        }

        try:
            joblib.dump(model_data, filepath)
            return True
        except Exception as e:
            print(f"❌ Error guardando modelo: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Carga un modelo entrenado."""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.feature_names = model_data["feature_names"]
            self.model_type = model_data["model_type"]
            self.is_trained = model_data["is_trained"]
            return True
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False


class PredictiveTelemetryAnalyzer:
    """Sistema completo de análisis predictivo de telemetría."""

    def __init__(self, lookback_steps: int = 10, prediction_horizon: int = 5):
        self.lookback_steps = lookback_steps
        self.prediction_horizon = prediction_horizon

        # Componentes del sistema
        self.data_collector = TelemetryDataCollector()
        self.predictive_model = PredictiveModel()

        # Estado del sistema
        self.is_running = False
        self.prediction_thread = None
        self.last_predictions: Dict[str, Any] = {}

        # Configuración de modelos
        self.model_file = "data/predictive_model.pkl"
        self.min_samples_for_training = 1000

        # Cargar modelo si existe
        self._load_existing_model()

    def _load_existing_model(self):
        """Carga modelo existente si está disponible."""
        if os.path.exists(self.model_file):
            if self.predictive_model.load_model(self.model_file):
                print("✅ Modelo predictivo cargado exitosamente")
            else:
                print("⚠️  No se pudo cargar el modelo existente")

    def start_analysis(self) -> bool:
        """Inicia el análisis predictivo."""
        if self.is_running:
            return False

        self.is_running = True
        self.prediction_thread = threading.Thread(target=self._prediction_loop, daemon=True)
        self.prediction_thread.start()

        print("🚀 Análisis predictivo iniciado")
        return True

    def stop_analysis(self):
        """Detiene el análisis predictivo."""
        self.is_running = False
        if self.prediction_thread:
            self.prediction_thread.join(timeout=2.0)
        print("[STOP] Análisis predictivo detenido")

    def _prediction_loop(self):
        """Bucle principal de predicciones."""
        while self.is_running:
            try:
                # Verificar si hay suficientes datos para predicción
                recent_samples = self.data_collector.get_recent_samples(self.lookback_steps)

                if len(recent_samples) >= self.lookback_steps:
                    # Preparar secuencia para predicción
                    sequence = []
                    for sample in recent_samples:
                        features = self.data_collector._extract_features(sample["data"])
                        sequence.extend(features)

                    sequence_array = np.array(sequence)

                    # Realizar predicción
                    prediction = self.predictive_model.predict(sequence_array)

                    if prediction is not None:
                        # Convertir predicción a diccionario
                        self.last_predictions = self._prediction_to_dict(prediction)
                        self.last_predictions["timestamp"] = datetime.now().isoformat()

                # Verificar si es necesario reentrenar el modelo
                if len(self.data_collector.telemetry_history) >= self.min_samples_for_training:
                    self._retrain_model_if_needed()

            except Exception as e:
                print(f"❌ Error en bucle de predicción: {e}")

            time.sleep(0.1)  # 10 Hz

    def _prediction_to_dict(self, prediction: np.ndarray) -> Dict[str, float]:
        """Convierte array de predicción a diccionario."""
        return dict(zip(self.predictive_model.feature_names, prediction))

    def _retrain_model_if_needed(self):
        """Reentrena el modelo si es necesario."""
        # Reentrenar cada 5000 muestras nuevas
        if len(self.data_collector.telemetry_history) % 5000 == 0:
            print("🔄 Reentrenando modelo predictivo...")
            self.train_model()

    def train_model(self) -> Dict[str, Any]:
        """Entrena el modelo con datos disponibles."""
        X, y = self.data_collector.get_training_data(self.lookback_steps)

        if len(X) == 0:
            return {"error": "No hay suficientes datos para entrenar"}

        print(f"🏋️  Entrenando modelo con {len(X)} muestras...")

        metrics = self.predictive_model.train(X, y)

        if "error" not in metrics:
            # Guardar modelo entrenado
            self.predictive_model.save_model(self.model_file)
            print("✅ Modelo entrenado y guardado")

        return metrics

    def add_telemetry_sample(self, telemetry_data: Dict[str, Any]):
        """Agrega nueva muestra de telemetría."""
        self.data_collector.add_telemetry_sample(telemetry_data)

    def get_current_predictions(self) -> Dict[str, Any]:
        """Obtiene las predicciones actuales."""
        return self.last_predictions.copy()

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado del sistema de análisis predictivo."""
        return {
            "is_running": self.is_running,
            "model_trained": self.predictive_model.is_trained,
            "data_collector_stats": self.data_collector.get_statistics(),
            "last_predictions": self.last_predictions,
            "lookback_steps": self.lookback_steps,
            "prediction_horizon": self.prediction_horizon,
        }


class PredictiveAutopilotController:
    """Controlador de piloto automático con capacidades predictivas."""

    def __init__(self, tsc_integration: TSCIntegration):
        self.tsc = tsc_integration
        self.predictive_analyzer = PredictiveTelemetryAnalyzer()

        # Estado del controlador
        self.is_active = False
        self.control_thread = None

        # Parámetros de control predictivo
        self.prediction_weight = 0.3  # Peso de las predicciones en las decisiones
        self.safety_margin = 0.9  # Margen de seguridad para límites

    def start_predictive_control(self) -> bool:
        """Inicia el control automático con predicciones."""
        if self.is_active:
            return False

        # Iniciar análisis predictivo
        if not self.predictive_analyzer.start_analysis():
            return False

        self.is_active = True
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()

        print("🎯 Control predictivo iniciado")
        return True

    def stop_predictive_control(self):
        """Detiene el control automático predictivo."""
        self.is_active = False
        self.predictive_analyzer.stop_analysis()

        if self.control_thread:
            self.control_thread.join(timeout=2.0)

        print("[STOP] Control predictivo detenido")

    def _control_loop(self):
        """Bucle principal de control predictivo."""
        while self.is_active:
            try:
                # Leer datos actuales
                datos_actuales = self.tsc.leer_datos_archivo()

                if datos_actuales:
                    # Agregar a análisis predictivo
                    self.predictive_analyzer.add_telemetry_sample(datos_actuales)

                    # Obtener predicciones
                    predicciones = self.predictive_analyzer.get_current_predictions()

                    # Calcular comandos usando predicciones
                    comandos = self._calculate_predictive_commands(datos_actuales, predicciones)

                    # Enviar comandos
                    if comandos:
                        self.tsc.enviar_comandos(comandos)

            except Exception as e:
                print(f"❌ Error en control predictivo: {e}")

            time.sleep(0.1)  # 10 Hz

    def _calculate_predictive_commands(
        self, current_data: Dict[str, Any], predictions: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """Calcula comandos usando datos actuales y predicciones."""
        if not predictions:
            return None

        velocidad_actual = current_data.get("velocidad_actual", 0)
        limite_velocidad = current_data.get("limite_velocidad", 160)
        pendiente = current_data.get("pendiente", 0)

        # Usar predicción de velocidad futura
        velocidad_predicha = predictions.get("velocidad_actual", velocidad_actual)

        # Lógica de control predictiva
        if velocidad_predicha > limite_velocidad * self.safety_margin:
            # Reducir velocidad si la predicción indica que excederá el límite
            acelerador = 0.0
            freno_tren = min(0.8, (velocidad_predicha - limite_velocidad * self.safety_margin) / 50)
        elif velocidad_actual < limite_velocidad * 0.8:
            # Acelerar si está por debajo del 80% del límite
            acelerador = min(0.8, 0.5 + pendiente * 0.1)  # Compensar pendiente
            freno_tren = 0.0
        else:
            # Mantener velocidad de crucero
            acelerador = 0.3
            freno_tren = 0.0

        # Ajustes por pendiente usando predicciones
        pendiente_predicha = predictions.get("pendiente", pendiente)
        if pendiente_predicha > 5:  # Subida pronunciada
            acelerador = min(acelerador + 0.2, 1.0)
        elif pendiente_predicha < -5:  # Bajada pronunciada
            freno_tren = min(freno_tren + 0.1, 0.5)

        return {
            "acelerador": acelerador,
            "freno_tren": freno_tren,
            "freno_motor": 0.0,
            "reverser": 1.0,
        }

    def get_control_status(self) -> Dict[str, Any]:
        """Obtiene el estado del controlador predictivo."""
        return {
            "is_active": self.is_active,
            "prediction_weight": self.prediction_weight,
            "safety_margin": self.safety_margin,
            "analyzer_status": self.predictive_analyzer.get_system_status(),
        }
