# Correcciones Dashboard - 2 de diciembre de 2025

## Resumen de Problemas Corregidos

Este documento registra las correcciones implementadas en el dashboard web del
sistema Train Simulator Autopilot durante diciembre de 2025.

## 1. Problema: Esfuerzo de Tracción No Se Mostraba

### Descripción del Problema (Esfuerzo de Tracción)

- El campo `TractiveEffort` del RailDriver no estaba disponible inicialmente
para la locomotora en uso
- Cuando el campo sí estaba disponible, se mostraba como "0 kN" debido al
redondeo con `toFixed(0)`
- Los valores pequeños (ej: 233.974 N = 0.2 kN) se redondeaban a 0

### Solución Implementada (Esfuerzo de Tracción)

1. **Valor por defecto**: Agregado `esfuerzo_traccion: 0.0` en
`tsc_integration.py` cuando el campo no está disponible
2. **Cambio de unidades**: Modificado para mostrar en Newtons (N) en lugar de
kiloNewtons (kN)
3. **Actualización de etiqueta**: Cambiada la etiqueta HTML de "(kN)" a "(N)"

### Archivos Modificados

- `tsc_integration.py`: Línea ~190, agregado valor por defecto
- `web/static/js/dashboard.js`: Líneas 318-322, cambio de kN a N
- `web/templates/index.html`: Línea 273, cambio de etiqueta

### Resultado (Esfuerzo de Tracción)

- **Antes**: 233.974 N → "0 kN" (confuso)
- **Después**: 233.974 N → "234 N" (claro y significativo)

## 2. Problema: Error "alerts no es un array"

### Descripción del Problema (Alertas)

- El backend enviaba `active_alerts` como objeto:
`{new_alerts: 0, active_alerts: 27, alerts: Array(0)}`
- El JavaScript esperaba un array directo, causando error:
`alerts no es un array: object`

### Solución Implementada (Alertas)

Modificación de la función `updateActiveAlerts()` en `dashboard.js` para manejar
ambos formatos:

- Array directo (formato antiguo)
- Objeto con propiedad `alerts` (formato nuevo)

### Código Modificado

```javascript
function updateActiveAlerts(alertsData) {
  let alerts = [];
  if (Array.isArray(alertsData)) {
    alerts = alertsData;
  } else if (
    alertsData &&
    typeof alertsData === 'object' &&
    Array.isArray(alertsData.alerts)
  ) {
    alerts = alertsData.alerts;
  }
  // ... resto del código
}
```

### Resultado (Alertas)

- Eliminado el error de JavaScript
- Las alertas se muestran correctamente
- Compatible con ambos formatos de datos

## 3. Mejoras en la Visualización de Datos

### Unidades Consistentes

- **Esfuerzo de tracción**: N (Newtons) - más legible para valores pequeños
- **Presiones de freno**: PSI (libras por pulgada cuadrada)
- **Velocidad**: km/h (kilómetros por hora)
- **RPM**: revoluciones por minuto
- **Amperaje**: A (amperios)

### Manejo de Valores Nulos

- Todos los campos tienen valores por defecto cuando no están disponibles
- Se muestra "--" en la UI cuando los datos no están disponibles
- Logging mejorado para debugging

## 4. Verificación del Sistema

### Estado Actual

- ✅ Sistema configurado para datos reales del RailDriver
- ✅ Esfuerzo de tracción se muestra correctamente en N
- ✅ Alertas funcionan sin errores
- ✅ Todos los campos de telemetría se procesan correctamente

## 5. Notas Técnicas

### Dependencias del RailDriver

- Diferentes locomotoras pueden proporcionar diferentes campos
- `TractiveEffort` puede no estar disponible en todas las locomotoras
- El sistema maneja gracefully la ausencia de campos

### Formato de Datos

- Backend envía datos en formato JSON vía WebSocket
- Frontend actualiza DOM en tiempo real cada 100ms
- Campos opcionales tienen valores por defecto

## Fecha de Implementación

- **2 de diciembre de 2025**
- **Versión**: v2.1.0-dashboard-fixes
