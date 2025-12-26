API — Endpoints relevantes

POST /api/control/set
---------------------
Establece un valor para un control del tren.

Request JSON schema (informal):
- control: string (REQUIRED)
  - Debe ser una cadena imprimible, **no** vacía tras aplicarse `.strip()`
  - **No** puede contener `:`, saltos de línea (`\n`, `\r`) ni NUL (`\x00`)
  - Máx. 100 caracteres
- value: number (int/float) | boolean | string (REQUIRED)
  - Tipos permitidos: boolean, int, float, str
  - Tipos no permitidos: list, dict, object complejo

Responses:
- 200 OK: {"success": true, "control": <control>, "value": <value>} — comando aceptado y enviado a TSCIntegration
- 400 Bad Request: {"success": false, "error": "..."} — payload inválido o validación fallida
- 500 Internal Server Error: {"success": false, "error": "..."} — integración TSC no disponible o fallo al enviar

Examples
--------
- Set numeric value (regulator to 0.45):

  curl -X POST "http://localhost:5001/api/control/set" \
    -H "Content-Type: application/json" \
    -d '{"control":"Regulator","value":0.45}'

- Set boolean value (enable autopilot flag):

  curl -X POST "http://localhost:5001/api/control/set" \
    -H "Content-Type: application/json" \
    -d '{"control":"autopilot","value":true}'

- Set string value (custom command):

  curl -X POST "http://localhost:5001/api/control/set" \
    -H "Content-Type: application/json" \
    -d '{"control":"command","value":"emergency_brake"}'

Notes
-----
- El endpoint aplica validaciones para evitar inyección en el protocolo de control en archivos (p. ej., `plugins/autopilot_commands.txt`).
- **Rate limiting:** el endpoint está protegido por límites por IP para mitigar abuso. El límite por defecto es `60/minute` y puede configurarse mediante la variable de entorno `CONTROL_RATE_LIMIT` o `app.config['CONTROL_RATE_LIMIT']`.
- Si necesitas controles con nombres especiales, adapta el mapeo en `TSCIntegration` y documenta los nombres permitidos.
