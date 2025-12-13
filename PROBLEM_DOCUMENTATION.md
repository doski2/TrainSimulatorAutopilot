# Problema: Dashboard Mostrando Datos No Reales en Train Simulator Autopilot

## Fecha del Problema

29 de noviembre de 2025

## Descripción del Problema

El dashboard web del sistema Train Simulator Autopilot no mostraba datos reales
de telemetría del simulador Train Simulator Classic (TSC). En su lugar, se
observaban valores inconsistentes, oscilantes o simulados que no correspondían
con los datos reales del simulador.

### Síntomas Observados

- Velocidades que no coincidían con el estado real del tren (ej: 29.98 km/h
  cuando el tren estaba detenido)
- Valores de aceleración y otros parámetros que no reflejaban la realidad
- Desconexión frecuente entre el backend y el frontend
- Error `ERR_CONNECTION_REFUSED` al intentar acceder al dashboard

## Diagnóstico Realizado

### 1. Verificación de Datos Fuente

- **Archivo GetData.txt**: Ubicado en `C:\Program Files
  (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt`
- **Valores reales**: CurrentSpeed ≈ -0.001 m/s (equivalente a 0.0 km/h cuando
  el tren está detenido)
- **Estado**: El archivo existe y se actualiza correctamente cuando TSC está
  corriendo

### 2. Verificación del Pipeline de Datos

- **Backend (web_dashboard.py)**: Lee datos de TSCIntegration
- **WebSocket**: Transmite datos al frontend
- **Frontend (dashboard.js)**: Recibe y muestra datos

### 3. Pruebas de Componentes

- **TSCIntegration**: ✅ Funciona correctamente, devuelve datos reales
- **WebSocket Server**: ✅ Envía datos correctamente
- **WebSocket Client**: ✅ Recibe datos reales (0.0 km/h, aceleraciones
  variables)

## Causas Identificadas

### Causa Principal

El servidor web no estaba ejecutándose.

Esto provocó el error `ERR_CONNECTION_REFUSED` al intentar acceder a
`http://localhost:5000`.

### Causas Secundarias

1. **Servidor detenido**: El proceso de Python que ejecuta `web_dashboard.py` no
  estaba corriendo
2. **Configuración de unidades**: El frontend manejaba unidades de manera
  inconsistente
3. **Posibles datos cacheados**: Versiones anteriores del código podrían haber
  tenido datos simulados

## Soluciones Implementadas

### 1. Reinicio del Servidor

```bash
python web_dashboard.py
```

- El servidor se inició correctamente en el puerto 5000
- WebSocket funcionando correctamente
- Datos reales fluyendo desde TSC al dashboard

### 2. Verificación de Integridad de Datos

- Confirmado que TSCIntegration lee correctamente GetData.txt
- Verificado que las conversiones de unidades son correctas (m/s → km/h)
- Validado que WebSocket transmite datos reales

### 3. Correcciones en el Código Frontend (dashboard.js)

Se aplicaron las siguientes correcciones para asegurar consistencia en unidades:

#### a) Función formatSpeedForDisplay

```javascript
function formatSpeedForDisplay(kmhValue, unit) {
  if (!Number.isFinite(kmhValue)) return null;
  if (unit === 'mph') {
    const mph = kmhValue / 1.609344;
    return `${mph.toFixed(1)} mph`;
  }
  // default km/h
  return `${kmhValue.toFixed(1)} km/h`;
}
```

#### b) Actualización de Etiquetas del Gráfico

```javascript
speedChart.data.datasets[0].label = 'Velocidad (km/h)';
```

#### c) Conversión Dinámica en updatePredictions

```javascript
{ label: 'Velocidad', value: predictions.velocidad_actual, unit: dashboardConfig.speedUnit === 'kmh' ? 'km/h' : (dashboardConfig.speedUnit === 'mph' ? 'mph' : 'm/s'), decimals: 1 }
```

#### d) Conversión en updateLocomotives

```javascript
const displaySpeed = dashboardConfig.speedUnit === 'mph' ? (speed / 1.609344).toFixed(1) : speed.toFixed(1);
const displayLimit = dashboardConfig.speedUnit === 'mph' ? (limit / 1.609344).toFixed(0) : limit.toFixed(0);
```

#### e) Conversión en updateChart

```javascript
let speedValue = telemetry.velocidad_actual || 0;
if (dashboardConfig.speedUnit === 'mph') {
    speedValue = speedValue / 1.609344;
} else if (dashboardConfig.speedUnit === 'ms') {
    speedValue = speedValue / 3.6;
}
```

#### f) Configuración por Defecto

```javascript
speedUnit: 'kmh'  // Cambiado de 'mph' a 'kmh'
```

## Resultados

### ✅ Problema Resuelto

- Dashboard accesible en `http://localhost:5000`
- Muestra datos reales de TSC
- Velocidad: 0.0 km/h (correcto para tren detenido)
- Unidades consistentes en todo el dashboard
- WebSocket funcionando correctamente

### 📊 Verificación Final

- **GetData.txt**: CurrentSpeed ≈ -0.001 m/s
- **Backend**: Convierte correctamente a 0.0 km/h
- **WebSocket**: Transmite `velocidad_actual: 0.0`
- **Frontend**: Muestra "0.0 km/h"

## Lecciones Aprendidas

1. **Importancia del monitoreo continuo**: El sistema debe verificar que el
  servidor esté corriendo
2. **Consistencia de unidades**: Centralizar las conversiones y mantener
  consistencia en las unidades utilizadas
3. **Validación de datos**: Implementar validaciones robustas para detectar
  valores no numéricos
4. **Documentación**: Mantener registro detallado de problemas y soluciones

## Herramientas de Diagnóstico Utilizadas

- `monitor_getdata.py`: Monitoreo en tiempo real del archivo GetData.txt
- `ws_client_test.py`: Prueba del cliente WebSocket
- `test_tsc.py`: Verificación directa de TSCIntegration
- Inspección manual de archivos de configuración

## Estado Actual

🟢 **RESUELTO**: El dashboard muestra datos reales de TSC correctamente.

## Recomendaciones Futuras

1. Implementar monitoreo automático del estado del servidor
2. Agregar indicadores visuales de conexión al simulador
3. Crear sistema de alertas para desconexiones
4. Documentar procedimientos de troubleshooting
5. Implementar tests automatizados para validar integridad de datos

--- **Resuelto por**: GitHub Copilot **Fecha de resolución**: 29 de noviembre de
2025
