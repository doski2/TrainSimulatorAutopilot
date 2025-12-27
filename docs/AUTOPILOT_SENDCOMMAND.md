# Autopilot → SendCommand (evidencia)

Resumen:

- Endpoint `POST /api/control/start_autopilot` escribe el comando
  `start_autopilot` en los archivos:
  - `SendCommand.txt` (ruta configurada en
    `TSCIntegration.ruta_archivo_comandos`)
  - `autopilot_commands.txt` (archivo que el plugin Lua lee)

Reproducción local (pasos):

1. Crear `GetData.txt` con telemetría mínima.
2. Configurar `TSCIntegration.ruta_archivo` y `ruta_archivo_comandos` a un directorio temporal.
3. Crear `autopilot_state.txt` con `on` para simular plugin responsive.
4. Llamar `POST /api/control/start_autopilot` vía `app.test_client()`.

Resultado observado:

- HTTP 200
- JSON:

  ```json
  { 'success': True,
    'action': 'start_autopilot',
    'autopilot_plugin_state': 'on' }
  ```

- `SendCommand.txt` y `autopilot_commands.txt` contienen
  `start_autopilot`.
- Cada archivo contiene el comando en su propia línea.
- Si `autopilot_state.txt` no existe o no cambia a `on`, la API **no**
  esperará y, por robustez, aplicará las líneas de fallback descritas más
  abajo.

Evidencia (ejemplo de salida capturada durante la prueba):

```text
--- SendCommand.txt content ---
start_autopilot

--- autopilot_commands.txt content ---
start_autopilot

--- autopilot_state.txt content ---
on
```

Notas operativas:

- `SendCommand.txt` es la versión en minúsculas destinada a
  compatibilidad con ciertos controladores (RailDriver).
- `autopilot_commands.txt` es el archivo que el plugin Lua realmente lee.
- Se escribe también por seguridad para que el plugin lo procese.
- Si quieres que documente el flujo de fallback con más detalle
  (timeouts, métricas y comportamiento ante plugin offline), lo añado
  en esta misma página.

## Confirmación por archivo — estado actual

**Nota:** La confirmación por archivo (`autopilot_state.txt`) **ya no** es
obligatoria y la API no espera confirmaciones del plugin Lua. El
endpoint `POST /api/control/start_autopilot` devuelve éxito
inmediatamente y aplica controles de fallback cuando es necesario.

- Razonamiento: en entornos reales la confirmación por archivo resultó
  poco fiable (plugin no cargado, errores de I/O en Windows). Esto podía
  provocar bloqueos y errores. Por robustez operativa preferimos no
  depender de este mecanismo (ver `CHANGELOG.md` y `docs/CONTROLS.md`).

- Consideración operativa: las variables de entorno antiguas relacionadas
  con la espera de confirmación (`AUTOPILOT_REQUIRE_ACK`) han quedado
  obsoletas y se ignoran por el servidor.

## Observación práctica: aceleración inicial

- En pruebas locales (cuando el plugin no estaba cargado o no respondió y
  la espera por ACK se omitió), el sistema aplica por defecto las líneas de
  fallback `Regulator:0.125` y `VirtualThrottle:0.125`.
  - Esto corresponde a un **12.5%** de acelerador (observado en juego como
    aproximadamente **13%**).

- Reproducción rápida:
  1. Asegúrate de que no exista `autopilot_state.txt` en la carpeta `plugins/`.
  2. Llama `POST /api/control/start_autopilot` desde `app.test_client()` o `curl`.
  3. Comprueba `plugins/SendCommand.txt` y
   `plugins/autopilot_commands.txt` — deben contener `start_autopilot` y las
   líneas de fallback `Regulator:0.125` y `VirtualThrottle:0.125`.
  4. En el simulador observa que la velocidad aumenta ligeramente (~13%).

- Nota: si prefieres otro valor de inicio, se puede modificar la
  constante de fallback en `tsc_integration.py` o exponerla vía
  configuración (`AUTOPILOT_START_THROTTLE`) en una futura mejora.
