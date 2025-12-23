# Instrucciones de GitHub Copilot - Train Simulator Autopilot

## Descripción del proyecto
Train Simulator Autopilot es un sistema multinivel (multi-language) que integra control automático de trenes con Train Simulator Classic. Incluye tres dashboards operativos (TypeScript/Node.js, Flask/Python, Electron) conectados por WebSockets y scripts Lua que gestionan la integración en tiempo real mediante IPC basado en archivos.

## Fundamentos de la arquitectura
- **Backend**: Núcleo en Python con scikit-learn para ML, APIs Flask y comunicación en tiempo real por Socket.IO
- **Dashboards**: TypeScript/Express (puerto 3000), Flask (puerto 5001), aplicación Electron (escritorio)
- **Integración con el simulador**: Scripts Lua en `RailWorks/plugins/` que leen/escriben telemetría en `GetData.txt`/`SendCommand.txt`
- **Flujo de datos**: TSC → Lua → Archivos → Backend Python → WebSocket → Dashboards
- **Multilocomotora**: Soporte para formaciones complejas con control independiente

## Flujos críticos (workflows)
### Inicio del sistema
```bash
start.bat              # Inicio completo (Python + dashboards)
python web_dashboard.py # Solo dashboard Flask (puerto 5001)
cd dashboard && npm start # Dashboard TypeScript (puerto 3000)
```

### Pruebas y calidad
```bash
python -m pytest -v                    # Ejecutar todas las pruebas
python -m pytest --cov=. --cov-report=html  # Ejecutar con cobertura
ruff check . && ruff format .          # Lint y formato Python
cd dashboard && npm run lint           # Lint TypeScript
```

### Configuración
```bash
python configurator.py validate        # Validar configuración
cp config.ini.example config.ini       # Copiar plantilla de configuración
cp .env.example .env                   # Copiar variables de entorno
```

## Patrones y convenciones de código

### Estructura del backend (Python)
- **Módulos clave**: `autopilot_system.py`, `tsc_integration.py`, `predictive_telemetry_analysis.py`
- **Configuración**: `config.ini` (copiar desde `config.ini.example`), variables en `.env`
- **Logging**: Usar `from logging_config import get_logger; logger = get_logger(__name__)`
- **Manejo de errores**: Usar try/except con excepciones concretas y logging contextual
- **Type hints**: Recomendados para parámetros y retornos

### Comunicación basada en archivos (archivo GetData / SendCommand)
```python
# Lectura de telemetría
with open(r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt", 'r') as f:
    data = f.read()

# Envío de comandos
with open(r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt", 'w') as f:
    f.write(command_string)
```
- Use rutas absolutas en Windows y considere bloqueo de archivos en escenarios concurrentes.

### Eventos WebSocket
```python
# Backend (Flask-SocketIO)
socketio.emit('telemetry', telemetry_data)
socketio.emit('status', {'system': 'active'})

# Conexión en frontend
socket.on('telemetry', (data) => { /* procesar telemetría */ });
```

### Patrones en scripts Lua
- **Leer controles**: `Call("*:GetControlValue", control_name, 0)`
- **Escribir controles**: `Call("*:SetControlValue", control_name, 0, value)`
- **Operaciones de archivo**: Usar rutas absolutas y gestionar bloqueo
- **Comprobaciones**: Verificar `Call("*:ControlExists", name, 0) == 1` antes de leer

## Guía de pruebas
- **Framework**: `pytest` con `pytest-cov` y `pytest-mock`
- **Estructura**: Archivos en `tests/` nombrados `test_*.py`
- **Mocking**: Simular E/S de archivos, llamadas a TSC y redes
- **Cobertura**: Apuntar a ≥80% para código nuevo
- **Nomenclatura**: `test_should_[behavior]_when_[condition]`

## Archivos y directorios clave
- `autopilot_system.py` - Lógica principal del IA
- `tsc_integration.py` - Capa de comunicación con el simulador
- `Railworks_GetData_Script.lua` - Script Lua principal para integración
- `dashboard/` - Dashboard TypeScript/Node.js (principal)
- `web_dashboard.py` - Dashboard Flask (secundario)
- `config.ini.example` - Plantilla de configuración
- `requirements.txt` - Dependencias Python
- `tests/` - Suite de pruebas
- `.github/agents/` - Instrucciones para agentes especializados

## Reglas para agentes automatizados
- **Comprobar antes de crear:** Antes de crear cualquier archivo nuevo, busca si ya existe un archivo similar (mismo propósito o nombre parecido). Revisa `*.md`, `*.py`, `*.lua` y directorios relevantes como `.github/agents/`, `docs/`, `scripts/`.
- **Preferir actualización sobre duplicado:** Si existe un archivo adecuado, prefiera **actualizar** y adaptar ese archivo en lugar de crear uno nuevo que duplique funcionalidad o contenido.
- **En caso de duda, preguntar:** Si no está claro si se debe crear o actualizar, abre un issue o solicita confirmación al mantenedor del repositorio antes de crear el archivo.
- **Documentar la decisión:** Cuando cree o modifique archivos, añada en la descripción del PR la razón, los archivos que revisó y por qué la creación fue necesaria.
- **Evitar duplicados en rutas clave:** No crear archivos con nombres que ya existan en directorios clave (`.github/agents/`, `docs/`, `dashboard/`), salvo una razón explícita.
- **Ejemplo práctico:** Antes de añadir `scripts/new_agent.py`, busque `scripts/*.py` y `scripts/agent_*` y actualice un archivo existente si aplica.

## Preparar el entorno de desarrollo
1. Instalar Python 3.9+, Node.js 18+
2. `pip install -r requirements.txt`
3. `cd dashboard && npm install`
4. Copiar `config.ini.example` a `config.ini`
5. Ejecutar `python configurator.py` para validar la configuración
6. Usar `start.bat` para pruebas de integración completas

## Puntos de integración comunes
- **Interfaz Raildriver**: Mapeo de hardware y controles
- **Multilocomotora**: `multi_locomotive_integration.py`
- **Sistema de alertas**: `alert_system.py` para monitorización de seguridad
- **Análisis predictivo**: Modelos en `predictive_telemetry_analysis.py`
- **Informes automáticos**: `automated_reports.py` para PDFs y reportes

## Consideraciones de seguridad
- Validar todas las entradas externas (simulador/Lua)
- Usar variables de entorno para rutas y secretos sensibles
- Aplicar límites de tasa en conexiones WebSocket cuando corresponda
- Registrar eventos de seguridad con `logger.warning()`
- No exponer rutas de archivos del simulador en interfaces web
</content>
<parameter name="filePath">c:\Users\doski\TrainSimulatorAutopilot\.github\copilot-instructions.md