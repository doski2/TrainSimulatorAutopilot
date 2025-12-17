# Opción 1 — Protocolo basado en archivos con ACK (especificación)

Resumen

Esta especificación documenta la solución “Archivo + ACK” para permitir que la IA o el servicio local envíen comandos al simulador por archivo y reciban confirmación (ACK) cuando el plugin del juego los procesa.

Objetivos
- Proveer un protocolo sencillo, auditable y robusto para enviar comandos.
- Minimizar condiciones de carrera mediante escritura atómica y archivos "por comando".
- Asegurar idempotencia y reintentos con IDs y timestamps.

Directorio y convenciones
- Carpeta principal preferida: `plugins/ts_autopilot/` (configurable).
- Comandos se escriben como archivos individuales: `cmd-{id}.json`.
- ACKs creados por el plugin: `ack-{id}.json`.
- Archivos temporales: escribir en `tmp/` y renombrar (atomic `os.replace`).

Formato de comando (recomendado)
- JSON por archivo, ejemplo:

```json
{
  "id": "cmd-001",
  "type": "set_regulator",
  "value": 0.4,
  "ts": 1700000000,
  "meta": { "source": "orchestrator" }
}
```

Formato de ACK (recomendado)

```json
{
  "id": "cmd-001",
  "status": "applied",  // applied | failed
  "ts": 1700000001,
  "notes": "Regulator set to 0.4"
}
```

Semántica y garantías
- Escritura atómica: orquestador escribe en `tmp/cmd-{id}.tmp` y hace `os.replace(tmp, target)`.
- Idempotencia: plugin mantiene una lista (persistente en memoria o archivo) de `ids` ya procesados y descarta duplicados.
- Reintentos: orquestador espera ACK con timeout configurado (ej. 5s), reintenta hasta N veces y luego marca "failed".
- Orden: los comandos son independientes (por id). Si se necesita orden, añadir campo `sequence` y lógica de consumidor para aplicar en orden.

Ejemplo de flujo (pasos)
1. Orquestador crea `cmd-{id}.json` con datos.
2. Plugin detecta archivo, lo lee, valida `id` y ejecuta comando.
3. Plugin escribe `ack-{id}.json` con estado.
4. Orquestador observa `ack-{id}.json` y marca comando como `applied` o `failed`.

Implementación POC — Python (enqueue + wait_for_ack)

```python
# tools/poc_file_ack/enqueue.py (POC)
import json, os, time, uuid

def atomic_write_cmd(dirpath, payload):
    cmd_id = payload.get('id') or str(uuid.uuid4())
    payload['id'] = cmd_id
    tmp = os.path.join(dirpath, f"cmd-{cmd_id}.tmp")
    final = os.path.join(dirpath, f"cmd-{cmd_id}.json")
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(json.dumps(payload, ensure_ascii=False))
    os.replace(tmp, final)
    return cmd_id


def wait_for_ack(dirpath, cmd_id, timeout=5.0):
    ack = os.path.join(dirpath, f"ack-{cmd_id}.json")
    end = time.time() + timeout
    while time.time() < end:
        if os.path.exists(ack):
            with open(ack, 'r', encoding='utf-8') as f:
                return json.load(f)
        time.sleep(0.1)
    return None
```

Implementación POC — Lua (consumidor simplificado)

```lua
-- plugins/ts_autopilot/consumer.lua (pseudocódigo)
function read_command(path)
  -- leer archivo JSON, parsear (implementación dependiente de entorno Lua)
end

function write_ack(dirpath, id, status, notes)
  local ack = {
    id = id,
    status = status,
    ts = os.time(),
    notes = notes
  }
  local f = io.open(dirpath .. '/ack-' .. id .. '.json', 'w')
  if f then
    f:write(require('json').encode(ack))
    f:close()
  end
end

function Update(elapsed)
  -- cada N ms: listar archivos cmd-*.json, por cada uno:
  -- 1) validar id no procesado
  -- 2) aplicar comando (ej. SetRegulator(value))
  -- 3) write_ack(...)
end
```

Operación y manejo de errores (consideraciones operativas)

- Manejo de excepciones: el consumidor (plugin o mock) no debe silenciar excepciones genéricas; en el POC el consumidor ahora usa `logging.exception(...)` para registrar fallos inesperados y continuar ejecutando el bucle de polling. Esto facilita debugging y evita perder fallos silenciosos.
- Persistencia y resiliencia: el consumer persiste IDs procesados en `processed_ids.json` para evitar reprocesos después de reinicios. Se recomienda revisar permisos y rotación de este archivo en producción.
- Probe & readiness: el plugin escribe `plugin_loaded.txt` al iniciarse (contiene timestamp); el orquestador puede comprobar la existencia de este fichero antes de confiar en la recepción de comandos en caliente.
- Archivos temporales: use `tmp` + `os.replace` para escrituras atómicas y evitar lecturas parciales.

- Orden seguro de procesamiento: **Importante** — para evitar condiciones de carrera el consumer debe **marcar el id como procesado y persistirlo antes de escribir el ACK**. De esta forma, si la eliminación del archivo de comando falla o el proceso se interrumpe justo después de escribir el ACK, el reinicio del consumer no reprocesará el comando duplicadamente. Esta práctica está implementada en el POC y cubierta por tests (`tests/unit/test_consumer_race_condition.py`).

- Manejo de archivos malformados/duplicados: cuando el consumer encuentra un archivo de comando que carece del campo `id` o cuyo `id` ya está marcado como procesado, el proceso ahora **registra una advertencia** y elimina el archivo para evitar confusión y facilitar el diagnóstico. Esto está probado en `tests/unit/test_consumer_ignore_malformed_or_duplicate.py`.

- Bounded processed-ids cache: para evitar crecimiento ilimitado en memoria, el consumer mantiene una caché LRU-like de IDs procesados con un tamaño configurable (`processed_ids_max`, por defecto 10000). Las entradas más antiguas se evictan cuando se supera el límite. Implementado y probado en `tests/unit/test_consumer_bounded_processed_set.py`.

Pruebas y CI (qué está presente hoy)

- Tests añadidos:
  - Unit: `tests/unit/test_consumer_exceptions.py` valida que excepciones en persistencia se registren y que el consumidor siga funcionando.
  - E2E POC: `tests/e2e/test_file_ack.py`, `tests/e2e/test_probe_file.py`, `tests/e2e/test_retries.py`, `tests/e2e/test_persist_ids.py` (comprueban enqueue→ack, probe, retries y persistencia respectivamente).
  - API: `tests/unit/test_api_commands.py` verifica el endpoint `POST /api/commands` con y sin espera por ACK.
- CI: existe un job específico para el POC `/.github/workflows/poc-e2e.yml` que ejecuta el subconjunto E2E POC en PRs a la rama del POC.
- Configuración de tests: se centralizó la manipulación de `sys.path` en `tests/conftest.py` en lugar de insertar `sys.path` en cada test; esto hace las importaciones más robustas y coherentes en CI y desarrollo local.

Checklist de despliegue (estado actual)
- [x] Definir carpeta configurable y documentar permisos (documentado en instalación) 
- [x] Añadir probe file escrito por plugin al iniciar (`plugin_loaded.txt`) 
- [x] Implementar lista persistente de `ids` procesados por consumer (`processed_ids.json`) 
- [x] Configurar timeouts y política de reintentos (por defecto: la POC implementa retries/backoff con parámetros configurables)
- [x] Añadir logs correlacionados por `id` y métricas (latencia enqueue→ack) — POC introduce logging básico y es sugerible extender con métricas
- [x] Manejo de excepciones: el consumer ahora registra errores en vez de silenciarlos

Problemas comunes y remedios
- Latencia: reducir polling y usar archivos por comando (no un único monolito).
- Concursos: uso de `os.replace` y tmp files para escrituras atómicas.
- Plugin no cargado: probe file + fallback GetData (documentado) + alertas en orquestador.

Siguientes pasos propuestos

1. Pulir el endpoint `POST /api/commands` para añadir autenticación y validación más estricta (por ejemplo, API key o JWT).
2. Monitorización y métricas (exponer latencias enqueue→ack y recuento de excepciones en consumer).
3. Integración completa del plugin en escenarios reales y añadir tests de integración que ejecuten escenarios de la vida real.

---

¿Quieres que cree ahora la carpeta `tools/poc_file_ack/` con scripts POC y abra PR (si no lo está ya)? Si sí, lo dejo listo en `wip/ack-implementation` para revisión.