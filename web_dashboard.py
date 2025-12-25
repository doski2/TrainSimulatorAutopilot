#!/usr/bin/env python3
"""
web_dashboard.py
Dashboard web en tiempo real para Train Simulator Autopilot
Servidor web completo con WebSockets, APIs REST y interfaz moderna
"""

# Configurar path antes de cualquier otro import
import os  # noqa: E402
import sys  # noqa: E402

print(f"[BOOT] Python executable: {sys.executable}")
print(f"[BOOT] Python version: {sys.version}")
print(f"[BOOT] Directorio actual: {os.getcwd()}")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"[BOOT] Path agregado: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")

# Thread-local storage for stub request JSON data to avoid cross-request races
# We initialize lazily so module import order does not require `threading` to be available immediately.
_thread_local = None


def _get_current_json_data():
    """Return the thread-local current JSON data for stub requests."""
    global _thread_local
    if _thread_local is None:
        import threading

        _thread_local = threading.local()
    return getattr(_thread_local, "current_json_data", None)


def _set_current_json_data(val):
    """Set the thread-local current JSON data for stub requests."""
    global _thread_local
    if _thread_local is None:
        import threading

        _thread_local = threading.local()
    _thread_local.current_json_data = val

# Standard library imports
import configparser  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Directorio actual: {os.getcwd()}")
logger.info(f"Path agregado: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")

# Optional imports (with fallbacks)
try:
    import psutil  # noqa: E402

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False
    logger.warning("psutil no disponible - algunas métricas estarán limitadas")

logger.info("Imports estándar completados")

# Third-party imports
try:
    from bokeh.embed import server_document  # noqa: E402
    from flask import Flask, Response, jsonify, render_template, request  # noqa: E402
    from flask_socketio import SocketIO, emit  # noqa: E402

    print("[BOOT] Imports de terceros completados")
except Exception as e:
    # Entorno de pruebas sin dependencias: crear stubs mínimos para tests
    print(f"[BOOT] Error en imports de terceros: {e} — usando stubs para pruebas")

    # Minimal request stub
    class _SimpleRequest:
        def get_json(self):
            return _get_current_json_data()

    request = _SimpleRequest()

    # Simple jsonify
    def jsonify(obj):
        return obj

    def render_template(template_name_or_list, **context):
        return f"<rendered {template_name_or_list}>"

    # Simple Flask-like test harness
    class _SimpleResponse:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data

        def get_json(self):
            return self._data

    class _SimpleClient:
        def __init__(self, app):
            self.app = app
            self._json_data = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, path, json=None):
            # Thread-safe: set the thread-local json data for the stub request
            _set_current_json_data(json)
            try:
                func = self.app._routes.get(path)
                if not func:
                    return _SimpleResponse(404, {"error": "not found"})
                # Call view function without arguments (compatible with Flask view signature)
                result = func() if callable(func) else (None, 500)
                if isinstance(result, tuple):
                    data, code = result
                else:
                    data, code = result, 200
                return _SimpleResponse(code, data)
            finally:
                # Clear thread-local storage after handling to avoid leakage between requests
                _set_current_json_data(None)

    class Flask:
        def __init__(self, *a, **kw):
            self._routes = {}
            self.config = {}
            self._after_request = None
            self.static_folder = kw.get("static_folder", "web/static")
            self.template_folder = kw.get("template_folder", "web/templates")
            self.name = "web_dashboard"
            self.import_name = "web_dashboard"

            class _MockUrlMap:
                def __init__(self):
                    self._rules = []

            self.url_map = _MockUrlMap()

        def route(self, path, methods=None):
            def decorator(f):
                self._routes[path] = f
                return f

            return decorator

        def after_request(self, f):
            # register a function to be called after requests; store and return
            self._after_request = f
            return f

        def test_client(self):
            return _SimpleClient(self)

        # Minimal render_template compatibility
        def render_template(self, *args, **kwargs):
            return ''

    # Minimal socketio stub
    class _SimpleSocketIO:
        def __init__(self, app, cors_allowed_origins=None, async_mode=None):
            self.app = app
            self._handlers = {}

        def emit(self, *args, **kwargs):
            pass

        def on(self, event):
            def decorator(f):
                self._handlers[event] = f
                return f

            return decorator

        def run(self, *args, **kwargs):
            pass

    SocketIO = _SimpleSocketIO

    def emit(*args, **kwargs):
        pass


# Local imports
try:
    from direct_tsc_control import DirectTSCControl, create_direct_control  # noqa: E402

    DIRECT_CONTROL_AVAILABLE = True
    print("[BOOT] Sistema de control directo TSC disponible")
except ImportError:
    DirectTSCControl = None
    create_direct_control = None
    DIRECT_CONTROL_AVAILABLE = False
    print("[BOOT] Sistema de control directo TSC no disponible")

try:
    from tsc_integration import TSCIntegration  # noqa: E402

    TSC_AVAILABLE = True
    print("[BOOT] TSC Integration importado (modo compatibilidad)")
except ImportError:
    TSC_AVAILABLE = False
    TSCIntegration = None
    print("[BOOT] TSC Integration no disponible")

# POC helpers para protocolo file+ACK
try:
    from tools.poc_file_ack.enqueue import atomic_write_cmd, send_command_with_retries  # noqa: E402
except Exception:
    # En entornos donde 'tools' no esté disponible (tests aislados), lo ignoramos
    atomic_write_cmd = None
    send_command_with_retries = None

try:
    # from predictive_telemetry_analysis import PredictiveTelemetryAnalyzer  # noqa: E402  # TEMPORALMENTE COMENTADO
    from multi_locomotive_integration import MultiLocomotiveIntegration  # noqa: E402

    print("[BOOT] Multi-locomotive integration importado")

    from autopilot_system import AutopilotSystem  # noqa: E402

    print("[BOOT] Autopilot system importado")

    from performance_monitor import (  # noqa: E402
        data_compressor,
        latency_optimizer,
        optimize_dashboard_performance,
        performance_monitor,
        record_dashboard_metric,
        smart_cache,
    )

    print("[BOOT] Performance monitor importado")

    from alert_system import check_alerts, get_alert_system  # noqa: E402
    print("[BOOT] Alert system importado")

    from automated_reports import generate_report, get_automated_reports  # noqa: E402
    print("[BOOT] Automated reports importado")

except Exception as e:
    # Do not exit on missing optional local modules; continue in degraded mode
    print(f"[BOOT] Warning: some local imports failed: {e}")
    import traceback

    traceback.print_exc()

logger.info("Todos los imports completados exitosamente")

# Configuración del servidor

# Configuración del servidor
app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())
app.config["SESSION_COOKIE_SECURE"] = False  # Para desarrollo local
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hora

# Timeout para esperar ACK del plugin autopilot (segundos). Puede sobreescribirse
# por variable de entorno AUTOPILOT_ACK_TIMEOUT
try:
    AUTOPILOT_ACK_TIMEOUT = float(os.getenv("AUTOPILOT_ACK_TIMEOUT", "3.0"))
except Exception:
    AUTOPILOT_ACK_TIMEOUT = 3.0

# Configuración SocketIO
SOCKETIO_CORS_ORIGINS = "*"
SOCKETIO_ASYNC_MODE = "threading"
socketio = SocketIO(app, cors_allowed_origins=SOCKETIO_CORS_ORIGINS, async_mode=SOCKETIO_ASYNC_MODE)

# Componentes del sistema
tsc_integration = None
predictive_analyzer = None
multi_loco_integration = None
autopilot_system = None
direct_control = None

# Estado del dashboard
dashboard_active = False
telemetry_thread = None
last_telemetry = {}
bokeh_port = None  # Puerto dinámico del servidor Bokeh
start_time = time.time()  # Tiempo de inicio del servidor
system_status = {
    "tsc_connected": False,
    "predictive_active": False,
    "multi_loco_active": False,
    "autopilot_active": False,
    "telemetry_updates": 0,
    "telemetry_source": "unknown",
    "alerts_active": False,
    "reports_active": False,
    "autobrake_by_signal": True,
    "performance_monitoring": False,
}

# Métricas relacionadas con el plugin Autopilot (visibilidad y reintentos)
autopilot_metrics = {
    "retry_total": 0,
    "unacked_total": 0,
}

# Estado de controles de locomotora
control_states = {
    "lights_on": False,  # Estado actual de las luces
}


def validate_dashboard_config(config):
    """
    Valida la configuración del dashboard.

    Args:
        config (dict): Configuración a validar

    Returns:
        tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Validar tema
    if "theme" in config:
        valid_themes = ["light", "dark", "auto"]
        if config["theme"] not in valid_themes:
            errors.append(f"Tema inválido: {config['theme']}. Valores válidos: {valid_themes}")

    # Validar intervalo de actualización
    if "updateInterval" in config:
        interval = config["updateInterval"]
        if not isinstance(interval, (int, float)) or interval < 100 or interval > 10000:
            errors.append("Intervalo de actualización debe estar entre 100ms y 10000ms")
        elif interval < 500:
            warnings.append("Intervalo muy bajo puede afectar el rendimiento")

    # Validar puntos de historial
    if "historyPoints" in config:
        points = config["historyPoints"]
        if not isinstance(points, int) or points < 10 or points > 1000:
            errors.append("Puntos de historial deben estar entre 10 y 1000")
        elif points > 200:
            warnings.append("Muchos puntos de historial pueden afectar el rendimiento")

    # Validar unidad de velocidad
    if "speedUnit" in config:
        valid_units = ["mph", "kmh", "ms"]
        if config["speedUnit"] not in valid_units:
            errors.append(
                f"Unidad de velocidad inválida: {config['speedUnit']}. Valores válidos: {valid_units}"
            )

    # Validar configuración de alertas
    if "alerts" in config:
        alerts = config["alerts"]
        if not isinstance(alerts, dict):
            errors.append("Configuración de alertas debe ser un objeto")
        else:
            valid_alert_types = ["speedLimit", "emergency", "system"]
            for alert_type in alerts:
                if alert_type not in valid_alert_types:
                    warnings.append(f"Tipo de alerta desconocido: {alert_type}")
                elif not isinstance(alerts[alert_type], bool):
                    errors.append(f"Alerta {alert_type} debe ser true/false")

    # Validar animaciones
    if "animations" in config:
        if not isinstance(config["animations"], bool):
            errors.append("Configuración de animaciones debe ser true/false")

    return len(errors) == 0, errors, warnings


def initialize_system():
    """Inicializar todos los componentes del sistema."""
    global tsc_integration, predictive_analyzer, multi_loco_integration, autopilot_system, direct_control

    logger.info("Comenzando inicialización del sistema...")
    try:
        # Inicializar control directo TSC (sistema primario)
        if DIRECT_CONTROL_AVAILABLE:
            logger.info("Inicializando control directo TSC...")
            assert create_direct_control is not None  # Type guard for Pylance
            direct_control = create_direct_control()
            if direct_control.connect():
                system_status["tsc_connected"] = True
                system_status["control_mode"] = "direct"
                print("[OK] Control directo TSC inicializado")
            else:
                logger.warning("Control directo TSC falló, intentando modo compatibilidad")
                system_status["control_mode"] = "compatibility"
        else:
            logger.info("Control directo no disponible, usando modo compatibilidad")
            system_status["control_mode"] = "compatibility"

        # Inicializar integración TSC (SIEMPRE para lectura de telemetría)
        if TSC_AVAILABLE:
            logger.info("Inicializando integración TSC (lectura de telemetría)...")
            # Usar archivo de prueba para debugging del dashboard
            ruta_prueba = os.path.join(os.path.dirname(__file__), "test_data.txt")
            if os.path.exists(ruta_prueba):
                logger.info(f"Usando archivo de prueba: {ruta_prueba}")
                tsc_integration = TSCIntegration(ruta_archivo=ruta_prueba)
                system_status["telemetry_source"] = "test"
            else:
                logger.info("Archivo de prueba no encontrado, usando ruta por defecto")
                tsc_integration = TSCIntegration()
                system_status["telemetry_source"] = "GetData"
            print("[OK] Integración TSC inicializada (para telemetría)")
        else:
            print("[WARN] Integración TSC no disponible - no se podrá leer telemetría")
            tsc_integration = None
            if system_status["control_mode"] == "compatibility":
                system_status["tsc_connected"] = False

        logger.info("Inicializando analizador predictivo...")
        # Inicializar analizador predictivo
        # predictive_analyzer = PredictiveTelemetryAnalyzer()  # TEMPORALMENTE COMENTADO
        # system_status['predictive_active'] = predictive_analyzer.predictive_model.is_trained  # TEMPORALMENTE COMENTADO
        system_status["predictive_active"] = False  # TEMPORAL
        logger.info("Analizador predictivo inicializado (temporalmente desactivado)")

        logger.info("Inicializando integracion multi-locomotora...")
        # Inicializar integración multi-locomotora
        multi_loco_integration = MultiLocomotiveIntegration()
        system_status["multi_loco_active"] = True
        logger.info("Integracion multi-locomotora inicializada")

        logger.info("Inicializando sistema autopilot...")
        # Inicializar sistema autopilot
        autopilot_system = AutopilotSystem()
        system_status["autopilot_active"] = False  # Inicia detenido
        logger.info("Sistema autopilot inicializado")
        # Cargar la opción autobrake_by_signal del config.ini y aplicarla
        try:
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(__file__), "config.ini")
            if os.path.exists(config_path):
                config.read(config_path, encoding="utf-8")
                ab = config.getboolean("TSC_INTEGRATION", "autobrake_by_signal", fallback=True)
                system_status["autobrake_by_signal"] = ab
                try:
                    autopilot_system.autobrake_by_signal = ab
                except Exception:
                    # Ignore if autopilot doesn't have the attribute
                    pass
                # Fuel capacity configuration removed (feature deprecated)
        except Exception:
            pass

        logger.info("Inicializando sistema de alertas...")
        # Inicializar sistema de alertas
        alert_system = get_alert_system()
        alert_system.start_monitoring(interval_seconds=30)
        system_status["alerts_active"] = True
        logger.info("Sistema de alertas inicializado")

        logger.info("Inicializando sistema de reportes...")
        # Inicializar sistema de reportes
        reports_system = get_automated_reports()
        # Verificar que el sistema se inicializó correctamente
        status = reports_system.get_reports_status()
        system_status["reports_active"] = status.get("automation_enabled", False)
        logger.info("Sistema de reportes inicializado")

        logger.info("Todos los componentes inicializados exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando sistema: {e}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


def telemetry_update_loop():
    """Bucle principal de actualización de telemetría."""
    global last_telemetry, system_status

    logger.debug("Iniciando bucle de telemetria")
    update_count = 0
    last_update_time = time.time()

    while dashboard_active:
        loop_start = time.time()

        try:
            # Leer telemetría actual
            if tsc_integration:
                telemetry = tsc_integration.obtener_datos_telemetria()
                system_status["simulator_active"] = tsc_integration.simulador_activo
                if telemetry:
                    last_telemetry = telemetry
                    last_telemetry["timestamp"] = datetime.now().isoformat()
                    system_status["telemetry_updates"] += 1
                    update_count += 1

                    # Calcular frecuencia de actualización
                    current_time = time.time()
                    time_diff = current_time - last_update_time
                    if time_diff > 0:
                        frequency = 1.0 / time_diff
                        record_dashboard_metric("metrics_update_frequency", frequency)
                    last_update_time = current_time
                else:
                    # Si no hay datos del TSC, mantener valores en cero (solo datos reales)
                    if not last_telemetry:
                        # Crear estructura de datos vacía inicial
                        last_telemetry = {
                            "velocidad_actual": 0.0,
                            "aceleracion": 0.0,
                            "pendiente": 0.0,
                            "esfuerzo_traccion": 0.0,
                            "rpm": 0.0,
                            "amperaje": 0.0,
                            "deslizamiento_ruedas": 0.0,
                                    "deslizamiento_ruedas_intensidad": 0.0,
                            "presion_tubo_freno": 0.0,
                            "presion_freno_loco": 0.0,
                            "presion_freno_tren": 0.0,
                            "presion_deposito_equalizacion": 0.0,
                            "presion_tubo_freno_cola": 0.0,
                            "presion_freno_loco_mostrada": 0.0,
                            "timestamp": datetime.now().isoformat(),
                        }

                    # Actualizar solo el timestamp para indicar que el sistema está activo
                    # pero esperando datos reales del simulador
                    last_telemetry["timestamp"] = datetime.now().isoformat()

            # Siempre enviar actualización (con datos reales o simulados)
            if last_telemetry:
                # Comprimir datos antes de enviar - FASE 4
                compressed_telemetry = (
                    data_compressor.compress_data(last_telemetry)
                    if data_compressor
                    else last_telemetry
                )

                # Cache inteligente para predicciones - FASE 4
                cache_key = f"predictions_{int(time.time() // 60)}"  # Cache por minuto
                cached_predictions = smart_cache.get(cache_key) if smart_cache else None
                if cached_predictions is None:
                    # Obtener predicciones actuales del analizador predictivo
                    predictions = (
                        predictive_analyzer.get_current_predictions() if predictive_analyzer else {}
                    )
                    cached_predictions = predictions
                    if smart_cache:
                        smart_cache.put(cache_key, predictions)

                # Obtener datos de multi-locomotora
                multi_loco_data = (
                    multi_loco_integration.leer_datos_todas_locomotoras()
                    if multi_loco_integration
                    else {}
                )

                # Verificar alertas activas
                active_alerts = check_alerts()

                # Obtener métricas de rendimiento
                performance_report = (
                    performance_monitor.get_performance_report()
                    if performance_monitor
                    else {}
                )

                # Obtener estado de reportes
                reports_status = {
                    "status": "not_available",
                    "last_report": None,
                    "scheduled_reports": [],
                }

                # Medir latencia antes de WebSocket emit - FASE 4
                ws_start = time.time()

                # Emitir actualización vía WebSocket (con manejo seguro)
                try:
                    socketio.emit(
                        "telemetry_update",
                        {
                            "telemetry": compressed_telemetry,
                            "predictions": cached_predictions,
                            "multi_loco": multi_loco_data,
                            "system_status": system_status,
                            "active_alerts": active_alerts,
                            "performance": performance_report,
                            "reports": reports_status,
                        },
                    )

                    # Registrar latencia WebSocket con optimizaciones
                    ws_latency = (time.time() - ws_start) * 1000  # ms
                    record_dashboard_metric("websocket_latency", ws_latency)

                    # Aplicar optimizaciones de latencia si latencia es alta
                    if ws_latency > 50:  # Más de 50ms
                        if latency_optimizer:
                            latency_optimizer.apply_optimization("websocket_batching")

                    # Debug: show wheelslip raw and intensity for diagnostic
                    try:
                        ws_debug = f"[DEBUG] Wheelslip raw={compressed_telemetry.get('deslizamiento_ruedas_raw')} intensity={compressed_telemetry.get('deslizamiento_ruedas_intensidad')}"
                        print(ws_debug)
                    except Exception as e:
                        print(f"[ERROR] Failed to print wheelslip debug info: {e}")
                        import traceback

                        traceback.print_exc()
                    # Ensure system_status reflects performance monitor state
                    try:
                        system_status["performance_monitoring"] = performance_monitor.is_monitoring
                    except Exception:
                        system_status["performance_monitoring"] = False

                    # Ensure system_status reflects autopilot Lua plugin state (if TSC integration available)
                    try:
                        if tsc_integration:
                            system_status["autopilot_plugin_loaded"] = tsc_integration.is_autopilot_plugin_loaded()
                            system_status["autopilot_plugin_state"] = tsc_integration.get_autopilot_plugin_state()
                        else:
                            system_status["autopilot_plugin_loaded"] = False
                            system_status["autopilot_plugin_state"] = None
                    except Exception:
                        system_status["autopilot_plugin_loaded"] = False
                        system_status["autopilot_plugin_state"] = None

                    # Debug: active alerts payload
                    try:
                        active_list = active_alerts.get('alerts') if isinstance(active_alerts, dict) else active_alerts
                        if isinstance(active_list, list):
                            print(f"[DEBUG] Active alerts (count) = {len(active_list)}")
                            print(f"[DEBUG] Active alerts (types) = {[a.get('alert_type') for a in active_list[:10]]}")
                        else:
                            print(f"[DEBUG] Active alerts: {active_alerts}")
                    except Exception as e:
                        print(f"[ERROR] Failed to print active alerts debug info: {e}")
                        import traceback

                        traceback.print_exc()
                except Exception as emit_error:
                    print(f"[WS] Error en emit: {emit_error}")
                    print(
                        f"[DEBUG] Estado tras error emit: predictive_running={predictive_analyzer.is_running if predictive_analyzer else False}"
                    )
        except Exception as e:
            print(f"[ERROR] Error en actualizacion de telemetria: {e}")
            import traceback

            traceback.print_exc()

        # Registrar tiempo total del loop
        loop_time = (time.time() - loop_start) * 1000  # ms
        if loop_time > 100:  # Solo registrar si excede el intervalo esperado
            record_dashboard_metric("telemetry_loop_time", loop_time)

        time.sleep(0.1)  # 10 Hz


# Rutas web
@app.route("/")
def index():
    """Página principal del dashboard."""
    return render_template("index.html")


@app.after_request
def add_no_cache_headers(response):
    """Agregar headers para evitar cache de archivos estáticos."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/health")
def health_check():
    """Endpoint de health check para verificar estado del servidor."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "tsc_integration": system_status.get("tsc_connected", False),
                "bokeh_server": bokeh_port is not None,
                "alerts_system": system_status.get("alerts_active", False),
                "reports_system": system_status.get("reports_active", False),
                "dashboard_active": dashboard_active,
            },
            "uptime": time.time() - (globals().get("start_time", time.time())),
            "telemetry_updates": system_status.get("telemetry_updates", 0),
        }
    )


@app.route("/api/server_info")
def server_info():
    """Información detallada del servidor."""
    return jsonify(
        {
            "python_version": sys.version,
            "flask_version": getattr(app, "__version__", "unknown"),
            "socketio_version": getattr(socketio, "__version__", "unknown"),
            "server_port": 5001,
            "bokeh_port": bokeh_port,
            "cors_origins": SOCKETIO_CORS_ORIGINS,
            "async_mode": SOCKETIO_ASYNC_MODE,
            "routes_count": len(app.url_map._rules),
            "static_folder": app.static_folder,
            "template_folder": app.template_folder,
        }
    )
    """Página de debug para verificar datos."""
    return f"""
    <html>
    <head><title>Debug - Train Simulator Data</title></head>
    <body>
        <h1>Datos de Train Simulator Classic</h1>
        <pre>{json.dumps(last_telemetry, indent=2, default=str)}</pre>
        <h2>Estado del Sistema</h2>
        <pre>{json.dumps(system_status, indent=2)}</pre>
        <script>
            setInterval(() => {{
                fetch('/debug_data')
                    .then(r => r.json())
                    .then(data => {{
                        document.querySelector('pre').textContent = JSON.stringify(data.telemetry, null, 2);
                        document.querySelectorAll('pre')[1].textContent = JSON.stringify(data.system_status, null, 2);
                    }});
            }}, 1000);
        </script>
    </body>
    </html>
    """


@app.route("/debug_data")
def debug_data_json():
    """API para datos de debug."""
    return jsonify(
        {
            "telemetry": last_telemetry,
            "system_status": system_status,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/validate_config", methods=["POST"])
def validate_config():
    """API para validar configuración del dashboard."""
    start_time = time.time()

    try:
        config = request.get_json()

        if not config:
            return (
                jsonify(
                    {
                        "valid": False,
                        "errors": ["No se recibió configuración"],
                        "warnings": [],
                    }
                ),
                400,
            )

        is_valid, errors, warnings = validate_dashboard_config(config)

        # Registrar tiempo de respuesta de validación
        response_time = (time.time() - start_time) * 1000  # ms
        record_dashboard_metric("dashboard_response_time", response_time)

        # Evaluar si las presiones de freno están presentes en la telemetría actual
        brake_pressure_present = False
        if last_telemetry and isinstance(last_telemetry, dict):
            brake_pressure_present = any(
                [
                    last_telemetry.get("presion_tubo_freno_presente", False),
                    last_telemetry.get("presion_freno_loco_presente", False),
                    last_telemetry.get("presion_freno_tren_presente", False),
                    last_telemetry.get("presion_deposito_principal_presente", False),
                    last_telemetry.get("eq_reservoir_presente", False),
                    last_telemetry.get("presion_tubo_freno_mostrada_presente", False),
                    last_telemetry.get("presion_freno_loco_mostrada_presente", False),
                    last_telemetry.get("presion_deposito_auxiliar_presente", False),
                ]
            )

        return jsonify(
            {
                "valid": is_valid,
                "errors": errors,
                "warnings": warnings,
                "config": config,
                "brake_pressure_present": brake_pressure_present,
            }
        )

    except Exception as e:
        # Registrar error de validación
        record_dashboard_metric("dashboard_response_time", (time.time() - start_time) * 1000)

        return (
            jsonify(
                {
                    "valid": False,
                    "errors": [f"Error interno del servidor: {str(e)}"],
                    "warnings": [],
                }
            ),
            500,
        )


@app.route("/api/performance_report")
def get_performance_report():
    """API para obtener reporte de rendimiento."""
    try:
        if performance_monitor is None:
            return jsonify({"error": "Performance monitor not available"}), 503
        report = performance_monitor.get_performance_report()
        return jsonify(report)
    except Exception as e:
        return (
            jsonify({"error": f"Error obteniendo reporte de rendimiento: {str(e)}"}),
            500,
        )


@app.route("/api/control/status")
def get_control_status():
    """Obtener estado actual de los controles de la locomotora."""
    try:
        return jsonify(
            {
                "success": True,
                "control_states": control_states,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Error obteniendo estado de controles: {str(e)}"}),
            500,
        )


@app.route("/api/status")
def get_system_status():
    """Obtener estado actual del sistema para el dashboard"""
    try:
        # Obtener estado de Bokeh dashboard si está disponible
        bokeh_playback_active = True  # Por defecto activo
        data_points = 0

        # Intentar obtener datos reales si están disponibles
        if last_telemetry:
            data_points = len(last_telemetry) if isinstance(last_telemetry, dict) else 1
        else:
            data_points = 0

        # Evaluar presencia de datos de presión de freno
        brake_pressure_present = False
        if last_telemetry and isinstance(last_telemetry, dict):
            brake_pressure_present = any(
                [
                    last_telemetry.get("presion_tubo_freno_presente", False),
                    last_telemetry.get("presion_freno_loco_presente", False),
                    last_telemetry.get("presion_freno_tren_presente", False),
                    last_telemetry.get("presion_deposito_principal_presente", False),
                    last_telemetry.get("eq_reservoir_presente", False),
                    last_telemetry.get("presion_tubo_freno_mostrada_presente", False),
                    last_telemetry.get("presion_freno_loco_mostrada_presente", False),
                    last_telemetry.get("presion_deposito_auxiliar_presente", False),
                ]
            )

        return jsonify(
            {
                "tsc_connected": system_status.get("tsc_connected", False),
                "playback_active": bokeh_playback_active,
                "data_points": data_points,
                "timestamp": datetime.now().isoformat(),
                "telemetry_source": system_status.get("telemetry_source", "unknown"),
                "brake_pressure_present": brake_pressure_present,
                # Exponer flags de presencia individuales para verificación rápida
                "presion_tubo_freno_presente": last_telemetry.get("presion_tubo_freno_presente", False) if last_telemetry else False,
                "presion_tubo_freno_mostrada_presente": last_telemetry.get("presion_tubo_freno_mostrada_presente", False) if last_telemetry else False,
                "presion_freno_loco_presente": last_telemetry.get("presion_freno_loco_presente", False) if last_telemetry else False,
                "presion_freno_loco_mostrada_presente": last_telemetry.get("presion_freno_loco_mostrada_presente", False) if last_telemetry else False,
                "presion_freno_tren_presente": last_telemetry.get("presion_freno_tren_presente", False) if last_telemetry else False,
                "posicion_freno_tren_presente": last_telemetry.get("posicion_freno_tren_presente", False) if last_telemetry else False,
                "presion_freno_tren_inferida": last_telemetry.get("presion_freno_tren_inferida", False) if last_telemetry else False,
                "presion_freno_loco_avanzada_presente": last_telemetry.get("presion_freno_loco_avanzada_presente", False) if last_telemetry else False,
                "presion_deposito_principal_presente": last_telemetry.get("presion_deposito_principal_presente", False) if last_telemetry else False,
                "eq_reservoir_presente": last_telemetry.get("eq_reservoir_presente", False) if last_telemetry else False,
                "presion_deposito_auxiliar_presente": last_telemetry.get("presion_deposito_auxiliar_presente", False) if last_telemetry else False,
                "presion_tubo_freno_cola_presente": last_telemetry.get("presion_tubo_freno_cola_presente", False) if last_telemetry else False,
                # Información del plugin Lua (si está disponible)
                "autopilot_plugin_loaded": tsc_integration.is_autopilot_plugin_loaded() if tsc_integration else False,
                "autopilot_plugin_state": tsc_integration.get_autopilot_plugin_state() if tsc_integration else None,
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "tsc_connected": False,
                    "playback_active": False,
                    "data_points": 0,
                    "error": str(e),
                }
            ),
            500,
        )


@app.route('/api/commands', methods=['POST'])
def api_commands():
    """Endpoint para encolar comandos para el simulador.

    JSON esperado:
    {
        "type": "set_regulator",
        "value": 0.4,
        "wait_for_ack": true,  # opcional (default: false)
        "timeout": 5.0,       # opcional
        "retries": 3          # opcional
    }

    Si `wait_for_ack` es true, el endpoint esperará hasta `timeout`
    por un ACK y devolverá 200 con el ACK si lo recibe, o 504/500 si falla.
    Si `wait_for_ack` es false, devolverá 202 Accepted inmediatamente.
    """
    global tsc_integration
    try:
        payload = request.get_json() or {}
        wait_for_ack_flag = bool(payload.get('wait_for_ack', False))
        timeout = float(payload.get('timeout', 5.0))
        retries = int(payload.get('retries', 0))

        # Determine plugins directory from TSCIntegration
        if tsc_integration:
            plugins_dir = os.path.dirname(tsc_integration.ruta_archivo_comandos)
        else:
            # fallback to local plugins dir
            plugins_dir = os.path.abspath('./plugins')
            os.makedirs(plugins_dir, exist_ok=True)

        # If not waiting for ack, just write atomically and return 202
        if not wait_for_ack_flag:
            if atomic_write_cmd is None:
                return (
                    jsonify(
                        {"status": "error", "error": "atomic command writer unavailable"}
                    ),
                    503,
                )
            cmd_id = atomic_write_cmd(plugins_dir, payload)
            return jsonify({"status": "queued", "id": cmd_id}), 202

        # else, send with retries and wait for ack
        if send_command_with_retries is None:
            return (
                jsonify({"status": "error", "error": "ACK sender unavailable"}),
                503,
            )
        ack = send_command_with_retries(plugins_dir, payload, timeout=timeout, retries=retries)
        if ack is not None:
            return jsonify({"status": "applied", "ack": ack}), 200
        else:
            return jsonify({"status": "failed", "error": "no ACK received"}), 504
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/control/<action>", methods=["POST"])
def control_action(action):
    """API para controlar el sistema."""
    print(f"Control action received: {action}")
    global autopilot_system
    try:
        allowed_actions = [
            "start_autopilot",
            "stop_autopilot",
            "start_predictive",
            "stop_predictive",
            "train_model",
            "toggle_doors",
            "toggle_lights",
            "emergency_brake",
            "toggle_performance",
        ]

        if action not in allowed_actions:
            return jsonify({"success": False, "error": f"Acción no permitida: {action}"}), 400

        if action == "start_autopilot":
            # Lógica para iniciar piloto automático
            if autopilot_system:
                try:
                    autopilot_system.start()
                    autopilot_system.activar_modo_automatico()  # Activar modo automático
                    system_status["autopilot_active"] = True
                    socketio.emit(
                        "system_message",
                        {"message": "Piloto automático iniciado", "type": "success"},
                    )
                    # Determinar si el cliente pidió esperar por ACK (por defecto: True)
                    payload = request.get_json(silent=True) or {}
                    wait_for_ack = bool(payload.get("wait_for_ack", True))

                    # Intentar confirmar estado desde el plugin Lua
                    plugin_state = None
                    try:
                        if tsc_integration:
                            # Primer intento: comprobar estado actual
                            plugin_state = tsc_integration.get_autopilot_plugin_state()
                            # Si no hay ack inmediato y el cliente quiere esperar, hacerlo con timeout configurado
                            if plugin_state is None and wait_for_ack:
                                if tsc_integration.wait_for_autopilot_state("on", timeout=AUTOPILOT_ACK_TIMEOUT):
                                    plugin_state = "on"
                                else:
                                    # No llegó ACK en tiempo: registrar métrica y responder con 504 (Gateway Timeout)
                                    try:
                                        autopilot_metrics["unacked_total"] += 1
                                    except Exception:
                                        pass
                                    return (
                                        jsonify(
                                            {
                                                "success": False,
                                                "error": "Autopilot plugin did not confirm start within timeout",
                                                "action": action,
                                            }
                                        ),
                                        504,
                                    )
                    except Exception:
                        plugin_state = None

                    return jsonify({"success": True, "action": action, "autopilot_plugin_state": plugin_state})
                except Exception as e:
                    return (
                        jsonify(
                            {"success": False, "error": f"Error iniciando autopilot: {str(e)}"}
                        ),
                        500,
                    )
            else:
                return (
                    jsonify({"success": False, "error": "Sistema autopilot no inicializado"}),
                    500,
                )

                return (
                    jsonify({"success": False, "error": "Sistema autopilot no inicializado"}),
                    500,
                )

        elif action == "stop_autopilot":
            # Lógica para detener piloto automático
            if autopilot_system:
                try:
                    autopilot_system.stop()
                    system_status["autopilot_active"] = False
                    socketio.emit(
                        "system_message",
                        {"message": "Piloto automático detenido", "type": "info"},
                    )
                    # Intentar confirmar estado desde el plugin Lua
                    plugin_state = None
                    try:
                        if tsc_integration:
                            plugin_state = tsc_integration.get_autopilot_plugin_state()
                            if plugin_state is None and tsc_integration.wait_for_autopilot_state("off", timeout=2.0):
                                plugin_state = "off"
                    except Exception:
                        plugin_state = None

                    return jsonify({"success": True, "action": action, "autopilot_plugin_state": plugin_state})
                except Exception as e:
                    return (
                        jsonify(
                            {"success": False, "error": f"Error deteniendo autopilot: {str(e)}"}
                        ),
                        500,
                    )
            else:
                return (
                    jsonify({"success": False, "error": "Sistema autopilot no inicializado"}),
                    500,
                )

        elif action == "start_predictive":
            # Iniciar análisis predictivo
            if predictive_analyzer and not predictive_analyzer.is_running:
                predictive_analyzer.start_analysis()
                system_status["predictive_active"] = True
                socketio.emit(
                    "system_message",
                    {"message": "Análisis predictivo iniciado", "type": "success"},
                )
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Analizador predictivo no disponible o ya ejecutándose",
                        }
                    ),
                    400,
                )

        elif action == "stop_predictive":
            # Detener análisis predictivo
            if predictive_analyzer and predictive_analyzer.is_running:
                predictive_analyzer.stop_analysis()
                system_status["predictive_active"] = False
                socketio.emit(
                    "system_message",
                    {"message": "Análisis predictivo detenido", "type": "info"},
                )
            else:
                return (
                    jsonify({"success": False, "error": "Analizador predictivo no ejecutándose"}),
                    400,
                )

        elif action == "toggle_performance":
            # Toggle performance monitoring
            try:
                if performance_monitor.is_monitoring:
                    performance_monitor.stop_monitoring()
                    system_status["performance_monitoring"] = False
                    socketio.emit(
                        "system_message",
                        {"message": "Monitor de rendimiento detenido", "type": "info"},
                    )
                else:
                    performance_monitor.start_monitoring()
                    system_status["performance_monitoring"] = True
                    socketio.emit(
                        "system_message",
                        {"message": "Monitor de rendimiento iniciado", "type": "success"},
                    )

                return jsonify({"success": True, "performance_monitoring": system_status["performance_monitoring"]})
            except Exception as e:
                return (
                    jsonify({"success": False, "error": f"Error toggling performance monitor: {e}"}),
                    500,
                )

        elif action == "train_model":
            # Entrenar modelo predictivo
            if predictive_analyzer:
                metrics = predictive_analyzer.train_model()
                if "error" in metrics:
                    socketio.emit(
                        "system_message",
                        {
                            "message": f'Error entrenando modelo: {metrics["error"]}',
                            "type": "error",
                        },
                    )
                    return jsonify({"success": False, "error": metrics["error"]}), 500
                else:
                    socketio.emit(
                        "system_message",
                        {"message": "Modelo entrenado exitosamente", "type": "success"},
                    )
            else:
                return (
                    jsonify({"success": False, "error": "Analizador predictivo no disponible"}),
                    400,
                )

        # Doors control removed: IA will handle door operations in future

        elif action == "toggle_lights":
            # Alternar luces
            if tsc_integration:
                try:
                    # Alternar estado
                    control_states["lights_on"] = not control_states["lights_on"]
                    command = "lights_on" if control_states["lights_on"] else "lights_off"

                    success = tsc_integration.enviar_comandos({"command": command})
                    if success:
                        status_msg = (
                            "Luces ENCENDIDAS" if control_states["lights_on"] else "Luces APAGADAS"
                        )
                        socketio.emit(
                            "system_message",
                            {"message": f"Comando enviado: {status_msg}", "type": "info"},
                        )
                    else:
                        return (
                            jsonify({"success": False, "error": "Error enviando comando de luces"}),
                            500,
                        )
                except Exception as e:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"Error enviando comando de luces: {str(e)}",
                            }
                        ),
                        500,
                    )
            else:
                return jsonify({"success": False, "error": "Sistema TSC no inicializado"}), 500

        elif action == "emergency_brake":
            # Freno de emergencia
            if tsc_integration:
                try:
                    success = tsc_integration.enviar_comandos({"command": "emergency_brake"})
                    if success:
                        socketio.emit(
                            "system_message",
                            {"message": "¡FRENO DE EMERGENCIA ACTIVADO!", "type": "danger"},
                        )
                    else:
                        return (
                            jsonify(
                                {"success": False, "error": "Error enviando freno de emergencia"}
                            ),
                            500,
                        )
                except Exception as e:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"Error enviando freno de emergencia: {str(e)}",
                            }
                        ),
                        500,
                    )
            else:
                return jsonify({"success": False, "error": "Sistema TSC no inicializado"}), 500

        return jsonify({"success": True, "action": action})

    except Exception as e:
        print(f"[ERROR] Error en control_action '{action}': {e}")
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}"}), 500


def send_tsc_command(command_name, value):
    """Enviar comando directo al TSC."""
    try:
        from tsc_integration import TSCIntegration

        tsc = TSCIntegration()
        comandos = {command_name: value}
        return tsc.enviar_comandos(comandos)
    except Exception as e:
        print(f"[ERROR] Error enviando comando TSC {command_name}={value}: {e}")
        return False


@app.route("/api/control/set", methods=["POST"])
def control_set():
    """Set a control value on the train via TSCIntegration.

    Expected JSON body: {"control": "Regulator", "value": 0.5}
    The `control` name can be either a RailDriver control or a supported Spanish alias defined in the TSCIntegration mapping.
    """
    try:
        try:
            payload = request.get_json(silent=True) or {}
        except TypeError:
            # Some test stubs implement get_json() without keyword args
            try:
                payload = request.get_json() or {}
            except Exception:
                return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        except Exception:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        control = payload.get("control")
        value = payload.get("value")
        if not control or value is None:
            logger.warning("control_set: invalid payload: control=%s (%s) value=%s (%s)", control, type(control), value, type(value))
            return jsonify({"success": False, "error": "Invalid payload, expected 'control' and 'value'"}), 400

        # Validate control name to prevent injection into file-based command protocol.
        # Reject control names containing ':' or control characters like newlines or NUL.
        if not isinstance(control, str):
            logger.warning("control_set: control name not a string: %r", control)
            return jsonify({"success": False, "error": "Invalid control name"}), 400
        forbidden = {":", "\n", "\r", "\x00"}
        if any(ch in control for ch in forbidden) or not control.isprintable() or len(control) > 100:
            logger.warning("control_set: rejected control name with forbidden characters: %r", control)
            return jsonify({"success": False, "error": "Invalid control name"}), 400

        # Use TSCIntegration to map and write control commands
        if tsc_integration is None:
            return jsonify({"success": False, "error": "TSC integration not available"}), 500

        ok = tsc_integration.enviar_comandos({control: value})
        if ok:
            return jsonify({"success": True, "control": control, "value": value}), 200
        else:
            return jsonify({"success": False, "error": "Failed to send command to TSC"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Eventos WebSocket
@socketio.on("connect")
def handle_connect():
    """Manejar conexión de cliente WebSocket."""
    sid = getattr(request, "sid", "unknown")  # type: ignore
    print(f"[WS] Cliente conectado: {sid}")
    print(
        f"[DEBUG] Estado del sistema: predictive_running={predictive_analyzer.is_running if predictive_analyzer else False}"
    )
    try:
        emit("system_message", {"message": "Conectado al dashboard", "type": "success"})
        print(f"[WS] Mensaje de bienvenida enviado a {sid}")
    except Exception as e:
        print(f"[WS] Error enviando mensaje de bienvenida: {e}")
        import traceback

        traceback.print_exc()


@socketio.on("disconnect")
def handle_disconnect():
    """Manejar desconexión de cliente WebSocket."""
    sid = getattr(request, "sid", "unknown")  # type: ignore
    print(f"[WS] Cliente desconectado: {sid}")


@socketio.on("request_telemetry")
def handle_telemetry_request():
    """Manejar solicitud de telemetría."""
    print("[WS] Solicitud de telemetria recibida")
    try:
        # Comprimir datos antes de enviar
        compressed_telemetry = (
            data_compressor.compress_data(last_telemetry) if last_telemetry else {}
        )

        emit(
            "telemetry_update",
            {
                "telemetry": compressed_telemetry,
                "predictions": (
                    predictive_analyzer.get_current_predictions() if predictive_analyzer else {}
                ),
                "multi_loco": (
                    multi_loco_integration.leer_datos_todas_locomotoras()
                    if multi_loco_integration
                    else {}
                ),
                "system_status": system_status,
                "active_alerts": check_alerts(),
                "performance": (
                    performance_monitor.get_performance_report()
                    if performance_monitor
                    else {}
                ),
                "reports": get_automated_reports().get_reports_status(),
            },
        )
        print("[WS] Respuesta de telemetria enviada")
    except Exception as e:
        print(f"[WS] Error en solicitud de telemetria: {e}")


@app.route("/bokeh")


@app.route('/api/control/retry_autopilot', methods=['POST'])
def retry_autopilot():
    """Endpoint para reintentar iniciar Autopilot sin esperar por ACK.

    - Incrementa un contador de reintentos
    - Envía comando de inicio y devuelve el estado conocido del plugin (no espera ACK)
    """
    global autopilot_metrics
    try:
        if not autopilot_system:
            return jsonify({"success": False, "error": "Sistema autopilot no inicializado"}), 500

        # Incrementar contador de reintentos
        try:
            autopilot_metrics["retry_total"] += 1
        except Exception:
            pass

        # Forzar start sin esperar ACK
        try:
            autopilot_system.start()
            autopilot_system.activar_modo_automatico()
            # Intentar leer estado conocido del plugin (no esperar)
            plugin_state = None
            if tsc_integration:
                plugin_state = tsc_integration.get_autopilot_plugin_state()
            return jsonify({"success": True, "action": "retry_autopilot", "autopilot_plugin_state": plugin_state}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
def bokeh_dashboard():
    """Servir el dashboard interactivo de Bokeh."""
    try:
        if bokeh_port is None:
            return "Servidor Bokeh no disponible. Reinicie el dashboard.", 503

        # Usar server_document para integrar Bokeh con Flask
        script = server_document(f"http://localhost:{bokeh_port}/bokeh_dashboard")

        return render_template(
            "bokeh_dashboard.html",
            bokeh_script=script,
            title="Dashboard Bokeh - Train Simulator Autopilot",
        )

    except Exception as e:
        print(f"[BOKEH] Error al cargar dashboard Bokeh: {e}")
        return f"Error al cargar dashboard Bokeh: {str(e)}", 500


# ==================== ENDPOINTS DE ALERTAS ====================


@app.route("/api/alerts/status")
def get_alerts_status():
    """Obtener estado actual del sistema de alertas"""
    try:
        alert_system = get_alert_system()
        status = alert_system.get_alerts_summary()
        active_alerts = alert_system.get_active_alerts()

        return jsonify(
            {
                "success": True,
                "status": status,
                "active_alerts": [alert.to_dict() for alert in active_alerts[:10]],  # Últimas 10
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/alerts/check", methods=["POST"])
def check_alerts_endpoint():
    """Ejecutar verificación manual de alertas"""
    try:
        result = check_alerts()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/alerts/acknowledge/<alert_id>", methods=["POST"])
def acknowledge_alert(alert_id):
    """Marcar alerta como reconocida"""
    try:
        alert_system = get_alert_system()
        success = alert_system.acknowledge_alert(alert_id)

        if success:
            return jsonify({"success": True, "message": f"Alerta {alert_id} reconocida"})
        else:
            return jsonify({"success": False, "error": "Alerta no encontrada o ya reconocida"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/alerts/start_monitoring", methods=["POST"])
def start_alert_monitoring():
    """Iniciar monitoreo continuo de alertas"""
    try:
        alert_system = get_alert_system()
        alert_system.start_monitoring(interval_seconds=30)
        return jsonify({"success": True, "message": "Monitoreo de alertas iniciado"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/alerts/stop_monitoring", methods=["POST"])
def stop_alert_monitoring():
    """Detener monitoreo continuo de alertas"""
    try:
        alert_system = get_alert_system()
        alert_system.stop_monitoring()
        return jsonify({"success": True, "message": "Monitoreo de alertas detenido"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ENDPOINTS DE REPORTES AUTOMÁTICOS ====================


@app.route("/api/reports/status")
def get_reports_status():
    """Obtener estado del sistema de reportes automáticos"""
    try:
        reports_system = get_automated_reports()
        status = reports_system.get_reports_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reports/generate/<report_type>", methods=["POST"])
def generate_report_endpoint(report_type):
    """Generar reporte manualmente"""
    try:
        allowed_types = ["daily", "weekly", "monthly", "performance", "alerts"]

        if report_type not in allowed_types:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Tipo de reporte inválido: {report_type}. Tipos permitidos: {', '.join(allowed_types)}",
                    }
                ),
                400,
            )

        result = generate_report(report_type)

        if result and "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 500

        return jsonify({"success": True, "data": result})
    except Exception as e:
        print(f"[ERROR] Error generando reporte '{report_type}': {e}")
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}"}), 500


@app.route("/api/reports/start_automation", methods=["POST"])
def start_reports_automation():
    """Iniciar automatización de reportes"""
    try:
        reports_system = get_automated_reports()
        reports_system.start_automation()
        return jsonify({"success": True, "message": "Automatización de reportes iniciada"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reports/stop_automation", methods=["POST"])
def stop_reports_automation():
    """Detener automatización de reportes"""
    try:
        reports_system = get_automated_reports()
        reports_system.stop_automation()
        return jsonify({"success": True, "message": "Automatización de reportes detenida"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ENDPOINTS DE OPTIMIZACIÓN - FASE 4 ====================


@app.route("/api/optimize/performance", methods=["POST"])
def apply_performance_optimizations():
    """Aplicar optimizaciones de rendimiento."""
    try:
        results = optimize_dashboard_performance()

        if results and "error" in results:
            return jsonify({"success": False, "error": results["error"]}), 500

        return jsonify({"success": True, "results": results})
    except Exception as e:
        print(f"[ERROR] Error aplicando optimizaciones de rendimiento: {e}")
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}"}), 500


@app.route("/api/optimize/stats")
def get_optimization_stats():
    """Obtener estadísticas de optimizaciones."""
    try:
        from performance_monitor import latency_optimizer, smart_cache

        cache_stats = smart_cache.get_stats()
        latency_stats = latency_optimizer.get_latency_report()

        return jsonify(
            {
                "success": True,
                "cache": cache_stats,
                "latency": latency_stats,
                "compression_enabled": data_compressor.compression_enabled,
            }
        )
    except ImportError as e:
        print(f"[ERROR] Error importando módulos de optimización: {e}")
        return jsonify({"success": False, "error": "Módulos de optimización no disponibles"}), 503
    except Exception as e:
        print(f"[ERROR] Error obteniendo estadísticas de optimización: {e}")
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}"}), 500


@app.route("/api/optimize/compression/toggle", methods=["POST"])
def toggle_compression():
    """Activar/desactivar compresión de datos."""
    try:
        data = request.get_json() or {}
        enabled = data.get("enabled", True)

        if not isinstance(enabled, bool):
            return (
                jsonify(
                    {"success": False, "error": "El parámetro 'enabled' debe ser un valor booleano"}
                ),
                400,
            )

        data_compressor.compression_enabled = enabled

        return jsonify(
            {"success": True, "compression_enabled": data_compressor.compression_enabled}
        )
    except Exception as e:
        print(f"[ERROR] Error cambiando estado de compresión: {e}")
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}"}), 500


@app.route("/api/autobrake/status")
def get_autobrake_status():
    """Obtener estado actual de autobrake_by_signal desde config cargado en runtime."""
    try:
        return jsonify({"autobrake_by_signal": system_status.get("autobrake_by_signal", True)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/autobrake", methods=["POST"])
def set_autobrake_status():
    """Habilitar o deshabilitar autobrake_by_signal en el archivo de configuración.

    Body: { "enabled": true }
    """
    try:
        data = request.get_json() or {}
        enabled = data.get("enabled", None)

        if enabled is None or not isinstance(enabled, bool):
            return jsonify({"success": False, "error": "El campo 'enabled' debe ser booleano"}), 400

        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        if os.path.exists(config_path):
            config.read(config_path, encoding="utf-8")
        if not config.has_section("TSC_INTEGRATION"):
            config.add_section("TSC_INTEGRATION")
        config.set("TSC_INTEGRATION", "autobrake_by_signal", str(enabled).lower())
        with open(config_path, "w", encoding="utf-8") as cf:
            config.write(cf)

        # Aplicar al runtime en memoria
        system_status["autobrake_by_signal"] = enabled
        if autopilot_system:
            try:
                autopilot_system.autobrake_by_signal = enabled
            except Exception:
                pass

        socketio.emit(
            "system_message", {"message": f"autobrake_by_signal set to {enabled}", "type": "info"}
        )
        return jsonify({"success": True, "autobrake_by_signal": enabled})
    except Exception as e:
        print(f"[ERROR] Error setting autobrake: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@socketio.on("toggle_autobrake_by_signal")
def handle_toggle_autobrake(payload):
    """Socket event to toggle autobrake option. Payload: { enabled: true }"""
    try:
        enabled = payload.get("enabled") if isinstance(payload, dict) else None
        if not isinstance(enabled, bool):
            emit(
                "system_message",
                {"message": "Invalid payload for toggle_autobrake_by_signal", "type": "danger"},
            )
            return

        # Reuse endpoint logic to persist setting
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        if os.path.exists(config_path):
            config.read(config_path, encoding="utf-8")
        if not config.has_section("TSC_INTEGRATION"):
            config.add_section("TSC_INTEGRATION")
        config.set("TSC_INTEGRATION", "autobrake_by_signal", str(enabled).lower())
        with open(config_path, "w", encoding="utf-8") as cf:
            config.write(cf)

        system_status["autobrake_by_signal"] = enabled
        if autopilot_system:
            try:
                autopilot_system.autobrake_by_signal = enabled
            except Exception:
                pass

        emit(
            "system_message",
            {"message": f"autobrake_by_signal set to {enabled}", "type": "success"},
        )
        # Broadcast to all connected clients
        socketio.emit("autobrake_status", {"autobrake_by_signal": enabled})
    except Exception as e:
        emit("system_message", {"message": f"Error toggling autobrake: {e}", "type": "danger"})


@app.route("/api/metrics/dashboard")
def get_dashboard_metrics():
    """Obtener métricas detalladas del dashboard."""
    try:
        from performance_monitor import performance_monitor

        # Obtener métricas del monitor de rendimiento
        perf_report = (
            performance_monitor.get_performance_report()
            if performance_monitor
            else {}
        )

        # Calcular métricas adicionales
        uptime = time.time() - (globals().get("start_time", time.time()))
        # Calcular conexiones activas de manera segura
        server = getattr(socketio, "server", None)
        eio = getattr(server, "eio", None) if server else None
        sockets = getattr(eio, "sockets", {}) if eio else {}
        active_connections = len(sockets) if isinstance(sockets, dict) else 0

        metrics = {
            "uptime_seconds": uptime,
            "uptime_formatted": f"{int(uptime // 3600):02d}:{int((uptime % 3600) // 60):02d}:{int(uptime % 60):02d}",
            "telemetry_updates": system_status.get("telemetry_updates", 0),
            "active_connections": active_connections,
            "system_status": system_status,
            "performance": perf_report,
            "memory_usage": (
                {
                    "rss": psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                    "vms": psutil.Process().memory_info().vms / 1024 / 1024,  # MB
                    "percent": psutil.Process().memory_percent(),
                }
                if PSUTIL_AVAILABLE and psutil
                else None
            ),
        }

        return jsonify({"success": True, "metrics": metrics})

    except ImportError as e:
        print(f"[ERROR] Error importando módulos para métricas: {e}")
        return jsonify({"success": False, "error": "Módulos de métricas no disponibles"}), 503
    except Exception as e:
        print(f"[ERROR] Error obteniendo métricas del dashboard: {e}")
        logger.exception("Error collecting dashboard metrics: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/metrics/io")
def get_io_metrics_endpoint():
    """Endpoint que devuelve métricas I/O del TSC Integration (lectura/escritura)."""
    try:
        if tsc_integration:
            return jsonify({"tsc_io_metrics": tsc_integration.get_io_metrics()}), 200
        else:
            return jsonify({"error": "TSC integration not configured"}), 200
    except Exception as e:
        logger.exception("Error obtaining I/O metrics: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route('/metrics')
def prometheus_metrics_endpoint():
    """Export simple Prometheus text metrics (no depende de prometheus_client).

    Exponemos métricas de I/O del TSC integration y métricas básicas del dashboard.
    Formato: texto plano compatible con el colector Prometheus (type=gauge).
    """
    try:
        lines = []
        # TSC I/O metrics
        io = tsc_integration.get_io_metrics() if tsc_integration else {}
        for k, v in io.items():
            name = f"tsc_io_{k}"
            lines.append(f"# HELP {name} TSC I/O metric {k}")
            lines.append(f"# TYPE {name} gauge")
            # Ensure numeric formatting
            try:
                val = float(v)
            except Exception:
                val = 0.0
            lines.append(f"{name} {val}")
        # Alert system metrics (if available)
        try:
            if alert_system:
                a_metrics = getattr(alert_system, "metrics", {})
                for k, v in a_metrics.items():
                    name = f"alerts_{k}"
                    lines.append(f"# HELP {name} Alert system metric {k}")
                    lines.append(f"# TYPE {name} gauge")
                    try:
                        val = float(v)
                    except Exception:
                        val = 0.0
                    lines.append(f"{name} {val}")
        except Exception:
            # Intentionally ignore errors while collecting alert system metrics.
            # The alert system may be uninitialized or return non-numeric values; we
            # prefer to continue returning other metrics rather than failing the
            # whole /metrics endpoint for a non-critical subsystem.
            pass

        # Autopilot IA metrics (if available)
        try:
            if autopilot_system and getattr(autopilot_system, "ia", None):
                ia_metrics = getattr(autopilot_system.ia, "metrics", {})
                for k, v in ia_metrics.items():
                    name = f"autopilot_ia_{k}"
                    lines.append(f"# HELP {name} Autopilot IA metric {k}")
                    lines.append(f"# TYPE {name} gauge")
                    try:
                        val = float(v)
                    except Exception:
                        val = 0.0
                    lines.append(f"{name} {val}")
        except Exception:
            # Intentionally ignore errors while collecting IA metrics (e.g., IA not initialized
            # or unexpected metric types). We do not want a problem in metrics collection to
            # make the /metrics endpoint fail. Log at debug level so we can diagnose if
            # unexpected errors become frequent in user environments.
            logger.debug("Ignoring exception while collecting IA metrics", exc_info=True)
            pass

        # Dashboard uptime
        uptime = time.time() - globals().get("start_time", time.time())
        lines.append("# HELP dashboard_uptime_seconds Uptime of dashboard in seconds")
        lines.append("# TYPE dashboard_uptime_seconds gauge")
        lines.append(f"dashboard_uptime_seconds {uptime}")

        # Autopilot plugin metrics (reintentos y ACKs faltantes)
        try:
            am = globals().get("autopilot_metrics", {})
            for k, v in am.items():
                name = f"autopilot_plugin_{k}"
                lines.append(f"# HELP {name} Autopilot plugin metric {k}")
                lines.append(f"# TYPE {name} gauge")
                try:
                    val = float(v)
                except Exception:
                    val = 0.0
                lines.append(f"{name} {val}")
        except Exception:
            # Intentionally ignore errors while collecting autopilot plugin metrics to
            # ensure /metrics remains available even if plugin metrics are malformed.
            pass

        # Exponer estado del plugin como métric gauge (1 = on, 0 = off/unknown)
        try:
            plugin_state = None
            if tsc_integration:
                plugin_state = tsc_integration.get_autopilot_plugin_state()
            state_val = 1.0 if plugin_state == "on" else 0.0
            lines.append("# HELP autopilot_plugin_state_up 1 if autopilot plugin reports 'on'")
            lines.append("# TYPE autopilot_plugin_state_up gauge")
            lines.append(f"autopilot_plugin_state_up {state_val}")
        except Exception:
            pass

        body = "\n".join(lines) + "\n"
        return Response(body, mimetype="text/plain; version=0.0.4")
    except Exception as e:
        logger.exception("Error producing prometheus metrics: %s", e)
        return Response("", status=500, mimetype="text/plain")


def start_bokeh_server():
    """Iniciar el servidor Bokeh en un hilo separado."""
    try:
        import threading

        from bokeh.application import Application
        from bokeh.application.handlers.function import FunctionHandler
        from bokeh.server.server import Server

        from bokeh_dashboard import create_bokeh_app

        print("[BOKEH] Iniciando servidor Bokeh...")

        # Intentar diferentes puertos si el 5006 está ocupado
        ports_to_try = [5006, 5007, 5008, 5009]
        server = None

        for port in ports_to_try:
            try:
                # Crear la aplicación Bokeh
                handler = FunctionHandler(create_bokeh_app())
                app_bokeh = Application(handler)

                # Crear y configurar el servidor
                server = Server(
                    {"/bokeh_dashboard": app_bokeh},
                    port=port,
                    allow_websocket_origin=[
                        "localhost:5001",
                        "127.0.0.1:5001",
                        "localhost:5000",
                        "127.0.0.1:5000",
                    ],
                )
                print(f"[BOKEH] Servidor Bokeh creado en puerto {port}")
                break
            except Exception as port_error:
                print(f"[BOKEH] Puerto {port} ocupado, intentando siguiente... {port_error}")
                continue

        if server is None:
            print(
                "[BOKEH] No se pudo iniciar servidor Bokeh en ningun puerto disponible. Continuando sin Bokeh."
            )
            return

        # Iniciar el servidor en un hilo separado para no bloquear
        def run_server():
            try:
                print(f"[BOKEH] Ejecutando servidor Bokeh en puerto {port}...")
                # Desactivar señales para evitar problemas en hilos
                import signal

                original_signal = signal.signal
                signal.signal = lambda signum, handler: None  # no-op
                try:
                    server.run_until_shutdown()
                finally:
                    signal.signal = original_signal
                print("[BOKEH] Servidor Bokeh terminado")
            except Exception as e:
                print(f"[BOKEH] Error ejecutando servidor Bokeh: {e}")

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        print(f"[BOKEH] Servidor Bokeh iniciado en puerto {port}")

        # Almacenar el puerto para uso en rutas
        global bokeh_port
        bokeh_port = port

    except Exception as e:
        print(f"[BOKEH] Error iniciando servidor Bokeh: {e}")
        import traceback

        traceback.print_exc()
        print("[BOKEH] Continuando sin servidor Bokeh...")


def start_dashboard(host="127.0.0.1", port=5001):
    """Iniciar el dashboard web."""
    global dashboard_active, telemetry_thread

    # Si estamos en CI, enlazamos en 0.0.0.0 para que contenedores (Prometheus)
    # puedan acceder al servicio del runner.
    effective_host = host
    # If running in CI or when ALLOW_UNSAFE_WERKZEUG is enabled, bind to 0.0.0.0
    # so containers (Prometheus) can access the service on the runner host.
    if os.getenv("CI", "").lower() == "true" or os.getenv("ALLOW_UNSAFE_WERKZEUG", "").lower() in ("1", "true", "yes"):
        effective_host = "0.0.0.0"

    print("[START] Iniciando Train Simulator Autopilot Dashboard...")
    print(f"[WEB] Servidor web en http://{effective_host}:{port}")
    print(f"[LOG] Host: {effective_host}, Port: {port}")
    print(f"[LOG] Directorio actual: {os.getcwd()}")
    print(f"[LOG] Python executable: {sys.executable}")
    print(f"[LOG] Python version: {sys.version}")
    print("=" * 60)

    # Inicializar sistema
    logger.info("Iniciando inicialización del sistema...")
    if not initialize_system():
        logger.error("Error inicializando sistema. Saliendo...")
        return False
    logger.info("Sistema inicializado correctamente")

    # Iniciar servidor Bokeh en hilo separado (no bloqueante)
    logger.info("Iniciando servidor Bokeh en background...")
    bokeh_thread = threading.Thread(target=start_bokeh_server, daemon=True)
    bokeh_thread.start()
    print("[BOKEH] Hilo de Bokeh iniciado")

    # Iniciar dashboard inmediatamente
    print("[DASHBOARD] Iniciando dashboard...")
    dashboard_active = True
    telemetry_thread = threading.Thread(target=telemetry_update_loop, daemon=True)
    telemetry_thread.start()
    print("[DASHBOARD] Hilo de telemetría iniciado")

    print("[OK] Dashboard iniciado exitosamente")
    print("[DATA] Telemetria actualizandose cada 100ms")
    print("[LINK] Abre tu navegador en la URL mostrada arriba")
    print("=" * 60)

    try:
        print("[SERVER] Iniciando servidor SocketIO...")
        print(f"[SERVER] Configuración: host={effective_host}, port={port}")
        print(f"[SERVER] App configurada: {app is not None}")
        print(f"[SERVER] SocketIO configurado: {socketio is not None}")

        # Verificar que las rutas están registradas
        logger.info(f"Rutas registradas: {len(app.url_map._rules)}")

        # Permitir el uso de Werkzeug explícitamente en CI o cuando se requiera
        allow_unsafe = os.getenv("ALLOW_UNSAFE_WERKZEUG", "").lower() in ("1", "true", "yes")
        # GitHub Actions sets CI=true automatically; respetamos ese caso también
        allow_unsafe = allow_unsafe or os.getenv("CI", "").lower() == "true"
        if allow_unsafe:
            logger.warning("allow_unsafe_werkzeug enabled via ALLOW_UNSAFE_WERKZEUG or CI environment")

        logger.info("Ejecutando socketio.run()...")
        # Use the computed effective_host (may be 0.0.0.0 in CI or when ALLOW_UNSAFE_WERKZEUG is set)
        socketio.run(app, host=effective_host, port=port, debug=False, allow_unsafe_werkzeug=allow_unsafe)
        logger.debug("Servidor SocketIO terminó normalmente")
    except KeyboardInterrupt:
        logger.info("Dashboard detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en servidor SocketIO: {e}")
        import traceback

        traceback.print_exc()
    finally:
        logger.debug(f"Entrando al finally - dashboard_active={dashboard_active}")
        dashboard_active = False
        if predictive_analyzer:
            print(
                f"[DEBUG] Deteniendo analizador predictivo - is_running={predictive_analyzer.is_running}"
            )
            predictive_analyzer.stop_analysis()

        # Detener monitoreo de rendimiento y guardar reporte
        print("[PERF] Deteniendo monitoreo de rendimiento...")
        performance_monitor.stop_monitoring()
        performance_monitor.save_report()

        print("[CLOSED] Dashboard cerrado")

    return True


if __name__ == "__main__":
    start_dashboard()
