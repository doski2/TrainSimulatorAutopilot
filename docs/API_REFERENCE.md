# 📚 API Reference Completa - Train Simulator Autopilot

## Documentación completa de todas las APIs del sistema Train Simulator

Autopilot

**Última actualización:** Diciembre 2025

## 🏗️ Arquitectura General

### Componentes Principales

```python
# Backend Python
from tsc_integration import TSCIntegration
from predictive_telemetry_analysis import PredictiveTelemetryAnalyzer
from web_dashboard import WebDashboard

# Dashboard TypeScript (Principal)
# Ver sección Dashboard TypeScript API

# Cliente WebSocket
# Ver sección WebSocket Client API

# Aplicación Electron
# Ver sección Electron Application API
```

### Diagrama de Arquitectura Actual (02/12/2025)

```text
┌─────────────────────────────────────────────────────────────┐
│                    TRAIN SIMULATOR AUTOPILOT                │
│                        (v3.0.0)                            │
└─────────────────┬───────────────────┬───────────────────────┘
                  │                   │
                  ▼                   ▼
┌─────────────────┴───────────────────┴───────────────────────┐
│                    BACKEND CORE (Python)                     │
├─────────────────────────────────────────────────────────────┤
│  TSCIntegration │ PredictiveTelemetryAnalyzer │ WebDashboard│
└─────────────────┼───────────────────┼───────────────────────┘
                  │                   │
                  ▼                   ▼
┌─────────────────┴───────────────────┴───────────────────────┐
│                 DASHBOARDS MULTI-PLATAFORMA                 │
├─────────────────┼───────────────────┼───────────────────────┘
│ Dashboard       │ Dashboard         │ Aplicación            │
│ TypeScript      │ Flask             │ Electron              │
│ (Principal)     │ (Secundario)      │ (Nativa)              │
│ Puerto 3000     │ Puerto 5001       │ Desktop               │
├─────────────────┼───────────────────┼───────────────────────┘
│ Express.js      │ Flask + Bootstrap │ Electron + Chromium   │
│ Socket.IO       │ Socket.IO         │ Backend integrado     │
│ TypeScript      │ Python            │ Node.js               │
└─────────────────┼───────────────────┼───────────────────────┘
                  │                   │
                  ▼                   ▼
┌─────────────────┴───────────────────┴───────────────────────┐
│                 TRAIN SIMULATOR CLASSIC                      │
└─────────────────────────────────────────────────────────────┘
```

### Arquitectura Multi-Dashboard

El sistema implementa **tres dashboards especializados**:

#### 🏠 **Dashboard TypeScript (Sistema Principal)**

- **Tecnología**: Node.js + TypeScript + Express.js + Socket.IO
- **Puerto**: 3000
- **Características**: API REST completa, WebSocket en tiempo real, interfaz
moderna
- **Estado**: ✅ **Completamente operativo**

#### 📊 **Dashboard Flask (Sistema Secundario)**

- **Tecnología**: Python Flask + Bootstrap + Socket.IO
- **Puerto**: 5001
- **Características**: Dashboard web responsive, métricas avanzadas
- **Estado**: ✅ **Completamente operativo**

#### 🖥️ **Aplicación Electron (Sistema Nativo)**

- **Tecnología**: Electron + Chromium
- **Características**: Aplicación de escritorio nativa
- **Estado**: ✅ **Completamente operativa**

## 🌐 Web Dashboard API (Flask)

### 📋 Información General

**Versión:** 1.1.0 **Framework:** Flask + Socket.IO **Puerto Principal:** 5001
**Puerto Bokeh:** Dinámico (5006-5009)

### 🎯 Propósito

El servidor web Flask proporciona una interfaz REST API completa para el
monitoreo y control remoto del sistema Train Simulator Autopilot, incluyendo
comunicación en tiempo real vía WebSocket.

### 🚀 Inicio Rápido

#### Requisitos Previos

```bash
# Instalar dependencias
pip install flask flask-socketio flask-cors bokeh
```

#### Iniciar el Servidor

```bash
python web_dashboard.py
```

### 📡 API Endpoints

#### 🔍 Health & Status

##### `GET /health`

Health check básico del servidor.

**Respuesta (200):**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-29T10:30:00.000000",
  "version": "1.0.0",
  "services": {
    "tsc_integration": true,
    "bokeh_server": true,
    "alerts_system": true,
    "reports_system": true,
    "dashboard_active": true
  },
  "uptime": 3600.5,
  "telemetry_updates": 15000
}
```

##### `GET /api/server_info`

Información detallada del servidor.

##### `GET /api/metrics/dashboard` ⭐ **NUEVO**

Métricas detalladas del dashboard.

#### 🎮 Control del Sistema

##### `POST /api/control/{action}`

Control principal del piloto automático.

**Parámetros URL:** `action`: `start_autopilot`, `stop_autopilot`,
`start_predictive`, `stop_predictive`, `train_model`

#### 🚨 Sistema de Alertas

##### `GET /api/alerts/status`

Estado del sistema de alertas.

##### `POST /api/alerts/check`

Verificación manual de alertas.

##### `POST /api/alerts/acknowledge/{alert_id}`

Confirmar recepción de alerta.

#### 📊 Reportes

##### `GET /api/reports/status`

Estado del sistema de reportes.

##### `POST /api/reports/generate/{report_type}`

Generar reporte manual. Tipos: `daily`, `weekly`, `monthly`, `performance`,
`alerts`

#### ⚡ Optimización y Rendimiento

##### `POST /api/optimize/performance`

Aplicar optimizaciones de rendimiento.

##### `GET /api/optimize/stats`

Estadísticas de optimizaciones.

##### `POST /api/optimize/compression/toggle`

Activar/desactivar compresión.

#### 📈 Rendimiento

##### `GET /api/performance_report`

Reporte de rendimiento del sistema.

##### `POST /api/performance_baseline`

Establecer línea base de rendimiento.

#### 🎨 Visualización Bokeh

##### `GET /bokeh`

Servir aplicación Bokeh.

### 🌐 WebSocket Events

#### Eventos de Salida (Servidor → Cliente)

```javascript
// Conectar
const socket = io('http://localhost:5001');

// Eventos disponibles
socket.on('telemetry_update', (data) => {
  console.log('Telemetría:', data);
});

socket.on('system_message', (data) => {
  console.log('Mensaje:', data.message, 'Tipo:', data.type);
});

socket.on('alert_triggered', (alert) => {
  console.log('Alerta:', alert);
});

socket.on('performance_update', (metrics) => {
  console.log('Rendimiento:', metrics);
});
```

#### Frecuencia de Actualización

- **Telemetría:** 10 Hz (cada 100ms)
- **Alertas:** Event-driven
- **Rendimiento:** 1 Hz (cada 1s)
- **Mensajes del Sistema:** Event-driven

## 📊 APIs de Análisis Estadístico

### 🚀 Funcionalidades Disponibles

#### 1. Sistema de Alertas

**Endpoint:** `GET /api/alerts`

Retorna todas las alertas activas del sistema.

#### 2. Sistema de Reportes

**Endpoint:** `GET /api/reports`

Lista todos los reportes disponibles.

**Generar Reporte:** `POST /api/reports/generate`

#### 3. Análisis de Velocidad

**Endpoint:** `GET /api/analytics/velocity`

Retorna análisis estadístico completo de la distribución de velocidad.

#### 4. Matriz de Correlación

**Endpoint:** `GET /api/analytics/correlation`

Calcula y retorna la matriz de correlación entre todas las variables de
telemetría.

### 🔧 Uso Programático

#### Cliente Python

```python
import requests

class AnalyticsClient:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url

    def get_velocity_analysis(self, hours=24):
        response = requests.get(f"{self.base_url}/api/analytics/velocity?hours={hours}")
        return response.json()

    def get_correlation_matrix(self, method="pearson"):
        response = requests.get(f"{self.base_url}/api/analytics/correlation?method={method}")
        return response.json()

    def generate_report(self, report_type="daily", format="pdf"):
        data = {
            "type": report_type,
            "format": format,
            "include_charts": True
        }
        response = requests.post(f"{self.base_url}/api/reports/generate", json=data)
        return response.json()
```

#### Cliente JavaScript

```javascript
class AnalyticsAPI {
  constructor(baseURL = 'http://localhost:5001') {
    this.baseURL = baseURL;
  }

  async getVelocityAnalysis(hours = 24) {
    const response = await fetch(
      `${this.baseURL}/api/analytics/velocity?hours=${hours}`,
    );
    return await response.json();
  }

  async getCorrelationMatrix(method = 'pearson') {
    const response = await fetch(
      `${this.baseURL}/api/analytics/correlation?method=${method}`,
    );
    return await response.json();
  }
}
```

### 📊 Tipos de Alertas

- **🔴 Critical**: Condiciones peligrosas que requieren acción inmediata
- **🟠 High**: Problemas significativos que afectan el rendimiento
- **🟡 Medium**: Anomalías que requieren atención
- **🔵 Low**: Notificaciones informativas
- **🟢 Info**: Información general del sistema

### 📈 Reportes Automáticos

- **daily**: Reporte diario con métricas del día anterior
- **weekly**: Reporte semanal con tendencias semanales
- **monthly**: Reporte mensual con análisis completos
- **custom**: Reportes personalizados con rangos de fecha específicos

### 🔍 Análisis Estadístico Avanzado

#### Algoritmos Implementados

1. **Detección de Anomalías**: Método IQR, Z-Score analysis
2. **Análisis de Tendencias**: Regresión lineal, Media móvil exponencial
3. **Correlación Avanzada**: Pearson, Spearman rank correlation

## 🛡️ Seguridad

### CORS Configuration

```python
socketio_cors_allowed_origins = [
    "http://localhost:5000",  # Dashboard principal
    "http://localhost:5001",  # Servidor Flask
]
```

### Validación de Entrada

- ✅ **Lista Blanca:** Acciones y tipos permitidos
- ✅ **Validación de Tipos:** Booleanos, strings, números
- ✅ **Sanitización:** Limpieza de datos de entrada

### Manejo de Errores

#### Códigos HTTP

- **200 OK:** Operación exitosa
- **400 Bad Request:** Parámetros inválidos
- **403 Forbidden:** Acceso denegado
- **404 Not Found:** Endpoint no encontrado
- **500 Internal Server Error:** Error del servidor
- **503 Service Unavailable:** Servicio no disponible

## 📝 Logging

### Niveles de Log

```log
[BOOT] Inicialización del sistema
[INIT] Sistema inicializado correctamente
[BOKEH] Servidor Bokeh iniciado en puerto 5006
[ERROR] Error en endpoint /api/control/start_autopilot: Connection timeout
[PERF] Optimización aplicada: websocket_batching
```

## 🔄 Ciclo de Vida

### 1. Inicialización

```python
# Cargar configuración
config = load_config()

# Inicializar componentes
tsc_integration = get_tsc_integration()
alert_system = get_alert_system()
reports_system = get_automated_reports()

# Iniciar servidor
start_dashboard(host="127.0.0.1", port=5001)
```

### 2. Bucle Principal

```python
while dashboard_active:
    # Obtener telemetría
    telemetry = tsc_integration.get_telemetry()

    # Procesar datos
    processed_data = process_telemetry(telemetry)

    # Emitir vía WebSocket
    socketio.emit('telemetry_update', processed_data)

    # Verificar alertas
    check_alerts()

    time.sleep(0.1)  # 10 Hz
```

### 3. Apagado

```python
# Detener componentes
predictive_analyzer.stop_analysis()
performance_monitor.stop_monitoring()

# Guardar estado
save_system_state()

# Cerrar conexiones
tsc_integration.disconnect()
```

## 🐛 Troubleshooting

### Puerto Ocupado

```bash
# Verificar procesos usando el puerto
netstat -ano | findstr :5001

# Matar proceso (reemplazar PID)
taskkill /PID <PID> /F
```

### Error de CORS

```log
Access to XMLHttpRequest blocked by CORS policy
```

**Solución:** Verificar configuración CORS en `web_dashboard.py`

### Error de Importación

```log
ModuleNotFoundError: No module named 'bokeh'
```

**Solución:**

```bash
pip install bokeh
```

### Debug Mode

```bash
# Ejecutar con debug
FLASK_DEBUG=true python web_dashboard.py
```

## 📊 Monitoreo

### Métricas Disponibles

- **Uptime:** Tiempo de actividad del servidor
- **Conexiones Activas:** Número de clientes WebSocket conectados
- **Actualizaciones de Telemetría:** Contador de mensajes enviados
- **Uso de Memoria:** RSS, VMS, porcentaje
- **Rendimiento:** CPU, latencia de respuesta

### Health Checks

```bash
# Health check básico
curl http://localhost:5001/health

# Métricas detalladas
curl http://localhost:5001/api/metrics/dashboard

# Estado de servicios
curl http://localhost:5001/api/server_info
```

## 📞 Soporte

### Canales de Comunicación

- **Issues:** GitHub Issues del proyecto
- **Logs:** Revisar logs de consola para debugging
- **Documentación:** Esta guía y `docs/api-reference.md`

### Información de Debug

```python
# Obtener información del sistema
GET /api/server_info

# Ver métricas detalladas
GET /api/metrics/dashboard

# Health check
GET /health
```

---

**Para documentación completa detallada, consultar:**

- `api-reference.md` - Referencia completa de APIs
- `WEB_DASHBOARD_API.md` - API específica del dashboard web
- `APIS_ANALISIS_ESTADISTICO.md` - APIs de análisis estadístico
