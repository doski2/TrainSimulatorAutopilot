# demo_bokeh_simple.py
# Demostración simple de Bokeh para Train Simulator Autopilot

import numpy as np
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, save


def crear_dashboard_estatico():
    """Crear un dashboard estático con Bokeh"""

    # Datos de ejemplo de telemetría
    np.random.seed(42)
    n_points = 100

    data = {
        "tiempo": pd.date_range("2025-01-01 10:00:00", periods=n_points, freq="1s"),
        "velocidad": np.random.normal(75, 10, n_points).clip(0, 120),
        "aceleracion": np.random.normal(0, 0.5, n_points),
        "rpm": np.random.normal(800, 100, n_points).clip(0, 1500),
        "presion_freno": np.random.uniform(0, 100, n_points),
        "acelerador": np.random.uniform(0, 100, n_points),
    }

    df = pd.DataFrame(data)
    source = ColumnDataSource(df)

    # Crear gráficos
    p1 = figure(title="Velocidad del Tren", x_axis_type="datetime", width=600, height=300)
    p1.line("tiempo", "velocidad", source=source, line_width=2, color="blue")
    p1.xaxis.axis_label = "Tiempo"
    p1.yaxis.axis_label = "Velocidad (km/h)"

    p2 = figure(title="Aceleración", x_axis_type="datetime", width=600, height=300)
    p2.line("tiempo", "aceleracion", source=source, line_width=2, color="green")
    p2.xaxis.axis_label = "Tiempo"
    p2.yaxis.axis_label = "Aceleración (m/s²)"

    p3 = figure(title="Presión de Freno", x_axis_type="datetime", width=600, height=300)
    p3.line("tiempo", "presion_freno", source=source, line_width=2, color="red")
    p3.xaxis.axis_label = "Tiempo"
    p3.yaxis.axis_label = "Presión (PSI)"

    p4 = figure(title="Acelerador vs RPM", width=600, height=300)
    p4.scatter(x="acelerador", y="rpm", source=source, size=8, alpha=0.6, color="orange")
    p4.xaxis.axis_label = "Acelerador (%)"
    p4.yaxis.axis_label = "RPM"

    # Layout
    layout = column(row(p1, p2), row(p3, p4))

    # Guardar como HTML
    output_file("bokeh_dashboard_estatico.html")
    save(layout)

    print("Dashboard estático creado: bokeh_dashboard_estatico.html")
    print("Abre el archivo en tu navegador para ver los gráficos interactivos")


def crear_analisis_estadistico():
    """Crear análisis estadístico con datos de ejemplo"""

    # Generar datos de ejemplo
    np.random.seed(42)
    n_samples = 1000

    data = {
        "velocidad": np.random.normal(75, 15, n_samples).clip(0, 150),
        "aceleracion": np.random.normal(0, 0.8, n_samples),
        "rpm": np.random.normal(800, 150, n_samples).clip(0),
        "presion_freno": np.random.uniform(0, 120, n_samples),
        "acelerador": np.random.uniform(0, 100, n_samples),
        "corriente": np.random.normal(450, 80, n_samples).clip(0),
        "freno": np.random.uniform(0, 100, n_samples),
    }

    df = pd.DataFrame(data)

    # Crear visualizaciones estadísticas
    from bokeh.layouts import gridplot

    # Histogramas usando numpy
    hist_vel = figure(title="Distribución de Velocidad", width=400, height=300)
    hist, edges = np.histogram(df["velocidad"], bins=20)
    hist_vel.quad(
        top=hist,
        bottom=0,
        left=edges[:-1],
        right=edges[1:],
        fill_color="blue",
        line_color="white",
        alpha=0.7,
    )
    hist_vel.xaxis.axis_label = "Velocidad (km/h)"
    hist_vel.yaxis.axis_label = "Frecuencia"

    # Scatter plot
    scatter = figure(title="Velocidad vs RPM", width=400, height=300)
    scatter.scatter(
        x="velocidad", y="rpm", source=ColumnDataSource(df), size=5, alpha=0.6, color="red"
    )
    scatter.xaxis.axis_label = "Velocidad (km/h)"
    scatter.yaxis.axis_label = "RPM"

    # Estadísticas descriptivas como texto
    stats_text = f"""
    Estadísticas de Velocidad:
    Media: {df['velocidad'].mean():.1f} km/h
    Desv. Estándar: {df['velocidad'].std():.1f} km/h
    Mín: {df['velocidad'].min():.1f} km/h
    Máx: {df['velocidad'].max():.1f} km/h

    Estadísticas de RPM:
    Media: {df['rpm'].mean():.0f} RPM
    Desv. Estándar: {df['rpm'].std():.0f} RPM
    """

    from bokeh.models import Div

    stats_div = Div(text=f"<pre>{stats_text}</pre>", width=400, height=300)

    # Layout
    grid = gridplot([[hist_vel, scatter], [stats_div, None]])
    output_file("bokeh_analisis_estadistico.html")
    save(grid)

    print("Análisis estadístico creado: bokeh_analisis_estadistico.html")


if __name__ == "__main__":
    print("🚀 Creando dashboards con Bokeh para Train Simulator Autopilot")
    print()

    print("1. Creando dashboard estático...")
    crear_dashboard_estatico()
    print()

    print("2. Creando análisis estadístico...")
    crear_analisis_estadistico()
    print()

    print("✅ ¡Completado!")
    print()
    print("Archivos generados:")
    print("- bokeh_dashboard_estatico.html")
    print("- bokeh_analisis_estadistico.html")
    print()
    print("Abre estos archivos en tu navegador para ver los gráficos interactivos de Bokeh.")
