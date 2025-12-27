# PoC File+ACK — Deprecated

Este directorio contiene una prueba de concepto (POC) para un flujo de "archivo + ACK" en el que el consumidor (plugin) escribe archivos `ack-<id>.json` y el productor espera por ellos.

Estado: DEPRECATED

Razonamiento:
- Durante pruebas e implementación se observó que la confirmación por archivos (`autopilot_state.txt` o `ack-{id}.json`) no es fiable en entornos reales.
- Problemas detectados: el plugin no siempre se carga, y en Windows la escritura/lectura puede fallar por permisos o bloqueo (`Access denied` / `file locked`).

Decisión:
- El soporte de espera por ACK ha sido eliminado del flujo principal del proyecto.
- Mantener estos scripts como referencia histórica para investigación y debugging, pero **no** se usan en producción.

Si necesitas reactivar la POC, considera mover estos archivos a una rama separada o a `tools/deprecated/` y actualizar pruebas/e2e antes de volver a integrarlos.