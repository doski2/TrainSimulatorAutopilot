#!/usr/bin/env python3
"""
architecture_diagram.py
Diagrama de arquitectura completo del sistema TrainSimulatorAutopilot
Genera un diagrama visual usando la librería diagrams
"""

from diagrams import Cluster, Diagram
from diagrams.generic.compute import Rack
from diagrams.generic.device import Mobile  # noqa: F401 - Reserved for future mobile interface
from diagrams.generic.os import Windows
from diagrams.generic.storage import Storage
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.programming.language import Python


def create_architecture_diagram():
    """Crear diagrama de arquitectura completo del sistema TrainSimulatorAutopilot"""
    # pylint: disable=expression-not-assigned
    # Pylance disable for diagram connections - they create edges but don't need assignment

    with Diagram(
        "TrainSimulatorAutopilot - Arquitectura Completa",
        show=False,
        filename="architecture_diagram_complete",
        direction="TB",
    ):

        # Usuario
        user = User("Usuario")

        # Aplicación Electron
        with Cluster("Aplicación Desktop"):
            electron_app = Windows("main.js\n(Electron App)")
            test_config = Storage("test_config.html")  # noqa: F841 - Part of diagram structure

        # Dashboard Web
        with Cluster("Dashboard Web"):
            flask_app = Server("web_dashboard.py\n(Flask Server - Puerto 5001)")
            socketio = Internet("Socket.IO\n(Tiempo Real)")
            with Cluster("Frontend"):
                index_html = Storage("index.html")
                dashboard_js = Storage("dashboard.js")
                dashboard_css = Storage("dashboard.css")

        # Backend Python - Componentes principales
        with Cluster("Backend Python - Core"):
            with Cluster("Integración TSC"):
                tsc_integration = Python("tsc_integration.py")
                _tsc_optimized = Python(
                    "tsc_integration_optimized.py"
                )  # noqa: F841 - Part of diagram structure
                getdata_file = Storage("GetData.txt")

            with Cluster("Sistema de Autopilot"):
                autopilot_system = Python("autopilot_system.py")
                predictive_analysis = Python("predictive_telemetry_analysis.py")
                multi_loco = Python("multi_locomotive_integration.py")

            with Cluster("Monitoreo y Utilidades"):
                performance_monitor = Python("performance_monitor.py")
                logging_config = Python("logging_config.py")
                configurator = Python("configurator.py")  # noqa: F841 - Part of diagram structure

        # Scripts y Configuración
        with Cluster("Scripts y Configuración"):
            with Cluster("Scripts de Inicio"):
                start_bat = Storage("start.bat")
                start_dev_bat = Storage("start_dev.bat")
                iniciar_dashboard = Storage("iniciar_dashboard.bat")

            with Cluster("Scripts de Testing"):
                _test_config_bat = Storage(
                    "test_config.bat"
                )  # noqa: F841 - Part of diagram structure
                _diagnostico_config = Storage(
                    "diagnostico_config.bat"
                )  # noqa: F841 - Part of diagram structure

            with Cluster("Configuración"):
                config_ini = Storage("config.ini")
                _config_example = Storage(
                    "config.ini.example"
                )  # noqa: F841 - Part of diagram structure
                pytest_ini = Storage("pytest.ini")

        # Interfaz Raildriver
        with Cluster("Raildriver Interface v3.3.0.9"):
            raildriver = Rack("Raildriver Interface")
            lua_script = Storage("Railworks_GetData_Script.lua")
            with Cluster("Configuración Raildriver"):
                _alternative_engine = Storage(
                    "Alternative_New_Engine_Template.lua"
                )  # noqa: F841 - Part of diagram structure
                _control_names = Storage(
                    "ControlNames_Master.txt"
                )  # noqa: F841 - Part of diagram structure

        # Train Simulator Classic
        with Cluster("Train Simulator Classic"):
            tsc = Rack("TSC Engine")
            plugins_folder = Storage("plugins/")  # noqa: F841 - Part of diagram structure
            getdata_output = Storage("GetData.txt\n(Output)")
            _sendcommand_input = Storage(
                "SendCommand.txt\n(Input)"
            )  # noqa: F841 - Part of diagram structure

        # Tests y QA
        with Cluster("Testing y QA"):
            with Cluster("Tests Unitarios"):
                test_tsc = Storage("test_tsc_integration.py")
                test_dashboard = Storage("test_dashboard.py")
                test_predictive = Storage("test_predictive_telemetry.py")

            with Cluster("Tests E2E"):
                e2e_tests = Storage("tests/e2e/")  # noqa: F841 - Part of diagram structure

            with Cluster("Cobertura"):
                htmlcov = Storage("htmlcov/")  # noqa: F841 - Part of diagram structure
                coverage_reports = Storage("coverage.xml")  # noqa: F841 - Part of diagram structure

        # Documentación
        with Cluster("Documentación"):
            readme_md = Storage("README.md")
            readme_desktop = Storage("README_DESKTOP.md")  # noqa: F841 - Part of diagram structure
            docs_folder = Storage("docs/")
            mkdocs_yml = Storage("mkdocs.yml")  # noqa: F841 - Part of diagram structure
            with Cluster("Documentos Técnicos"):
                data_received = Storage("Data received from Railworks.txt")
                security_report = Storage("SECURITY_REPORT.md")
                changelog = Storage("CHANGELOG.md")  # noqa: F841 - Part of diagram structure

        # Datos y Resultados
        with Cluster("Datos y Resultados"):
            with Cluster("Datos de Telemetría"):
                _test_historial = Storage(
                    "test_historial.json"
                )  # noqa: F841 - Part of diagram structure
                benchmark_results = Storage("benchmark_resultados.json")
                bandit_results = Storage("bandit_results.json")

            with Cluster("Gráficos y Visuales"):
                _velocidad_chart = Storage(
                    "velocidad_chart.png"
                )  # noqa: F841 - Part of diagram structure
                _controles_chart = Storage(
                    "controles_chart.png"
                )  # noqa: F841 - Part of diagram structure

        # Conexiones principales
        # Diagram connections create edges but don't need assignment - using _ to indicate intentional
        _ = user >> electron_app >> flask_app
        _ = electron_app >> test_config
        _ = flask_app >> socketio >> index_html
        _ = index_html >> dashboard_js
        _ = index_html >> dashboard_css

        # Conexiones del backend
        _ = flask_app >> tsc_integration
        _ = flask_app >> autopilot_system
        _ = flask_app >> predictive_analysis
        _ = flask_app >> multi_loco
        _ = flask_app >> performance_monitor

        # Conexiones entre componentes del backend
        _ = autopilot_system >> multi_loco
        _ = autopilot_system >> predictive_analysis
        _ = predictive_analysis >> performance_monitor
        _ = tsc_integration >> logging_config

        # Conexión a Raildriver
        _ = tsc_integration >> raildriver
        _ = raildriver >> lua_script
        _ = lua_script >> tsc

        # Scripts de inicio
        _ = start_bat >> electron_app
        _ = start_dev_bat >> electron_app
        _ = iniciar_dashboard >> flask_app

        # Configuración
        _ = config_ini >> tsc_integration
        _ = config_ini >> autopilot_system
        _ = pytest_ini >> test_tsc

        # Datos de telemetría
        _ = tsc >> lua_script >> getdata_output
        _ = getdata_output >> tsc_integration
        _ = tsc_integration >> getdata_file

        # Tests
        _ = test_tsc >> tsc_integration
        _ = test_dashboard >> flask_app
        _ = test_predictive >> predictive_analysis

        # Documentación
        _ = readme_md >> user
        _ = docs_folder >> data_received
        _ = docs_folder >> security_report

        # Resultados
        _ = performance_monitor >> benchmark_results
        _ = test_tsc >> bandit_results


if __name__ == "__main__":
    create_architecture_diagram()
    print("Diagrama de arquitectura completa generado: architecture_diagram_complete.png")
