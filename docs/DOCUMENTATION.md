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
- **Señales y telemetría mejorada**: Notas de `SignalAspect` y
`KVB_SignalAspect` añadidas en la sección de telemetría

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

- **Backend**: Python 3.8+, Flask-SocketIO
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
- **Node.js 16+** (para Electron)
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

  ```ini
   [TSC_INTEGRATION]
  data_file_path = C:\...\GetData.txt
  command_file_path = C:\...\SendCommand.txt
   update_frequency_hz = 10
    ```

2. **Verificar rutas de TSC**:

- Asegurarse de que los archivos `GetData.txt` y `SendCommand.txt` existan
- Verificar permisos de escritura en la carpeta plugins

3. **Configurar puertos**:

- Dashboard principal: `http://localhost:5000`
- Visualizaciones Bokeh: `http://localhost:5006`

---

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

## DOCUMENTATION (Copied from root)

This file mirrors the top level `DOCUMENTATION.md` to expose it through MkDocs.

---

<!-- Re-imported content from root DOCUMENTATION.md -->

{{# copied content omitted in repo to avoid duplication - full content is in
root DOCUMENTATION.md }}
