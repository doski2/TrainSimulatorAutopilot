# integrated_bokeh.py
# Integración de Bokeh con el dashboard Flask existente

import threading
import time

from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.embed import server_document
from bokeh.server.server import Server
from flask import Flask, render_template


class BokehFlaskIntegration:
    """Integración de Bokeh con aplicación Flask existente"""

    def __init__(self, flask_app, bokeh_port=5020):
        self.flask_app = flask_app
        self.bokeh_port = bokeh_port
        self.bokeh_server = None
        self.server_thread = None

    def create_bokeh_app(self):
        """Crear aplicación Bokeh simple para integración"""

        def bokeh_app(doc):
            from bokeh.models import ColumnDataSource
            from bokeh.plotting import figure

            # Datos de ejemplo
            source = ColumnDataSource(data={"x": [1, 2, 3, 4, 5], "y": [2, 5, 3, 8, 7]})

            p = figure(title="Gráfico Integrado con Flask", width=400, height=300)
            p.scatter("x", "y", source=source, size=10, color="blue")

            doc.add_root(p)

        return bokeh_app

    def start_bokeh_server(self):
        """Iniciar servidor Bokeh en thread separado"""

        def run_server():
            app = self.create_bokeh_app()
            handler = FunctionHandler(app)

            self.bokeh_server = Server(
                {"/bokeh": Application(handler)},
                port=self.bokeh_port,
                allow_websocket_origin=["localhost:5002"],  # Permitir desde Flask
            )

            print(f"Servidor Bokeh iniciado en puerto {self.bokeh_port}")
            self.bokeh_server.start()
            self.bokeh_server.io_loop.start()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        # Esperar a que el servidor esté listo
        time.sleep(2)

    def get_bokeh_script(self):
        """Obtener script para embeber en template Flask"""
        bokeh_url = f"http://localhost:{self.bokeh_port}/bokeh"
        return server_document(bokeh_url)


# Extensión del dashboard Flask existente
def setup_bokeh_integration(app):
    """Configurar integración Bokeh en aplicación Flask"""

    bokeh_integration = BokehFlaskIntegration(app)

    @app.route("/bokeh-dashboard")
    def bokeh_dashboard():
        """Ruta para dashboard con Bokeh integrado"""
        bokeh_script = bokeh_integration.get_bokeh_script()
        return render_template(
            "bokeh_dashboard.html", bokeh_script=bokeh_script, title="Dashboard con Bokeh"
        )

    return bokeh_integration


# Template HTML para integrar Bokeh (bokeh_dashboard.html)
BOKEH_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
          rel="stylesheet">

    <!-- Bokeh CSS/JS -->
    {{ bokeh_script | safe }}
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h1 class="mt-4 mb-4">{{ title }}</h1>
            </div>
        </div>

        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>Gráfico Interactivo Bokeh</h5>
                    </div>
                    <div class="card-body">
                        <!-- Aquí se renderiza el gráfico Bokeh -->
                        <div id="bokeh-plot">
                            <!-- Bokeh insertará el gráfico aquí -->
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Información</h5>
                    </div>
                    <div class="card-body">
                        <p>Este dashboard integra Bokeh con Flask para visualizaciones interactivas.</p>
                        <ul>
                            <li>✅ Gráficos interactivos</li>
                            <li>✅ Actualización en tiempo real</li>
                            <li>✅ Integración perfecta con Flask</li>
                        </ul>
                        <a href="/" class="btn btn-primary">Volver al Dashboard Principal</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Ejemplo de uso
if __name__ == "__main__":
    import os

    from flask import Flask

    app = Flask(__name__, template_folder="../web/templates")

    # Configurar integración Bokeh
    bokeh_integration = setup_bokeh_integration(app)

    # Iniciar servidor Bokeh
    bokeh_integration.start_bokeh_server()

    print("Iniciando servidor Flask con Bokeh integrado...")
    print("Accede a:")
    print("- Dashboard principal: http://localhost:5002/")
    print("- Dashboard Bokeh: http://localhost:5002/bokeh-dashboard")

    # Security: Use environment variable for debug mode to prevent code execution in production (CWE-94)
    # Default to False for production safety
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    app.run(host="localhost", port=5002, debug=debug_mode)
