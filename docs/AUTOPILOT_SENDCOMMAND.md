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
