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

### Archivos Modificados (Fuel)

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

## 3. Mejora: Lista Completa de Alertas Activas y Dedupe en UI

### Descripción (Alertas completas)

- Se añadió `active_alerts_list` al payload `telemetry_update` como arreglo
  completo de alertas activas (objetos).

  El dashboard ahora prefiere `active_alerts_list` si está presente y
  realiza un dedupe de alertas por clave `type+title` para evitar
  notificaciones repetidas.

### Implementación (Alertas)

- **Backend**: `alert_system.py` añade `active_alerts_list` al payload
  `telemetry_update`.
- **Frontend**: `web/static/js/dashboard.js` adopta la preferencia por
  `active_alerts_list`, realiza dedup con `knownAlertKeys` y muestra
  notificaciones sticky sólo cuando una alerta nueva aparece.

### Beneficio (Alertas)

- Evita spam de notificaciones y asegura la visualización consistente de
  alertas que ya fueron mostradas.

## 4. Mejora: Auto-resolución de Alertas Transitorias

### Descripción (Auto-resolución)

- Alertas transitorias (wheelslip, speed_violation, overheating menor) pueden
  auto-resolverse cuando la telemetría ya no satisface la condición; el
  sistema ahora marca estas alertas como `acknowledged` cuando el estado
  vuelve a normal.

### Implementación (Auto-resolución)

- `alert_system.py` guarda `last_telemetry` y ejecuta
  `_resolve_transient_alerts` tras cada ciclo de monitoreo.

### Beneficio (Auto-resolución)

- Reduce alertas persistentes y evita la necesidad de acción manual para
  condiciones que desaparecieron por sí solas.

## 5. Eliminación del Soporte de Combustible (Fuel)

### Descripción (Fuel)

- FuelLevel y métricas relacionadas fueron marcadas como NO IMPLEMENTADO y
  removidas del flujo importante del sistema (alertas, UI, procesamiento).

  Se añadió un script de limpieza, `scripts/cleanup_persisted_fuel.py`, para
  purgar entradas históricas relacionadas con `FuelLevel`.

### Archivos Modificados

- `tsc_integration.py`, `tsc_integration_optimized.py`: eliminación de
   mapeo/métricas de combustible
- `web/static/js/dashboard.js`, `web/templates` y `sd40` templates:
   eliminación de UI/alertas de combustible
- `alert_system.py`: eliminación de `check fuel_low` y limpieza de alertas
   persistentes
- `scripts/cleanup_persisted_fuel.py`: script para limpiar
   alertas/telemetría histórica

### Notas

- El campo `FuelLevel` sigue presente en GetData proveniente de Railworks
  para compatibilidad, pero no se utiliza en la lógica del piloto automático
  para TSC.

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
