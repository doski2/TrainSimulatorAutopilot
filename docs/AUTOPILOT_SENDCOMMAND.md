# Autopilot → SendCommand (evidencia)

Resumen:

- Endpoint `POST /api/control/start_autopilot` escribe el comando
  `start_autopilot` en los archivos:
  - `SendCommand.txt` (ruta configurada en `TSCIntegration.ruta_archivo_comandos`)
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

- `SendCommand.txt` y `autopilot_commands.txt` contienen `start_autopilot`.
- Cada archivo contiene el comando en su propia línea.
- Si `autopilot_state.txt` no existe o no cambia a `on` dentro de
  `AUTOPILOT_ACK_TIMEOUT`, la API espera (por defecto), retorna 504 y
  registra la métrica `autopilot_metrics['unacked_total']++`.

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
- Si quieres que documente el flujo ACK/fallback con más detalle
  (timeouts, métricas y comportamiento ante plugin offline), lo añado
  en esta misma página.
## Notas sobre ACK y configuración

- Si `autopilot_state.txt` no aparece o no cambia a `on` dentro de
  `AUTOPILOT_ACK_TIMEOUT`, la API **por defecto NO espera** y devuelve éxito inmediato. Si quieres que la API espere por ACK, activa la variable de entorno `AUTOPILOT_REQUIRE_ACK=true`.
  - Si `AUTOPILOT_REQUIRE_ACK=true` y no llega ACK en tiempo, la API devolverá 504 e incrementará `autopilot_metrics['unacked_total']`.  
  - Si `AUTOPILOT_REQUIRE_ACK=false` (por defecto), la métrica `autopilot_metrics['ack_skipped_total']` se incrementará para indicar que la espera fue omitida.
- Para entornos donde el plugin no puede cargar o no es fiable,
  puedes desactivar la espera globalmente con:

  ```bash
  export AUTOPILOT_REQUIRE_ACK=false
  ```

  - Cuando se desactiva, `POST /api/control/start_autopilot` retornará
    200 inmediatamente y la métrica `autopilot_metrics['ack_skipped_total']`
    se incrementará para indicar que la espera fue omitida.

## Observación práctica: aceleración inicial

- En pruebas locales (cuando el plugin no estaba cargado o no respondió y la espera por ACK se omitió), el sistema aplica por defecto las líneas de fallback `Regulator:0.125` y `VirtualThrottle:0.125`.
  - Esto corresponde a un **12.5%** de acelerador (observado en juego como aproximadamente **13%**).

- Reproducción rápida:
  1. Asegúrate de que no exista `autopilot_state.txt` en la carpeta `plugins/`.
  2. Establece la variable de entorno `AUTOPILOT_REQUIRE_ACK=false` y reinicia el dashboard.
  3. Llama `POST /api/control/start_autopilot` desde `app.test_client()` o `curl`.
  4. Comprueba `plugins/SendCommand.txt` y `plugins/autopilot_commands.txt` — deben contener `start_autopilot` y las líneas de fallback `Regulator:0.125` y `VirtualThrottle:0.125`.
  5. En el simulador observa que la velocidad aumenta ligeramente (~13%).

- Nota: si prefieres otro valor de inicio, se puede modificar la constante de fallback en `tsc_integration.py` o exponerla vía configuración (`AUTOPILOT_START_THROTTLE`) en una futura mejora.

