Train Simulator Autopilot — Controls guide

Formato de comandos para control directo

- El plugin Lua acepta líneas en formato `ControlName:value` en `plugins/autopilot_commands.txt`.
  - Ejemplos:
    - `Regulator:0.500`  — establece el controlador `Regulator` a 0.5 (float entre 0 y 1)
    - `TrainBrakeControl:1.000` — freno a valor 1.0
    - `Headlights:true` — activa las luces (booleans aceptados: `true`/`false`)

- Formas de enviar comandos:
  1. Desde Python (API REST): POST /api/control/set con JSON { "control": "Regulator", "value": 0.5 }
     - Respuesta: { "success": true, "control": "Regulator", "value": 0.5 }
     - Este endpoint usa `TSCIntegration.enviar_comandos` y escribe atómicamente el archivo que lee el plugin Lua.

  2. Escribir directamente en `plugins/autopilot_commands.txt` (solo para pruebas): cada línea será procesada por el plugin cuando el motor esté en ejecución.

Notas de seguridad y robustez

- El plugin intenta parsear valores numéricos (tonumber) y booleanos (`true`/`false`), y aplica `PlayerEngineSetControlValue` internamente.
- Asegúrate de que el simulador esté cargado y la escena tenga `engine key` para que el plugin procese las líneas (el plugin escribe logs en `plugins/autopilot_debug.log`).

Ejemplo en curl

curl -X POST "http://localhost:5001/api/control/set" \
  -H "Content-Type: application/json" \
  -d '{"control":"Regulator","value":0.45}'

---
Documentación añadida por GitHub Copilot para la rama `copilot/implement-plugin-controls`.