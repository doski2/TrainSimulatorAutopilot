# Train Simulator Autopilot — Controls guide

Formato de comandos para control directo

- El plugin Lua acepta líneas en formato `ControlName:value`.
  Estas se escriben en `plugins/autopilot_commands.txt`.

  - Ejemplos:

    - `Regulator:0.500` — establece el controlador `Regulator` a 0.5
      (float entre 0 y 1).

    - `TrainBrakeControl:1.000` — aplica freno a 1.0.

    - `Headlights:true` — activa las luces
      (booleans aceptados: `true`/`false`).

- Formas de enviar comandos:
  1. Desde Python (API REST):
     - POST `/api/control/set` con JSON, por ejemplo:
       `{ "control": "Regulator", "value": 0.5 }`.
     - Respuesta de ejemplo:
       `{ "success": true, "control": "Regulator", "value": 0.5 }`.
     - Este endpoint usa `TSCIntegration.enviar_comandos`.
     - Escribe atómicamente el archivo que lee el plugin Lua.
     - **Esquema y ejemplos detallados:** ver `docs/API.md` (nuevo).

  2. Escribir directamente en `plugins/autopilot_commands.txt`.
     (solo para pruebas).
     Cada línea será procesada por el plugin cuando el motor
     esté en ejecución.

Notas de seguridad y robustez

- El plugin intenta parsear valores numéricos (tonumber) y
  booleanos (`true`/`false`).
- Aplica internamente `PlayerEngineSetControlValue` para aplicar los valores.
- El endpoint REST `POST /api/control/set` valida el nombre del control y rechazará
  nombres que contengan `:` o caracteres de control (por ejemplo `\n`, `\r`, NUL)
  para prevenir inyección en el protocolo basado en archivos.
- Asegúrate de que el simulador esté cargado y la escena tenga `engine key`.
  Esto permite que el plugin procese las líneas.
- El plugin escribe logs en `plugins/autopilot_debug.log`.

Ejemplo en curl

```bash
curl -X POST "http://localhost:5001/api/control/set" \
  -H "Content-Type: application/json" \
  -d '{"control":"Regulator","value":0.45}'
```

## Nuevas mejoras (control y compatibilidad) ✅

**Resumen:** Si el plugin Lua no está cargado, cualquier directiva
`start_autopilot` o `autopilot:true` enviada se complementará con controles
reales que el TSClassic Interface o controles legacy puedan entender.
Por ejemplo: `Regulator:0.125` y `VirtualThrottle:0.125`.

Además, la IA ajusta (snap-to-notch) los valores de `acelerador` a muescas
discretas para compatibilidad con activos que esperan pasos discretos.

### Comportamiento añadido 🔧

- Escritura múltiple de destinos de control:
  - `plugins/SendCommand.txt` (TSClassic Interface) — ahora se escribe para
    compatibilidad con la interfaz x64.
  - `plugins/sendcommand.txt` — archivo legacy también escrito por
    compatibilidad.
  - `plugins/autopilot_commands.txt` — usado por el plugin Lua cuando
    está activo.
    (Opcional: controlado por `write_lua_commands`).

- Fallback `start_autopilot`:
  - Si se envía `start_autopilot` y `autopilot_plugin` **no está cargado**:
    `TSCIntegration` añade las siguientes líneas de respaldo:
    - `Regulator:0.125`  (≈12.5% de acelerador — observado como ~13% en pruebas)
    - `VirtualThrottle:0.125` (mismo valor aplicado como fallback)
  - Esto permite que el TSClassic Interface aplique una muesca inicial
    y que el tren comience a reaccionar.

- Snap-to-notch (ajuste a muescas):
  - La IA redondea el valor de `acelerador` a la muesca más
    cercana antes de escribir los archivos.
  - Tabla de muescas por defecto:
    `[0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]`.
  - Política: en empate, se elige la muesca superior
    (favorecer movimiento).
  - Es configurable en tiempo de ejecución mediante
    `TSCIntegration.throttle_notches` o en la configuración
    del sistema.

### Pruebas añadidas ✅

- `tests/unit/test_tsc_interface_write.py`
  - `test_write_to_tsc_interface_file`
    — validación de escritura a `SendCommand.txt`.
  - `test_acelerador_writes_both_regulator_and_virtualthrottle`
    — `acelerador` escribe ambos controles.
  - `test_start_autopilot_fallback_when_plugin_not_loaded`
    — confirma fallback cuando el plugin no está cargado.
  - `test_acelerador_snaps_to_nearest_notch`
    — valida comportamiento snap-to-notch.

Puedes ejecutar las pruebas con:

```bash
python -m pytest tests/unit/test_tsc_interface_write.py -q
```

### Cómo validar in situ (pasos rápidos) 🎮

1. Asegúrate de que `TSClassic Interface` (x64) esté ejecutándose si lo usas.
2. Desde el dashboard o con `curl` envía un comando de autopilot o acelerador:
   - `POST /api/control/set` con JSON. Ejemplos:

     ```json
     {"control": "autopilot", "value": true}
     ```

     ```json
     {"control": "acelerador", "value": 0.19}
     ```

3. Comprueba los archivos `plugins/SendCommand.txt` y
   `plugins/sendcommand.txt` para ver las líneas escritas.
4. Si el plugin Lua no está cargado, verás líneas de
   fallback (`Regulator:0.125` y `VirtualThrottle:0.125`).
   Cuando el plugin está cargado, la directiva
   `start_autopilot` la gestionará directamente.
5. Confirma en el juego que la muesca aplicada produce movimiento.
   Si no funciona, revisa `plugins/autopilot_debug.log` y
   confirma si `autopilot_plugin_loaded.txt` existe.

---

## Cambios: ACK eliminado y diagnóstico 🩺

- El soporte de ACK para la confirmación del plugin Lua ha sido **eliminado** del proyecto. `POST /api/control/start_autopilot` **ya no** requiere `autopilot_state.txt` ni espera confirmaciones.
- Razonamiento:
  - En entornos reales encontramos que el plugin no siempre se cargaba y que las escrituras a archivos fallaban por permisos o bloqueo (`Access denied` / `file locked`), lo que hacía que la dependencia del ACK provocara llamadas bloqueadas y errores en producción.
  - Para aumentar la robustez operativa y evitar bloqueos, eliminamos la dependencia del ACK y aplicamos controles de fallback (`Regulator:0.125`, `VirtualThrottle:0.125`) cuando el plugin no procesa directamente `start_autopilot`.
- Qué cambia para operadores:
  1. `POST /api/control/start_autopilot` devuelve éxito inmediatamente y escribe los comandos necesarios.
  2. El plugin Lua puede seguir siendo usado si está disponible; el sistema escribirá `autopilot_commands.txt` como antes.
  3. Las métricas relacionadas con el ACK han sido removidas del panel (p. ej. `ack_skipped_total` y `unacked_total`).

**Diagnóstico rápido:**

1. Revisa `tsc_autopilot.log` para confirmaciones de escritura y errores tipo `Access denied` o `file locked`.
2. Confirma la presencia del plugin y su carga (`autopilot_plugin_loaded.txt`) si lo necesitas para debugging.
3. Si quieres, puedo crear un script de diagnóstico que capture logs, archivos y permisos para facilitar el soporte en entornos Windows.

---

> **Nota:** Estas medidas mejoran la robustez cuando el plugin Lua
> no responde o no está cargado.
> En entornos con el plugin activo, la comunicación preferible es
> `autopilot_commands.txt`.

---

Documentación actualizada por **GitHub Copilot** en la rama
`copilot/implement-plugin-controls`.

Si quieres, puedo agregar una sección en `config.ini.example`
para exponer la tabla de muescas como opción configurable.
