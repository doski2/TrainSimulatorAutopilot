Resumen de revisión y próximos pasos
=================================

Cambios principales implementados:

- Eliminación de la lógica y UI relacionada con `FuelLevel` (TSC considera
  combustible infinito)
- Introducción de `active_alerts_list` en payloads `telemetry_update` y
  actualización del cliente para preferirlo
- Dedupe de alertas en la UI (prevent spam) por clave `type+title` con
  `knownAlertKeys`
- Auto-resolución de alertas transitorias (`wheelslip`, `speed_violation`,
  `overheating` menores)
- Script de limpieza `scripts/cleanup_persisted_fuel.py` para eliminar
  alertas históricas y keys de telemetría relacionadas con el combustible
- Actualizaciones en documentación: `API_DOCUMENTATION.md`,
  `DOCUMENTATION.md`, `docs/CORRECCIONES_DASHBOARD.md`,
  `docs/ejemplos/ejemplos-codigo.md` y `docs/maintenance-log.md`

Pruebas realizadas:

- Suite de tests completos: `pytest -q` ✅ 74/74 passed
- Script `scripts/cleanup_persisted_fuel.py` ejecutado con backups creados

Acciones sugeridas (manuales / operativas):

 - Revisar `alerts.json.bak.*` y
   `data/telemetry_history.json.bak.*` si se desea conservar historial;
   eliminar backups solo si está seguro
 - Revisar las plantillas del plugin RailDriver/SD40 si desea mantener
   compatibilidad con otros simuladores que usen `FuelLevel`
 - Si todo está listo, crear una rama y PR desde `master` hacia `main` con
   los cambios y la documentación

Tareas opcionales:

 - Añadir tests E2E que verifiquen la deduplicación y la auto-resolución en
   un entorno de integración
 - Añadir script o migración para eliminar referencias a `FuelLevel` de
   repositorios y plugins externos si se desea centralizar la compatibilidad

Contacto:

- Para ajustes adicionales, indícame si quieres que realice: commit + PR, limpieza de backups, o añadir migración automatizada de datos históricos.
