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

Pruebas sugeridas
- Unit tests: formato JSON, escritura atómica, wait_for_ack comportamiento con ack presente/ausente.
- E2E: lanzar POC Python encolador y un proceso Lua (o mock consumer) que lee y emite ACK. Verificar timeout/retry.
- CI: agregar mock adapter para simular plugin en GitHub Actions y ejecutar tests E2E.

Checklist de despliegue
- [ ] Definir carpeta configurable y documentar permisos
- [ ] Añadir probe file escrito por plugin al iniciar (`plugin_loaded.txt`)
- [ ] Implementar lista persistente de `ids` procesados en plugin para idempotencia
- [ ] Configurar timeouts y política de reintentos (por defecto 3 reintentos)
- [ ] Añadir logs correlacionados por `id` y métricas (latencia enqueue→ack)

Problemas comunes y remedios
- Latencia: reducir polling y usar archivos por comando (no un único monolito).
- Concursos: uso de `os.replace` y tmp files para escrituras atómicas.
- Plugin no cargado: probe file + fallback GetData (documentado) + alertas en orquestador.

Siguiente pasos propuestos
1. Añadir POC funcional a `tools/poc_file_ack/` (Python enqueue + Lua consumer mock).
2. Añadir tests E2E y CI job que ejecute el mock.
3. Si OK, integrar adapter en el Orchestrator y exponer endpoint HTTP para la IA.

---

¿Quieres que cree ahora la carpeta `tools/poc_file_ack/` con los scripts POC y un test E2E en `tests/e2e/`? Si sí, los añado en la rama `wip/file-ack-poc` y abro PR. 👇