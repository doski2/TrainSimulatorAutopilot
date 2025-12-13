# bokeh_dashboard.py
# Dashboard interactivo con Bokeh para Train Simulator Autopilot

from datetime import datetime

import numpy as np
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, Div, Select, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server

# Importar integración con TSC
from tsc_integration import TSCIntegration


class BokehDashboard:
    """Dashboard interactivo con Bokeh para visualización en tiempo real"""

    def __init__(self):
        self.source = ColumnDataSource(
            data={
                "time": [],
                "velocity": [],
                "acceleration": [],
                "brake_pressure": [],
                "throttle": [],
                "rpm": [],
                "current": [],
            }
        )

        # Inicializar integración TSC
        self.tsc_integration = TSCIntegration()

        # Ranges compartidos para zoom/pan sincronizado
        from bokeh.models import DataRange1d

        self.shared_x_range = DataRange1d()
        self.shared_y_velocity = DataRange1d()
        self.shared_y_acceleration = DataRange1d()
        self.shared_y_brake = DataRange1d()
        self.shared_y_throttle = DataRange1d()

        # Crear figuras con ranges compartidos
        self.p_velocity = self.create_velocity_plot()
        self.p_acceleration = self.create_acceleration_plot()
        self.p_brake = self.create_brake_plot()
        self.p_throttle = self.create_throttle_plot()

        # Controles básicos
        self.slider_window = Slider(
            title="Ventana de tiempo (minutos)", value=5, start=1, end=60, step=1
        )
        self.button_clear = Button(label="Limpiar Datos", button_type="warning")

        # Controles avanzados - FASE 3
        self.button_play = Button(label="▶️ Play", button_type="success")
        self.button_pause = Button(label="⏸️ Pause", button_type="warning", disabled=True)
        self.button_reset = Button(label="🔄 Reset", button_type="danger")

        # Controles de theme
        self.theme_select = Select(
            title="Tema:", value="default", options=["default", "dark", "tsc", "minimal"]
        )
        self.export_button = Button(label="📊 Exportar Gráficos", button_type="primary")

        # Estado de reproducción
        self.is_playing = True
        self.update_callback = None

        # Layout mejorado
        basic_controls = column(self.slider_window, self.button_clear)
        playback_controls = column(
            Div(text="<b>Controles de Reproducción:</b>"),
            row(self.button_play, self.button_pause, self.button_reset),
        )
        theme_controls = column(
            Div(text="<b>Apariencia:</b>"), self.theme_select, self.export_button
        )

        controls = column(basic_controls, playback_controls, theme_controls)
        plots = column(self.p_velocity, self.p_acceleration, self.p_brake, self.p_throttle)
        self.layout = row(controls, plots)

        # Callbacks
        self.slider_window.on_change("value", self.update_window)
        self.button_clear.on_click(self.clear_data)

        # Callbacks avanzados - FASE 3
        self.button_play.on_click(self.play_data)
        self.button_pause.on_click(self.pause_data)
        self.button_reset.on_click(self.reset_data)
        self.theme_select.on_change("value", self.change_theme)
        self.export_button.on_click(self.export_charts)

    def create_velocity_plot(self):
        """Crear gráfico de velocidad"""
        p = figure(
            title="Velocidad del Tren (km/h)",
            x_axis_type="datetime",
            x_range=self.shared_x_range,
            y_range=self.shared_y_velocity,
            width=800,
            height=300,
        )

        p.line(
            "time",
            "velocity",
            source=self.source,
            line_width=2,
            color="blue",
            legend_label="Velocidad",
        )

        p.xaxis.axis_label = "Tiempo"
        p.yaxis.axis_label = "Velocidad (km/h)"
        p.legend.location = "top_left"

        return p

    def create_acceleration_plot(self):
        """Crear gráfico de aceleración"""
        p = figure(
            title="Aceleración (m/s²)",
            x_axis_type="datetime",
            x_range=self.shared_x_range,
            y_range=self.shared_y_acceleration,
            width=800,
            height=300,
        )

        p.line(
            "time",
            "acceleration",
            source=self.source,
            line_width=2,
            color="green",
            legend_label="Aceleración",
        )

        p.xaxis.axis_label = "Tiempo"
        p.yaxis.axis_label = "Aceleración (m/s²)"

        return p

    def create_brake_plot(self):
        """Crear gráfico de presión de freno"""
        p = figure(
            title="Presión de Freno (PSI)",
            x_axis_type="datetime",
            x_range=self.shared_x_range,
            y_range=self.shared_y_brake,
            width=800,
            height=300,
        )

        p.line(
            "time",
            "brake_pressure",
            source=self.source,
            line_width=2,
            color="red",
            legend_label="Presión de Freno",
        )

        p.xaxis.axis_label = "Tiempo"
        p.yaxis.axis_label = "Presión (PSI)"

        return p

    def create_throttle_plot(self):
        """Crear gráfico de acelerador y RPM"""
        from bokeh.models import LinearAxis, Range1d

        p = figure(
            title="Acelerador y RPM",
            x_axis_type="datetime",
            x_range=self.shared_x_range,
            y_range=self.shared_y_throttle,
            width=800,
            height=300,
        )

        # Configurar eje Y derecho para RPM
        p.extra_y_ranges = {"rpm": Range1d(start=0, end=2000)}
        p.add_layout(LinearAxis(y_range_name="rpm", axis_label="RPM"), "right")

        p.line(
            "time",
            "throttle",
            source=self.source,
            line_width=2,
            color="orange",
            legend_label="Acelerador",
        )
        p.line(
            "time",
            "rpm",
            source=self.source,
            line_width=2,
            color="purple",
            legend_label="RPM",
            y_range_name="rpm",
        )

        p.xaxis.axis_label = "Tiempo"
        p.yaxis.axis_label = "Acelerador (%)"

        return p

    def update_data(self, telemetry_data=None):
        """Actualizar datos en tiempo real"""
        # Solo actualizar si está en modo play
        if not self.is_playing:
            return

        current_time = datetime.now()

        if telemetry_data is None:
            # Intentar leer datos reales de TSC
            try:
                tsc_data = self.tsc_integration.leer_datos_archivo()
                if tsc_data is not None:
                    telemetry_data = {
                        "velocidad_actual": float(tsc_data.get("velocidad_actual", 0)),
                        "aceleracion": float(tsc_data.get("aceleracion", 0)),
                        "presion_freno": float(tsc_data.get("presion_freno", 0)),
                        "acelerador": float(tsc_data.get("acelerador", 0)),
                        "rpm": float(tsc_data.get("rpm", 0)),
                        "corriente": float(tsc_data.get("corriente", 0)),
                    }
                else:
                    raise ValueError("Datos TSC no disponibles")
            except Exception as e:
                # Fallback a datos simulados si no hay datos reales
                print(f"Usando datos simulados (error TSC: {e})")
                telemetry_data = {
                    "velocidad_actual": np.random.normal(80, 10),
                    "aceleracion": np.random.normal(0, 0.5),
                    "presion_freno": np.random.uniform(0, 100),
                    "acelerador": np.random.uniform(0, 100),
                    "rpm": np.random.normal(800, 100),
                    "corriente": np.random.normal(500, 50),
                }

        new_data = {
            "time": [current_time],
            "velocity": [telemetry_data.get("velocidad_actual", 0)],
            "acceleration": [telemetry_data.get("aceleracion", 0)],
            "brake_pressure": [telemetry_data.get("presion_freno", 0)],
            "throttle": [telemetry_data.get("acelerador", 0)],
            "rpm": [telemetry_data.get("rpm", 0)],
            "current": [telemetry_data.get("corriente", 0)],
        }

        # Agregar nuevos datos usando stream con rollover automático
        window_minutes = self.slider_window.value
        max_points = window_minutes * 60  # puntos por minuto
        self.source.stream(new_data, rollover=int(max_points))

    def update_window(self, attr, old, new):
        """Actualizar ventana de tiempo"""
        # Nota: Bokeh no permite cambiar rollover dinámicamente,
        # el rollover se establece en cada llamada a stream() en update_data()
        pass

    def clear_data(self):
        """Limpiar todos los datos"""
        self.source.data = {
            "time": [],
            "velocity": [],
            "acceleration": [],
            "brake_pressure": [],
            "throttle": [],
            "rpm": [],
            "current": [],
        }

    # ==================== CONTROLES AVANZADOS - FASE 3 ====================

    def play_data(self):
        """Iniciar reproducción de datos"""
        self.is_playing = True
        self.button_play.disabled = True
        self.button_pause.disabled = False
        print("▶️ Reproducción iniciada")

    def pause_data(self):
        """Pausar reproducción de datos"""
        self.is_playing = False
        self.button_play.disabled = False
        self.button_pause.disabled = True
        print("⏸️ Reproducción pausada")

    def reset_data(self):
        """Resetear dashboard a estado inicial"""
        self.clear_data()
        self.is_playing = True
        self.button_play.disabled = True
        self.button_pause.disabled = False
        self.slider_window.value = 5  # Reset a valor por defecto
        print("🔄 Dashboard reseteado")

    def change_theme(self, attr, old, new):
        """Cambiar tema del dashboard"""
        # Los themes se aplicarán en el nivel de documento Bokeh
        # Esta funcionalidad se implementará cuando se integre con el servidor
        print(f"🎨 Cambiando tema a: {new}")

    def export_charts(self):
        """Exportar gráficos en alta resolución"""
        try:
            import os
            from datetime import datetime

            from bokeh.io import export_png

            # Crear directorio de exportación
            export_dir = "exports"
            os.makedirs(export_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Exportar cada gráfico
            exports = []
            for name, plot in [
                ("velocity", self.p_velocity),
                ("acceleration", self.p_acceleration),
                ("brake", self.p_brake),
                ("throttle", self.p_throttle),
            ]:
                filename = f"{export_dir}/tsc_dashboard_{name}_{timestamp}.png"
                export_png(plot, filename=filename)
                exports.append(filename)

            print(f"📊 Gráficos exportados: {', '.join(exports)}")

        except ImportError:
            print("❌ Error: selenium y webdriver-manager requeridos para exportación")
            print("   Instalar con: pip install selenium webdriver-manager")
        except Exception as e:
            print(f"❌ Error exportando gráficos: {e}")


def create_bokeh_app():
    """Crear aplicación Bokeh"""
    dashboard = BokehDashboard()

    def app(doc):
        doc.title = "Train Simulator Autopilot - Dashboard Interactivo"
        doc.add_root(dashboard.layout)

        # Función para actualizar datos periódicamente
        def update():
            # Aquí se conectarían con los datos reales del sistema
            # Por ahora, datos de ejemplo
            mock_data = {
                "velocidad_actual": np.random.normal(80, 10),
                "aceleracion": np.random.normal(0, 0.5),
                "presion_freno": np.random.uniform(0, 100),
                "acelerador": np.random.uniform(0, 100),
                "rpm": np.random.normal(800, 100),
                "corriente": np.random.normal(500, 50),
            }
            dashboard.update_data(mock_data)

        # Actualizar cada segundo
        doc.add_periodic_callback(update, 1000)

    return app


if __name__ == "__main__":
    # Ejecutar servidor Bokeh
    app = create_bokeh_app()
    handler = FunctionHandler(app)

    server = Server({"/": Application(handler)}, port=5006)
    server.start()

    print("Dashboard Bokeh ejecutándose en http://localhost:5006")
    server.io_loop.start()
