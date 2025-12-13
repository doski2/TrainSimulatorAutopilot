# 🚂 Train Simulator Autopilot

Sistema de piloto automático inteligente para Train Simulator Classic
con capacidades predictivas avanzadas.

<!-- markdownlint-disable MD013 -->
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-9.0+-green.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
<!-- markdownlint-enable MD013 -->

## 📋 Descripción

El **Train Simulator Autopilot** es un sistema avanzado de piloto automático que
utiliza inteligencia artificial y análisis predictivo para controlar trenes en
Train Simulator Classic. El sistema integra:

- **Integración en tiempo real** con Train Simulator Classic
- **Análisis predictivo** de telemetría para optimización de conducción
- **Control adaptativo** basado en condiciones de vía y tren
- **Dashboard web** para monitoreo y control remoto
- **Sistema de seguridad** con múltiples capas de protección

## ✨ Características Principales

### 🤖 Inteligencia Artificial

- **Análisis predictivo** de velocidad, aceleración y eficiencia energética
- **Optimización automática** de parámetros de conducción
- **Aprendizaje adaptativo** basado en datos históricos
- **Detección de anomalías** en tiempo real

### 🎮 Integración con TSC

- **Lectura en tiempo real** de datos del simulador
- **Envío de comandos** de control al juego
- **Mapeo automático** de controles y señales
- **Soporte multi-locomotora** y configuraciones complejas

### 🌐 Dashboard Web

- **Interfaz intuitiva** para monitoreo del sistema
- **Gráficos en tiempo real** de telemetría
- **Control remoto** del piloto automático
- **Historial de conducción** y análisis de rendimiento

#### Dashboards Disponibles

El sistema incluye **tres dashboards completamente funcionales** con tecnologías
especializadas:

##### 🏠 **Dashboard Principal TypeScript** (Puerto 3000)

- **Tecnología**: Node.js + TypeScript + Express.js + Socket.IO
- **Características**:
  - Servidor robusto con APIs REST completas
  - WebSocket en tiempo real para telemetría
  - Interfaz moderna con Bootstrap 5 y Chart.js
  - 6 paneles funcionales: señalización, métricas, sistemas ACSES/PTC/ATC/CAB,
    controles
  - Configuración personalizable (4 temas, animaciones, intervalos)
- **APIs**: `/api/status`, `/api/data`, `/api/system/:name`, `/api/command`
- **WebSocket Events**: `telemetry`, `status`, `command`, `alert`
- **Estado**: ✅ **SISTEMA PRINCIPAL COMPLETAMENTE OPERATIVO**

##### 📊 **Dashboard Flask Secundario** (Puerto 5001)

- **Tecnología**: Python Flask + Bootstrap + Socket.IO
- **Características**:
  - Dashboard web responsive con métricas avanzadas
  - APIs REST con validación completa
  - WebSocket corregido y funcional
  - Endpoint de métricas: `/api/metrics/dashboard`
  - Manejo robusto de errores y logging detallado
- **Estado**: ✅ **SISTEMA SECUNDARIO COMPLETAMENTE OPERATIVO**

##### 🖥️ **Aplicación Electron Nativa**

- **Tecnología**: Electron + Chromium (interfaz nativa)
- **Características**:
  - Aplicación de escritorio sin navegador
  - Inicio automático con `start.bat`
  - Modo desarrollo con DevTools (`start_dev.bat`)
  - Integración completa con backend Flask
- **Estado**: ✅ **SISTEMA NATIVO COMPLETAMENTE OPERATIVO**

##### 📈 **Dashboards Analíticos Legacy**

- **Dashboard Bokeh Interactivo** (`/bokeh`): Visualización interactiva
  (mantenido por compatibilidad)
- **Dashboard Seaborn Analytics** (`/analytics`): Análisis estadístico avanzado
- **Dashboard SD 40-2**: Especializado para locomotoras SD 40-2

### ⚡ Optimizaciones de Rendimiento (FASE 4)

- **Compresión de datos**: Algoritmos RLE y diferencial (reducción hasta 20%+)
- **Cache inteligente**: LRU con TTL para datos predictivos
- **Optimización de latencia**: Batching y sampling de WebSockets
- **Validación cross-browser**: Compatibilidad con Chrome, Firefox, Edge, Safari
- **APIs de optimización**: `/api/optimize/performance`,
  `/api/optimize/compression/*`

### 🛡️ Sistema de Seguridad

- **Múltiples capas** de validación y verificación
- **Detección de condiciones peligrosas** (velocidad excesiva, deslizamiento)
- **Respuesta automática** a situaciones de emergencia
- **Registro completo** de eventos para auditoría

## 📚 Documentación

- **[Documentación completa](http://localhost:8001)** - Sitio MkDocs con guías
  detalladas
- **[Guía de instalación](INSTALLATION_GUIDE.md)** - Instrucciones paso a paso
- **[Arquitectura](docs/ARCHITECTURE.md)** - Diseño del sistema
- **[API Reference](docs/API_REFERENCE.md)** - Referencia completa de APIs
- **[Troubleshooting](docs/troubleshooting.md)** - Solución de problemas comunes

## 🚀 Instalación

### Prerrequisitos

- **Python 3.9+** (actualizado para compatibilidad)
- **Node.js 18+** y **npm** (para dashboard TypeScript)
- **Train Simulator Classic** instalado
- **Raildriver Interface** configurado (opcional pero recomendado)

### Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/train-simulator-autopilot.git
cd train-simulator-autopilot

# Ejecutar instalador automático
install.bat  # Windows
# ./install.sh  # Linux/Mac
```

### Instalación Manual Completa

```bash
# 1. Configurar Python
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configurar Node.js/TypeScript (Dashboard Principal)
cd dashboard
npm install
npm run build

# 3. Configurar el sistema
python configurator.py
```

### Instalación por Componentes

#### Dashboard Principal (TypeScript)

```bash
cd dashboard
npm install
npm run build  # Compilar TypeScript
npm start      # Iniciar servidor (puerto 3000)
```

#### Dashboard Secundario (Flask)

```bash
python web_dashboard.py  # Inicia en puerto 5001
```

#### Aplicación Nativa (Electron)

```bash
start.bat       # Inicio automático completo
start_dev.bat   # Modo desarrollo con DevTools
```

## 🧪 Pruebas (Testing)

Se incluyen tests automatizados usando pytest para validar comportamientos clave
del sistema (ej., respuesta a señales).

Para ejecutar todas las pruebas:

```powershell
python -m pytest -q
```

Si quieres ejecutar un solo archivo de prueba (por ejemplo las pruebas de
señales):

```powershell
python -m pytest -q tests/test_signals.py
```

Instalar dependencias de desarrollo (incluye pytest):

```powershell
pip install -r requirements-dev.txt
```

Los tests usan archivos de GetData temporales creados en el directorio de
sistema temporal y no afectan tu instalación de Train Simulator Classic.

## 📖 Uso

### Inicio de Dashboards

#### 🚀 **Inicio Completo del Sistema**

```bash
# Opción 1: Inicio automático completo (recomendado)
start.bat

# Opción 2: Inicio manual por componentes
```

#### 🏠 **Inicio del Dashboard Principal TypeScript**

```bash
cd dashboard
npm run build  # Solo la primera vez
npm start
# Acceder en: http://localhost:3000
```

#### 📊 **Inicio del Dashboard Flask Secundario**

```bash
python web_dashboard.py
# Acceder en: http://localhost:5001
```

#### 🖥️ **Inicio de la Aplicación Electron**

```bash
start.bat       # Inicio automático con verificación
start_dev.bat   # Modo desarrollo con DevTools
```

### Inicio Rápido del Sistema

```python
from tsc_integration import TSCIntegration
from predictive_telemetry_analysis import PredictiveTelemetryAnalyzer

# Inicializar componentes
tsc = TSCIntegration()
analyzer = PredictiveTelemetryAnalyzer()

# Iniciar análisis predictivo
analyzer.start_analysis()

# El sistema comenzará a leer datos y hacer predicciones automáticamente
```

## 🔒 Configuración de Seguridad

### Variables de Entorno

Antes de ejecutar el sistema, configura las variables de entorno para mayor
seguridad:

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores seguros
# FLASK_SECRET_KEY=tu-clave-secreta-muy-segura-aqui
```

### Configuración Recomendada

- **Desarrollo local:** Mantén `DASHBOARD_HOST=127.0.0.1` para acceso solo local
- **Acceso remoto:** Configura un host específico y considera usar HTTPS
- **Clave secreta:** Usa una clave aleatoria fuerte de al menos 32 caracteres

### Verificación de Seguridad

```bash
# Escanear código con Bandit
pip install bandit
bandit -r . --exclude .venv,node_modules

# Verificar dependencias con Safety
pip install safety
safety check
```

## 🚀 Inicio Rápido

```bash
# Iniciar el dashboard
python web_dashboard.py

# Acceder en el navegador: http://localhost:5001
```

### Testing

```bash
# Ejecutar todos los tests
python -m pytest

# Tests unitarios
python -m pytest tests/unit/

# Tests de integración
python -m pytest tests/integration/

# Tests end-to-end
python -m pytest tests/e2e/

# Con reporte de cobertura
python -m pytest --cov=. --cov-report=html
```

## 📁 Estructura del Proyecto

```text
TrainSimulatorAutopilot/
├── 📂 data/                    # Datos y modelos
│   ├── clean/                 # Datos procesados
│   ├── logs/                  # Registros del sistema
│   └── raw/                   # Datos crudos
├── 📂 docs/                   # Documentación
│   ├── data-cleaning.md      # Limpieza de datos
│   ├── ia-references.md      # Referencias de IA
│   ├── ia-spec.md           # Especificaciones de IA
│   ├── integration.md       # Guía de integración
│   └── workflow-log.md      # Log de desarrollo
├── 📂 scripts/               # Scripts auxiliares
├── 📂 tests/                 # Framework de testing
│   ├── unit/                # Tests unitarios
│   ├── integration/         # Tests de integración
│   └── e2e/                 # Tests end-to-end
├── 📄 configurator.py       # Configuración del sistema
├── 📄 engineScript.lua      # Script Lua para TSC
├── 📄 predictive_telemetry_analysis.py  # Análisis predictivo
├── 📄 tsc_integration.py    # Integración con TSC
├── 📄 web_dashboard.py      # Dashboard web
└── 📄 pytest.ini           # Configuración de testing
```

## 🧪 Framework de Testing

### Cobertura de Tests

| Tipo de Test | Cantidad | Estado | |--------------|----------|--------| |
Unitarios | 14 tests | ✅ Completo | | Integración | 5 tests | ✅ Completo | |
End-to-End | 4 tests | ✅ Completo | | **Total** | **23 tests** | **100%
Funcional** |

### Ejecución de Tests

```bash
# Tests completos con cobertura
python -m pytest --cov=. --cov-report=html

# Tests por marcador
python -m pytest -m "unit and not slow"     # Tests unitarios rápidos
python -m pytest -m integration            # Tests de integración
python -m pytest -m e2e                    # Tests end-to-end

# Tests de rendimiento
python -m pytest -m slow -v                # Tests que toman tiempo
```

### Reportes de Cobertura

Los reportes de cobertura se generan automáticamente en:

- **Terminal**: Salida en consola con porcentajes
- **HTML**: `htmlcov/index.html` - Reporte interactivo detallado

## 🔧 Configuración

### Archivo de Configuración

El sistema utiliza un archivo `config.ini` para configuración:

```ini
[TSC]
ruta_getdata = C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt
ruta_sendcommand = C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt

[PREDICTIVE]
modelo_archivo = data/predictive_model.pkl
ventana_analisis = 10
horizonte_prediccion = 5

[WEB]
puerto = 5001
host = 0.0.0.0
debug = false
```

### Configuración Automática

```bash
python configurator.py validate  # Validar configuración
python configurator.py optimize  # Optimizar parámetros
python configurator.py show      # Mostrar configuración actual
```

## 📊 API Reference

### TSCIntegration

```python
class TSCIntegration:
    def __init__(self)
    def obtener_datos_telemetria() -> Dict[str, Any]
    def enviar_comandos(comandos: Dict[str, Any]) -> bool
    def estado_conexion() -> Dict[str, Any]
    def conectar() -> bool
    def desconectar() -> None
```

### PredictiveTelemetryAnalyzer

```python
class PredictiveTelemetryAnalyzer:
    def __init__(self, lookback_steps: int = 10, prediction_horizon: int = 5)
    def add_telemetry_sample(self, telemetry_data: Dict[str, Any])
    def train_model(self) -> Dict[str, Any]
    def get_current_predictions(self) -> Dict[str, Any]
    def get_system_status(self) -> Dict[str, Any]
    def start_analysis(self) -> bool
    def stop_analysis()
```

### Web Dashboard

**Endpoints principales:**

- `GET /` - Dashboard principal
- `GET /bokeh` - Dashboard Bokeh interactivo
- `GET /analytics` - Dashboard Seaborn analytics
- `GET /api/telemetry` - Datos de telemetría en tiempo real
- `POST /api/control` - Enviar comandos de control
- `GET /api/predictions` - Predicciones actuales
- `GET /api/status` - Estado del sistema

**APIs de Optimización (FASE 4):**

- `GET /api/optimize/performance` - Aplicar optimizaciones de rendimiento
- `GET /api/optimize/stats` - Estadísticas de optimización actuales
- `POST /api/optimize/compression/toggle` - Activar/desactivar compresión
- `GET /api/optimize/cache/clear` - Limpiar cache inteligente
- `GET /api/optimize/latency/test` - Probar latencia del sistema

**APIs de Análisis Estadístico:**

- `GET /api/alerts` - Lista de alertas activas
- `GET /api/reports` - Lista de reportes disponibles
- `POST /api/reports/generate` - Generar reporte automático
- `GET /api/analytics/velocity` - Análisis de distribución de velocidad
- `GET /api/analytics/correlation` - Matriz de correlación

## 🤝 Contribución

### Guía de Desarrollo

1. **Fork** el repositorio
2. **Crear** una rama para tu feature: `git checkout -b feature/nueva-
  funcionalidad`
3. **Desarrollar** siguiendo las guías de estilo
4. **Agregar tests** para nueva funcionalidad
5. **Ejecutar** todos los tests: `python -m pytest`
6. **Crear commit** con mensaje descriptivo
7. **Push** a tu rama: `git push origin feature/nueva-funcionalidad`
8. **Crear Pull Request**

### Estándares de Código

- **PEP 8** para estilo de código Python
- **Google Style** para docstrings
- **Type hints** obligatorios en funciones públicas
- **Tests** requeridos para toda nueva funcionalidad
- **Cobertura** mínima del 80% en código nuevo

### Configuración de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Ejecutar linting
flake8 . --max-line-length=100
black . --check
isort . --check-only
```

## 📈 Rendimiento

### Métricas del Sistema

- **Latencia de respuesta**: < 100ms para comandos
- **Frecuencia de muestreo**: 10 Hz (100ms)
- **Precisión predictiva**: > 85% en condiciones normales
- **Consumo de CPU**: < 5% en operaciones normales
- **Consumo de memoria**: < 100MB en operación continua

### Optimizaciones

- **Procesamiento asíncrono** de telemetría
- **Buffer circular** para datos históricos
- **Lazy loading** de modelos predictivos
- **Compresión** de datos históricos
- **Pooling de conexiones** para estabilidad

## 🔒 Seguridad

### Medidas Implementadas

- **Validación de entrada** en todos los endpoints
- **Rate limiting** en API web
- **Encriptación** de datos sensibles
- **Auditoría completa** de comandos
- **Fail-safe mechanisms** para situaciones críticas

### Mejores Prácticas

- Nunca ejecutar como root/administrador
- Mantener actualizado el software
- Monitorear logs regularmente
- Backup de modelos entrenados
- Validar configuración antes de producción

## 📝 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver archivo `LICENSE` para
detalles.

## 🙏 Agradecimientos

- Comunidad de **Train Simulator Classic**
- Desarrolladores de **Raildriver Interface**
- Contribuidores de **scikit-learn** y **Flask**
- Beta testers y usuarios de la comunidad

## 📞 Soporte

### Canales de Soporte

- **Issues**: [GitHub Issues][gh_issues]
- **Discussions**: [GitHub Discussions][gh_discussions]
- **Wiki**: [Documentación completa][gh_wiki]

<!-- markdownlint-disable MD013 -->
[gh_issues]: https://github.com/tu-usuario/train-simulator-autopilot/issues
[gh_discussions]: https://github.com/tu-usuario/train-simulator-autopilot/discussions
[gh_wiki]: https://github.com/tu-usuario/train-simulator-autopilot/wiki
<!-- markdownlint-enable MD013 -->

## 🔌 Integración con Otros Juegos

El sistema está diseñado para ser extensible a otros juegos y simuladores.
Consulta la documentación completa:

### 📚 Documentación de Integración

- **[Guía Completa de Integración](docs/GUIA_COMPLETA_INTEGRACION_JUEGO.md)** -
  Pasos detallados para integrar un nuevo juego
- **[Checklist Rápido](docs/CHECKLIST_RAPIDO_INTEGRACION.md)** - Lista de
  verificación para implementación rápida
- **[Plantilla de Documentación](docs/template_telemetry_documentation.txt)** -
  Plantilla para documentar telemetría
- **[Guía de Plantillas](docs/TELEMETRY_TEMPLATE_README.md)** - Cómo usar las
  plantillas de documentación

### 🎮 Juegos Soportados

| Juego | Estado | Tipo | Método | |-------|--------|------|--------| | Train
Simulator Classic | ✅ Completo | Simulador Tren | Script Lua | | Microsoft
Flight Simulator | 📝 Documentado | Simulador Vuelo | SimConnect API | | Victoria
3 | 📝 Documentado | Estrategia | API Modding |

### 🚀 Agregar Nuevo Juego

Para integrar un nuevo juego:

1. **Evalúa compatibilidad** - Verifica APIs o métodos de captura disponibles
2. **Documenta variables** - Usa la plantilla para catalogar datos disponibles
3. **Implementa integración** - Crea clase basada en `tsc_integration.py`
4. **Actualiza dashboard** - Agrega métricas específicas del juego
5. **Prueba exhaustivamente** - Valida funcionamiento en diferentes escenarios

**Tiempo estimado**: 14-26 horas para integración completa

### Reportar Bugs

```markdown
**Título**: [BUG] Descripción breve

**Descripción**:
Pasos para reproducir:
1. Paso 1
2. Paso 2
3. Resultado esperado vs actual

**Entorno**:
- OS: [Windows/Linux/Mac]
- Python: [versión]
- TSC: [versión]
- Hardware: [especificaciones]
```

---

**🚂 ¡Disfruta conduciendo con inteligencia artificial!**
