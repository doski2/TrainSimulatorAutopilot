# seaborn_analysis.py
# Análisis estadístico con Seaborn para datos de Train Simulator Autopilot

import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Importar integración TSC
from tsc_integration import TSCIntegration


class SeabornAnalysis:
    """Análisis estadístico de datos de telemetría usando Seaborn"""

    def __init__(self, data_file=None, use_tsc_integration=True):
        self.df = None
        self.tsc_integration = None

        # Configurar estilo de Seaborn
        sns.set_style("whitegrid")
        sns.set_palette("husl")

        # Inicializar integración TSC si se solicita
        if use_tsc_integration:
            self.tsc_integration = TSCIntegration()
            print("Integración TSC inicializada para análisis estadístico")

        # Cargar datos si se proporciona archivo
        if data_file:
            self.load_data(data_file)

    def load_data_from_tsc(self, max_records=None, collection_time=30):
        """Cargar datos directamente desde TSC recopilando múltiples lecturas"""
        if not self.tsc_integration:
            print("Integración TSC no disponible")
            return False

        try:
            print(f"Recopilando datos desde TSC durante {collection_time} segundos...")

            import time

            datos_recopilados = []
            start_time = time.time()

            while time.time() - start_time < collection_time:
                # Leer datos actuales
                datos_actuales = self.tsc_integration.leer_datos_archivo()

                if datos_actuales and isinstance(datos_actuales, dict):
                    # Agregar timestamp
                    datos_actuales["timestamp"] = time.time()
                    datos_recopilados.append(datos_actuales)
                    print(f"✓ Lectura {len(datos_recopilados)}: {len(datos_actuales)} variables")
                else:
                    print(f"⚠ Lectura fallida o datos inválidos: {type(datos_actuales)}")

                # Pequeña pausa entre lecturas
                time.sleep(0.1)  # 100ms

                # Verificar límite de registros
                if max_records and len(datos_recopilados) >= max_records:
                    break

            if not datos_recopilados:
                print("No se pudieron recopilar datos desde TSC")
                return False

            print(f"Intentando crear DataFrame con {len(datos_recopilados)} registros...")

            # Convertir a DataFrame
            try:
                self.df = pd.DataFrame(datos_recopilados)
                print(f"✅ DataFrame creado exitosamente: {self.df.shape}")
                print(f"📋 Columnas disponibles: {list(self.df.columns)}")
            except Exception as df_error:
                print(f"❌ Error creando DataFrame: {df_error}")
                print(
                    f"Primeros datos de ejemplo: {datos_recopilados[:2] if datos_recopilados else 'None'}"
                )
                return False

            # Limpiar y preparar datos
            self._clean_and_prepare_data()

            print(
                f"✅ Datos TSC recopilados: {len(self.df)} registros en {collection_time} segundos"
            )
            return True

        except Exception as e:
            print(f"❌ Error recopilando datos desde TSC: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _clean_and_prepare_data(self):
        """Limpiar y preparar datos del DataFrame"""
        if self.df is None:
            return

        # Mapeo de nombres de columnas TSC a nombres estándar
        column_mapping = {
            "CurrentSpeed": "velocidad",
            "Acceleration": "aceleracion",
            "RPM": "rpm",
            "Ammeter": "corriente",
            "AirBrakePipePressurePSI": "presion_freno",
            "LocoBrakeCylinderPressurePSI": "presion_freno_loco",
            "TrainBrakeCylinderPressurePSI": "presion_freno_tren",
            "MainReservoirPressurePSIDisplayed": "presion_deposito",
            # FuelLevel removed from mapping; not used in analysis
            "Gradient": "pendiente",
            "TractiveEffort": "esfuerzo_traccion",
            "Wheelslip": "deslizamiento_ruedas",
        }

        # Renombrar columnas según el mapeo
        self.df = self.df.rename(columns=column_mapping)

        # Convertir timestamps si existen
        if "timestamp" in self.df.columns:
            self.df["fecha_hora"] = pd.to_datetime(self.df["timestamp"], unit="s")
        elif "fecha_hora" not in self.df.columns:
            # Crear timestamps sintéticos si no existen
            self.df["fecha_hora"] = pd.date_range(
                start=datetime.now() - timedelta(seconds=len(self.df)),
                periods=len(self.df),
                freq="100ms",  # 100ms entre lecturas
            )

        # Asegurar tipos de datos numéricos
        numeric_columns = [
            "velocidad",
            "aceleracion",
            "rpm",
            "corriente",
            "presion_freno",
            "presion_freno_loco",
            "presion_freno_tren",
            "presion_deposito",
            # combustible removed from numeric columns
            "pendiente",
            "esfuerzo_traccion",
            "deslizamiento_ruedas",
        ]

        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        # Crear columna 'acelerador' basada en aceleración positiva
        if "aceleracion" in self.df.columns:
            self.df["acelerador"] = self.df["aceleracion"].clip(lower=0)

        # Crear columna 'freno' basada en aceleración negativa
        if "aceleracion" in self.df.columns:
            self.df["freno"] = (-self.df["aceleracion"]).clip(lower=0)

        # Eliminar filas con valores NaN críticos (si existe velocidad)
        if "velocidad" in self.df.columns:
            self.df = self.df.dropna(subset=["velocidad"])

        # Ordenar por tiempo
        if "fecha_hora" in self.df.columns:
            self.df = self.df.sort_values("fecha_hora")

        print(f"📊 Datos preparados: {len(self.df)} filas, {len(self.df.columns)} columnas")
        print(f"📋 Columnas finales: {list(self.df.columns)}")

    def load_data(self, file_path):
        """Cargar datos desde archivo CSV"""
        try:
            self.df = pd.read_csv(file_path)
            if "fecha_hora" in self.df.columns:
                self.df["fecha_hora"] = pd.to_datetime(self.df["fecha_hora"])
            print(f"Datos cargados: {len(self.df)} registros")
            return True
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return False

    def plot_velocity_distribution(self, save_path=None):
        """Distribución de velocidad con análisis estadístico"""
        if self.df is None or "velocidad" not in self.df.columns:
            print("Datos de velocidad no disponibles")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Análisis Estadístico de Velocidad", fontsize=16)

        # Histograma con KDE
        sns.histplot(data=self.df, x="velocidad", kde=True, ax=axes[0, 0])
        axes[0, 0].set_title("Distribución de Velocidad")
        axes[0, 0].set_xlabel("Velocidad (km/h)")
        axes[0, 0].set_ylabel("Frecuencia")

        # Box plot
        sns.boxplot(data=self.df, y="velocidad", ax=axes[0, 1])
        axes[0, 1].set_title("Box Plot de Velocidad")
        axes[0, 1].set_ylabel("Velocidad (km/h)")

        # Violin plot
        sns.violinplot(data=self.df, y="velocidad", ax=axes[1, 0])
        axes[1, 0].set_title("Violin Plot de Velocidad")
        axes[1, 0].set_ylabel("Velocidad (km/h)")

        # Estadísticas descriptivas
        stats_text = (
            ".2f"
            ".2f"
            ".2f"
            ".2f"
            f"""
        Estadísticas de Velocidad:
        Media: {self.df['velocidad'].mean():.2f} km/h
        Mediana: {self.df['velocidad'].median():.2f} km/h
        Desv. Estándar: {self.df['velocidad'].std():.2f} km/h
        Mín: {self.df['velocidad'].min():.2f} km/h
        Máx: {self.df['velocidad'].max():.2f} km/h
        """
        )

        axes[1, 1].text(
            0.1,
            0.5,
            stats_text,
            transform=axes[1, 1].transAxes,
            fontsize=10,
            verticalalignment="center",
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightblue"},
        )
        axes[1, 1].set_title("Estadísticas Descriptivas")
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].axis("off")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Gráfico guardado en: {save_path}")

        plt.show()

    def plot_correlation_matrix(self, variables=None, save_path=None):
        """Matriz de correlación entre variables"""
        if self.df is None:
            print("Datos no disponibles")
            return

        # Variables numéricas por defecto
        if variables is None:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            variables = [
                col
                for col in numeric_cols
                if col
                in [
                    "velocidad",
                    "aceleracion",
                    "rpm",
                    "corriente",
                    "presion_freno",
                    "acelerador",
                    "temperatura",
                ]
            ]

        if len(variables) < 2:
            print("Se necesitan al menos 2 variables numéricas")
            return

        # Calcular correlación
        corr_matrix = self.df[variables].corr()

        # Crear heatmap
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

        sns.heatmap(
            corr_matrix,
            mask=mask,
            annot=True,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.5},
        )

        plt.title("Matriz de Correlación - Variables de Telemetría", fontsize=14)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Matriz de correlación guardada en: {save_path}")

        plt.show()

    def plot_time_series_analysis(self, save_path=None):
        """Análisis de series temporales con tendencias"""
        if self.df is None or "fecha_hora" not in self.df.columns:
            print("Datos de tiempo no disponibles")
            return

        # Variables a analizar
        variables = ["velocidad", "aceleracion", "rpm", "presion_freno"]
        available_vars = [v for v in variables if v in self.df.columns]

        if not available_vars:
            print("No hay variables temporales disponibles")
            return

        n_vars = len(available_vars)
        fig, axes = plt.subplots(n_vars, 1, figsize=(15, 4 * n_vars), sharex=True)

        if n_vars == 1:
            axes = [axes]

        for i, var in enumerate(available_vars):
            # Serie temporal
            axes[i].plot(self.df["fecha_hora"], self.df[var], linewidth=1, alpha=0.7, label=var)

            # Tendencia (media móvil)
            if len(self.df) > 10:
                rolling_mean = self.df[var].rolling(window=min(50, len(self.df) // 10)).mean()
                axes[i].plot(
                    self.df["fecha_hora"],
                    rolling_mean,
                    linewidth=2,
                    color="red",
                    label=f"{var} (tendencia)",
                )

            axes[i].set_ylabel(self._get_variable_label(var))
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)

        axes[-1].set_xlabel("Tiempo")
        plt.suptitle("Análisis de Series Temporales - Variables de Telemetría", fontsize=14)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Análisis temporal guardado en: {save_path}")

        plt.show()

    def plot_performance_analysis(self, save_path=None):
        """Análisis de rendimiento y eficiencia"""
        if self.df is None:
            print("Datos no disponibles")
            return

        # Crear métricas de rendimiento
        if "velocidad" in self.df.columns and "rpm" in self.df.columns:
            # Eficiencia: velocidad / RPM (simplificada)
            self.df["eficiencia"] = self.df["velocidad"] / (self.df["rpm"] + 1) * 100

        if "acelerador" in self.df.columns and "freno" in self.df.columns:
            # Actividad de control
            self.df["actividad_control"] = self.df["acelerador"] + self.df["freno"]

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Análisis de Rendimiento del Sistema", fontsize=14)

        # Eficiencia
        if "eficiencia" in self.df.columns:
            sns.scatterplot(data=self.df, x="velocidad", y="eficiencia", ax=axes[0, 0], alpha=0.6)
            axes[0, 0].set_title("Eficiencia vs Velocidad")
            axes[0, 0].set_xlabel("Velocidad (km/h)")
            axes[0, 0].set_ylabel("Eficiencia (%)")

        # Actividad de control
        if "actividad_control" in self.df.columns:
            sns.histplot(data=self.df, x="actividad_control", ax=axes[0, 1], kde=True)
            axes[0, 1].set_title("Distribución de Actividad de Control")
            axes[0, 1].set_xlabel("Actividad de Control (%)")

        # Velocidad vs RPM
        if "rpm" in self.df.columns:
            sns.scatterplot(data=self.df, x="rpm", y="velocidad", ax=axes[1, 0], alpha=0.6)
            axes[1, 0].set_title("Velocidad vs RPM")
            axes[1, 0].set_xlabel("RPM")
            axes[1, 0].set_ylabel("Velocidad (km/h)")

        # Análisis de consumo energético (velocidad vs corriente)
        if "velocidad" in self.df.columns and "corriente" in self.df.columns:
            # Calcular eficiencia energética aproximada
            eficiencia_energetica = self.df["velocidad"] / (
                self.df["corriente"] + 1
            )  # +1 para evitar división por cero

            # Scatter plot con densidad
            sns.scatterplot(
                data=self.df,
                x="velocidad",
                y="corriente",
                hue=eficiencia_energetica,
                palette="viridis",
                ax=axes[1, 1],
            )
            axes[1, 1].set_title("Eficiencia Energética (Velocidad vs Corriente)")
            axes[1, 1].set_xlabel("Velocidad (km/h)")
            axes[1, 1].set_ylabel("Corriente (A)")
            axes[1, 1].legend(title="Eficiencia", bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Análisis de rendimiento guardado en: {save_path}")

        plt.show()

    def _get_variable_label(self, var):
        """Obtener etiqueta descriptiva para variable"""
        labels = {
            "velocidad": "Velocidad (km/h)",
            "aceleracion": "Aceleración (m/s²)",
            "rpm": "RPM",
            "presion_freno": "Presión de Freno (PSI)",
            "acelerador": "Acelerador (%)",
            "corriente": "Corriente (A)",
            "temperatura": "Temperatura (°C)",
        }
        return labels.get(var, var.title())

    def analyze_velocity_trends(self, save_path=None):
        """Análisis avanzado de tendencias de velocidad"""
        if self.df is None or "velocidad" not in self.df.columns:
            print("Datos de velocidad no disponibles")
            return

        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle("Análisis Avanzado de Tendencias de Velocidad", fontsize=16)

        # 1. Serie temporal con tendencias
        axes[0, 0].plot(
            self.df["fecha_hora"], self.df["velocidad"], linewidth=1, alpha=0.7, label="Velocidad"
        )
        if len(self.df) > 20:
            rolling_mean = self.df["velocidad"].rolling(window=min(100, len(self.df) // 5)).mean()
            axes[0, 0].plot(
                self.df["fecha_hora"],
                rolling_mean,
                linewidth=3,
                color="red",
                label="Tendencia (media móvil)",
            )
        axes[0, 0].set_title("Serie Temporal de Velocidad")
        axes[0, 0].set_ylabel("Velocidad (km/h)")
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Análisis de aceleración/deceleración
        if "aceleracion" in self.df.columns:
            # Calcular cambios de velocidad
            vel_changes = self.df["velocidad"].diff().astype(float)
            accelerating = vel_changes > 1  # Acelerando
            decelerating = vel_changes < -1  # Desacelerando
            stable = abs(vel_changes) <= 1  # Estable

            axes[0, 1].scatter(
                self.df["fecha_hora"][accelerating],
                self.df["velocidad"][accelerating],
                color="green",
                alpha=0.6,
                s=20,
                label="Acelerando",
            )
            axes[0, 1].scatter(
                self.df["fecha_hora"][decelerating],
                self.df["velocidad"][decelerating],
                color="red",
                alpha=0.6,
                s=20,
                label="Desacelerando",
            )
            axes[0, 1].scatter(
                self.df["fecha_hora"][stable],
                self.df["velocidad"][stable],
                color="blue",
                alpha=0.6,
                s=20,
                label="Estable",
            )
            axes[0, 1].set_title("Patrones de Aceleración/Desaceleración")
            axes[0, 1].set_ylabel("Velocidad (km/h)")
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)

        # 3. Distribución por rangos de velocidad
        vel_ranges = pd.cut(
            self.df["velocidad"],
            bins=[0, 20, 40, 60, 80, 100, 200],
            labels=["0-20", "20-40", "40-60", "60-80", "80-100", "100+"],
        )
        vel_counts = vel_ranges.value_counts().sort_index()

        vel_counts.plot(kind="bar", ax=axes[1, 0], color="skyblue")
        axes[1, 0].set_title("Distribución por Rangos de Velocidad")
        axes[1, 0].set_xlabel("Rango de Velocidad (km/h)")
        axes[1, 0].set_ylabel("Frecuencia")
        axes[1, 0].tick_params(axis="x", rotation=45)

        # 4. Análisis de estabilidad
        if len(self.df) > 10:
            # Calcular variabilidad de velocidad
            rolling_std = self.df["velocidad"].rolling(window=min(50, len(self.df) // 10)).std()
            axes[1, 1].plot(self.df["fecha_hora"], rolling_std, color="orange", linewidth=2)
            axes[1, 1].set_title("Estabilidad de Velocidad (Desv. Estándar)")
            axes[1, 1].set_ylabel("Desv. Estándar (km/h)")
            axes[1, 1].grid(True, alpha=0.3)

        # 5. Eficiencia energética (si hay datos de corriente)
        if "corriente" in self.df.columns and "velocidad" in self.df.columns:
            # Calcular eficiencia aproximada (velocidad / corriente)
            efficiency = self.df["velocidad"] / (
                self.df["corriente"] + 1
            )  # +1 para evitar división por cero
            axes[2, 0].scatter(self.df["velocidad"], efficiency, alpha=0.6, color="purple")
            axes[2, 0].set_title("Eficiencia Energética")
            axes[2, 0].set_xlabel("Velocidad (km/h)")
            axes[2, 0].set_ylabel("Eficiencia (km/h/A)")
            axes[2, 0].grid(True, alpha=0.3)

        # 6. Estadísticas resumen
        stats_text = (
            ".2f"
            ".2f"
            ".2f"
            ".2f"
            ".2f"
            ".2f"
            f"""
        Estadísticas de Velocidad:
        Media: {self.df['velocidad'].mean():.2f} km/h
        Mediana: {self.df['velocidad'].median():.2f} km/h
        Desv. Estándar: {self.df['velocidad'].std():.2f} km/h
        Máx: {self.df['velocidad'].max():.2f} km/h
        Mín: {self.df['velocidad'].min():.2f} km/h
        CV: {(self.df['velocidad'].std() / self.df['velocidad'].mean() * 100):.2f}%

        Tendencias:
        • {len(self.df[self.df['velocidad'] > 80])} registros > 80 km/h
        • {len(self.df[self.df['velocidad'] < 20])} registros < 20 km/h
        • {(self.df['velocidad'].diff().astype(float) > 2).sum()} aceleraciones bruscas
        """
        )

        axes[2, 1].text(
            0.05,
            0.95,
            stats_text,
            transform=axes[2, 1].transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightyellow"},
        )
        axes[2, 1].set_title("Estadísticas y Métricas")
        axes[2, 1].set_xlim(0, 1)
        axes[2, 1].set_ylim(0, 1)
        axes[2, 1].axis("off")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Análisis de tendencias de velocidad guardado en: {save_path}")

        plt.show()

    def detect_anomalies(self, threshold=2.0, save_path=None):
        """Detección de anomalías usando métodos estadísticos"""
        if self.df is None:
            print("Datos no disponibles")
            return

        # Variables a analizar
        variables = ["velocidad", "aceleracion", "rpm", "corriente", "presion_freno"]
        available_vars = [v for v in variables if v in self.df.columns]

        if not available_vars:
            print("No hay variables disponibles para análisis de anomalías")
            return

        # Crear figura
        n_vars = len(available_vars)
        fig, axes = plt.subplots(n_vars, 1, figsize=(15, 4 * n_vars), sharex=True)
        if n_vars == 1:
            axes = [axes]

        anomalies_summary = {}

        for i, var in enumerate(available_vars):
            # Verificar si hay variabilidad en los datos
            data_clean = self.df[var].dropna()
            if len(data_clean) < 3 or data_clean.std() == 0:
                # Datos constantes o insuficientes - no hay anomalías
                z_scores = pd.Series([0] * len(data_clean), index=data_clean.index)
                anomalies = pd.Series([False] * len(data_clean), index=data_clean.index)
                max_zscore = 0.0
            else:
                # Calcular z-score manualmente para evitar problemas de tipo
                data_array = np.asarray(data_clean, dtype=float)
                mean_val = np.mean(data_array)
                std_val = np.std(data_array, ddof=1)  # ddof=1 para sample standard deviation
                if std_val > 0:
                    z_scores = np.abs((data_array - mean_val) / std_val)
                else:
                    z_scores = np.zeros_like(data_array)
                anomalies = z_scores > threshold
                max_zscore = float(np.max(z_scores)) if len(z_scores) > 0 else 0.0

            # Graficar
            axes[i].plot(
                self.df["fecha_hora"], self.df[var], linewidth=1, alpha=0.7, label=var, color="blue"
            )

            # Marcar anomalías
            if anomalies.any():
                anomaly_times = self.df["fecha_hora"][anomalies]
                anomaly_values = self.df[var][anomalies]
                axes[i].scatter(
                    anomaly_times,
                    anomaly_values,
                    color="red",
                    s=50,
                    alpha=0.8,
                    label="Anomalías",
                    edgecolors="darkred",
                    linewidth=1,
                )

            # Líneas de umbral
            mean_val = self.df[var].mean()
            std_val = self.df[var].std()
            axes[i].axhline(
                y=mean_val, color="green", linestyle="--", alpha=0.7, label=f"Media: {mean_val:.2f}"
            )
            axes[i].axhline(
                y=mean_val + threshold * std_val,
                color="red",
                linestyle=":",
                alpha=0.7,
                label=f"+{threshold}σ",
            )
            axes[i].axhline(
                y=mean_val - threshold * std_val,
                color="red",
                linestyle=":",
                alpha=0.7,
                label=f"-{threshold}σ",
            )

            axes[i].set_ylabel(self._get_variable_label(var))
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
            axes[i].set_title(f"Detección de Anomalías - {var.title()} (Z-score > {threshold})")

            # Contar anomalías
            n_anomalies = anomalies.sum()
            anomalies_summary[var] = {
                "count": n_anomalies,
                "percentage": (n_anomalies / len(data_clean) * 100) if len(data_clean) > 0 else 0,
                "max_zscore": max_zscore,
            }

        axes[-1].set_xlabel("Tiempo")
        plt.suptitle(f"Análisis de Anomalías (Z-score threshold: {threshold})", fontsize=14)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Análisis de anomalías guardado en: {save_path}")

        # Mostrar resumen de anomalías
        print("\n" + "=" * 50)
        print("RESUMEN DE ANOMALÍAS DETECTADAS")
        print("=" * 50)
        for var, var_stats in anomalies_summary.items():
            print(
                f"{var.title()}: {var_stats['count']} anomalías "
                f"({var_stats['percentage']:.1f}%) - Z-score máx: {var_stats['max_zscore']:.2f}"
            )

        plt.show()

        return anomalies_summary

    def generate_complete_report(self, output_dir="reports"):
        """Generar reporte completo de análisis"""
        import os

        os.makedirs(output_dir, exist_ok=True)

        print("Generando reporte completo de análisis estadístico...")

        # Análisis de distribución
        self.plot_velocity_distribution(f"{output_dir}/distribucion_velocidad.png")

        # Matriz de correlación
        self.plot_correlation_matrix(save_path=f"{output_dir}/matriz_correlacion.png")

        # Análisis temporal
        self.plot_time_series_analysis(f"{output_dir}/analisis_temporal.png")

        # Análisis de rendimiento
        self.plot_performance_analysis(f"{output_dir}/analisis_rendimiento.png")

        # NUEVO: Análisis de tendencias de velocidad
        self.analyze_velocity_trends(f"{output_dir}/tendencias_velocidad.png")

        # NUEVO: Detección de anomalías
        anomalies = self.detect_anomalies(save_path=f"{output_dir}/deteccion_anomalias.png")

        # Generar resumen en texto
        self._generate_text_summary(output_dir, anomalies)

        print(f"Reporte completo generado en: {output_dir}/")

    def _generate_text_summary(self, output_dir, anomalies=None):
        """Generar resumen textual del análisis"""
        summary_file = f"{output_dir}/resumen_analisis.txt"

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("ANÁLISIS ESTADÍSTICO - TRAIN SIMULATOR AUTOPILOT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Registros analizados: {len(self.df) if self.df is not None else 0}\n\n")

            if self.df is not None and "velocidad" in self.df.columns:
                f.write("ESTADÍSTICAS DE VELOCIDAD:\n")
                f.write("-" * 30 + "\n")
                vel_stats = self.df["velocidad"].describe()
                f.write(f"Media: {vel_stats['mean']:.2f} km/h\n")
                f.write(f"Mediana: {vel_stats['50%']:.2f} km/h\n")
                f.write(f"Desv. Estándar: {vel_stats['std']:.2f} km/h\n")
                f.write(f"Mínimo: {vel_stats['min']:.2f} km/h\n")
                f.write(f"Máximo: {vel_stats['max']:.2f} km/h\n")
                f.write(
                    f"Coeficiente de variación: {(vel_stats['std']/vel_stats['mean']*100):.2f}%\n\n"
                )

                # Análisis de rangos
                vel_ranges = pd.cut(
                    self.df["velocidad"],
                    bins=[0, 20, 40, 60, 80, 100, 200],
                    labels=["0-20", "20-40", "40-60", "60-80", "80-100", "100+"],
                )
                range_counts = vel_ranges.value_counts().sort_index()
                f.write("DISTRIBUCIÓN POR RANGOS DE VELOCIDAD:\n")
                for range_name, count in range_counts.items():
                    percentage = count / len(self.df) * 100
                    f.write(f"  {range_name} km/h: {count} registros ({percentage:.1f}%)\n")
                f.write("\n")

            if anomalies:
                f.write("ANOMALÍAS DETECTADAS:\n")
                f.write("-" * 20 + "\n")
                for var, stats in anomalies.items():
                    f.write(
                        f"{var.title()}: {stats['count']} anomalías "
                        f"({stats['percentage']:.1f}%) - Z-score máx: {stats['max_zscore']:.2f}\n"
                    )
                f.write("\n")

            f.write("ARCHIVOS GENERADOS:\n")
            f.write("-" * 18 + "\n")
            f.write("• distribucion_velocidad.png - Análisis estadístico de velocidad\n")
            f.write("• matriz_correlacion.png - Correlaciones entre variables\n")
            f.write("• analisis_temporal.png - Series temporales con tendencias\n")
            f.write("• analisis_rendimiento.png - Métricas de rendimiento\n")
            f.write("• tendencias_velocidad.png - Análisis avanzado de tendencias\n")
            f.write("• deteccion_anomalias.png - Anomalías detectadas\n")
            f.write("• resumen_analisis.txt - Este archivo resumen\n")

        print(f"Resumen textual guardado en: {summary_file}")

    def generate_automatic_report(self, output_dir="reports_automaticos", interval_hours=24):
        """Generar reportes automáticos basados en intervalo de tiempo"""
        if self.df is None:
            print("No hay datos disponibles para reporte automático")
            return False

        # Crear directorio con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = f"{output_dir}/reporte_{timestamp}"
        os.makedirs(report_dir, exist_ok=True)

        print(f"Generando reporte automático: {timestamp}")

        # Filtrar datos del último intervalo (o usar todos si no hay datos recientes)
        if "fecha_hora" in self.df.columns:
            cutoff_time = datetime.now() - timedelta(hours=interval_hours)
            recent_data = self.df[self.df["fecha_hora"] > cutoff_time]

            if len(recent_data) == 0:
                print(
                    f"No hay datos en las últimas {interval_hours} horas, usando todos los datos disponibles"
                )
                recent_data = self.df.copy()
            else:
                print(
                    f"Analizando {len(recent_data)} registros de las últimas {interval_hours} horas"
                )

            # Usar solo datos recientes para el análisis
            original_df = self.df
            self.df = recent_data

        try:
            # Generar análisis completo
            self.generate_complete_report(report_dir)

            # Agregar información específica del reporte automático
            with open(f"{report_dir}/info_reporte.txt", "w", encoding="utf-8") as f:
                f.write(f"REPORTE AUTOMÁTICO - {timestamp}\n")
                f.write(f"Intervalo analizado: Últimas {interval_hours} horas\n")
                f.write(f"Registros analizados: {len(self.df)}\n")
                f.write(f"Periodo: {self.df['fecha_hora'].min()} - {self.df['fecha_hora'].max()}\n")

            print(f"Reporte automático completado: {report_dir}")
            return True

        finally:
            # Restaurar datos originales
            if "original_df" in locals():
                self.df = original_df

        return False


# Ejemplo de uso
if __name__ == "__main__":
    print("Iniciando análisis estadístico con integración TSC...")

    # Crear analizador con integración TSC
    analyzer = SeabornAnalysis(use_tsc_integration=True)

    # Intentar cargar datos reales de TSC (10 segundos de recopilación para pruebas)
    if analyzer.load_data_from_tsc(max_records=100, collection_time=10):
        print("✅ Datos TSC recopilados exitosamente")
        if analyzer.df is not None:
            print(f"📊 Registros disponibles: {len(analyzer.df)}")

            # Mostrar columnas disponibles
            print(f"📋 Columnas disponibles: {list(analyzer.df.columns)}")

            # Generar análisis completo con datos reales
            analyzer.generate_complete_report("reports_tsc")

            # Generar reporte automático de las últimas horas
            analyzer.generate_automatic_report("reports_automaticos", interval_hours=1)
        else:
            print("❌ Error: DataFrame es None después de cargar datos TSC")
    else:
        print("⚠️ No se pudieron recopilar datos TSC, usando datos de ejemplo...")

        # Generar datos de ejemplo para demostración
        np.random.seed(42)
        n_samples = 1000

        example_data = {
            "timestamp": np.arange(n_samples) * 0.1,  # timestamps simulados
            "velocidad": np.random.normal(75, 15, n_samples).clip(0, 150),
            "aceleracion": np.random.normal(0, 0.8, n_samples),
            "rpm": np.random.normal(800, 150, n_samples).clip(0),
            "presion_freno": np.random.uniform(0, 120, n_samples),
            "acelerador": np.random.uniform(0, 100, n_samples),
            "corriente": np.random.normal(450, 80, n_samples).clip(0),
            "freno": np.random.uniform(0, 100, n_samples),
        }

        analyzer.df = pd.DataFrame(example_data)
        analyzer._clean_and_prepare_data()

        # Generar análisis con datos de ejemplo
        analyzer.generate_complete_report("reports_ejemplo")
