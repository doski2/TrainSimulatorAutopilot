# Registro de pasos — POC Archivo + ACK

Este documento recoge todos los pasos, comandos y decisiones tomadas en la
implementación del POC para el protocolo "Archivo + ACK".

Branch y PR

- Branch de trabajo: `wip/ack-implementation` (POC).  
- Pull Request: https://github.com/doski2/TrainSimulatorAutopilot/pull/8

Resumen de ficheros añadidos

- docs/docs controles/opcion1_archivo_ack.md — Especificación detallada.
- tools/poc_file_ack/enqueue.py — escritura atómica y wait_for_ack helper.
- tools/poc_file_ack/consumer.py — mock consumer que procesa comandos y escribe ack.
- tools/poc_file_ack/run_poc.py — demo que ejecuta POC (start consumer y encola un comando).
- tests/e2e/test_file_ack.py — test E2E que verifica enqueue → ack.

Comandos ejecutados (útiles para reproducir localmente)

1. Cambiar a la rama de trabajo (si no existe):

```powershell
# crea rama y cámbiate a ella (si no la tienes local)
git checkout -b wip/ack-implementation
```

2. Ejecutar demo local (daemon consumer + enqueue + wait for ack):

```powershell
# desde la raíz del repositorio; por defecto se usa un directorio temporal que se limpia al terminar
python tools/poc_file_ack/run_poc.py

# o especificar un directorio explícito (no será eliminado automáticamente):
python tools/poc_file_ack/run_poc.py --dir C:\ruta\a\mi\poc_dir
```

Ejecutar el demo de `enqueue` (envío con reintentos) desde la raíz del repo:

```powershell
# por defecto usa un directorio temporal para la demostración
python -m tools.poc_file_ack.enqueue

# o especificar un directorio persistente para inspección manual
python -m tools.poc_file_ack.enqueue --dir C:\ruta\a\mi\poc_dir
```

**Nota**: ambos demos usan un `TemporaryDirectory` por defecto para evitar crear carpetas en ubicaciones inesperadas; use `--dir` para pasar una ruta persistente si necesita inspeccionar archivos después de la ejecución.

3. Ejecutar test E2E individual:

```powershell
pytest tests/e2e/test_file_ack.py -q
```

4. Crear y subir cambios:

```powershell
git add <files>
git commit -m "poc(ack): ..."
git push origin wip/ack-implementation
```

Comportamiento del POC

- `enqueue.atomic_write_cmd(dir, payload)` escribe atómicamente
  `cmd-{id}.json` en el directorio.
- `consumer.Consumer` monitoriza el directorio, procesa comandos y escribe
  `ack-{id}.json` atómicamente tras procesarlos.
- `wait_for_ack(dir, id, timeout)` espera el fichero `ack-{id}.json` hasta
  que aparezca o se exceda el timeout.

Decisiones de diseño

- Usamos archivos por comando (cmd-{id}.json) para evitar condiciones de
  carrera y permitir ACK por id.
- Escritura atómica: se usa `os.replace(tmp, final)` para que no haya lecturas
  de archivos parcialmente escritos.
- El consumer marca ids procesados en memoria (set). Plan: persistir esos ids
  en disco para soportar restarts (tarea pendiente).

Pruebas y resultados

- El test `tests/e2e/test_file_ack.py` pasa localmente en Windows con Python 3.13.
- Se añadió `tests/unit/test_consumer_exceptions.py` para verificar que el consumer registra excepciones inesperadas y continúa ejecutando el bucle de polling.
- Se centralizó la configuración de import path para pytest en `tests/conftest.py` (ya no se insertan líneas `sys.path` en cada test).
- `.gitignore` fue actualizado para ignorar `tmp_poc_dir/` creado por ejecuciones manuales del consumer.

Checklist de mejoras pendientes (próximos pasos)

- [x] Implementar probe file en el consumer (`plugin_loaded.txt`) y listar
  comportamiento de readiness. (Implementado, test `tests/e2e/test_probe_file.py`)
- [x] Añadir retries/backoff al `enqueue` y tests relacionados. (Implementado: `send_command_with_retries`, tests `tests/e2e/test_retries.py`)
- [x] Persistir IDs procesados por el consumer para idempotencia. (Implementado: `processed_ids.json`, test `tests/e2e/test_persist_ids.py`)
- [x] Integrar el adapter con el Orchestrator (exponer POST /api/commands). (Implementado en `web_dashboard.py`, tests `tests/unit/test_api_commands.py`)
- [x] Añadir job en CI (GitHub Actions) que ejecute pruebas E2E del POC (subset de tests POC). (Implementado: `.github/workflows/poc-e2e.yml`)
- [x] Añadir UI mínima para disparar comandos y mostrar estado/ACK. (Implementado: botón en `index.html` + JS en `web/static/js/dashboard.js`)
- [x] Robustecer manejo de errores del consumer: ahora **registra** excepciones en vez de silenciarlas (test: `tests/unit/test_consumer_exceptions.py`).
- [x] Marcar y persistir IDs procesados antes de escribir el ACK para evitar reprocesos (implementado y probado: `tests/unit/test_consumer_race_condition.py`).
- [x] Centralizar la configuración de `sys.path` para pytest en `tests/conftest.py`.
- [x] Añadir `tmp_poc_dir/` a `.gitignore` para evitar commits accidentales de artefactos temporales.

Notas operativas

- Directorios y permisos: definir carpeta configurable para los archivos y
  documentar permisos (Windows: privilegios de usuario, UAC si procede).
- Observabilidad: logs correlacionados por `id` y métricas de latencia.
- Recomendación: en entornos de desarrollo y CI se recomienda `pip install -e .` para evitar depender de modificaciones de `sys.path` por tests.

¿Siguiente paso?

Dime si quieres que:

1. Implemente ahora el probe file en el consumer (marcaré la tarea como
   completada y continuaré con ello), o
2. Empiece por añadir retries y backoff en `enqueue`, o
3. Abra el PR inmediatamente para revisión del equipo (ya creado).  

Indica tu preferencia y procedo.  
