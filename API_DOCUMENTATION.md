# 📡 Documentación de APIs - Train Simulator Autopilot

**Revisado:** 13/01/2026 — Revisado por @doski2 ✅

## 📋 Información General

**Base URL**: `http://localhost:5001`  (por defecto; configurable con la variable de entorno `FLASK_PORT`)
**Protocolo**: HTTP/1.1 + WebSocket  
**Autenticación**: Ninguna (desarrollo local). **En producción debe habilitarse autenticación/autorización** (issue creado).  
**Formato**: JSON  

## 🔌 Endpoints REST API

### GET `/api/status`

Obtiene el estado actual del sistema del dashboard.

**Respuesta Exitosa (200)**:

```json
{
  "tsc_connected": true,
  "playback_active": true,
  "data_points": 23,
  "timestamp": "2025-11-29T01:02:15.123456"
}
```

**Campos**:

- `tsc_connected`: Boolean - Indica si la integración TSC está conectada
- `playback_active`: Boolean - Indica si el playback de Bokeh está activo
- `data_points`: Integer - Número de puntos de datos en la última telemetría
- `timestamp`: String - Timestamp ISO de la respuesta

---

### GET `/api/alerts/status`

Obtiene el estado actual del sistema de alertas.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "status": {
    "monitoring_active": true,
    "total_alerts": 5,
    "active_alerts": 2
  },
  "active_alerts": [
    {
      "id": "alert_001",
      "message": "Velocidad excesiva",
      "severity": "warning",
      "timestamp": "2025-11-29T01:00:00Z"
    }
  ]
}
```

---

### POST `/api/alerts/check`

Ejecuta verificación manual de alertas.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "data": {
    "alerts_checked": 5,
    "new_alerts": 1
  }
}
```

---

### POST `/api/alerts/acknowledge/<alert_id>`

Marca una alerta como reconocida.

**Parámetros URL**:

- `alert_id`: ID de la alerta a reconocer

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "message": "Alerta alert_001 reconocida"
}
```

---

### POST `/api/alerts/start_monitoring`

Inicia el monitoreo continuo de alertas.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "message": "Monitoreo de alertas iniciado"
}
```

---

### POST `/api/alerts/stop_monitoring`

Detiene el monitoreo continuo de alertas.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "message": "Monitoreo de alertas detenido"
}
```

---

### GET `/api/reports/status`

Obtiene el estado del sistema de reportes automáticos.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "status": {
    "automation_active": false,
    "last_report": null,
    "scheduled_reports": []
  }
}
```

---

### POST `/api/reports/generate/<report_type>`

Genera un reporte manualmente.

**Parámetros URL**:

- `report_type`: Tipo de reporte (`daily`, `weekly`, `monthly`)

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "data": {
    "report_type": "daily",
    "generated_at": "2025-11-29T01:00:00Z",
    "file_path": "reports/daily_report_20251129.json"
  }
}
```

---

### POST `/api/reports/start_automation`

Inicia la automatización de reportes.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "message": "Automatización de reportes iniciada"
}
```

---

### POST `/api/reports/stop_automation`

Detiene la automatización de reportes.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "message": "Automatización de reportes detenida"
}
```

---

### GET `/api/performance_report`

Obtiene el reporte de rendimiento actual.

**Respuesta Exitosa (200)**:

```json
{
  "metrics": {
    "websocket_latency": 45.2,
    "telemetry_loop_time": 12.5,
    "dashboard_response_time": 5.8
  },
  "baseline": {
    "websocket_latency": 40.0,
    "telemetry_loop_time": 10.0
  },
  "timestamp": "2025-11-29T01:00:00Z"
}
```

---

### POST `/api/performance_baseline`

Establece una nueva línea base de rendimiento.

**Cuerpo de la Solicitud**:

```json
{
  "label": "baseline_test"
}
```

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "message": "Línea base 'baseline_test' establecida",
  "label": "baseline_test"
}
```

---

### POST `/api/control/<action>`

Envía comandos de control al sistema.

Los controles de alternancia (puertas, luces) mantienen estado interno.

**Parámetros URL**:

- `action`: Acción a ejecutar
  - `start_autopilot`, `stop_autopilot`: Control del piloto automático
  - `start_predictive`, `stop_predictive`: Control del análisis predictivo
  - `train_model`: Entrenar modelo predictivo
  - `toggle_doors`: Alternar estado de puertas (abre/cierra)
  - `toggle_lights`: Alternar estado de luces (enciende/apaga)
  - `emergency_brake`: Activar freno de emergencia (¡acción crítica — deben existir comprobaciones de seguridad en servidor y logs auditables!)

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "action": "toggle_lights"
}
```

**Nota:** Las acciones críticas (por ejemplo `emergency_brake`) deben documentarse y requerir validaciones/confirmaciones específicas en el servidor; se creó un issue para proponer medidas de seguridad y validación de control.

---

### GET `/api/control/status`

Obtiene el estado actual de los controles de la locomotora.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "control_states": {
    "doors_open": false,
    "lights_on": true
  },
  "timestamp": "2025-12-06T12:30:00.000000"
}
```

---

### POST `/api/validate_config`

Valida la configuración del dashboard.

**Cuerpo de la Solicitud**:

```json
{
  "theme": "dark",
  "updateInterval": 500,
  "historyPoints": 100
}
```

**Respuesta Exitosa (200)**:

```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "config": {
    "theme": "dark",
    "updateInterval": 500,
    "historyPoints": 100
  }
}
```

---

### POST `/api/optimize/performance`

Aplica optimizaciones de rendimiento.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "results": {
    "applied_optimizations": [
      "websocket_batching",
      "data_sampling",
      "render_throttling"
    ]
  }
}
```

---

### GET `/api/optimize/stats`

Obtiene estadísticas de optimizaciones.

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "cache": {
    "stats": "cache statistics here"
  },
  "latency": {
    "report": "latency report here"
  },
  "compression_enabled": true
}
```

---

### POST `/api/optimize/compression/toggle`

Activa/desactiva la compresión de datos.

**Cuerpo de la Solicitud**:

```json
{
  "enabled": true
}
```

**Respuesta Exitosa (200)**:

```json
{
  "success": true,
  "compression_enabled": true
}
```

---

### GET `/debug`

Página de debug para verificar datos (HTML).

### GET `/debug_data`

Datos de debug en formato JSON.

**Respuesta Exitosa (200)**:

```json
{
  "telemetry": {
    "velocidad_actual": 0.0,
    "timestamp": "2025-11-29T01:00:00.000000"
  },
  "system_status": {
    "tsc_connected": true,
    "telemetry_updates": 150
  },
  "timestamp": "2025-11-29T01:00:00.000000"
}
```

---

### GET `/bokeh`

Sirve el dashboard interactivo de Bokeh.

---

### GET `/`

Página principal del dashboard (HTML).

---

## 🔌 Eventos WebSocket

### Conexión

**URL**: `ws://localhost:5001/socket.io/`  (usa `wss://...` en producción con TLS)
**Protocolo**: Socket.IO  
**Namespace**: `/` (default)  

### Eventos de Servidor a Cliente

#### `telemetry_update`

Actualización de telemetría cada 100ms.

```json
{
  "telemetry": {
    "velocidad_actual": 85.5,
    "aceleracion": 0.0023,
    "rpm": 1200
  },
  "predictions": {},
  "multi_loco": {},
  "system_status": {
    "tsc_connected": true,
    "telemetry_updates": 150
  },
  "active_alerts": [],
  "active_alerts_list": [],
  "performance": {
    "metrics": {}
  },
  "reports": {
    "status": "not_available"
  }
}
```

**Nota:** `active_alerts_list` contiene el array completo de objetos de alerta activos (preferible al contador numérico `active_alerts`).

**Acción pendiente:** El esquema completo y tipos de datos del payload `telemetry_update` (campos, unidades y ejemplos) deben documentarse formalmente — se creó un issue para definir y mantener el esquema (JSON Schema / OpenAPI).

Fuel-related metrics (e.g. `fuelLevel`, `fuelConsumption`) are deprecated for
TSC integration; use efficiency metrics instead.

#### `system_message`

Mensajes del sistema.

```json
{
  "message": "Piloto automático iniciado",
  "type": "success"
}
```

### Eventos de Cliente a Servidor

#### `connect`

Conexión de cliente.

#### `disconnect`

Desconexión de cliente.

#### `request_telemetry`

Solicitud de actualización de telemetría.

---

## 📊 Códigos de Error

### Códigos HTTP

- **200**: OK - Solicitud exitosa
- **400**: Bad Request - Datos inválidos
- **404**: Not Found - Endpoint no encontrado
- **500**: Internal Server Error - Error del servidor

### Respuestas de Error

```json
{
  "success": false,
  "error": "Descripción del error"
}
```

---

## 🧪 Testing de APIs

### Usando PowerShell

```powershell
# Test de estado
Invoke-RestMethod -Uri "http://localhost:5000/api/status" -Method GET

# Test de alertas
Invoke-RestMethod -Uri "http://localhost:5000/api/alerts/status" -Method GET
```

### Usando cURL

```bash
# Test de estado
curl -X GET http://localhost:5000/api/status

# Test de alertas
curl -X GET http://localhost:5000/api/alerts/status
```

### Usando Python

```python
import requests

# Test básico
response = requests.get('http://localhost:5000/api/status')
print(f"Status: {response.status_code}")
print(response.json())
```

---

## 📈 Límites y Consideraciones

- **Actualización**: Telemetría cada 100ms
- **Compresión**: Datos comprimidos por defecto
- **WebSocket**: Conexiones Socket.IO para tiempo real
- **Cache**: Optimizaciones de rendimiento activas

---

*Última actualización: 13/01/2026*</content>
parameter name="filePath">c:\Users\doski\TrainSimulatorAutopilot\API_DOCUMENTATION.md
