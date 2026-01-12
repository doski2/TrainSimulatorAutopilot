# 🚂 Train Simulator Autopilot - Documentación Completa

## 📋 Información General

**Versión**: 2.0.0 **Fecha**: Noviembre 2025 **Autor**: Train Simulator
Autopilot Team **Licencia**: MIT

## 🎯 Resumen Ejecutivo

El **Train Simulator Autopilot** es un sistema avanzado de piloto automático
inteligente que utiliza inteligencia artificial y análisis predictivo para
controlar trenes en Train Simulator Classic. El sistema proporciona un dashboard
web completo con monitoreo en tiempo real, alertas inteligentes, reportes
automáticos y visualizaciones interactivas.

### ✨ Características Principales

- **Dashboard Web Completo**: Interfaz moderna con monitoreo en tiempo real
- **Sistema de Alertas**: Detección automática de condiciones críticas
- **Reportes Automáticos**: Generación programada de informes de rendimiento
- **Visualizaciones Interactivas**: Gráficos Bokeh en tiempo real
- **Monitoreo de Rendimiento**: Métricas detalladas de latencia y eficiencia
- **Integración Multi-locomotora**: Soporte para configuraciones complejas
- **Control de Locomotora**: Puertas, luces y frenos de emergencia
- **WebSocket Real-time**: Actualizaciones continuas cada 100ms

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```log
TrainSimulatorAutopilot/
├── web_dashboard.py          # Servidor Flask-SocketIO principal
├── dashboard.js              # Frontend JavaScript
├── index.html               # Template del dashboard
├── main.js                  # Aplicación Electron
├── autopilot_system.py      # Lógica del piloto automático
├── alert_system.py          # Sistema de alertas
├── automated_reports.py     # Generador de reportes
├── performance_monitor.py   # Monitoreo de rendimiento
└── tsc_integration.py       # Integración con TSC
```

### Tecnologías Utilizadas

- **Backend**: Python 3.9+, Flask-SocketIO
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **Visualizaciones**: Bokeh (puerto 5006)
- **Desktop App**: Electron.js
- **WebSockets**: Comunicación real-time
- **Base de Datos**: JSON para configuración y logs

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.8+**
- **Train Simulator Classic** instalado
- **Node.js 18+** (para Electron)
- **Raildriver Interface** (opcional pero recomendado)

### Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/train-simulator-autopilot.git
cd train-simulator-autopilot

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias Node.js
npm install

# Configurar el sistema
python configurator.py
```

### Configuración Inicial

1. **Editar `config.ini`**:

   <!-- markdownlint-disable MD013 -->

```ini
[TSC_INTEGRATION]
data_file_path = C:\...\GetData.txt
command_file_path = C:\...\SendCommand.txt
update_frequency_hz = 10
fuel_capacity_gallons = 300.0
```

Nota: Las métricas de combustible para integraciones TSC están deprecadas.
TSC usa combustible "infinito", por lo que `FuelLevel` no se utiliza en
el piloto automático.

La opción `fuel_capacity_gallons` se mantiene solo para integraciones que usen
valores de combustible externos (no TSC).

Si no se configura `fuel_capacity_gallons`, el dashboard mostrará porcentaje
cuando `FuelLevel` esté en 0..1. Si `FuelLevel` es un número grande (por ejemplo
4000), el dashboard intentará interpretarlo como galones.
<!-- markdownlint-enable MD013 -->

1. **Verificar rutas de TSC**:
   - Asegurarse de que los archivos `GetData.txt` y `SendCommand.txt` existan
   - Verificar permisos de escritura en la carpeta plugins

2. **Configurar puertos**:

- Dashboard principal: `http://localhost:5000`
- Visualizaciones Bokeh: `http://localhost:5006`

---

## Migración: Eliminación de FuelLevel y limpieza de datos

En la versión actual, `FuelLevel` y métricas de combustible han sido marcadas
como no implementadas para integraciones TSC (Train Simulator Classic) y
no se usan en el piloto automático. Si tu `alerts.json` o
`data/telemetry_history.json` contienen entradas históricas relacionadas con
combustible, ejecuta el script de limpieza:

```powershell
& .\.venv\Scripts\Activate.ps1
python scripts/cleanup_persisted_fuel.py
```

Este script crea respaldos y elimina entradas/keys de combustible históricas.

## Política de Datos de Telemetría y Alertas

**Resumen:** No subir datos de telemetría en ejecución o logs de pruebas
al control de versiones. Los archivos generados durante el
desarrollo/ejecución (por ejemplo `data/telemetry_history.json` o
grandes series de alertas) deben mantenerse fuera del repositorio y, si
es necesario, archivarse en `tests/fixtures` como muestras reducidas y
documentadas.

Buenas prácticas:

- Evita commitear archivos de telemetría en tiempo de ejecución o dumps
  de alertas completos.
- Usa `tests/fixtures/` para almacenar muestras pequeñas y
  reproducibles útiles para debugging o tests (no datasets completos
  generados en CI / local runs).
- Si necesitas limpiar datos históricos de telemetría o combustible,
  usa `scripts/cleanup_persisted_fuel.py` o `scripts/trim_alerts.py` para
  generar versiones reducidas apropiadas para el repositorio.
- Añade archivos temporales y scripts de depuración a `.gitignore` (p.
  ej. `tmp_*.py`, `data/telemetry_history.json`). Ya se han añadido
  estas reglas; por favor no remuevas estas entradas.

Procedimiento recomendado para archivar alertas de prueba:

1. Ejecuta `scripts/trim_alerts.py` para reemplazar `alerts.json` por una
   versión reducida de ejemplo.
2. Mueve o guarda el archivo completo en
   `tests/fixtures/alerts_wheelslip_full.json` (o similar) para referencia
   futura.
3. Añade una nota en el commit explicando que los datos completos se
   archivaron y por qué fueron removidos.

Razón: mantener el repositorio legible, reducir ruido en las revisiones y
evitar fugas accidentales de datos de entorno de ejecución.

## 🎮 Uso del Sistema

### Inicio del Dashboard

```bash
# Iniciar el servidor web
python web_dashboard.py

# O usar el launcher
python iniciar_dashboard.bat
```

### Interfaz del Dashboard

#### Panel Principal

- **Telemetría en Tiempo Real**: Velocidad, aceleración, controles
- **Alertas Activas**: Lista de alertas críticas con severidad
- **Métricas de Rendimiento**: Latencia, compresión, caché
- **Estado de Reportes**: Reportes generados y pendientes

#### Controles Interactivos

- **Botón Bokeh**: Carga visualizaciones interactivas
- **Controles de Navegación**: Pestañas para diferentes vistas
- **Configuración**: Ajustes en tiempo real

### Modos de Operación

1. **Modo Simulado**: Funciona sin TSC conectado (datos simulados)
2. **Modo TSC**: Integración completa con Train Simulator Classic
3. **Modo Multi-locomotora**: Control de formaciones complejas

### Controles de Locomotora

El sistema incluye controles avanzados para operar la locomotora:

#### Puertas Automáticas

- **Apertura/Cierre**: Control manual de puertas
- **Lógica Automática**: Se abren automáticamente al moverse, se cierran al
  detenerse
- **Feedback Visual**: Mensajes en pantalla del simulador

#### Sistema de Iluminación

- **Encendido/Apagado**: Control de luces de la locomotora
- **Estados**: Apagado (0) / Encendido (1)
- **Feedback**: Confirmación visual en el dashboard

#### Freno de Emergencia

- **Activación**: Botón dedicado para situaciones críticas
- **Prioridad Alta**: Anula otros controles automáticamente
- **Alertas**: Notificaciones visuales y auditivas

#### Comportamiento de Freno y Autopilot (actualizado)

- **Señales y reacciones**: El autopilot prioriza `KVB_SignalAspect`
  (señal avanzada) sobre `SignalAspect`.
  La señal resultante se expone en la variable `senal_procesada`.
  Los valores son: `-1` = DESCONOCIDO, `0` = ROJA, `1` = AMARILLA, `2` = VERDE.

- **Frenada por señal**: Si `autobrake_by_signal` está activado en `config.ini`,
  el autopilot reacciona a la señal procesada como sigue:
  - ROJA (0): Frenada completa — aplica `TrainBrakeControl = 1.0`.
    Si `TrainBrakeControl` no está disponible, se usa `VirtualBrake`.
  - AMARILLA (1): Frenada suave — aplica `TrainBrakeControl = 0.5` (valor
    heurístico configurable en `autopilot_system.py`).

-- **Prioridad de controles**: El sistema prioriza
  el control físico/real de freno (`TrainBrakeControl`) si está presente.
  Si no, usa `VirtualBrake` como fallback.
  En ausencia de ambos, se infiere la presión de freno por
  `freno_tren` calculado (derivado de `Acceleration` o fallbacks).

-- **Flags de presencia e inferencia**: En la telemetría la integración
  expone flags como `posicion_freno_tren_presente`,
  `presion_tubo_freno_presente` y `presion_freno_tren_presente`.
  Hay equivalentes con sufijo `_inferida` (ej. `presion_freno_tren_inferida`).
  Estos flags se pueden consultar en `/api/status` o recibir en
  `telemetry_update` para decidir visualización o la lógica del autopilot.

-- **Comandos y fallbacks**: Cuando se envían
  comandos de freno (por ejemplo, autopilot), la integración usará
  heurísticas y fallback controls — por ejemplo, si
  `DynamicBrake` no existe, puede mapear `DynamicBrake` a
  `VirtualEngineBrakeControl`.

- Asegúrate de que `TrainBrakeControl` o `VirtualBrake` aparecen en
    `GetData.txt`, o que `posicion_freno_tren_presente` sea True.
- Si el mod/locomotora solo reporta `presion_tubo_freno_mostrada` y no
    `AirBrakePipePressurePSI`, la integración usa
    `presion_tubo_freno_mostrada` como fallback y marca
    `presion_tubo_freno_inferida`.

**Ejemplo — comportamiento sobre señal:**

- `KVB_SignalAspect = 0` (ROJA) → autopilot envía `TrainBrakeControl: 1.0`.
- `KVB_SignalAspect = 1` (AMARILLA) → autopilot envía `TrainBrakeControl: 0.5`.

---

## 📊 APIs Disponibles

### Endpoints REST

#### `/api/status`

**Método**: GET **Descripción**: Estado general del sistema **Respuesta**:

```json
{
  "status": "online",
  "version": "2.0.0",
  "uptime": "01:23:45",
  "components": {
    "tsc_integration": "active",
    "alert_system": "active",
    "reports": "active",
    "performance": "active"
  }
}
```

Nota: El endpoint `/api/status` incluye además indicadores de presencia de
telemetría y flags de inferencia relacionados con frenos. Ejemplo:

```json
{
  "brake_pressure_present": true,
  "presion_tubo_freno_presente": true,
  "presion_tubo_freno_cola_presente": true,
  "presion_freno_loco_presente": true,
  "presion_freno_tren_presente": true,
  "posicion_freno_tren_presente": true,
  "presion_freno_tren_inferida": false,
  "brake_pipe_discrepancy_alert": { "active": true, "threshold_psi": 20 }
}
```

Estos flags facilitan la detección de si datos específicos están poblados desde
`GetData.txt` o si la integración los está infiriendo (ej. valores
calculados o estimados).
El dashboard también expone estos campos vía `telemetry_update`.

#### `/api/alerts`

**Método**: GET **Descripción**: Lista de alertas activas **Respuesta**:

```json
{
  "alerts": [
    {
      "id": "alert_001",
      "severity": "critical",
      "message": "Velocidad excesiva detectada",
      "timestamp": "2025-11-29T00:50:15Z"
    }
  ]
}
```

#### `/api/performance`

**Método**: GET **Descripción**: Métricas de rendimiento **Respuesta**:

```json
{
  "latency_ms": 45.2,
  "compression_ratio": 0.85,
  "cache_hit_rate": 0.92,
  "websocket_connections": 1
}
```

#### `/api/reports`

**Método**: GET **Descripción**: Estado de reportes **Respuesta**:

```json
{
  "last_report": "2025-11-29T00:45:00Z",
  "next_scheduled": "2025-11-29T01:00:00Z",
  "total_reports": 15
}
```

### Eventos WebSocket

#### `telemetry_update`

**Descripción**: Actualización de telemetría cada 100ms **Datos**:

```json
{
  "timestamp": "2025-11-29T00:50:15.123Z",
  "velocity": 85.5,
  "acceleration": 0.0023,
  "throttle": 0.75,
  "brake": 0.0,
  "alerts": [...],
  "performance": {...},
  "reports": {...}
}
```

Note: The telemetry payload includes signal fields:

- `senal_principal`: estado de la señal principal (values: -1 unknown, 0
  stop/red, 1 caution/yellow, 2 proceed/green)
- `senal_avanzada`: (when available) cab signalling like `KVB_SignalAspect`
- `senal_procesada`: normalized value used by the IA/UI (prefers
  `senal_avanzada` when present)

Autopilot rule: If `senal_procesada == 0` (ROJA/STOP), autopilot applies a full
brake; if `senal_procesada == 1` (AMARILLA/CAUTION), the autopilot reduces speed
and applies a light brake.

---

## 🔧 Configuración Avanzada

### Archivo `config.ini`

<!-- markdownlint-disable MD013 -->
```ini
[GENERAL]
debug_mode = false
log_level = INFO
max_log_size_mb = 10

[TSC_INTEGRATION]
data_file_path = C:\...\GetData.txt
command_file_path = C:\...\SendCommand.txt
update_frequency_hz = 10
max_read_attempts = 5
read_timeout_seconds = 1.0

[IA_SYSTEM]
max_speed_kmh = 160
min_speed_kmh = 0
brake_safety_margin = 0.1
acceleration_smoothing = 0.8
gradient_compensation_factor = 0.02

[VISUALIZATION]
enable_realtime_plot = true
plot_update_interval_ms = 100
max_data_points = 1000
enable_console_output = true
```
<!-- markdownlint-enable MD013 -->

### Variables de Entorno

```bash
# Puerto del servidor web
export FLASK_PORT=5000

# Puerto de Bokeh
export BOKEH_PORT=5006

# Nivel de logging
export LOG_LEVEL=INFO

# Modo debug
export DEBUG_MODE=false
```

---

## 🛠️ Solución de Problemas

### Problemas Comunes

#### 1. Error de Conexión TSC

**Síntoma**: "Integración TSC no disponible" **Solución**:

- Verificar que TSC esté ejecutándose
- Comprobar rutas en `config.ini`
- Verificar permisos de archivos

#### 2. Dashboard No Carga

**Síntoma**: Página en blanco o error de conexión **Solución**:

- Verificar que el puerto 5000 esté disponible
- Comprobar firewall/antivirus
- Revisar logs del servidor

#### 3. Actualizaciones No Real-time

**Síntoma**: Datos no se actualizan automáticamente **Solución**:

- Verificar conexión WebSocket
- Comprobar configuración de navegador
- Revisar logs de JavaScript

#### 4. Error de Puerto Ocupado

**Síntoma**: "Address already in use" **Solución**:

- Cambiar puerto en configuración
- Cerrar procesos que usen el puerto
- Usar `netstat` para identificar procesos

### Logs y Depuración

Los logs se almacenan en:

- `logs/autopilot.log`: Logs principales
- `logs/performance.log`: Métricas de rendimiento
- `reports/`: Reportes generados

Para habilitar debug:

```ini
[GENERAL]
debug_mode = true
log_level = DEBUG
```

---

## 📈 Monitoreo y Métricas

### Métricas de Rendimiento

- **Latencia WebSocket**: < 50ms promedio
- **Ratio de Compresión**: > 80%
- **Hit Rate del Caché**: > 90%
- **Uptime del Sistema**: > 99.9%

### Alertas del Sistema

#### Niveles de Severidad

- **🔴 Crítica**: Requiere atención inmediata
- **🟠 Alta**: Problema significativo
- **🟡 Media**: Advertencia
- **🟢 Baja**: Información

#### Tipos de Alertas

- Velocidad excesiva
- Fallo de comunicación TSC
- Problemas de rendimiento
- Anomalías en telemetría

---

## 🔄 Actualizaciones y Mantenimiento

### Actualización del Sistema

```bash
# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Reiniciar servicios
python web_dashboard.py
```

### Backup de Configuración

```bash
# Backup de configuración
cp config.ini config.ini.backup

# Backup de logs
cp -r logs logs_backup_$(date +%Y%m%d)
```

### Limpieza del Sistema

```bash
# Limpiar logs antiguos
find logs -name "*.log" -mtime +30 -delete

# Limpiar reportes antiguos
find reports -name "*.json" -mtime +90 -delete
```

---

## 🤝 Contribución

### Guías de Desarrollo

1. **Fork** el repositorio
2. Crear **branch** para nueva funcionalidad
3. **Commit** cambios con mensajes descriptivos
4. **Push** a branch
5. Crear **Pull Request**

6. **Añadir entradas en el CHANGELOG**:
   - Añade una entrada concisa en `CHANGELOG.md` bajo *Unreleased* siguiendo el formato "Keep a Changelog" (título, fecha y entradas breves).
   - Si la entrada es extensa o histórica, propon el archivado de versiones anteriores en `archivado/` y documenta la razón en la PR.
   - Si `CONTRIBUTING.md` no contiene pautas para el changelog, crea un issue para añadirlas (se puede automatizar la plantilla si se desea).

### Estándares de Código

- **Python**: PEP 8
- **JavaScript**: ESLint
- **HTML/CSS**: HTML5/CSS3 standards
- **Commits**: Conventional commits

### Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=.

# Tests específicos
pytest tests/test_tsc_integration.py
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más
detalles.

---

## 📞 Soporte

### Canales de Soporte

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: Documentación completa
- **Discord**: Comunidad de usuarios

### Información de Contacto

- **Email**: <support@trainsimulator-autopilot.com>
- **Discord**: [Train Simulator Autopilot](https://discord.gg/train-simulator)
- **GitHub**: Issues —
  <https://github.com/tu-usuario/train-simulator-autopilot/issues>

---

## 🔗 Enlaces Útiles

- [Documentación API](./api-docs.md)
- [Guía de Configuración](./configuration-guide.md)
- [Tutoriales](./tutorials/)
- [Ejemplos](./examples/)
- [Changelog](./CHANGELOG.md)

---

*Última actualización: Noviembre 2025*</content> parameter
name="filePath">c:\Users\doski\TrainSimulatorAutopilot\DOCUMENTATION.md
