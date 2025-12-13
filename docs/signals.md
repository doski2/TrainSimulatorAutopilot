# Señales y estados de señalización

Este documento describe las variables de señalización expuestas por Train
Simulator Classic y cómo se procesan en el sistema TrainSimulatorAutopilot.

## Campos principales

- `SignalAspect`: Indicador del estado visible de la señal en vía. Valores:
  - `-1` = DESCONOCIDO
  - `0` = ROJA (STOP)
  - `1` = AMARILLA (CAUTION)
  - `2` = VERDE (PROCEED)

- `KVB_SignalAspect`: Variable para cab signalling (por ejemplo KVB o ATP).
Tiene los mismos valores que `SignalAspect`. Normalmente vale `-1` si no aplica.

- `senal_procesada`: Campo interno usado por la IA y la UI. Se normaliza el
valor y se prioriza `KVB_SignalAspect` si está presente (no `-1`). En caso
contrario se usa `SignalAspect`.

## Cómo se obtienen

- Los scripts Lua (p. ej. `complete_autopilot_lua.lua`) llaman a
`Call("GetControlValue", "SignalAspect")` y `Call("GetControlValue",
"KVB_SignalAspect")` para incluir los valores en la salida `GetData.txt`.

- `tsc_integration.py` mapea estos campos a `senal_principal` y
`senal_avanzada`, y agrega `senal_procesada` en la transformación
`convertir_datos_ia()`.

## Uso en la IA y reglas de seguridad

- Si `senal_procesada == 0` (ROJA), el sistema aplicará freno máximo. Esto está
implementado como la decisión `SEÑAL_ROJA_STOP` en `autopilot_system.py`.

- Si `senal_procesada == 1` (AMARILLA), el sistema aplica un freno leve y reduce
el objetivo de velocidad.

- Si `senal_procesada == 2` (VERDE), el sistema no aplica freno por señal y
continúa la lógica habitual de control de velocidad.

## Pruebas sugeridas

1. Simular un `GetData.txt` que incluya los controles de señal y verificar la
salida:
   - Crear `GetData_test.txt` con:

     ```text
     ControlName:SignalAspect
     ControlValue:0
     ControlName:KVB_SignalAspect
     ControlValue:-1
     ```

   - Ejecutar `tsc_integration` apuntando a ese archivo y comprobar que
`senal_procesada` toma el valor esperado.

2. Validar la UI:
   - Iniciar `web_dashboard.py` y observar `main-signal` y `distant-signal` en
el dashboard.
   - Usar `ws_client_test.py` para validar que el payload `telemetry_update`
contiene `senal_procesada`.

3. Validar la reacción del Autopilot: asegurar que `autopilot_system` aplica
`freno_tren=1.0` cuando `senal_procesada == 0`.

## Notas y recomendaciones

- `SignalAspect` puede variar según los paquetes de contenido; algunos usan el
prefijo `KVB_` para señales. Mapea varios nombres si es necesario.

- Para desactivar el auto-freno por señal durante pruebas, añade un flag
`autobrake_by_signal` en `config.ini` y cónsultalo desde `autopilot_system.py`.

---

Documentación: página Signals (señales) para referencia de desarrolladores y
probadores.
